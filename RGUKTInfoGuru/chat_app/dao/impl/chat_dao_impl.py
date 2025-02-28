from ..interface.chat_dao_interface import ChatDaoInterface
from rest_framework import status
from ...exceptions import CustomException
from ...models import User, Chat, Message
from .user_auth_dao_impl import UserAuthDaoImpl

class ChatDaoImpl(ChatDaoInterface):
    """
    Implementation of UserAuthDAOInterface.
    """
    _instance = None
    def __new__(cls, *args, **kwargs):
        """
        Implements the Singleton pattern to ensure only one instance is created.
        """
        if cls._instance is None:
            cls._instance = super(ChatDaoImpl, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        """
        Initializes the AuthenticationView instance if it hasn't been initialized yet.
        Ensures that initialization only happens once.
        """
        if not hasattr(self, "initialized"):
            super().__init__(**kwargs)
            self.initialized = True
            self.user_dao = UserAuthDaoImpl()


    def create_chat(self, user_id, chat_name="Chat1"):
        """
        creates new chat

        Args:
            user_id (str): The user's ID.
            chat_name (str): The name of the chat. Defaults to "Chat1".

        Returns:
            Chat: The newly created chat object.
        """

        try:
            user = self.user_dao.get_user_by_id(user_id)

            chat = Chat.objects.create(user=user, chat_name=chat_name)

            print(f"The chat is created with the user {user.email}")

            return chat

        except Exception as e:
            raise CustomException(detail=str(e), status_code=status.HTTP_404_NOT_FOUND)
        
    def save_message(self, chat: Chat, role, content):
        """
        Saves the message to the chat

        Args:
            chat (Chat): The chat object.
            role (str): The role of the user.
            content (str): The content of the message.

        Returns:
            Message: The newly created message object.
        """
        try:
            message = Message.objects.create(chat=chat, role=role, content=content)
            print(f"The message is saved. with role {role} and content {content}")
            return message
        except Exception as e:
            raise CustomException(detail=str(e), status_code=status.HTTP_404_NOT_FOUND)
        
    def get_chat_by_id(self, chat_id):
        """
        Retrieves chat by ID
        """

        try:
            chat = Chat.objects.get(chat_id=chat_id)
            return chat
        except Exception as e:
            raise CustomException(detail=str(e), status_code=status.HTTP_404_NOT_FOUND)
        
    def get_chat_messages(self, chat_id):
        """
        Retrieves chat messages
        """
        
        try:
            messages = Message.objects.filter(chat__chat_id=chat_id).order_by("timestamp")
            return messages
        except Exception as e:
            raise CustomException(detail=str(e), status_code=status.HTTP_404_NOT_FOUND)
