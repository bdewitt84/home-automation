# app.py

from fastapi import FastAPI
from api.v1.v1_router import v1_router
from services.media.vlc_media_control import VLCMediaControl


def startup_event():
    vlc_media_control_instance = VLCMediaControl(
        'http://localhost:8080',
        'your_password'
    )
    app.state.media_control_instance = vlc_media_control_instance

app = FastAPI(
    on_startup=[startup_event],
)

app.include_router(
    v1_router,
    prefix="/api/v1",
)

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
