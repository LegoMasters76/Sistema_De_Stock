from django.contrib import admin
from .models import Categoria, Provedor, Producto, MovimientosStock

admin.site.register(Categoria)
admin.site.register(Provedor)
admin.site.register(Producto)
admin.site.register(MovimientosStock)