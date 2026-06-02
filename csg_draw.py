import matplotlib.pyplot as pyplot
import numpy as np 
import shapes as sp

p01 = sp.XPlane(1, 1)
s02 = sp.OSphere(2.5)
c03 = sp.YCylinder(0, 0, 2)

num_set = np.array([
    [[0,0,0], [0,0,1], [0,0,2], [0,0,3]],
    [[1,0,0], [1,0,1], [1,0,2], [1,0,3]],
    [[2,0,0], [2,0,1], [2,0,2], [2,0,3]]
    ])

X = num_set[:, :, 0]
Y = num_set[:, :, 1]
Z = num_set[:, :, 2]

mask_p = p01.is_inside(X, Y, Z)
mask_s = s02.is_inside(X, Y, Z)
mask_c = c03.is_inside(X, Y, Z)

final_mask = mask_p & mask_s & mask_c

print(final_mask)
