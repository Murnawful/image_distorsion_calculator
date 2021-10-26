import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror
from tkinter.messagebox import askyesno

from gui import file_manager
from gui import dicom_viewer_frame
from gui import dicom_imager
from gui import cloud_point_preparer

from irm_dist_calculator import imageGrid as ig
from irm_dist_calculator import referenceGrid as rg
from irm_dist_calculator import analyzer as a

import pydicom as pdcm

import threading

import open3d as o3d


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

        self.im_grid = None
        self.ref_grid = None
        self.ref_frame = None

        self.progress_window = None

        self.t1 = None
        self.t2 = None
        self.popup_progress = None

        self.vertex_number = 0
        self.analyzer = None

        self.init_gui()

    def init_gui(self):
        window_width = self.winfo_screenwidth()
        window_height = self.winfo_screenheight()

        # self.geometry(f'{window_width}x{window_height}')
        self.geometry('1600x900')
        self.title("DistCal")

        self.file_manager_frame = file_manager.FileManager(self)
        self.file_manager_frame.grid(row=0, column=0, columnspan=2, sticky='nw')

        load_dicom_button = ttk.Button(self, text='Load DICOM files', command=self.load_dicom_files)
        load_dicom_button.grid(row=1, column=0, columnspan=2, sticky='new')

        self.dicom_viewer_frame = dicom_viewer_frame.DicomViewerFrame(self)
        self.dicom_viewer_frame.grid(row=0, column=2, rowspan=3, sticky='nsew')
        self.dicom_viewer_frame.init_viewer_frame()

        self.pcd_preparer = cloud_point_preparer.PCDPrepare(self)
        self.pcd_preparer.grid(row=2, column=0, columnspan=2, sticky='nsew')

        analysis_button = ttk.Button(self, text='Launch analysis', command=self.launch_analysis)

        self.t1 = threading.Thread(target=self.registration_thread)
        self.t2 = threading.Thread(target=self.display_progress)

        self.bind("<Control-q>", self.close_app)

    def close_app(self, event):
        answer = askyesno(title="Quit", message="Are you sure you want to quit ?")
        if answer:
            self.destroy()

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
            im_sagittal, index_sagittal = self.imager.get_current_coronal_image(self.dicom_viewer_frame.upper,
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
        try:
            roi = self.dicom_viewer_frame.roi
            arr = self.imager.values
            upper = self.pcd_preparer.current_value_upper.get()
            lower = self.pcd_preparer.current_value_lower.get()
            irm = self.pcd_preparer.is_irm.get()
            center_ = self.dicom_viewer_frame.get_virtual_grid_center()
            self.im_grid = ig.ImageGrid(values=arr, spacing=self.imager.spacings, image_roi=roi,
                                        range_values=(lower, upper),
                                        is_mri=irm)
            self.ref_grid = rg.ReferenceGrid(center=center_)
            self.ref_grid.build()
            self.ref_grid.convert()
            self.im_grid.convert()
            self.ref_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.05, origin=[0, 0, 0])
            self.ref_grid.pcd.paint_uniform_color([0, 0, 1])
            o3d.visualization.draw_geometries([self.ref_frame, self.im_grid.pcd, self.ref_grid.pcd])
        except TypeError:
            showerror(title="Error", message="No ROI is defined !")

    def registration_thread(self):
        try:
            self.ref_grid.register(self.im_grid.pcd, float(self.pcd_preparer.value_reg_coarse.get()),
                                   float(self.pcd_preparer.value_reg_fine.get()))
            self.popup_progress.destroy()
            o3d.visualization.draw_geometries([self.ref_frame, self.im_grid.pcd, self.ref_grid.pcd])
            answer = askyesno(title="Saving", message="Save results of registration ?")
            if answer:
                self.ref_grid.save_point_cloud("data/", "registeredGrid")
                self.im_grid.save_point_cloud("data/", "realGrid")
        except TypeError:
            showerror(title="Error", message="No parameters for registration were given !")
        except ValueError:
            showerror(title="Error", message="Wrong values for coregistration !")

    def display_progress(self):
        self.popup_progress = tk.Toplevel()
        self.popup_progress.geometry("240x100")
        tk.Label(self.popup_progress, text="Registering...").grid(row=0, column=0, pady=10)
        progress = ttk.Progressbar(self.popup_progress, mode="indeterminate", length=200)
        progress.grid(row=1, column=0, padx=20)
        self.popup_progress.pack_slaves()
        progress.start()

    def launch_registration(self):
        self.t2.start()
        self.t1.start()

    def analysis_thread(self):
        self.analyzer.launch_analysis()

    def launch_analysis(self):
        if not self.t1.is_alive() or not self.t2.is_alive():
            self.analyzer = a.Analyzer(dir_tofile="../data/",
                                       file_source="realGrid.ply",
                                       file_vertex="registeredGrid_vertex.ply",
                                       file_registered="registeredGrid_full.ply")
            self.vertex_number = self.analyzer.points_vertex.shape[0]
            self.progress['mode'] = 'determinate'
            self.t2 = threading.Thread(target=self.set_progress)
            self.t1 = threading.Thread(target=self.analysis_thread)
            self.t2.start()
            self.t1.start()
