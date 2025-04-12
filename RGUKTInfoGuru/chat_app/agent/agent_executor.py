import os
from rest_framework.permissions import IsAuthenticated
from ..utils.response import CustomResponse
import logging
from ..exceptions import CustomException
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import time
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_chroma import Chroma
from ..dao.impl.chat_dao_impl import ChatDaoImpl
from pprint import pformat

from .prompts import Context_Prompt, System_Prompt, Chat_Title_Prompt
from ..utils.response import remove_think_tags

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH")
DATASET_PATH = os.getenv("DATASET_PATH")
HF_TOKEN=os.getenv("HF_TOKEN")


logger = logging.getLogger(__name__)


class AgentExecutor:
    """
    This class is responsible for executing the llm and generating the responses.
    """

    permission_classes = [IsAuthenticated]
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AgentExecutor, cls).__new__(cls)
        return cls._instance
        
    def __init__(self, **kwargs):
        if not hasattr(self, "initialized"):
            super().__init__(**kwargs)
            self.initialized = True
            self.Response = CustomResponse()
            self.chat_dao = ChatDaoImpl()

            self.llm = ChatGroq(
                groq_api_key=GROQ_API_KEY,
                model_name=MODEL_NAME
            )

            self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLm-L6-v2")

            self.vectordb = self.load_chroma_db()

            self.retriever = self.vectordb.as_retriever()

            self.history_aware_retriever = create_history_aware_retriever(self.llm, self.retriever, Context_Prompt)

            self.document_chain = create_stuff_documents_chain(self.llm, System_Prompt)

            self.rag_chain = create_retrieval_chain(self.history_aware_retriever, self.document_chain)

            self.chat_history = ChatMessageHistory()

            logger.info("AgentExecutor is initialized successfully")


    def load_chroma_db(self):
        """
        Load the Chroma Database
        """
        try: 
            if os.path.exists(CHROMA_DB_PATH):
                logger.info("Loading Chroma Database...")
                return Chroma(persist_directory=CHROMA_DB_PATH, embedding_function=self.embeddings)
            
            else:
                raise CustomException(detail="Chroma Database not found, please check the path", status_code=404)
            
        except Exception as e:
            logger.info("An Exception occured while loading the Chroma Database")
            raise CustomException(detail=str(e), status_code=404)

    def get_session_history(self, user_id, chat_id):
        """
        Function to retrieve chat messages for RunnableWithMessageHistory.
        Returns the messages as a list of dictionaries.
        """
        logger.info("Retrieving chat messages")

        try: 
            messages = self.chat_dao.get_chat_messages(user_id, chat_id)

            chat_history = ChatMessageHistory()
        
            for msg in messages:
                chat_history.add_message({"role": msg.role, "content": msg.content})

            return chat_history

        except Exception as e:
            logger.info(f"An Exception occured while retrieving chat messages {str(e)}")
            raise CustomException(detail=str(e), status_code=404)

    def execute(self, message, user_id, chat_id):
        """
        Executes the llm model and generates the response.
        
        Args:
            message (str): The message to be asked the Chatbot.
            chat_history (list): The user's chat history.

        Returns:
            str: The response of the Chatbot.
        """

        logger.info(f"Executing the model with message {message}")

        try:

            self.rag_agent = RunnableWithMessageHistory(
                self.rag_chain,
                get_session_history=lambda session_id: self.get_session_history(user_id, session_id),
                input_messages_key="input",
                history_messages_key="chat_history",
                output_messages_key="response"
            )

            start_time = time.process_time()

            response_content = self.rag_agent.invoke(
                {
                    "input": message
                },
                config={
                    "configurable": {
                        "session_id": chat_id
                    }
                }
            )

            elapsed_time = time.process_time() - start_time

            logger.info(f"Model response generated in {elapsed_time:.2f} seconds.")
            logger.info(f"Generated Response: {pformat(response_content)}")

            return {
                    "response": response_content,
                    "time_taken_seconds": round(elapsed_time, 2),
                }
            

        except Exception as e:
            logger.error(f"An error occured in executing the model: {str(e)}")
            raise CustomException(detail=str(e), status_code=404)
        
    def generate_chat_name(self, message):
        """
        This function is used to generate the chat name based on the message""
        """

        try:
            document_chain = create_stuff_documents_chain(self.llm, Chat_Title_Prompt)

            response = document_chain.invoke({
                "input": message,
                "context": ""
            })

            logger.info(f"Generated Chat Name: {response}")

            return remove_think_tags(response)
        except Exception as e:
            logger.error(f"An error occured in generating chat name: {str(e)}")
            raise CustomException(detail=str(e), status_code=404)

