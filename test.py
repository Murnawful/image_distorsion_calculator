import numpy as np

arr = np.array([[0, 1, 0, 0, 1],
                [0, 1, 1, 0, 1],
                [1, 0, 0, 0, 0],
                [1, 1, 1, 1, 0]])

print(arr * (-1) + 1)