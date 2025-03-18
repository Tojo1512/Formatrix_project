import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'formatrix.settings')
django.setup()

from django.contrib.auth.models import User
from formateurs.models import Formateur

def fix_formateur_user_relations():
    print('=== ÉTAT ACTUEL ===')
    for formateur in Formateur.objects.all():
        print(f'Formateur {formateur.formateurid} ({formateur.nom} {formateur.prenom})')
        print(f'  Email: {formateur.email}')
        print(f'  User ID actuel: {formateur.user.id if formateur.user else None}')
        
        # Chercher un utilisateur correspondant
        matching_user = User.objects.filter(email=formateur.email).first()
        if matching_user:
            print(f'  ✓ Utilisateur trouvé: {matching_user.id} ({matching_user.username})')
            formateur.user = matching_user
            formateur.save()
            print('  ✓ Association mise à jour')
        else:
            print('  ✗ Aucun utilisateur trouvé avec cet email')
        print()

if __name__ == '__main__':
    fix_formateur_user_relations()
