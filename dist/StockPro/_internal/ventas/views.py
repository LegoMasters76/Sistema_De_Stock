from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.contrib import messages
from django.http import JsonResponse
from .models import Venta, Detalle_venta, Cliente
from .forms import VentaForm, DetalleVentaFormSet, ClienteForm
from Stock.models import Producto
import json

class ClienteCreateView(LoginRequiredMixin, CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'ventas/agregar_cliente.html'
    success_url = reverse_lazy('ventas:venta_create')
    
    def form_valid(self, form):
        messages.success(self.request, "Cliente registrado exitosamente.")
        return super().form_valid(form)

class VentaListView(LoginRequiredMixin, ListView):
    model = Venta
    template_name = 'ventas/venta_list.html'
    context_object_name = 'ventas'
    ordering = ['-fecha']

class VentaDetailView(LoginRequiredMixin, DetailView):
    model = Venta
    template_name = 'ventas/venta_detail.html'
    context_object_name = 'venta'

class VentaCreateView(LoginRequiredMixin, CreateView):
    model = Venta
    form_class = VentaForm
    template_name = 'ventas/venta_form.html'
    success_url = reverse_lazy('ventas:venta_list')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['detalles'] = DetalleVentaFormSet(self.request.POST)
        else:
            data['detalles'] = DetalleVentaFormSet()
        
        productos = Producto.objects.all()
        productos_info = {p.id: {'precio': float(p.precio), 'stock': p.stock} for p in productos}
        data['productos_info'] = json.dumps(productos_info)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        detalles = context['detalles']
        
        if detalles.is_valid():
            for detalle_form in detalles:
                if detalle_form.cleaned_data and not detalle_form.cleaned_data.get('DELETE', False):
                    prod = detalle_form.cleaned_data.get('producto')
                    cant = detalle_form.cleaned_data.get('cantidad')
                    if prod and cant and cant > prod.stock:
                        messages.error(self.request, f"Sin stock suficiente para '{prod.nombre}'. Solicitas {cant}, pero quedan {prod.stock}.")
                        return self.render_to_response(self.get_context_data(form=form))
        else:
            return self.render_to_response(self.get_context_data(form=form))

        with transaction.atomic():
            form.instance.vendedor = self.request.user
            self.object = form.save()
            
            detalles.instance = self.object
            detalles_guardados = detalles.save()
            
            total_venta = 0
            for detalle in detalles_guardados:
                producto = detalle.producto
                producto.stock -= detalle.cantidad
                producto.save()
                total_venta += (detalle.cantidad * detalle.precio_unitario)
            
            self.object.total = total_venta
            self.object.save()
            messages.success(self.request, "Venta registrada exitosamente.")
            return super().form_valid(form)

def clientes_api(request):
    clientes = Cliente.objects.values('id', 'telefono', 'email')
    clientes_dict = {
        str(c['id']): {
            'telefono': c['telefono'] or '',
            'email': c['email'] or ''
        } for c in clientes
    }
    return JsonResponse(clientes_dict)
