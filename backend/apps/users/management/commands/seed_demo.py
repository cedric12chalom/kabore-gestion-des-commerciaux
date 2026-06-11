"""
Crée les comptes de démonstration GeoCommerce Pro.
Usage : python manage.py seed_demo
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.commerciaux.models import Commercial, ObjectifCommercial
from decimal import Decimal

User = get_user_model()

DEMO_ACCOUNTS = [
    {
        'email': 'admin@geocommerce.pro',
        'password': 'admin123',
        'role': 'ADMIN',
        'first_name': 'Daniel',
        'last_name': 'KINKEU',
        'phone': '+237677777777',
        'username': 'admin',
        'is_staff': True,
        'is_superuser': True,
    },
    {
        'email': 'manager@geocommerce.pro',
        'password': 'manager123',
        'role': 'MANAGER',
        'first_name': 'Marie',
        'last_name': 'NGONO',
        'phone': '+237678888888',
        'username': 'manager1',
    },
    {
        'email': 'commercial@geocommerce.pro',
        'password': 'commercial123',
        'role': 'COMMERCIAL',
        'first_name': 'Jean',
        'last_name': 'MBALLA',
        'phone': '+237690111111',
        'username': 'commercial1',
        'manager_email': 'manager@geocommerce.pro',
        'matricule': 'COM-DEMO001',
    },
    {
        'email': 'commercial2@geocommerce.pro',
        'password': 'commercial123',
        'role': 'COMMERCIAL',
        'first_name': 'Aline',
        'last_name': 'FOUDA',
        'phone': '+237690222222',
        'username': 'commercial2',
        'manager_email': 'manager@geocommerce.pro',
        'matricule': 'COM-DEMO002',
    },
]


class Command(BaseCommand):
    help = 'Crée ou met à jour les comptes de démonstration'

    def handle(self, *args, **options):
        managers = {}

        for data in DEMO_ACCOUNTS:
            email = data['email']
            password = data['password']
            manager_email = data.pop('manager_email', None)
            matricule = data.pop('matricule', None)
            is_staff = data.pop('is_staff', False)
            is_superuser = data.pop('is_superuser', False)

            user, created = User.objects.update_or_create(
                email=email,
                defaults={
                    'username': data['username'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'role': data['role'],
                    'phone': data['phone'],
                    'is_active': True,
                    'is_staff': is_staff,
                    'is_superuser': is_superuser,
                },
            )
            user.set_password(password)
            user.save()

            if manager_email:
                user.manager = managers.get(manager_email) or User.objects.filter(email=manager_email).first()
                user.save(update_fields=['manager'])

            if data['role'] == 'MANAGER':
                managers[email] = user

            if data['role'] == 'COMMERCIAL' and matricule:
                manager_user = user.manager
                commercial, _ = Commercial.objects.update_or_create(
                    user=user,
                    defaults={
                        'matricule': matricule,
                        'statut': 'ACTIF',
                        'manager': manager_user,
                    },
                )
                ObjectifCommercial.objects.get_or_create(
                    commercial=commercial,
                    periode=ObjectifCommercial.Periode.MENSUEL,
                    annee=2026,
                    mois=6,
                    defaults={'cible': Decimal('5000000')},
                )

            action = 'Créé' if created else 'Mis à jour'
            self.stdout.write(self.style.SUCCESS(f'{action} : {email} / {password}'))

        self.stdout.write(self.style.SUCCESS('\nComptes démo prêts.'))
