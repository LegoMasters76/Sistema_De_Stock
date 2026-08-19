from django.urls import path
from . import views

urlpatterns = [
    path('activar/', views.ActivarLicenciaView.as_view(), name='activar_licencia'),
]
