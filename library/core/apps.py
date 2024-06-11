from typing import override

from django.apps import AppConfig
from django.contrib import admin
from django.contrib.admin.apps import AdminConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"


class AllAuthCompatibleAdminConfig(AdminConfig):
    @override
    def ready(self) -> None:
        super().ready()
        # must import this within the function to avoid error "Apps aren't loaded yet."
        from allauth.account.decorators import secure_admin_login

        admin.site.login = secure_admin_login(admin.site.login)  # type: ignore
