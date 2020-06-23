from core import consumers
from django.conf.urls import url
from channels.routing import URLRouter
from channels.http import AsgiHandler
import django_eventstream

websocket_urlpatterns = [
    url(r'^ws$', consumers.ChatConsumer),
]
urlpatterns = [
    url(r'^events/', 
        URLRouter(django_eventstream.routing.urlpatterns)
    , {'channels': ['home']}),
    url(r'', AsgiHandler),
]
