from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from .models import Venta, Detalle_venta, Cliente
from .forms import VentaForm, DetalleVentaFormSet, ClienteForm
from Stock.models import Producto
from Stock.services import InventoryValidationError, procesar_venta

class ClienteCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'ventas/agregar_cliente.html'
    success_url = reverse_lazy('ventas:venta_create')
    permission_required = 'ventas.manage_clients'
    raise_exception = True
    
    def form_valid(self, form):
        messages.success(self.request, "Cliente registrado exitosamente.")
        return super().form_valid(form)

class VentaListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Venta
    template_name = 'ventas/venta_list.html'
    context_object_name = 'ventas'
    ordering = ['-fecha']
    paginate_by = 10
    permission_required = 'ventas.view_sales'
    raise_exception = True

    def get_queryset(self):
        queryset = super().get_queryset().select_related('cliente', 'vendedor').prefetch_related('detalles__producto')
        if not self.request.user.has_perm('ventas.view_all_sales'):
            queryset = queryset.filter(vendedor=self.request.user)
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
            queryset = queryset.filter(cliente__nombre__icontains=cliente)
        
        if producto_id:
            try:
                queryset = queryset.filter(detalles__producto__id=int(producto_id)).distinct()
            except (TypeError, ValueError):
                queryset = queryset.none()

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
        context['clientes_lista'] = sorted(Cliente.objects.exclude(nombre__isnull=True).exclude(nombre='').values_list('nombre', flat=True))
        context['dia_filter'] = self.request.GET.get('dia', '')
        context['hora_filter'] = self.request.GET.get('hora', '')
        context['producto_filter'] = self.request.GET.get('producto', '')
        context['cliente_filter'] = self.request.GET.get('cliente', '')
        return context

class VentaDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Venta
    template_name = 'ventas/venta_detail.html'
    context_object_name = 'venta'
    permission_required = 'ventas.view_sales'
    raise_exception = True

    def get_queryset(self):
        queryset = super().get_queryset().select_related('cliente', 'vendedor').prefetch_related('detalles__producto')
        if not self.request.user.has_perm('ventas.view_all_sales'):
            queryset = queryset.filter(vendedor=self.request.user)
        return queryset

class VentaCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Venta
    form_class = VentaForm
    template_name = 'ventas/venta_form.html'
    success_url = reverse_lazy('ventas:venta_list')
    permission_required = 'ventas.create_sales'
    raise_exception = True

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['detalles'] = DetalleVentaFormSet(self.request.POST)
        else:
            data['detalles'] = DetalleVentaFormSet()
        
        productos = Producto.objects.all()
        productos_info = {p.id: {'precio': float(p.precio), 'stock': p.stock} for p in productos}
        data['productos_info'] = productos_info
        return data

    def form_valid(self, form):
        context = self.get_context_data(form=form)
        detalles = context['detalles']
        if not detalles.is_valid():
            return self.render_to_response(context)
        lineas = [
            detalle_form.cleaned_data
            for detalle_form in detalles
            if detalle_form.cleaned_data and not detalle_form.cleaned_data.get('DELETE', False)
        ]
        try:
            self.object = procesar_venta(
                cliente=form.cleaned_data['cliente_seleccion'],
                vendedor=self.request.user,
                telefono=form.cleaned_data.get('telefono', ''),
                email=form.cleaned_data.get('email', ''),
                detalles=lineas,
            )
        except InventoryValidationError as error:
            form.add_error(None, str(error))
            return self.render_to_response(context)

        messages.success(self.request, "Venta registrada exitosamente.")
        return redirect(self.get_success_url())

from django.contrib.auth.decorators import login_required, permission_required

@login_required
@permission_required('ventas.access_customer_api', raise_exception=True)
def clientes_api(request):
    clientes = Cliente.objects.values('id', 'telefono', 'email')
    clientes_dict = {
        str(c['id']): {
            'telefono': c['telefono'] or '',
            'email': c['email'] or ''
        } for c in clientes
    }
    return JsonResponse(clientes_dict)
