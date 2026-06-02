import cell as cl 
import shapes as sp 
import numpy as np 

px01 = sp.XPlane(1, 0.5)
so02 = sp.OSphere(2)
cz03 = sp.ZCylinder(0,0,1)

cl01 = cl.Cell([px01, -so02, -cz03])
cl01.print_info()

num_set = np.array([
    [[0,0,0], [0,0,1], [0,0,2], [0,0,3]],
    [[1,0,0], [1,0,1], [1,0,2], [1,0,3]],
    [[2,0,0], [2,0,1], [2,0,2], [2,0,3]]
    ])

X = num_set[:, :, 0]
Y = num_set[:, :, 1]
Z = num_set[:, :, 2]

mask_p = cl01.is_inside_cell(X, Y, Z)
print(mask_p)
