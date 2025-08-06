import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import pandas as pd
import db
import bcra  # Gail model logic

# ==== Column mapping (real data -> display name) ====
COLUMN_MAPPING = {
    "T1": "Age",
    "N_Biop": "Biopsies",
    "HypPlas": "Hyperplasia",
    "AgeMen": "Menarche",
    "Age1st": "First Live Birth",
    "N_Rels": "First Degree Relatives",
    "RaceName": "Race",
    "Five_Year_Risk": "Five Year Risk",
    "Lifetime_Risk": "Lifetime Risk"
}

PINK = "#E75480"
BLUE_LINK = "#007BFF"

# Global variables
current_df = None
tree = None
summary_labels = {}

# ==== Show explanation popups ====
REQUIREMENTS_INFO = {
    "Age": "The patient's current age in years.",
    "Biopsies": "Number of prior breast biopsies the patient has had.",
    "Hyperplasia": "Whether atypical hyperplasia was found in a prior biopsy.",
    "Menarche": "Age at which the patient had her first menstrual period.",
    "First Live Birth": "Age at which the patient had her first live birth.",
    "First Degree Relatives": "Number of first-degree relatives with breast cancer (mother, sister, daughter).",
    "Race": "The patient's self-identified race."
}

def show_info(requirement):
    messagebox.showinfo(requirement, REQUIREMENTS_INFO.get(requirement, "No info available."))

# ==== Update patient summary ====
def update_patient_summary(event=None):
    if tree is None or current_df is None:
        return

    selected_item = tree.selection()
    if not selected_item:
        return

    values = tree.item(selected_item[0], "values")
    if not values:
        return

    patient_data = dict(zip(current_df.columns, values))

    # Update labels based on mapping
    for col, display_name in COLUMN_MAPPING.items():
        value = patient_data.get(col, "N/A")
        summary_labels[display_name].config(text=f"{display_name}: {value}")

# ==== Table display ====
def display_table(df):
    global tree
    if df is None or df.empty:
        messagebox.showwarning("No Data", "No data to display.")
        return

    for widget in table_frame.winfo_children():
        widget.destroy()

    tree = ttk.Treeview(table_frame, show="headings", selectmode="browse")
    tree.pack(side="left", fill="both", expand=True)

    vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
    tree.configure(yscroll=vsb.set, xscroll=hsb.set)
    vsb.pack(side="right", fill="y")
    hsb.pack(side="bottom", fill="x")

    tree["columns"] = list(df.columns)
    for col in df.columns:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor="center")

    for _, row in df.iterrows():
        tree.insert("", "end", values=list(row))

    # Bind selection event
    tree.bind("<<TreeviewSelect>>", update_patient_summary)

# ==== Data loading functions ====
def connect_database():
    global current_df
    try:
        conns, cursor = db.setup_dbs()
        if not cursor:
            messagebox.showerror("Database Error", "Failed to connect to database.")
            return
        query = "SELECT * FROM [bcra].[dbo].exampledata;"
        cursor.execute(query)
        rows = cursor.fetchall()
        current_df = pd.DataFrame.from_records(rows, columns=[col[0] for col in cursor.description])
        messagebox.showinfo("Database", f"Loaded {len(current_df)} patient records from database.")
        display_table(current_df)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load from database:\n{e}")

def load_excel_file():
    global current_df
    file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx *.xls")])
    if not file_path:
        return
    try:
        current_df = pd.read_excel(file_path)
        messagebox.showinfo("Excel Load", f"Loaded {len(current_df)} records from Excel file.")
        display_table(current_df)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load Excel file:\n{e}")

def load_csv_file():
    global current_df
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if not file_path:
        return
    try:
        current_df = pd.read_csv(file_path)
        messagebox.showinfo("CSV Load", f"Loaded {len(current_df)} records from CSV file.")
        display_table(current_df)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load CSV file:\n{e}")

# ==== Generate Report ====
def generate_report():
    global current_df
    if current_df is None or current_df.empty:
        messagebox.showerror("No Data", "Please load patient data first.")
        return

    try:
        results_df = bcra.bcra_analysis(current_df.values.tolist())
        current_df = results_df
        display_table(current_df)
        messagebox.showinfo("Success", "Risk assessment completed successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to run Gail model:\n{e}")

# ==== Login placeholder ====
def login_action():
    messagebox.showinfo("Login", "Login functionality will be implemented later.")

# ==== Styled button helper ====
def create_styled_button(parent, text, style_name, command=None, fill_x=True):
    btn = ttk.Button(parent, text=text, style=style_name, command=command)
    if fill_x:
        btn.pack(pady=5, ipadx=5, ipady=2, fill="x")
    else:
        btn.pack(pady=5, ipadx=10, ipady=5)
    return btn

