from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.patches import Patch

from geometry import Geometry, MULTI_DEFINED
from slicing import SliceGrid


MULTI_COLOR = "#ff00ff"
DEFAULT_VOID_COLOR = "#d9d9d9"

DEFAULT_COLORS = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
    "#bcbd22",
    "#17becf",
]


def _plane_title(plane):
    terms = []
    for coefficient, name in ((plane.a, "x"), (plane.b, "y"), (plane.c, "z")):
        if coefficient == 0:
            continue
        if coefficient == 1:
            terms.append(f"+{name}")
        elif coefficient == -1:
            terms.append(f"-{name}")
        else:
            terms.append(f"{coefficient:+g}{name}")

    lhs = " ".join(terms) if terms else "0"
    if lhs.startswith("+"):
        lhs = lhs[1:]
    return f"{lhs} = {plane.d:g}"


def _resolve_cell_colors(
    geometry,
    colors=None,
    color_by="cell",
    material_colors=None,
    void_color=DEFAULT_VOID_COLOR,
):
    count = len(geometry)

    if colors is not None:
        if color_by != "cell":
            raise ValueError(
                "explicit colors cannot be combined with color_by='material'"
            )
        colors = list(colors)
        if count and not colors:
            raise ValueError(
                "colors must not be empty when geometry has cells"
            )
        if len(colors) < count:
            colors = [colors[index % len(colors)] for index in range(count)]
        return colors[:count], None

    if color_by == "cell":
        return [
            entry.color or DEFAULT_COLORS[index % len(DEFAULT_COLORS)]
            for index, entry in enumerate(geometry)
        ], None

    if color_by != "material":
        raise ValueError(f"unknown color mode: {color_by!r}")

    material_colors = dict(material_colors or {})
    mapping = {}

    for entry in geometry:
        material = entry.material
        if material in mapping:
            continue
        if material == 0:
            color = material_colors.get(0, void_color)
        elif material in material_colors:
            color = material_colors[material]
        else:
            color = DEFAULT_COLORS[
                len(mapping) % len(DEFAULT_COLORS)
            ]
        mapping[material] = color

    return [mapping[entry.material] for entry in geometry], mapping


def _legend_items(geometry, cell_colors, color_by, material_map):
    if color_by == "cell" or material_map is None:
        return [
            (f"ID={entry.cell_id}", color)
            for entry, color in zip(geometry, cell_colors)
        ]

    items = []
    seen = set()
    for entry in geometry:
        material = entry.material
        if material in seen:
            continue
        seen.add(material)
        if material == 0:
            label = "MAT=0 (VOID)"
        else:
            label = f"MAT={material}"
        items.append((label, material_map[material]))
    return items


def _add_cell_legend(fig, items, has_multi, title):
    handles = [
        Patch(facecolor=color, edgecolor="none", label=label)
        for label, color in items
    ]
    if has_multi:
        handles.append(
            Patch(
                facecolor=MULTI_COLOR,
                edgecolor="none",
                label="ID=Multi-Defined",
            )
        )

    if handles:
        fig.legend(
            handles=handles,
            loc="center left",
            bbox_to_anchor=(1.02, 0.5),
            title=title,
            frameon=False,
        )


def render_slice(
    geometry: Geometry,
    grid: SliceGrid,
    colors=None,
    background="#ffffff",
    ax=None,
    title=None,
    mark_conflicts=True,
    color_by="cell",
    material_colors=None,
    void_color=DEFAULT_VOID_COLOR,
):
    """Render a colorized CSG slice and return (figure, axes)."""
    if ax is None:
        u_span = grid.extent[1] - grid.extent[0]
        v_span = grid.extent[3] - grid.extent[2]
        figsize = (6.0, 6.0 * v_span / u_span)
        fig, ax = plt.subplots(figsize=figsize, constrained_layout=True)
    else:
        fig = ax.figure

    labels = geometry.sample(
        grid.x,
        grid.y,
        grid.z,
        mark_conflicts=mark_conflicts,
    )
    count = len(geometry)
    has_multi = bool(np.any(labels == MULTI_DEFINED))

    if count:
        cell_colors, material_map = _resolve_cell_colors(
            geometry,
            colors=colors,
            color_by=color_by,
            material_colors=material_colors,
            void_color=void_color,
        )
        if has_multi:
            plot_labels = np.where(labels == MULTI_DEFINED, count, labels)
            plot_colors = cell_colors + [MULTI_COLOR]
            color_count = count + 1
        else:
            plot_labels = labels
            plot_colors = cell_colors
            color_count = count

        cmap = ListedColormap(plot_colors).with_extremes(bad=background)
        norm = BoundaryNorm(np.arange(color_count + 1) - 0.5, color_count)
        masked = np.ma.masked_less(plot_labels, 0)
        ax.imshow(
            masked,
            origin="lower",
            extent=grid.extent,
            cmap=cmap,
            norm=norm,
            interpolation="nearest",
        )
        legend_items = _legend_items(
            geometry,
            cell_colors,
            color_by,
            material_map,
        )
        legend_title = "Cell IDs" if color_by == "cell" else "Materials"
        _add_cell_legend(
            fig,
            legend_items,
            has_multi,
            legend_title,
        )

    ax.set_facecolor(background)
    ax.set_aspect("equal")
    ax.set_xlim(grid.extent[0], grid.extent[1])
    ax.set_ylim(grid.extent[2], grid.extent[3])
    ax.set_xlabel(grid.u_label)
    ax.set_ylabel(grid.v_label)

    if title is None:
        title = _plane_title(grid.frame.plane)
    ax.set_title(title)

    return fig, ax


def save_slice(
    geometry: Geometry,
    grid: SliceGrid,
    path,
    colors=None,
    background="#ffffff",
    dpi=150,
    title=None,
    mark_conflicts=True,
    color_by="cell",
    material_colors=None,
    void_color=DEFAULT_VOID_COLOR,
):
    """Render a slice and save it to an image file."""
    fig, _ = render_slice(
        geometry,
        grid,
        colors=colors,
        background=background,
        title=title,
        mark_conflicts=mark_conflicts,
        color_by=color_by,
        material_colors=material_colors,
        void_color=void_color,
    )

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    return path
