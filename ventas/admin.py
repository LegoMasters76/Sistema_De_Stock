from django.contrib import admin
from .models import Venta, Detalle_venta

class DetalleVentaInLine(admin.TabularInline):
    model= Detalle_venta
    extra= 1
    
@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display= ('id', 'vendedor', 'fecha', 'total')
    inlines= [DetalleVentaInLine]
    