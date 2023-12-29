# Generated by Django 3.2.19 on 2023-12-28 22:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crossing', '0008_alter_wcp_entries_year_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wcp_entries',
            name='cp_group_text',
            field=models.CharField(max_length=200, verbose_name='Group'),
        ),
        migrations.AlterField(
            model_name='wcp_entries',
            name='desig_text',
            field=models.CharField(max_length=200, verbose_name='Desig'),
        ),
        migrations.AlterField(
            model_name='wcp_entries',
            name='eno_text',
            field=models.CharField(max_length=20, verbose_name='Eno'),
        ),
        migrations.AlterField(
            model_name='wcp_entries',
            name='genes_text',
            field=models.CharField(blank=True, max_length=500, verbose_name='Genes'),
        ),
        migrations.AlterField(
            model_name='wcp_entries',
            name='notes_text',
            field=models.CharField(blank=True, max_length=1000, verbose_name='Notes'),
        ),
        migrations.AlterField(
            model_name='wcp_entries',
            name='purdy_text',
            field=models.CharField(max_length=500, verbose_name='Purdy Pedigree'),
        ),
        migrations.AlterField(
            model_name='wcp_entries',
            name='sample_id_text',
            field=models.CharField(blank=True, max_length=200, verbose_name='Genotyping Id'),
        ),
        migrations.AlterField(
            model_name='wcp_entries',
            name='wcp_id',
            field=models.CharField(max_length=20, primary_key=True, serialize=False, verbose_name='WCP Id'),
        ),
    ]