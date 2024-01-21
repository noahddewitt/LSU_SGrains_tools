# Generated by Django 3.2.19 on 2024-01-18 21:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crossing', '0020_alter_wcp_entries_purdy_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='crosses',
            name='status_text',
            field=models.CharField(choices=[('Set', 'Set'), ('Made', 'Made'), ('Failed', 'Failed')], default='Made', max_length=10, verbose_name='Status'),
        ),
    ]