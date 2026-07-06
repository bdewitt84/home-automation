# app/main.py

from fastapi import FastAPI

from app.bootstrap.lifespan import lifespan

# Start the FastAPI application
# Bootstrapping is handled by app/bootstrap/lifespan.py
app = FastAPI(description="home-automation-service",
              lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Hello World"}
