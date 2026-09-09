from django.urls import path
from .views import RegistroUsuario, LoginUsuario, LogoutUsuario, PerfilDetalle, PerfilEdicion, PasswordCambio

urlpatterns = [
    path('registro/', RegistroUsuario.as_view(), name='registro'),
    path('login/', LoginUsuario.as_view(), name='login'),
    path('logout/', LogoutUsuario.as_view(), name='logout'),
    path('perfil/', PerfilDetalle.as_view(), name='perfil'),
    path('perfil/editar/', PerfilEdicion.as_view(), name='perfil_edit'),
    path('perfil/password/', PasswordCambio.as_view(), name='password_change'),
]
