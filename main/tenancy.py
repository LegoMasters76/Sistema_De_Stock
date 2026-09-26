from contextvars import ContextVar

from django.core.exceptions import ValidationError
from django.db import models


_current_tenant_id = ContextVar("current_tenant_id", default=None)


def get_current_tenant_id():
    return _current_tenant_id.get()


def set_current_tenant(tenant):
    tenant_id = getattr(tenant, "pk", tenant)
    return _current_tenant_id.set(tenant_id)


def reset_current_tenant(token):
    _current_tenant_id.reset(token)


class TenantQuerySet(models.QuerySet):
    def update(self, **kwargs):
        tenant_id = get_current_tenant_id()
        new_tenant_id = kwargs.get("empresa_id", kwargs.get("empresa"))
        if new_tenant_id is not None and getattr(new_tenant_id, "pk", new_tenant_id) != tenant_id:
            raise ValidationError("No se puede mover un registro a otra empresa.")
        return super().update(**kwargs)

    def bulk_create(self, objs, **kwargs):
        tenant_id = get_current_tenant_id()
        if tenant_id is None:
            raise ValidationError("Se requiere una empresa activa para guardar registros.")
        objs = list(objs)
        for obj in objs:
            if obj.empresa_id not in (None, tenant_id):
                raise ValidationError("No se puede guardar un registro de otra empresa.")
            obj.empresa_id = tenant_id
        return super().bulk_create(objs, **kwargs)


class TenantManager(models.Manager.from_queryset(TenantQuerySet)):
    def get_queryset(self):
        queryset = super().get_queryset()
        tenant_id = get_current_tenant_id()
        if tenant_id is None:
            return queryset.none()
        return queryset.filter(empresa_id=tenant_id)


class TenantModel(models.Model):
    empresa = models.ForeignKey(
        "main.Empresa",
        on_delete=models.PROTECT,
        related_name="+",
    )

    objects = TenantManager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        tenant_id = get_current_tenant_id()
        if self.empresa_id is None:
            if tenant_id is None:
                raise ValidationError("Se requiere una empresa activa para guardar este registro.")
            self.empresa_id = tenant_id
        elif tenant_id is not None and self.empresa_id != tenant_id:
            raise ValidationError("No se puede guardar un registro de otra empresa.")
        for field in self._meta.concrete_fields:
            if not isinstance(field, models.ForeignKey) or field.name == "empresa":
                continue
            related = getattr(self, field.name, None)
            related_empresa_id = getattr(related, "empresa_id", None)
            if related_empresa_id is not None and related_empresa_id != self.empresa_id:
                raise ValidationError({field.name: "El registro relacionado pertenece a otra empresa."})
        return super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        tenant_id = get_current_tenant_id()
        if tenant_id is not None and self.empresa_id not in (None, tenant_id):
            raise ValidationError({"empresa": "La empresa no coincide con el tenant activo."})