"""
Consumer WebSocket pour streaming GPS temps réel
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


class GPSConsumer(AsyncWebsocketConsumer):
    """
    Consumer WebSocket pour recevoir les positions GPS en temps réel
    d'un commercial spécifique.
    """

    async def connect(self):
        self.commercial_id = self.scope['url_route']['kwargs']['commercial_id']
        self.room_group_name = f"gps_{self.commercial_id}"

        # Vérifier l'authentification
        if self.scope["user"].is_anonymous:
            await self.close()
            return

        # Rejoindre le groupe
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Envoyer un message de confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection',
            'message': f'Connecté au stream GPS du commercial {self.commercial_id}'
        }))

    async def disconnect(self, close_code):
        # Quitter le groupe
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """Recevoir une position GPS du client WebSocket"""
        data = json.loads(text_data)

        position_data = {
            'type': 'position',
            'commercial_id': self.commercial_id,
            'latitude': data.get('latitude'),
            'longitude': data.get('longitude'),
            'vitesse': data.get('vitesse'),
            'timestamp': data.get('timestamp'),
        }

        # Diffuser à tous les clients du groupe
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'gps_position',
                'message': position_data
            }
        )

    async def gps_position(self, event):
        """Recevoir une position du groupe et l'envoyer au client"""
        await self.send(text_data=json.dumps(event['message']))
