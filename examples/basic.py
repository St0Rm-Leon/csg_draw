"""Basic Cell/Geometry membership demonstration."""

import numpy as np

import cell as cl
import shapes as sp


def main():
    px01 = sp.XPlane(1, 0.5)
    so02 = sp.OSphere(2)
    cz03 = sp.ZCylinder(0, 0, 1)

    cl01 = cl.Cell([px01, -so02, -cz03])
    cl01.print_info()

    num_set = np.array([
        [[0, 0, 0], [0, 0, 1], [0, 0, 2], [0, 0, 3]],
        [[1, 0, 0], [1, 0, 1], [1, 0, 2], [1, 0, 3]],
        [[2, 0, 0], [2, 0, 1], [2, 0, 2], [2, 0, 3]],
    ])

    x = num_set[:, :, 0]
    y = num_set[:, :, 1]
    z = num_set[:, :, 2]

    print(cl01.is_inside_cell(x, y, z))


if __name__ == "__main__":
    main()
