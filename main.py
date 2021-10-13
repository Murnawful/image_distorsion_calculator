import open3d as o3d
import numpy as np
import pydicom as pdcm
from irm_dist_calculator import analyzer as a
from irm_dist_calculator import referenceGrid as ref
from irm_dist_calculator import imageGrid as im
from irm_dist_calculator import referenceFiducials as rFi

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

coor = np.where(data != 0)
points = np.zeros((coor[0].shape[0], 3))
points[:, 0] = coor[2] * spacing_x
points[:, 1] = coor[1] * spacing_y
points[:, 2] = coor[0] * spacing_z
pcd_full = o3d.geometry.PointCloud()
pcd_full.points = o3d.utility.Vector3dVector(points)
# pcd_full.paint_uniform_color([0, 1, 0])

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

fiduc = rFi.ReferenceFiducials((4e-2, 6.9e-2, 5e-2))
fiduc.build()
fiduc.convert()

fiduc.register(pcd, "L", 1e-2, 1e-9)
fiduc.register(pcd, "R", 1e-2, 1e-9)

print(fiduc.check_parallelism(1e-4))

ori = fiduc.define_stereotactic_space()
ori1 = fiduc.define_stereotactic_space()
for i in range(len(ori)):
    ori1[i] += .1
print(ori)

fiduc.pcd_fiducial_L.paint_uniform_color([1, 0, 0])
fiduc.pcd_fiducial_R.paint_uniform_color([0, 0, 1])

ref_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.05, origin=ori)
ref_frame1 = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.05, origin=ori1)
o3d.visualization.draw_geometries([fiduc.pcd_fiducial_R, fiduc.pcd_fiducial_L, ref_frame, pcd_full, ref_frame1])

################ Node deviation analysis ################

"""# (0.12, 0.115, 0.095)  # CBCT_wo_H2O
# (0.135, 0.135, 0.06)  # 3DT1_115slices_coreg
# (0.135, 0.135, 0.06)  # 3DT1_115slices_fiduc
# (0.135, 0.135, 0.08)  # 3DT1_160slices_fiduc
# (0.109, 0.1095, 0.03)  # 3DT2_coreg
# (0.134, 0.134, 0.184)  # Protons_fiduc
# (0.105, 0.105, 0.03)  # T1Spir_30slices_coreg
# (0.105, 0.105, 0.202)  # T1Spir_30slices_FOV_coreg
grid = ref.ReferenceGrid(center=(0.105, 0.105, 0.03))
grid.build()
grid.convert()

name = "T1Spir_30slices_FOV_coreg"

ref_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.05, origin=[0, 0, 0])

# roi =  ((68, 150, 90), (260, 300, 220))  # CBCT2
# roi = ((68, 150, 210), (264, 300, 340))  # CBCT
# roi = ((166, 136, 195), (290, 330, 320))  # CBCT_wo_H2O
# roi = ((90, 80, 28), (160, 170, 86))  # 3DT1_115slices_coreg
# roi = ((90, 80, 28), (160, 170, 86))  # 3DT1_115slices_fiduc
# roi = ((100, 85, 50), (160, 170, 110))  # 3DT1_160slices_fiduc
# roi = ((182, 138, 0), (328, 352, 66))  # 3DT2_coreg
# roi = ((177, 148, 10), (300, 318, 40))  # Protons_fiduc
# roi = ((281, 213, 0), (505, 545, 28))  # T1Spir_30slices_coreg
# roi = ((306, 235, 0), (560, 598, 28))  # T1Spir_30slices_FOV_coreg
roi = ((306, 235, 0), (560, 598, 29))
source = im.ImageGrid("../../im_DICOM/complete_IRM_CBCT/" + name + "/", 29, range_hu=(150, 500), is_mri=True,
                      image_roi=roi)

# (100, 5000)  # CBCT_wo_H2O
# (400, 500)  # Protons_fiduc
# (890, 10000)  # 3DT2_coreg
# (10, 185)  # 3DT1_115slices_coreg
# (250, 1000)  # 3DT1_115slices_fiduc
# (270, 1000)  # 3DT1_160slices_fiduc
# (150, 500)  # T1Spir_30slices_coreg
# (150, 500)  # T1Spir_30slices_FOV_coreg
source.convert()
source.save_point_cloud("../data/" + name + "/", "realGrid_" + name)

grid.register(source.pcd, 1e-3, 1e-7)
grid.save_point_cloud("../data/" + name + "/", "registeredGrid_" + name)

grid.pcd.paint_uniform_color([0, 0, 1])

# o3d.visualization.draw_geometries([grid.pcd, ref_frame, source.pcd])

analyser = a.Analyzer(dir_tofile="../data/" + name + "/",
                      file_source="realGrid_" + name + ".ply",
                      file_vertex="registeredGrid_" + name + "_vertex.ply",
                      file_registered="registeredGrid_" + name + "_full.ply",
                      scope=3e-3)
analyser.launch_analysis()
analyser.save_analysis(name)"""
