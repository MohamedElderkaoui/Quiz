import asyncio
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class QuizTimerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = "quiz_timer"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """Recibe mensajes del cliente (si es necesario)."""
        data = json.loads(text_data)
        action = data.get("action")

        if action == "start_timer":
            await self.start_countdown()

    async def start_countdown(self):
        """Inicia la cuenta atrás de 30 segundos y envía actualizaciones cada segundo."""
        for seconds_remaining in range(30, -1, -1):
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "send_timer",
                    "seconds_remaining": seconds_remaining
                }
            )
            await asyncio.sleep(1)

    async def send_timer(self, event):
        """Envía la cuenta atrás a los clientes."""
        await self.send(text_data=json.dumps({
            "seconds_remaining": event["seconds_remaining"]
        }))
