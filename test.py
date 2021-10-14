import open3d
import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(-3, 3, 10000)

y1 = lambda x1: np.sqrt(np.cos(x1)) * np.cos(3200 * x1) + np.sqrt(np.abs(x1) + .2) + np.power((5 - np.square(x1)), .01)

plt.plot(x, y1(x), color="r")
plt.show()
