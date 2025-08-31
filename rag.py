# rag.py
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI

# -------------------------------
# Load environment variables
# -------------------------------
load_dotenv()
if "GOOGLE_API_KEY" not in os.environ:
    raise ValueError("❌ GOOGLE_API_KEY not set. Please export it in your .env file.")

# -------------------------------
# Initialize LLM (Gemini / Google)
# -------------------------------
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro",
    temperature=0
)

# -------------------------------
# Load documents
# -------------------------------
loader = DirectoryLoader("data/docs", glob="*.md", loader_cls=TextLoader)
docs = loader.load()
print(f"✅ Loaded {len(docs)} documents")

# -------------------------------
# Split documents into chunks
# -------------------------------
splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
chunks = splitter.split_documents(docs)
print(f"✅ Split into {len(chunks)} chunks")

# -------------------------------
# Create embeddings
# -------------------------------
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# -------------------------------
# Build or load FAISS vector store
# -------------------------------
if os.path.exists("faiss_store"):
    vectorstore = FAISS.load_local("faiss_store", embeddings, allow_dangerous_deserialization=True)
    print("✅ FAISS vector store loaded from faiss_store/")
else:
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local("faiss_store")
    print("✅ FAISS vector store saved in faiss_store/")

# -------------------------------
# Retriever function
# -------------------------------
def get_retriever():
    """Return a retriever for RAG queries."""
    return vectorstore.as_retriever()
