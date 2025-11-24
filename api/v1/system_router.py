# api/v1/system_router.py

from fastapi import APIRouter
from services import system_service

system_router = APIRouter(tags=["system"])

@system_router.get("/update_application")
async def update_application():
    return system_service.update_application()
