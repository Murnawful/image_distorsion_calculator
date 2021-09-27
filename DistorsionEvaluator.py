import open3d as o3d
import numpy as np
import pydicom as pdcm
import os


class ReferenceGrid:
    spacing = 13e-3
    param_long = np.linspace(-100, 100, 1000) * (3 * spacing / 100)
    param_short = np.linspace(-100, 100, 1000) * (2 * spacing / 100)
    data = None
    pcd = None
    is_built = False
    pose_graph = None
    vertex = None

    def __init__(self, center):
        self.offset = center

    def generate_vertex(self):
        v = []
        for i in range(-3, 4):
            for j in range(-2, 3):
                for k in range(-2, 3):
                    v.append(np.array([i * self.spacing, j * self.spacing, k * self.spacing]))
        v = np.array(v)
        v = self.generate_offset(v)
        self.vertex = o3d.geometry.PointCloud()
        self.vertex.points = o3d.utility.Vector3dVector(v)
        return 0

    def generate_offset(self, d):
        for i in range(3):
            d[:, i] += self.offset[i]
        return d

    def build(self):
        self.data = []

        for i in range(-2, 3):
            x = self.param_long.T
            y = (np.zeros(self.param_long.shape) + i * self.spacing).T
            z = np.zeros(self.param_long.shape)
            temp = np.concatenate((x[:, None], y[:, None]), axis=1)
            temp = np.concatenate((temp, z[:, None]), axis=1)
            self.data.append(temp)
        self.data = np.concatenate(self.data)
        new_data = np.copy(self.data)
        for i in range(-2, 3):
            if i != 0:
                new_data[:, 2] = self.spacing * i
                self.data = np.concatenate((self.data, new_data), axis=0)

        new_data = []
        for i in range(-2, 3):
            x = np.zeros(self.param_short.shape).T
            y = (np.zeros(self.param_short.shape) + i * self.spacing).T
            z = self.param_short.T
            temp = np.concatenate((x[:, None], y[:, None]), axis=1)
            temp = np.concatenate((temp, z[:, None]), axis=1)
            new_data.append(temp)
        new_data = np.concatenate(new_data)
        self.data = np.concatenate((new_data, self.data), axis=0)
        for i in range(-3, 4):
            if i != 0:
                new_data[:, 0] = self.spacing * i
                self.data = np.concatenate((self.data, new_data), axis=0)

        new_data = []
        for i in range(-3, 4):
            x = (np.zeros(self.param_short.shape) + i * self.spacing).T
            y = self.param_short.T
            z = np.zeros(self.param_short.shape).T
            temp = np.concatenate((x[:, None], y[:, None]), axis=1)
            temp = np.concatenate((temp, z[:, None]), axis=1)
            new_data.append(temp)
        new_data = np.concatenate(new_data)
        self.data = np.concatenate((new_data, self.data), axis=0)
        for i in range(-2, 3):
            if i != 0:
                new_data[:, 2] = self.spacing * i
                self.data = np.concatenate((self.data, new_data), axis=0)

        self.is_built = True
        self.data = self.generate_offset(self.data)
        self.generate_vertex()
        print("Reference grid built")
        return 0

    def convert(self):
        try:
            self.pcd = o3d.geometry.PointCloud()
            self.pcd.points = o3d.utility.Vector3dVector(self.data)
            print("Conversion of grid to point cloud done")
        except RuntimeError:
            print("Error: the grid is not built. Run method build() first.")
        return 0

    def display(self, colour=None):
        if colour is None:
            colour = [0, 1, 0]
        try:
            self.pcd.paint_uniform_color(colour)

            ref_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.1, origin=[0, 0, 0])

            o3d.visualization.draw_geometries([self.pcd, ref_frame])
        except AttributeError:
            print("Error: grid should be built and converted before. Use built() then convert() methods.")
        return 0

    def save_point_cloud(self, path="", name=""):
        try:
            o3d.io.write_point_cloud(path + name + "_full.ply", self.pcd)
            o3d.io.write_point_cloud(path + name + "_vertex.ply", self.vertex)
            print("Reference grid and vertices saved as point clouds")
        except TypeError or AttributeError:
            print("Error: the point cloud does not exist. Build it and convert it first")
        return 0

    def register(self, source, max_correspondence_distance_coarse=10e-5, max_correspondence_distance_fine=1.0e-5):
        print("Starting full registration with maximum correspondence distance of " + str(
            max_correspondence_distance_fine * 1000) + " mm")
        # Providing an estimation of the normals of target
        self.pcd.estimate_normals()

        # Appending a node chosen for world transformation The vector is 4-dimensional in order to consider
        # transformation from one cloud to the other. Reader should consider both clouds as corresponding to two time
        # frames if the we see these clouds as being part of geometry acquisition with a movie recorder
        self.pose_graph = o3d.pipelines.registration.PoseGraph()
        odometry = np.identity(4)
        self.pose_graph.nodes.append(o3d.pipelines.registration.PoseGraphNode(odometry))

        # Creating ICP registration
        icp_coarse = o3d.pipelines.registration.registration_icp(source, self.pcd, max_correspondence_distance_coarse,
                                                                 np.identity(4),
                                                                 o3d.pipelines.registration.TransformationEstimationPointToPlane())
        icp_fine = o3d.pipelines.registration.registration_icp(source, self.pcd, max_correspondence_distance_fine,
                                                               icp_coarse.transformation,
                                                               o3d.pipelines.registration.TransformationEstimationPointToPlane())

        # Retaining the fine registration as it is the most precise and getting the corresponding transformation
        transformation_icp = icp_fine.transformation
        information_icp = o3d.pipelines.registration.get_information_matrix_from_point_clouds(source, self.pcd,
                                                                                              max_correspondence_distance_fine,
                                                                                              icp_fine.transformation)

        # Creating the node and edge transformation
        odometry = np.dot(transformation_icp, odometry)
        self.pose_graph.nodes.append(o3d.pipelines.registration.PoseGraphNode(np.linalg.inv(odometry)))
        self.pose_graph.edges.append(o3d.pipelines.registration.PoseGraphEdge(0,
                                                                              1,
                                                                              transformation_icp,
                                                                              information_icp,
                                                                              uncertain=False))

        # Optimizing the transformation
        option = o3d.pipelines.registration.GlobalOptimizationOption(
            max_correspondence_distance=max_correspondence_distance_fine,
            edge_prune_threshold=0.025,
            reference_node=0)
        o3d.pipelines.registration.global_optimization(
            self.pose_graph,
            o3d.pipelines.registration.GlobalOptimizationLevenbergMarquardt(),
            o3d.pipelines.registration.GlobalOptimizationConvergenceCriteria(),
            option)

        # Applying the transformation to the target
        # pcd1.transform(pose_graph.nodes[0].pose)
        self.pcd.transform(self.pose_graph.nodes[1].pose)
        self.vertex.transform(self.pose_graph.nodes[1].pose)

        print("Registration done")
        print("Transformation vector for target:")
        print(self.pose_graph.nodes[1].pose)
        return 0


