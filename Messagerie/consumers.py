from channels.generic.websocket import AsyncJsonWebsocketConsumer
from asgiref.sync import async_to_sync
import json


class PracticeConsumer(AsyncJsonWebsocketConsumer):
    async def websocket_connect(self, event):
        # when websocket connects
        await self.channel_layer.group_add("0", self.channel_name)
        await self.accept()

    async def websocket_receive(self, event):
        # when messages is received from websocket

        await self.channel_layer.group_send("0", {"type": "chat_message", "text": event['text']})


    async def websocket_disconnect(self, event):
        # when websocket disconnects
        print("disconnected", event)

    async def chat_message(self, event):
        await self.send(event['text'])