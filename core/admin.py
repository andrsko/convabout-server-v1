from django.contrib.admin import ModelAdmin, site
from core.models import MessageModel, Post, SiteContacted

site.register(Post)
site.register(MessageModel)
site.register(SiteContacted)
