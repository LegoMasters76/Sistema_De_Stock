from django.db import models
from django.contrib.auth.models import AbstractUser

def avatar_upload_to(instance, filename):
    return f"avatars/{instance.username}/{filename}"

class Perfil(AbstractUser):
    avatar = models.ImageField(
        upload_to=avatar_upload_to,
        default="default/default.png",
        blank=True,
        null=True,
        verbose_name="Avatar"
    )
    bio = models.TextField(max_length=500, blank=True, null=True, verbose_name="Biografía")
    pais = models.CharField(max_length=50, blank=True, null=True)
    dni = models.CharField(max_length=12, blank=True, null=True)
    direccion = models.CharField(max_length=100, blank=True, null=True)
    # Quitamos el unique=True para evitar errores al crear superusuarios
    nro_usuario = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfiles"

    def __str__(self):
        return f"{self.username}"
