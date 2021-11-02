import numpy as np

from gui import dicom_imager


class DicomBinaryImager(dicom_imager.DicomImager):
    def __init__(self, datasets):
        super().__init__(datasets)

    def get_coronal_image(self, index, upper=None, lower=None, *args, **kwargs):
        # int32 true values (HU or brightness units)
        img = self._values[index, :, :]

        res1 = np.zeros(img.shape)
        res1[img < upper] = 1
        res1[img < lower] = 0

        # Cast to RGB image so that Tkinter can handle it
        res = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)
        res[:, :, 0] = res[:, :, 1] = res[:, :, 2] = res1 * 255

        return res

    def get_axial_image(self, index, upper=None, lower=None, *args, **kwargs):
        # int32 true values (HU or brightness units)
        img = self._values[:, :, index]

        res1 = np.zeros(img.shape)
        res1[img < upper] = 1
        res1[img < lower] = 0

        # Cast to RGB image so that Tkinter can handle it
        res = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)
        res[:, :, 0] = res[:, :, 1] = res[:, :, 2] = res1 * 255

        return res

    def get_current_coronal_image(self, upper, lower):
        return self.get_coronal_image(self._index_coronal, upper=upper, lower=lower), self._index_coronal

    def get_current_axial_image(self, upper, lower):
        return self.get_axial_image(self._index_axial, upper=upper, lower=lower), self._index_axial


import pydicom as pdcm
import matplotlib.pyplot as plt

if __name__ == "__main__":
    d1 = pdcm.dcmread("../../../im_DICOM/new_acquisition_IRM_CBCT/NA_CBCT_wo_H2O/IMG0000000373.dcm")
    d2 = pdcm.dcmread("../../../im_DICOM/new_acquisition_IRM_CBCT/NA_CBCT_wo_H2O/IMG0000000374.dcm")
    d3 = pdcm.dcmread("../../../im_DICOM/new_acquisition_IRM_CBCT/NA_CBCT_wo_H2O/IMG0000000375.dcm")
    d4 = pdcm.dcmread("../../../im_DICOM/new_acquisition_IRM_CBCT/NA_CBCT_wo_H2O/IMG0000000376.dcm")
    s = [d1, d2, d3, d4]
    test = DicomBinaryImager(s)
    im, ind = test.get_current_coronal_image(lower=0, upper=1000)
    print(im.shape)
    plt.imshow(im)
    plt.show()
