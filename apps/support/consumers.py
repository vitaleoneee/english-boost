from time import monotonic

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from apps.support.exceptions import SupportServiceError
from apps.support.models import SupportRequest
from apps.support.permissions import is_moderator
from apps.support.realtime import MODERATOR_CHANNEL_GROUP
from apps.support.services import send_support_message


class SupportConsumer(AsyncJsonWebsocketConsumer):
    MESSAGE_MIN_INTERVAL_SECONDS = 0.5

    async def connect(self):
        self.request_id = self.scope["url_route"]["kwargs"]["request_id"]
        self.group_name = f"support.request.{self.request_id}"
        self.last_message_at = 0.0

        connection_data = await self._get_connection_data()
        if connection_data["close_code"] is not None:
            await self.close(code=connection_data["close_code"])
            return

        self.user_is_moderator = connection_data["is_moderator"]
        self.user_is_owner = connection_data["is_owner"]
        self.request_status = connection_data["status"]
        self.request_can_rate = connection_data["can_rate"]

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.send_json(
            {
                "type": "request.state",
                "request_id": self.request_id,
                "status": self.request_status,
                "can_send_messages": self._can_send_messages(self.request_status),
                "can_rate": self.request_can_rate,
            }
        )
        await self.send_json(
            {
                "type": "message.history",
                "messages": connection_data["messages"],
            }
        )

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name,
            )

    async def receive_json(self, content, **kwargs):
        if not isinstance(content, dict):
            await self._send_error("INVALID_EVENT", "WebSocket event must be an object")
            return

        if content.get("type") != "message.send":
            await self._send_error("UNSUPPORTED_EVENT", "Unsupported WebSocket event")
            return

        now = monotonic()
        if now - self.last_message_at < self.MESSAGE_MIN_INTERVAL_SECONDS:
            await self._send_error(
                "RATE_LIMITED", "Messages are being sent too quickly"
            )
            return
        self.last_message_at = now

        try:
            result = await self._send_support_message(content.get("text"))
        except SupportServiceError as error:
            await self._send_error(error.code, str(error))
            return

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "support.message.created",
                **result,
            },
        )
        if result["status_changed"]:
            await self.channel_layer.group_send(
                MODERATOR_CHANNEL_GROUP,
                {
                    "type": "support.request.status_changed",
                    "request_id": self.request_id,
                    "status": result["status"],
                },
            )

    async def support_message_created(self, event):
        self.request_status = event["status"]
        await self.send_json(
            {
                "type": "message.created",
                "message": event["message"],
            }
        )

        if event["status_changed"]:
            await self._send_status_changed(self.request_status)

    async def support_request_status_changed(self, event):
        self.request_status = event["status"]
        await self._send_status_changed(self.request_status)

    async def _send_status_changed(self, status):
        self.request_can_rate = (
            self.user_is_owner and status == SupportRequest.Status.CLOSED
        )
        await self.send_json(
            {
                "type": "request.status_changed",
                "status": status,
                "can_send_messages": self._can_send_messages(status),
                "can_rate": self.request_can_rate,
            }
        )

    async def _send_error(self, code, message):
        await self.send_json(
            {
                "type": "error",
                "code": code,
                "message": message,
            }
        )

    def _can_send_messages(self, status):
        if status == SupportRequest.Status.CLOSED:
            return False
        if status == SupportRequest.Status.IN_PROGRESS:
            return True
        return self.user_is_moderator

    @database_sync_to_async
    def _get_connection_data(self):
        user = self.scope["user"]
        if not user.is_authenticated:
            return self._denied_connection(close_code=4401)

        try:
            support_request = SupportRequest.objects.select_related(
                "user", "rating"
            ).get(pk=self.request_id)
        except SupportRequest.DoesNotExist:
            return self._denied_connection(close_code=4404)

        user_is_moderator = is_moderator(user)
        user_is_owner = support_request.user_id == user.pk
        if not user_is_owner and not user_is_moderator:
            return self._denied_connection(close_code=4403)

        messages = [
            self._serialize_message(message, support_request.user_id)
            for message in support_request.messages.select_related("author").all()
        ]
        return {
            "close_code": None,
            "is_moderator": user_is_moderator,
            "is_owner": user_is_owner,
            "status": support_request.status,
            "can_rate": (
                user_is_owner
                and support_request.status == SupportRequest.Status.CLOSED
                and not hasattr(support_request, "rating")
            ),
            "messages": messages,
        }

    @database_sync_to_async
    def _send_support_message(self, text):
        result = send_support_message(
            request_id=self.request_id,
            author=self.scope["user"],
            text=text,
        )
        return {
            "message": self._serialize_message(
                result.message,
                result.request.user_id,
            ),
            "status": result.request.status,
            "status_changed": result.status_changed,
        }

    @staticmethod
    def _serialize_message(message, request_user_id):
        author_role = "user" if message.author_id == request_user_id else "moderator"
        return {
            "id": message.pk,
            "author": author_role,
            "author_name": message.author.get_username(),
            "text": message.text,
            "created_at": message.created_at.isoformat(),
        }

    @staticmethod
    def _denied_connection(close_code):
        return {
            "close_code": close_code,
            "is_moderator": False,
            "is_owner": False,
            "status": None,
            "can_rate": False,
            "messages": [],
        }


class ModeratorQueueConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if not user.is_authenticated:
            await self.close(code=4401)
            return
        if not await self._is_moderator(user):
            await self.close(code=4403)
            return

        await self.channel_layer.group_add(
            MODERATOR_CHANNEL_GROUP,
            self.channel_name,
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            MODERATOR_CHANNEL_GROUP,
            self.channel_name,
        )

    async def support_request_created(self, event):
        await self.send_json(
            {
                "type": "request.created",
                "request_id": event["request_id"],
            }
        )

    async def support_request_status_changed(self, event):
        await self.send_json(
            {
                "type": "request.status_changed",
                "request_id": event["request_id"],
                "status": event["status"],
            }
        )

    @database_sync_to_async
    def _is_moderator(self, user):
        return is_moderator(user)
