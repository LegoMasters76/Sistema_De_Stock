from django import forms
from .models import Producto, Categoria, Provedor

class ProductoForm(forms.ModelForm):

    class Meta:
        model = Producto
        fields = '__all__'

class CategoriaForm(forms.ModelForm):
    
    class Meta:
        model= Categoria
        fields= "__all__"
        
        
class ProvedorForm(forms.ModelForm):
    
    class Meta:
        model= Provedor
        fields= "__all__"