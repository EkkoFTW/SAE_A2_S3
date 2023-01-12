from channels.generic.websocket import AsyncJsonWebsocketConsumer
from asgiref.sync import async_to_sync
import json
import time


class PracticeConsumer(AsyncJsonWebsocketConsumer):
    async def websocket_connect(self, event):
        # when websocket connects
        await self.channel_layer.group_add("userId"+str(self.scope['user'].id), self.channel_name)
        await self.accept()

    async def websocket_receive(self, event):
        # when messages is received from websocket
        print(event)
        loader = json.loads(event['text'])

    async def websocket_disconnect(self, event):
        # when websocket disconnects
        print("disconnected", event)

    async def sendMessage(self, event):
        await self.send(json.dumps(event))

    async def add_usertoconv(self, event):
        await self.send(json.dumps(event))

    async def got_addedtoconv(self, event):
        await self.send(json.dumps(event))

    async def kickFromConv(self, event):
        await self.channel_layer.group_discard("convId"+str(event['convid']), self.channel_name)
        await self.send(json.dumps(event))

    async def userToKick(self, event):
        await self.send(json.dumps(event))

    async def msgToDelete(self, event):
        await self.send(json.dumps(event))

    async def createConv(self, event):
        await self.send(json.dumps(event))

    async def discardConvGroup(self, event):
        await self.channel_layer.group_discard("convId"+str(event['old_convid']), self.channel_name)

    async def addConvGroup(self, event):
        await self.channel_layer.group_add("convId"+str(event['convid']), self.channel_name)

    async def selectConv(self, event):
        await self.send(json.dumps(event))

    async def editMsg(self, event):
        await self.send(json.dumps(event))
