import matplotlib.pyplot as plt
import numpy as np
import pydicom as pdcm
import open3d as o3d
import pyransac3d as pr3d


def distance(a, b):
    d = np.sqrt(((a[0] - b[0]) ** 2) + ((a[1] - b[1]) ** 2) + ((a[2] - b[2]) ** 2))
    return d


path = "../../im_DICOM/complete_IRM_CBCT/3DT1_160slices_fiduc/"
slice_number = 160

data = []
for i in range(slice_number):
    if i < 10:
        name = path + "IMG000000000" + str(i) + ".dcm"
    elif i < 100:
        name = path + "IMG00000000" + str(i) + ".dcm"
    else:
        name = path + "IMG0000000" + str(i) + ".dcm"
    ds = pdcm.dcmread(name)
    a = ds.pixel_array
    data.append(a)
data = np.array(data)

spacing_x = ds.PixelSpacing[0] * 1e-3
spacing_y = ds.PixelSpacing[1] * 1e-3
spacing_z = ds.SliceThickness * 1e-3

data[data < 100] = 0
data[data != 0] = 1

r = 50
data[:, :, r:data.shape[1] - r] = 0
data[:, :45, :] = 0
data[:45, :, :] = 0

coor = np.where(data != 0)
points = np.zeros((coor[0].shape[0], 3))
points[:, 0] = coor[2] * spacing_x
points[:, 1] = coor[1] * spacing_y
points[:, 2] = coor[0] * spacing_z
pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(points)

offset_x = 5e-2
offset_y = 6e-2
offset_z = 0

t = np.linspace(0, 120e-3, 10000)
x = np.zeros(t.shape) + offset_x
y = np.zeros(t.shape) + offset_y
z = np.copy(t) + offset_z

x1 = np.zeros(t.shape) + offset_x
y1 = np.ones(t.shape) * 120e-3 + offset_y
z1 = np.copy(t) + offset_z

x2 = np.zeros(t.shape) + offset_x
y2 = (-1) * np.copy(t) + 2 * 60e-3 + offset_y
z2 = np.copy(t) + offset_z

x_line = np.concatenate((x, x1, x2))
y_line = np.concatenate((y, y1, y2))
z_line = np.concatenate((z, z1, z2))

line_points1 = np.zeros((x_line.shape[0], 3))
line_points1[:, 0] = x_line
line_points1[:, 1] = y_line
line_points1[:, 2] = z_line

line_points2 = np.zeros((x_line.shape[0], 3))
line_points2[:, 0] = x_line + 190e-3
line_points2[:, 1] = y_line
line_points2[:, 2] = z_line

pcd_fiducials_L = o3d.geometry.PointCloud()
pcd_fiducials_L.points = o3d.utility.Vector3dVector(line_points1)
pcd_fiducials_R = o3d.geometry.PointCloud()
pcd_fiducials_R.points = o3d.utility.Vector3dVector(line_points2)

pcd_fiducials_R.paint_uniform_color([1, 0, 0])
pcd_fiducials_L.paint_uniform_color([0, 0, 1])

ref_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.05, origin=[0, 0, 0])

o3d.visualization.draw_geometries([pcd, ref_frame, pcd_fiducials_R, pcd_fiducials_L])
