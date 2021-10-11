import numpy as np

arr = np.array([[0, 0, 0],
                [0, 1, 2],
                [2, 1, 0],
                [3, 8, 0],
                [0, 0, 0]])
arr1 = np.array([[3, 3, 3],
                 [4, 4, 4],
                 [5, 5, 5]])


all_arr = np.concatenate((arr, arr1), axis=0)

print(all_arr)
