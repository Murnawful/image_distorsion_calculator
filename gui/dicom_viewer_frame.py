import PIL.Image
import PIL.ImageTk
import numpy as np

from gui.statusbar import *

from tkinter.messagebox import showinfo


class DicomViewerFrame(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)

        self.parent = parent

        self.image_ax = None
        self.image_sag = None
        self.photo_ax = None
        self.photo_sag = None
        self.canvas_axial = None
        self.canvas_sagittal = None
        self.imager = None

        self.arr_axial = None
        self.arr_sagittal = None
        self.index_axial = None
        self.index_sagittal = None

        self.status_axial = None
        self.status_sagittal = None

        self.upper = 0
        self.lower = 0

        self.selection = None
        self.start_x = None
        self.start_y = None
        self.end_x = self.end_y = 0
        self.roi = None

        self.init_viewer_frame()

    def init_viewer_frame(self):

        # Image canvas
        self.canvas_axial = Canvas(self, bd=0, highlightthickness=0)
        self.canvas_axial.grid(row=0, column=0, sticky="w")
        self.canvas_axial.bind("<MouseWheel>", self.scroll_axial_images)
        self.canvas_axial.bind("<B1-Motion>", self.on_move_press)
        self.canvas_axial.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas_axial.bind("<ButtonRelease-1>", self.on_button_release)

        self.canvas_sagittal = Canvas(self, bd=0, highlightthickness=0)
        self.canvas_sagittal.grid(row=0, column=1, sticky="w")
        self.canvas_sagittal.bind("<MouseWheel>", self.scroll_sagittal_images)

        # Status bar
        self.status_axial = StatusBar(self)
        self.status_axial.grid(row=3, column=0, sticky="w")
        self.status_sagittal = StatusBar(self)
        self.status_sagittal.grid(row=3, column=1, sticky="w")

        self.canvas_axial.bind('<Motion>', self.motion_axial)
        self.canvas_sagittal.bind('<Motion>', self.motion_sagittal)

    def on_button_press(self, event):
        self.canvas_axial.delete(self.selection)

        # save mouse drag start position
        self.start_x = event.x
        self.start_y = event.y

        self.selection = self.canvas_axial.create_rectangle(self.end_x, self.end_y, 1, 1, outline="green")

    def on_move_press(self, event):
        curX, curY = (event.x, event.y)
        self.end_x = curX
        self.end_y = curY

        self.motion_axial(event)

        # expand rectangle as you drag the mouse
        self.canvas_axial.coords(self.selection, self.start_x, self.start_y, curX, curY)

    def on_button_release(self, event):
        self.roi = self.canvas_axial.bbox(self.selection)
        showinfo(title="ROI", message=str(self.roi))

    def show_image(self, array_axial, index_axial, array_sagittal, index_sagittal):
        self.upper = int(self.parent.pcd_preparer.get_current_upper().get())
        self.lower = int(self.parent.pcd_preparer.get_current_lower().get())

        if array_axial is None:
            return
        if array_sagittal is None:
            return

        # Convert numpy array into a PhotoImage and add it to canvas
        self.image_ax = PIL.Image.fromarray(array_axial)
        self.photo_ax = PIL.ImageTk.PhotoImage(self.image_ax)
        self.canvas_axial.delete("IMG")
        self.canvas_axial.create_image(0, 0, image=self.photo_ax, anchor=NW, tags="IMG")
        self.canvas_axial.create_text(40, 10, fill="green", text="Slice " + str(index_axial), font=10)

        self.image_sag = PIL.Image.fromarray(array_sagittal)
        self.photo_sag = PIL.ImageTk.PhotoImage(self.image_sag)
        self.canvas_sagittal.delete("IMG")
        self.canvas_sagittal.create_image(0, 0, image=self.photo_sag, anchor=NW, tags="IMG")
        self.canvas_sagittal.create_text(40, 10, fill="green", text="x = " + str(index_sagittal), font=10)

        width_ax = self.image_ax.width
        height_ax = self.image_ax.height
        width_sag = self.image_sag.width
        height_sag = self.image_sag.height

        self.canvas_axial.configure(width=width_ax, height=height_ax)
        self.canvas_sagittal.configure(width=width_sag, height=height_sag)

        # We need to at least fit the entire image, but don't shrink if we don't have to
        width_ax = max(self.parent.winfo_width(), width_ax)
        height_ax = max(self.parent.winfo_height(), height_ax + StatusBar.height)
        width_sag = max(self.parent.winfo_width(), width_sag)
        height_sag = max(self.parent.winfo_height(), height_sag + StatusBar.height)

        # Resize root window and prevent resizing smaller than the image
        newsize = "{}x{}".format(width_ax + width_sag, height_ax + StatusBar.height)
        self.parent.geometry(newsize)
        self.parent.minsize(width_ax + width_sag, height_ax)

    def scroll_sagittal_images(self, e):
        self.imager.index_sagittal += int(e.delta / 120)
        self.arr_sagittal, self.index_sagittal = self.imager.get_current_sagittal_image(self.upper, self.lower)
        self.show_image(self.arr_axial, self.index_axial, self.arr_sagittal, self.index_sagittal)

    def scroll_axial_images(self, e):
        self.imager.index_axial += int(e.delta / 120)
        self.arr_axial, self.index_axial = self.imager.get_current_axial_image(self.upper, self.lower)
        self.show_image(self.arr_axial, self.index_axial, self.arr_sagittal, self.index_sagittal)

    def change_range(self):
        self.arr_axial, self.index_axial = self.imager.get_current_axial_image(self.upper, self.lower)
        self.arr_sagittal, self.index_sagittal = self.imager.get_current_sagittal_image(self.upper, self.lower)
        self.show_image(self.arr_axial, self.index_axial, self.arr_sagittal, self.index_sagittal)

    def set_imager(self, im):
        self.imager = im

    def motion_axial(self, event):
        x, y = event.x, event.y
        self.status_axial.set('x = {}, y = {}'.format(x, y))

    def motion_sagittal(self, event):
        y, z = event.x, event.y
        self.status_sagittal.set('y = {}, z = {}'.format(y, z))
