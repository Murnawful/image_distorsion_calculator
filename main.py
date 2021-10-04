import open3d as o3d
from irm_dist_calculator import analyzer as a
from irm_dist_calculator import referenceGrid as ref
from irm_dist_calculator import imageGrid as im

# (0.12, 0.115, 0.095)  # CBCT_wo_H2O
# (0.135, 0.135, 0.06)  # 3DT1_115slices_coreg
# (0.135, 0.135, 0.06)  # 3DT1_115slices_fiduc
# (0.135, 0.135, 0.035)  # 3DT1_160slices_fiduc
# (0.109, 0.1095, 0.074)  # 3DT2_coreg
# (0.134, 0.134, 0.184)  # Protons_fiduc
# (0.105, 0.105, 0.205)  # T1Spir_30slices_coreg
grid = ref.ReferenceGrid(center=(0.105, 0.105, 0.205))
grid.build()
grid.convert()

name = "T1Spir_30slices_FOV_coreg"

ref_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.05, origin=[0, 0, 0])

# roi =  ((68, 150, 90), (260, 300, 220))  # CBCT2
# roi = ((68, 150, 210), (264, 300, 340))  # CBCT
# roi = ((166, 136, 195), (290, 330, 320))  # CBCT_wo_H2O
# roi = ((90, 80, 28), (160, 170, 86))  # 3DT1_115slices_coreg
# roi = ((90, 80, 28), (160, 170, 86))  # 3DT1_115slices_fiduc
# roi = ((100, 85, 50), (160, 170, 130))  # 3DT1_160slices_fiduc
# roi = ((100, 100, 0), (312, 412, 49))  # Protons_fiduc
# roi = ((281, 213, 0), (505, 545, 29))  # T1Spir_30slices_coreg
roi = ((306, 235, 0), (560, 598, 29))
source = im.ImageGrid("../../im_DICOM/complete_IRM_CBCT/" + name + "/", 115, range_hu=(150, 200), is_mri=True,
                      image_roi=roi)
source.convert()
source.save_point_cloud("../data/" + name + "/", "realGrid_" + name)

grid.register(source.pcd, 1e-3, 1e-7)
grid.save_point_cloud("../data/" + name + "/", "registeredGrid_" + name)

grid.pcd.paint_uniform_color([0, 0, 1])

# o3d.visualization.draw_geometries([grid.pcd, ref_frame, source.pcd])

analyser = a.Analyzer(dir="../data/" + name + "/", file_source="realGrid_" + name + ".ply",
                      file_vertex="registeredGrid_" + name + "_vertex.ply",
                      file_registered="registeredGrid_" + name + "_full.ply",
                      scope=2e-3)
analyser.launch_analysis()
analyser.save_analysis(name)
