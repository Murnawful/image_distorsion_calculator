import matplotlib.pyplot as plt
import numpy as np
import pydicom as pdcm
import open3d as o3d
import pyransac3d as pr3d

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

data[:, :, 50:210] = 0

fig = plt.figure(figsize=(10, 7))
ax = plt.axes()
im = plt.imshow(data[0, :, :], animated=True, cmap='bone')
plt.colorbar(shrink=0.75)
plt.tight_layout()


def init():
    ds = pdcm.dcmread(path + "IMG0000000010.dcm")
    im.set_data(ds.pixel_array)
    return im,


# animation function.  This is called sequentially
def animate(i):
    im.set_array(data[i, :, :])
    return im,


# anim = animation.FuncAnimation(fig, animate, init_func=init, frames=slice_number, interval=100, blit=True)

coor = np.where(data != 0)
points = np.zeros((coor[0].shape[0], 3))
points[:, 0] = coor[2] * spacing_x
points[:, 1] = coor[1] * spacing_y
points[:, 2] = coor[0] * spacing_z
pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(points)

all_inliers = []
all_slopes = []
all_intercept = []

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

all_slopes = np.array(all_slopes)
all_intercept = np.array(all_intercept)

all_lines = []

for i in range(8):
    t = np.linspace(-1e-1, 2e-1, 1000)
    x = all_slopes[i, 0] * t + all_intercept[i, 0]
    y = all_slopes[i, 1] * t + all_intercept[i, 1]
    z = all_slopes[i, 2] * t + all_intercept[i, 2]

    line_points = np.zeros((t.shape[0], 3))
    line_points[:, 0] = x
    line_points[:, 1] = y
    line_points[:, 2] = z
    line_pcd = o3d.geometry.PointCloud()
    line_pcd.points = o3d.utility.Vector3dVector(line_points)
    all_lines.append(line_pcd)

pcd.paint_uniform_color([1, 0, 0])

ref_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.05, origin=[0, 0, 0])

o3d.visualization.draw_geometries([pcd,
                                   all_lines[0],
                                   all_lines[1],
                                   all_lines[2],
                                   all_lines[3],
                                   all_lines[4],
                                   all_lines[5],
                                   all_lines[6],
                                   all_lines[7],
                                   ref_frame])

# plt.show()
# plt.savefig("slice230.png", dpi=500, transparent=True)
