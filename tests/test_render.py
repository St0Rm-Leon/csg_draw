import matplotlib

matplotlib.use("Agg", force=True)

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import to_rgba

import cell
import geometry
import render
import shapes as sp
import slicing


def _space():
    return geometry.Geometry([
        geometry.CellEntry(
            cell.Cell([-sp.OSphere(1)]),
            cell_id=1,
            material=1,
            color="#d62728",
        ),
        geometry.CellEntry(
            cell.Cell([-sp.OSphere(2), +sp.OSphere(1)]),
            cell_id=2,
            material=2,
            color="#1f77b4",
        ),
    ])


def _grid():
    return slicing.make_slice_grid(
        sp.Plane(0, 0, 1, 0),
        u_range=(-2.5, 2.5),
        v_range=(-2.5, 2.5),
        nx=11,
        ny=11,
    )


def _overlapping_space():
    return geometry.Geometry([
        geometry.CellEntry(cell.Cell([-sp.OSphere(1)]), cell_id=1),
        geometry.CellEntry(cell.Cell([-sp.OSphere(1)]), cell_id=2),
    ])


def test_render_slice_returns_image():
    space = _space()
    grid = _grid()

    fig, ax = render.render_slice(space, grid)

    assert len(ax.images) == 1
    image = ax.images[0]
    labels = np.ma.filled(image.get_array(), -1)
    mask = np.ma.getmaskarray(image.get_array())

    assert labels.shape == grid.shape
    assert labels[5, 5] == 0
    assert labels[0, 0] == -1
    assert mask[0, 0]
    assert not mask[5, 5]

    plt.close(fig)


def test_render_slice_matches_geometry_sample():
    space = _space()
    grid = _grid()

    fig, ax = render.render_slice(space, grid, title="custom title")
    labels = np.ma.filled(ax.images[0].get_array(), -1)

    assert np.array_equal(labels, space.sample(grid.x, grid.y, grid.z))
    assert ax.get_title() == "custom title"

    plt.close(fig)


def test_custom_colors_are_used():
    space = _space()
    grid = _grid()

    fig, ax = render.render_slice(
        space,
        grid,
        colors=["#ff0000", "#00ff00"],
    )
    cmap = ax.images[0].cmap

    np.testing.assert_allclose(cmap(0)[:3], (1.0, 0.0, 0.0))
    np.testing.assert_allclose(cmap(1)[:3], (0.0, 1.0, 0.0))

    plt.close(fig)


def test_empty_geometry_renders_background_only():
    space = geometry.Geometry([])
    grid = _grid()

    fig, ax = render.render_slice(space, grid)

    assert len(ax.images) == 0
    assert ax.get_title() == "z = 0"

    plt.close(fig)


def test_save_slice(tmp_path):
    space = _space()
    grid = _grid()
    path = tmp_path / "nested" / "slice.png"

    result = render.save_slice(space, grid, path)

    assert result == path
    assert path.exists()
    assert path.stat().st_size > 0


def test_render_slice_reuses_existing_axis():
    space = _space()
    grid = _grid()
    fig, ax = plt.subplots()

    result_fig, result_ax = render.render_slice(space, grid, ax=ax)

    assert result_fig is fig
    assert result_ax is ax

    plt.close(fig)


def test_render_slice_marks_multi_defined_and_adds_legend():
    space = _overlapping_space()
    grid = _grid()

    fig, ax = render.render_slice(space, grid)

    labels = np.ma.filled(ax.images[0].get_array(), -1)
    assert np.any(labels == len(space))

    legend_texts = [text.get_text() for text in fig.legends[0].get_texts()]
    assert "ID=1" in legend_texts
    assert "ID=2" in legend_texts
    assert "ID=Multi-Defined" in legend_texts

    plt.close(fig)


def test_material_color_mode_groups_cells():
    space = geometry.Geometry([
        geometry.CellEntry(
            cell.Cell([-sp.OSphere(1)]),
            cell_id=1,
            material=1,
        ),
        geometry.CellEntry(
            cell.Cell([-sp.OSphere(2), +sp.OSphere(1)]),
            cell_id=2,
            material=1,
        ),
    ])
    grid = _grid()

    fig, ax = render.render_slice(space, grid, color_by="material")
    cmap = ax.images[0].cmap

    np.testing.assert_allclose(cmap(0), cmap(1))
    legend_texts = [text.get_text() for text in fig.legends[0].get_texts()]
    assert "MAT=1" in legend_texts
    assert "ID=1" not in legend_texts

    plt.close(fig)


def test_void_color_and_legend():
    space = geometry.Geometry([
        geometry.CellEntry(
            cell.Cell([-sp.OSphere(1)]),
            cell_id=1,
            material=0,
        ),
        geometry.CellEntry(
            cell.Cell([-sp.OSphere(2), +sp.OSphere(1)]),
            cell_id=2,
            material=1,
        ),
    ])
    grid = _grid()

    fig, ax = render.render_slice(
        space,
        grid,
        color_by="material",
        void_color="#123456",
    )
    cmap = ax.images[0].cmap

    np.testing.assert_allclose(cmap(0), to_rgba("#123456"))
    legend_texts = [text.get_text() for text in fig.legends[0].get_texts()]
    assert "MAT=0 (VOID)" in legend_texts
    assert "MAT=1" in legend_texts

    plt.close(fig)
