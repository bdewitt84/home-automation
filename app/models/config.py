# ./models/config.py

from typing import Any, Callable, List, Dict
from pydantic import BaseModel, Field


class ConfigComponent(BaseModel):
    name: str
    type: str
    settings: BaseModel | None


class Config(BaseModel):
    version: str
    app_settings: Dict = Field(default_factory=dict)
    components: Dict[str, ConfigComponent] = Field(default_factory=dict)
