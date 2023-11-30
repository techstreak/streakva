# text_utils.py
import tkinter as tk
def update_text(output_text, text):
    output_text.insert(tk.END, f"{text}\n")
    output_text.yview(tk.END)
