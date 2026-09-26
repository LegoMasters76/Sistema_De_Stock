from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Producto, Categoria, Proveedor, Estanteria, ConfiguracionDeposito, MovimientosStock

class NoBulkDeleteModelAdmin(admin.ModelAdmin):
    actions = None

@admin.register(Producto)
class ProductoAdmin(SimpleHistoryAdmin):
    actions = None
    list_display = ('nombre', 'stock', 'precio', 'categoria', 'fecha_creacion')
    search_fields = ('nombre', 'categoria__nombre')
    list_filter = ('categoria', 'proveedor')
    readonly_fields = ('fecha_creacion', 'stock')

@admin.register(MovimientosStock)
class MovimientosStockAdmin(SimpleHistoryAdmin):
    actions = None
    list_display = ('producto', 'tipo', 'cantidad', 'fecha', 'saldo_resultante', 'usuario')
    list_filter = ('tipo', 'fecha')
    search_fields = ('producto__nombre', 'descripcion', 'referencia')
    readonly_fields = tuple(field.name for field in MovimientosStock._meta.fields)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(
    [Categoria, Proveedor, Estanteria, ConfiguracionDeposito],
    NoBulkDeleteModelAdmin,
)
