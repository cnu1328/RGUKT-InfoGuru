from abc import ABC, abstractmethod

class UserAuthDaoInterface(ABC):
    """
    Interface for User Authentication DAO
    """

    @abstractmethod
    def create_user(self, email: str, password: str, user_name: str, avatar: str):
        pass

    @abstractmethod
    def validate_user(self, email: str, password: str):
        pass

    @abstractmethod
    def get_user_by_email(self, email: str):
        pass