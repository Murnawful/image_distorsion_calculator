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
        self.image_cor = None
        self.photo_ax = None
        self.photo_cor = None
        self.canvas_axial = None
        self.canvas_coronal = None
        self.imager = None

        self.arr_axial = None
        self.arr_coronal = None
        self.index_axial = None
        self.index_coronal = None

        self.status_axial = None
        self.status_coronal = None

        self.roi_definition = True

        self.upper = 0
        self.lower = 0

        self.selection_axial = None
        self.selection_coronal = None
        self.center_axial = None
        self.center_coronal = None
        self.start_x = self.start_y = self.start_z = 0
        self.end_x = self.end_y = self.end_z = 0
        self.x = self.y = self.z = 0
        self.roi = None

        self.offset = 800
        self.extent = 4

        self.init_viewer_frame()

    def init_viewer_frame(self):

        self.roi = None

        # Image canvas
        self.canvas_axial = Canvas(self, bd=0, highlightthickness=0)
        self.canvas_axial.grid(row=0, column=0, sticky="nw")
        self.canvas_axial.bind("<MouseWheel>", self.scroll_axial_images)
        self.canvas_axial.config(width=self.offset)
        if self.roi_definition:
            self.canvas_axial.bind("<B1-Motion>", self.on_move_press_axial)
            self.canvas_axial.bind("<ButtonPress-1>", self.on_button_press_axial)
            self.canvas_axial.bind("<ButtonRelease-1>", self.on_button_release)
            self.canvas_axial.bind("<Button-3>", self.on_right_press_axial)

        self.canvas_coronal = Canvas(self, bd=0, highlightthickness=0)
        self.canvas_coronal.grid(row=0, column=1, sticky="nw")
        self.canvas_coronal.bind("<MouseWheel>", self.scroll_coronal_images)
        if self.roi_definition:
            self.canvas_coronal.bind("<B1-Motion>", self.on_move_press_coronal)
            self.canvas_coronal.bind("<ButtonPress-1>", self.on_button_press_coronal)
            self.canvas_coronal.bind("<ButtonRelease-1>", self.on_button_release)
            self.canvas_coronal.bind("<Button-3>", self.on_right_press_coronal)

        # Status bar
        self.status_axial = StatusBar(self)
        self.status_axial.grid(row=3, column=0, sticky="w")
        self.status_coronal = StatusBar(self)
        self.status_coronal.grid(row=3, column=1, sticky="w")

        self.canvas_axial.bind('<Motion>', self.motion_axial)
        self.canvas_coronal.bind('<Motion>', self.motion_coronal)
        return 0

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
        self.image_cor = PIL.Image.fromarray(array_sagittal)
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

        self.parent.geometry(newsize)
        # self.parent.minsize(width_ax + width_sag, height_ax + height_sag)

        if self.selection_axial is not None:
            self.selection_axial = self.canvas_axial.create_rectangle(self.start_x, self.start_y, self.end_x,
                                                                      self.end_y, outline="green")
        if self.center_axial is not None:
            x1, y1 = (self.x - self.extent), (self.y - self.extent)
            x2, y2 = (self.x + self.extent), (self.y + self.extent)
            self.center_axial = self.canvas_axial.create_oval(x1, y1, x2, y2, fill="red")

        if self.selection_coronal is not None:
            self.selection_coronal = self.canvas_coronal.create_rectangle(self.start_z, self.start_x, self.end_z,
                                                                          self.end_x, outline="green")
        if self.center_coronal is not None:
            x1, z1 = (self.x - self.extent), (self.z - self.extent)
            x2, z2 = (self.x + self.extent), (self.z + self.extent)
            self.center_coronal = self.canvas_coronal.create_oval(z1, x1, z2, x2, fill="red")
        return 0

    def on_right_press_axial(self, event):
        self.canvas_axial.delete(self.center_axial)
        self.canvas_coronal.delete(self.center_coronal)

        self.x = event.x
        self.y = event.y

        x1, y1 = (self.x - self.extent), (self.y - self.extent)
        x2, y2 = (self.x + self.extent), (self.y + self.extent)
        x3, y3 = ((self.image_cor.width // 2) - self.extent), (self.x - self.extent)
        x4, y4 = ((self.image_cor.width // 2) + self.extent), (self.x + self.extent)

        self.center_axial = self.canvas_axial.create_oval(x1, y1, x2, y2, fill="red")
        self.center_coronal = self.canvas_coronal.create_oval(x3, y3, x4, y4, fill="red")
        return 0

    def on_right_press_coronal(self, event):
        self.canvas_coronal.delete(self.center_coronal)

        self.z = event.x

        x1, z1 = (self.x - self.extent), (self.z - self.extent)
        x2, z2 = (self.x + self.extent), (self.z + self.extent)

        self.center_coronal = self.canvas_coronal.create_oval(z1, x1, z2, x2, fill="red")
        return 0

    def on_button_press_axial(self, event):
        self.canvas_axial.delete(self.selection_axial)
        self.canvas_coronal.delete(self.selection_coronal)

        # save mouse drag start position
        self.start_x = event.x
        self.start_y = event.y

        self.selection_axial = self.canvas_axial.create_rectangle(self.end_x, self.end_y, 0, 0, outline="green")
        self.selection_coronal = self.canvas_coronal.create_rectangle(0, self.start_x, self.arr_coronal.shape[1],
                                                                      self.end_x, outline="green")
        return 0

    def on_button_press_coronal(self, event):
        self.canvas_coronal.delete(self.selection_coronal)

        # save mouse drag start position
        self.start_z = event.x

        self.selection_coronal = self.canvas_coronal.create_rectangle(self.start_z, self.start_x, 0,
                                                                      self.end_x, outline="green")
        return 0

    def on_move_press_axial(self, event):
        curX, curY = (event.x, event.y)
        self.end_x = curX
        self.end_y = curY

        self.motion_axial(event)

        # expand rectangle as you drag the mouse
        self.canvas_axial.coords(self.selection_axial, self.start_x, self.start_y, curX, curY)
        self.canvas_coronal.coords(self.selection_coronal, 0, self.start_x, self.arr_coronal.shape[1], curX)
        return 0

    def on_move_press_coronal(self, event):
        curZ = event.x
        self.end_z = curZ

        self.motion_coronal(event)

        # expand rectangle as you drag the mouse
        self.canvas_coronal.coords(self.selection_coronal, self.start_z, self.start_x, curZ, self.end_x)
        return 0

    def on_button_release(self, event):
        roi_axial = self.canvas_axial.bbox(self.selection_axial)
        roi_sagittal = self.canvas_coronal.bbox(self.selection_coronal)
        self.roi = ((roi_axial[0], roi_axial[1], roi_sagittal[0] + 1), (roi_axial[2], roi_axial[3], roi_sagittal[2] - 1))
        return 0

    def scroll_coronal_images(self, e):
        self.imager.index_coronal += int(e.delta / 120)
        self.arr_coronal, self.index_coronal = self.imager.get_current_coronal_image(self.upper, self.lower)
        self.show_image(self.arr_axial, self.index_axial, self.arr_coronal, self.index_coronal)
        return 0

    def scroll_axial_images(self, e):
        self.imager.index_axial += int(e.delta / 120)
        self.arr_axial, self.index_axial = self.imager.get_current_axial_image(self.upper, self.lower)
        self.show_image(self.arr_axial, self.index_axial, self.arr_coronal, self.index_coronal)
        return 0

    def change_range(self):
        self.arr_axial, self.index_axial = self.imager.get_current_axial_image(self.upper, self.lower)
        self.arr_coronal, self.index_coronal = self.imager.get_current_coronal_image(self.upper, self.lower)
        self.show_image(self.arr_axial, self.index_axial, self.arr_coronal, self.index_coronal)
        return 0

    def set_imager(self, im):
        self.imager = im
        return 0

    def motion_axial(self, event):
        x, y = event.x, event.y
        self.status_axial.set('x = {}, y = {}'.format(x, y))
        return 0

    def motion_coronal(self, event):
        z, y = event.x, event.y
        self.status_coronal.set('y = {}, z = {}'.format(y, z))
        return 0
