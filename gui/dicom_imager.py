import numpy as np

from abc import ABC


class DicomImager(ABC):
    def __init__(self, datasets):
        self._values = None

        self.datasets = datasets
        self._index_axial = 0
        self._index_coronal = 0
        self._window_width = 1
        self._window_center = 0

        self.size = (int(datasets[1].Rows), int(datasets[1].Columns), len(datasets))
        self.spacings = (float(datasets[1].PixelSpacing[0]),
                         float(datasets[1].PixelSpacing[1]),
                         float(datasets[1].SliceThickness))

        self.axes = (np.arange(0.0, (self.size[0] + 1) * self.spacings[0], self.spacings[0]),
                     np.arange(0.0, (self.size[2] + 1) * self.spacings[2], self.spacings[2]),
                     np.arange(0.0, (self.size[1] + 1) * self.spacings[1], self.spacings[1]))

        # Load pixel data
        self._values = np.zeros(self.size, dtype='int32')
        for i, d in enumerate(datasets):
            # Also performs rescaling. 'unsafe' since it converts from float64 to int32
            np.copyto(self._values[:, :, i], d.pixel_array, 'unsafe')

        self.max_value = np.amax(self._values)
        self.min_value = np.amin(self._values)

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

    def get_coronal_image(self, index, *args, **kwargs):
        pass

    def get_axial_image(self, index, *args, **kwargs):
        pass

    def get_current_coronal_image(self, *args, **kwargs):
        pass

    def get_current_axial_image(self, *args, **kwargs):
        pass
