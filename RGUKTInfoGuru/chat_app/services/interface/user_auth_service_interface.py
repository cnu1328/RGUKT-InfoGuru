from abc import ABC, abstractmethod

class UserAuthServiceInterface(ABC):
    """
    Interface for User Authentication Service
    """

    @abstractmethod
    def signup(self, email:str, password: str):
        pass

    @abstractmethod
    def login(self, email: str, password: str):
        pass