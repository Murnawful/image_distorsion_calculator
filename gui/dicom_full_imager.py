import numpy as np

from gui import dicom_imager


class DicomFullImager(dicom_imager.DicomImager):
    def __init__(self, datasets):
        super().__init__(datasets)

    def get_coronal_image(self, index, *args, **kwargs):
        img = self._values[index, :, :]
        return img

    def get_axial_image(self, index, *args, **kwargs):
        img = self._values[:, :, index]
        return img

    def get_current_coronal_image(self):
        return self.get_coronal_image(self._index_coronal), self._index_coronal

    def get_current_axial_image(self):
        return self.get_axial_image(self._index_axial), self._index_axial
