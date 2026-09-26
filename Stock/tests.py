from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from threading import Barrier

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import close_old_connections
from django.test import Client, TestCase, TransactionTestCase, skipUnlessDBFeature
from django.urls import reverse

from main.models import Empresa, Licencia
from main.tenancy import reset_current_tenant, set_current_tenant
from ventas.models import Cliente, Detalle_venta, Venta

from .models import Categoria, MovimientosStock, Producto
from .services import (
	InventoryValidationError,
	ajuste_stock,
	procesar_venta,
	registrar_entrada,
)


class TenantFixtureMixin:
	def crear_contexto(self, slug="empresa-prueba"):
		self.empresa = Empresa.objects.create(nombre="Empresa de prueba", slug=slug)
		self.tenant_token = set_current_tenant(self.empresa)
		Licencia.objects.create(serial=f"LIC-{slug}", activo=True)
		self.usuario = get_user_model().objects.create_user(
			username=f"usuario-{slug}",
			password="clave-segura",
			empresa=self.empresa,
		)
		self.categoria = Categoria.objects.create(nombre="General")
		self.cliente = Cliente.objects.create(nombre="Cliente de prueba")
		self.producto = Producto.objects.create(
			nombre="Producto de prueba",
			precio=Decimal("12.50"),
			stock=5,
			categoria=self.categoria,
		)

	def asignar_rol(self, usuario, nombre):
		usuario.groups.add(Group.objects.get(name=nombre))
		return get_user_model().objects.get(pk=usuario.pk)

	def limpiar_contexto(self):
		reset_current_tenant(self.tenant_token)


class SecurityTests(TenantFixtureMixin, TestCase):
	def setUp(self):
		self.crear_contexto()
		self.vendedor = self.asignar_rol(self.usuario, "Vendedor")

	def tearDown(self):
		self.limpiar_contexto()
		super().tearDown()

	def test_usuario_anonimo_no_accede_al_stock(self):
		response = self.client.get(reverse("stock"))

		self.assertEqual(response.status_code, 302)
		self.assertIn("/accounts/login/", response["Location"])

	def test_rol_vendedor_puede_ver_stock(self):
		self.client.force_login(self.vendedor)

		response = self.client.get(reverse("stock"))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.producto.nombre)

	def test_rol_vendedor_no_puede_administrar_productos(self):
		self.client.force_login(self.vendedor)

		response = self.client.get(reverse("agregar_producto"))

		self.assertEqual(response.status_code, 403)

	def test_publicacion_sin_token_csrf_es_rechazada(self):
		cliente_csrf = Client(enforce_csrf_checks=True)
		cliente_csrf.force_login(self.vendedor)

		response = cliente_csrf.post(reverse("eliminar_producto", args=[self.producto.pk]))

		self.assertEqual(response.status_code, 403)


class InventoryServiceTests(TenantFixtureMixin, TestCase):
	def setUp(self):
		self.crear_contexto()

	def tearDown(self):
		self.limpiar_contexto()
		super().tearDown()

	def test_compra_registra_entrada_y_saldo(self):
		producto = registrar_entrada(
			self.producto.pk,
			4,
			usuario=self.usuario,
			referencia="Compra 001",
		)

		producto.refresh_from_db()
		movimiento = MovimientosStock.objects.get()
		self.assertEqual(producto.stock, 9)
		self.assertEqual(movimiento.tipo, "ENTRADA")
		self.assertEqual(movimiento.cantidad, 4)
		self.assertEqual(movimiento.saldo_resultante, 9)
		self.assertEqual(movimiento.usuario, self.usuario)
		self.assertEqual(movimiento.referencia, "Compra 001")

	def test_venta_actualiza_stock_total_detalle_y_movimiento(self):
		venta = procesar_venta(
			cliente=self.cliente,
			vendedor=self.usuario,
			detalles=[{"producto": self.producto, "cantidad": 2}],
		)

		self.producto.refresh_from_db()
		detalle = Detalle_venta.objects.get(venta=venta)
		movimiento = MovimientosStock.objects.get()
		self.assertEqual(self.producto.stock, 3)
		self.assertEqual(venta.total, Decimal("25.00"))
		self.assertEqual(detalle.precio_unitario, Decimal("12.50"))
		self.assertEqual(movimiento.tipo, "VENTA")
		self.assertEqual(movimiento.cantidad, 2)
		self.assertEqual(movimiento.saldo_resultante, 3)

	def test_merma_registra_ajuste_negativo(self):
		producto = ajuste_stock(
			self.producto.pk,
			-2,
			usuario=self.usuario,
			referencia="Merma vencimiento",
		)

		movimiento = MovimientosStock.objects.get()
		self.assertEqual(producto.stock, 3)
		self.assertEqual(movimiento.tipo, "MERMA")
		self.assertEqual(movimiento.cantidad, 2)
		self.assertEqual(movimiento.saldo_resultante, 3)

	def test_venta_sin_existencia_no_crea_venta_ni_movimientos(self):
		with self.assertRaises(InventoryValidationError):
			procesar_venta(
				cliente=self.cliente,
				vendedor=self.usuario,
				detalles=[{"producto": self.producto, "cantidad": 6}],
			)

		self.producto.refresh_from_db()
		self.assertEqual(self.producto.stock, 5)
		self.assertEqual(Venta.objects.count(), 0)
		self.assertEqual(MovimientosStock.objects.count(), 0)

	def test_ajuste_que_produciria_stock_negativo_se_rechaza_sin_cambios(self):
		with self.assertRaises(InventoryValidationError):
			ajuste_stock(self.producto.pk, -6, usuario=self.usuario)

		self.producto.refresh_from_db()
		self.assertEqual(self.producto.stock, 5)
		self.assertEqual(MovimientosStock.objects.count(), 0)

	def test_rechaza_cantidades_no_positivas_o_no_enteras(self):
		for cantidad in (0, -1, 1.5, True):
			with self.subTest(cantidad=cantidad):
				with self.assertRaises(InventoryValidationError):
					registrar_entrada(self.producto.pk, cantidad)

		self.assertEqual(MovimientosStock.objects.count(), 0)


