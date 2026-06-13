# Generated manually — visites gérées par le manager (contrôle points de vente)

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def clear_visites(apps, schema_editor):
    Visite = apps.get_model('visites', 'Visite')
    Visite.objects.all().delete()


def get_default_manager_id(apps, schema_editor):
    User = apps.get_model('users', 'User')
    manager = User.objects.filter(role='MANAGER').order_by('id').first()
    if not manager:
        manager = User.objects.order_by('id').first()
    return manager.id if manager else 1


class Migration(migrations.Migration):

    dependencies = [
        ('visites', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(clear_visites, migrations.RunPython.noop),
        migrations.RemoveIndex(
            model_name='visite',
            name='visites_vis_commerc_6a50a6_idx',
        ),
        migrations.RemoveIndex(
            model_name='visite',
            name='visites_vis_contact_25e8a2_idx',
        ),
        migrations.RemoveField(
            model_name='visite',
            name='commercial',
        ),
        migrations.RemoveField(
            model_name='visite',
            name='satisfaction_client',
        ),
        migrations.RenameField(
            model_name='visite',
            old_name='contact_nom',
            new_name='point_vente_nom',
        ),
       migrations.AddField(
    model_name='visite',
    name='manager',
    field=models.ForeignKey(
        null=True,
        blank=True,
        limit_choices_to={'role': 'MANAGER'},
        on_delete=django.db.models.deletion.CASCADE,
        related_name='visites',
        to=settings.AUTH_USER_MODEL,
        verbose_name='manager',
    ),
),
        migrations.AlterField(
            model_name='visite',
            name='type_visite',
            field=models.CharField(
                choices=[
                    ('CONTROLE_PDV', 'Contrôle point de vente'),
                    ('REGULIERE', 'Visite régulière'),
                    ('RECOUVREMENT', 'Recouvrement'),
                    ('LIVRAISON', 'Livraison'),
                    ('PRESENTATION', 'Présentation produit'),
                    ('AUTRE', 'Autre'),
                ],
                default='CONTROLE_PDV',
                max_length=20,
                verbose_name='type',
            ),
        ),
        migrations.RenameField(
            model_name='rapportvisite',
            old_name='besoins_client',
            new_name='constats',
        ),
        migrations.AddIndex(
            model_name='visite',
            index=models.Index(fields=['manager', 'statut', 'date_prevue'], name='visites_vis_manager_idx'),
        ),
        migrations.AddIndex(
            model_name='visite',
            index=models.Index(fields=['point_vente_nom', 'date_prevue'], name='visites_vis_pdv_idx'),
        ),
    ]
