from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Mensaje
from account.models import Perfil

# 1. Inbox: Ver mensajes recibidos
class InboxView(LoginRequiredMixin, ListView):
    model = Mensaje
    template_name = 'messenger/inbox.html'
    context_object_name = 'mensajes'

    def get_queryset(self):
        # Filtramos para que solo vea los mensajes que le enviaron a él
        return Mensaje.objects.filter(destinatario=self.request.user)

# 2. Ver Detalle de un mensaje
class MensajeDetalle(LoginRequiredMixin, DetailView):
    model = Mensaje
    template_name = 'messenger/mensaje_detalle.html'
    context_object_name = 'mensaje'

    def get_object(self):
        obj = super().get_object()
        if obj.destinatario == self.request.user and not obj.leido:
            obj.leido = True
            obj.save()
        return obj

    def get_queryset(self):
        # Aseguramos que solo pueda leer sus propios mensajes
        return Mensaje.objects.filter(destinatario=self.request.user)

# 3. Enviar Mensaje
class EnviarMensajeView(LoginRequiredMixin, CreateView):
    model = Mensaje
    fields = ['destinatario', 'contenido']
    template_name = 'messenger/enviar_mensaje.html'
    success_url = reverse_lazy('inbox')

    def form_valid(self, form):
        # El remitente siempre es el usuario logueado
        form.instance.remitente = self.request.user
        return super().form_valid(form)
