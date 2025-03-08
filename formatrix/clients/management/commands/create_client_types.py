from django.core.management.base import BaseCommand
from clients.models import TypeClient

class Command(BaseCommand):
    help = 'Crée les types de clients initiaux'

    def handle(self, *args, **kwargs):
        client_types = [
            {
                'typeclient': 'Organisation Non Gouvernementale',
                'categorie': 'ong',
                'description': 'Organisation à but non lucratif œuvrant pour le développement'
            },
            {
                'typeclient': 'Entreprise Privée',
                'categorie': 'entreprise',
                'description': 'Société commerciale ou industrielle'
            },
            {
                'typeclient': 'Autre Organisation',
                'categorie': 'autre',
                'description': 'Autre type d\'organisation'
            }
        ]
        
        for type_data in client_types:
            TypeClient.objects.get_or_create(
                typeclient=type_data['typeclient'],
                defaults={
                    'categorie': type_data['categorie'],
                    'description': type_data['description']
                }
            )
            self.stdout.write(
                self.style.SUCCESS(f'Type de client créé : {type_data["typeclient"]}')
            ) 