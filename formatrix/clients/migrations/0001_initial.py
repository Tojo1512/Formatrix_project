# Generated by Django 5.1.6 on 2025-03-04 16:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TypeClient',
            fields=[
                ('typeclientid', models.AutoField(primary_key=True, serialize=False)),
                ('typeclient', models.CharField(max_length=100)),
                ('reseau', models.CharField(choices=[('interne', 'Interne'), ('externe', 'Externe')], max_length=50)),
            ],
            options={
                'db_table': 'typeclient',
            },
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('clientid', models.AutoField(primary_key=True, serialize=False)),
                ('nomclient', models.CharField(max_length=100)),
                ('autresnom', models.CharField(max_length=100, null=True)),
                ('email', models.CharField(max_length=100, null=True)),
                ('localite', models.CharField(max_length=100, null=True)),
                ('ville', models.CharField(max_length=100, null=True)),
                ('numero_immatriculation', models.CharField(max_length=50, null=True)),
                ('adresse_rue', models.TextField(null=True)),
                ('telephone', models.CharField(max_length=20, null=True)),
                ('typeclientid', models.ForeignKey(db_column='typeclientid', on_delete=django.db.models.deletion.CASCADE, to='clients.typeclient')),
            ],
            options={
                'db_table': 'client',
            },
        ),
    ]
