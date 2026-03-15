from django.db import models

# Create your models here.

class Categoria(models.Model):
    nombre= models.CharField(max_length=100)
    descripcion= models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.nombre

class Provedor (models.Model):
    nombre= models.CharField(max_length=100)
    telefono=models.CharField(max_length=20)
    email= models.EmailField(blank=True, null=True)
    
    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre=models.CharField(max_length=20)
    descripcion =models.TextField(blank=True, null=True)
    precio=models.DecimalField(max_digits=10, decimal_places=2)
    stock=models.IntegerField(default=0)
    
    Categoria=models.ForeignKey(Categoria, on_delete=models.CASCADE)
    provedor= models.ForeignKey(Provedor, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return self.nombre
    
class MovimientosStock(models.Model):
    
    TIPO_MOVIMIENTO =[
        ("entrada", "Entrada"),
        ("salida", "Salida"),
    ]
    
    producto= models.ForeignKey(Producto, on_delete=models.CASCADE)
    tipo= models.CharField(max_length=10, choices=TIPO_MOVIMIENTO)
    cantidad=models.IntegerField()
    fecha=models.DateTimeField(auto_now_add=True)
    descripcion= models.TextField(blank=True,null=True)

    def __str__(self):
        return f"{self.producto.nombre} - {self.tipo} - {self.cantidad}"
