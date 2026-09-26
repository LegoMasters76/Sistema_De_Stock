from django.contrib import admin

from .models import AuditEvent


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ("created_at", "action", "object_type", "object_id", "actor", "empresa")
    list_filter = ("action", "empresa", "created_at")
    search_fields = ("object_type", "object_id", "details")
    readonly_fields = tuple(field.name for field in AuditEvent._meta.fields)
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
from django.contrib import admin

from .models import Empresa, Licencia


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "slug", "activa", "fecha_creacion")
    list_filter = ("activa",)
    search_fields = ("nombre", "slug")


admin.site.register(Licencia)