class ConcurrencyTests(TenantFixtureMixin, TransactionTestCase):
	reset_sequences = True

	def setUp(self):
		self.crear_contexto(slug="empresa-concurrente")
		self.producto.stock = 1
		self.producto.save(update_fields=["stock"])

	def tearDown(self):
		self.limpiar_contexto()
		super().tearDown()

	@skipUnlessDBFeature("has_select_for_update")
	def test_dos_ventas_simultaneas_no_venden_la_unidad_dos_veces(self):
		barrera = Barrier(2)
		tenant_id = self.empresa.pk
		producto_id = self.producto.pk
		cliente_id = self.cliente.pk
		usuario_id = self.usuario.pk

		def vender_una_unidad():
			close_old_connections()
			token = set_current_tenant(tenant_id)
			try:
				cliente = Cliente.objects.get(pk=cliente_id)
				vendedor = get_user_model().objects.get(pk=usuario_id)
				barrera.wait(timeout=10)
				procesar_venta(
					cliente=cliente,
					vendedor=vendedor,
					detalles=[{"producto_id": producto_id, "cantidad": 1}],
				)
				return "vendida"
			except InventoryValidationError:
				return "sin_stock"
			finally:
				reset_current_tenant(token)
				close_old_connections()

		with ThreadPoolExecutor(max_workers=2) as executor:
			resultados = list(executor.map(lambda _: vender_una_unidad(), range(2)))

		self.producto.refresh_from_db()
		self.assertCountEqual(resultados, ["vendida", "sin_stock"])
		self.assertEqual(self.producto.stock, 0)
		self.assertEqual(Venta.objects.count(), 1)
		self.assertEqual(MovimientosStock.objects.count(), 1)


class TenantIsolationTests(TenantFixtureMixin, TestCase):
	def setUp(self):
		self.crear_contexto()
		self.encargado = self.asignar_rol(self.usuario, "Encargado de Depósito")
		self.otra_empresa = Empresa.objects.create(
			nombre="Otra empresa", slug="otra-empresa"
		)
		token = set_current_tenant(self.otra_empresa)
		try:
			self.producto_ajeno = Producto.objects.create(
				nombre="Producto ajeno",
				precio=Decimal("99.00"),
				stock=8,
				categoria=self.categoria,
			)
		finally:
			reset_current_tenant(token)

	def tearDown(self):
		self.limpiar_contexto()
		super().tearDown()

	def test_consulta_de_productos_solo_devuelve_el_tenant_activo(self):
		productos = list(Producto.objects.all())

		self.assertEqual([producto.pk for producto in productos], [self.producto.pk])

	def test_tenant_no_puede_recuperar_o_editar_producto_ajeno(self):
		self.client.force_login(self.encargado)

		response = self.client.get(
			reverse("editar_producto", args=[self.producto_ajeno.pk])
		)

		self.assertEqual(response.status_code, 404)

	def test_tenant_no_puede_eliminar_producto_ajeno(self):
		self.client.force_login(self.encargado)

		response = self.client.post(
			reverse("eliminar_producto", args=[self.producto_ajeno.pk])
		)

		self.assertEqual(response.status_code, 404)
		self.assertTrue(
			Producto._base_manager.filter(pk=self.producto_ajeno.pk).exists()
		)

	def test_modelo_rechaza_guardado_con_empresa_distinta_al_tenant(self):
		with self.assertRaises(ValidationError):
			Producto.objects.create(
				nombre="Intento de fuga",
				precio=Decimal("1.00"),
				stock=1,
				categoria=self.categoria,
				empresa=self.otra_empresa,
			)

	def test_sin_tenant_activo_el_manager_no_expone_productos(self):
		token = set_current_tenant(None)
		try:
			self.assertEqual(Producto.objects.count(), 0)
		finally:
			reset_current_tenant(token)
