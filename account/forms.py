from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Perfil

class PerfilRegistroForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = Perfil
        fields = ('username', 'email', 'first_name', 'last_name')

class PerfilEdicionForm(UserChangeForm):
    password = None  # No queremos editar password en este form

    class Meta:
        model = Perfil
        fields = ('first_name', 'last_name', 'email', 'avatar', 'bio', 'pais', 'dni', 'direccion')
