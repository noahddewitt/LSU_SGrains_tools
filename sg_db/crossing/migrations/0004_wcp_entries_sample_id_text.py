# Generated by Django 3.2.19 on 2023-12-13 19:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crossing', '0003_auto_20231213_1413'),
    ]

    operations = [
        migrations.AddField(
            model_name='wcp_entries',
            name='sample_id_text',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
