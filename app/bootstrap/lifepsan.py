# app/bootstrap/lifespan.py

from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.bootstrap.wiring import initialize_application
from app.bootstrap.lifecycle import startup_state, shutdown_state


@asynccontextmanager
async def lifespan(app: FastAPI):

    initialize_application(app)
    await startup_state(app)

    yield

    await shutdown_state(app)