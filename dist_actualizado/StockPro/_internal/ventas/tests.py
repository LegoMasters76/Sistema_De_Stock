from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from Stock.models import Categoria, MovimientosStock, Producto
from .models import Cliente, Detalle_venta, Venta


MIDDLEWARE_SIN_LICENCIA = [
	middleware for middleware in settings.MIDDLEWARE
	if 'VerificacionLicenciaMiddleware' not in middleware
]


@override_settings(MIDDLEWARE=MIDDLEWARE_SIN_LICENCIA)
class VentaStockTests(TestCase):
	def setUp(self):
		User = get_user_model()
		self.usuario = User.objects.create_user(username='vendedor', password='clave-segura')
		self.cliente = Cliente.objects.create(nombre='Cliente de prueba')
		categoria = Categoria.objects.create(nombre='General')
		self.producto = Producto.objects.create(
			nombre='Producto de prueba', precio=Decimal('12.50'), stock=5, categoria=categoria,
		)

	def datos_venta(self, cantidad, precio='999.99', cantidad_lineas=1):
		datos = {
			'cliente_seleccion': self.cliente.pk,
			'telefono': '', 'email': '',
			'detalles-TOTAL_FORMS': str(cantidad_lineas),
			'detalles-INITIAL_FORMS': '0', 'detalles-MIN_NUM_FORMS': '0',
			'detalles-MAX_NUM_FORMS': '1000',
		}
		for indice in range(cantidad_lineas):
			datos.update({
				f'detalles-{indice}-producto': self.producto.pk,
				f'detalles-{indice}-cantidad': str(cantidad if indice == 0 else 1),
				f'detalles-{indice}-precio_unitario': precio,
			})
		return datos

	def test_venta_sin_stock_hace_rollback(self):
		self.client.force_login(self.usuario)
		response = self.client.post(reverse('ventas:venta_create'), self.datos_venta(6))

		self.assertEqual(response.status_code, 200)
		self.assertEqual(Producto.objects.get(pk=self.producto.pk).stock, 5)
		self.assertEqual(Venta.objects.count(), 0)
		self.assertEqual(MovimientosStock.objects.count(), 0)

	def test_venta_consolida_lineas_usa_precio_servidor_y_crea_movimiento(self):
		self.client.force_login(self.usuario)
		response = self.client.post(
			reverse('ventas:venta_create'), self.datos_venta(2, cantidad_lineas=2),
		)

		self.assertEqual(response.status_code, 302)
		venta = Venta.objects.get()
		detalle = Detalle_venta.objects.get(venta=venta)
		movimiento = MovimientosStock.objects.get()
		self.assertEqual(detalle.cantidad, 3)
		self.assertEqual(detalle.precio_unitario, Decimal('12.50'))
		self.assertEqual(venta.total, Decimal('37.50'))
		self.assertEqual(Producto.objects.get(pk=self.producto.pk).stock, 2)
		self.assertEqual(movimiento.tipo, 'VENTA')
		self.assertEqual(movimiento.cantidad, 3)
		self.assertEqual(movimiento.saldo_resultante, 2)
		self.assertEqual(movimiento.usuario, self.usuario)
		self.assertEqual(movimiento.referencia, f'Venta #{venta.pk}')

	def test_usuario_no_staff_no_puede_crear_producto(self):
		self.client.force_login(self.usuario)
		response = self.client.get(reverse('agregar_producto'))
		self.assertEqual(response.status_code, 302)

	def test_listado_filtra_por_cliente_y_producto(self):
		self.client.force_login(self.usuario)
		venta = Venta.objects.create(cliente=self.cliente, vendedor=self.usuario)
		Detalle_venta.objects.create(
			venta=venta, producto=self.producto, cantidad=1, precio_unitario=self.producto.precio,
		)

		response = self.client.get(reverse('ventas:venta_list'), {'cliente': self.cliente.nombre, 'producto': self.producto.pk})

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, f'#{venta.pk}')

	def test_listado_rechaza_producto_invalido_sin_error_500(self):
		self.client.force_login(self.usuario)

		response = self.client.get(reverse('ventas:venta_list'), {'producto': 'no-es-un-id'})

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'No hay ventas registradas')

	def test_base_de_datos_rechaza_stock_negativo(self):
		from django.db import IntegrityError

		with self.assertRaises(IntegrityError):
			Producto.objects.filter(pk=self.producto.pk).update(stock=-1)
