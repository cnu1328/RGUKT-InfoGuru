import os
import streamlit as st
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage
from langchain.chains import create_history_aware_retriever
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from dotenv import load_dotenv
import pickle
import faiss

# Load environment variables
load_dotenv()

# File paths for FAISS index and metadata
DATASET_PATH = "rguktBasarDataset"
TRAINED_DATA_PATH = "trainedData"
INDEX_FILE = os.path.join(TRAINED_DATA_PATH, "faiss_index.faiss")
METADATA_FILE = os.path.join(TRAINED_DATA_PATH, "faiss_metadata.pkl")

# API Keys
# os.environ['GROQ_API_KEY'] = os.getenv("GROQ_API_KEY")
# os.environ["HF_TOKEN"] = os.getenv("HF_TOKEN")
os.environ["HF_TOKEN"] = st.secrets["HF_TOKEN"]
os.environ['GROQ_API_KEY'] = st.secrets["GROQ_API_KEY"]

# Set up LLM and embeddings
llm = ChatGroq(groq_api_key=st.secrets["GROQ_API_KEY"], model_name="llama-3.3-70b-versatile")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Prompts
system_prompt = (
    "You are a virtual assistant for RGUKT Basar. Your goal is to answer questions clearly and accurately based on the provided context. "
    "If you don't know the answer or the information is unavailable in the provided context, respond with: 'I'm sorry, I don't have that information right now.' "
    "Use concise language wherever possible, but when additional explanation is necessary, provide as much detail as needed to fully answer the query. "
    "For ambiguous questions, politely ask for clarification or provide the closest relevant information."
    "\n\n"
    "Context:\n{context}\n\n"
    "Remember to keep responses formal yet approachable, ensuring clarity for students, faculty, and visitors."
)


contextualize_q_system_prompt = (
    "You are tasked with improving user queries about RGUKT Basar to ensure they are clear and self-contained. "
    "Given the chat history and the latest user question, reformulate the question to be standalone, so it can be understood without the chat history. "
    "If the question is already clear and self-contained, return it as is. "
    "For ambiguous or incomplete questions, use the chat history to make the question precise while retaining its original intent."
)

qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

# Initialize session history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = ChatMessageHistory()

if "input_text" not in st.session_state:
    st.session_state.input_text = ""

if "last_query" not in st.session_state:
    st.session_state.last_query = None

# Load vector database
def load_vector_database():
    st.write("Loading vector database...")
    vector_store = FAISS.load_local(INDEX_FILE, embeddings, allow_dangerous_deserialization=True)
    with open(METADATA_FILE, "rb") as f:
        metadata = pickle.load(f)
    return vector_store, metadata

# History-aware retriever
retriever = FAISS.load_local(INDEX_FILE, embeddings, allow_dangerous_deserialization=True).as_retriever()
history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)

# Retrieval chain
question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

# Conversational RAG chain
conversational_rag_chain = RunnableWithMessageHistory(
    rag_chain,
    lambda session_id: st.session_state.chat_history,
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer",
)

# Streamlit UI
st.title("RGUKT InfoGuru")
st.markdown("Your personal assistant for RGUKT Basar queries.")

# Styles for user and assistant messages
HUMAN_STYLE = "background-color: #f0f0f0; padding: 10px; margin: 5px; border-radius: 5px; text-align: left;"
AI_STYLE = "background-color: #d0e6ff; padding: 10px; margin: 5px; border-radius: 5px; text-align: left;"

# Build the chat history as a single HTML block
chat_html = """
<div style="max-height: 400px; overflow-y: auto; padding: 10px; border: 1px solid #ccc; border-radius: 5px;">
"""

for message in st.session_state.chat_history.messages:
    if isinstance(message, HumanMessage):
        chat_html += f'<div style="{HUMAN_STYLE}"><strong>User:</strong> {message.content}</div>'
    elif isinstance(message, AIMessage):
        chat_html += f'<div style="{AI_STYLE}"><strong>Assistant:</strong> {message.content}</div>'

chat_html += "</div>"

# Render the chat history
st.markdown(chat_html, unsafe_allow_html=True)

# Input box at the bottom
input_query = st.text_input("Type your query here...", value=st.session_state.input_text)

if input_query and input_query != st.session_state.last_query:
    st.session_state.last_query = input_query  # Track the last query

    # Generate response
    response = conversational_rag_chain.invoke(
        {"input": input_query},
        config={"configurable": {"session_id": "rgukt_chat_session"}}
    )
    response_text = response["answer"]

    print(response_text)

    # Add messages to chat history
    st.session_state.chat_history.add_message(HumanMessage(content=input_query))
    st.session_state.chat_history.add_message(AIMessage(content=response_text))

    # Clear input text
    st.session_state.input_text = ""

    # Refresh the interface
    st.rerun()
