# app.py
from agents import NL2SQLAgent, SQLExecutorAgent
from db import SQLiteClient

def main():
    print("🔹 Northwind Agentic RAG — NL→SQL + SQL Executor")
    print("Type a question (or 'quit'):\n"
          "Examples:\n"
          "- Which customers ordered the most in 2024?\n"
          "- What are the top 3 selling product categories in France?\n"
          "- How many suppliers are based in the UK?\n"
          "- What is the total revenue in Q2 2023?\n")

    # Initialize agents
    db_client = SQLiteClient("northwind.db")
    sql_agent = SQLExecutorAgent(db_client)
    nl2sql_agent = NL2SQLAgent()

    while True:
        question = input("Your question> ").strip()
        if question.lower() in ["quit", "exit"]:
            print("Goodbye!")
            break
        if not question:
            continue

        # Generate SQL using NL2SQLAgent
        gen_result = nl2sql_agent.run(question)
        sql = gen_result.get("sql", "")
        if gen_result.get("needs_clarification"):
            print(f"❗ Clarification needed: {gen_result.get('clarifying_question')}")
            continue
        if not sql:
            print(f"❌ Failed to generate SQL: {gen_result.get('reasoning')}")
            continue

        print("\n🔎 SQL generated:\n", sql)

        # Execute SQL safely
        result = sql_agent.run(sql)
        print("\n💡 Query Result:\n", result)

if __name__ == "__main__":
    main()
