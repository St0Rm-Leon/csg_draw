import numpy as np
import pytest

import cell
import geometry
import shapes as sp
import slicing


def _sphere_cell(radius):
    return cell.Cell([-sp.OSphere(radius)])


def test_empty_geometry_is_background():
    space = geometry.Geometry([])

    assert space.find_cell(0.0, 0.0, 0.0) == -1
    assert np.array_equal(
        space.sample(
            np.array([0.0, 1.0]),
            np.array([0.0, 0.0]),
            np.array([0.0, 0.0]),
        ),
        np.array([-1, -1]),
    )


def test_single_cell_and_background():
    space = geometry.Geometry([_sphere_cell(1)])

    assert space.find_cell(0.0, 0.0, 0.0) == 0
    assert space.find_cell(1.0, 0.0, 0.0) == 0
    assert space.find_cell(2.0, 0.0, 0.0) == -1
    assert space.cell_ids == [0]


def test_plain_cells_get_positional_ids():
    space = geometry.Geometry([_sphere_cell(1), _sphere_cell(2)])

    assert space.cell_ids == [0, 1]
    assert [entry.cell_id for entry in space] == [0, 1]
    assert len(space) == 2


def test_first_match_wins():
    space = geometry.Geometry([
        geometry.CellEntry(_sphere_cell(1), cell_id=10),
        geometry.CellEntry(_sphere_cell(2), cell_id=20),
    ])

    assert space.find_cell(0.0, 0.0, 0.0) == 0
    assert space.find_cell(1.5, 0.0, 0.0) == 1
    assert space.find_cell(2.5, 0.0, 0.0) == -1


def test_spherical_shell_and_metadata():
    inner = cell.Cell([-sp.OSphere(1)])
    shell = cell.Cell([-sp.OSphere(2), +sp.OSphere(1)])
    space = geometry.Geometry([
        geometry.CellEntry(inner, cell_id=10, material=1, color="red"),
        geometry.CellEntry(shell, cell_id=20, material=2, color="blue"),
    ])

    points = np.array([
        [0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [1.5, 0.0, 0.0],
        [2.0, 0.0, 0.0],
        [3.0, 0.0, 0.0],
    ])
    labels = space.sample(points[:, 0], points[:, 1], points[:, 2])

    assert labels.tolist() == [0, 0, 1, 1, -1]
    assert space.cell_ids == [10, 20]
    assert space.entries[0].material == 1
    assert space.entries[0].color == "red"
    assert space.entries[1].material == 2
    assert space.entries[1].color == "blue"


def test_sample_broadcasting():
    space = geometry.Geometry([_sphere_cell(1)])

    labels = space.sample(0.0, np.array([0.0, 2.0]), 0.0)
    assert np.array_equal(labels, np.array([0, -1]))

    labels = space.sample(
        np.array([[0.0], [2.0]]),
        np.array([0.0, 0.0]),
        0.0,
    )
    assert labels.shape == (2, 2)
    assert labels.tolist() == [[0, 0], [-1, -1]]


def test_find_cell_rejects_array_coordinates():
    space = geometry.Geometry([_sphere_cell(1)])

    with pytest.raises(ValueError):
        space.find_cell(np.array([0.0]), 0.0, 0.0)


def test_duplicate_cell_ids_are_rejected():
    with pytest.raises(ValueError):
        geometry.Geometry([
            geometry.CellEntry(_sphere_cell(1), cell_id=1),
            geometry.CellEntry(_sphere_cell(2), cell_id=1),
        ])


def test_invalid_entries_are_rejected():
    with pytest.raises(TypeError):
        geometry.Geometry([object()])


def test_cell_entry_defaults():
    entry = geometry.CellEntry(_sphere_cell(1), cell_id=5)

    assert entry.material is None
    assert entry.color is None


def test_geometry_sampling_on_slice_grid():
    space = geometry.Geometry([_sphere_cell(1)])
    grid = slicing.make_slice_grid(
        sp.Plane(0, 0, 1, 0),
        u_range=(-2.0, 2.0),
        v_range=(-2.0, 2.0),
        nx=5,
        ny=5,
    )

    labels = space.sample(grid.x, grid.y, grid.z)

    assert labels.shape == (5, 5)
    assert labels[2, 2] == 0
    assert labels[0, 0] == -1
