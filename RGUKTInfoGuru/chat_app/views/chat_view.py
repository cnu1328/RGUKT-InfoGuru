from rest_framework.viewsets import ViewSet
from ..utils.response import CustomResponse
from rest_framework.decorators import action
from rest_framework import status
from ..serializers.chat_serailizer import ChatSerializer, ChatRenameSerializers
from rest_framework.permissions import IsAuthenticated
from ..services.impl.chat_service_impl import ChatServiceImpl
import logging

logger = logging.getLogger(__name__)

class ChatViewSet(ViewSet):
    """
    This view take care of Chat Process
    """

    _instance = None
    permission_classes = [IsAuthenticated]

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ChatViewSet, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, **kwargs):
        if not hasattr(self, "initialized"):
            super().__init__(**kwargs)
            self.initialized = True
            self.Response = CustomResponse()
            self.chat_service = ChatServiceImpl()
            logger.info("ChatViewSet is initialized successfully")



    @action(methods=['post'], detail=False)
    def chat(self, request):
        """
        Handles User's chat
        Request Params:
            user_id: Identifies the user
            chat_id: Identifies the chat
            message: The message to be asked the Chatbot
        
        Response:
            data: The response of the Chatbot
            message: The message of the response
            status_code: The status code of the resposne
        """


        serializer = ChatSerializer(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data

            try:
                user_id = data["user_id"]
                chat_id = data["chat_id"]
                message = data["message"]
                model = data["model"]

                logger.info(f"The user with user id {user_id} is asking the chatbot with message {message} using model {model}")
                

                result = self.chat_service.generate_response(user_id, chat_id, message, model)

                return self.Response(data=result, message="ChatBot is successfully Responded", status_code=200)
            except Exception as e:
                logger.debug(f"An error Occured in ChatViewSet: {str(e)}")
                return self.Response(message=str(e), status_code=404)
            
        return self.Response(data=serializer.errors, message="Error Occured", status_code=404)

    @action(methods=['get'], detail=False)
    def get_chats_by_user_id(self, request, user_id=None):
        """
        Returns the Chats of the user
        Request Params:
            user_id: Identifies the user

        Response:
            data: All the chats of the user
        """
        logger.info(f"Getting the chats of the user with user id {user_id}")

        try:

            if user_id is None:
                return self.Response(message="User ID is required", status_code=404)

            chats = self.chat_service.get_chats_by_user_id(user_id)

            chat_data = {
                "user_id": user_id,
                "chats": [
                    {
                        "chat_id": chat.chat_id,
                        "chat_name": chat.chat_name,
                        "created_at": chat.created_at
                    } for chat in chats
                ]
            }

            return self.Response(data=chat_data, message="Chats are successfully retrieved", status_code=200)

        except Exception as e:
            return self.Response(message=str(e), status_code=404)

    @action(methods=['get'], detail=False)
    def get_messages_by_chat_id(self, request, user_id=None, chat_id=None):
        """
        Returns the Messages of the chat
        Request Params:
            chat_id: Identifies the chat

        Response:
            data: All the messages of the chat
        """

        try:
            if chat_id is None:
                return self.Response(message="Chat ID is required. It is in get_messages_by_chat_id", status_code=404)
            
            if user_id is None:
                return self.Response(message="User ID is required", status_code=404)
            
            messages = self.chat_service.get_messages_by_chat_id(user_id, chat_id)

            chat_data = {
                "user_id": user_id,
                "chat_id": chat_id,
                "messages": [
                    {
                        "role": msg.role,
                        "content": msg.content,
                        "message_id": msg.message_id,
                        "created_at": msg.timestamp
                    } for msg in messages
                ]
            }

            return self.Response(data=chat_data, message="Messages are successfully retrieved", status_code=200)

        except Exception as e:
            return self.Response(message=str(e), status_code=404)
        
    @action(methods=['post'], detail=False)
    def rename_chat(self, request, chat_id=None):
        """
        Renames the chat
        Request Params:
            chat_id: Identifies the chat
            chat_name: The new name of the chat
            
        Response:
            data: The renamed chat
            message: The message of the response
            status_code: The status code of the response
        """
        
        chat_name = request.data.get("chat_name", None)

        if chat_id is None:
            return self.Response(message="Chat ID is required", status_code=404)
        
        if chat_name is None: 
            return self.Response(message="Chat Name is required", status_code=404)
        
        try:
            chat = self.chat_service.rename_chat(chat_id, chat_name)

            return self.Response(data=chat, message="Chat is successfully renamed", status_code=200)
        except Exception as e:
            logger.info(f"An error Occured in ChatViewSet: {str(e)}")
            return self.Response(message=str(e), status_code=404)
        
    def delete_chat(self, request, chat_id=None):
        
        """
        Deletes the chat
        Request Params:
            chat_id: Identifies the chat
            
        Response:
            message: The message of the response
            status_code: The status code of the response
        """

        if chat_id is None:
            return self.Response(message="Chat ID is required", status_code=404)
        
        try:
            self.chat_service.delete_chat(chat_id)

            return self.Response(message="Chat is successfully deleted", status_code=200)
        except Exception as e:
            logger.info(f"An error Occured in ChatViewSet: {str(e)}")
            return self.Response(message=str(e), status_code=404)









