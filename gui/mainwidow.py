import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror

from gui import file_manager
from gui import dicom_viewer_frame as dvf
from gui import dicom_imager

import irm_dist_calculator as idc

import pydicom as pdcm


class GUI(tk.Tk):

    def __init__(self):
        super().__init__()

        self.filenames = None
        self.working_directory = None
        self.dicom_datasets = []
        self.file_manager_frame = None
        self.dicom_viewer_frame = None
        self.imager = None

        self.init_gui()

    def init_gui(self):
        window_width = self.winfo_screenwidth()
        window_height = self.winfo_screenheight()

        self.geometry(f'{window_width}x{window_height}')

        self.file_manager_frame = file_manager.FileManager(self)
        self.file_manager_frame.grid(row=0, column=0, sticky='nw')

        load_dicom_button = ttk.Button(self, text='Load DICOM files', command=self.load_dicom_files)
        load_dicom_button.grid(row=1, column=0, sticky='new')

        self.dicom_viewer_frame = dvf.DicomViewerFrame(self)
        self.dicom_viewer_frame.grid(row=0, rowspan=5, column=1, sticky='nsew')
        self.dicom_viewer_frame.init_ui()

        self.bind("<Control-q>", self.close_app)

    def close_app(self, event):
        self.quit()

    def load_dicom_files(self):
        try:
            self.filenames = self.file_manager_frame.filenames
            self.working_directory = self.file_manager_frame.files_directory + "/"

            self.dicom_datasets.clear()
            for file in self.filenames:
                self.dicom_datasets.append(pdcm.read_file(file.name))

            self.sort_datasets()

            self.imager = dicom_imager.DicomImager(self.dicom_datasets)

            self.dicom_viewer_frame.set_imager(self.imager)
            self.dicom_viewer_frame.show_image(self.imager.get_current_image())
        except self.file_manager_frame.filenames == []:
            showerror(title='Error', message='No files present in the file manager')

    def sort_datasets(self):
        try:
            self.dicom_datasets.sort(key=lambda x: x.InstanceNumber)
        except AttributeError:
            try:
                self.dicom_datasets.sort(key=lambda x: x.SOPInstanceUID)
            except AttributeError:
                pass
