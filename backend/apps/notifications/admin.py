"""
Admin Django pour Notifications
"""
from django.contrib import admin
from .models import Notification, Message


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['destinataire', 'type', 'titre', 'is_lue', 'date_creation']
    list_filter = ['type', 'is_lue', 'priorite']
    search_fields = ['titre', 'message']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['expediteur', 'destinataire', 'contenu_truncated', 'is_lu', 'date_envoi']
    list_filter = ['is_lu']
    search_fields = ['contenu']

    def contenu_truncated(self, obj):
        return obj.contenu[:50] + '...' if len(obj.contenu) > 50 else obj.contenu
    contenu_truncated.short_description = 'Contenu'
