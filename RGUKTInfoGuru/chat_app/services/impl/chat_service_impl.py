from ...dao.impl.user_auth_dao_impl import UserAuthDaoImpl
from ...services.interface.chat_service_interface import ChatServiceInterface
from ...exceptions import CustomException
import logging
from rest_framework_simplejwt.tokens import RefreshToken
from ...dao.impl.chat_dao_impl import ChatDaoImpl
from ...agent.agent_executor import AgentExecutor
from pprint import pformat
from ...utils.response import remove_think_tags


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
            self.agent_executor = AgentExecutor.get_instance()

    def generate_response(self, user_id, chat_id, message, model):
        """
        Generates the response for the user's chat
        
        Args:
            user_id (str): The user's ID.
            chat_id (str): The chat's ID.
            message (str): The message to be asked the Chatbot.
        Response:
            str: The response of the Chatbot.
        """
        logger.info(f"The user with id {user_id} is asking the chatbot with message '{message}'")

        try:
            user = self.user_dao.get_user_by_id(user_id)
            if user is None:
                logger.info("User is not found")
                raise CustomException(detail="User not found",status_code=404)

            if chat_id is None:

                chat_name = self.agent_executor.generate_chat_name(message)

                chat = self.chat_dao.create_chat(user_id, chat_name)
            else:
                chat = self.chat_dao.get_chat_by_id(chat_id)

            response = self.agent_executor.execute(message, user_id, chat.chat_id, model)
            
            logger.info(f"Response from the agent: {pformat(response)}")
            logger.info(f"Response answer from the agent: {response['response']['answer']}")

            self.chat_dao.save_message(chat, 'user', message)
            self.chat_dao.save_message(chat, 'assistant', remove_think_tags(response['response']['answer']))

            messages = self.chat_dao.get_chat_messages(user_id, chat.chat_id)

            return {
                "user_id": user.id,
                "email": user.email,
                "chat_id": chat.chat_id,
                "chat_name": chat.chat_name,
                "created_at": chat.created_at,
                "message": message,
                "response": remove_think_tags(response['response']['answer']),
                "time_taken_seconds": response['time_taken_seconds'],
                "messages": [
                    {
                        "role": msg.role,
                        "content": msg.content,
                        "message_id": msg.message_id,
                        "created_at": msg.timestamp
                    }
                    for msg in list(messages)[-2:]
                ]
            }

        except Exception as e:
            logger.info(f"An error occured in {str(e)}")
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
        
    
    def rename_chat(self, chat_id, chat_name):
        """
        Renames the Chat
        """
        

        try:
            chat = self.chat_dao.rename_chat(chat_id, chat_name)

            chatResponse = {
                "chat_id": chat.chat_id,
                "chat_name": chat.chat_name,
                "created_at": chat.created_at
            }

            return chatResponse
        

        except Exception as e:
            logger.info(f"An error occured in remaining chat: {str(e)}")
            raise CustomException(detail=str(e), status_code=404)
    
    def delete_chat(self, chat_id):
        """
        Deletes the Chat
        """
        

        try:
            self.chat_dao.delete_chat(chat_id)
        
        except Exception as e:
            logger.info(f"An error occured in deleting chat: {str(e)}")
            raise CustomException(detail=str(e), status_code=404)
