from app.routes.auth import router as auth_router
from app.routes.channels import router as channels_router
from app.routes.proxy import router as proxy_router
from app.routes.accounts import router as accounts
from app.routes.comments import router as commenting
from app.routes.reactions import router as reactions
from app.routes.views import router as views

routers = [
    auth_router,
    commenting,
    channels_router,
    proxy_router,
    accounts,
    reactions,
    views,
]