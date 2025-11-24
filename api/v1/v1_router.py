# api/v1/v1_router.py

from fastapi import APIRouter
from api.v1.system_router import system_router


v1_router = APIRouter(tags=["api", "v1"])

v1_router.include_router(system_router,
                         prefix="/system")

@v1_router.get("/")
async def ready():
    return {"message": "v1 api ready"}