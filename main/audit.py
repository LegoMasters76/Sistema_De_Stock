from contextvars import ContextVar

from .models import AuditEvent


_current_actor = ContextVar("current_audit_actor", default=None)


def set_audit_actor(actor):
    return _current_actor.set(actor)


def reset_audit_actor(token):
    _current_actor.reset(token)


def registrar_evento_sensible(action, instance, actor=None, details=None):
    """Persist a business event such as a sale cancellation or credit note."""
    allowed_actions = {choice[0] for choice in AuditEvent.ACTIONS}
    if action not in allowed_actions:
        raise ValueError(f"Acción de auditoría no permitida: {action}")

    if actor is None:
        actor = _current_actor.get()
    return AuditEvent.objects.create(
        empresa_id=getattr(instance, "empresa_id", None),
        actor=actor,
        action=action,
        object_type=instance._meta.label,
        object_id=str(instance.pk),
        details=details or {},
    )