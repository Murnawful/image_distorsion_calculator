import matplotlib.pyplot as plt

import tkinter as tk
import PIL.Image
import PIL.ImageTk

from gui import dicom_viewer_frame
from gui import dicom_full_imager
from gui.statusbar import *

import os
import pydicom as pdcm


class DicomFullViewerFrame(dicom_viewer_frame.DicomViewerFrame):
    def __init__(self, root):

        super().__init__(root)

    def show_image(self, array_axial, index_axial, array_sagittal, index_sagittal, *args, **kwargs):

        if array_axial is None:
            return
        if array_sagittal is None:
            return

        # Convert numpy array into a PhotoImage and add it to canvas
        self.image_ax = PIL.Image.fromarray(array_axial, mode='RGB')
        self.photo_ax = PIL.ImageTk.PhotoImage(self.image_ax)
        self.image_cor = PIL.Image.fromarray(array_sagittal, mode='RGB')
        self.photo_cor = PIL.ImageTk.PhotoImage(self.image_cor)

        self.canvas_axial.delete("IMG")
        self.canvas_axial.create_image((0, 0), image=self.photo_ax, anchor=NW, tags="IMG")
        self.canvas_axial.create_text(40, 10, fill="green", text="Slice " + str(index_axial), font=10)
        self.canvas_axial.create_text(40, 40, fill="green", text="Axial", font=10)

        self.canvas_coronal.delete("IMG")
        self.canvas_coronal.create_image((0, 0), image=self.photo_cor, anchor=NW, tags="IMG")
        self.canvas_coronal.create_text(40, 10, fill="green", text="x = " + str(index_sagittal), font=10)
        self.canvas_coronal.create_text(40, 40, fill="green", text="Coronal", font=10)

        width_ax = self.image_ax.width
        height_ax = self.image_ax.height
        width_sag = self.image_cor.width
        height_sag = self.image_cor.height

        self.canvas_axial.configure(width=width_ax, height=height_ax)
        self.canvas_coronal.configure(width=width_sag, height=height_sag)

        # We need to at least fit the entire image, but don't shrink if we don't have to
        width_ax = max(self.parent.winfo_width(), width_ax)
        height_ax = max(self.parent.winfo_height(), height_ax + StatusBar.height)
        width_sag = max(self.parent.winfo_width(), width_sag)
        height_sag = max(self.parent.winfo_height(), height_sag + StatusBar.height)

        # Resize root window and prevent resizing smaller than the image
        newsize = "{}x{}".format(width_ax + width_sag, height_ax + StatusBar.height)

        # self.parent.geometry(newsize)
        # self.parent.minsize(width_ax + width_sag, height_ax + height_sag)

        if self.selection_axial is not None:
            self.selection_axial = self.canvas_axial.create_rectangle(self.start_x, self.start_y, self.end_x,
                                                                      self.end_y, outline="green")
        if self.center_axial is not None:
            x1, y1 = (self.x_center - self.extent), (self.y_center - self.extent)
            x2, y2 = (self.x_center + self.extent), (self.y_center + self.extent)
            self.center_axial = self.canvas_axial.create_oval(x1, y1, x2, y2, fill="red")

        if self.selection_coronal is not None:
            self.selection_coronal = self.canvas_coronal.create_rectangle(self.start_z, self.start_x, self.end_z,
                                                                          self.end_x, outline="green")
        if self.center_coronal is not None:
            x1, z1 = (self.x_center - self.extent), (self.z_center - self.extent)
            x2, z2 = (self.x_center + self.extent), (self.z_center + self.extent)
            self.center_coronal = self.canvas_coronal.create_oval(z1, x1, z2, x2, fill="red")
        return 0

    def scroll_axial_images(self, event):
        self.imager.index_axial += int(event.delta / 120)
        self.arr_axial, self.index_axial = self.imager.get_current_axial_image()
        self.show_image(self.arr_axial, self.index_axial, self.arr_coronal, self.index_coronal)
        return 0

    def scroll_coronal_images(self, event):
        self.imager.index_coronal += int(event.delta / 120)
        self.arr_coronal, self.index_coronal = self.imager.get_current_coronal_image()
        self.show_image(self.arr_axial, self.index_axial, self.arr_coronal, self.index_coronal)
        return 0


if __name__ == "__main__":
    parent = tk.Tk()
    up = DicomFullViewerFrame(parent)
    up.pack()

    dir = "../../../im_DICOM/new_acquisition_IRM_CBCT/NA_CBCT_wo_H2O/"

    datasets = []
    for filename in os.listdir(dir):
        if filename[0] == "I":
            ds = pdcm.dcmread(dir + filename)
            datasets.append(ds)

    imager = dicom_full_imager.DicomFullImager(datasets)

    up.set_imager(imager)

    im_axial, ind_axial = imager.get_current_axial_image()
    im_coronal, ind_coronal = imager.get_current_coronal_image()

    up.show_image(im_axial, ind_axial, im_coronal, ind_coronal)

    parent.mainloop()
