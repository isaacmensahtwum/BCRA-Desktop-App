import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import pandas as pd
import db  # reuse your working database connection code

# ==== Requirement explanations ====
REQUIREMENTS_INFO = {
    "Age": "The patient's current age in years.",
    "Biopsies": "Number of prior breast biopsies the patient has had.",
    "Hyperplasia": "Whether atypical hyperplasia was found in a prior biopsy.",
    "Menarche": "Age at which the patient had her first menstrual period.",
    "First Live Birth": "Age at which the patient had her first live birth.",
    "First Degree Relatives": "Number of first-degree relatives with breast cancer (mother, sister, daughter).",
    "Race": "The patient's self-identified race."
}

PINK = "#E75480"
BLUE_LINK = "#007BFF"

# Global variable to store loaded patient data
current_df = None

# ==== Show explanation popups ====
def show_info(requirement):
    messagebox.showinfo(requirement, REQUIREMENTS_INFO.get(requirement, "No info available."))

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
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load CSV file:\n{e}")

# ==== Placeholder actions ====
def generate_report():
    messagebox.showinfo("Generate Report", "Report generation will be implemented later.")

def login_action():
    messagebox.showinfo("Login", "Login functionality will be implemented later.")

# ==== Create styled button ====
def create_styled_button(parent, text, style_name, command=None, fill_x=True):
    btn = ttk.Button(parent, text=text, style=style_name, command=command)
    if fill_x:
        btn.pack(pady=5, ipadx=5, ipady=2, fill="x")
    else:
        btn.pack(pady=5, ipadx=10, ipady=5)
    return btn

# ==== Modern frame with pink header ====
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

    bottom_frame = tk.Frame(root, bg="#f4f6f8", pady=15)
    bottom_frame.pack(fill="both", expand=True, padx=20)
    req_frame, req_content = create_modern_frame(bottom_frame, "Requirements")
    req_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
    for req in REQUIREMENTS_INFO.keys():
        link = tk.Label(req_content, text=req, fg=BLUE_LINK, cursor="hand2", bg="white", font=("Arial", 12, "underline"))
        link.pack(anchor="w", pady=2)
        link.bind("<Button-1>", lambda e, r=req: show_info(r))
    risk_frame, risk_content = create_modern_frame(bottom_frame, "Risk Chart")
    risk_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
    tk.Label(risk_content, text="(Risk chart will be displayed here for a selected patient)", bg="white", font=("Arial", 11), wraplength=250, justify="center").pack(expand=True)

    action_frame = tk.Frame(root, bg="#f4f6f8", pady=20)
    action_frame.pack(fill="x")
    create_styled_button(action_frame, "Generate Report", "PinkFilled.TButton", command=generate_report, fill_x=False)

    root.mainloop()

if __name__ == "__main__":
    create_app()
