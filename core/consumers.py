
# chat/consumers.py

from channels.generic.websocket import AsyncWebsocketConsumer
import json
from django.contrib.sessions.models import Session
from core.models import MessageModel, Post
from channels.db import database_sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user_id = self.scope["session"].session_key

        self.group_name = "{}".format(user_id)
        # Join room group

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data=None,bytes_data = None):
        text_data_json = json.loads(text_data)
        if text_data_json['type'] == "save":
            await self.save_message(text_data_json)
        elif text_data_json['type'] == "seen":
            await self.mark_message_as_seen(text_data_json)

    
    @database_sync_to_async
    def save_message(self, text_data_json):
        try:
            user = Session.objects.get(session_key=self.scope["session"].session_key)
        except Session.DoesNotExist:
            return "error"          
        try:
            post = Post.objects.get(id=int(text_data_json['post_id']))
        except Post.DoesNotExist:
            return "error"        	
        recipient_session_key = (post.responder.session_key
                                 if (post.user.session_key
                                 == self.scope["session"].session_key) 
                                 else post.user.session_key)
        try:
            recipient = Session.objects.get(session_key=recipient_session_key)
        except Session.DoesNotExist:
            return "error"			
        msg = MessageModel(recipient=recipient,
                           body=text_data_json['body'],
                           user=user, post=post)
        msg.save()  

    @database_sync_to_async
    def mark_message_as_seen(self, text_data_json):    
        try:
            message = MessageModel.objects.get(id=int(text_data_json['message_id']))
        except MessageModel.DoesNotExist:
            return "error"        	
        if not message.recipient.session_key == self.scope["session"].session_key:
            return "error" 
        message.seen=True
        message.save()  

    async def recieve_group_message(self, event):
        message = json.loads(event['message'])
        message['is_author']=self.scope["session"].session_key==message["user_session_key"]
        del message["user_session_key"]

        # Send message to WebSocket
        await self.send(
             text_data=json.dumps(message, indent=4, sort_keys=True, default=str))