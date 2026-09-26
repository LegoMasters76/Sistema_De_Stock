from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from Stock.models import Producto

from .audit import registrar_evento_sensible


@receiver(pre_save, sender=Producto)
def recordar_precio_anterior(sender, instance, **kwargs):
    if not instance.pk:
        instance._audit_precio_anterior = None
        return
    instance._audit_precio_anterior = (
        sender._base_manager.filter(pk=instance.pk)
        .values_list("precio", flat=True)
        .first()
    )


@receiver(post_save, sender=Producto)
def auditar_cambio_de_precio(sender, instance, created, **kwargs):
    precio_anterior = getattr(instance, "_audit_precio_anterior", None)
    if not created and precio_anterior is not None and precio_anterior != instance.precio:
        registrar_evento_sensible(
            "product_price_changed",
            instance,
            details={
                "precio_anterior": str(precio_anterior),
                "precio_nuevo": str(instance.precio),
            },
        )