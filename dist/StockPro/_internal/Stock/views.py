from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from .models import Categoria, Proveedor, Producto, MovimientosStock, Estanteria, ConfiguracionDeposito
from .forms import ProductoForm, ProveedorForm, CategoriaForm 
from django.contrib import messages
import json
from django.views.generic import TemplateView, DetailView
from django.db.models import F
from django.contrib.auth.decorators import login_required

class AboutMe(TemplateView):
    template_name = "Stock/about.html"

class ProductoDetalle(DetailView):
    model = Producto
    template_name = "Stock/producto_detalle.html"
    context_object_name = "producto"

def index(request):
    productos = Producto.objects.all()
    context = {
        "total_productos": productos.count(),
        "bajo_stock": productos.filter(stock__lte=F('stock_minimo'), stock__gt=0).count(),
        "sin_stock": productos.filter(stock=0).count(),
    }
    return render(request, "Stock/index.html", context)

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

def configurar_limites(request):
    config, created = ConfiguracionDeposito.objects.get_or_create(id=1)
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            config.ancho_px = int(data.get('ancho'))
            config.largo_px = int(data.get('largo'))
            config.save()
            return JsonResponse({"status": "ok"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    return render(request, "Stock/dibujar_mapa.html", {"config": config})

def buscar_producto(request):
    resultados = []
    nombre_buscado = request.GET.get("nombre")
    if nombre_buscado:
        resultados = Producto.objects.filter(nombre__icontains=nombre_buscado)
    return render(request, "Stock/buscar_producto.html", {"resultados": resultados})

def productos_por_estante(request, id):
    estante = get_object_or_404(Estanteria, id=id)
    productos = estante.productos.all().values('nombre', 'stock', 'nivel_especifico')
    return JsonResponse({"estante": estante.nombre, "productos": list(productos)})
