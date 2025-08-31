# test_demo.py
from agents import NL2SQLAgent, SQLExecutorAgent
from db import SQLiteClient

def run_demo():
    db = SQLiteClient("northwind.db")
    sql_agent = SQLExecutorAgent(db)
    nl2sql_agent = NL2SQLAgent()

    test_queries = [
        "How many suppliers are based in the UK?",
        "Show top 5 countries by total sales",
        "Which customers ordered the most in 2024?",
        "What is the total revenue in Q2 2023?",
        "Show best-selling products by quantity",
        "Revenue breakdown by category and quarter",
        "Average order value per customer",
        "Compare sales trends over months/years",
        "Top 3 selling product categories in France",
        "Total orders handled by each employee"
    ]

    for q in test_queries:
        print(f"\n==== Query: {q}")
        gen_result = nl2sql_agent.run(q)
        sql = gen_result.get("sql", "")
        if not sql:
            print("❌ No SQL generated:", gen_result.get("reasoning"))
            continue
        print("Generated SQL:\n", sql)
        result = sql_agent.run(sql)
        print("Query Result:\n", result)

if __name__ == "__main__":
    run_demo()
