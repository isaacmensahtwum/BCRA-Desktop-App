import tkinter as tk
from tkinter import messagebox

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

# ==== Show explanation popups ====
def show_info(requirement):
    messagebox.showinfo(requirement, REQUIREMENTS_INFO.get(requirement, "No info available."))

# ==== Placeholder action for Generate Report ====
def generate_report():
    messagebox.showinfo("Generate Report", "Report generation will be implemented later.")

# ==== Create application ====
def create_app():
    root = tk.Tk()
    root.title("Breast Cancer Risk Assessment")
    root.geometry("1200x750")
    root.configure(bg="#f4f6f8")  # Light gray background

    # ==== Title ====
    title_frame = tk.Frame(root, bg="#007BFF", pady=10)
    title_frame.pack(fill="x")
    title_label = tk.Label(
        title_frame,
        text="Breast Cancer Risk Assessment",
        font=("Arial", 24, "bold"),
        fg="white",
        bg="#007BFF"
    )
    title_label.pack()

    # ==== Top section (Risk Calculator, Data Source, Decision Support) ====
    top_frame = tk.Frame(root, bg="#f4f6f8", pady=15)
    top_frame.pack(fill="x", padx=20)

    # Panels evenly spaced
    for frame_name, buttons in [
        ("Risk Calculator", ["BCRA", "Tyrer-Cuzick", "BOADICEA"]),
        ("Data Source", ["Connect to DB", "Load Excel", "Load CSV"]),
        ("Decision Support", ["Model Comparison", "Report", "Guidelines"])
    ]:
        lf = tk.LabelFrame(
            top_frame,
            text=frame_name,
            font=("Arial", 14, "bold"),
            bg="white",
            fg="black",
            padx=10,
            pady=10,
            labelanchor="n",
            bd=2
        )
        lf.pack(side="left", expand=True, fill="both", padx=5)

        for btn in buttons:
            color = "#007BFF" if "BCRA" in btn else "white"
            fg_color = "white" if "BCRA" in btn else "black"
            tk.Button(
                lf,
                text=btn,
                bg=color,
                fg=fg_color,
                relief="solid",
                font=("Arial", 11, "bold"),
                width=20,
                height=2
            ).pack(pady=5)

    # ==== Bottom section ====
    bottom_frame = tk.Frame(root, bg="#f4f6f8", pady=15)
    bottom_frame.pack(fill="both", expand=True, padx=20)

    # Requirements
    req_frame = tk.LabelFrame(
        bottom_frame,
        text="Requirements",
        font=("Arial", 14, "bold"),
        bg="white",
        padx=10,
        pady=10,
        labelanchor="n",
        bd=2
    )
    req_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    for req in REQUIREMENTS_INFO.keys():
        link = tk.Label(
            req_frame,
            text=req,
            fg="#007BFF",
            cursor="hand2",
            bg="white",
            font=("Arial", 12, "underline")
        )
        link.pack(anchor="w", pady=2)
        link.bind("<Button-1>", lambda e, r=req: show_info(r))

    # 5-Year Risk placeholder
    risk_frame = tk.LabelFrame(
        bottom_frame,
        text="5-Year Risk",
        font=("Arial", 14, "bold"),
        bg="white",
        padx=10,
        pady=10,
        labelanchor="n",
        bd=2
    )
    risk_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    tk.Label(
        risk_frame,
        text="(Risk chart will be displayed here for a selected patient)",
        bg="white",
        font=("Arial", 11),
        wraplength=250,
        justify="center"
    ).pack(expand=True)

    # Generate Report button at bottom center
    action_frame = tk.Frame(root, bg="#f4f6f8", pady=20)
    action_frame.pack(fill="x")

    tk.Button(
        action_frame,
        text="Generate Report",
        bg="#007BFF",
        fg="white",
        font=("Arial", 14, "bold"),
        width=25,
        height=2,
        command=generate_report
    ).pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    create_app()
