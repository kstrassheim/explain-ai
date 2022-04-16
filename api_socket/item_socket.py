import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.urls import re_path
from api.auth import process_authorization

urls = [] 
class ItemConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            access_token = self.scope["subprotocols"][0]
            login_name = process_authorization(access_token)["login"]
            #await self.send({'statusCode': 200})
            await self.accept(subprotocol=access_token)
            # subscript own channel name to group
            await self.channel_layer.group_add("item", self.channel_name)
        except:
            #await self.send({'statusCode': 403}, close=True)
            await self.close()
        
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("item", self.channel_name)
        #await self.close()

    # dont change the method params
    async def receive(self, text_data):
        item = json.loads(text_data)
        #raise group event
        await self.channel_layer.group_send("item", {
            "type": "item.info",
            "operation": "info",
            "item": item
        })

    async def item_info(self, event):
        # Send a group event down to the client
        await self.send(text_data=json.dumps(event))


urls+=[re_path(r'socket/itemsocket', ItemConsumer.as_asgi())]