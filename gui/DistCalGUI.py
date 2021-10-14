import tkinter as tk
from tkinter import ttk


class GUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.geometry("1500x800")

        self.bind("<Control-q>", self.close_app)

    def close_app(self, event):
        self.quit()
