import tkinter as tk
from tkinter import ttk

import numpy as np


class PCDPrepare(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent

        self['text'] = "Point cloud control"

        self.slider_upper = None
        self.current_value_upper = tk.IntVar()
        self.label_upper = None

        self.slider_lower = None
        self.current_value_lower = tk.IntVar()
        self.label_lower = None

        self.invert_for_irm = None
        self.is_irm = tk.BooleanVar()

        self.value_reg_coarse = tk.StringVar()
        self.value_reg_fine = tk.StringVar()
        self.transformation = np.identity(4)
        self.trans_label = None

        self.init_frame()

    def init_frame(self):
        self.slider_upper = ttk.Scale(self,
                                      from_=0,
                                      to=self.parent.dicom_viewer_frame.upper,
                                      orient='horizontal',
                                      command=self.slider_changed_upper,
                                      variable=self.current_value_upper)
        self.slider_upper.grid(row=0, column=1, sticky='ns')
        self.label_upper = tk.Label(self, text="Upper bound: " + str(self.get_current_upper().get()))
        self.label_upper.grid(column=1, row=1, sticky='nw')

        self.slider_lower = ttk.Scale(self,
                                      from_=0,
                                      to=self.parent.dicom_viewer_frame.lower,
                                      orient='horizontal',
                                      command=self.slider_changed_lower,
                                      variable=self.current_value_lower)
        self.slider_lower.grid(row=0, column=0, sticky='ns')
        self.label_lower = tk.Label(self, text="Lower bound: " + str(self.get_current_lower().get()))
        self.label_lower.grid(column=0, row=1, sticky='nw')

        self.invert_for_irm = ttk.Checkbutton(self, text="Invert signal", onvalue=1, offvalue=0, var=self.is_irm)
        self.invert_for_irm.grid(row=4, column=0, sticky='nw')

        virtual_grid_button = ttk.Button(self, text='Place virtual grid', command=self.parent.place_virtual_grid)
        virtual_grid_button.grid(row=5, column=0, columnspan=3, sticky='new')

        coarse_label = tk.Label(self, text="Coarse regsitration")
        coarse_label.grid(row=6, column=0, sticky='w')
        fine_label = tk.Label(self, text="Fine regsitration")
        fine_label.grid(row=6, column=1, sticky='w')
        entry_coarse = ttk.Entry(self, textvariable=self.value_reg_coarse)
        entry_fine = ttk.Entry(self, textvariable=self.value_reg_fine)
        entry_coarse.grid(row=7, column=0, sticky="w")
        entry_fine.grid(row=7, column=1, sticky="w")

        registration_button = ttk.Button(self, text="Launch coregistration",
                                         command=self.parent.launch_registration)
        registration_button.grid(row=8, column=0, columnspan=3, sticky="new")

        self.trans_label = tk.Label(self, text="Transformation: \n" + self.get_transformation_string())
        self.trans_label.grid(row=9, column=0, sticky='ew')

    def get_current_upper(self):
        return self.current_value_upper

    def get_current_lower(self):
        return self.current_value_lower

    def get_transformation_string(self):
        return str(self.transformation)

    def set_transformation(self, t):
        self.transformation = t
        np.set_printoptions(suppress=False, precision=2)
        self.trans_label.config(text=self.transformation)
        return 0

    def slider_changed_upper(self, event):
        self.label_upper.configure(text="Upper bound: " + str(self.get_current_upper().get()))
        self.parent.dicom_viewer_frame.upper = int(self.get_current_upper().get())
        self.parent.dicom_viewer_frame.change_range()

    def slider_changed_lower(self, event):
        self.label_lower.configure(text="Lower bound: " + str(self.get_current_lower().get()))
        self.parent.dicom_viewer_frame.lower = int(self.get_current_lower().get())
        self.parent.dicom_viewer_frame.change_range()

    def update_scales(self):
        self.slider_upper.config(to=self.parent.imager_binary.max_value)
        self.slider_lower.config(to=self.parent.imager_binary.max_value)
