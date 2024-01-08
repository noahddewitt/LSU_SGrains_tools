# Generated by Django 3.2.19 on 2024-01-08 15:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('germplasm', '0010_auto_20240107_1125'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trials',
            name='plot_type',
            field=models.CharField(choices=[('Yield', 'Yield'), ('HR', 'Headrows'), ('SP', 'Single Plants'), ('Pot', 'Pots')], max_length=10, verbose_name='Plot Type'),
        ),
    ]
