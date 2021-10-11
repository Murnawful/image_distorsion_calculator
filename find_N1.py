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
print(data.shape)

spacing_x = ds.PixelSpacing[0] * 1e-3
spacing_y = ds.PixelSpacing[1] * 1e-3
spacing_z = ds.SliceThickness * 1e-3

data[data < 100] = 0
data[data != 0] = 1

r = 50
data[:, :, r:data.shape[1] - r] = 0
data[:, :45, :] = 0
data[:45, :, :] = 0

plt.imshow(data[int(data.shape[0] / 2), :, :])
plt.show()

coor = np.where(data != 0)
points = np.zeros((coor[0].shape[0], 3))
points[:, 0] = coor[2] * spacing_x
points[:, 1] = coor[1] * spacing_y
points[:, 2] = coor[0] * spacing_z
pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(points)

max_x = np.amax(points[:, 0])
min_x = np.amin(points[:, 0])
max_y = np.amax(points[:, 1])
min_y = np.amin(points[:, 1])
max_z = np.amax(points[:, 2])
min_z = np.amin(points[:, 2])

all_inliers = []
all_slopes = []
all_intercept = []
all_lines = []
fiducial1 = []
fiducial2 = []

for i in range(8):
    line_fitting = pr3d.Line().fit(points, 2e-3, 1000)
    all_slopes.append(line_fitting[0])
    all_intercept.append(line_fitting[1])
    inliers_index = line_fitting[2]
    inliers_points = points[inliers_index, :]
    points = np.delete(points, inliers_index, axis=0)
    inliers_pcd = o3d.geometry.PointCloud()
    inliers_pcd.points = o3d.utility.Vector3dVector(inliers_points)
    all_inliers.append(inliers_pcd)

    t = np.linspace(-1e-1, 2e-1, 1000)
    x = all_slopes[i][0] * t + all_intercept[i][0]
    y = all_slopes[i][1] * t + all_intercept[i][1]
    z = all_slopes[i][2] * t + all_intercept[i][2]

    line_points = np.zeros((t.shape[0], 3))
    line_points[:, 0] = x
    line_points[:, 1] = y
    line_points[:, 2] = z

    line_points = line_points[line_points[:, 1] < max_y]
    line_points = line_points[line_points[:, 1] > min_y]
    line_points = line_points[line_points[:, 2] < max_z]
    line_points = line_points[line_points[:, 2] > min_z]

    line_pcd = o3d.geometry.PointCloud()
    line_pcd.points = o3d.utility.Vector3dVector(line_points)

    if abs(line_points[0, 0] - max_x) > abs(line_points[0, 0] - min_x):
        fiducial1.append(line_pcd)
    else:
        fiducial2.append(line_pcd)
    all_lines.append(line_pcd)

all_slopes = np.array(all_slopes)
all_intercept = np.array(all_intercept)
fiducial1 = np.array(fiducial1)
fiducial2 = np.array(fiducial2)

print(fiducial1.shape)
print(fiducial2.shape)

pcd.paint_uniform_color([1, 0, 0])

ref_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.05, origin=[0, 0, 0])

o3d.visualization.draw_geometries([pcd,
                                   fiducial1[0],
                                   fiducial1[1],
                                   fiducial1[2],
                                   fiducial1[3],
                                   ref_frame])
