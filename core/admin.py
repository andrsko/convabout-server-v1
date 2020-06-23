from django.contrib.admin import ModelAdmin, site
from core.models import MessageModel
from core.models import Post

site.register(Post)
site.register(MessageModel)
