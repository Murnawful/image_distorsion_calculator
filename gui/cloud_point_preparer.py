import tkinter as tk
from tkinter import ttk


class PCDPrepare(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent

        self.slider_upper = None
        self.current_value_upper = tk.IntVar()
        self.label_upper = None

        self.slider_lower = None
        self.current_value_lower = tk.IntVar()
        self.label_lower = None

        self.invert_for_irm = None

        self.init_frame()

    def init_frame(self):
        self.slider_upper = ttk.Scale(self,
                                      from_=0,
                                      to=self.parent.dicom_viewer_frame.upper,
                                      orient='horizontal',
                                      command=self.slider_changed_upper,
                                      variable=self.current_value_upper)
        self.slider_upper.grid(row=0, column=0, sticky='ns')
        self.label_upper = tk.Label(self, text="Upper bound: " + str(self.get_current_upper().get()))
        self.label_upper.grid(column=0, row=1, sticky='w')

        self.slider_lower = ttk.Scale(self,
                                      from_=0,
                                      to=self.parent.dicom_viewer_frame.lower,
                                      orient='horizontal',
                                      command=self.slider_changed_lower,
                                      variable=self.current_value_lower)
        self.slider_lower.grid(row=0, column=1, sticky='ns')
        self.label_lower = tk.Label(self, text="Lower bound: " + str(self.get_current_lower().get()))
        self.label_lower.grid(column=1, row=1, sticky='w')

    def get_current_upper(self):
        return self.current_value_upper

    def get_current_lower(self):
        return self.current_value_lower

    def slider_changed_upper(self, event):
        self.label_upper.configure(text="Upper bound: " + str(self.get_current_upper().get()))
        self.parent.dicom_viewer_frame.upper = int(self.get_current_upper().get())
        self.parent.dicom_viewer_frame.change_range()

    def slider_changed_lower(self, event):
        self.label_lower.configure(text="Lower bound: " + str(self.get_current_lower().get()))
        self.parent.dicom_viewer_frame.lower = int(self.get_current_lower().get())
        self.parent.dicom_viewer_frame.change_range()

    def update_scales(self):
        self.slider_upper.config(to=self.parent.imager.max_value)
        self.slider_lower.config(to=self.parent.imager.max_value)
