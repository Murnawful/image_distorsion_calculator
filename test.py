import numpy as np
import matplotlib.pyplot as plt
import pydicom as pdcm
import tkinter as tk
from tkinter import ttk
import PIL.Image
import PIL.ImageTk

ds = pdcm.read_file("../../im_DICOM/complete_IRM_CBCT/CBCT_wo_H2O/IMG0000000220.dcm")
img = ds.pixel_array

plt.imshow(img)
plt.show()

_window_width = 10
_window_center = 50

# Vectorized windowing using boolean masks
w_left = (_window_center - _window_width / 2)
w_right = (_window_center + _window_width / 2)
mask_0 = img < 150
mask_1 = img > 100
mask_2 = np.invert(mask_0 + mask_1)

ask_0 = img < 5000
ask_1 = img > 100
ask_2 = ask_0 + ask_1
res1 = np.zeros(img.shape)
res1[img < 5000] = 1
res1[img < 100] = 0

# Cast to RGB image so that Tkinter can handle it
res = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)
res[:, :, 0] = res[:, :, 1] = res[:, :, 2] = res1 * 255

plt.imshow(res1)
plt.show()

root = tk.Tk()

myCanvas = tk.Canvas(root, bg="white", height=1000, width=1000)
image = PIL.Image.fromarray(res)
photo = PIL.ImageTk.PhotoImage(image)
myCanvas.create_image(500, 500, image=photo)

myCanvas.pack()
root.mainloop()

