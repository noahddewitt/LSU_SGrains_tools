# Generated by Django 3.2.19 on 2024-01-03 13:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crossing', '0017_alter_wcp_entries_sample_id_text'),
    ]

    operations = [
        migrations.AddField(
            model_name='wcp_entries',
            name='source_text',
            field=models.CharField(blank=True, max_length=50, verbose_name='Source'),
        ),
    ]
