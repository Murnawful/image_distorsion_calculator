import open3d
import numpy as np

plane = np.array([0.9998788,
                  -0.0155117,
                  0.00133355,
                  -0.03708078])
A = plane[0]
B = plane[1]
C = plane[2]
D = plane[3]
x = np.linspace(0, 1e-2, 100)
y = np.linspace(0, 1e-2, 100)
print(-D/C)
z = (-1 / C) * (A * x + B * y + D)

print(z)
