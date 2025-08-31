import re
import json
import math
from typing import Dict, Any, Optional, List, Tuple

from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory

from config import settings
from rag import get_retriever
from prompts import NL2SQL_PROMPT, SQL_SYSTEM
from db import SQLiteClient


# ======================================================
# NL2SQLAgent (Agent 2) -- Natural Language to SQL
# ======================================================
class NL2SQLAgent:
    def __init__(
        self,
        llm: Optional[ChatOpenAI] = None,
        retriever=None,
        memory: Optional[ConversationBufferMemory] = None,
    ):
        # LLM
        self.llm = llm or ChatOpenAI(
            model_name=getattr(settings, "OPENAI_MODEL", None) or "gpt-3.5-turbo",
            openai_api_key=getattr(settings, "OPENAI_API_KEY", None),
            temperature=0.0,
        )

        # Retriever (RAG)
        self.retriever = retriever or get_retriever()

        # Memory for multi-turn
        self.memory = memory or ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        # Chain: prompt template -> llm
        self.chain = LLMChain(llm=self.llm, prompt=NL2SQL_PROMPT)

    def _build_context(self, question: str) -> str:
        """
        Build context by combining memory + retrieved schema/docs.
        """
        history_text = ""
        mem = self.memory.load_memory_variables({})
        if mem and mem.get("chat_history"):
            for m in mem["chat_history"]:
                try:
                    who = getattr(m, "type", "user")
                    text = getattr(m, "content", str(m))
                except Exception:
                    who = "user"
                    text = str(m)
                history_text += f"{who}: {text}\n"

        # Retrieve relevant documents using the retriever
        retrieved = self.retriever.get_relevant_documents(question + "\n" + history_text)
        context_chunks = [d.page_content for d in retrieved]
        sources = ", ".join([d.metadata.get("source", "") for d in retrieved if d.metadata.get("source")])
        ctx = ""
        if sources:
            ctx += f"SOURCES: {sources}\n\n"
        ctx += "\n\n".join(context_chunks)
        return ctx

    def run(self, question: str) -> Dict[str, Any]:
        """
        Input: natural language question
        Output: dict containing at least:
           - sql (str)
           - reasoning (str)
           - needs_clarification (bool)
           - clarifying_question (str or None)
        """
        context = self._build_context(question)
        prompt_vars = {"system": SQL_SYSTEM, "context": context, "question": question}

        # Call the chain
        llm_out = self.chain.run(**prompt_vars)

        parsed = {}
        try:
            text = llm_out.strip()
            match = re.search(r"(\{.*\})", text, re.S)
            json_text = match.group(1) if match else text
            parsed = json.loads(json_text)
        except Exception as e:
            parsed = {
                "sql": "",
                "reasoning": f"Failed to parse agent output as JSON: {e}. Raw output: {llm_out}",
                "needs_clarification": True,
                "clarifying_question": "I couldn't parse the model output; could you rephrase or provide more detail?"
            }

        # Save user question to memory
        try:
            self.memory.chat_memory.add_user_message(question)
            if parsed.get("clarifying_question"):
                self.memory.chat_memory.add_ai_message(parsed.get("clarifying_question"))
        except Exception:
            pass

        parsed.setdefault("sql", "")
        parsed.setdefault("reasoning", "")
        parsed.setdefault("needs_clarification", False)
        parsed.setdefault("clarifying_question", None)

        return parsed

    def generate_sql(self, question: str) -> str:
        out = self.run(question)
        if out.get("needs_clarification"):
            raise ValueError(f"Needs clarification: {out.get('clarifying_question')}")
        sql = out.get("sql", "").strip()
        if not sql:
            raise ValueError("No SQL returned by NL2SQLAgent. Reasoning: " + out.get("reasoning", ""))
        return sql


# ======================================================
# SQLExecutorAgent (Agent 1) -- Execute SQL safely
# ======================================================
class SQLExecutorAgent:
    def __init__(self, db_client: SQLiteClient):
        self.db = db_client

    def run(self, sql: str) -> str:
        """
        Validate and run query safely. Returns formatted markdown table + summary.
        """
        # Disallow destructive SQL
        forbidden = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "PRAGMA"]
        sql_upper = sql.strip().upper()
        if not (sql_upper.startswith("SELECT") or sql_upper.startswith("WITH")):
            return "**ERROR**: Refusing to run non-SELECT queries."
        if any(f in sql_upper for f in forbidden):
            return "**ERROR**: Refusing to run non-SELECT or potentially destructive queries."

        try:
            cols, rows = self.db.execute(sql)
        except Exception as e:
            return f"**ERROR**: Failed to execute query: {e}"

        if not rows:
            return "_No results._"

        # Format results as Markdown table
        md = "| " + " | ".join(cols) + " |\n"
        md += "| " + " | ".join(["---"] * len(cols)) + " |\n"
        for row in rows[:50]:  # limit output
            md += "| " + " | ".join(str(x) for x in row) + " |\n"

        # Add summary
        summary = f"**Summary:** {len(rows)} rows"
        if re.search(r"GROUP BY", sql, re.I):
            summary += " (grouped by: )"
        return md + "\n\n" + summary

