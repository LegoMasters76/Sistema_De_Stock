from django.db import models
from django.conf import settings
from simple_history.models import HistoricalRecords
from Stock.models import Producto
from main.tenancy import TenantModel

class Cliente(TenantModel):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    class Meta:
        permissions = [
            ("access_customer_api", "Can access the customer lookup API"),
            ("manage_clients", "Can create and manage clients"),
        ]

    def __str__(self):
        return self.nombre

class Venta(TenantModel):
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='ventas')
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    vendedor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    history = HistoricalRecords(inherit=True)

    class Meta:
        permissions = [
            ("create_sales", "Can create sales"),
            ("view_sales", "Can view own sales"),
            ("view_all_sales", "Can view all sales"),
        ]
    
    def __str__(self):
        return f"Venta {self.id} - {self.cliente} ({self.fecha.strftime('%d/%m/%Y')})"
    
class Detalle_venta(TenantModel):
    venta = models.ForeignKey(Venta, related_name="detalles", on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad}"
