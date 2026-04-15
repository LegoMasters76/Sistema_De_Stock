from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DetailView
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Perfil
from .forms import PerfilRegistroForm, PerfilEdicionForm

# 1. REGISTRO (CBV)
class RegistroUsuario(CreateView):
    model = Perfil
    form_class = PerfilRegistroForm
    template_name = 'account/registro.html'
    success_url = reverse_lazy('login')

# 2. LOGIN (CBV)
class LoginUsuario(LoginView):
    template_name = 'account/login.html'
    next_page = reverse_lazy('inicio')

# 3. LOGOUT (CBV)
class LogoutUsuario(LogoutView):
    template_name = 'account/logout.html'

# 4. VER PERFIL (CBV)
class PerfilDetalle(LoginRequiredMixin, DetailView):
    model = Perfil
    template_name = 'account/perfil.html'
    context_object_name = 'perfil'

    def get_object(self):
        return self.request.user

# 5. EDITAR PERFIL (CBV)
class PerfilEdicion(LoginRequiredMixin, UpdateView):
    model = Perfil
    form_class = PerfilEdicionForm
    template_name = 'account/perfil_edit.html'
    success_url = reverse_lazy('inicio')

    def get_object(self):
        return self.request.user

# 6. CAMBIO DE CONTRASEÑA (CBV)
class PasswordCambio(LoginRequiredMixin, PasswordChangeView):
    template_name = 'account/password_cambio.html'
    success_url = reverse_lazy('inicio')
