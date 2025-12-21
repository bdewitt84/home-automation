# app/bootstrap/lifespan.py

from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.bootstrap.wiring import initialize_application
from app.bootstrap.lifecycle import startup_state, shutdown_state
from app.bootstrap.state import (
    create_dependency_container,
    create_lifecycle_manager,
)


@asynccontextmanager
async def lifespan(app: FastAPI):

    # --- Bootstrap phase ---
    create_dependency_container(app)
    create_lifecycle_manager(app)
    initialize_application(app)
    await startup_state(app)


    yield # control back to fastAPI


    # -- Shutdown phase ---
    await shutdown_state(app)
