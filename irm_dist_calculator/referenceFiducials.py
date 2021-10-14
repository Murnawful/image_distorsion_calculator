import numpy as np
import open3d as o3d
import pyransac3d as p3d
import matplotlib.pyplot as plt


def norm(a):
    return np.sqrt(np.square(a[0]) + np.square(a[1]) + np.square(a[2]))


class ReferenceFiducials:
    offset_x = None
    offset_y = None
    offset_z = None
    data_fiducial_R = None
    data_fiducial_L = None
    pcd_fiducial_R = None
    pcd_fiducial_L = None
    pose_graph = None
    mean_vector = None

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

        x3 = np.zeros(t.shape) + self.offset_x
        y3 = np.copy(t) + self.offset_y
        z3 = np.zeros(t.shape) + self.offset_z

        x_line = np.concatenate((x, x1, x2, x3))
        y_line = np.concatenate((y, y1, y2, y3))
        z_line = np.concatenate((z, z1, z2, z3))

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

    def register(self, source, l_or_r="L", max_correspondence_distance_coarse=10e-5,
                 max_correspondence_distance_fine=1.0e-5):
        print("Starting full registration for " + l_or_r + " with maximum correspondence distance of " +
              str(round(max_correspondence_distance_fine * 1000, 6)) + " mm")
        # Providing an estimation of the normals of target

        if l_or_r == "L":
            pcd = self.pcd_fiducial_L
        else:
            pcd = self.pcd_fiducial_R
        pcd.estimate_normals()

        # Appending a node chosen for world transformation The vector is 4-dimensional in order to consider
        # transformation from one cloud to the other. Reader should consider both clouds as corresponding to two time
        # frames if the we see these clouds as being part of geometry acquisition with a movie recorder
        self.pose_graph = o3d.pipelines.registration.PoseGraph()
        odometry = np.identity(4)
        self.pose_graph.nodes.append(o3d.pipelines.registration.PoseGraphNode(odometry))

        # Creating ICP registration
        icp_coarse = o3d.pipelines.registration.registration_icp(source, pcd, max_correspondence_distance_coarse,
                                                                 np.identity(4),
                                                                 o3d.pipelines.registration.TransformationEstimationPointToPlane())
        icp_fine = o3d.pipelines.registration.registration_icp(source, pcd, max_correspondence_distance_fine,
                                                               icp_coarse.transformation,
                                                               o3d.pipelines.registration.TransformationEstimationPointToPlane())

        # Retaining the fine registration as it is the most precise and getting the corresponding transformation
        transformation_icp = icp_fine.transformation
        information_icp = o3d.pipelines.registration.get_information_matrix_from_point_clouds(source, pcd,
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
        if l_or_r == "L":
            self.pcd_fiducial_L.transform(self.pose_graph.nodes[1].pose)
        else:
            self.pcd_fiducial_R.transform(self.pose_graph.nodes[1].pose)

        print("Registration done")

    def check_parallelism(self, tol):
        plane_L, inliers = self.pcd_fiducial_L.segment_plane(distance_threshold=.4, ransac_n=3, num_iterations=1000)
        plane_R, inliers = self.pcd_fiducial_R.segment_plane(distance_threshold=.4, ransac_n=3, num_iterations=1000)

        normal_L = plane_L[:3]
        normal_R = plane_R[:3]

        self.mean_vector = (normal_R + normal_L) / 2

        scalar = np.dot(normal_L, normal_R)

        print("Angle between fiducials: " + str(np.round(180 * np.arccos(scalar) / np.pi, 2)) + " degrees")

        if abs(scalar - 1) < tol:
            return True
        else:
            return False

    def define_stereotactic_space(self, size=0.05):
        lower_z = max(np.amax(self.data_fiducial_R[:, 2]), np.amax(self.data_fiducial_L[:, 2])) + 15e-3
        lower_x = max(np.amax(self.data_fiducial_R[:, 0]), np.amax(self.data_fiducial_L[:, 0]))
        lower_y = max(np.amax(self.data_fiducial_R[:, 1]), np.amax(self.data_fiducial_L[:, 1]))
        origin_x = lower_x + 5e-3
        origin_y = lower_y + 40e-3
        origin_z = lower_z - 200e-3

        ori = [origin_x, origin_y, origin_z]
        ori1 = np.copy(ori)
        for i in range(len(ori)):
            ori1[i] += .1

        ref_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=size, origin=ori)
        ref_frame1 = o3d.geometry.TriangleMesh.create_coordinate_frame(size=size, origin=ori1)

        R = ref_frame.get_rotation_matrix_from_xyz((0, 0, np.pi))
        ref_frame.rotate(R, center=ori)
        ref_frame1.rotate(R, center=ori)
        return ref_frame, ref_frame1
