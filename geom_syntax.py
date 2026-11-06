"""Common MCNP/PHITS geometry syntax interface."""

import re
from pathlib import Path

from _geom_syntax_core import (
    CellSyntaxError,
    InputSyntaxError,
    LoadedModel,
    ParsedCell,
    ParsedSurface,
    SurfaceSyntaxError,
)
from mcnp_geom_syntax import MCNPGeomSyntax
from phits_geom_syntax import PHITSGeomSyntax


_SYNTAXES = {
    "mcnp": MCNPGeomSyntax(),
    "phits": PHITSGeomSyntax(),
}

_SECTION_RE = re.compile(r"^\s*\[(cell|surface)\]\s*$", re.IGNORECASE | re.MULTILINE)


def detect_syntax(text):
    """Return 'phits' when PHITS section headers are present, else 'mcnp'."""
    if _SECTION_RE.search(text):
        return "phits"
    return "mcnp"


def get_syntax(name):
    try:
        return _SYNTAXES[name.lower()]
    except KeyError:
        raise ValueError(f"unknown geometry syntax: {name!r}") from None


def parse_geometry(text, syntax="auto"):
    """Parse input text into LoadedModel."""
    if syntax == "auto":
        syntax = detect_syntax(text)
    return get_syntax(syntax).load(text)


def load_geometry(source, syntax="auto"):
    """Parse a path or input text into LoadedModel."""
    if isinstance(source, Path):
        text = source.read_text(encoding="utf-8")
    elif isinstance(source, str) and "\n" not in source:
        path = Path(source)
        text = path.read_text(encoding="utf-8") if path.is_file() else source
    else:
        text = str(source)

    return parse_geometry(text, syntax=syntax)


__all__ = [
    "CellSyntaxError",
    "InputSyntaxError",
    "LoadedModel",
    "ParsedCell",
    "ParsedSurface",
    "SurfaceSyntaxError",
    "detect_syntax",
    "get_syntax",
    "load_geometry",
    "parse_geometry",
]
