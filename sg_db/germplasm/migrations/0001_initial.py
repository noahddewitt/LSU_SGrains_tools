# Generated by Django 3.2.19 on 2023-12-30 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Trials',
            fields=[
                ('trial_id', models.CharField(max_length=40, primary_key=True, serialize=False, verbose_name='Trial Id')),
            ],
        ),
    ]