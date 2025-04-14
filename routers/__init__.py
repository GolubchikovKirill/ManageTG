from routers.auth import router as auth_router
from routers.сommenting import router as commenting
from routers.channels import router as channels_router
from routers.proxy import router as proxy_router
from routers.actions import  router as actions

routers = [
    auth_router,
    commenting,
    channels_router,
    proxy_router,
    actions,
]