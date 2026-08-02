# ./app/bootstrap/loader.py

from json import load
from typing import (
    Callable,
    IO,
)

from app.models.config import Config
from app.bootstrap.interpolator import interpolate_environment_variables


class Loader:
    def __init__(self,
                 parser: Callable[[dict], Config],
                 reader: Callable[[str, str], IO[str]] = open,
                 decoder: Callable[[IO[str]], dict] = load,
                 interpolator: Callable[[dict], None] = interpolate_environment_variables,
                 ):
        self._parser = parser
        self._reader = reader
        self._decoder = decoder
        self._interpolator = interpolator

    def load_from_path(self, path: str = None) -> Config:
        data = self._decode_stream(path)
        self._interpolator(data)
        return self._parse_decoded_stream(data)

    def _decode_stream(self, path: str) -> dict:
        try:
            with self._reader(file=path, mode='r') as f:
                data = self._decoder(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found: {path}")
        except Exception as e:
            raise RuntimeError(f"Critical failure reading config file: {e}") from e
        return data

    def _parse_decoded_stream(self, data: dict) -> Config:
        return self._parser(data)
