import tkinter as tk
from tkinter import messagebox, Canvas


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


# ==== Placeholder login ====
def login_action():
    messagebox.showinfo("Login", "Login functionality will be implemented later.")


# ==== Rounded button function ====
def create_rounded_button(parent, text, command=None, bg="#007BFF", fg="white", width=18, height=2):
    btn = tk.Button(
        parent,
        text=text,
        bg=bg,
        fg=fg,
        activebackground=bg,
        activeforeground=fg,
        relief="flat",
        font=("Arial", 11, "bold"),
        command=command
    )
    btn.configure(highlightthickness=0, bd=0)
    btn.pack(pady=5)
    return btn


# ==== Modern frame with colored header ====
def create_modern_frame(parent, title, bg_color="#007BFF", text_color="white"):
    frame_container = tk.Frame(parent, bg="white", bd=1, relief="solid")

    # Header
    header = tk.Frame(frame_container, bg=bg_color)
    header.pack(fill="x")
    tk.Label(
        header,
        text=title,
        bg=bg_color,
        fg=text_color,
        font=("Arial", 14, "bold"),
        pady=5
    ).pack()

    # Inner content frame
    content_frame = tk.Frame(frame_container, bg="white", padx=10, pady=10)
    content_frame.pack(fill="both", expand=True)

    return frame_container, content_frame


# ==== Create application ====
def create_app():
    root = tk.Tk()
    root.title("Breast Cancer Risk Assessment")
    root.geometry("1200x750")
    root.configure(bg="#f4f6f8")  # Light gray background

    # ==== Title bar with login ====
    title_bar = tk.Frame(root, bg="#007BFF", pady=10)
    title_bar.pack(fill="x")

    tk.Label(
        title_bar,
        text="Breast Cancer Risk Assessment",
        font=("Arial", 24, "bold"),
        fg="white",
        bg="#007BFF"
    ).pack(side="left", padx=20)

    # Login area
    login_frame = tk.Frame(title_bar, bg="#007BFF")
    login_frame.pack(side="right", padx=20)

    # Circular initials logo
    logo_canvas = Canvas(login_frame, width=30, height=30, bg="#007BFF", highlightthickness=0)
    logo_canvas.create_oval(2, 2, 28, 28, fill="white", outline="")
    logo_canvas.create_text(15, 15, text="IT", font=("Arial", 10, "bold"), fill="#007BFF")
    logo_canvas.pack(side="left", padx=5)

    # Login button
    tk.Button(
        login_frame,
        text="Login",
        command=login_action,
        bg="white",
        fg="#007BFF",
        font=("Arial", 10, "bold"),
        relief="flat",
        padx=10,
        pady=2
    ).pack(side="left")

    # ==== Top section (Risk Calculator, Data Source, Decision Support) ====
    top_frame = tk.Frame(root, bg="#f4f6f8", pady=15)
    top_frame.pack(fill="x", padx=20)

    for frame_name, buttons in [
        ("Risk Calculator", ["BCRA >", "Tyrer-Cuzick", "BOADICEA"]),
        ("Data Source", ["Connect to DB", "Load Excel", "Load CSV"]),
        ("Decision Support", ["Model Comparison", "Report", "Guidelines"])
    ]:
        lf, lf_content = create_modern_frame(top_frame, frame_name)
        lf.pack(side="left", expand=True, fill="both", padx=5)

        for btn in buttons:
            if "BCRA" in btn:
                create_rounded_button(lf_content, btn, bg="#007BFF", fg="white")
            else:
                create_rounded_button(lf_content, btn, bg="white", fg="black")

    # ==== Bottom section ====
    bottom_frame = tk.Frame(root, bg="#f4f6f8", pady=15)
    bottom_frame.pack(fill="both", expand=True, padx=20)

    # Requirements
    req_frame, req_content = create_modern_frame(bottom_frame, "Requirements")
    req_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    for req in REQUIREMENTS_INFO.keys():
        link = tk.Label(
            req_content,
            text=req,
            fg="#007BFF",
            cursor="hand2",
            bg="white",
            font=("Arial", 12, "underline")
        )
        link.pack(anchor="w", pady=2)
        link.bind("<Button-1>", lambda e, r=req: show_info(r))

    # 5-Year Risk placeholder
    risk_frame, risk_content = create_modern_frame(bottom_frame, "5-Year Risk")
    risk_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    tk.Label(
        risk_content,
        text="(Risk chart will be displayed here for a selected patient)",
        bg="white",
        font=("Arial", 11),
        wraplength=250,
        justify="center"
    ).pack(expand=True)

    # Generate Report button at bottom center
    action_frame = tk.Frame(root, bg="#f4f6f8", pady=20)
    action_frame.pack(fill="x")

    create_rounded_button(
        action_frame,
        "Generate Report",
        command=generate_report,
        bg="#007BFF",
        fg="white",
        width=25,
        height=2
    )

    root.mainloop()


if __name__ == "__main__":
    create_app()
