import tkinter as tk
from tkinter import ttk

from tkinter.messagebox import showinfo
from tkinter.messagebox import askyesno

import numpy as np


class ProgressWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__()

        self.analyser = parent.analyzer
        self.parent = parent

        self.progress = None
        self.progress_label = None

        self.ind_copy = 0

        self.init_window()

    def init_window(self):
        self.geometry("240x100")
        self.progress_label = ttk.Label(self, text="Analysis running...")
        self.progress_label.pack(pady=10)
        self.progress = ttk.Progressbar(self, mode="determinate", length=200)
        self.progress.pack()

        self.pack_slaves()

    def change_progress(self):
        ind = self.analyser.get_index() + 1
        tot = self.analyser.get_vertex_number()
        t = "Treating node number " + str(ind) + " out of " + str(tot)
        self.progress_label['text'] = t
        if ind > self.ind_copy:
            self.progress['value'] += 100 / tot
        self.ind_copy = np.copy(ind)
        self.update()

    def notify_end(self):
        showinfo(title="Done", message="Node analysis")
        self.analyser.compute_results()
        self.destroy()
