from django import forms
from django.forms import inlineformset_factory
from .models import Venta, Detalle_venta, Cliente

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'telefono', 'email']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class VentaForm(forms.ModelForm):
    cliente_seleccion = forms.ModelChoiceField(
        queryset=Cliente.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'cliente-select'}),
        label="Cliente *",
        empty_label="--- Seleccione un Cliente ---"
    )

    class Meta:
        model = Venta
        fields = ['telefono', 'email']
        widgets = {
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        }
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        cliente_obj = self.cleaned_data.get('cliente_seleccion')
        if cliente_obj:
            instance.cliente = cliente_obj.nombre
        if commit:
            instance.save()
        return instance

DetalleVentaFormSet = inlineformset_factory(
    Venta, 
    Detalle_venta, 
    fields=['producto', 'cantidad', 'precio_unitario'],
    extra=1,
    can_delete=True,
    widgets={
        'producto': forms.Select(attrs={'class': 'form-select producto-select', 'required': True}),
        'cantidad': forms.NumberInput(attrs={'class': 'form-control cantidad-input', 'min': 1, 'required': True}),
        'precio_unitario': forms.NumberInput(attrs={'class': 'form-control precio-input', 'step': '0.01', 'required': True}),
    }
)
