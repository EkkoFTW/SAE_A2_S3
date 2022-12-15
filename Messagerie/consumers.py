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
        loader = json.loads(event['text'])
        if "sendMessage" == loader['type']:
            await self.channel_layer.group_send("convId"+str(loader['convid']), {"type": "chat_message", "text": event['text']})
        elif "selectConv" == loader['type']:
            try:
                await self.channel_layer.group_discard("convId"+str(loader['old_convid']), self.channel_name)
            except:
                pass
            try:
                await self.channel_layer.group_add("convId"+str(loader['convid']), self.channel_name)
            except:
                pass
            await self.send(event['text'])
        elif "deleteConv" == loader['type']:
            await self.channel_layer.group_send("userId"+str(loader['userid']), {"type": "kickFromConv", "text": event['text']})
            await self.channel_layer.group_send("convId"+str(loader['convid']), {"type": "userToKick", "text": event['text']})
        elif "createConv" == loader['type']:
            await self.send(event['text'])
        elif "addUserToConv" == loader['type']:
            await self.channel_layer.group_send("convId"+str(loader['convid']), {"type": "add_usertoconv", "text": str(event['text'])})
            await self.channel_layer.group_send("userId"+str(loader['userid']), {"type": "got_addedtoconv", "text": str(event['text'])})
        elif "hasBeenKicked" == loader['type']:
            await self.channel_layer.group_discard("convId"+str(loader['convid']), self.channel_name)
        elif "deleteMsg" == loader['type']:
            await self.channel_layer.group_send("convId"+str(loader['convid']), {"type": "msgToDelete", "text": str(event['text'])})

    async def websocket_disconnect(self, event):
        # when websocket disconnects
        print("disconnected", event)

    async def chat_message(self, event):
        await self.send(event['text'])

    async def add_usertoconv(self, event):
        loaded = json.loads(event['text'])
        loaded['type'] = "add_usertoconv"
        await self.send(json.dumps(loaded))

    async def got_addedtoconv(self, event):
        loaded = json.loads(event['text'])
        loaded['type'] = "got_addedtoconv"
        await self.send(json.dumps(loaded))

    async def kickFromConv(self, event):
        loaded = json.loads(event['text'])
        loaded['type'] = "kickFromConv"
        await self.send(json.dumps(loaded))

    async def userToKick(self, event):
        loaded = json.loads(event['text'])
        loaded['type'] = "userToKick"
        await self.send(json.dumps(loaded))

    async def msgToDelete(self, event):
        loaded = json.loads(event['text'])
        loaded['type'] = "msgToDelete"
        await self.send(json.dumps(loaded))