from .models import Mensaje

def mensajes_no_leidos(request):
    if request.user.is_authenticated:
        cantidad = Mensaje.objects.filter(destinatario=request.user, leido=False).count()
        return {'mensajes_pendientes_count': cantidad}
    return {'mensajes_pendientes_count': 0}
