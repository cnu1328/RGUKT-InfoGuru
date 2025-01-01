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


# Load environment variables
load_dotenv()

# File paths for FAISS index and metadata
DATASET_PATH = "rguktBasarDataset"
TRAINED_DATA_PATH = "trainedData"
INDEX_FILE = os.path.join(TRAINED_DATA_PATH, "faiss_index.faiss")
METADATA_FILE = os.path.join(TRAINED_DATA_PATH, "faiss_metadata.pkl")

# API Keys
os.environ['GROQ_API_KEY'] = os.getenv("GROQ_API_KEY")
os.environ["HF_TOKEN"] = os.getenv("HF_TOKEN")

# Set up LLM and embeddings
llm = ChatGroq(groq_api_key=os.getenv("GROQ_API_KEY"), model_name="llama-3.3-70b-versatile")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Prompts
system_prompt = (
    "You are a virtual assistant for RGUKT Basar named RGUKT InfoGuru. Your goal is to answer questions clearly and accurately based on the provided context. "
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

qa_prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])

contextualize_q_prompt = ChatPromptTemplate.from_messages([
    ("system", contextualize_q_system_prompt),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])


# Initialize session state for messages and history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = ChatMessageHistory()

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Hi, I'm RGUKT InfoGuru! How can I help you today?"}
    ]

# Load vector database
def load_vector_database():
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
st.markdown(
    "<h1 style='text-align: center;'>RGUKT InfoGuru</h1>", 
    unsafe_allow_html=True
)

# Display chat history using st.chat_message
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg['content'])

# Input box for user query
if prompt := st.chat_input(placeholder="Ask me anything about RGUKT Basar..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Use the RAG chain for response generation
    response = conversational_rag_chain.invoke({"input": prompt}, config={"configurable": {"session_id": "rgukt_chat_session"}})
    response_text = response["answer"]

    st.session_state.messages.append({"role": "assistant", "content": response_text})
    st.chat_message("assistant").write(response_text)
