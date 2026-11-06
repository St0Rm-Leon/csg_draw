import numpy as np
import pytest

import shapes as sp
import slicing


@pytest.mark.parametrize("plane, origin, u, v, labels", [
    (
        sp.Plane(1, 0, 0, 2),
        (2.0, 0.0, 0.0),
        (0.0, 1.0, 0.0),
        (0.0, 0.0, 1.0),
        ("y", "z"),
    ),
    (
        sp.Plane(0, 1, 0, 2),
        (0.0, 2.0, 0.0),
        (1.0, 0.0, 0.0),
        (0.0, 0.0, 1.0),
        ("x", "z"),
    ),
    (
        sp.Plane(0, 0, 1, 2),
        (0.0, 0.0, 2.0),
        (1.0, 0.0, 0.0),
        (0.0, 1.0, 0.0),
        ("x", "y"),
    ),
])
def test_axis_aligned_frames(plane, origin, u, v, labels):
    frame = slicing.plane_frame(plane)

    np.testing.assert_allclose(frame.origin, origin)
    np.testing.assert_allclose(frame.u, u)
    np.testing.assert_allclose(frame.v, v)
    assert (frame.u_label, frame.v_label) == labels


def test_axis_aligned_frame_handles_scaled_plane():
    frame = slicing.plane_frame(sp.Plane(0, 0, 10, 20))

    np.testing.assert_allclose(frame.origin, (0.0, 0.0, 2.0))
    assert frame.u_label == "x"
    assert frame.v_label == "y"


def test_axis_aligned_frame_handles_negative_normal():
    frame = slicing.plane_frame(sp.Plane(0, 0, -1, 2))

    np.testing.assert_allclose(frame.origin, (0.0, 0.0, -2.0))
    assert frame.u_label == "x"
    assert frame.v_label == "y"


def test_arbitrary_frame_is_orthonormal_and_lies_on_plane():
    plane = sp.Plane(1, 2, 3, 4)
    frame = slicing.plane_frame(plane)

    np.testing.assert_allclose(np.linalg.norm(frame.normal), 1.0)
    np.testing.assert_allclose(np.dot([1.0, 2.0, 3.0], frame.origin), 4.0)
    np.testing.assert_allclose(np.dot(frame.normal, frame.u), 0.0, atol=1e-12)
    np.testing.assert_allclose(np.dot(frame.normal, frame.v), 0.0, atol=1e-12)
    np.testing.assert_allclose(np.dot(frame.u, frame.v), 0.0, atol=1e-12)
    np.testing.assert_allclose(np.linalg.norm(frame.u), 1.0)
    np.testing.assert_allclose(np.linalg.norm(frame.v), 1.0)
    assert (frame.u_label, frame.v_label) == ("u", "v")


def test_make_slice_grid_axis_aligned():
    grid = slicing.make_slice_grid(
        sp.Plane(0, 0, 1, 1),
        u_range=(-2.0, 2.0),
        v_range=(-3.0, 3.0),
        nx=5,
        ny=7,
    )

    assert grid.shape == (7, 5)
    assert grid.u.shape == (5,)
    assert grid.v.shape == (7,)
    assert grid.extent == (-2.0, 2.0, -3.0, 3.0)
    assert grid.u_label == "x"
    assert grid.v_label == "y"

    np.testing.assert_allclose(grid.x[0], (-2.0, -1.0, 0.0, 1.0, 2.0))
    np.testing.assert_allclose(grid.y[:, 0], (-3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0))
    np.testing.assert_allclose(grid.z, 1.0)


def test_make_slice_grid_arbitrary_plane():
    plane = sp.Plane(1, 2, 3, 4)
    grid = slicing.make_slice_grid(
        plane,
        u_range=(-1.0, 1.0),
        v_range=(-0.5, 0.5),
        nx=9,
        ny=5,
    )

    assert grid.shape == (5, 9)
    np.testing.assert_allclose(
        1.0 * grid.x + 2.0 * grid.y + 3.0 * grid.z,
        4.0,
        atol=1e-12,
    )


@pytest.mark.parametrize("u_range, v_range, nx, ny", [
    ((-1.0, -1.0), (-1.0, 1.0), 5, 5),
    ((1.0, -1.0), (-1.0, 1.0), 5, 5),
    ((-1.0, 1.0), (-1.0, -1.0), 5, 5),
    ((-1.0, 1.0), (1.0, -1.0), 5, 5),
    ((-1.0, 1.0), (-1.0, 1.0), 1, 5),
    ((-1.0, 1.0), (-1.0, 1.0), 5, 1),
    ((-1.0, 1.0), (-1.0, 1.0), 5.5, 5),
])
def test_invalid_slice_grid_parameters(u_range, v_range, nx, ny):
    with pytest.raises(ValueError):
        slicing.make_slice_grid(
            sp.Plane(0, 0, 1, 0),
            u_range=u_range,
            v_range=v_range,
            nx=nx,
            ny=ny,
        )
