from tkinter import Tk, Label, Text, Frame, Scrollbar, Canvas, END, BOTH, RIGHT, Y, LEFT
import subprocess, sys, os

# ─── THEME ───────────────────────────────────────────────────────────────────
SKY   = "#01579b"
NAVY  = "#e1f5fe"
WHITE = "#F0F8FF"
LIGHT = "#D6EAF8"
BTN   = "#1565C0"

w = Tk()
w.title("Python → C Converter")
w.state("zoomed")          # fullscreen on Windows/Linux
w.configure(bg=NAVY)
w.resizable(True, True)

# ─── TITLE ───────────────────────────────────────────────────────────────────
Label(w, text="Python  →  C  Converter",
      bg=NAVY, fg=SKY, font=("Courier", 22, "bold")).grid(
      row=0, column=0, columnspan=3, pady=(18, 4))

Label(w, text="Paste Python code below, click the arrow, get C code.",
      bg=NAVY, fg=SKY, font=("Courier", 12, "bold")).grid(
      row=1, column=0, columnspan=3, pady=(0, 12))

# ─── LABELS ──────────────────────────────────────────────────────────────────
Label(w, text="Python Code", bg=NAVY, fg=SKY,
      font=("Courier", 13, "bold")).grid(row=2, column=0, padx=24, sticky="w")

Label(w, text="Generated C Code", bg=NAVY, fg=SKY,
      font=("Courier", 13, "bold")).grid(row=2, column=2, padx=24, sticky="w")

# ─── INPUT BOX ───────────────────────────────────────────────────────────────
in_frame = Frame(w, bg=SKY, bd=2)
in_frame.grid(row=3, column=0, padx=(24, 6), pady=6, sticky="nsew")

in_scroll = Scrollbar(in_frame)
in_scroll.pack(side=RIGHT, fill=Y)

input_box = Text(in_frame, width=40, height=24,
                 bg=WHITE, fg="#0d1b2a", insertbackground=SKY,
                 font=("Courier", 12), yscrollcommand=in_scroll.set,
                 relief="flat", bd=6)
input_box.pack(side=LEFT, fill=BOTH, expand=True)
in_scroll.config(command=input_box.yview)

# ─── TRIANGLE ARROW BUTTON ───────────────────────────────────────────────────
btn_frame = Frame(w, bg=NAVY)
btn_frame.grid(row=3, column=1, padx=8)

def draw_triangle_btn(parent, cmd):
    c = Canvas(parent, width=80, height=80, bg=NAVY, highlightthickness=0)

    # Triangle pointing right (like a play/forward arrow)
    pts = [10, 10, 10, 70, 70, 40]
    tri = c.create_polygon(pts, fill=BTN, outline=SKY, width=2)

    c.bind("<Button-1>", lambda e: cmd())
    c.bind("<Enter>",    lambda e: c.itemconfig(tri, fill="#1976D2"))
    c.bind("<Leave>",    lambda e: c.itemconfig(tri, fill=BTN))
    return c

def convert():
    py_code = input_box.get("1.0", END).strip()
    if not py_code:
        output_box.delete("1.0", END)
        output_box.insert(END, "⚠  Paste some Python code first.")
        return

    lines = py_code.splitlines()
    n     = len(lines)
    stdin = f"{n}\n" + "\n".join(lines) + "\n"

    script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "project.py")

    try:
        result = subprocess.run(
            [sys.executable, script],
            input=stdin, capture_output=True, text=True, timeout=10
        )
        out = result.stdout.strip()
        if "Generated C Code:" in out:
            out = out[out.index("Generated C Code:") + len("Generated C Code:"):].strip()
    except FileNotFoundError:
        out = "  project.py not found.\n    Keep cdgui.py and project.py in the same folder."
    except Exception as ex:
        out = f"  Error: {ex}"

    output_box.delete("1.0", END)
    output_box.insert(END, out)

tri_btn = draw_triangle_btn(btn_frame, convert)
tri_btn.pack(pady=20)

# ─── OUTPUT BOX ──────────────────────────────────────────────────────────────
out_frame = Frame(w, bg=SKY, bd=2)
out_frame.grid(row=3, column=2, padx=(6, 24), pady=6, sticky="nsew")

out_scroll = Scrollbar(out_frame)
out_scroll.pack(side=RIGHT, fill=Y)

output_box = Text(out_frame, width=40, height=24,
                  bg=NAVY, fg=SKY, insertbackground=SKY,
                  font=("Courier", 12), yscrollcommand=out_scroll.set,
                  relief="flat", bd=6)
output_box.pack(side=LEFT, fill=BOTH, expand=True)
out_scroll.config(command=output_box.yview)

# ─── GRID WEIGHTS ────────────────────────────────────────────────────────────
w.grid_columnconfigure(0, weight=1)
w.grid_columnconfigure(1, weight=0)
w.grid_columnconfigure(2, weight=1)
w.grid_rowconfigure(3, weight=1)

w.mainloop()
