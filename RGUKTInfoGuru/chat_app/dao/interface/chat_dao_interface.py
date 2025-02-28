from abc import ABC, abstractmethod
from ...models import Chat

class ChatDaoInterface(ABC):
    """
    Interface for Chat DAO
    """

    @abstractmethod
    def create_chat(self, user_id, chat_name):
        pass

    @abstractmethod
    def save_message(self, chat: Chat, role, content):
        pass