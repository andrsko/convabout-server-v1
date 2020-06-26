from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
from core.api import (MessageModelViewSet, PostModelViewSet, respond, MyTalksListAPIView,
    number_of_not_seen_messages, not_seen_present, talk_present, site_contact)
router = DefaultRouter()
router.register(r'message', MessageModelViewSet, basename='message-api')
router.register(r'post', PostModelViewSet, basename='post-api')

urlpatterns = [
    path(r'api/v1/', include(router.urls)),
    path('api/v1/respond/', respond, name='respond'),    
    path('api/v1/my_talks/', MyTalksListAPIView.as_view(), name="my-talks"),
    path('api/v1/number_of_not_seen_messages/', number_of_not_seen_messages, name='number-of-not-seen-messages'),    
    path('api/v1/not_seen_present/', not_seen_present, name='not-seen-present'),    
    path('api/v1/talk_present/', talk_present, name='talk-present'),    
     path('api/v1/contact/', site_contact, name='site-contact'),     
]
