from irm_dist_calculator import node_analyzer as a

name = "T1Spir_30slices_FOV_coreg"
d = "../data/" + name + "/"
im = a.NodeAnalyzer(dir_tofile=d,
                    file_source="realGrid_" + name + ".ply",
                    file_vertex="registeredGrid_" + name + "_vertex.ply",
                    file_registered="registeredGrid_" + name + "_full.ply",
                    scope=2e-3)
im.load_results(d + name + "_median_nodes_real_grid.ply",
                d + name + "_mean_nodes_real_grid.ply")
im.compute_results()
im.prepare_display()
im.save_results(name)
