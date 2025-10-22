from abc import ABCMeta, abstractmethod
from ..controllers.controller import Controller

class HardwareWrapper(metaclass=ABCMeta):
    _instance = None

    def __new__(cls):
        if cls._instance is not None:
            return cls._instance

        instance = super().__new__(cls)
        cls._instance = instance
        Controller().register_update_handler(instance.update)
        return instance

    @abstractmethod
    def update(self, dt):
        pass