# rag.py
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

# 1. Load API key from .env
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("❌ No Google API key found. Please set GOOGLE_API_KEY in your .env")

# 2. Load all Markdown docs
loader = DirectoryLoader("data/docs", glob="*.md", loader_cls=TextLoader)
docs = loader.load()
print(f"✅ Loaded {len(docs)} documents")

# 3. Split into chunks
splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
chunks = splitter.split_documents(docs)
print(f"✅ Split into {len(chunks)} chunks")

# 4. Create embeddings using Gemini
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# 5. Build FAISS vector store
vectorstore = FAISS.from_documents(chunks, embeddings)

# 6. Save FAISS store locally
vectorstore.save_local("faiss_store")
print("✅ FAISS vector store saved in faiss_store/")
