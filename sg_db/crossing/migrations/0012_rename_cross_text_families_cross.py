# Generated by Django 3.2.19 on 2023-12-30 03:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crossing', '0011_auto_20231229_1629'),
    ]

    operations = [
        migrations.RenameField(
            model_name='families',
            old_name='cross_text',
            new_name='cross',
        ),
    ]
