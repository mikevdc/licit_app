from fastapi import APIRouter
from app.api.v1.endpoints import auctions, users, auth

api_router = APIRouter()
api_router.include_router(auctions.router, tags = ["Auctions"])
api_router.include_router(users.router, tags = ["Users"])
api_router.include_router(auth.router, tags = ["Auth"])
