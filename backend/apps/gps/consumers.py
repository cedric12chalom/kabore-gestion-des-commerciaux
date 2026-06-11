"""
Consumer WebSocket GPS temps réel.
Groupes : commercial_{id} | manager_{id} | admin_all
"""
import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone

from apps.commerciaux.models import Commercial
from .models import PositionTempsReel, HistoriqueParcours
from .redis_utils import validate_position

logger = logging.getLogger(__name__)


class GPSConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get('user')
        if not self.user or self.user.is_anonymous:
            await self.close(code=4001)
            return

        self.mode = self.scope['url_route']['kwargs'].get('mode', 'track')
        self.groups_joined: list[str] = []

        if self.mode == 'track':
            if not await self._user_is_commercial():
                await self.close(code=4003)
                return
            commercial = await self._get_commercial()
            self.commercial_id = commercial.id
            await self._join_group(f"commercial_{self.commercial_id}")

        elif self.mode == 'watch':
            role = await self._get_user_role()
            if role == 'ADMIN':
                await self._join_group('admin_all')
            elif role == 'MANAGER':
                await self._join_group(f"manager_{self.user.id}")
            else:
                await self.close(code=4003)
                return
        else:
            await self.close(code=4000)
            return

        await self.accept()
        await self.send(text_data=json.dumps({
            'type': 'connected',
            'mode': self.mode,
            'groups': self.groups_joined,
        }))

    async def disconnect(self, close_code):
        for group in self.groups_joined:
            await self.channel_layer.group_discard(group, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        if self.mode != 'track':
            return

        try:
            payload = json.loads(text_data)
        except json.JSONDecodeError:
            await self._send_error('JSON invalide')
            return

        if not self._validate_payload(payload):
            await self._send_error('lat et lng requis')
            return

        allowed, reason = validate_position(self.commercial_id, payload)
        if not allowed:
            await self.send(text_data=json.dumps({'type': 'throttled', 'reason': reason}))
            return

        await self._persist_position(self.commercial_id, payload)
        await self._persist_historique(self.commercial_id, payload)

        broadcast = {
            'type': 'position_update',
            'commercial_id': self.commercial_id,
            'nom': await self._get_commercial_name(),
            'matricule': await self._get_commercial_matricule(),
            'lat': payload['lat'],
            'lng': payload['lng'],
            'accuracy': payload.get('accuracy'),
            'speed': payload.get('speed'),
            'heading': payload.get('heading'),
            'online': True,
            'timestamp': timezone.now().isoformat(),
        }

        manager_id = await self._get_manager_id(self.commercial_id)
        for group in filter(None, [
            f"commercial_{self.commercial_id}",
            f"manager_{manager_id}" if manager_id else None,
            'admin_all',
        ]):
            await self.channel_layer.group_send(
                group, {'type': 'gps.broadcast', 'data': broadcast}
            )

        await self.send(text_data=json.dumps({'type': 'ack', 'status': 'ok'}))

    async def gps_broadcast(self, event):
        await self.send(text_data=json.dumps(event['data']))

    async def _join_group(self, group_name: str):
        await self.channel_layer.group_add(group_name, self.channel_name)
        self.groups_joined.append(group_name)

    async def _send_error(self, message: str):
        await self.send(text_data=json.dumps({'type': 'error', 'message': message}))

    @staticmethod
    def _validate_payload(payload: dict) -> bool:
        return 'lat' in payload and 'lng' in payload

    @database_sync_to_async
    def _persist_position(self, commercial_id, payload):
        commercial = Commercial.objects.get(pk=commercial_id)
        return PositionTempsReel.upsert_from_payload(commercial, payload)

    @database_sync_to_async
    def _persist_historique(self, commercial_id, payload):
        commercial = Commercial.objects.get(pk=commercial_id)
        return HistoriqueParcours.creer_depuis_payload(commercial, payload)

    @database_sync_to_async
    def _get_commercial(self):
        return self.user.commercial_profile

    @database_sync_to_async
    def _user_is_commercial(self):
        return hasattr(self.user, 'commercial_profile')

    @database_sync_to_async
    def _get_user_role(self):
        return self.user.role

    @database_sync_to_async
    def _get_manager_id(self, commercial_id):
        return Commercial.objects.filter(pk=commercial_id).values_list('manager_id', flat=True).first()

    @database_sync_to_async
    def _get_commercial_name(self):
        return self.user.get_full_name()

    @database_sync_to_async
    def _get_commercial_matricule(self):
        return self.user.commercial_profile.matricule
