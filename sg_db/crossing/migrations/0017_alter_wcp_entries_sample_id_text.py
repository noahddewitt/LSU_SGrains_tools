# Generated by Django 3.2.19 on 2023-12-31 18:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crossing', '0016_auto_20231230_1332'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wcp_entries',
            name='sample_id_text',
            field=models.CharField(blank=True, max_length=200, verbose_name='Geno Id'),
        ),
    ]
