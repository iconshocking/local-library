# Generated by Django 5.0.6 on 2024-07-07 17:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0011_alter_book_cover_image_height_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bookinstance',
            name='imprint',
        ),
    ]
