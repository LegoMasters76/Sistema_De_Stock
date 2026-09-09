from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from .models import Licencia
from .utils import validar_serial

class ActivarLicenciaView(View):
    def get(self, request):
        # Si ya hay licencia, redirigir al inicio
        if Licencia.objects.filter(activo=True).exists():
            return redirect('inicio')
        return render(request, 'main/activar_licencia.html')

    def post(self, request):
        serial = request.POST.get('serial', '').strip()
        cliente = request.POST.get('cliente', '').strip()
        
        if validar_serial(serial):
            # Desactivar otras licencias si existieran
            Licencia.objects.all().update(activo=False)
            
            # Crear nueva licencia
            Licencia.objects.create(
                serial=serial,
                cliente=cliente,
                activo=True
            )
            messages.success(request, "¡Sistema activado correctamente!")
            return redirect('inicio')
        else:
            messages.error(request, "Serial inválido. Por favor, intente nuevamente.")
            return render(request, 'main/activar_licencia.html', {'serial': serial, 'cliente': cliente})
