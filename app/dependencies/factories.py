# app.dependencies.factories

from services.media.vlc_media_control import VLCMediaControl


def vlc_media_control_factory(url: str, password: str):
    return VLCMediaControl(url, password)

