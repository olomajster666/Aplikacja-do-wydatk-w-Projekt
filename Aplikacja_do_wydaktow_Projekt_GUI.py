import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from fpdf import FPDF
from Aplikacja_do_wydatkow_Projekt import ExpenseTracker


class ExpenseTrackerGUI:
    def __init__(self, root):
        self.tracker = ExpenseTracker()
        self.root = root
        self.root.title("Expense Tracker")

        # Zmienna na przechowywanie stylu
        self.dark_mode = tk.BooleanVar(value=False)

        # Zmienna na przechowywanie miesiecznego budzetu
        self.month_year = datetime.now().strftime("%Y-%m")
        self.budget = tk.DoubleVar(value=self.tracker.get_budget(self.month_year) or 0)
        self.remaining_budget = tk.DoubleVar(value=self.tracker.calculate_remaining_budget(self.month_year))

        # Konfiguracja interfejsu
        self.setup_ui()
        self.update_budget_display()
        self.update_expenses_list()

    def setup_ui(self):
        # Gorne menu
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)
        settings_menu = tk.Menu(menu_bar, tearoff=0)
        settings_menu.add_checkbutton(label="Ciemny motyw", variable=self.dark_mode, command=self.toggle_theme)
        menu_bar.add_cascade(label="Ustawienia", menu=settings_menu)

        # Sekcja budzetu
        budget_frame = ttk.LabelFrame(self.root, text="Budzet miesieczny")
        budget_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

        tk.Label(budget_frame, text="Ustaw budzet:").grid(row=0, column=0, padx=5, pady=5)
        self.budget_entry = tk.Entry(budget_frame, textvariable=self.budget)
        self.budget_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(budget_frame, text="Zapisz budzet", command=self.save_budget).grid(row=0, column=2, padx=5, pady=5)
        tk.Label(budget_frame, text="Pozostaly budzet:").grid(row=1, column=0, padx=5, pady=5)
        self.remaining_budget_label = tk.Label(budget_frame, textvariable=self.remaining_budget, font=("Arial", 12, "bold"))
        self.remaining_budget_label.grid(row=1, column=1, padx=5, pady=5)

        # Sekcja dodawania wydatkow
        add_expense_frame = ttk.LabelFrame(self.root, text="Dodaj wydatek")
        add_expense_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        tk.Label(add_expense_frame, text="Kwota:").grid(row=0, column=0, padx=5, pady=5)
        self.expense_amount = tk.Entry(add_expense_frame)
        self.expense_amount.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(add_expense_frame, text="Kategoria:").grid(row=1, column=0, padx=5, pady=5)
        self.expense_category = tk.Entry(add_expense_frame)
        self.expense_category.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(add_expense_frame, text="Opis:").grid(row=2, column=0, padx=5, pady=5)
        self.expense_description = tk.Entry(add_expense_frame)
        self.expense_description.grid(row=2, column=1, padx=5, pady=5)

        tk.Button(add_expense_frame, text="Dodaj", command=self.add_expense).grid(row=3, column=0, columnspan=2, pady=5)

        # Lista wydatkow
        list_frame = ttk.LabelFrame(self.root, text="Lista wydatkow")
        list_frame.grid(row=1, column=1, padx=10, pady=5, sticky="nsew")

        self.expense_list = ttk.Treeview(list_frame, columns=("id", "amount", "category", "date", "description"), show="headings")
        self.expense_list.heading("id", text="ID")
        self.expense_list.heading("amount", text="Kwota")
        self.expense_list.heading("category", text="Kategoria")
        self.expense_list.heading("date", text="Data")
        self.expense_list.heading("description", text="Opis")
        self.expense_list.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

        # Przycisk usuwania wydatkow
        tk.Button(list_frame, text="Usun wydatek", command=self.delete_expense).grid(row=1, column=0, columnspan=2, pady=5)

        # Przycisk do generowania raportu
        tk.Button(self.root, text="Generuj raport PDF", command=self.generate_pdf).grid(row=2, column=0, columnspan=2, pady=10)

    def save_budget(self):
        try:
            budget = float(self.budget_entry.get())
            self.tracker.set_budget(self.month_year, budget)
            self.update_budget_display()
            messagebox.showinfo("Sukces", "Budzet zostal zapisany.")
        except ValueError:
            messagebox.showerror("Blad", "Nieprawidlowa kwota.")

    def update_budget_display(self):
        self.remaining_budget.set(self.tracker.calculate_remaining_budget(self.month_year))

    def update_expenses_list(self):
        for item in self.expense_list.get_children():
            self.expense_list.delete(item)
        expenses = self.tracker.view_expenses_by_month(self.month_year)
        for expense in expenses:
            self.expense_list.insert("", "end", values=expense)

    def add_expense(self):
        try:
            amount = float(self.expense_amount.get())
            category = self.expense_category.get()
            description = self.expense_description.get()
            self.tracker.add_expense(amount, category, description)
            self.update_expenses_list()
            self.update_budget_display()
            messagebox.showinfo("Sukces", "Wydatek zostal dodany.")
        except ValueError:
            messagebox.showerror("Blad", "Nieprawidlowa kwota.")

    def delete_expense(self):
        selected_item = self.expense_list.selection()
        if not selected_item:
            messagebox.showerror("Blad", "Nie wybrano zadnego wydatku.")
            return

        expense_id = self.expense_list.item(selected_item, "values")[0]
        self.tracker.cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        self.tracker.conn.commit()
        self.update_expenses_list()
        self.update_budget_display()
        messagebox.showinfo("Sukces", "Wydatek zostal usuniety.")

    def generate_pdf(self):
        expenses = self.tracker.view_expenses_by_month(self.month_year)
        summary = self.tracker.get_expenses_summary_by_category(self.month_year)
        remaining_budget = self.tracker.calculate_remaining_budget(self.month_year)

        pdf = FPDF()
        pdf.add_page() 
        pdf.add_font('Arial', '', r'C:\Windows\Fonts\arial.ttf', uni=True)  # Œcie¿ka do czcionki TrueType (arial.ttf)
        pdf.set_font('Arial', '', 12)   

        pdf.cell(200, 10, txt="Raport wydatkow - " + self.month_year, ln=True, align="C")
        pdf.ln(10)
        pdf.cell(200, 10, txt=f"Budzet: {self.budget.get()}", ln=True)
        pdf.cell(200, 10, txt=f"Pozostaly budzet: {remaining_budget}", ln=True)
        pdf.ln(10)

        pdf.cell(200, 10, txt="Lista wydatkow:", ln=True)
        for expense in expenses:
            pdf.cell(200, 10, txt=f"{expense[3]} - {expense[1]} PLN - {expense[2]} - {expense[4]}", ln=True)

        pdf.ln(10)
        pdf.cell(200, 10, txt="Podsumowanie kategorii:", ln=True)
        for category, total in summary:
            pdf.cell(200, 10, txt=f"{category}: {total} PLN", ln=True)

        pdf.output("raport.pdf")
        messagebox.showinfo("Sukces", "Raport zostal wygenerowany jako raport.pdf.")

    def toggle_theme(self):
        if self.dark_mode.get():
            self.root.configure(bg="black")
        else:
            self.root.configure(bg="white")


# Uruchomienie aplikacji
if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerGUI(root)
    root.mainloop()