# ==== Modern frame helper ====
def create_modern_frame(parent, title, bg_color=PINK, text_color="white"):
    frame_container = tk.Frame(parent, bg="white", bd=1, relief="solid")
    header = tk.Frame(frame_container, bg=bg_color)
    header.pack(fill="x")
    tk.Label(header, text=title, bg=bg_color, fg=text_color, font=("Arial", 14, "bold"), pady=5).pack()
    content_frame = tk.Frame(frame_container, bg="white", padx=10, pady=10)
    content_frame.pack(fill="both", expand=True)
    return frame_container, content_frame

# ==== Create application ====
def create_app():
    global table_frame, summary_labels
    root = tk.Tk()
    root.title("Breast Cancer Risk Assessment")
    root.geometry("1200x750")
    root.configure(bg="#f4f6f8")

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Pink.TButton", background=PINK, foreground="black", font=("Arial", 11, "bold"), borderwidth=1)
    style.map("Pink.TButton", background=[("active", PINK)], foreground=[("active", "black")])
    style.configure("White.TButton", background="white", foreground="black", font=("Arial", 11, "bold"), borderwidth=1, relief="solid")
    style.map("White.TButton", background=[("active", "#f0f0f0")])
    style.configure("PinkFilled.TButton", background=PINK, foreground="white", font=("Arial", 12, "bold"), borderwidth=1)
    style.map("PinkFilled.TButton", background=[("active", PINK)], foreground=[("active", "white")])

    # Title bar
    title_bar = tk.Frame(root, bg=PINK, pady=10)
    title_bar.pack(fill="x")
    try:
        logo_img = Image.open("breast_cancer_logo.png").resize((40, 40), Image.LANCZOS)
        ribbon_logo = ImageTk.PhotoImage(logo_img)
        logo_label = tk.Label(title_bar, image=ribbon_logo, bg=PINK)
        logo_label.image = ribbon_logo
        logo_label.pack(side="left", padx=(20, 5))
    except FileNotFoundError:
        print("Logo image 'breast_cancer_logo.png' not found.")
    tk.Label(title_bar, text="Breast Cancer Risk Assessment", font=("Arial", 24, "bold"), fg="white", bg=PINK).pack(side="left", expand=True)
    ttk.Button(title_bar, text="Login", style="White.TButton", command=login_action).pack(side="right", padx=20)

    # Top buttons
    top_frame = tk.Frame(root, bg="#f4f6f8", pady=15)
    top_frame.pack(fill="x", padx=20)
    for frame_name, buttons in [
        ("Risk Calculator", [("BCRA", "Pink.TButton"), ("Tyrer-Cuzick", "White.TButton"), ("BOADICEA", "White.TButton")]),
        ("Data Source", [("Connect to DB", "White.TButton", connect_database), ("Load Excel", "White.TButton", load_excel_file), ("Load CSV", "White.TButton", load_csv_file)]),
        ("Decision Support", [("Model Comparison", "White.TButton"), ("Report", "White.TButton"), ("Guidelines", "White.TButton")])
    ]:
        lf, lf_content = create_modern_frame(top_frame, frame_name)
        lf.pack(side="left", expand=True, fill="both", padx=5)
        for btn_info in buttons:
            if len(btn_info) == 3:
                btn_text, btn_style, btn_cmd = btn_info
                create_styled_button(lf_content, btn_text, btn_style, command=btn_cmd)
            else:
                btn_text, btn_style = btn_info
                create_styled_button(lf_content, btn_text, btn_style)

    # Bottom section with Requirements and Patient Summary
    bottom_frame = tk.Frame(root, bg="#f4f6f8", pady=15)
    bottom_frame.pack(fill="both", expand=True, padx=20)

    # Requirements
    req_frame, req_content = create_modern_frame(bottom_frame, "Requirements")
    req_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
    for req in REQUIREMENTS_INFO.keys():
        link = tk.Label(req_content, text=req, fg=BLUE_LINK, cursor="hand2", bg="white", font=("Arial", 12, "underline"))
        link.pack(anchor="w", pady=2)
        link.bind("<Button-1>", lambda e, r=req: show_info(r))

    # Patient Summary
    summary_frame, summary_content = create_modern_frame(bottom_frame, "Patient Summary")
    summary_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    # Default message before data is loaded
    default_label = tk.Label(summary_content, text="Select a patient to see summary", bg="white", font=("Arial", 11, "italic"))
    default_label.pack(anchor="w", pady=2)

    # Create summary labels
    for display_name in COLUMN_MAPPING.values():
        lbl = tk.Label(summary_content, text=f"{display_name}: N/A", bg="white", font=("Arial", 11))
        lbl.pack(anchor="w", pady=2)
        summary_labels[display_name] = lbl

    # Table display area
    table_frame = tk.Frame(root, bg="#f4f6f8")
    table_frame.pack(fill="both", expand=True, padx=20, pady=10)

    # Generate Report
    action_frame = tk.Frame(root, bg="#f4f6f8", pady=20)
    action_frame.pack(fill="x")
    create_styled_button(action_frame, "Generate Report", "PinkFilled.TButton", command=generate_report, fill_x=False)

    root.mainloop()

if __name__ == "__main__":
    create_app()
