import sqlite3
from datetime import datetime

# Po³¹czenie z baz¹ danych i tworzenie tabel
class ExpenseTracker:
    def __init__(self, db_name="expenses.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        # Tworzenie tabeli wydatków
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT
        )
        ''')

        # Tworzenie tabeli oszczêdnoœci
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS savings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            goal TEXT
        )
        ''')

        # Tworzenie tabeli bud¿etu
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS budget (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            month TEXT NOT NULL,
            planned_amount REAL NOT NULL
        )
        ''')

        self.conn.commit()

    # CRUD dla wydatków
    def add_expense(self, amount, category, description=""):
        date = datetime.now().strftime("%Y-%m-%d")
        self.cursor.execute('''
        INSERT INTO expenses (amount, category, date, description)
        VALUES (?, ?, ?, ?)
        ''', (amount, category, date, description))
        self.conn.commit()

    def view_expenses(self):
        self.cursor.execute('SELECT * FROM expenses')
        return self.cursor.fetchall()

    def update_expense(self, expense_id, amount=None, category=None, description=None):
        updates = []
        params = []
        if amount is not None:
            updates.append("amount = ?")
            params.append(amount)
        if category is not None:
            updates.append("category = ?")
            params.append(category)
        if description is not None:
            updates.append("description = ?")
            params.append(description)
        params.append(expense_id)

        self.cursor.execute(f'''
        UPDATE expenses SET {', '.join(updates)} WHERE id = ?
        ''', params)
        self.conn.commit()

    def delete_expense(self, expense_id):
        self.cursor.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
        self.conn.commit()

    # CRUD dla oszczêdnoœci
    def add_saving(self, amount, goal=""):
        date = datetime.now().strftime("%Y-%m-%d")
        self.cursor.execute('''
        INSERT INTO savings (amount, date, goal)
        VALUES (?, ?, ?)
        ''', (amount, date, goal))
        self.conn.commit()

    def view_savings(self):
        self.cursor.execute('SELECT * FROM savings')
        return self.cursor.fetchall()

    # CRUD dla bud¿etu
    def set_budget(self, month, planned_amount):
        self.cursor.execute('''
        INSERT OR REPLACE INTO budget (month, planned_amount)
        VALUES (?, ?)
        ''', (month, planned_amount))
        self.conn.commit()

    def view_budget(self):
        self.cursor.execute('SELECT * FROM budget')
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()

# Przyk³ad u¿ycia
if __name__ == "__main__":
    tracker = ExpenseTracker()

    # Dodawanie wydatków
    tracker.add_expense(50.0, "Food", "Lunch")
    tracker.add_expense(20.0, "Transport", "Bus ticket")

    # Wyœwietlanie wydatków
    print("Wydatki:", tracker.view_expenses())

    # Aktualizacja wydatku
    tracker.update_expense(1, amount=55.0, description="Lunch with coffee")
    print("Wydatki po aktualizacji:", tracker.view_expenses())

    # Usuwanie wydatku
    tracker.delete_expense(2)
    print("Wydatki po usuniêciu:", tracker.view_expenses())

    # Dodawanie oszczêdnoœci
    tracker.add_saving(100.0, "Vacation")
    print("Oszczêdnoœci:", tracker.view_savings())

    # Ustawianie bud¿etu
    tracker.set_budget("2025-01", 500.0)
    print("Bud¿et:", tracker.view_budget())

    tracker.close()

