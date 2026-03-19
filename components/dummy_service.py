# services/dummy_service.py

from app.di.registry import component
from interfaces.dummy import DummyService


@component(is_dependency=True)
class DummyServiceImplementation(DummyService):
    def __init__(self):
        super().__init__()

    async def dummy_method(self):
        print("Dummy method called")
