# tests_demo.py
"""
Smoke tests: run 10 sample queries end-to-end.
"""
from agents import NL2SQLAgent, SQLExecutorAgent
from config import settings

QUERIES = [
    "Show top 5 countries by total sales",
    "Show best-selling products by quantity",
    "Revenue breakdown by category and quarter",
    "Average order value per customer",
    "Compare sales trends over months in 1997",
    "Which customers ordered the most in 1997?",
    "What are the top 3 selling product categories in France?",
    "How many suppliers are based in the UK?",
    "What is the total revenue in Q2 1997?",
    "Top employees by sales in 1997"
]

def run():
    gen = NL2SQLAgent()
    exe = SQLExecutorAgent(settings.DB_PATH)
    for q in QUERIES:
        print("\n====", q)
        plan = gen.run(q)
        sql = plan.get("sql", "")
        print("Generated SQL:\n", sql)
        if plan.get("needs_clarification"):
            print("Clarification needed:", plan.get("clarifying_question"))
            continue
        if not sql:
            print("No SQL generated. Reasoning:", plan.get("reasoning"))
            continue
        res = exe.run(sql)
        if res.get("error"):
            print("ERROR:", res["error"])
        else:
            print("Rows:", res["rows"])
            print(res["table_markdown"][:1000])  # print first 1000 chars of table preview

if __name__ == "__main__":
    run()
