# Generated by Django 3.2.19 on 2023-12-30 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crossing', '0013_auto_20231230_0840'),
    ]

    operations = [
        migrations.AddField(
            model_name='families',
            name='order_int',
            field=models.IntegerField(default=1, verbose_name='Cross Order'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='families',
            name='year_text',
            field=models.CharField(default=2024, max_length=4, verbose_name='Cross Year'),
            preserve_default=False,
        ),
    ]