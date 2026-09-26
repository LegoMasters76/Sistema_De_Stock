from django.contrib.auth.models import Group, Permission


ROLE_PERMISSIONS = {
    "Vendedor": (
        ("Stock", "view_stock"),
        ("ventas", "access_customer_api"),
        ("ventas", "manage_clients"),
        ("ventas", "create_sales"),
        ("ventas", "view_sales"),
    ),
    "Encargado de Depósito": (
        ("Stock", "view_stock"),
        ("Stock", "manage_products"),
        ("Stock", "view_warehouse"),
        ("Stock", "manage_warehouse"),
    ),
}


def configure_role_groups(sender, using, **kwargs):
    """Create role groups and synchronize their application permissions."""
    permission_rows = Permission.objects.using(using).filter(
        content_type__app_label__in={"Stock", "ventas"},
        codename__in={
            codename
            for permissions in ROLE_PERMISSIONS.values()
            for _, codename in permissions
        } | {"view_all_sales"},
    )
    permissions_by_key = {
        (permission.content_type.app_label, permission.codename): permission
        for permission in permission_rows.select_related("content_type")
    }

    administrator, _ = Group.objects.using(using).get_or_create(
        name="Administrador"
    )
    administrator.permissions.set(Permission.objects.using(using).all())

    for role_name, permission_keys in ROLE_PERMISSIONS.items():
        role, _ = Group.objects.using(using).get_or_create(name=role_name)
        role.permissions.set(
            [
                permissions_by_key[key]
                for key in permission_keys
                if key in permissions_by_key
            ]
        )

    administrator.permissions.add(
        *[
            permission
            for key, permission in permissions_by_key.items()
            if key == ("ventas", "view_all_sales")
        ]
    )