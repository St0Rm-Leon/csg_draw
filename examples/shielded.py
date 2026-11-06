"""A slightly larger programmatic CSG example.

The model is a spherical core and cladding inside a rectangular box:

    1. inner sphere  : r < 1
    2. spherical shell: 1 < r < 2
    3. box filler    : inside the box and outside the shell
    4. background    : outside the box

Run from the project root:

    uv run python -m examples.shielded
"""

import matplotlib

matplotlib.use("Agg", force=True)

from cell import Cell
from geometry import CellEntry, Geometry
from macro import RPP
from render import save_slice
from shapes import OSphere, Plane
from slicing import make_slice_grid


BOX = RPP(-4, 4, -4, 4, -4, 4)


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
        CellEntry(
            Cell([-BOX, +OSphere(2)]),
            cell_id=3,
            material=3,
            color="#2ca02c",
        ),
    ])


def check_sample_points(space):
    checks = [
        ((0.0, 0.0, 0.0), 0, "inner sphere"),
        ((1.5, 0.0, 0.0), 1, "spherical shell"),
        ((3.0, 0.0, 0.0), 2, "box filler"),
        ((5.0, 0.0, 0.0), -1, "background"),
    ]

    print("sample checks:")
    for point, expected, label in checks:
        index = space.find_cell(*point)
        cell_id = space.entries[index].cell_id if index >= 0 else -1
        print(
            f"  {point} -> index={index:2d}, "
            f"cell_id={cell_id:2d} ({label})"
        )
        assert index == expected, (point, index, expected)


def main():
    space = build_geometry()
    check_sample_points(space)

    slices = [
        (
            "output/example_z.png",
            Plane(0, 0, 1, 0),
            "shielded sphere: z = 0",
        ),
        (
            "output/example_x.png",
            Plane(1, 0, 0, 0),
            "shielded sphere: x = 0",
        ),
        (
            "output/example_plane.png",
            Plane(1, 1, 1, 1.0),
            "shielded sphere: x + y + z = 1",
        ),
    ]

    for path, plane, title in slices:
        grid = make_slice_grid(
            plane,
            u_range=(-5.0, 5.0),
            v_range=(-5.0, 5.0),
            nx=700,
            ny=700,
        )
        save_slice(space, grid, path, title=title)
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
