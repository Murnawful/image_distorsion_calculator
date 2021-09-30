import open3d as o3d
from irm_dist_calculator import analyzer as a
from irm_dist_calculator import referenceGrid as ref
from irm_dist_calculator import imageGrid as im

grid = ref.ReferenceGrid(center=(0.12, 0.115, 0.095))
grid.build()
grid.convert()

ref_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.05, origin=[0, 0, 0])

# roi =  ((68, 150, 90), (260, 300, 220)) # CBCT2
# roi = ((68, 150, 210), (264, 300, 340)) # CBCT
roi = ((166, 136, 195), (290, 330, 320)) # CBCT_wo_H2O
source = im.ImageGrid("../../im_DICOM/complete_IRM_CBCT/CBCT_wo_H2O/", 448, image_roi=roi)
source.convert()
source.save_point_cloud("../data/", "grid_CBCT_wo_H2O")

grid.register(source.pcd, 1e-3, 1e-7)
grid.save_point_cloud("../data/", "registeredGrid_CBCT_wo_H2O")

grid.pcd.paint_uniform_color([0, 0, 1])

# o3d.visualization.draw_geometries([grid.pcd, ref_frame, source.pcd])

analyser = a.Analyzer(dir="../data/", file_source="grid_CBCT_wo_H2O.ply", file_vertex="registeredGrid_CBCT_wo_H2O_vertex.ply", file_registered="registeredGrid_CBCT_wo_H2O_full.ply")
analyser.launch_analysis()
analyser.save_analysis("CBCT_wo_H2O")