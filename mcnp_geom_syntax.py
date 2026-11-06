"""MCNP surface/cell/input syntax interpreter."""

import re

import transforms
from _geom_syntax_core import (
    GeomSyntax,
    InputSyntaxError,
    TOKEN_RE,
    UNSIGNED_INT_RE,
    _is_comment_line,
    build_loaded_model,
    parse_cell_line,
    parse_cell_lines,
    parse_expression,
    parse_surface_block,
    parse_surface_line,
)


_TRANSFORM_RE = re.compile(r"^\*?TR(\d+)$", re.IGNORECASE)


class MCNPGeomSyntax(GeomSyntax):
    name = "mcnp"

    def load(self, text):
        return load_mcnp_text(text)


MCNP = MCNPGeomSyntax()


def parse_mcnp_expression(text, surfaces, known_cell_ids=None):
    return parse_expression(text, surfaces, known_cell_ids)


def parse_mcnp_surface(line):
    return parse_surface_line(line)


def parse_mcnp_surfaces(lines, transforms=None):
    return parse_surface_block(lines, transforms)


def parse_mcnp_cell(line, surfaces, known_cell_ids=None):
    return parse_cell_line(
        line,
        surfaces,
        known_cell_ids=known_cell_ids,
        allow_cell_keyword=False,
        allow_inline_transform=False,
    )


def parse_mcnp_cells(lines, surfaces, known_cell_ids=None):
    return parse_cell_lines(
        lines,
        surfaces,
        known_cell_ids=known_cell_ids,
        allow_cell_keyword=False,
        allow_inline_transform=False,
    )


def parse_mcnp_transform_line(line):
    clean_line = line.split("$", 1)[0].strip()
    tokens = clean_line.split()
    if not tokens:
        raise InputSyntaxError("empty MCNP transform card")

    match = _TRANSFORM_RE.fullmatch(tokens[0])
    if match is None:
        raise InputSyntaxError(
            f"invalid MCNP transform card: {tokens[0]!r}"
        )
    if len(tokens) != 13:
        raise InputSyntaxError(
            "MCNP transform needs a name and 12 values"
        )

    number = int(match.group(1))
    if number <= 0:
        raise InputSyntaxError("transform number must be positive")

    try:
        values = [float(token) for token in tokens[1:]]
    except ValueError:
        raise InputSyntaxError("invalid numeric transform parameter") from None

    try:
        return transforms.Transform.from_mcnp(number, values)
    except ValueError as exc:
        raise InputSyntaxError(str(exc)) from exc


def parse_mcnp_transforms(lines):
    result = {}
    for line in lines:
        stripped = line.split("$", 1)[0].strip()
        if not stripped or _is_comment_line(line):
            continue
        if _TRANSFORM_RE.fullmatch(stripped.split()[0]) is None:
            continue

        transform = parse_mcnp_transform_line(line)
        if transform.number in result:
            raise InputSyntaxError(
                f"duplicate transform number: {transform.number}"
            )
        result[transform.number] = transform
    return result


def _split_mcnp_blocks(text):
    lines = text.splitlines()
    if not lines:
        raise InputSyntaxError("empty MCNP input")

    title = lines[0].strip()
    blocks = []
    current = []

    for line in lines[1:]:
        stripped = line.split("$", 1)[0].strip()
        if not stripped:
            if current:
                blocks.append(current)
                current = []
            continue

        if _is_comment_line(line):
            continue

        current.append(line)

    if current:
        blocks.append(current)

    if len(blocks) < 2:
        raise InputSyntaxError(
            "MCNP input needs cell and surface blocks"
        )

    return title, blocks


def _known_cell_ids(lines):
    ids = set()
    for line in lines:
        tokens = TOKEN_RE.findall(line.split("$", 1)[0])
        if tokens and UNSIGNED_INT_RE.fullmatch(tokens[0]):
            ids.add(int(tokens[0]))
    return ids


def load_mcnp_text(text):
    title, blocks = _split_mcnp_blocks(text)
    cell_lines = blocks[0]
    surface_lines = blocks[1]
    transform_lines = [
        line
        for block in blocks[2:]
        for line in block
    ]

    transforms_by_id = parse_mcnp_transforms(transform_lines)
    surfaces = parse_mcnp_surfaces(surface_lines, transforms_by_id)
    known_ids = _known_cell_ids(cell_lines)
    cells = parse_mcnp_cells(
        cell_lines,
        surfaces,
        known_cell_ids=known_ids,
    )

    return build_loaded_model(
        "mcnp",
        title,
        surfaces,
        cells,
        transforms=transforms_by_id,
    )
