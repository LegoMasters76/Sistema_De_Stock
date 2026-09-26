from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from Stock.models import Categoria, Producto
from ventas.models import Cliente, Venta

from .audit import registrar_evento_sensible, reset_audit_actor, set_audit_actor
from .models import AuditEvent, Empresa
from .tenancy import reset_current_tenant, set_current_tenant


class AuditTrailTests(TestCase):
    def setUp(self):
        self.empresa = Empresa.objects.create(nombre="Empresa de auditoría", slug="empresa-auditoria")
        self.tenant_token = set_current_tenant(self.empresa)
        self.usuario = get_user_model().objects.create_user(
            username="auditor-test", password="clave-segura", empresa=self.empresa
        )
        self.producto = Producto.objects.create(
            nombre="Producto auditado",
            precio=Decimal("10.00"),
            categoria=Categoria.objects.create(nombre="General"),
        )

    def tearDown(self):
        reset_current_tenant(self.tenant_token)
        super().tearDown()

    def test_modificacion_de_precio_guarda_actor_y_valores(self):
        actor_token = set_audit_actor(self.usuario)
        try:
            self.producto.precio = Decimal("12.50")
            self.producto.save(update_fields=["precio"])
        finally:
            reset_audit_actor(actor_token)

        event = AuditEvent.objects.get(action="product_price_changed")
        self.assertEqual(event.actor, self.usuario)
        self.assertEqual(event.empresa, self.empresa)
        self.assertEqual(event.object_id, str(self.producto.pk))
        self.assertEqual(
            event.details,
            {"precio_anterior": "10.00", "precio_nuevo": "12.50"},
        )

    def test_registra_cancelacion_y_nota_de_credito(self):
        venta = Venta.objects.create(
            cliente=Cliente.objects.create(nombre="Cliente auditado"),
            vendedor=self.usuario,
        )
        registrar_evento_sensible(
            "sale_cancelled", venta, self.usuario, {"motivo": "Error de carga"}
        )
        registrar_evento_sensible(
            "credit_note_issued", venta, self.usuario, {"numero": "NC-001"}
        )

        self.assertEqual(
            list(AuditEvent.objects.order_by("action").values_list("action", flat=True)),
            ["credit_note_issued", "sale_cancelled"],
        )
