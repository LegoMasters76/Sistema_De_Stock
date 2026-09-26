from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Venta, Detalle_venta

class DetalleVentaInLine(admin.TabularInline):
    model= Detalle_venta
    extra= 1
    
@admin.register(Venta)
class VentaAdmin(SimpleHistoryAdmin):
    list_display= ('id', 'vendedor', 'fecha', 'total')
    inlines= [DetalleVentaInLine]
    