# rag.py
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import google.generativeai as genai
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI

# smart_uae_agent.py
from __future__ import annotations
import os
from typing import Any, Dict
from datetime import datetime

# LangChain imports
from langchain.agents import initialize_agent, Tool, AgentType
from langchain.memory import ConversationBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI

# ---------------------------------------------------------------------
# ✅ Setup Google Gemini API
# ---------------------------------------------------------------------
# Make sure you set your API key:
# export GOOGLE_API_KEY="your-key-here"

if "GOOGLE_API_KEY" not in os.environ:
    raise ValueError("❌ GOOGLE_API_KEY not set. Please export it before running.")

# Initialize Gemini model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro",  # or "gemini-2.5-flash" if you want it faster
    temperature=0
)

# ---------------------------------------------------------------------
# ✅ Define Custom Tools
# ---------------------------------------------------------------------

def uae_knowledge_tool_func(query: str) -> str:
    """Answer general knowledge questions about UAE."""
    knowledge_base: Dict[str, str] = {
        "capital": "The capital of the UAE is Abu Dhabi.",
        "currency": "The currency of the UAE is the Dirham (AED).",
        "language": "The official language of the UAE is Arabic.",
        "ruler": "The President of the UAE is Sheikh Mohamed bin Zayed Al Nahyan."
    }
    for key, value in knowledge_base.items():
        if key in query.lower():
            return value
    return "I don’t know the answer to that UAE-related question."


def prayer_time_tool_func(city: str) -> str:
    """Return a simple mock prayer time based on city."""
    now = datetime.now()
    fajr = now.replace(hour=5, minute=0).strftime("%H:%M")
    dhuhr = now.replace(hour=12, minute=30).strftime("%H:%M")
    asr = now.replace(hour=15, minute=45).strftime("%H:%M")
    maghrib = now.replace(hour=18, minute=15).strftime("%H:%M")
    isha = now.replace(hour=19, minute=45).strftime("%H:%M")

    return (
        f"Prayer times for {city} today:\n"
        f"Fajr: {fajr}\n"
        f"Dhuhr: {dhuhr}\n"
        f"Asr: {asr}\n"
        f"Maghrib: {maghrib}\n"
        f"Isha: {isha}"
    )


def trip_budget_tool_func(input_text: str) -> str:
    """Estimate a simple UAE trip budget."""
    base_cost = 3000  # base AED cost
    if "luxury" in input_text.lower():
        return f"Estimated budget for a luxury trip to the UAE is {base_cost * 3} AED."
    elif "budget" in input_text.lower():
        return f"Estimated budget for a budget-friendly trip to the UAE is {base_cost} AED."
    else:
        return f"Estimated budget for a standard trip to the UAE is {base_cost * 2} AED."


# ---------------------------------------------------------------------
# ✅ Register Tools
# ---------------------------------------------------------------------
tools = [
    Tool(
        name="UAE Knowledge Tool",
        func=uae_knowledge_tool_func,
        description="Useful for answering general knowledge questions about the UAE."
    ),
    Tool(
        name="Prayer Time Tool",
        func=prayer_time_tool_func,
        description="Useful for retrieving today's prayer times for a given UAE city."
    ),
    Tool(
        name="Trip Budget Tool",
        func=trip_budget_tool_func,
        description="Useful for estimating travel budgets to the UAE."
    ),
]

# ---------------------------------------------------------------------
# ✅ Create Agent
# ---------------------------------------------------------------------
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    verbose=True,
    memory=memory,
)

# ---------------------------------------------------------------------
# ✅ Run Main Loop
# ---------------------------------------------------------------------
if __name__ == "__main__":
    print("🤖 Smart UAE Agent (Gemini Edition)")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("👋 Goodbye!")
            break

        response = agent.run(user_input)
        print(f"Agent: {response}\n")


# 3. Split into chunks
splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
chunks = splitter.split_documents(docs)
print(f"✅ Split into {len(chunks)} chunks")

# 4. Create embeddings using Gemini
class GeminiEmbeddings:
    def __init__(self, model="models/embedding-001"):
        self.model = model

    def embed_documents(self, texts):
        embeddings = []
        for text in texts:
            result = genai.embed_text(model=self.model, text=text)
            embeddings.append(result["embedding"])
        return embeddings

embeddings = GeminiEmbeddings()
# 5. Build FAISS vector store
vectorstore = FAISS.from_documents(chunks, embeddings)

# 6. Save FAISS store locally
vectorstore.save_local("faiss_store")
print("✅ FAISS vector store saved in faiss_store/")

