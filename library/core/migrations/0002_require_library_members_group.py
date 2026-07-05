from django.db import migrations


def require_library_members_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.get_or_create(name="Library Members")


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(require_library_members_group, reverse_code=migrations.RunPython.noop),
    ]
