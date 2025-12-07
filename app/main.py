# app/main.py

from fastapi import FastAPI
from api.v1.v1_router import v1_router
from app.state import configure_state, shutdown_state
from app.container import DependencyContainer
from app.dependencies.container_keys import CONTAINER_KEY

# Create the dependency container
dependency_container = DependencyContainer()

# Start the FastAPI application
app = FastAPI(description="home-automation-service")

# Attach the dependency container to the application state
setattr(app.state, CONTAINER_KEY, dependency_container)

# Attach the configuration script to the startup event.
# This script will initialize all required dependencies and store them
# in the dependency container that factories will use to build services.
# More details in app.state.py
app.add_event_handler('startup', lambda: configure_state(app) )
app.add_event_handler('shutdown', lambda: shutdown_state(app) )

app.include_router(v1_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Hello World"}
