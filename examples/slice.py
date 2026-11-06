"""Generate example CSG slice images."""

import matplotlib

matplotlib.use("Agg", force=True)

from cell import Cell
from geometry import CellEntry, Geometry
from render import save_slice
from shapes import OSphere, Plane
from slicing import make_slice_grid


def build_geometry():
    return Geometry([
        CellEntry(
            Cell([-OSphere(1)]),
            cell_id=1,
            material=1,
            color="#d62728",
        ),
        CellEntry(
            Cell([-OSphere(2), +OSphere(1)]),
            cell_id=2,
            material=2,
            color="#1f77b4",
        ),
    ])


def main():
    space = build_geometry()
    slices = [
        ("output/slice_z.png", Plane(0, 0, 1, 0)),
        ("output/slice_plane.png", Plane(1, 1, 1, 0.5)),
    ]

    for path, plane in slices:
        grid = make_slice_grid(
            plane,
            u_range=(-3.0, 3.0),
            v_range=(-3.0, 3.0),
            nx=600,
            ny=600,
        )
        save_slice(space, grid, path)
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
