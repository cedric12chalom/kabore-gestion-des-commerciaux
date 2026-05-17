"""
Views pour Notifications et Messagerie
"""
from rest_framework import generics, status, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q, Count
from django.utils import timezone

from .models import Notification, Message


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer inline"""
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    priorite_display = serializers.CharField(source='get_priorite_display', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'type', 'type_display', 'priorite', 'priorite_display',
            'titre', 'message', 'objet_type', 'objet_id',
            'is_lue', 'is_envoyee', 'date_creation', 'date_lecture',
        ]


class NotificationListView(generics.ListAPIView):
    """GET /api/v1/notifications/ - Notifications de l'utilisateur connecté"""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(
            destinataire=self.request.user
        ).order_by('-date_creation')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def marquer_lue_view(request, notification_id):
    """POST /api/v1/notifications/<id>/lue/"""
    try:
        notif = Notification.objects.get(id=notification_id, destinataire=request.user)
        notif.is_lue = True
        notif.date_lecture = timezone.now()
        notif.save()
        return Response({'success': True})
    except Notification.DoesNotExist:
        return Response({'success': False, 'error': 'Notification non trouvée'}, status=404)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def marquer_toutes_lues_view(request):
    """POST /api/v1/notifications/lues/"""
    Notification.objects.filter(
        destinataire=request.user,
        is_lue=False
    ).update(is_lue=True, date_lecture=timezone.now())

    return Response({'success': True, 'message': 'Toutes les notifications marquées comme lues'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notifications_non_lues_view(request):
    """GET /api/v1/notifications/non-lues/ - Compteur notifications"""
    count = Notification.objects.filter(
        destinataire=request.user,
        is_lue=False
    ).count()

    recentes = Notification.objects.filter(
        destinataire=request.user,
        is_lue=False
    ).order_by('-date_creation')[:5]

    serializer = NotificationSerializer(recentes, many=True)

    return Response({
        'success': True,
        'count': count,
        'recentes': serializer.data,
    })


# ========== MESSAGERIE ==========

class MessageSerializer(serializers.ModelSerializer):
    """Serializer inline"""
    expediteur_nom = serializers.CharField(source='expediteur.get_full_name', read_only=True)
    destinataire_nom = serializers.CharField(source='destinataire.get_full_name', read_only=True)

    class Meta:
        model = Message
        fields = [
            'id', 'expediteur', 'expediteur_nom',
            'destinataire', 'destinataire_nom',
            'contenu', 'client', 'visite',
            'is_lu', 'date_lecture', 'date_envoi',
        ]


class MessageListCreateView(generics.ListCreateAPIView):
    """GET/POST /api/v1/notifications/messages/"""
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Messages où l'utilisateur est expéditeur OU destinataire
        return Message.objects.filter(
            Q(expediteur=user) | Q(destinataire=user)
        ).select_related('expediteur', 'destinataire').order_by('-date_envoi')

    def perform_create(self, serializer):
        serializer.save(expediteur=self.request.user)


class ConversationView(generics.ListAPIView):
    """GET /api/v1/notifications/messages/<user_id>/ - Conversation avec un utilisateur"""
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        other_id = self.kwargs.get('user_id')
        return Message.objects.filter(
            Q(expediteur=user, destinataire_id=other_id) |
            Q(expediteur_id=other_id, destinataire=user)
        ).select_related('expediteur', 'destinataire').order_by('date_envoi')


# Import serializers
from rest_framework import serializers
