from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
from .audit import reset_audit_actor, set_audit_actor
from .models import Licencia
from .tenancy import reset_current_tenant, set_current_tenant


class AuditActorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        actor = request.user if getattr(request.user, "is_authenticated", False) else None
        token = set_audit_actor(actor)
        try:
            return self.get_response(request)
        finally:
            reset_audit_actor(token)


class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        tenant = getattr(user, "empresa", None) if getattr(user, "is_authenticated", False) else None
        if tenant is not None and not tenant.activa:
            tenant = None
        request.tenant = tenant
        request.tenant_id = getattr(tenant, "pk", None)
        token = set_current_tenant(tenant)
        try:
            return self.get_response(request)
        finally:
            reset_current_tenant(token)


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
