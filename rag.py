# rag.py
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

# 1. Load documents
loader = DirectoryLoader("data/docs", glob="*.md")
documents = loader.load()

# 2. Split into chunks
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
docs = splitter.split_documents(documents)

# 3. Embeddings
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=os.getenv("GEMINI_API_KEY")
)

# 4. Build Vector Store
vectorstore = FAISS.from_documents(docs, embeddings)
vectorstore.save_local("vector_store")

print("✅ Vector store built and saved to vector_store/")
