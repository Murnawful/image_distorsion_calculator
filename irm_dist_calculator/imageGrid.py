import numpy as np
import open3d as o3d


class ImageGrid:

    def __init__(self, values, spacing, image_roi=None, range_values=(0, 200000), is_mri=False):
        self.data = None
        self.points = None
        self.pcd = None
        self.ds = None
        self.voxelSpacing_x = None
        self.voxelSpacing_y = None
        self.voxelSpacing_z = None
        self.hu_range = None
        self.is_loaded = False
        self.roi = None
        self.imageIsMri = False

        try:
            self.set_spacing(spacing)
            self.data = values
            self.hu_range = range_values
            self.imageIsMri = is_mri
            if image_roi is None:
                self.roi = None
            else:
                self.roi = (slice(image_roi[0][1], image_roi[1][1]),
                            slice(image_roi[0][0], image_roi[1][0]),
                            slice(image_roi[0][2], image_roi[1][2]))

            self.is_loaded = True
            print("DICOM files loaded and stored")
        except PermissionError:
            print("Error: No DICOM files was found in this directory")

    def convert(self):
        try:
            new_data = np.zeros(self.data.shape)

            new_data[self.data < self.hu_range[1]] = 1
            new_data[self.data < self.hu_range[0]] = 0

            if self.roi is None:
                self.data = new_data
            else:
                self.data = np.zeros(new_data.shape)
                self.data[self.roi] = new_data[self.roi]
                if self.imageIsMri:
                    m = np.amax(self.data[self.roi])
                    self.data[self.roi] = (-1) * self.data[self.roi] + m

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

    def set_spacing(self, s):
        self.voxelSpacing_x = s[0] * 1e-3
        self.voxelSpacing_y = s[1] * 1e-3
        self.voxelSpacing_z = s[2] * 1e-3
        return 0
