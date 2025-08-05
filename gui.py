import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel, Label, Entry, Button
import os
import data_loader
import risk_calculator
import db

def run_gui():
    def load_csv():
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            df = data_loader.load_from_csv(file_path)
            results = risk_calculator.bcra_analysis(df.values.tolist())
            messagebox.showinfo("Calculation Complete", f"Processed {len(results)} patients.")

    def load_excel():
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if file_path:
            df = data_loader.load_from_excel(file_path)
            results = risk_calculator.bcra_analysis(df.values.tolist())
            messagebox.showinfo("Calculation Complete", f"Processed {len(results)} patients.")

    def connect_database():
        def submit_db_details():
            # Save entered values to environment variables
            os.environ['DB_HOSTNAME'] = entry_host.get()
            os.environ['DB_NAME'] = entry_db.get()
            os.environ['DB_USERNAME'] = entry_user.get()
            os.environ['DB_PASSWORD'] = entry_pass.get()

            # Try loading data from SQL
            try:
                df = data_loader.load_from_sql()
                results = risk_calculator.bcra_analysis(df.values.tolist())
                messagebox.showinfo("Calculation Complete", f"Processed {len(results)} patients.")
                db_window.destroy()
            except Exception as e:
                messagebox.showerror("Database Error", str(e))

        # Create popup window for DB details
        db_window = Toplevel(root)
        db_window.title("Database Connection")

        Label(db_window, text="Hostname:").grid(row=0, column=0, sticky="e")
        entry_host = Entry(db_window, width=30)
        entry_host.grid(row=0, column=1)

        Label(db_window, text="Database:").grid(row=1, column=0, sticky="e")
        entry_db = Entry(db_window, width=30)
        entry_db.grid(row=1, column=1)

        Label(db_window, text="Username:").grid(row=2, column=0, sticky="e")
        entry_user = Entry(db_window, width=30)
        entry_user.grid(row=2, column=1)

        Label(db_window, text="Password:").grid(row=3, column=0, sticky="e")
        entry_pass = Entry(db_window, show="*", width=30)
        entry_pass.grid(row=3, column=1)

        Button(db_window, text="Connect", command=submit_db_details).grid(row=4, column=0, columnspan=2, pady=10)

    root = tk.Tk()
    root.title("Breast Cancer Risk Assessment - Desktop App")

    tk.Button(root, text="Load CSV", width=25, command=load_csv).pack(pady=10)
    tk.Button(root, text="Load Excel", width=25, command=load_excel).pack(pady=10)
    tk.Button(root, text="Connect to Database", width=25, command=connect_database).pack(pady=10)
    tk.Button(root, text="Exit", width=25, command=root.destroy).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    run_gui()
