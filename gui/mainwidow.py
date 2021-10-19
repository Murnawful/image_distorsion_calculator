import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror

from gui import file_manager
from gui import dicom_viewer_frame
from gui import dicom_imager
from gui import cloud_point_preparer

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
        self.pcd_preparer = None

        self.init_gui()

    def init_gui(self):
        window_width = self.winfo_screenwidth()
        window_height = self.winfo_screenheight()

        self.geometry(f'{window_width}x{window_height}')
        self.title("DistCal")

        self.file_manager_frame = file_manager.FileManager(self)
        self.file_manager_frame.grid(row=0, column=0, sticky='nw')

        load_dicom_button = ttk.Button(self, text='Load DICOM files', command=self.load_dicom_files)
        load_dicom_button.grid(row=1, column=0, columnspan=2, sticky='new')

        self.dicom_viewer_frame = dicom_viewer_frame.DicomViewerFrame(self)
        self.dicom_viewer_frame.grid(row=0, column=2, rowspan=4, sticky='nsew')
        self.dicom_viewer_frame.init_viewer_frame()

        self.pcd_preparer = cloud_point_preparer.PCDPrepare(self)
        self.pcd_preparer.grid(row=2, column=0, columnspan=2, sticky='nsew')

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
            im_axial, index_axial = self.imager.get_current_axial_image(self.dicom_viewer_frame.upper,
                                                                        self.dicom_viewer_frame.lower)
            im_sagittal, index_sagittal = self.imager.get_current_sagittal_image(self.dicom_viewer_frame.upper,
                                                                                 self.dicom_viewer_frame.lower)
            self.dicom_viewer_frame.show_image(im_axial, index_axial, im_sagittal, index_sagittal)

            self.pcd_preparer.update_scales()
        except TypeError:
            showerror(title='Error', message='No files present in the file manager')

    def sort_datasets(self):
        try:
            self.dicom_datasets.sort(key=lambda x: x.InstanceNumber)
        except AttributeError:
            try:
                self.dicom_datasets.sort(key=lambda x: x.SOPInstanceUID)
            except AttributeError:
                pass

    def place_virtual_grid(self):
        lower_slice = self.pcd_preparer.lower_slice.get()
        upper_slice = self.pcd_preparer.upper_slice.get()
