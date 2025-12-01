# services/media_control_service.py

from services.media.vlc_media_control import VLCMediaControl


def play() -> dict:
    media_control = VLCMediaControl('http://localhost:8080', 'your_password')
    status = media_control.play()
    return status.__dict__

def stop() -> dict:
    return {'message': 'stop stub'}

def enqueue(file_path: str) -> dict:
    return {'message': 'enqueue stub'}