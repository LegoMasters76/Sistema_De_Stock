from django.db import models
from django.conf import settings


class Empresa(models.Model):
    nombre = models.CharField(max_length=150)
    slug = models.SlugField(max_length=160, unique=True)
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"

    def __str__(self):
        return self.nombre


class Licencia(models.Model):
    serial = models.CharField(max_length=50, unique=True)
    fecha_activacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    cliente = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = "Licencia del Sistema"
        verbose_name_plural = "Licencias del Sistema"

    def __str__(self):
        return f"Licencia {'Activa' if self.activo else 'Inactiva'} - {self.serial}"


class AuditEvent(models.Model):
    ACTIONS = [
        ("product_price_changed", "Modificación de precio"),
        ("sale_cancelled", "Cancelación de venta"),
        ("credit_note_issued", "Emisión de nota de crédito"),
    ]

    empresa = models.ForeignKey("main.Empresa", on_delete=models.PROTECT, null=True, blank=True)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_events",
    )
    action = models.CharField(max_length=40, choices=ACTIONS)
    object_type = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100)
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [models.Index(fields=("empresa", "action", "created_at"))]

    def __str__(self):
        return f"{self.get_action_display()} - {self.object_type} #{self.object_id}"
