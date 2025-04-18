# Generated by Django 5.1.6 on 2025-03-05 16:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('apprenants', '0001_initial'),
        ('clients', '0001_initial'),
        ('seances', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Inscription',
            fields=[
                ('inscription_id', models.AutoField(primary_key=True, serialize=False)),
                ('type_inscription', models.CharField(choices=[('individuelle', 'Inscription individuelle'), ('groupe', 'Inscription par groupe'), ('entreprise', 'Inscription par entreprise'), ('rse', 'Inscription via RSE'), ('ong', 'Inscription via ONG')], max_length=50)),
                ('date_inscription', models.DateField(auto_now_add=True)),
                ('statut_inscription', models.CharField(choices=[('en_cours', 'En cours'), ('validee', 'Validée'), ('annulee', 'Annulée')], default='en_cours', max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('apprenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apprenants.apprenant')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clients.client')),
                ('seance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='seances.seance')),
                ('sponsor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sponsorships', to='clients.client')),
            ],
            options={
                'db_table': 'inscription',
                'unique_together': {('client', 'seance', 'apprenant')},
            },
        ),
    ]
