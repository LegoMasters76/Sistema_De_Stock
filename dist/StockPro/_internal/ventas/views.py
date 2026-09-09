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
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        dia = self.request.GET.get('dia')
        hora = self.request.GET.get('hora')
        producto_id = self.request.GET.get('producto')
        cliente = self.request.GET.get('cliente')

        if dia:
            queryset = queryset.filter(fecha__date=dia)
        if hora:
            try:
                if ':' in hora:
                    h = hora.split(':')[0]
                    m = hora.split(':')[1]
                    queryset = queryset.filter(fecha__hour=h, fecha__minute=m)
                else:
                    queryset = queryset.filter(fecha__hour=hora)
            except ValueError:
                pass
                
        if cliente:
            queryset = queryset.filter(cliente__icontains=cliente)
        
        if producto_id:
            queryset = queryset.filter(detalles__producto__id=producto_id).distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Paginación - rango de páginas
        page_obj = context.get('page_obj')
        if page_obj:
            paginator = page_obj.paginator
            # Generar rango de 5 en 5, ej: ventana alrededor de la página actual
            # get_elided_page_range requiere el número de página actual
            page_range = paginator.get_elided_page_range(page_obj.number, on_each_side=2, on_ends=1)
            context['custom_page_range'] = page_range
            
        context['productos_lista'] = Producto.objects.all()
        from .models import Cliente
        clientes_nombres = set(Cliente.objects.exclude(nombre__isnull=True).exclude(nombre='').values_list('nombre', flat=True))
        clientes_nombres.update(Venta.objects.exclude(cliente__isnull=True).exclude(cliente='').values_list('cliente', flat=True))
        context['clientes_lista'] = sorted(list(clientes_nombres))
        context['dia_filter'] = self.request.GET.get('dia', '')
        context['hora_filter'] = self.request.GET.get('hora', '')
        context['producto_filter'] = self.request.GET.get('producto', '')
        context['cliente_filter'] = self.request.GET.get('cliente', '')
        return context

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

from django.contrib.auth.decorators import login_required

@login_required
def clientes_api(request):
    clientes = Cliente.objects.values('id', 'telefono', 'email')
    clientes_dict = {
        str(c['id']): {
            'telefono': c['telefono'] or '',
            'email': c['email'] or ''
        } for c in clientes
    }
    return JsonResponse(clientes_dict)
