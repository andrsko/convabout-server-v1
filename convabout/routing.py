from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from core import routing as core_routing

application = ProtocolTypeRouter({
    "websocket": AuthMiddlewareStack(
        URLRouter(
            core_routing.websocket_urlpatterns
        )
    ),
    'http': AuthMiddlewareStack(URLRouter(core_routing.urlpatterns)),
})
