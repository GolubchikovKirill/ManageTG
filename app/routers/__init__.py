from app.routers.auth import router as auth_router
from app.routers.channels import router as channels_router
from app.routers.proxy import router as proxy_router
from app.routers.accounts import router as accounts
from app.routers.comments import router as commenting
from app.routers.reactions import router as reactions
from app.routers.views import router as views

routers = [
    auth_router,
    commenting,
    channels_router,
    proxy_router,
    accounts,
    reactions,
    views,
]