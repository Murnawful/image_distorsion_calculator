import numpy as np


class DicomImager:
    def __init__(self, datasets):
        self.datasets = datasets
        self._index = 0
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
    def index(self):
        return self._index

    @index.setter
    def index(self, value):

        while value < 0:
            value += self.size[2]

        self._index = value % self.size[2]

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

    def get_image(self, index, upper, lower):
        # int32 true values (HU or brightness units)
        img = self.values[:, :, index]

        # Vectorized windowing using boolean masks
        w_left = (self._window_center - self._window_width / 2)
        w_right = (self._window_center + self._window_width / 2)
        mask_0 = img < w_left
        mask_1 = img > w_right
        mask_2 = np.invert(mask_0 + mask_1)

        res1 = np.zeros(img.shape)
        res1[img < upper] = 1
        res1[img < lower] = 0

        # Cast to RGB image so that Tkinter can handle it
        res = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)
        res[:, :, 0] = res[:, :, 1] = res[:, :, 2] = res1 * 255

        return res

    def get_current_image(self, upper, lower):
        return self.get_image(self.index, upper, lower), self.index
