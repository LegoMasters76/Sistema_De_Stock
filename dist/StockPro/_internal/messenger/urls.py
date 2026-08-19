from django.urls import path
from .views import InboxView, EnviarMensajeView, MensajeDetalle

urlpatterns = [
    path('inbox/', InboxView.as_view(), name='inbox'),
    path('enviar/', EnviarMensajeView.as_view(), name='enviar_mensaje'),
    path('mensaje/<int:pk>/', MensajeDetalle.as_view(), name='mensaje_detalle'),
]
