```python


import os
import pickle
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
os.environ["HF_TOKEN"] = os.getenv("HF_TOKEN")

# Set up embeddings
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# File paths for FAISS index and metadata
DATASET_PATH = "rguktBasarDataset"
TRAINED_DATA_PATH = "trainedData"
INDEX_FILE = os.path.join(TRAINED_DATA_PATH, "faiss_index.faiss")
METADATA_FILE = os.path.join(TRAINED_DATA_PATH, "faiss_metadata.pkl")

# Ensure the trainedData directory exists
os.makedirs(TRAINED_DATA_PATH, exist_ok=True)

# Function to create and save the vector database
def create_and_save_vector_database():
    print("Training model and creating vector database...")

    # Load documents from the dataset directory
    loader = PyPDFDirectoryLoader(DATASET_PATH)
    docs = loader.load()

    # Split documents into manageable chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    final_documents = text_splitter.split_documents(docs)

    # Create FAISS vector database
    vector_store = FAISS.from_documents(final_documents, embeddings)

    # Save the FAISS index and metadata
    vector_store.save_local(INDEX_FILE)
    with open(METADATA_FILE, "wb") as f:
        pickle.dump(final_documents, f)

    print("Vector database created and saved to disk.")


# Function to load the vector database from disk
def load_vector_database():
    print("Loading vector database from disk...")
    vector_store = FAISS.load_local(INDEX_FILE, embeddings, allow_dangerous_deserialization=True)
    with open(METADATA_FILE, "rb") as f:
        final_documents = pickle.load(f)
    return vector_store, final_documents

if __name__ == "__main__":
    # Check if FAISS index and metadata exist
    if os.path.exists(INDEX_FILE) and os.path.exists(METADATA_FILE):
        print("Pre-trained FAISS index found. Loading...")
        vectors, final_documents = load_vector_database()
    else:
        print("No pre-trained FAISS index found. Creating a new one...")
        create_and_save_vector_database()
        vectors, final_documents = load_vector_database()

    print("Vector database is ready for use.")


```
