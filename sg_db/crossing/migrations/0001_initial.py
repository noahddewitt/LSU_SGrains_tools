# Generated by Django 3.2.19 on 2023-11-25 19:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='WCP_Entries',
            fields=[
                ('wcp_id', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('year_text', models.CharField(max_length=4)),
                ('eno_text', models.CharField(max_length=2)),
                ('desig_text', models.CharField(max_length=200)),
                ('cp_group_text', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Cross',
            fields=[
                ('cross_text', models.CharField(max_length=200, primary_key=True, serialize=False)),
                ('cross_date', models.DateTimeField(verbose_name='Date Cross Made')),
                ('crosser_text', models.CharField(max_length=10)),
                ('parent_one', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='parent_one', to='crossing.wcp_entries')),
                ('parent_two', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='parent_two', to='crossing.wcp_entries')),
            ],
        ),
    ]
