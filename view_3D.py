import open3d as o3d

name = "T1Spir_30slices_coreg"

real_grid = o3d.io.read_point_cloud("../data/" + name + "/registeredGrid_" + name + "_vertex.ply")
media_points = o3d.io.read_point_cloud("../data/" + name + "/" + name + "_median_nodes_real_grid.ply")
mean_points = o3d.io.read_point_cloud("../data/" + name + "/" + name + "_mean_nodes_real_grid.ply")

ref_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.05, origin=[0, 0, 0])

real_grid.paint_uniform_color([0, 0, 1])
media_points.paint_uniform_color([1, 0, 0])
mean_points.paint_uniform_color([0, 1, 0])

o3d.visualization.draw_geometries([ref_frame, real_grid, mean_points, media_points])