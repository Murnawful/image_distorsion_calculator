import tkinter as tk
from tkinter import ttk
from gui import file_manager
import irm_dist_calculator as idc
from tkinter.messagebox import showerror
import pydicom as pdcm


class GUI(tk.Tk):
    filenames = None
    working_directory = None
    dicom_datasets = []

    def __init__(self):
        super().__init__()

        # get the screen dimension
        window_width = self.winfo_screenwidth()
        window_height = self.winfo_screenheight()

        # set the position of the window to the center of the screen
        self.geometry(f'{window_width}x{window_height}')

        self.file_manager_frame = file_manager.FileManager(self)
        self.file_manager_frame.grid(row=0,
                                     column=0,
                                     sticky='w')

        load_dicom_button = ttk.Button(self,
                                       text='Load DICOM files',
                                       command=self.load_dicom_files)
        load_dicom_button.grid(row=1,
                               column=0,
                               sticky='ew')

        self.bind("<Control-q>", self.close_app)

    def close_app(self, event):
        self.quit()

    def load_dicom_files(self):
        try:
            self.filenames = self.file_manager_frame.filenames
            self.working_directory = self.file_manager_frame.files_directory + "/"
            print(self.working_directory)
        except self.file_manager_frame.filenames == []:
            showerror(title='Error',
                      message='No files present in the file manager')
