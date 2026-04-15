from django.db import models
from ckeditor.fields import RichTextField

class ConfiguracionDeposito(models.Model):
    nombre = models.CharField(max_length=100, default="Depósito Principal")
    ancho_px = models.IntegerField(default=2000)
    largo_px = models.IntegerField(default=1500)
    color_suelo = models.CharField(max_length=20, default="#ffffff")

    class Meta:
        verbose_name = "Configuración del Depósito"
        verbose_name_plural = "Configuración del Depósito"

    def __str__(self):
        return f"{self.nombre} ({self.ancho_px}x{self.largo_px}px)"

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.nombre

class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    
    class Meta:
        verbose_name_plural = "Proveedores"

    def __str__(self):
        return self.nombre

class Estanteria(models.Model):
    nombre = models.CharField(max_length=50)
    posicion_x = models.IntegerField()
    posicion_y = models.IntegerField()
    ancho = models.IntegerField(default=100)
    largo = models.IntegerField(default=50)
    niveles = models.IntegerField(default=1)
    altura_m = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"Estante {self.nombre}"

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = RichTextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    stock_minimo = models.IntegerField(default=5)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True)
    estanteria = models.ForeignKey(
        Estanteria, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="productos"
    )
    nivel_especifico = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.nombre

class MovimientosStock(models.Model):
    TIPO_MOVIMIENTO = [
        ("entrada", "Entrada"),
        ("salida", "Salida"),
    ]
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=10, choices=TIPO_MOVIMIENTO)
    cantidad = models.IntegerField()
    fecha = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Movimiento de Stock"
        verbose_name_plural = "Movimientos de Stock"

    def __str__(self):
        return f"{self.producto.nombre} - {self.tipo} ({self.cantidad})"
