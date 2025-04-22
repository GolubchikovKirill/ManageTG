from routers.auth import router as auth_router
from routers.channels import router as channels_router
from routers.proxy import router as proxy_router
from routers.accounts import router as accounts
from routers.commenting import router as commenting
from routers.reactions import router as reactions
from routers.views import router as views

routers = [
    auth_router,
    commenting,
    channels_router,
    proxy_router,
    accounts,
    reactions,
    views,
]