from irm_dist_calculator import referenceFiducials as rFi

import numpy as np
import open3d as o3d


class DiffAnalyzer:
    def __init__(self, root, dicom_datasets, center):
        self.parent = root

        self.datasets = dicom_datasets
        self.spacings = None

        self.center = center

        self.coor = None
        self.points = None
        self.pcd = None
        self.data = []

        self.fiduc = None

        self.init_analyzer()

    def init_analyzer(self):
        self.spacings = (self.datasets[0].PixelSpacing[0] * 1e-3,
                         self.datasets[0].PixelSpacing[1] * 1e-3,
                         self.datasets[0].SliceThickness * 1e-3)

        for i in range(len(self.datasets)):
            ds = self.datasets[i]
            self.data.append(ds.pixel_array)
        self.data = np.array(self.data)

        self.data[self.data < 100] = 0
        self.data[self.data != 0] = 1

        self.coor = np.where(self.data != 0)
        self.points = np.zeros((self.coor[0].shape[0], 3))
        self.points[:, 0] = self.coor[2] * self.spacings[0]
        self.points[:, 1] = self.coor[1] * self.spacings[1]
        self.points[:, 2] = self.coor[0] * self.spacings[2]

        self.pcd = o3d.geometry.PointCloud()
        self.pcd.points = o3d.utility.Vector3dVector(self.points)

        self.fiduc = rFi.ReferenceFiducials(self.center)
        self.fiduc.build()
        self.fiduc.convert()

    def register_fiducials(self):
        self.fiduc.register(self.pcd, "L", 1e-3, 1e-4)
        self.fiduc.register(self.pcd, "R", 1e-3, 1e-4)

    def get_stereotactic_origin(self):
        self.fiduc.check_parallelism(1e-4)

        origin1, origin2 = self.fiduc.define_stereotactic_space()

        self.fiduc.pcd_fiducial_L.paint_uniform_color([1, 0, 0])
        self.fiduc.pcd_fiducial_R.paint_uniform_color([0, 0, 1])

        o3d.visualization.draw_geometries([self.fiduc.pcd_fiducial_R, self.fiduc.pcd_fiducial_L, self.pcd,
                                           origin1, origin2])

        return origin1
