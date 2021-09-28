import open3d as o3d
import numpy as np
import pydicom as pdcm
import os
import matplotlib.pyplot as plt
import scipy.stats as sc
from matplotlib.offsetbox import AnchoredText


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


def distance(a, b):
    d = np.sqrt(((a[0] - b[0]) ** 2) + ((a[1] - b[1]) ** 2) + ((a[2] - b[2]) ** 2))
    return d


def string2array(s):
    s = s.split(" ")
    s[0] = s[0][1:]
    s[-1] = s[-1][:-1]
    s = [float(r) for r in s if r != '']
    return s


class Analyzer:
    pcd_source = None
    pcd_registered = None
    pcd_vertex = None
    points_source = None
    points_registered = None
    points_vertex = None
    data_dir = None

    points_close_to_vertices = []
    points_mean_nodes_real_grid = []
    points_median_nodes_real_grid = []

    def __init__(self, dir="/", file_source="grid.ply", file_registered="registeredGrid.ply",
                 file_vertex="registeredGrid_vertex.ply"):
        self.data_dir = dir
        self.pcd_source = o3d.io.read_point_cloud(dir + file_source)
        self.pcd_registered = o3d.io.read_point_cloud(dir + file_registered)
        self.pcd_vertex = o3d.io.read_point_cloud(dir + file_vertex)
        self.points_source = np.asarray(self.pcd_source.points)
        self.points_registered = np.asarray(self.pcd_registered.points)
        self.points_vertex = np.asarray(self.pcd_vertex.points)

    def launch_analysis(self):
        for i in range(self.points_vertex.shape[0]):
            print("Treating node number " + str(i + 1) + " out of " + str(self.points_vertex.shape[0]))
            points_close_to_vertices = [self.points_source[j, :] for j in range(self.points_source.shape[0]) if
                                        distance(self.points_vertex[i, :], self.points_source[j, :]) < 2e-3]
            points_close_to_vertices = np.array(points_close_to_vertices)
            density = np.zeros(len(points_close_to_vertices))
            for k in range(len(points_close_to_vertices)):
                for j in range(len(points_close_to_vertices)):
                    if distance(points_close_to_vertices[k, :], points_close_to_vertices[j, :]) < 7e-4:
                        density[k] += 1
            good_candidates = points_close_to_vertices[np.where(density == np.amax(density))[0]]
            good_candidates_mean = np.array([np.mean(good_candidates[:, 0]),
                                             np.mean(good_candidates[:, 1]),
                                             np.mean(good_candidates[:, 2])])
            good_candidates_median = np.array([np.median(good_candidates[:, 0]),
                                               np.median(good_candidates[:, 1]),
                                               np.median(good_candidates[:, 2])])
            self.points_mean_nodes_real_grid.append(good_candidates_mean)
            self.points_median_nodes_real_grid.append(good_candidates_median)
        self.points_mean_nodes_real_grid = np.array(self.points_mean_nodes_real_grid)
        self.points_median_nodes_real_grid = np.array(self.points_median_nodes_real_grid)

    def save_analysis(self):
        points_mean_nodes_real_grid_pcd = o3d.geometry.PointCloud()
        points_mean_nodes_real_grid_pcd.points = o3d.utility.Vector3dVector(self.points_mean_nodes_real_grid)
        points_median_nodes_real_grid_pcd = o3d.geometry.PointCloud()
        points_median_nodes_real_grid_pcd.points = o3d.utility.Vector3dVector(self.points_median_nodes_real_grid)
        o3d.io.write_point_cloud(self.data_dir + "mean_nodes_real_grid.ply", points_mean_nodes_real_grid_pcd)
        o3d.io.write_point_cloud(self.data_dir + "median_nodes_real_grid.ply", points_median_nodes_real_grid_pcd)

    def display_results(self):
        diff_mean = (self.points_vertex - self.points_mean_nodes_real_grid) * 1000
        diff_median = (self.points_vertex - self.points_median_nodes_real_grid) * 1000

        fig, ax = plt.subplots(2, 3)
        bin_number = 70
        _, bins_mean_x, _ = ax[0, 0].hist(diff_mean[:, 0], bins=bin_number, color='b')
        ax[0, 0].set_xlabel("Deviation [mm]")
        ax[0, 0].set_title("Mean deviation along $x$")
        ax[0, 0].grid(b=True, which='both')
        ax[0, 0].minorticks_on()
        ax[0, 0].tick_params(labelcolor='b')
        _, bins_mean_y, _ = ax[0, 1].hist(diff_mean[:, 1], bins=bin_number, color='b')
        ax[0, 1].set_xlabel("Deviation [mm]")
        ax[0, 1].set_title("Mean deviation along $y$")
        ax[0, 1].grid(b=True, which='both')
        ax[0, 1].minorticks_on()
        ax[0, 1].tick_params(labelcolor='b')
        _, bins_mean_z, _ = ax[0, 2].hist(diff_mean[:, 2], bins=bin_number, color='b')
        ax[0, 2].set_xlabel("Deviation [mm]")
        ax[0, 2].set_title("Mean deviation along $z$")
        ax[0, 2].grid(b=True, which='both')
        ax[0, 2].minorticks_on()
        ax[0, 2].tick_params(labelcolor='b')
        _, bins_median_x, _ = ax[1, 0].hist(diff_median[:, 0], bins=bin_number, color='b')
        ax[1, 0].set_xlabel("Deviation [mm]")
        ax[1, 0].set_title("Median deviation along $x$")
        ax[1, 0].grid(b=True, which='both')
        ax[1, 0].minorticks_on()
        ax[1, 0].tick_params(labelcolor='b')
        _, bins_median_y, _ = ax[1, 1].hist(diff_median[:, 1], bins=bin_number, color='b')
        ax[1, 1].set_xlabel("Deviation [mm]")
        ax[1, 1].set_title("Median deviation along $y$")
        ax[1, 1].grid(b=True, which='both')
        ax[1, 1].minorticks_on()
        ax[1, 1].tick_params(labelcolor='b')
        _, bins_median_z, _ = ax[1, 2].hist(diff_median[:, 2], bins=bin_number, color='b')
        ax[1, 2].set_xlabel("Deviation [mm]")
        ax[1, 2].set_title("Median deviation along $z$")
        ax[1, 2].grid(b=True, which='both')
        ax[1, 2].minorticks_on()
        ax[1, 2].tick_params(labelcolor='b')

        mu_mean_x, sigma_mean_x = sc.norm.fit(diff_mean[:, 0])
        gauss_mean_x = sc.norm.pdf(bins_mean_x, mu_mean_x, sigma_mean_x)
        ax001 = ax[0, 0].twinx()
        ax001.plot(bins_mean_x, gauss_mean_x, color="r")
        ax001.tick_params(axis='y', labelcolor="r")
        mu_mean_y, sigma_mean_y = sc.norm.fit(diff_mean[:, 1])
        gauss_mean_y = sc.norm.pdf(bins_mean_y, mu_mean_y, sigma_mean_y)
        ax011 = ax[0, 1].twinx()
        ax011.plot(bins_mean_y, gauss_mean_y, color="r")
        ax011.tick_params(axis='y', labelcolor="r")
        mu_mean_z, sigma_mean_z = sc.norm.fit(diff_mean[:, 2])
        gauss_mean_z = sc.norm.pdf(bins_mean_z, mu_mean_z, sigma_mean_x)
        ax021 = ax[0, 2].twinx()
        ax021.plot(bins_mean_z, gauss_mean_z, color="r")
        ax021.tick_params(axis='y', labelcolor="r")

        ax[0, 0].add_artist(
            AnchoredText('$\\mu = $' + str(round(mu_mean_x, 2)) + '\n$\\sigma = $' + str(round(sigma_mean_x, 2)),
                         loc="upper right"))
        ax[0, 1].add_artist(
            AnchoredText('$\\mu = $' + str(round(mu_mean_y, 2)) + '\n$\\sigma = $' + str(round(sigma_mean_y, 2)),
                         loc="upper right"))
        ax[0, 2].add_artist(
            AnchoredText('$\\mu = $' + str(round(mu_mean_z, 2)) + '\n$\\sigma = $' + str(round(sigma_mean_z, 2)),
                         loc="upper right"))

        mu_median_x, sigma_median_x = sc.norm.fit(diff_median[:, 0])
        gauss_median_x = sc.norm.pdf(bins_median_x, mu_median_x, sigma_median_x)
        ax101 = ax[1, 0].twinx()
        ax101.plot(bins_median_x, gauss_median_x, color="r")
        ax101.tick_params(axis='y', labelcolor="r")
        mu_median_y, sigma_median_y = sc.norm.fit(diff_median[:, 1])
        gauss_median_y = sc.norm.pdf(bins_median_y, mu_median_y, sigma_median_y)
        ax111 = ax[1, 1].twinx()
        ax111.plot(bins_median_y, gauss_median_y, color="r")
        ax111.tick_params(axis='y', labelcolor="r")
        mu_median_z, sigma_median_z = sc.norm.fit(diff_median[:, 2])
        gauss_median_z = sc.norm.pdf(bins_median_z, mu_median_z, sigma_median_x)
        ax121 = ax[1, 2].twinx()
        ax121.plot(bins_median_z, gauss_median_z, color="r")
        ax121.tick_params(axis='y', labelcolor="r")

        ax[1, 0].add_artist(
            AnchoredText('$\\mu = $' + str(round(mu_median_x, 2)) + '\n$\\sigma = $' + str(round(sigma_median_x, 2)),
                         loc="upper right"))
        ax[1, 1].add_artist(
            AnchoredText('$\\mu = $' + str(round(mu_median_y, 2)) + '\n$\\sigma = $' + str(round(sigma_median_y, 2)),
                         loc="upper right"))
        ax[1, 2].add_artist(
            AnchoredText('$\\mu = $' + str(round(mu_median_z, 2)) + '\n$\\sigma = $' + str(round(sigma_median_z, 2)),
                         loc="upper right"))

        plt.tight_layout()
        plt.show()
