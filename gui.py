import tkinter as tk
from tkinter import filedialog, messagebox, ttk, Toplevel, Label, Entry, Button
import os
import json
import data_loader
import risk_calculator
import db
import pandas as pd

CONFIG_FILE = "db_config.json"
current_results_df = None  # Store analysis results for export/push


# ====== CONFIG SAVE/LOAD ======
def load_saved_db_config():
    """Load last used DB connection details from file."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_db_config(config):
    """Save DB connection details to file."""
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f)
    except Exception as e:
        messagebox.showerror("Error", f"Could not save DB config: {e}")


# ====== MAIN GUI FUNCTION ======
def run_gui():
    global current_results_df

    # ===== Filtering Function =====
    def apply_filters():
        """Filter table based on search term and risk category."""
        if current_results_df is None:
            return

        df = current_results_df.copy()

        # Filter by Patient ID
        search_term = search_var.get().strip().lower()
        if search_term:
            df = df[df["ID"].astype(str).str.lower().str.contains(search_term)]

        # Filter by risk category
        risk_choice = risk_filter_var.get()
        if risk_choice == "Low (<1.67%)":
            df = df[df["Five_Year_Risk"] < 1.67]
        elif risk_choice == "Medium (1.67–3%)":
            df = df[(df["Five_Year_Risk"] >= 1.67) & (df["Five_Year_Risk"] < 3)]
        elif risk_choice == "High (≥3%)":
            df = df[df["Five_Year_Risk"] >= 3]

        display_results(df)

    # ===== Display Table =====
    def display_results(df):
        """Display cleaned DataFrame in a scrollable Treeview."""
        for widget in results_frame.winfo_children():
            widget.destroy()

        # Remove unwanted columns and rename T1 to Age
        columns_to_remove = ["T2", "T3", "Race"]
        df_display = df.drop(columns=[col for col in columns_to_remove if col in df.columns], errors="ignore")
        df_display = df_display.rename(columns={"T1": "Age"})

        # Create Treeview
        tree = ttk.Treeview(results_frame, columns=list(df_display.columns), show="headings", height=15)

        for col in df_display.columns:
            tree.heading(col, text=col)  # display header
            tree.column(col, width=100)

        for _, row in df_display.iterrows():
            tree.insert("", tk.END, values=list(row))

        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(expand=True, fill="both")

    # ===== File & DB Loaders =====
    def load_csv():
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            df = data_loader.load_from_csv(file_path)
            results = risk_calculator.bcra_analysis(df.values.tolist())
            if results is not None:
                current_results_df = results
                display_results(results)

    def load_excel():
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if file_path:
            df = data_loader.load_from_excel(file_path)
            results = risk_calculator.bcra_analysis(df.values.tolist())
            if results is not None:
                current_results_df = results
                display_results(results)

    def prompt_for_credentials():
        """Ask for DB credentials and connect."""
        def submit_db_details():
            config = {
                'DB_HOSTNAME': entry_host.get(),
                'DB_NAME': entry_db.get(),
                'DB_USERNAME': entry_user.get(),
                'DB_PASSWORD': entry_pass.get()
            }
            save_db_config(config)
            for key, value in config.items():
                os.environ[key] = value

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

    def connect_database():
        saved_config = load_saved_db_config()
        if saved_config and messagebox.askyesno("Database Connection", "Use saved credentials?"):
            for key, value in saved_config.items():
                os.environ[key] = value
            try:
                df = data_loader.load_from_sql()
                results = risk_calculator.bcra_analysis(df.values.tolist())
                if results is not None:
                    current_results_df = results
                    display_results(results)
                return
            except Exception as e:
                messagebox.showerror("Database Error", str(e))
                prompt_for_credentials()
        else:
            prompt_for_credentials()

    # ===== Export Results =====
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

    # ===== Push Results to Database =====
    def push_to_database():
        if current_results_df is None:
            messagebox.showerror("No Data", "No results to push to database.")
            return

        saved_config = load_saved_db_config()
        if not saved_config or not messagebox.askyesno("Database Connection", "Use saved credentials to push data?"):
            prompt_for_credentials()
            return
        for key, value in saved_config.items():
            os.environ[key] = value

        try:
            db.setup_dbs()
            db.conns_cursor.execute('TRUNCATE TABLE [bcra].[dbo].BCRA_Risk_Assessment')
            insert_query = """
                INSERT INTO [bcra].[dbo].BCRA_Risk_Assessment
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            data = [
                (
                    row.ID, row.T1, row.N_Biop, row.HypPlas,
                    row.AgeMen, row.Age1st, row.N_Rels, row.Race,
                    row.Five_Year_Risk, row.Lifetime_Risk
                )
                for row in current_results_df.itertuples(index=False)
            ]
            db.conns_cursor.executemany(insert_query, data)
            db.conns.commit()
            messagebox.showinfo("Success", f"Pushed {len(data)} records to the database.")
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            db.close_db_connections()

    # ===== GUI Layout =====
    root = tk.Tk()
    root.title("Breast Cancer Risk Assessment - Desktop App")
    root.geometry("1200x700")

    # Top button bar
    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="Load CSV", width=25, command=load_csv).grid(row=0, column=0, padx=5)
    tk.Button(button_frame, text="Load Excel", width=25, command=load_excel).grid(row=0, column=1, padx=5)
    tk.Button(button_frame, text="Connect to Database", width=25, command=connect_database).grid(row=0, column=2, padx=5)
    tk.Button(button_frame, text="Export Results", width=25, command=export_results).grid(row=0, column=3, padx=5)
    tk.Button(button_frame, text="Push to Database", width=25, command=push_to_database).grid(row=0, column=4, padx=5)
    tk.Button(button_frame, text="Exit", width=25, command=root.destroy).grid(row=0, column=5, padx=5)

    # Search/filter section
    filter_frame = tk.Frame(root)
    filter_frame.pack(fill="x", padx=10, pady=5)

    tk.Label(filter_frame, text="Search Patient ID:").pack(side="left", padx=5)
    search_var = tk.StringVar()
    tk.Entry(filter_frame, textvariable=search_var, width=20).pack(side="left", padx=5)

    tk.Label(filter_frame, text="Risk Filter:").pack(side="left", padx=5)
    risk_filter_var = tk.StringVar(value="All")
    ttk.Combobox(
        filter_frame,
        textvariable=risk_filter_var,
        values=["All", "Low (<1.67%)", "Medium (1.67–3%)", "High (≥3%)"],
        state="readonly",
        width=20
    ).pack(side="left", padx=5)

    tk.Button(filter_frame, text="Apply Filter", command=apply_filters).pack(side="left", padx=5)

    # Results table section
    results_frame = tk.Frame(root)
    results_frame.pack(expand=True, fill="both", padx=10, pady=10)

    root.mainloop()


if __name__ == "__main__":
    run_gui()
