# app/main.py

from fastapi import FastAPI
from api.v1.v1_router import v1_router
from app.state import configure_state, shutdown_state
from app.container import DependencyContainer
from app.dependencies.container_keys import CONTAINER_KEY


dependency_container = DependencyContainer()

app = FastAPI(description="home-automation-service")

setattr(app.state, CONTAINER_KEY, dependency_container)

app.add_event_handler('startup', lambda: configure_state(app) )
app.add_event_handler('shutdown', lambda: shutdown_state(app) )

app.include_router(v1_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Hello World"}
