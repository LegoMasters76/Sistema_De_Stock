from django.apps import AppConfig


class AccountConfig(AppConfig):
    name = 'account'

    def ready(self):
        from django.db.models.signals import post_migrate
        from .permissions import configure_role_groups

        post_migrate.connect(
            configure_role_groups,
            dispatch_uid='account.configure_role_groups',
        )
