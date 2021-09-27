import numpy as np
import pydicom as pdcm
import open3d as o3d
import os
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.colors import LinearSegmentedColormap

path = "../../im_DICOM/CBCT2/"

ds = pdcm.dcmread(path + "IMG0000000000.dcm")

arr = [pdcm.dcmread(path + filename).pixel_array for filename in os.listdir(path) if filename[0] == "I"]
arr = np.array(arr)

center_theo_pcd = o3d.io.read_point_cloud("../data/registeredGrid_vertex.ply")
mean_nodes_pcd = o3d.io.read_point_cloud("../data/mean_nodes_real_grid.ply")
median_nodes_pcd = o3d.io.read_point_cloud("../data/median_nodes_real_grid.ply")
ref_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.05, origin=[0, 0, 0])

# o3d.visualization.draw_geometries([center_theo_pcd, ref_frame])

center_theo = np.asarray(center_theo_pcd.points)
x = (center_theo[:, 0] / 5e-4).astype("int64")
y = (center_theo[:, 1] / 5e-4).astype("int64")
z = -(center_theo[:, 2] / 5e-4).astype("int64") + arr.shape[0]

mean_nodes = np.asarray(mean_nodes_pcd.points)
x1 = (mean_nodes[:, 0] / 5e-4).astype("int64")
y1 = (mean_nodes[:, 1] / 5e-4).astype("int64")
z1 = -(mean_nodes[:, 2] / 5e-4).astype("int64") + arr.shape[0]

median_nodes = np.asarray(median_nodes_pcd.points)
x2 = (median_nodes[:, 0] / 5e-4).astype("int64")
y2 = (median_nodes[:, 1] / 5e-4).astype("int64")
z2 = -(median_nodes[:, 2] / 5e-4).astype("int64") + arr.shape[0]

where_good = (x, y, z)
where_good1 = (x1, y1, z1)
where_good2 = (x2, y2, z2)
new_arr = np.zeros(arr.shape)
new_arr[where_good] = 2000
new_arr1 = np.zeros(arr.shape)
new_arr1[where_good1] = 2000
new_arr2 = np.zeros(arr.shape)
new_arr2[where_good2] = 2000

fig = plt.figure(figsize=(10, 10))
ax = plt.axes()

ncolors = 256
color_array = plt.get_cmap('tab10')(range(ncolors))
color_array[:, -1] = np.linspace(0, 1, ncolors)
map_object = LinearSegmentedColormap.from_list(name='tab10_alpha', colors=color_array)
color_array1 = plt.get_cmap('jet')(range(ncolors))
color_array1[:, -1] = np.linspace(0, 1, ncolors)
map_object1 = LinearSegmentedColormap.from_list(name='jet_alpha', colors=color_array1)
color_array2 = plt.get_cmap('brg')(range(ncolors))
color_array2[:, -1] = np.linspace(0, 1, ncolors)
map_object2 = LinearSegmentedColormap.from_list(name='brg_alpha', colors=color_array2)

plt.register_cmap(cmap=map_object)
plt.register_cmap(cmap=map_object1)
plt.register_cmap(cmap=map_object2)

# 99 -> 209
frame = 155

plt.imshow(arr[frame, :, :], animated=True, cmap='bone', alpha=.2)
# Nodes théoriques
plt.imshow(new_arr[:, :, frame], animated=True, cmap='tab10_alpha')
# Nodes moyens
plt.imshow(new_arr1[:, :, frame], animated=True, cmap='jet_alpha')
# Nodes médians
plt.imshow(new_arr2[:, :, frame], animated=True, cmap='brg_alpha')
plt.xlim(162, 287)
plt.ylim(252, 66)
# plt.colorbar(label="HU", shrink=0.75)
plt.tight_layout()

plt.show()
