"""Backward-compatible cell syntax imports.

New code should use mcnp_geom_syntax / phits_geom_syntax / geom_syntax.
"""

from _geom_syntax_core import CellSyntaxError, ParsedCell
from mcnp_geom_syntax import (
    parse_mcnp_cell,
    parse_mcnp_cells,
    parse_mcnp_expression,
    parse_mcnp_surface,
    parse_mcnp_surfaces,
)
from phits_geom_syntax import (
    parse_phits_cell,
    parse_phits_cells,
    parse_phits_expression,
    parse_phits_surface,
    parse_phits_surfaces,
)


__all__ = [
    "CellSyntaxError",
    "ParsedCell",
    "parse_mcnp_cell",
    "parse_mcnp_cells",
    "parse_mcnp_expression",
    "parse_mcnp_surface",
    "parse_mcnp_surfaces",
    "parse_phits_cell",
    "parse_phits_cells",
    "parse_phits_expression",
    "parse_phits_surface",
    "parse_phits_surfaces",
]
