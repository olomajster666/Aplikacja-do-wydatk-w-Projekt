import sqlite3
from datetime import datetime


class ExpenseTracker:
    def __init__(self):
        self.conn = sqlite3.connect("expenses.db")
        self.cursor = self.conn.cursor()
        self.create_table()
        self.create_budget_table()

    def create_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT
        )
        """)
        self.conn.commit()

    def create_budget_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS budget (
            month_year TEXT PRIMARY KEY,
            budget REAL NOT NULL
        )
        """)
        self.conn.commit()

    def set_budget(self, month_year, budget):
        self.cursor.execute("""
        INSERT OR REPLACE INTO budget (month_year, budget) VALUES (?, ?)
        """, (month_year, budget))
        self.conn.commit()

    def get_budget(self, month_year):
        self.cursor.execute("SELECT budget FROM budget WHERE month_year = ?", (month_year,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def add_expense(self, amount, category, description=""):
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("INSERT INTO expenses (amount, category, date, description) VALUES (?, ?, ?, ?)",
                            (amount, category, date, description))
        self.conn.commit()

    def view_expenses_by_month(self, month_year):
        self.cursor.execute("""
        SELECT * FROM expenses WHERE strftime('%Y-%m', date) = ?
        """, (month_year,))
        return self.cursor.fetchall()

    def calculate_remaining_budget(self, month_year):
        budget = self.get_budget(month_year) or 0
        self.cursor.execute("""
        SELECT SUM(amount) FROM expenses WHERE strftime('%Y-%m', date) = ?
        """, (month_year,))
        total_spent = self.cursor.fetchone()[0] or 0
        return budget - total_spent

    def get_expenses_summary_by_category(self, month_year):
        self.cursor.execute("""
        SELECT category, SUM(amount) FROM expenses WHERE strftime('%Y-%m', date) = ? GROUP BY category
        """, (month_year,))
        return self.cursor.fetchall()

    def __del__(self):
        self.conn.close()
