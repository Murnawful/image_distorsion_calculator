import numpy as np
import open3d as o3d


class ReferenceFiducials:
    offset_x = None
    offset_y = None
    offset_z = None
    data_fiducial_R = None
    data_fiducial_L = None
    pcd_fiducial_R = None
    pcd_fiducial_L = None

    def __init__(self, offset):
        self.offset_x = offset[0]
        self.offset_y = offset[1]
        self.offset_z = offset[2]

    def build(self):
        t = np.linspace(0, 120e-3, 10000)
        x = np.zeros(t.shape) + self.offset_x
        y = np.zeros(t.shape) + self.offset_y
        z = np.copy(t) + self.offset_z

        x1 = np.zeros(t.shape) + self.offset_x
        y1 = np.ones(t.shape) * 120e-3 + self.offset_y
        z1 = np.copy(t) + self.offset_z

        x2 = np.zeros(t.shape) + self.offset_x
        y2 = (-1) * np.copy(t) + 2 * 60e-3 + self.offset_y
        z2 = np.copy(t) + self.offset_z

        x_line = np.concatenate((x, x1, x2))
        y_line = np.concatenate((y, y1, y2))
        z_line = np.concatenate((z, z1, z2))

        self.data_fiducial_L = np.zeros((x_line.shape[0], 3))
        self.data_fiducial_L[:, 0] = x_line
        self.data_fiducial_L[:, 1] = y_line
        self.data_fiducial_L[:, 2] = z_line

        self.data_fiducial_R = np.zeros((x_line.shape[0], 3))
        self.data_fiducial_R[:, 0] = x_line + 190e-3
        self.data_fiducial_R[:, 1] = y_line
        self.data_fiducial_R[:, 2] = z_line

    def convert(self):
        self.pcd_fiducial_R = o3d.geometry.PointCloud()
        self.pcd_fiducial_R.points = o3d.utility.Vector3dVector(self.data_fiducial_R)
        self.pcd_fiducial_L = o3d.geometry.PointCloud()
        self.pcd_fiducial_L.points = o3d.utility.Vector3dVector(self.data_fiducial_L)
