import tkinter as tk
from tkinter import ttk
from gui import file_manager


class GUI(tk.Tk):

    def __init__(self):
        super().__init__()

        self.filenames = None

        self.geometry("1500x800")

        file_manager_frame = file_manager.FileManager(self)
        file_manager_frame.grid(row=0,
                                column=0,
                                sticky='w')

        self.bind("<Control-q>", self.close_app)

    def close_app(self, event):
        self.quit()
