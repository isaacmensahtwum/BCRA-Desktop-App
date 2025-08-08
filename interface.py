import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import pandas as pd
import db
import bcra
from fpdf import FPDF
from textwrap import wrap

PINK = "#E75480"
BLUE_LINK = "#007BFF"

# Columns mapping
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

REMOVE_COLS = ["T2", "T3", "Race"] 

# Global vars
current_df = None
display_df = None
tree = None
summary_frame_content = None


REQUIREMENTS_INFO = {
    "Age": "The patient's current age in years.",
    "Biopsies": "Number of prior breast biopsies the patient has had.",
    "Hyperplasia": "Whether atypical hyperplasia was found in a prior biopsy.",
    "Menarche": "Age at which the patient had her first menstrual period.",
    "First Live Birth": "Age at which the patient had her first live birth.",
    "First Degree Relatives": "Number of first-degree relatives with breast cancer (mother, sister, daughter).",
    "Race": "The patient's self-identified race."
}

# ==== Filter & Rename Data ====
def filter_and_rename(df):
    df_filtered = df.drop(columns=[c for c in REMOVE_COLS if c in df.columns], errors="ignore")
    df_filtered = df_filtered.rename(columns={"T1": "Age"})
    return df_filtered

# ==== Show placeholder in summary ====
def show_summary_placeholder():
    for widget in summary_frame_content.winfo_children():
        widget.destroy()
    tk.Label(
        summary_frame_content,
        text="Select a patient to see summary",
        bg="white",
        font=("Arial", 12, "italic"),
        fg="gray"
    ).pack(expand=True)

# ==== Show patient details in summary ====
def show_patient_details(patient_data):
    for widget in summary_frame_content.winfo_children():
        widget.destroy()
    for col, value in patient_data.items():
        tk.Label(summary_frame_content, text=f"{col}: {value}", bg="white", font=("Arial", 11)).pack(anchor="w", pady=2)

# ==== Update summary ====
def update_patient_summary(event=None):
    if tree is None or display_df is None:
        return
    selected_item = tree.selection()
    if not selected_item:
        return
    values = tree.item(selected_item[0], "values")
    patient_data = dict(zip(display_df.columns, values))
    show_patient_details(patient_data)

# ==== Double-click popup ====
def on_double_click(event=None):
    if tree is None or current_df is None:
        return
    selected_item = tree.selection()
    if not selected_item:
        return

    item_id = selected_item[0]
    index = tree.index(item_id)

    actual_row = current_df.iloc[index]

    patient_data = {}
    for internal_col, display_name in COLUMN_MAPPING.items():
        patient_data[display_name] = actual_row.get(internal_col, "N/A")

    popup = tk.Toplevel()
    popup.title("Patient Profile")
    popup.geometry("400x550")
    popup.configure(bg="white")

    tk.Label(
        popup,
        text="Patient Profile",
        font=("Arial", 16, "bold"),
        bg=PINK,
        fg="white",
        pady=10
    ).pack(fill="x")

    content_frame = tk.Frame(popup, bg="white", padx=15, pady=15)
    content_frame.pack(fill="both", expand=True)

    def add_section(title, display_keys):
        tk.Label(content_frame, text=title, font=("Arial", 12, "bold"), fg=PINK, bg="white").pack(anchor="w", pady=(10, 2))
        for label in display_keys:
            value = patient_data.get(label, "N/A")
            tk.Label(content_frame, text=f"{label}: {value}", bg="white", font=("Arial", 11)).pack(anchor="w")

    add_section("Demographics", ["Age", "Race"])
    add_section("Clinical History", ["Biopsies", "Hyperplasia", "Menarche", "First Live Birth", "First Degree Relatives"])
    add_section("Risk Assessment", ["Five Year Risk", "Lifetime Risk"])
    add_section("PCP Notes: ", [])

    # Buttons
    button_frame = tk.Frame(popup, bg="white")
    button_frame.pack(pady=10)

    ttk.Button(button_frame, text="📧 Email Report").pack(pady=5)
    ttk.Button(button_frame, text="📲 Text Report").pack(pady=5)
    ttk.Button(popup, text="Close", command=popup.destroy).pack(pady=10)


# ==== Table display ====
def display_table(df):
    global tree, display_df
    display_df = filter_and_rename(df)

    for widget in table_frame.winfo_children():
        widget.destroy()

    tree = ttk.Treeview(table_frame, show="headings", selectmode="browse")
    tree.pack(side="left", fill="both", expand=True)

    vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
    tree.configure(yscroll=vsb.set, xscroll=hsb.set)
    vsb.pack(side="right", fill="y")
    hsb.pack(side="bottom", fill="x")

    tree["columns"] = list(display_df.columns)
    for col in display_df.columns:
        tree.heading(col, text=col)
        tree.column(col, width=120, anchor="center")

    for _, row in display_df.iterrows():
        tree.insert("", "end", values=list(row))

    tree.bind("<<TreeviewSelect>>", update_patient_summary)
    tree.bind("<Double-1>", on_double_click)

