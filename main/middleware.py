from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
from .models import Licencia


class ContentSecurityPolicyMiddleware:
    """Add the configured CSP header to every production response."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["Content-Security-Policy"] = settings.CSP_POLICY
        return response

class VerificacionLicenciaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Rutas excluidas de la verificación de licencia
        rutas_excluidas = [
            reverse('activar_licencia'),
            '/admin/',
        ]
        
        # Permitir archivos estáticos y media
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return self.get_response(request)

        # Comprobar si es una ruta excluida
        es_excluida = False
        for ruta in rutas_excluidas:
            if request.path.startswith(ruta):
                es_excluida = True
                break

        if not es_excluida:
            # Buscar una licencia activa
            licencia_activa = Licencia.objects.filter(activo=True).first()
            if not licencia_activa:
                # Si no hay licencia activa, forzar redirección
                return redirect('activar_licencia')

        response = self.get_response(request)
        return response
