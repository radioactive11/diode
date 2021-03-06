import imp
from fastapi import APIRouter

from app.api.v1.endpoints import touch, details, instance, deploy

api_router = APIRouter()


api_router.include_router(touch.router, prefix="/touch")
api_router.include_router(details.router, prefix="/details")
api_router.include_router(instance.router, prefix="/instance")
api_router.include_router(deploy.router, prefix="/deploy")
