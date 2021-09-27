import open3d as o3d
import numpy as np


def distance(a, b):
    d = np.sqrt(((a[0] - b[0]) ** 2) + ((a[1] - b[1]) ** 2) + ((a[2] - b[2]) ** 2))
    return d


"""center_theo = np.array([[0, 0, 0]])
center_theo_pcd = o3d.geometry.PointCloud()
center_theo_pcd.points = o3d.utility.Vector3dVector(center_theo)
center_theo_pcd.paint_uniform_color([1, 0, 0])

t = np.linspace(-10, 10, 1000)
x = 1.05 + 2 * t
y = 2.01 - t
z = -3 + 3.6 * t
line1 = np.zeros((t.shape[0], 3))
line1[:, 0] = x
line1[:, 1] = y
line1[:, 2] = z

x1 = 1 - 4 * t
y1 = 2 + 2.05 * t
z1 = -2.99 + t
line2 = np.zeros((t.shape[0], 3))
line2[:, 0] = x1
line2[:, 1] = y1
line2[:, 2] = z1

x2 = 1 + 3 * t
y2 = 2 + 12 * t
z2 = -3.05 + 6 * t
line3 = np.zeros((t.shape[0], 3))
line3[:, 0] = x2
line3[:, 1] = y2
line3[:, 2] = z2

lines = np.concatenate((line1, line2, line3))

line1_pcd = o3d.geometry.PointCloud()
line1_pcd.points = o3d.utility.Vector3dVector(lines)
line1_pcd.paint_uniform_color([0, 1, 0])"""

center_theo_pcd = o3d.io.read_point_cloud("../data/registeredGrid_vertex.ply")
center_theo = np.asarray(center_theo_pcd.points)

lines_pcd = o3d.io.read_point_cloud("../data/grid.ply")

center_theo_pcd.paint_uniform_color([1, 0, 0])
lines_pcd.paint_uniform_color([0, 1, 0])

ref_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.05, origin=[0, 0, 0])

o3d.visualization.draw_geometries([center_theo_pcd, ref_frame, lines_pcd])

"""close_points = []
for i in range(len(lines)):
    if distance(center_theo[0], lines[i, :]) < 4:
        close_points.append(lines[i, :])
close_points = np.array(close_points)
close_points_pcd = o3d.geometry.PointCloud()
close_points_pcd.points = o3d.utility.Vector3dVector(close_points)
close_points_pcd.paint_uniform_color([0, 0, 1])

mean_x = np.mean(close_points[:, 0])
mean_y = np.mean(close_points[:, 1])
mean_z = np.mean(close_points[:, 2])
median_x = np.median(close_points[:, 0])
median_y = np.median(close_points[:, 1])
median_z = np.median(close_points[:, 2])

mean_center = np.array([[mean_x, mean_y, mean_z]])
mean_center_pcd = o3d.geometry.PointCloud()
mean_center_pcd.points = o3d.utility.Vector3dVector(mean_center)
mean_center_pcd.paint_uniform_color([1, 0, 0])

median_center = np.array([[median_x, median_y, median_z]])
median_center_pcd = o3d.geometry.PointCloud()
median_center_pcd.points = o3d.utility.Vector3dVector(median_center)
median_center_pcd.paint_uniform_color([0, 1, 0])

density = np.zeros(len(close_points))
for i in range(len(close_points)):
    for j in range(len(close_points)):
        if distance(close_points[i, :], close_points[j, :]) < .2:
            density[i] += 1

index = np.where(density == np.amax(density))[0]
#print(density)
#good_candidates = []
#for i in index:
#    good_candidates.append(close_points[i])
good_candidates = close_points[index]
# good_candidates = np.array(good_candidates)
good_candidates_mean = np.array(
    [[np.mean(good_candidates[:, 0]), np.mean(good_candidates[:, 1]), np.mean(good_candidates[:, 2])]])
good_candidates_median = np.array(
    [[np.median(good_candidates[:, 0]), np.median(good_candidates[:, 1]), np.median(good_candidates[:, 2])]])
good_candidates_mean_pcd = o3d.geometry.PointCloud()
good_candidates_mean_pcd.points = o3d.utility.Vector3dVector(good_candidates_mean)
good_candidates_mean_pcd.paint_uniform_color([1, 0, 0])
good_candidates_median_pcd = o3d.geometry.PointCloud()
good_candidates_median_pcd.points = o3d.utility.Vector3dVector(good_candidates_median)
good_candidates_median_pcd.paint_uniform_color([0, 0, 1])
ref_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.05, origin=[0, 0, 0])
o3d.visualization.draw_geometries([center_theo_pcd, good_candidates_mean_pcd, good_candidates_median_pcd, close_points_pcd])"""
