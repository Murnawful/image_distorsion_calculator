from tkinter.filedialog import askopenfilenames
import pydicom as dicom
import PIL.Image
import PIL.ImageTk

from gui.statusbar import *


class DicomViewerFrame(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)

        self.parent = parent

        self.image = None
        self.photo = None
        self.canvas = None
        self.imager = None

        self.status = None
        self.right_click_menu = None

        self.mouse_wheel_down = False
        self.last_mouse_pos = None

        self.init_ui()

    def init_ui(self):

        # Image canvas
        self.canvas = Canvas(self.parent, bd=0, highlightthickness=0)
        self.canvas.grid(row=0, rowspan=3, column=1, sticky="w")
        self.canvas.bind("<Button-3>", self.show_right_click_menu)  # <Button-3> is the right click event
        self.canvas.bind("<MouseWheel>", self.scroll_images)
        self.canvas.bind("<B2-Motion>", self.on_mouse_wheel_drag)
        self.canvas.bind("<Button-2>", self.on_mouse_wheel_down)
        self.canvas.bind("<ButtonRelease-2>", self.on_mouse_wheel_up)
        #  self.canvas.bind("<Configure>", self.resize)

        # Right-click menu
        self.right_click_menu = Menu(self.parent, tearoff=0)
        self.right_click_menu.add_command(label="Beep", command=self.bell)

    def show_image(self, numpy_array):
        if numpy_array is None:
            return

        # Convert numpy array into a PhotoImage and add it to canvas
        self.image = PIL.Image.fromarray(numpy_array)
        self.photo = PIL.ImageTk.PhotoImage(self.image)
        self.canvas.delete("IMG")
        self.canvas.create_image(0, 0, image=self.photo, anchor=NW, tags="IMG")
        self.canvas.configure(width=self.image.width, height=self.image.height)

        # We need to at least fit the entire image, but don't shrink if we don't have to
        width = max(self.parent.winfo_width(), self.image.width)
        height = max(self.parent.winfo_height(), self.image.height + StatusBar.height)

        # Resize root window and prevent resizing smaller than the image
        newsize = "{}x{}".format(width, height)
        self.parent.geometry(newsize)
        self.parent.minsize(self.image.width, self.image.height + StatusBar.height)

    def show_right_click_menu(self, e):
        self.right_click_menu.post(e.x_root, e.y_root)

    def scroll_images(self, e):
        self.imager.index += int(e.delta/120)
        self.show_image(self.imager.get_current_image())

    def on_mouse_wheel_down(self, e):
        self.last_mouse_pos = (e.x, e.y)
        self.mouse_wheel_down = True

    def on_mouse_wheel_up(self, e):
        self.last_mouse_pos = None
        self.mouse_wheel_down = True

    def on_mouse_wheel_drag(self, e):
        if self.mouse_wheel_down:
            delta = (e.x - self.last_mouse_pos[0], e.y - self.last_mouse_pos[1])
            self.last_mouse_pos = (e.x, e.y)

            self.imager.window_width += delta[0] * 5
            self.imager.window_center += delta[1] * 5

            self.show_image(self.imager.get_current_image())

    def callback(self):
        self.status.set("Not implemented yet!")

    def set_imager(self, im):
        self.imager = im