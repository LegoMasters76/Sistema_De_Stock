from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Producto
from .forms import ProductoForm, ProvedorForm, CategoriaForm
from django.contrib import messages



def index(request):
    
    productos = Producto.objects.all()

    context = {
        "total_productos": productos.count(),
        "bajo_stock": productos.filter(stock__lte=5, stock__gt=0).count(),
        "sin_stock": productos.filter(stock=0).count(),
    }

    return render(request, "Stock/index.html", context)


def stock(request):
    
    productos = Producto.objects.all()

    nombre = request.GET.get("nombre")

    if nombre:
        productos = Producto.objects.filter(nombre__icontains=nombre)

    return render(request, "Stock/stock.html", {"productos": productos})

def agregar_producto(request):
    if request.method == "POST":
        form= ProductoForm(request.POST)
        
        if form.is_valid():
            form.save()
            return redirect("stock")
    else:
        form= ProductoForm()
        
    context= {
        "form": form
    }
    
    return render(request, "Stock/agregar_producto.html", context)


def editar_producto(request, id):
    
    producto = get_object_or_404(Producto, id=id)

    if request.method == "POST":
        form = ProductoForm(request.POST, instance=producto)

        if form.is_valid():
            form.save()
            return redirect('stock')

    else:
        form = ProductoForm(instance=producto)

    context = {
        "form": form
    }

    return render(request, "Stock/editar_producto.html", context)

def eliminar_producto(request, id):
    
    producto = get_object_or_404(Producto, id=id)

    producto.delete()
    
    messages.success(request, "Producto eliminado correctamente")

    return redirect('stock')

def agregar_categoria(request):
    
    if request.method == "POST":
        form = CategoriaForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('inicio')

    else:
        form = CategoriaForm()

    return render(request,"Stock/agregar_categoria.html",{"form":form})


def agregar_proveedor(request):

    if request.method == "POST":
        form = ProvedorForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('inicio')

    else:
        form = ProvedorForm()

    return render(request,"Stock/agregar_proveedor.html",{"form":form})

def buscar_producto(request):
    
    resultados = []

    if request.GET.get("nombre"):

        nombre = request.GET["nombre"]

        resultados = Producto.objects.filter(nombre__icontains=nombre)

    return render(request, "Stock/buscar_producto.html", {"resultados": resultados})