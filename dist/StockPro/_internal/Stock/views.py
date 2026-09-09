from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from .models import Categoria, Proveedor, Producto, MovimientosStock, Estanteria, ConfiguracionDeposito
from .forms import ProductoForm, ProveedorForm, CategoriaForm 
from django.contrib import messages
import json
from django.views.generic import TemplateView, DetailView
from django.db.models import F
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

class ProductoDetalle(LoginRequiredMixin, DetailView):
    model = Producto
    template_name = "Stock/producto_detalle.html"
    context_object_name = "producto"

@login_required
def index(request):
    productos = Producto.objects.all()
    context = {
        "total_productos": productos.count(),
        "bajo_stock": productos.filter(stock__lte=F('stock_minimo'), stock__gt=0).count(),
        "sin_stock": productos.filter(stock=0).count(),
    }
    return render(request, "Stock/index.html", context)

@login_required
def stock(request):
    productos = Producto.objects.all()
    nombre = request.GET.get("nombre")
    if nombre:
        productos = Producto.objects.filter(nombre__icontains=nombre)
    return render(request, "Stock/stock.html", {"productos": productos})

@login_required
def agregar_producto(request):
    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("stock")
    else:
        form = ProductoForm()
    return render(request, "Stock/agregar_producto.html", {"form": form})

@login_required
def editar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('stock')
    else:
        form = ProductoForm(instance=producto)
    return render(request, "Stock/editar_producto.html", {"form": form})

@login_required
def eliminar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    producto.delete()
    messages.success(request, "Producto eliminado correctamente")
    return redirect('stock')

@login_required
def agregar_categoria(request):
    if request.method == "POST":
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inicio') 
    else:
        form = CategoriaForm()
    return render(request, "Stock/agregar_categoria.html", {"form": form})

@login_required
def agregar_proveedor(request):
    if request.method == "POST":
        form = ProveedorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inicio')
    else:
        form = ProveedorForm()
    return render(request, "Stock/agregar_proveedor.html", {"form": form})

@login_required
def mapa_stock(request):
    estanterias_qs = Estanteria.objects.all()
    config = ConfiguracionDeposito.objects.first()
    estanterias_data = []
    for e in estanterias_qs:
        estanterias_data.append({
            "id": e.id,
            "nombre": e.nombre,
            "x": e.posicion_x,
            "y": e.posicion_y,
            "ancho": e.ancho,
            "largo": e.largo,
            "niveles": e.niveles,
        })
    
    context = {
        "estanterias_json": json.dumps(estanterias_data),
        "config": config
    }
    return render(request, "Stock/mapa_stock.html", context)

@login_required
def guardar_estanteria(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            estanterias_recibidas = data.get('estanterias', [])
            mapeo_ids = {} 
            ids_presentes = []
            
            for est in estanterias_recibidas:
                temp_id = str(est['id'])
                if temp_id.startswith('new'):
                    obj = Estanteria.objects.create(
                        nombre=est['nombre'],
                        posicion_x=est['x'],
                        posicion_y=est['y'],
                        ancho=est['ancho'],
                        largo=est['largo'],
                        niveles=est['niveles'],
                    )
                else:
                    obj, created = Estanteria.objects.update_or_create(
                        id=int(temp_id),
                        defaults={
                            'nombre': est['nombre'],
                            'posicion_x': est['x'],
                            'posicion_y': est['y'],
                            'ancho': est['ancho'],
                            'largo': est['largo'],
                            'niveles': est['niveles'],
                        }
                    )
                mapeo_ids[temp_id] = obj.id
                ids_presentes.append(obj.id)

            Estanteria.objects.exclude(id__in=ids_presentes).delete()
            return JsonResponse({"status": "ok", "mapeo": mapeo_ids})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    return JsonResponse({"status": "error", "message": "Método no permitido"}, status=405)

@login_required
def configurar_limites(request):
    config, created = ConfiguracionDeposito.objects.get_or_create(id=1)
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            ancho = int(data.get('ancho'))
            largo = int(data.get('largo'))
            contorno = data.get('contorno', [])

            if ancho <= 0 or largo <= 0:
                return JsonResponse({"status": "error", "message": "Las dimensiones deben ser mayores que cero."}, status=400)
            if not isinstance(contorno, list) or len(contorno) < 3:
                return JsonResponse({"status": "error", "message": "El contorno debe tener al menos tres puntos."}, status=400)
            if any(
                not isinstance(point, dict)
                or not isinstance(point.get('x'), (int, float))
                or not isinstance(point.get('y'), (int, float))
                or point['x'] < 0 or point['x'] > ancho
                or point['y'] < 0 or point['y'] > largo
                for point in contorno
            ):
                return JsonResponse({"status": "error", "message": "Los puntos deben estar dentro de las dimensiones del depósito."}, status=400)

            config.ancho_px = ancho
            config.largo_px = largo
            config.contorno = contorno
            config.save()
            return JsonResponse({"status": "ok"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    return render(request, "Stock/dibujar_mapa.html", {"config": config})

@login_required
def buscar_producto(request):
    resultados = []
    nombre_buscado = request.GET.get("nombre")
    if nombre_buscado:
        resultados = Producto.objects.filter(nombre__icontains=nombre_buscado)
    return render(request, "Stock/buscar_producto.html", {"resultados": resultados})

@login_required
def productos_por_estante(request, id):
    estante = get_object_or_404(Estanteria, id=id)
    productos = estante.productos.all().values('nombre', 'stock', 'nivel_especifico')
    return JsonResponse({"estante": estante.nombre, "productos": list(productos)})
