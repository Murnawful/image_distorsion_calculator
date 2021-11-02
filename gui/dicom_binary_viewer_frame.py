import PIL.Image
import PIL.ImageTk

from gui.statusbar import *

from gui import dicom_viewer_frame


class DicomBinaryViewerFrame(dicom_viewer_frame.DicomViewerFrame):
    def __init__(self, root):
        super().__init__(root)

    def change_range(self):
        self.arr_axial, self.index_axial = self.imager.get_current_axial_image(self.upper, self.lower)
        self.arr_coronal, self.index_coronal = self.imager.get_current_coronal_image(self.upper, self.lower)
        self.show_image(self.arr_axial, self.index_axial, self.arr_coronal, self.index_coronal)
        return 0

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
        self.imager.index_axial += int(event.delta / 120)
        self.arr_axial, self.index_axial = self.imager.get_current_axial_image(self.upper, self.lower)
        self.show_image(self.arr_axial, self.index_axial, self.arr_coronal, self.index_coronal)
        return 0

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
        self.imager.index_coronal += int(event.delta / 120)
        self.arr_coronal, self.index_coronal = self.imager.get_current_coronal_image(self.upper, self.lower)
        self.show_image(self.arr_axial, self.index_axial, self.arr_coronal, self.index_coronal)
        return 0

    def motion_coronal(self, event):
        z, y = event.x, event.y
        self.status_coronal.set('y = {}, z = {}'.format(y, z))
        return 0
