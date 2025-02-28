from ...dao.impl.user_auth_dao_impl import UserAuthDaoImpl
from ...services.interface.chat_service_interface import ChatServiceInterface
from ...exceptions import CustomException
import logging
from rest_framework_simplejwt.tokens import RefreshToken
from ...dao.impl.chat_dao_impl import ChatDaoImpl

logger = logging.getLogger(__name__)

class ChatServiceImpl(ChatServiceInterface):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ChatServiceImpl, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        if not hasattr(self, "initialized"):
            super().__init__(**kwargs)
            self.initialized = True
            self.user_dao = UserAuthDaoImpl()
            self.chat_dao = ChatDaoImpl()

    def generate_response(self, user_id, chat_id, message):
        """
        Generates the response for the user's chat
        
        Args:
            user_id (str): The user's ID.
            chat_id (str): The chat's ID.
            message (str): The message to be asked the Chatbot.
        Response:
            str: The response of the Chatbot.
        """

        try:
            user = self.user_dao.get_user_by_id(user_id)
            if user is None:
                raise CustomException(detail="User not found",status_code=404)
            print(f"The user with email {user.email} is asking the chatbot with message {message}")

            if chat_id is None:
                chat = self.chat_dao.create_chat(user_id)
            else:
                chat = self.chat_dao.get_chat_by_id(chat_id)

            response = "Hello, I am ChatBot. How can I help you today?"

            self.chat_dao.save_message(chat, 'user', message)
            self.chat_dao.save_message(chat, 'assistant', response)

            messages = self.chat_dao.get_chat_messages(user_id, chat.chat_id)

            return {
                "user_id": user.id,
                "email": user.email,
                "chat_id": chat.chat_id,
                "chat_name": chat.chat_name,
                "message": message,
                "response": response,
                "messages": [
                    {"role": msg.role, "content": msg.content}
                    for msg in messages
                ]
            }

        except Exception as e:
            raise CustomException(detail=str(e), status_code=404)
        
    def get_chats_by_user_id(self, user_id):
        """
        Returns the Chats of the user
        """

        try:
            chats = self.chat_dao.get_chats_by_user(user_id)

            return chats
        
        except Exception as e:
            raise CustomException(detail=str(e), status_code=404)

    def get_messages_by_chat_id(self, user_id, chat_id):
        """
        Returns the Messages of the Chat
        """

        try:
            messages = self.chat_dao.get_chat_messages(user_id, chat_id)
            return messages
            
        except Exception as e:
            raise CustomException(detail=str(e), status_code=404)
