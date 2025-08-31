# Db.py
import sqlite3

class DatabaseHandler:
    """
    Handles database connection, query execution, and schema inspection.
    Works with SQLite but can be extended for other databases.
    """

    def __init__(self, db_path: str = "example.db"):
        """
        Initialize connection to the SQLite database.

        :param db_path: Path to the SQLite database file.
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def execute_query(self, query: str):
        """
        Execute a given SQL query and return the results.

        :param query: SQL query string
        :return: List of tuples with query results
        """
        try:
            self.cursor.execute(query)
            self.conn.commit()
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            return f"Database error: {e}"

    def get_schema(self):
        """
        Fetch database schema information (tables and columns).

        :return: Dictionary of tables with their columns
        """
        schema = {}
        try:
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in self.cursor.fetchall()]

            for table in tables:
                self.cursor.execute(f"PRAGMA table_info({table});")
                schema[table] = [col[1] for col in self.cursor.fetchall()]
        except sqlite3.Error as e:
            schema = {"error": str(e)}

        return schema

    def close(self):
        """Close the database connection."""
        self.conn.close()
