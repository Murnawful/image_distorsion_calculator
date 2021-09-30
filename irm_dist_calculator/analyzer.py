import open3d as o3d
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as sc
from matplotlib.offsetbox import AnchoredText


def distance(a, b):
    d = np.sqrt(((a[0] - b[0]) ** 2) + ((a[1] - b[1]) ** 2) + ((a[2] - b[2]) ** 2))
    return d


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

    def save_analysis(self, name):
        points_mean_nodes_real_grid_pcd = o3d.geometry.PointCloud()
        points_mean_nodes_real_grid_pcd.points = o3d.utility.Vector3dVector(self.points_mean_nodes_real_grid)
        points_median_nodes_real_grid_pcd = o3d.geometry.PointCloud()
        points_median_nodes_real_grid_pcd.points = o3d.utility.Vector3dVector(self.points_median_nodes_real_grid)
        o3d.io.write_point_cloud(self.data_dir + name + "_mean_nodes_real_grid.ply", points_mean_nodes_real_grid_pcd)
        o3d.io.write_point_cloud(self.data_dir + name + "_median_nodes_real_grid.ply", points_median_nodes_real_grid_pcd)

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