# ==== Loaders ====
def connect_database():
    global current_df
    try:
        conns, cursor = db.setup_dbs()
        query = "SELECT * FROM [bcra].[dbo].exampledata;"
        cursor.execute(query)
        rows = cursor.fetchall()
        current_df = pd.DataFrame.from_records(rows, columns=[col[0] for col in cursor.description])
        display_table(current_df)
        show_summary_placeholder()
    except Exception as e:
        messagebox.showerror("Error", f"DB load failed:\n{e}")

def load_excel_file():
    global current_df
    path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx *.xls")])
    if not path:
        return
    try:
        current_df = pd.read_excel(path)
        display_table(current_df)
        show_summary_placeholder()
    except Exception as e:
        messagebox.showerror("Error", f"Excel load failed:\n{e}")

def load_csv_file():
    global current_df
    path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if not path:
        return
    try:
        current_df = pd.read_csv(path)
        display_table(current_df)
        show_summary_placeholder()
    except Exception as e:
        messagebox.showerror("Error", f"CSV load failed:\n{e}")

# ==== Generate Report ====
def generate_report():
    global current_df
    if current_df is None or current_df.empty:
        messagebox.showerror("No Data", "Load data first.")
        return
    try:
        current_df = bcra.bcra_analysis(current_df.values.tolist())
        display_table(current_df)
        messagebox.showinfo("Success", "Risk assessment completed.")
    except Exception as e:
        messagebox.showerror("Error", f"Gail model failed:\n{e}")

# ==== Save Report functions ====
def save_all_excel():
    if display_df is None or display_df.empty:
        messagebox.showerror("Error", "No data to save.")
        return
    file = filedialog.asksaveasfilename(defaultextension=".xlsx")
    if file:
        display_df.to_excel(file, index=False)

def save_all_csv():
    if display_df is None or display_df.empty:
        messagebox.showerror("Error", "No data to save.")
        return
    file = filedialog.asksaveasfilename(defaultextension=".csv")
    if file:
        display_df.to_csv(file, index=False)

def save_all_pdf():
    if display_df is None or display_df.empty:
        messagebox.showerror("Error", "No data to save.")
        return
    file = filedialog.asksaveasfilename(defaultextension=".pdf")
    if not file:
        return

    class PDF(FPDF):
        def header(self):
            self.set_fill_color(231, 84, 128)
            self.set_text_color(255, 255, 255)
            self.set_font("Arial", "B", 14)
            self.cell(0, 10, "Breast Cancer Risk Assessment Report", ln=True, align="C", fill=True)
            self.ln(4)
        def footer(self):
            self.set_y(-15)
            self.set_font("Arial", "I", 8)
            self.set_text_color(128)
            self.cell(0, 10, f"Page {self.page_no()}", align="C")

    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_page()

    col_width = (pdf.w - 20) / len(display_df.columns)
    row_height = 8
    font_size = 9

    pdf.set_font("Arial", "B", font_size)
    pdf.set_fill_color(240, 128, 128)
    pdf.set_text_color(255, 255, 255)

    # Header
    for col in display_df.columns:
        pdf.cell(col_width, row_height, col, border=1, align="C", fill=True)
    pdf.ln(row_height)

    # Body
    pdf.set_font("Arial", "", font_size)
    pdf.set_text_color(0, 0, 0)

    for _, row in display_df.iterrows():
        max_lines = 1
        wrapped = []

        for value in row:
            lines = wrap(str(value), width=20)  # wrap text to fit in cell
            wrapped.append(lines)
            max_lines = max(max_lines, len(lines))

        for i in range(max_lines):
            for j, cell_lines in enumerate(wrapped):
                text = cell_lines[i] if i < len(cell_lines) else ""
                pdf.cell(col_width, row_height, text, border=1)
            pdf.ln(row_height)

    pdf.output(file)
    messagebox.showinfo("Saved", f"PDF saved:\n{file}")


