from django.db import models

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
