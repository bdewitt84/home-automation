# app/bootstrap/lifespan.py

from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.bootstrap.wiring import initialize_application
from app.bootstrap.lifecycle import startup_state, shutdown_state
from app.bootstrap.state import (
    init_dependency_container,
    init_lifecycle_manager,
)


@asynccontextmanager
async def lifespan(app: FastAPI):

    # --- Bootstrap phase ---
    try:
        initialize_application(app)
        await startup_state(app)

        yield # control back to fastAPI

    # -- Shutdown phase ---
    finally:
        await shutdown_state(app)
