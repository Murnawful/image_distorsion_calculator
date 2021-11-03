import PIL.Image
import PIL.ImageTk

from gui.statusbar import *


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
        self.x_center = self.y_center = self.z_center = 0
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

    def show_image(self, array_axial, index_axial, array_sagittal, index_sagittal, *args, **kwargs):
        pass

    def set_imager(self, im):
        self.imager = im
        return 0

    def get_virtual_grid_center(self):
        spacing = self.imager.spacings
        x = self.x_center * spacing[2] * 1e-3
        y = self.y_center * spacing[1] * 1e-3
        z = (self.imager.size[2] - self.z_center) * spacing[2] * 1e-3
        return x, y, z

    def on_right_press_axial(self, event):
        self.canvas_axial.delete(self.center_axial)
        self.canvas_coronal.delete(self.center_coronal)

        self.x_center = event.x
        self.y_center = event.y

        x1, y1 = (self.x_center - self.extent), (self.y_center - self.extent)
        x2, y2 = (self.x_center + self.extent), (self.y_center + self.extent)
        x3, y3 = ((self.image_cor.width // 2) - self.extent), (self.x_center - self.extent)
        x4, y4 = ((self.image_cor.width // 2) + self.extent), (self.x_center + self.extent)

        self.center_axial = self.canvas_axial.create_oval(x1, y1, x2, y2, fill="red")
        self.center_coronal = self.canvas_coronal.create_oval(x3, y3, x4, y4, fill="red")
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

    def on_move_press_axial(self, event):
        self.end_x = event.x
        self.end_y = event.y

        self.motion_axial(event)

        # expand rectangle as you drag the mouse
        self.canvas_axial.coords(self.selection_axial, self.start_x, self.start_y, self.end_x, self.end_y)
        self.canvas_coronal.coords(self.selection_coronal, 0, self.start_x, self.arr_coronal.shape[1], self.end_x)
        return 0

    def scroll_axial_images(self, event):
        pass

    def motion_axial(self, event):
        x, y = event.x, event.y
        self.status_axial.set('x = {}, y = {}'.format(x, y))
        return 0

    def on_right_press_coronal(self, event):
        self.canvas_coronal.delete(self.center_coronal)

        self.z_center = event.x

        x1, z1 = (self.x_center - self.extent), (self.z_center - self.extent)
        x2, z2 = (self.x_center + self.extent), (self.z_center + self.extent)

        self.center_coronal = self.canvas_coronal.create_oval(z1, x1, z2, x2, fill="red")
        return 0

    def on_button_press_coronal(self, event):
        self.canvas_coronal.delete(self.selection_coronal)

        self.start_z = event.x

        self.selection_coronal = self.canvas_coronal.create_rectangle(self.start_z, self.start_x, 0,
                                                                      self.end_x, outline="green")
        return 0

    def on_move_press_coronal(self, event):
        self.end_z = event.x

        self.motion_coronal(event)

        # expand rectangle as you drag the mouse
        self.canvas_coronal.coords(self.selection_coronal, self.start_z, self.start_x, self.end_z, self.end_x)
        return 0

    def on_button_release(self, event):
        roi_axial = self.canvas_axial.bbox(self.selection_axial)
        roi_sagittal = self.canvas_coronal.bbox(self.selection_coronal)
        self.roi = ((roi_axial[0], roi_axial[1], roi_sagittal[0] + 1), (roi_axial[2], roi_axial[3], roi_sagittal[2] - 1))
        return 0

    def scroll_coronal_images(self, event):
        pass

    def motion_coronal(self, event):
        z, y = event.x, event.y
        self.status_coronal.set('y = {}, z = {}'.format(y, z))
        return 0
