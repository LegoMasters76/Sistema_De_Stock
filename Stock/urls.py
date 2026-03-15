from django.urls import path
from Stock import views

urlpatterns = [
    path('', views.index, name='inicio'),
    path('stock/', views.stock, name='stock'),
    path('agregar_producto/', views.agregar_producto, name='agregar_producto'),
    path('editar_producto/<int:id>/', views.editar_producto, name='editar_producto'),
    path('eliminar_producto/<int:id>/', views.eliminar_producto, name='eliminar_producto'),
    path('agregar_categoria/', views.agregar_categoria, name='agregar_categoria'),
    path('agregar_proveedor/', views.agregar_proveedor, name='agregar_proveedor'),
    path('buscar_producto/', views.buscar_producto, name='buscar_producto'),
]