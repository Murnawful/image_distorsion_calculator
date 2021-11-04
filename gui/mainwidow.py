import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror
from tkinter.messagebox import askyesno

from gui import file_manager
from gui import dicom_binary_viewer_frame
from gui import dicom_full_viewer_frame
from gui import dicom_binary_imager
from gui import dicom_full_imager
from gui import cloud_point_preparer
from gui import progress_window
from gui import analysis_choice

from irm_dist_calculator import imageGrid as ig
from irm_dist_calculator import referenceGrid as rg
from irm_dist_calculator import node_analyzer as a

import pydicom as pdcm

import threading
import os

import open3d as o3d


def clear_data():
    """ Clearing data saved in the data/ folder when pressing clear button """
    folder = "data/"
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        os.unlink(file_path)


class GUI(tk.Tk):

    def __init__(self):
        """ Constructor """
        super().__init__()

        self.filenames = None
        self.working_directory = None
        self.dicom_datasets = []
        self.file_manager_frame = None
        self.choice_control_frame = None

        self.dicom_binary_viewer_frame = None
        self.dicom_full_viewer_frame = None
        self.imager_binary = None
        self.imager_full = None
        self.pcd_preparer = None

        self.frame_control = {}
        self.frame_viewer = {}

        self.im_grid = None
        self.ref_grid = None
        self.ref_frame = None

        self.progress_window = None

        self.t1 = None
        self.t2 = None
        self.popup_progress = None
        self.progress_label = None
        self.progress = None

        self.analyzer = None

        self.init_gui()

    def init_gui(self):
        """ Initialisation of main window, where all the different widgets are prepared """
        window_width = self.winfo_screenwidth()
        window_height = self.winfo_screenheight()

        # self.geometry(f'{window_width}x{window_height}')
        self.geometry('1600x900')
        self.title("DistCal")

        self.file_manager_frame = file_manager.FileManager(self)
        self.file_manager_frame.grid(row=0, column=0, columnspan=2, sticky='nw')

        self.choice_control_frame = analysis_choice.ControlAnalysisChoice(self)
        self.choice_control_frame.grid(row=1, column=0, columnspan=2, sticky='ew')

        load_dicom_button = ttk.Button(self, text='Load DICOM files', command=self.load_dicom_files)
        load_dicom_button.grid(row=2, column=0, columnspan=2, sticky='new')

        self.dicom_binary_viewer_frame = dicom_binary_viewer_frame.DicomBinaryViewerFrame(self)
        self.dicom_binary_viewer_frame.init_viewer_frame()
        self.dicom_full_viewer_frame = dicom_full_viewer_frame.DicomFullViewerFrame(self)
        self.dicom_full_viewer_frame.init_viewer_frame()

        self.frame_viewer[0] = self.dicom_full_viewer_frame
        self.frame_viewer[1] = self.dicom_binary_viewer_frame

        self.pcd_preparer = cloud_point_preparer.PCDPrepare(self)

        test = tk.Frame(self)
        tk.Label(test, text="COUCOU").grid(row=0, column=0, sticky='nsew')
        self.frame_control[0] = test
        self.frame_control[1] = self.pcd_preparer

        analysis_button = ttk.Button(self, text='Launch analysis', command=self.launch_analysis)
        analysis_button.grid(row=4, column=0, sticky='ew')

        save_analysis_button = ttk.Button(self, text='Save results', command=self.save_results)
        save_analysis_button.grid(row=4, column=1, sticky='ew')

        clear_button = ttk.Button(self, text="Clear data", command=clear_data)
        clear_button.grid(row=5, column=0, sticky='ew')

        choose_reference_button = ttk.Button(self, text="Choose CBCT reference", command=self.retrieve_reference)
        choose_reference_button.grid(row=5, column=1, sticky='ew')

        self.bind("<Control-q>", self.close_app)

    def retrieve_reference(self):
        pass

    def close_app(self, e=tk.Event()):
        """ Protocol occurring when quitting the app, either by close the window with the mouse or by hitting Ctrl-q """
        answer = askyesno(title="Quit", message="Are you sure you want to quit ?")
        if answer:
            self.destroy()

    def load_dicom_files(self):
        """ Reads the selected DICOM files datasets and gets their pixel array in order to prepare the view for the
        DICOM viewer frame """
        try:
            self.filenames = self.file_manager_frame.filenames
            self.working_directory = self.file_manager_frame.files_directory + "/"

            self.dicom_datasets.clear()
            for file in self.filenames:
                self.dicom_datasets.append(pdcm.read_file(file.name))

            self.sort_datasets()

            self.imager_binary = dicom_binary_imager.DicomBinaryImager(self.dicom_datasets)
            self.imager_full = dicom_full_imager.DicomFullImager(self.dicom_datasets)

            self.dicom_binary_viewer_frame.set_imager(self.imager_binary)
            self.dicom_full_viewer_frame.set_imager(self.imager_full)
            if self.choice_control_frame.selected_value.get() == 1:
                im_axial, index_axial = self.imager_binary.get_current_axial_image(self.dicom_binary_viewer_frame.upper,
                                                                                   self.dicom_binary_viewer_frame.lower)
                im_sagittal, index_sagittal = self.imager_binary\
                    .get_current_coronal_image(self.dicom_binary_viewer_frame.upper,
                                               self.dicom_binary_viewer_frame.lower)
                self.dicom_binary_viewer_frame.show_image(im_axial, index_axial, im_sagittal, index_sagittal)
                self.pcd_preparer.update_scales()
            else:
                im_axial, index_axial = self.imager_full.get_current_axial_image()
                im_sagittal, index_sagittal = self.imager_full.get_current_coronal_image()
                self.dicom_full_viewer_frame.show_image(im_axial, index_axial, im_sagittal, index_sagittal)

        except TypeError:
            showerror(title='Error', message='No files present in the file manager')

    def sort_datasets(self):
        """ Sorting the datasets in order to always have the right file coming at the right moment when scrolling
        views """
        try:
            self.dicom_datasets.sort(key=lambda x: x.InstanceNumber)
        except AttributeError:
            try:
                self.dicom_datasets.sort(key=lambda x: x.SOPInstanceUID)
            except AttributeError:
                pass

    def place_virtual_grid(self):
        """ Retrieves the coordinates of the user-defined ROI and center of virtual grid along with the upper and
        lower bounds on DICOM pixel array values """
        try:
            roi = self.dicom_binary_viewer_frame.roi
            arr = self.imager_binary._values
            upper = self.pcd_preparer.current_value_upper.get()
            lower = self.pcd_preparer.current_value_lower.get()
            irm = self.pcd_preparer.is_irm.get()
            center_ = self.dicom_binary_viewer_frame.get_virtual_grid_center()
            self.im_grid = ig.ImageGrid(values=arr, spacing=self.imager_binary.spacings, image_roi=roi,
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
            self.pcd_preparer.set_transformation(self.ref_grid.register(self.im_grid.pcd,
                                                                        float(self.pcd_preparer.value_reg_coarse.get()),
                                                                        float(self.pcd_preparer.value_reg_fine.get())))
            self.popup_progress.destroy()
            o3d.visualization.draw_geometries([self.ref_frame, self.im_grid.pcd, self.ref_grid.pcd])
            answer = askyesno(title="Saving", message="Save results of registration ?")
            if answer:
                self.ref_grid.save_point_cloud("data/", "registeredGrid")
                self.im_grid.save_point_cloud("data/", "realGrid")
        except TypeError as e:
            showerror(title="Error", message="No parameters for registration were given !")
        except ValueError as v:
            showerror(title="Error", message="Wrong values for coregistration !")
        return 0

    def display_progress(self):
        self.popup_progress = tk.Toplevel()
        self.popup_progress.geometry("240x100")
        tk.Label(self.popup_progress, text="Registering...").grid(row=0, column=0, pady=10)
        progress = ttk.Progressbar(self.popup_progress, mode="indeterminate", length=200)
        progress.grid(row=1, column=0, padx=20)
        self.popup_progress.pack_slaves()
        progress.start()

    def launch_registration(self):
        self.t1 = threading.Thread(target=self.registration_thread)
        self.t2 = threading.Thread(target=self.display_progress)
        self.t2.start()
        self.t1.start()

    def launch_analysis(self):
        self.analyzer = a.NodeAnalyzer(dir_tofile="data/",
                                       file_source="realGrid.ply",
                                       file_vertex="registeredGrid_vertex.ply",
                                       file_registered="registeredGrid_full.ply",
                                       scope=3e-3,
                                       parent=self)
        self.popup_progress = progress_window.ProgressWindow(self)

        self.t1 = threading.Thread(target=self.analyzer.launch_analysis)
        self.t2 = threading.Thread(target=self.popup_progress.change_progress)
        self.t2.start()
        self.t1.start()

    def save_results(self):
        self.analyzer.save_results("results")
