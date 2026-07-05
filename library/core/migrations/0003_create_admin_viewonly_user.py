from django.contrib.auth.hashers import make_password
from django.db import migrations


def create_admin_viewonly_user(apps, schema_editor):
    User = apps.get_model("core", "User")
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")

    models = [
        apps.get_model("catalog", model_name)
        for model_name in ["Book", "Author", "BookInstance", "Genre", "Language"]
    ]
    permissions = []
    for model in models:
        content_type, _ = ContentType.objects.get_or_create(
            app_label="catalog",
            model=model._meta.model_name,
        )
        perm_codename = f"view_{model._meta.model_name}"
        perm_name = f"Can view {model._meta.verbose_name}"
        permission, _ = Permission.objects.get_or_create(
            codename=perm_codename,
            content_type=content_type,
            defaults={"name": perm_name},
        )
        permissions.append(permission)

    user, created = User.objects.get_or_create(
        username="admin-viewonly",
        defaults={
            "email": "admin@example.com",
            "is_staff": True,
            "is_superuser": False,
            "password": make_password("adminexample"),
        },
    )

    if not user.is_staff:
        user.is_staff = True
    if user.is_superuser:
        user.is_superuser = False
    if not created:
        user.password = make_password("adminexample")
    user.save()
    user.user_permissions.set(permissions)


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_require_library_members_group"),
        ("catalog", "0015_alter_book_isbn"),
    ]

    operations = [
        migrations.RunPython(create_admin_viewonly_user, reverse_code=migrations.RunPython.noop),
    ]
