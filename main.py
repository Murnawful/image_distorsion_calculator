import DistorsionEvaluator as dist
import open3d as o3d
import numpy as np
from numpy import mean
from numpy import median
from numpy import array
from numpy import where
from numpy import amax
import matplotlib.pyplot as plt
import scipy.stats as sc
from matplotlib.offsetbox import AnchoredText
from irm_dist_calculator import analyzer as a

"""grid = dist.ReferenceGrid(center=(0.08, 0.11, 0.145))
grid.build()
grid.convert()
# grid.display([1, 0, 0])

source = dist.ImageGrid("../../im_DICOM/CBCT2/", 448)
source.convert()
source.save_point_cloud("../data/", "grid")

grid.register(source.pcd, 1e-3, 1e-7)
grid.save_point_cloud("../data/", "registeredGrid")

grid.pcd.paint_uniform_color([1, 0, 0])
source.pcd.paint_uniform_color([0, 0, 1])
ref_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.05, origin=[0, 0, 0])

o3d.visualization.draw_geometries([source.pcd, grid.pcd, ref_frame])"""

analyser = a.Analyzer("../data/")
analyser.launch_analysis()
analyser.save_analysis()

# BACKUP
"""pcd_source = o3d.io.read_point_cloud("../data/grid.ply")
pcd_registered = o3d.io.read_point_cloud("../data/registeredGrid.ply")
pcd_vertex = o3d.io.read_point_cloud("../data/registeredGrid_vertex.ply")

points_source = np.asarray(pcd_source.points)
points_registered = np.asarray(pcd_registered.points)
points_vertex = np.asarray(pcd_vertex.points)

ref_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.05, origin=[0, 0, 0])
pcd_vertex.paint_uniform_color([0, 0, 1])
pcd_source.paint_uniform_color([1, 0, 0])
pcd_registered.paint_uniform_color([0, 1, 0])


def distance(a, b):
    d = np.sqrt(((a[0] - b[0]) ** 2) + ((a[1] - b[1]) ** 2) + ((a[2] - b[2]) ** 2))
    return d


def string2array(s):
    s = s.split(" ")
    s[0] = s[0][1:]
    s[-1] = s[-1][:-1]
    s = [float(r) for r in s if r != '']
    return s


points_close_to_vertices = []
points_mean_nodes_real_grid = []
points_median_nodes_real_grid = []
for i in range(points_vertex.shape[0]):
    print("Treating node number " + str(i + 1) + " out of " + str(points_vertex.shape[0]))
    points_close_to_vertices = [points_source[j, :] for j in range(points_source.shape[0]) if
                                distance(points_vertex[i, :], points_source[j, :]) < 2e-3]
    points_close_to_vertices = array(points_close_to_vertices)
    density = np.zeros(len(points_close_to_vertices))
    for k in range(len(points_close_to_vertices)):
        for j in range(len(points_close_to_vertices)):
            if distance(points_close_to_vertices[k, :], points_close_to_vertices[j, :]) < 7e-4:
                density[k] += 1
    good_candidates = points_close_to_vertices[where(density == amax(density))[0]]
    good_candidates_mean = array([mean(good_candidates[:, 0]),
                                  mean(good_candidates[:, 1]),
                                  mean(good_candidates[:, 2])])
    good_candidates_median = array([median(good_candidates[:, 0]),
                                    median(good_candidates[:, 1]),
                                    median(good_candidates[:, 2])])
    points_mean_nodes_real_grid.append(good_candidates_mean)
    points_median_nodes_real_grid.append(good_candidates_median)
points_mean_nodes_real_grid = np.array(points_mean_nodes_real_grid)
points_median_nodes_real_grid = np.array(points_median_nodes_real_grid)

points_mean_nodes_real_grid_pcd = o3d.geometry.PointCloud()
points_mean_nodes_real_grid_pcd.points = o3d.utility.Vector3dVector(points_mean_nodes_real_grid)
points_median_nodes_real_grid_pcd = o3d.geometry.PointCloud()
points_median_nodes_real_grid_pcd.points = o3d.utility.Vector3dVector(points_median_nodes_real_grid)
o3d.io.write_point_cloud("../data/mean_nodes_real_grid.ply", points_mean_nodes_real_grid_pcd)
o3d.io.write_point_cloud("../data/median_nodes_real_grid.ply", points_median_nodes_real_grid_pcd)

diff_mean = (points_vertex - points_mean_nodes_real_grid) * 1000
diff_median = (points_vertex - points_median_nodes_real_grid) * 1000

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

ax[0, 0].add_artist(AnchoredText('$\\mu = $' + str(round(mu_mean_x, 2)) + '\n$\\sigma = $' + str(round(sigma_mean_x, 2)),
                                 loc="upper right"))
ax[0, 1].add_artist(AnchoredText('$\\mu = $' + str(round(mu_mean_y, 2)) + '\n$\\sigma = $' + str(round(sigma_mean_y, 2)),
                                 loc="upper right"))
ax[0, 2].add_artist(AnchoredText('$\\mu = $' + str(round(mu_mean_z, 2)) + '\n$\\sigma = $' + str(round(sigma_mean_z, 2)),
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

ax[1, 0].add_artist(AnchoredText('$\\mu = $' + str(round(mu_median_x, 2)) + '\n$\\sigma = $' + str(round(sigma_median_x, 2)),
                                 loc="upper right"))
ax[1, 1].add_artist(AnchoredText('$\\mu = $' + str(round(mu_median_y, 2)) + '\n$\\sigma = $' + str(round(sigma_median_y, 2)),
                                 loc="upper right"))
ax[1, 2].add_artist(AnchoredText('$\\mu = $' + str(round(mu_median_z, 2)) + '\n$\\sigma = $' + str(round(sigma_median_z, 2)),
                                 loc="upper right"))

plt.tight_layout()
plt.show()
"""
"""pcd_close_to_vertices = o3d.geometry.PointCloud()
pcd_close_to_vertices.points = o3d.utility.Vector3dVector(points_close_to_vertices)
# o3d.io.write_point_cloud("../data/sourceCloud_closeToVertices.ply", pcd_close_to_vertices)
pcd_close_to_vertices.paint_uniform_color([1, 0, 0])

o3d.visualization.draw_geometries([pcd_vertex, ref_frame, pcd_close_to_vertices])"""

