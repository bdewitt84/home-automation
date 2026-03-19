# interfaces/dummy.py

from abc import ABC, abstractmethod

from app.di.decorators import route, controller


@controller(prefix="dummy",
            tags=["dummy"],)
class DummyService(ABC):
    def __init__(self):
        pass


    @route(path="dummy",
           methods=["GET"],
           tags=["test"])
    @abstractmethod
    async def dummy_method(self):
        raise NotImplemented
