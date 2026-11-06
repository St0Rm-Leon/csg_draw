"""A deliberately conflicting CSG example.

Three overlapping spheres compete for the same points.  Geometry uses
first-match semantics, so the visible result is deterministic:

    cell 1 wins in the overlap of all three spheres
    cell 2 wins only where cell 1 is absent
    cell 3 wins only where cells 1 and 2 are absent

The example also demonstrates two other conflict cases:

* a cell whose two surfaces contradict each other (empty cell);
* duplicate cell IDs (rejected by Geometry).

Run from the project root:

    uv run python -m examples.conflict
"""

import matplotlib

matplotlib.use("Agg", force=True)

import numpy as np

from cell import Cell
from geometry import CellEntry, Geometry, write_overlap_report
from render import save_slice
from shapes import OSphere, Plane, Sphere
from slicing import make_slice_grid


def build_geometry():
    return Geometry([
        CellEntry(
            Cell([-Sphere(0, 0, 0, 1.5)]),
            cell_id=1,
            material=1,
            color="#d62728",
        ),
        CellEntry(
            Cell([-Sphere(1, 0, 0, 1.5)]),
            cell_id=2,
            material=2,
            color="#1f77b4",
        ),
        CellEntry(
            Cell([-Sphere(-1, 0, 0, 1.5)]),
            cell_id=3,
            material=3,
            color="#2ca02c",
        ),
        # Contradictory: inside and outside the same sphere simultaneously.
        # No point can satisfy both strict sides, so this cell is empty.
        CellEntry(
            Cell([-OSphere(1), +OSphere(1)]),
            cell_id=4,
            material=4,
            color="#9467bd",
        ),
    ])


def check_sample_points(space):
    checks = [
        ((0.0, 0.0, 0.0), 0, "all three spheres overlap"),
        ((2.5, 0.0, 0.0), 1, "only cell 2"),
        ((-2.4, 0.0, 0.0), 2, "only cell 3"),
        ((4.0, 0.0, 0.0), -1, "background"),
    ]

    print("sample checks:")
    for point, expected, label in checks:
        claims = [
            index
            for index, entry in enumerate(space)
            if bool(entry.cell.is_inside_cell(*point))
        ]
        index = space.find_cell(*point)
        print(
            f"  {point} -> claims={claims}, "
            f"first_match={index:2d} ({label})"
        )
        assert index == expected, (point, index, expected)


def check_duplicate_cell_ids():
    try:
        Geometry([
            CellEntry(Cell([-OSphere(1)]), cell_id=1),
            CellEntry(Cell([-OSphere(2)]), cell_id=1),
        ])
    except ValueError as exc:
        print(f"duplicate cell_id rejected: {exc}")
    else:
        raise AssertionError("duplicate cell_id should have been rejected")


def check_empty_cell(space):
    empty_cell = space.entries[3].cell
    assert not bool(empty_cell.is_inside_cell(0.0, 0.0, 0.0))
    print("contradictory cell is empty: OK")


def main():
    space = build_geometry()
    check_duplicate_cell_ids()
    check_sample_points(space)
    check_empty_cell(space)

    grid = make_slice_grid(
        Plane(0, 0, 1, 0),
        u_range=(-4.0, 4.0),
        v_range=(-4.0, 4.0),
        nx=700,
        ny=700,
    )

    labels = space.sample(grid.x, grid.y, grid.z)
    masks = np.array([
        entry.cell.is_inside_cell(grid.x, grid.y, grid.z)
        for entry in space
    ], dtype=bool)
    claim_count = masks.sum(axis=0)

    print("grid diagnostics:")
    print(f"  max simultaneous claims: {int(claim_count.max())}")
    print(f"  points with >1 claim:    {int(np.count_nonzero(claim_count > 1))}")
    print(f"  empty cell claims:       {int(np.count_nonzero(masks[3]))}")
    print(f"  background points:       {int(np.count_nonzero(labels == -1))}")

    report = write_overlap_report(
        space,
        grid.x,
        grid.y,
        grid.z,
        "output/conflict_overlap_warning.csv",
    )
    if report.count:
        print(
            f"WARNING: {report.count} grid points are claimed by multiple cells"
        )
    else:
        print("WARNING: no overlapping grid points found")
    print(f"wrote {report.path}")

    path = save_slice(
        space,
        grid,
        "output/conflict_z.png",
        title="conflicting spheres: z = 0 (multi-defined in magenta)",
    )
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
