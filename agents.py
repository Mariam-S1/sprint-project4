import re
import json
from typing import Any, Dict, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from rag import get_retriever
from prompts import NL2SQL_PROMPT, SQL_SYSTEM
from db import SQLiteClient  # your SQLite client

# ======================================================
# NL2SQLAgent (Gemini)
# ======================================================
class NL2SQLAgent:
    def __init__(
        self,
        llm: Optional[ChatGoogleGenerativeAI] = None,
        retriever=None,
        memory: Optional[ConversationBufferMemory] = None,
    ):
        self.llm = llm or ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0)
        self.retriever = retriever or get_retriever()
        self.memory = memory or ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.chain = LLMChain(llm=self.llm, prompt=NL2SQL_PROMPT)

    def _build_context(self, question: str) -> str:
        history_text = ""
        mem = self.memory.load_memory_variables({})
        if mem and mem.get("chat_history"):
            for m in mem["chat_history"]:
                who = getattr(m, "type", "user")
                text = getattr(m, "content", str(m))
                history_text += f"{who}: {text}\n"
        retrieved = self.retriever.get_relevant_documents(question + "\n" + history_text)
        context_chunks = [d.page_content for d in retrieved]
        sources = ", ".join([d.metadata.get("source", "") for d in retrieved if d.metadata.get("source")])
        ctx = f"SOURCES: {sources}\n\n" if sources else ""
        ctx += "\n\n".join(context_chunks)
        return ctx

    def run(self, question: str) -> Dict[str, Any]:
        context = self._build_context(question)
        prompt_vars = {"system": SQL_SYSTEM, "context": context, "question": question}
        llm_out = self.chain.run(**prompt_vars)

        try:
            json_text = re.search(r"(\{.*\})", llm_out, re.S).group(1)
            parsed = json.loads(json_text)
        except Exception as e:
            parsed = {
                "sql": "",
                "reasoning": f"Failed to parse output: {e}",
                "needs_clarification": True,
                "clarifying_question": "Please clarify your request."
            }

        return parsed

    def generate_sql(self, question: str) -> str:
        out = self.run(question)
        if out.get("needs_clarification"):
            raise ValueError(out.get("clarifying_question"))
        return out.get("sql", "").strip()

# ======================================================
# SQLExecutorAgent
# ======================================================
class SQLExecutorAgent:
    def __init__(self, db_client: SQLiteClient):
        self.db = db_client

    def run(self, sql: str) -> str:
        forbidden = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "PRAGMA"]
        if any(f in sql.upper() for f in forbidden):
            return "**ERROR**: Refusing to execute potentially destructive SQL."
        try:
            cols, rows = self.db.execute(sql)
        except Exception as e:
            return f"**ERROR**: {e}"
        if not rows:
            return "_No results._"
        md = "| " + " | ".join(cols) + " |\n"
        md += "| " + " | ".join(["---"] * len(cols)) + " |\n"
        for row in rows[:50]:
            md += "| " + " | ".join(str(x) for x in row) + " |\n"
        return md
