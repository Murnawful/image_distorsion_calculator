import tkinter as tk
from tkinter import ttk
import file_manager


class GUI(tk.Tk):

    def __init__(self):
        super().__init__()

        self.filenames = None

        self.geometry("1500x800")

        file_manager.FileManager()

        self.bind("<Control-q>", self.close_app)

    def close_app(self, event):
        self.quit()
