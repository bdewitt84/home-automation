# services/media_control_service.py
from interfaces.media_control_interface import MediaControlInterface


def play(media_control: MediaControlInterface) -> dict:
    status = media_control.play()
    return status.model_dump()

def stop() -> dict:
    return {'message': 'stop stub'}

def enqueue(file_path: str) -> dict:
    return {'message': 'enqueue stub'}