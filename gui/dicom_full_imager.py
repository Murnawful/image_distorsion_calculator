import numpy as np

from gui import dicom_imager


class DicomFullImager(dicom_imager.DicomImager):
    def __init__(self, datasets):
        self.new_values = None

        super().__init__(datasets)

        self.prepare_values_RGB()

    def get_coronal_image(self, index, *args, **kwargs):
        img = self.new_values[index, :, :, :]
        return img

    def get_axial_image(self, index, *args, **kwargs):
        img = self.new_values[:, :, index, :]
        return img

    def get_current_coronal_image(self):
        return self.get_coronal_image(self._index_coronal), self._index_coronal

    def get_current_axial_image(self):
        return self.get_axial_image(self._index_axial), self._index_axial

    def prepare_values_RGB(self):
        self.new_values = np.zeros((self._values.shape[0], self._values.shape[1], self._values.shape[2], 3),
                                   dtype='uint8')
        a_r = - 255 / ((self.max_value - self.min_value) ** 2)
        h_r = self.max_value
        a_g = - 1023 / ((self.min_value - self.max_value) ** 2)
        h_g = (self.min_value + self.max_value) / 2
        a_b = - 255 / ((self.min_value - self.max_value) ** 2)
        h_b = self.min_value
        r = a_r * np.square(self._values - h_r) + 255
        g = a_g * np.square(self._values - h_g) + 255
        b = a_b * np.square(self._values - h_b) + 255
        self.new_values[:, :, :, 0] = r
        self.new_values[:, :, :, 1] = g
        self.new_values[:, :, :, 2] = b
