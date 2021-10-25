# DistCal

This program is aimed at providing a way for the user to quantitatively assess geometric distorsions
in MR images using a CIRS STEEV phantom.

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

![](/im/file_manager.png)