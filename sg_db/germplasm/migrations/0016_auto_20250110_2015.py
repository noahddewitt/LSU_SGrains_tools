# Generated by Django 3.2.19 on 2025-01-11 02:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('germplasm', '0015_auto_20250110_2009'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='predictions',
            name='id',
        ),
        migrations.AddField(
            model_name='predictions',
            name='prediction_id',
            field=models.AutoField(default=1, primary_key=True, serialize=False),
            preserve_default=False,
        ),
    ]
