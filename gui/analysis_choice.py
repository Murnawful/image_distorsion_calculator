import tkinter as tk
from tkinter import ttk


class ControlAnalysisChoice(ttk.LabelFrame):
    def __init__(self, container):
        super().__init__(container)

        self.parent = container

        self.selected_value = tk.IntVar(0)

        self['text'] = "Analysis type"

        node_button = ttk.Radiobutton(self, text="Node analysis", value=1, variable=self.selected_value,
                                      command=self.change_frame)
        node_button.grid(row=0, column=0, padx=5, pady=5)
        diff_button = ttk.Radiobutton(self, text="Difference analysis", value=0, variable=self.selected_value,
                                      command=self.change_frame)
        diff_button.grid(row=0, column=1, padx=5, pady=5)

    def change_frame(self):
        frame_viewer = self.parent.frame_viewer[self.selected_value.get()]
        other_frame_viewer = self.parent.frame_viewer[int(not self.selected_value.get())]
        frame_viewer.grid(row=0, column=2, rowspan=6, sticky='nsew')
        other_frame_viewer.grid_forget()

        frame_control = self.parent.frame_control[self.selected_value.get()]
        other_frame_control = self.parent.frame_control[int(not self.selected_value.get())]
        frame_control.grid(row=3, column=0, columnspan=2, sticky='ew', padx=35)
        other_frame_control.grid_forget()
