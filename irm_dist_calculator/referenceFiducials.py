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
    pose_graph = None

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

    def register(self, source, l_or_r="L", max_correspondence_distance_coarse=10e-5,
                 max_correspondence_distance_fine=1.0e-5):
        print("Starting full registration with maximum correspondence distance of " + str(
            max_correspondence_distance_fine * 1000) + " mm")
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
        pcd.transform(self.pose_graph.nodes[1].pose)

        print("Registration done")
        print("Transformation vector for target:")
        print(self.pose_graph.nodes[1].pose)
        return 0