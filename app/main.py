# app/main.py

from fastapi import FastAPI
from api.v1.v1_router import v1_router
from app.lifecycle import configure_state, shutdown_state, startup_state
from app.di.container import DependencyContainer
from app.di.keys import CONTAINER_KEY


# Start the FastAPI application
app = FastAPI(description="home-automation-service")

# Create the dependency container and attach to application state
dependency_container = DependencyContainer()
setattr(app.state, CONTAINER_KEY, dependency_container)

async def startup_state_wrapper():
    await startup_state(app)

async def shutdown_state_wrapper():
    await shutdown_state(app)

# Attach the configuration script to the startup event.
# This script will initialize all required dependencies and store them
# in the dependency container that factories will use to build services.
# More details in app.lifecycle.py
app.add_event_handler('startup', lambda: configure_state(app) )
app.add_event_handler('startup', startup_state_wrapper )
app.add_event_handler('shutdown', shutdown_state_wrapper )

app.include_router(v1_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Hello World"}
