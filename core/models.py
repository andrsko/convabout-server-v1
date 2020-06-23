from django.contrib.auth.models import User
from django.db.models import (Model, TextField, DateTimeField, ForeignKey, CharField,
                              BooleanField, CASCADE)
from django.contrib.sessions.models import Session
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json
from django_eventstream import send_event


class Post(Model):
    user = ForeignKey(Session, on_delete=CASCADE, verbose_name='user',
                      related_name='posts')
    responder = ForeignKey(Session, on_delete=CASCADE, verbose_name='responder',
                      related_name='posts_responded_to', null=True, blank=True)					  
    timestamp = DateTimeField('timestamp', auto_now_add=True, editable=False,
                              db_index=True)	
    title = CharField(max_length=150)
    tags = CharField(max_length=150, null=True, blank=True)	
    body = CharField(max_length=500, null=True, blank=True)	
	
class MessageModel(Model):
    """
    This class represents a chat message. It has a owner (post.user), timestamp and
    the message body.

    """
    user = ForeignKey(Session, on_delete=CASCADE, verbose_name='user',
                      related_name='sent_messages', db_index=True, null=True)
    recipient = ForeignKey(Session, on_delete=CASCADE, verbose_name='recipient',
                           related_name='received_messages', db_index=True, null=True)
    post = ForeignKey(Post, on_delete=CASCADE, verbose_name='post',
                           related_name='messages', db_index=True, null=True)
    timestamp = DateTimeField('timestamp', auto_now_add=True, editable=False,
                              db_index=True)
    body = TextField('body')

    seen = BooleanField('seen', default=False)

    def __str__(self):
        return str(self.id)

    def characters(self):
        """
        Toy function to count body characters.
        :return: body's char number
        """
        return len(self.body)

    def notify_ws_clients(self):
        """
        Inform client there is a new message.
        """
        message = {
            "user_session_key": self.user.session_key, 
            "id":self.id,
            "post_id":self.post.id,
            "timestamp":self.timestamp,
            "body":self.body
        }
        notification = {
            'type': 'recieve_group_message',
            'message': json.dumps(message, indent=4, sort_keys=True, default=str)
        }

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)("{}".format(self.user.session_key), notification)
        async_to_sync(channel_layer.group_send)("{}".format(self.recipient.session_key), notification)

    def notify_es_clients(self):
        """
        Inform client there is a new message.
        """
        send_event('home', 'new_message',{})

    def save(self, *args, **kwargs):
        """
        Trims white spaces, saves the message and notifies the recipient via WS
        if the message is new.
        """
        new = self.id
        self.body = self.body.strip()  # Trimming whitespaces from the body
        super(MessageModel, self).save(*args, **kwargs)
        if new is None:
            self.notify_ws_clients()
            self.notify_es_clients()

    # Meta
    class Meta:
        app_label = 'core'
        verbose_name = 'message'
        verbose_name_plural = 'messages'
        ordering = ('-timestamp',)
