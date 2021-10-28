# DistCal

This program is aimed at providing a way for the user to quantitatively assess geometric distorsions
in MR images using a CIRS STEEV phantom. Acquisitions should be performed using the spatial 3D distorsion insert.

You can leave the application by pressing _Ctrl+q_

### _Required libraries:_
* Open3D
* Pydicom
* Scipy
* Numpy
* Matplotlib

## How to use it:
The program is engineered in a way to allow you to treat a set of DICOM slices that belong to a single acquisition.
Once the program is launched, you should first point to the set of slices to import by using the file manager in the
upper left corner of the window.

![file_manager](/im/file_manager.png)

You can add or delete as many files as you like. We however recommend importing the whole acquisition. Once all the slices
have been correctly selected, press the **Load DICOM files** button. The images will then be extracted and displayed in axial
and coronal views.

You will not see anything in both views after this procedure. Indeed, the program will need to extract a binary image in order
to perform the analysis. You will therefore need to use both sliders on the left side of the window in order to create this binary
image.

![sliders](/im/sliders.png)

These sliders allow defining bounds to an interval of values extracted from the arrays of the DICOM files. All values outside this
interval will be set to 0 while all values in this interval will be set to 1. You should set these bounds by watching their effect
on the image displayed in axial and coronal views. You can travel through slices by using the _mouse wheel_.

Once the interval has been selected, you should define a ROI that will select only the insert in the image. This can be done
with the _left click_ by pressing. Limits for _x_ and _y_ axis are defined on the axial view. You should start with those
as it will not be possible to start _z_ axis definition before that. Once the ROI is defined for _x_ and _y_, do the same on
the coronal view also with _left click_ in order to define the extent of the ROI along _z_ axis.

![roi](/im/roi.png)

You should then define the center of the insert. This can be done by _right clicking_ first on the axial view, then on the 
coronal view.

Once this is done, press the **Place virtual grid button**. This will open an _Open3D_ window showing you the selected ROI and 
placing a virtual grid at the position that you previously defined. This virtual grid was built according to dimensions provided
in the STEEV documentation.

If you are satisfied with the placement of the virtual grid, enter parameters in the **Coarse registration** and **Fine registration**.
These parameters will define how the virtual grid will be fitted to the ROI. Please read [this link](http://www.open3d.org/docs/0.12.0/tutorial/pipelines/icp_registration.html)
for more information on the registration that is performed. The chosen ICP is point-to-point. Once the parameters are chosen, press
the **Launch coregistration** button. A new _Open3D_ window will display the result of the registration. We recommend using
")" and "-" keys of your (AZERTY) keyboard in order to assess the quality of the regsitration. Close the Open3D window by hitting
the "a" key (AZERTY keyboard). If the registration is not to your liking, you can deny saving and try the registration once again
with different parameters.

Saving the result of the registration is primordial in order to perform node analysis. If the registration is deemed satisfying,
it must be saved. Node analysis can be launched with the corresponding button. This analysis will be performed with the saved
results as a source. The node analysis is described in the next section.

## Node analysis
Node analysis consists in comparing position of nodes of the virtual grid with that of the nodes of the real grid.

![nodes](/im/nodes.png)

Once the registration is done, the transformation applied to the virtual grid in order to fit the real grid is applied to a point cloud that corresponds to
the nodes of the virtual grid. For each of the nodes, points of the real grid standing in a radius of 3 mm (this value can be changed
in the source code in _Analyzer_ class, _launch_analysis()_ method) are saved. All these points are potential candidates to be the corresponding real grid node. In order to find it,
each of these points is looked at by counting the number of points that stand in a radius of 0.7 mm around this point (this value
can be changed in the source code in _Analyzer_ class, _launch_analysis()_ method). The algorithm then only selects points that
have the maximum number of close neighbours and computes the mean and median positions of all these good candidates. These mean and median positions
are considered as being the best candidates for the position of the corresponding real grid node. This process is performed for each node of the virtual grid.

Once this process is over, deviation between virtual grid nodes and real grid nodes is computed for all directions of space.
If the user chooses to save the results (with the corresponding button), a bar chart is saved in the _data_ folder along with
numpy arrays containing the corresponding data.