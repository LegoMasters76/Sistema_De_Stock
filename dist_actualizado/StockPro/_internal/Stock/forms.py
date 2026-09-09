from django import forms
from .models import Producto, Categoria, Proveedor

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        exclude = ['stock']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'
        
class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor 
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'