def export_all_db():
    if display_df is None or display_df.empty:
        messagebox.showerror("Error", "No data to export.")
        return
    try:
        conns, cursor = db.setup_dbs()
        cursor.execute("TRUNCATE TABLE [bcra].[dbo].BCRA_Risk_Assessment")
        for _, row in display_df.iterrows():
            cursor.execute("INSERT INTO [bcra].[dbo].BCRA_Risk_Assessment VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                           tuple(row.values))
        conns.commit()
        messagebox.showinfo("Database", "Exported to database.")
    except Exception as e:
        messagebox.showerror("Error", f"DB export failed:\n{e}")

# ==== Styled button ====
def create_styled_button(parent, text, style_name, command=None, fill_x=True):
    btn = ttk.Button(parent, text=text, style=style_name, command=command)
    if fill_x:
        btn.pack(pady=5, fill="x")
    else:
        btn.pack(pady=5)
    return btn

# ==== Frame helper ====
def create_modern_frame(parent, title, bg_color=PINK):
    frame_container = tk.Frame(parent, bg="white", bd=1, relief="solid")
    header = tk.Frame(frame_container, bg=bg_color)
    header.pack(fill="x")
    tk.Label(header, text=title, bg=bg_color, fg="white", font=("Arial", 14, "bold"), pady=5).pack()
    content_frame = tk.Frame(frame_container, bg="white", padx=10, pady=10)
    content_frame.pack(fill="both", expand=True)
    return frame_container, content_frame

# ==== Create App ====
def create_app():
    global table_frame, summary_frame_content

    root = tk.Tk()
    root.title("Breast Cancer Risk Assessment")
    root.geometry("1200x750")
    root.configure(bg="#f4f6f8")

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Pink.TButton", background=PINK, foreground="black", font=("Arial", 11, "bold"))
    style.configure("White.TButton", background="white", foreground="black", font=("Arial", 11, "bold"))
    style.configure("PinkFilled.TButton", background=PINK, foreground="white", font=("Arial", 12, "bold"))

    # Title bar
    title_bar = tk.Frame(root, bg=PINK, pady=10)
    title_bar.pack(fill="x")
    tk.Label(title_bar, text="Breast Cancer Risk Assessment", font=("Arial", 24, "bold"), fg="white", bg=PINK).pack(side="left", expand=True)

    # Top menu
    top_frame = tk.Frame(root, bg="#f4f6f8", pady=15)
    top_frame.pack(fill="x", padx=20)
    for frame_name, buttons in [
        ("Risk Calculator", [("BCRA Model", "Pink.TButton"), ("Tyrer-Cuzick Model", "White.TButton"), ("BOADICEA Model", "White.TButton")]),
        ("Data Source", [("Connect to DB", "White.TButton", connect_database), ("Load Excel", "White.TButton", load_excel_file), ("Load CSV", "White.TButton", load_csv_file)]),
        ("Decision Support", [("Model Comparison", "White.TButton"), ("Schedule Mammogram", "White.TButton"), ("Guidelines", "White.TButton")])
    ]:
        lf, lf_content = create_modern_frame(top_frame, frame_name)
        lf.pack(side="left", expand=True, fill="both", padx=5)
        for btn in buttons:
            if len(btn) == 3:
                create_styled_button(lf_content, btn[0], btn[1], command=btn[2])
            else:
                create_styled_button(lf_content, btn[0], btn[1])

    # Bottom
    bottom_frame = tk.Frame(root, bg="#f4f6f8", pady=15)
    bottom_frame.pack(fill="both", expand=True, padx=20)

    req_frame, req_content = create_modern_frame(bottom_frame, "Requirements")
    req_frame.pack(side="left", fill="both", expand=True, padx=5)
    for req in REQUIREMENTS_INFO.keys():
        link = tk.Label(req_content, text=req, fg=BLUE_LINK, cursor="hand2", bg="white", font=("Arial", 12, "underline"))
        link.pack(anchor="w", pady=2)

    summary_frame, summary_frame_content = create_modern_frame(bottom_frame, "Patient Summary")
    summary_frame.pack(side="left", fill="both", expand=True, padx=5)
    show_summary_placeholder()

    save_frame, save_content = create_modern_frame(bottom_frame, "Save Report")
    save_frame.pack(side="left", fill="both", expand=True, padx=5)
    create_styled_button(save_content, "Save as Excel", "White.TButton", command=save_all_excel)
    create_styled_button(save_content, "Save as CSV", "White.TButton", command=save_all_csv)
    create_styled_button(save_content, "Save as PDF", "White.TButton", command=save_all_pdf)
    create_styled_button(save_content, "Export to Database", "White.TButton", command=export_all_db)

    # Table area
    table_frame = tk.Frame(root, bg="#f4f6f8")
    table_frame.pack(fill="both", expand=True, padx=20, pady=10)

    # Footer
    footer = tk.Frame(root, bg="#f4f6f8")
    footer.pack(side="bottom", fill="x", pady=5)
    tk.Label(footer, text="Privacy", fg=BLUE_LINK, cursor="hand2", bg="#f4f6f8").pack(side="right", padx=10)
    tk.Label(footer, text="About", fg=BLUE_LINK, cursor="hand2", bg="#f4f6f8").pack(side="right", padx=10)

    # Generate report
    create_styled_button(root, "Generate Report", "PinkFilled.TButton", command=generate_report, fill_x=False)

    root.mainloop()

if __name__ == "__main__":
    create_app()
