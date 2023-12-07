from abc import ABC, abstractmethod

class GeneralAgent(ABC):
    @property
    @abstractmethod
    def position(self) -> tuple:
        pass

