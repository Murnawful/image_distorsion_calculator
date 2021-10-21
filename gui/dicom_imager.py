import numpy as np


class DicomImager:
    def __init__(self, datasets):
        self.values = None

        self.datasets = datasets
        self._index_axial = 0
        self._index_coronal = 0
        self._window_width = 1
        self._window_center = 0

        self.size = (int(datasets[0].Rows), int(datasets[0].Columns), len(datasets))
        self.spacings = (float(datasets[0].PixelSpacing[0]),
                         float(datasets[0].PixelSpacing[1]),
                         float(datasets[0].SliceThickness))

        self.axes = (np.arange(0.0, (self.size[0] + 1) * self.spacings[0], self.spacings[0]),
                     np.arange(0.0, (self.size[2] + 1) * self.spacings[2], self.spacings[2]),
                     np.arange(0.0, (self.size[1] + 1) * self.spacings[1], self.spacings[1]))

        # Load pixel data
        self.values = np.zeros(self.size, dtype='int32')
        for i, d in enumerate(datasets):
            # Also performs rescaling. 'unsafe' since it converts from float64 to int32
            np.copyto(self.values[:, :, i], d.pixel_array, 'unsafe')

        self.max_value = np.amax(self.values)
        self.min_value = np.amin(self.values)

    @property
    def index_coronal(self):
        return self._index_coronal

    @index_coronal.setter
    def index_coronal(self, value):

        while value < 0:
            value += self.size[0]

        self._index_coronal = value % self.size[0]

    @property
    def index_axial(self):
        return self._index_axial

    @index_axial.setter
    def index_axial(self, value):

        while value < 0:
            value += self.size[2]

        self._index_axial = value % self.size[2]

    @property
    def window_width(self):
        return self._window_width

    @window_width.setter
    def window_width(self, value):
        self._window_width = max(value, 1)

    @property
    def window_center(self):
        return self._window_center

    @window_center.setter
    def window_center(self, value):
        self._window_center = value

    def get_coronal_image(self, index, upper, lower):
        # int32 true values (HU or brightness units)
        img = self.values[index, :, :]

        res1 = np.zeros(img.shape)
        res1[img < upper] = 1
        res1[img < lower] = 0

        # Cast to RGB image so that Tkinter can handle it
        res = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)
        res[:, :, 0] = res[:, :, 1] = res[:, :, 2] = res1 * 255

        return res

    def get_axial_image(self, index, upper, lower):
        # int32 true values (HU or brightness units)
        img = self.values[:, :, index]

        res1 = np.zeros(img.shape)
        res1[img < upper] = 1
        res1[img < lower] = 0

        # Cast to RGB image so that Tkinter can handle it
        res = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)
        res[:, :, 0] = res[:, :, 1] = res[:, :, 2] = res1 * 255

        return res

    def get_current_coronal_image(self, upper, lower):
        return self.get_coronal_image(self._index_coronal, upper, lower), self._index_coronal

    def get_current_axial_image(self, upper, lower):
        return self.get_axial_image(self._index_axial, upper, lower), self._index_axial
