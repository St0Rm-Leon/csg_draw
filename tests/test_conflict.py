import csv

import numpy as np
import pytest

import cell
import geometry
import shapes as sp
import slicing


def _conflicting_space():
    return geometry.Geometry([
        geometry.CellEntry(
            cell.Cell([-sp.Sphere(0, 0, 0, 1.5)]),
            cell_id=1,
        ),
        geometry.CellEntry(
            cell.Cell([-sp.Sphere(1, 0, 0, 1.5)]),
            cell_id=2,
        ),
        geometry.CellEntry(
            cell.Cell([-sp.Sphere(-1, 0, 0, 1.5)]),
            cell_id=3,
        ),
        geometry.CellEntry(
            cell.Cell([-sp.OSphere(1), +sp.OSphere(1)]),
            cell_id=4,
        ),
    ])


def test_overlapping_cells_use_first_match():
    space = _conflicting_space()
    point = (0.0, 0.0, 0.0)

    claims = [
        bool(entry.cell.is_inside_cell(*point))
        for entry in space
    ]

    assert claims == [True, True, True, False]
    assert space.find_cell(*point) == 0


def test_visible_regions_follow_cell_order():
    space = _conflicting_space()

    assert space.find_cell(2.5, 0.0, 0.0) == 1
    assert space.find_cell(-2.4, 0.0, 0.0) == 2
    assert space.find_cell(4.0, 0.0, 0.0) == -1


def test_contradictory_cell_is_empty():
    space = _conflicting_space()
    empty_cell = space.entries[3].cell

    assert not bool(empty_cell.is_inside_cell(0.0, 0.0, 0.0))

    grid = slicing.make_slice_grid(
        sp.Plane(0, 0, 1, 0),
        u_range=(-4.0, 4.0),
        v_range=(-4.0, 4.0),
        nx=101,
        ny=101,
    )
    labels = space.sample(grid.x, grid.y, grid.z)

    assert not np.any(labels == 3)


def test_grid_labels_match_first_claimant_and_contain_overlaps():
    space = _conflicting_space()
    grid = slicing.make_slice_grid(
        sp.Plane(0, 0, 1, 0),
        u_range=(-4.0, 4.0),
        v_range=(-4.0, 4.0),
        nx=101,
        ny=101,
    )

    masks = np.array([
        entry.cell.is_inside_cell(grid.x, grid.y, grid.z)
        for entry in space
    ], dtype=bool)
    expected = np.where(masks.any(axis=0), masks.argmax(axis=0), -1)
    labels = space.sample(grid.x, grid.y, grid.z)

    assert np.array_equal(labels, expected)
    assert np.count_nonzero(masks.sum(axis=0) > 1) > 0


def test_fully_shadowed_cell_is_never_selected():
    space = geometry.Geometry([
        geometry.CellEntry(cell.Cell([-sp.OSphere(1)]), cell_id=1),
        geometry.CellEntry(cell.Cell([-sp.OSphere(1)]), cell_id=2),
    ])

    grid = slicing.make_slice_grid(
        sp.Plane(0, 0, 1, 0),
        u_range=(-2.0, 2.0),
        v_range=(-2.0, 2.0),
        nx=21,
        ny=21,
    )
    labels = space.sample(grid.x, grid.y, grid.z)

    assert labels[10, 10] == 0
    assert not np.any(labels == 1)


def test_duplicate_cell_ids_are_rejected():
    with pytest.raises(ValueError):
        geometry.Geometry([
            geometry.CellEntry(cell.Cell([-sp.OSphere(1)]), cell_id=7),
            geometry.CellEntry(cell.Cell([-sp.OSphere(2)]), cell_id=7),
        ])


def test_sample_can_mark_multi_defined_points():
    space = _conflicting_space()

    assert int(space.sample(0.0, 0.0, 0.0, mark_conflicts=True)) == (
        geometry.MULTI_DEFINED
    )
    assert int(space.sample(2.5, 0.0, 0.0, mark_conflicts=True)) == 1
    assert int(space.sample(4.0, 0.0, 0.0, mark_conflicts=True)) == -1


def test_write_overlap_report(tmp_path):
    space = _conflicting_space()
    grid = slicing.make_slice_grid(
        sp.Plane(0, 0, 1, 0),
        u_range=(-2.0, 2.0),
        v_range=(-2.0, 2.0),
        nx=11,
        ny=11,
    )
    path = tmp_path / "overlap.csv"

    report = geometry.write_overlap_report(
        space,
        grid.x,
        grid.y,
        grid.z,
        path,
    )

    assert report.path == path
    assert report.count > 0
    assert report.max_claim_count == 3

    lines = [
        line
        for line in path.read_text(encoding="utf-8").splitlines()
        if not line.startswith("#")
    ]
    rows = list(csv.DictReader(lines))

    assert len(rows) == report.count
    assert all(int(row["claim_count"]) > 1 for row in rows)
    assert any(row["cell_ids"] == "1;2;3" for row in rows)


def test_write_overlap_report_without_overlaps(tmp_path):
    space = geometry.Geometry([
        geometry.CellEntry(cell.Cell([-sp.OSphere(1)]), cell_id=1),
    ])
    grid = slicing.make_slice_grid(
        sp.Plane(0, 0, 1, 0),
        u_range=(-2.0, 2.0),
        v_range=(-2.0, 2.0),
        nx=5,
        ny=5,
    )
    path = tmp_path / "no_overlap.csv"

    report = geometry.write_overlap_report(
        space,
        grid.x,
        grid.y,
        grid.z,
        path,
    )

    assert report.count == 0
    lines = [
        line
        for line in path.read_text(encoding="utf-8").splitlines()
        if not line.startswith("#")
    ]
    assert len(lines) == 1  # header only
