import tkinter as tk
from tkinter import ttk


class DiffPreparer(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)

        self.value_reg_coarse = tk.StringVar()
        self.value_reg_fine = tk.StringVar()

        self.init_frame()

    def init_frame(self):
        coarse_label = tk.Label(self, text="Coarse regsitration")
        coarse_label.grid(row=0, column=0, sticky='w')
        fine_label = tk.Label(self, text="Fine regsitration")
        fine_label.grid(row=0, column=1, sticky='w')
        entry_coarse = ttk.Entry(self, textvariable=self.value_reg_coarse)
        entry_fine = ttk.Entry(self, textvariable=self.value_reg_fine)
        entry_coarse.grid(row=1, column=0, sticky="w")
        entry_fine.grid(row=1, column=1, sticky="w")
