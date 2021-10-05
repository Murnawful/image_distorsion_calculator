import numpy as np

arr = np.array([[0, 0, 0],
                [0, 1, 2],
                [2, 1, 0],
                [3, 8, 0],
                [0, 0, 0]])

print((arr[0, :] == np.array([0, 0, 0])).all())
