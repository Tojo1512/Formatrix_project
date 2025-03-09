# Generated by Django 5.1.6 on 2025-03-09 17:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seances', '0002_rename_date_debut_seance_date_remove_seance_date_fin_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='seance',
            name='statut',
            field=models.CharField(choices=[('pas_commence', 'Pas encore commencé'), ('en_cours', 'En cours'), ('termine', 'Terminé'), ('annule', 'Annulé')], default='pas_commence', max_length=50),
        ),
    ]
