from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Perfil

# Para que el modelo Perfil use el admin de Django de forma correcta
@admin.register(Perfil)
class PerfilAdmin(UserAdmin):
    # Personalizamos los campos que se ven en el Admin
    fieldsets = UserAdmin.fieldsets + (
        ('Información Extra', {
            'fields': ('avatar', 'bio', 'pais', 'dni', 'direccion', 'nro_usuario'),
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información Extra', {
            'fields': ('avatar', 'bio', 'pais', 'dni', 'direccion', 'nro_usuario'),
        }),
    )
