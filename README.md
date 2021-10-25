# DistCal

This program is aimed at providing a way for the user to quantitatively assess geometric distorsions
in MR images using a CIRS STEEV phantom. Acquisitions should be performed using the spatial 3D distorsion insert.

You can leave the application by pressing _<Ctrl-q>_

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
_)_ and _-_ keys of your (AZERTY) keyboard in order to assess the quality of the regsitration.