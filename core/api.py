import json
import urllib

from django.db.models import Q, Count
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django.contrib.sessions.models import Session
from convabout import settings
from core.serializers import MessageModelSerializer, PostModelSerializer, MyTalksPostModelSerializer
from core.models import MessageModel
from core.models import Post
from rest_framework.permissions import AllowAny
from rest_framework import generics, views
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.status import (HTTP_200_OK, HTTP_400_BAD_REQUEST, 
    HTTP_202_ACCEPTED, HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT)
from rest_framework import status
from rest_framework.decorators import api_view
from django_eventstream import send_event
from django.db.models import BooleanField, Case, When, Value
from django.db import connection
import logging
import sys

@api_view(['POST'])
def respond(request):

    ''' Begin reCAPTCHA validation '''
    recaptcha_response = request.data['g-recaptcha-response']

    url = 'https://www.google.com/recaptcha/api/siteverify'
    values = {
        'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
        'response': recaptcha_response
    }
    data = urllib.parse.urlencode(values).encode()
    req =  urllib.request.Request(url, data=data)
    response = urllib.request.urlopen(req)
    recaptcha_result = json.loads(response.read().decode())
    ''' End reCAPTCHA validation '''

    if recaptcha_result['success']:
        post_id = request.data["post_id"]            
        if not request.session.session_key:
            request.session.create() 
        try:
            responder = Session.objects.get(session_key=request.session.session_key)
        except Session.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)     
        try:
            post = Post.objects.get(id=post_id)
        except Session.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if post.user.session_key==responder.session_key:
            return Response(status=status.HTTP_200_OK)   

        if post.responder is not None:
            return Response(status=status.HTTP_409_CONFLICT) 

        post.responder = responder
        post.save()
        send_event('home', 'response', {'post_id': post_id})
        return Response(status=status.HTTP_200_OK) 
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def not_seen_present(request):
    user_messages = MessageModel.objects.filter(recipient__session_key=request.session.session_key, seen=False)
    return Response({"number": user_messages.count()}, status=status.HTTP_200_OK) 

@api_view(['GET'])
def talk_present(request):
    user_talks = Post.objects.filter(Q(user__session_key=request.session.session_key)  
                                     | Q(responder__session_key=request.session.session_key))
    return Response({"number": user_talks.count()}, status=status.HTTP_200_OK) 

@api_view(['GET'])
def number_of_not_seen_messages(request):
    # not working
    #not_seen_recipient_messages = MessageModel.objects.filter(
        #Q(recipient__session_key=request.session.session_key))
        #& Q(seen=False))
    #grouped = not_seen_recipient_messages.values('post').annotate(pcount=Count('post'))

    # IMPORTANT production/development: use "seen = false" for postgresql and "seen = 0" for sqllite
    sql= ('SELECT post_id AS id, COUNT(post_id) AS pcount FROM core_MessageModel WHERE seen = false AND recipient_id = %s GROUP BY post_id')
    cursor = connection.cursor()
    try:
        cursor.execute(sql, [request.session.session_key])
        rows = cursor.fetchall()
    except:
        raise
    finally:
        cursor.close()
    return Response(rows, status=status.HTTP_200_OK) 

class MyTalksListAPIView(generics.ListAPIView):
    serializer_class = MyTalksPostModelSerializer
    pagination_class = None  # Get all
    def get_queryset(self):
        if not self.request.session.session_key:
            self.request.session.create()   
            queryset = Post.objects.none()     
        else: 
            queryset = Post.objects.filter(Q(user__session_key=self.request.session.session_key) |
                                             Q(responder__session_key=self.request.session.session_key))			
        return queryset

class MessagePagination(PageNumberPagination):
    """
    Limit message prefetch to one page.
    """
    page_size = settings.MESSAGES_TO_LOAD



class MessageModelViewSet(ModelViewSet):
    queryset = MessageModel.objects.all()
    serializer_class = MessageModelSerializer
    allowed_methods = ('GET', 'HEAD', 'OPTIONS')
    #pagination_class = MessagePagination


 #   authentication_classes = (CsrfExemptSessionAuthentication,)
	
    def list(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter(Q(user__session_key=request.session.session_key) |
                                             Q(recipient__session_key=request.session.session_key))
        target = self.request.query_params.get('target', None)
        if target is not None:
            post = get_object_or_404(Post, pk=target)			
            if not (post.user.session_key == request.session.session_key or
                    post.responder.session_key == request.session.session_key):
                return Response(status=status.HTTP_403_FORBIDDEN)			
            self.queryset = self.queryset.filter(post__id=target)
            for message in self.queryset:
                message.seen = True
                message.save()
        return super(MessageModelViewSet, self).list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        msg = get_object_or_404(self.queryset, pk=kwargs['pk'])
        if not (msg.user.session_key == request.session.session_key or
                msg.recipient.session_key == request.session.session_key):
            return Response(status=status.HTTP_403_FORBIDDEN)			
        serializer = self.get_serializer(msg)
        return Response(serializer.data)


class PostModelViewSet(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostModelSerializer
    allowed_methods = ('GET', 'HEAD', 'OPTIONS','POST')
    pagination_class = None  # Get all

    def list(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter(responder__isnull=True)
        tag = self.request.query_params.get('tag', None)
        if tag is not None:
            self.queryset = self.queryset.filter(Q(tags__icontains=tag))	

        q = self.request.query_params.get('q', None)
        if q is not None:
            self.queryset = self.queryset.filter(Q(title__icontains=q)|
                                                Q(body__icontains=q)|
                                                Q(tags__icontains=q))													
        return super(PostModelViewSet, self).list(request, *args, **kwargs)

    """
    Create a model instance.
    """
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        ''' Begin reCAPTCHA validation '''
        recaptcha_response = request.data['g-recaptcha-response']

        url = 'https://www.google.com/recaptcha/api/siteverify'
        values = {
            'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }
        data = urllib.parse.urlencode(values).encode()
        req =  urllib.request.Request(url, data=data)
        response = urllib.request.urlopen(req)
        recaptcha_result = json.loads(response.read().decode())
        ''' End reCAPTCHA validation '''

        if recaptcha_result['success']:
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save()
