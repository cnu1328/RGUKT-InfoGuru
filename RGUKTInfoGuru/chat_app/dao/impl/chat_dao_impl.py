from ..interface.chat_dao_interface import ChatDaoInterface
from rest_framework import status
from ...exceptions import CustomException
from ...models import User, Chat, Message
from .user_auth_dao_impl import UserAuthDaoImpl
import logging 

logger = logging.getLogger(__name__)

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

            logger.info(f"The chat is created with the user {user.email}")

            return chat

        except Exception as e:
            logger.debug(f"An error occured in creating chat, {str(e)}")
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
            logger.info(f"The message is saved. with role {role} and content {content}")
            return message
        except Exception as e:
            logger.info(f"An error occured in saving message, {str(e)}")
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
        
    def get_chat_messages(self, user_id, chat_id):
        """
        Retrieves chat messages
        """

        logger.info("Retrieving chat messages")
        
        try:
            chat = Chat.objects.filter(chat_id=chat_id, user__id=user_id).first()

            if chat is None:
                logger.info("Chat for this user is not found")
                raise CustomException(detail="Chat for this user not found", status_code=status.HTTP_404_NOT_FOUND)
            
            messages = Message.objects.filter(chat__chat_id=chat_id).order_by("timestamp")
            return messages
        
        except Exception as e:
            logger.info(f"An error Occured in getting chat messages: {str(e)}")
            raise CustomException(detail=str(e), status_code=status.HTTP_404_NOT_FOUND)

    def get_chats_by_user(self, user_id):
        """
        Retrieves chats by user
        """

        try:
            chats = Chat.objects.filter(user__id=user_id).order_by("-created_at")

            return chats
        except Exception as e:
            raise CustomException(detail=str(e), status_code=status.HTTP_404_NOT_FOUND)
        
    def rename_chat(self, chat_id, chat_name):
        """
        Renames the chat
        
        Args: 
            chat_id (str): The ID of the chat to rename.
            chat_naem (str): The new name for the chat.
            
        """

        try:
            chat = Chat.objects.get(chat_id=chat_id)

            if(chat is None):
                logger.info(f"Chat is not found with the given chat id : {chat_id}")
                raise CustomException(detail="Chat is not found", status_code=status.HTTP_404_NOT_FOUND)
            
            chat.chat_name = chat_name
            chat.save()
            logger.info(f"Chat is renamed to {chat_name}")
            return chat
        except Exception as e:
            logger.info(f"An error Occured in renaming chat: {str(e)}")
            raise CustomException(detail=str(e), status_code=status.HTTP_404_NOT_FOUND)
                
    def rename_chat(self, chat_id, chat_name):
        """
        Renames the chat
        
        Args: 
            chat_id (str): The ID of the chat to rename.
            chat_naem (str): The new name for the chat.
            
        """

        try:
            chat = Chat.objects.get(chat_id=chat_id)

            if(chat is None):
                logger.info(f"Chat is not found with the given chat id : {chat_id}")
                raise CustomException(detail="Chat is not found", status_code=status.HTTP_404_NOT_FOUND)
            
            chat.chat_name = chat_name
            chat.save()
            logger.info(f"Chat is renamed to {chat_name}")
            return chat
        except Exception as e:
            logger.info(f"An error Occured in renaming chat: {str(e)}")
            raise CustomException(detail=str(e), status_code=status.HTTP_404_NOT_FOUND)
                
    def rename_chat(self, chat_id, chat_name):
        """
        Renames the chat
        
        Args: 
            chat_id (str): The ID of the chat to rename.
            chat_naem (str): The new name for the chat.
            
        """

        try:
            chat = Chat.objects.get(chat_id=chat_id)

            if(chat is None):
                logger.info(f"Chat is not found with the given chat id : {chat_id}")
                raise CustomException(detail="Chat is not found", status_code=status.HTTP_404_NOT_FOUND)
            
            chat.chat_name = chat_name
            chat.save()
            logger.info(f"Chat is renamed to {chat_name}")
            return chat
        except Exception as e:
            logger.info(f"An error Occured in renaming chat: {str(e)}")
            raise CustomException(detail=str(e), status_code=status.HTTP_404_NOT_FOUND)
                

    def delete_chat(self, chat_id):
        """
        Deletes the chat
        
        Args: 
            chat_id (str): The ID of the chat to rename.
        """

        try:
            chat = Chat.objects.get(chat_id=chat_id)

            if(chat is None):
                logger.info(f"Chat is not found with the given chat_id : {chat_id}")
                raise CustomException(detail="Chat is not found", status_code=status.HTTP_404_NOT_FOUND)
            
            chat.delete()  # This deletes the chat and all related messages due to CASCADE

            logger.info(f"Chat with chat_id {chat_id} deleted successfully.")

        except Exception as e:
            logger.info(f"An error Occured in deleting chat: {str(e)}")
            raise CustomException(detail=str(e), status_code=status.HTTP_404_NOT_FOUND)
                
    