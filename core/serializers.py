from django.contrib.sessions.models import Session
from django.shortcuts import get_object_or_404
from core.models import Post, MessageModel, SiteContacted
from rest_framework.serializers import ModelSerializer, CharField, BooleanField, EmailField
from rest_framework import serializers
from rest_framework import status
from django_eventstream import send_event


class MessageModelSerializer(ModelSerializer):
    post_id = CharField(source='post.id')
    is_author = serializers.SerializerMethodField()

    def get_is_author(self, obj):
        message = obj
        return message.user.session_key == self.context['request'].session.session_key
		
    class Meta:
        model = MessageModel
        fields = ('id', 'is_author', 'post_id', 'timestamp', 'body')

class PostModelSerializer(ModelSerializer):
    id = serializers.ReadOnlyField()
    timestamp = serializers.ReadOnlyField()

    def create(self, validated_data):

        if not self.context['request'].session.session_key:
            self.context['request'].session.create() 
        try:
            user = Session.objects.get(session_key=self.context['request'].session.session_key)
        except Session.DoesNotExist:
            msg = _('Problem with session initialization.')
            raise serializers.ValidationError(msg, code='authorization')

        post = Post(user=user,title=validated_data['title'],
                           body=validated_data['body'],
                           tags=validated_data['tags'])
        post.save()
        send_event('home', 'new_post', {
            'id': post.id,
            'title': post.title,
            'body': post.body,
            'tags': post.tags,
            'timestamp':post.timestamp
            })
        return post
        
    class Meta:
        model = Post
        fields = ('id', 'title', 'timestamp', 'body', 'tags')

class MyTalksPostModelSerializer(ModelSerializer):
    is_author = serializers.SerializerMethodField()

    def get_is_author(self, obj):
        post = obj
        return post.user.session_key == self.context['request'].session.session_key
		
    class Meta:
        model = Post
        fields = ('id', 'title', 'timestamp', 'body', 'tags', 'is_author')

class SiteContactedSerializer(ModelSerializer):
    class Meta:
        model = SiteContacted
        fields = ['message', 'name', 'email']