####### BACKUP #######
"""points_close_to_vertices = []
correspondence = {}
for i in range(points_vertex.shape[0]):
    correspondence[str(points_vertex[i, :])] = []
    for j in range(points_source.shape[0]):
        if distance(points_vertex[i, :], points_source[j, :]) < 2e-3:
            correspondence[str(points_vertex[i, :])].append(points_source[j, :])
            points_close_to_vertices.append(points_source[j, :])
points_close_to_vertices = np.array(points_close_to_vertices)

points_mean_nodes_real_grid = []
points_median_nodes_real_grid = []
points_nodes_theo_grid = []
for k in correspondence:
    if correspondence[k]:
        key = string2array(k)
        points = np.array(correspondence[k])
        points_nodes_theo_grid.append(key)
        points_mean_nodes_real_grid.append([np.mean(points[:, 0]), np.mean(points[:, 1]), np.mean(points[:, 2])])
        points_median_nodes_real_grid.append([np.median(points[:, 0]), np.median(points[:, 1]), np.median(points[:, 2])])
points_nodes_theo_grid = np.array(points_nodes_theo_grid) * 1000
points_mean_nodes_real_grid = np.array(points_mean_nodes_real_grid) * 1000
points_median_nodes_real_grid = np.array(points_median_nodes_real_grid) * 1000

diff_mean = points_nodes_theo_grid - points_mean_nodes_real_grid
diff_median = points_nodes_theo_grid - points_median_nodes_real_grid

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

plt.show()"""
