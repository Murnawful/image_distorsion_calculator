import tkinter as tk
from tkinter import ttk


class ControlAnalysisChoice(ttk.LabelFrame):
    def __init__(self, container):
        super().__init__(container)

        self.parent = container

        self.selected_value = tk.IntVar()

        self['text'] = "Analysis type"

        node_button = ttk.Radiobutton(self, text="Node analysis", value=1, variable=self.selected_value,
                                      command=self.change_frame)
        node_button.grid(row=0, column=0, padx=5, pady=5)
        diff_button = ttk.Radiobutton(self, text="Difference analysis", value=0, variable=self.selected_value,
                                      command=self.change_frame)
        diff_button.grid(row=0, column=1, padx=5, pady=5)

    def change_frame(self):
        frame_control = self.parent.frame_control[self.selected_value.get()]
        frame_control.reset()
        frame_control.tkraise()
