from abc import ABC, abstractmethod

class ChatServiceInterface(ABC):
    """
    Interface for Chat Service
    """

    @abstractmethod
    def generate_response(self, user_id, chat_id, message):
        pass