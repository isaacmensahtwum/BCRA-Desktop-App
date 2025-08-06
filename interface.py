import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk  # For ribbon logo image

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

PINK = "#E75480"  # Breast cancer pink
BLUE_LINK = "#007BFF"  # Blue for clickable requirement links

# ==== Show explanation popups ====
def show_info(requirement):
    messagebox.showinfo(requirement, REQUIREMENTS_INFO.get(requirement, "No info available."))

# ==== Placeholder actions ====
def generate_report():
    messagebox.showinfo("Generate Report", "Report generation will be implemented later.")

def login_action():
    messagebox.showinfo("Login", "Login functionality will be implemented later.")

# ==== Rounded clickable button ====
def create_rounded_button(parent, text, command=None, bg=PINK, fg="white", width=18, height=2):
    btn = tk.Button(
        parent,
        text=text,
        bg=bg,
        fg=fg,
        activebackground=bg,
        activeforeground=fg,
        relief="flat",
        font=("Arial", 11, "bold"),
        command=command,
        bd=0,
        highlightthickness=0,
        cursor="hand2"
    )
    btn.pack(pady=5, ipadx=5, ipady=2)
    return btn

# ==== Modern frame with pink header ====
def create_modern_frame(parent, title, bg_color=PINK, text_color="white"):
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

    # ==== Title bar ====
    title_bar = tk.Frame(root, bg=PINK, pady=10)
    title_bar.pack(fill="x")

    # Load ribbon logo
    try:
        logo_img = Image.open("breast_cancer_logo.png")
        logo_img = logo_img.resize((40, 40), Image.LANCZOS)
        ribbon_logo = ImageTk.PhotoImage(logo_img)
        logo_label = tk.Label(title_bar, image=ribbon_logo, bg=PINK)
        logo_label.image = ribbon_logo
        logo_label.pack(side="left", padx=(20, 5))
    except FileNotFoundError:
        print("Logo image 'breast_cancer_logo.png' not found.")

    # Title label centered
    title_label = tk.Label(
        title_bar,
        text="Breast Cancer Risk Assessment",
        font=("Arial", 24, "bold"),
        fg="white",
        bg=PINK
    )
    title_label.pack(side="left", expand=True)

    # Login button
    tk.Button(
        title_bar,
        text="Login",
        command=login_action,
        bg="white",
        fg=PINK,
        font=("Arial", 10, "bold"),
        relief="flat",
        padx=10,
        pady=2,
        cursor="hand2"
    ).pack(side="right", padx=20)

    # ==== Top section ====
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
                create_rounded_button(lf_content, btn, bg=PINK, fg="white")
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
            fg=BLUE_LINK,  # Blue clickable text
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
        bg=PINK,
        fg="white",
        width=25,
        height=2
    )

    root.mainloop()

if __name__ == "__main__":
    create_app()
