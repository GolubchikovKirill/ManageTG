from routers.auth import router as auth_router
from routers.launching_actions import router as commenting
from routers.channels import router as channels_router
from routers.proxy import router as proxy_router
from routers.actions import  router as actions
from routers.accounts import router as accounts

routers = [
    auth_router,
    commenting,
    channels_router,
    proxy_router,
    actions,
    accounts,
]