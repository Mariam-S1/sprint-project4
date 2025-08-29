# app.py
"""
Simple CLI app to demonstrate NL->SQL and execution.
"""
from agents import NL2SQLAgent, SQLExecutorAgent
from config import settings

BANNER = """
Northwind Agentic RAG — NL→SQL + SQL Executor
Type a question (or 'quit'). Examples:
- Which customers ordered the most in 1997?
- What are the top 3 selling product categories in France?
- How many suppliers are based in the UK?
- What is the total revenue in Q2 1997?
"""

def main():
    gen = NL2SQLAgent()
    exe = SQLExecutorAgent(settings.DB_PATH)
    print(BANNER)
    while True:
        q = input("\nYour question> ").strip()
        if q.lower() in {"quit", "exit"}:
            print("Bye.")
            break
        plan = gen.run(q)
        if plan.get("needs_clarification"):
            print("\n⚠️ Clarification needed:", plan.get("clarifying_question"))
            follow = input("Your answer> ").strip()
            q2 = q + " Additional details: " + follow
            plan = gen.run(q2)
        sql = plan.get("sql", "").strip()
        if not sql:
            print("\n❌ No SQL generated. Reasoning:", plan.get("reasoning"))
            continue
        print("\n🔎 SQL generated:\n")
        print(sql)
        result = exe.run(sql)
        if result.get("error"):
            print("\n❌ Error:", result["error"])
            continue
        print(f"\n✅ Rows: {result['rows']}\n")
        print(result["table_markdown"])

if __name__ == "__main__":
    main()
