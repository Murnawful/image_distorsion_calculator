import os

import matplotlib.pyplot as plt
import numpy as np
import open3d as o3d
import pydicom as pdcm


class ImageGrid:
    data = None
    points = None
    pcd = None
    ds = None
    voxelSpacing_x = None
    voxelSpacing_y = None
    voxelSpacing_z = None
    hu_range = None
    is_loaded = False
    roi = None
    imageIsMri = False

    def __init__(self, path="", slice_number=1, image_roi=None, range_hu=(0, 20000), is_mri=False):
        try:
            self.ds = pdcm.dcmread(path + os.listdir(path)[0])
            self.data = self.ds.pixel_array
            self.voxelSpacing_x = self.ds.PixelSpacing[0] * 1e-3
            self.voxelSpacing_y = self.ds.PixelSpacing[1] * 1e-3
            self.voxelSpacing_z = self.ds.SliceThickness * 1e-3
            self.data = np.zeros((self.data.shape[0], self.data.shape[1], slice_number))
            self.hu_range = range_hu
            self.imageIsMri = is_mri
            if is_mri:
                self.data_mri = np.zeros(self.data.shape)
            if image_roi is None:
                self.roi = None
            else:
                self.roi = (slice(image_roi[0][1], image_roi[1][1]),
                            slice(image_roi[0][0], image_roi[1][0]),
                            slice(image_roi[0][2], image_roi[1][2]))
            i = 0
            for filename in os.listdir(path):
                if filename.endswith(".dcm") and i != slice_number and filename[0] == "I":
                    name = path + filename
                    ds = pdcm.dcmread(name)
                    ds.decompress()
                    arr_temp = ds.pixel_array
                    self.data[:, :, i] = arr_temp
                    i += 1
            self.is_loaded = True
            print("DICOM files loaded and stored")
        except PermissionError:
            print("Error: No DICOM files was found in this directory")

    def convert(self):
        try:
            new_data = np.zeros(self.data.shape)
            if self.roi is None:
                new_data = self.data
            else:
                new_data[self.roi] = self.data[self.roi]
                if self.imageIsMri:
                    m = np.amax(new_data)
                    new_data_copy = np.copy(new_data)
                    new_data[self.roi] = (-1) * new_data_copy[self.roi] + m

            self.data[np.where(new_data < self.hu_range[0])] = 0
            self.data[np.where(new_data > self.hu_range[1])] = 0
            self.data[np.where(self.data != 0)] = 1

            coor = np.where(self.data == 1)
            self.points = np.zeros((coor[0].shape[0], 3))
            self.points[:, 0] = coor[0] * self.voxelSpacing_x
            self.points[:, 1] = coor[1] * self.voxelSpacing_y
            self.points[:, 2] = (-coor[2] + self.data.shape[2]) * self.voxelSpacing_z

            self.points = np.array(self.points)
            self.pcd = o3d.geometry.PointCloud()
            self.pcd.points = o3d.utility.Vector3dVector(self.points)
            print("Image grid extracted")
        except TypeError:
            print("Error: No DICOM files were loaded")
        return 0

    def save_point_cloud(self, path="", name=""):
        try:
            o3d.io.write_point_cloud(path + name + ".ply", self.pcd)
            print("ROI saved as cloud point")
        except TypeError or AttributeError:
            print("Error: the point cloud does not exist. Build it and convert it first")
        return 0
