from django.conf import settings
from django.db import models
from django.db.models import Q
from django_ckeditor_5.fields import CKEditor5Field
from simple_history.models import HistoricalRecords
from main.tenancy import TenantModel

class ConfiguracionDeposito(models.Model):
    nombre = models.CharField(max_length=100, default="Depósito Principal")
    ancho_px = models.IntegerField(default=2000)
    largo_px = models.IntegerField(default=1500)
    color_suelo = models.CharField(max_length=20, default="#ffffff")
    contorno = models.JSONField(default=list, blank=True)

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

    class Meta:
        permissions = [
            ("view_warehouse", "Can view warehouse layout"),
            ("manage_warehouse", "Can manage warehouse layout"),
        ]

    def __str__(self):
        return f"Estante {self.nombre}"

class Producto(TenantModel):
    nombre = models.CharField(max_length=100)
    descripcion = CKEditor5Field("Descripción", config_name="default", blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    stock_minimo = models.IntegerField(default=5)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True)
    estanteria = models.ForeignKey(
        Estanteria, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="productos"
    )
    nivel_especifico = models.IntegerField(null=True, blank=True)
    history = HistoricalRecords(inherit=True)

    class Meta:
        permissions = [
            ("view_stock", "Can view stock information"),
            ("manage_products", "Can manage products, categories, and suppliers"),
        ]
        constraints = [
            models.CheckConstraint(condition=Q(stock__gte=0), name='producto_stock_no_negativo'),
        ]

    def __str__(self):
        return self.nombre

class MovimientosStock(TenantModel):
    TIPO_MOVIMIENTO = [
        ("VENTA", "Venta"),
        ("ENTRADA", "Entrada"),
        ("AJUSTE", "Ajuste"),
        ("MERMA", "Merma"),
        ("TRANSFERENCIA", "Transferencia"),
    ]
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    tipo = models.CharField(max_length=20, choices=TIPO_MOVIMIENTO)
    cantidad = models.PositiveIntegerField()
    fecha = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField(blank=True, null=True)
    saldo_resultante = models.PositiveIntegerField(null=True, blank=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT)
    referencia = models.CharField(max_length=100, blank=True)
    history = HistoricalRecords(inherit=True)

    class Meta:
        verbose_name = "Movimiento de Stock"
        verbose_name_plural = "Movimientos de Stock"

    def __str__(self):
        return f"{self.producto.nombre} - {self.tipo} ({self.cantidad})"

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValueError("Los movimientos de stock son inmutables.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("Los movimientos de stock son inmutables.")