class ImageGrid:
    data = None
    points = None
    pcd = None
    ds = None
    voxelSpacing_x = None
    voxelSpacing_y = None
    voxelSpacing_z = None
    hu_range = (700, 1700)
    is_loaded = False

    def __init__(self, path="", slice_number=1):
        try:
            self.ds = pdcm.dcmread(path + os.listdir(path)[0])
            self.data = self.ds.pixel_array
            self.voxelSpacing_x = self.ds.PixelSpacing[0] * 1e-3
            self.voxelSpacing_y = self.ds.PixelSpacing[1] * 1e-3
            self.voxelSpacing_z = self.ds.SliceThickness * 1e-3
            self.data = np.zeros((self.data.shape[0], self.data.shape[1], slice_number))
            i = 0
            for filename in os.listdir(path):
                if filename.endswith(".dcm") and i != slice_number:
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
            self.data[np.where(self.data < self.hu_range[0])] = 0
            self.data[np.where(self.data > self.hu_range[1])] = 0
            self.data[np.where(self.data != 0)] = 1

            new_data = np.zeros(self.data.shape)
            new_data[68:260, 150:300, 90:220] = self.data[68:260, 150:300, 90:220]
            # new_data[68:264, 150:300, 210:340] = self.data[68:264, 150:300, 210:340]

            coor = np.where(new_data == 1)
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


class Analyzer:
    pcd_source = None
    pcd_registered = None
    pcd_vertex = None
    points_source = None
    points_registered = None
    points_vertex = None

    def __init__(self, dir="/", file_source="grid.ply", file_registered="registeredGrid.ply", file_vertex="registeredGrid_vertex.ply"):
        self.pcd_source = o3d.io.read_point_cloud(dir + file_source)
        self.pcd_registered = o3d.io.read_point_cloud(dir + file_registered)
        self.pcd_vertex = o3d.io.read_point_cloud(dir + file_vertex)
        self.points_source = np.asarray(self.pcd_source.points)
        self.points_registered = np.asarray(self.pcd_registered.points)
        self.points_vertex = np.asarray(self.pcd_vertex.points)

    def distance(self, a, b):
        d = np.sqrt(((a[0] - b[0]) ** 2) + ((a[1] - b[1]) ** 2) + ((a[2] - b[2]) ** 2))
        return d

    def string2array(self, s):
        s = s.split(" ")
        s[0] = s[0][1:]
        s[-1] = s[-1][:-1]
        s = [float(r) for r in s if r != '']
        return s