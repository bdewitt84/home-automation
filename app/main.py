# app/main.py

from fastapi import FastAPI
from api.v1.v1_router import v1_router
from app.lifecycle_manager import LifeCycleManager
from app.bootstrap.wiring import initialize_application
from app.bootstrap.lifecycle import shutdown_state, startup_state
from app.di.container import DependencyContainer
from app.di.keys import CONTAINER_KEY, LIFECYCLE_MANAGER_KEY

# Start the FastAPI application
app = FastAPI(description="home-automation-service")

# Create the dependency container and lifecycle manager,
# and attach them to the application state
dependency_container = DependencyContainer()
lifecycle_manager = LifeCycleManager()
setattr(app.state, CONTAINER_KEY, dependency_container)
setattr(app.state, LIFECYCLE_MANAGER_KEY, lifecycle_manager)

async def startup_state_wrapper():
    await startup_state(app)

async def shutdown_state_wrapper():
    await shutdown_state(app)

# Attach the configuration script to the startup event.
# This script will initialize all required dependencies and store them
# in the dependency container that factories will use to build services.
# More details in app.
app.add_event_handler('startup', lambda: initialize_application(app))
app.add_event_handler('startup', startup_state_wrapper )
app.add_event_handler('shutdown', shutdown_state_wrapper )

app.include_router(v1_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Hello World"}
