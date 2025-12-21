# app/main.py

from fastapi import FastAPI

from app.bootstrap.lifepsan import lifespan
from api.v1.v1_router import v1_router

# Start the FastAPI application
# Bootstrapping is handled by app/bootstrap/lifespan.py
app = FastAPI(description="home-automation-service",
              lifespan=lifespan)

# Dummy router for testing
app.include_router(v1_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Hello World"}
