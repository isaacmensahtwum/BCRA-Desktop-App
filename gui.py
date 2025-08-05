import tkinter as tk
from tkinter import filedialog, messagebox, ttk, Toplevel, Label, Entry, Button
import os
import data_loader
import risk_calculator
import db
import pandas as pd

current_results_df = None  # To store results for export

def run_gui():
    def display_results(df):
        # Clear previous table
        for widget in results_frame.winfo_children():
            widget.destroy()

        # Create Treeview table
        tree = ttk.Treeview(results_frame, columns=list(df.columns), show="headings", height=15)

        # Add column headers
        for col in df.columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        # Insert rows
        for _, row in df.iterrows():
            tree.insert("", tk.END, values=list(row))

        # Add scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(expand=True, fill="both")

    def load_csv():
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            df = data_loader.load_from_csv(file_path)
            results = risk_calculator.bcra_analysis(df.values.tolist())
            if results is not None:
                global current_results_df
                current_results_df = results
                display_results(results)

    def load_excel():
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if file_path:
            df = data_loader.load_from_excel(file_path)
            results = risk_calculator.bcra_analysis(df.values.tolist())
            if results is not None:
                global current_results_df
                current_results_df = results
                display_results(results)

    def connect_database():
        def submit_db_details():
            os.environ['DB_HOSTNAME'] = entry_host.get()
            os.environ['DB_NAME'] = entry_db.get()
            os.environ['DB_USERNAME'] = entry_user.get()
            os.environ['DB_PASSWORD'] = entry_pass.get()

            try:
                df = data_loader.load_from_sql()
                results = risk_calculator.bcra_analysis(df.values.tolist())
                if results is not None:
                    global current_results_df
                    current_results_df = results
                    display_results(results)
                db_window.destroy()
            except Exception as e:
                messagebox.showerror("Database Error", str(e))

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

    def export_results():
        if current_results_df is None:
            messagebox.showerror("No Data", "No results to export.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                 filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv")])
        if file_path:
            if file_path.endswith(".csv"):
                current_results_df.to_csv(file_path, index=False)
            else:
                current_results_df.to_excel(file_path, index=False)
            messagebox.showinfo("Export Complete", f"Results saved to {file_path}")

    root = tk.Tk()
    root.title("Breast Cancer Risk Assessment - Desktop App")
    root.geometry("1100x700")

    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="Load CSV", width=25, command=load_csv).grid(row=0, column=0, padx=5)
    tk.Button(button_frame, text="Load Excel", width=25, command=load_excel).grid(row=0, column=1, padx=5)
    tk.Button(button_frame, text="Connect to Database", width=25, command=connect_database).grid(row=0, column=2, padx=5)
    tk.Button(button_frame, text="Export Results", width=25, command=export_results).grid(row=0, column=3, padx=5)
    tk.Button(button_frame, text="Exit", width=25, command=root.destroy).grid(row=0, column=4, padx=5)

    results_frame = tk.Frame(root)
    results_frame.pack(expand=True, fill="both", padx=10, pady=10)

    root.mainloop()

if __name__ == "__main__":
    run_gui()
