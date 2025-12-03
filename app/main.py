# app/main.py

from fastapi import FastAPI
from api.v1.v1_router import v1_router
from app.state import configure_state


app = FastAPI(description="home-automation-service")

app.add_event_handler('startup', lambda: configure_state(app))
# app.add_event_handler('startup, lambda: ())
# app.add_event_handler('shutdown', lambda: ())

app.include_router(v1_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Hello World"}
