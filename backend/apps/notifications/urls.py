"""
URLs pour l'app notifications
"""
from django.urls import path
from .views import (
    NotificationListView, marquer_lue_view, marquer_toutes_lues_view,
    notifications_non_lues_view,
    MessageListCreateView, ConversationView,
)

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
    path('non-lues/', notifications_non_lues_view, name='notifications-non-lues'),
    path('<int:notification_id>/lue/', marquer_lue_view, name='notification-lue'),
    path('lues/', marquer_toutes_lues_view, name='notifications-toutes-lues'),

    # Messagerie
    path('messages/', MessageListCreateView.as_view(), name='message-list'),
    path('messages/<int:user_id>/', ConversationView.as_view(), name='conversation'),
]
