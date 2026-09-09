from django.contrib import admin
from .models import Producto, Categoria, Proveedor, Estanteria, ConfiguracionDeposito, MovimientosStock

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'stock', 'precio', 'categoria', 'fecha_creacion')
    search_fields = ('nombre', 'categoria__nombre')
    list_filter = ('categoria', 'proveedor')
    readonly_fields = ('fecha_creacion',)

admin.site.register(Categoria)
admin.site.register(Proveedor)
admin.site.register(Estanteria)
admin.site.register(ConfiguracionDeposito)
admin.site.register(MovimientosStock)
