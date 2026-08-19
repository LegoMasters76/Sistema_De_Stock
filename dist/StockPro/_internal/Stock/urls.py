from django.urls import path
from Stock import views

urlpatterns = [
    path('', views.index, name='inicio'),
    
    # --- PRODUCTOS Y CATEGORÍAS ---
    path('stock/', views.stock, name='stock'),
    path('stock/<int:pk>/', views.ProductoDetalle.as_view(), name='producto_detalle'),
    path('agregar_producto/', views.agregar_producto, name='agregar_producto'),
    path('editar_producto/<int:id>/', views.editar_producto, name='editar_producto'),
    path('eliminar_producto/<int:id>/', views.eliminar_producto, name='eliminar_producto'),
    path('agregar_categoria/', views.agregar_categoria, name='agregar_categoria'),
    path('agregar_proveedor/', views.agregar_proveedor, name='agregar_proveedor'),
    path('buscar_producto/', views.buscar_producto, name='buscar_producto'),
    
    # --- MAPA DE DEPÓSITO (KONVA.JS) ---
    path('mapa/', views.mapa_stock, name='mapa_stock'),
    path('guardar-estanteria/', views.guardar_estanteria, name='guardar_estanteria'),
    path('api/estante/<int:id>/productos/', views.productos_por_estante, name='productos_por_estante'),
    path('configurar-limites/', views.configurar_limites, name='configurar_limites'),
    path('about/', views.AboutMe.as_view(), name='about'),
]