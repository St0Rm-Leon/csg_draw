import pytest

import cell
import cell_syntax
import geometry
import shapes as sp
from cell import CellReference, Complement, Intersection, SurfaceTerm, Union


SURFACES = {
    1: sp.OSphere(1),
    2: sp.Plane(1, 0, 0, 0),
    3: sp.Sphere(2, 0, 0, 1),
    4: sp.ZCylinder(0, 0, 1),
}


def test_parse_intersection_expression():
    expression = cell_syntax.parse_mcnp_expression("-1 2 -3", SURFACES)

    assert isinstance(expression, Intersection)
    assert [term.sign for term in expression.children] == [-1, 1, -1]
    assert [term.surface for term in expression.children] == [
        SURFACES[1],
        SURFACES[2],
        SURFACES[3],
    ]


def test_parse_union_expression():
    expression = cell_syntax.parse_mcnp_expression("-1 : -3", SURFACES)

    assert isinstance(expression, Union)
    assert len(expression.children) == 2
    assert all(isinstance(child, SurfaceTerm) for child in expression.children)


def test_union_has_lower_precedence_than_intersection():
    expression = cell_syntax.parse_mcnp_expression("-1 2 : -3", SURFACES)

    assert isinstance(expression, Union)
    assert isinstance(expression.children[0], Intersection)
    assert isinstance(expression.children[1], SurfaceTerm)


def test_parenthesized_expression():
    expression = cell_syntax.parse_mcnp_expression("(-1 2 : -3) 4", SURFACES)

    assert isinstance(expression, Intersection)
    assert isinstance(expression.children[0], Union)
    assert isinstance(expression.children[1], SurfaceTerm)
    assert expression.children[1].surface is SURFACES[4]


def test_complement_cell_reference():
    expression = cell_syntax.parse_mcnp_expression(
        "#5",
        SURFACES,
        known_cell_ids={5},
    )

    assert isinstance(expression, Complement)
    assert isinstance(expression.child, CellReference)
    assert expression.child.cell_id == 5


def test_complement_parenthesized_expression():
    expression = cell_syntax.parse_mcnp_expression("#(-1 : -3)", SURFACES)

    assert isinstance(expression, Complement)
    assert isinstance(expression.child, Union)


def test_parsed_expression_can_be_evaluated():
    expression = cell_syntax.parse_mcnp_expression("-1 : -3", SURFACES)
    parsed_cell = cell.Cell(expression)

    assert parsed_cell.is_inside_cell(0.0, 0.0, 0.0) is True
    assert parsed_cell.is_inside_cell(2.0, 0.0, 0.0) is True
    assert parsed_cell.is_inside_cell(4.0, 0.0, 0.0) is False


def test_parse_mcnp_cell_card():
    parsed = cell_syntax.parse_mcnp_cell(
        "10 1 -1.0 -1 2 -3 imp:n=1",
        SURFACES,
    )

    assert parsed.cell_id == 10
    assert parsed.material == 1
    assert parsed.density == -1.0
    assert isinstance(parsed.expression, Intersection)
    assert parsed.options == ("imp:n=1",)
    assert parsed.option_dict == {"imp:n": "1"}
    assert isinstance(parsed.to_cell(), cell.Cell)


def test_parse_void_cell_without_density():
    parsed = cell_syntax.parse_mcnp_cell("20 0 -1 2", SURFACES)

    assert parsed.cell_id == 20
    assert parsed.material == 0
    assert parsed.density is None
    assert isinstance(parsed.expression, Intersection)


def test_parse_scientific_density_and_comment():
    parsed = cell_syntax.parse_mcnp_cell(
        "30 2 1.0e-3 -1 2 $ material cell",
        SURFACES,
    )

    assert parsed.density == pytest.approx(1.0e-3)
    assert parsed.options == ()


def test_phits_cell_and_expression_match_mcnp():
    mcnp = cell_syntax.parse_mcnp_cell(
        "1 1 -1.0 -1 2 -3",
        SURFACES,
    )
    phits = cell_syntax.parse_phits_cell(
        "1 1 -1.0 -1 2 -3",
        SURFACES,
    )

    assert mcnp.cell_id == phits.cell_id
    assert mcnp.material == phits.material
    assert mcnp.density == phits.density
    assert isinstance(phits.expression, Intersection)
    assert mcnp.to_cell().is_inside_cell(0.0, 0.0, 0.0) == (
        phits.to_cell().is_inside_cell(0.0, 0.0, 0.0)
    )


def test_phits_expression_parser():
    expression = cell_syntax.parse_phits_expression("(-1 2 : -3)", SURFACES)

    assert isinstance(expression, Union)
    assert isinstance(expression.children[0], Intersection)


def test_phits_cell_keyword_prefix():
    parsed = cell_syntax.parse_phits_cell(
        "cell 1 1 -1.0 -1",
        SURFACES,
    )

    assert parsed.cell_id == 1
    assert parsed.material == 1
    assert parsed.density == -1.0


def test_parsed_complement_cell_works_in_geometry():
    parsed = cell_syntax.parse_mcnp_cell(
        "2 0 #1",
        SURFACES,
        known_cell_ids={1, 2},
    )
    space = geometry.Geometry([
        geometry.CellEntry(cell.Cell([-SURFACES[1]]), cell_id=1),
        geometry.CellEntry(parsed.to_cell(), cell_id=2),
    ])

    assert space.find_cell(0.0, 0.0, 0.0) == 0
    assert space.find_cell(2.0, 0.0, 0.0) == 1


def test_unknown_surface_raises():
    with pytest.raises(cell_syntax.CellSyntaxError, match="unknown surface"):
        cell_syntax.parse_mcnp_expression("-99", SURFACES)


def test_unknown_cell_reference_raises():
    with pytest.raises(cell_syntax.CellSyntaxError, match="unknown cell"):
        cell_syntax.parse_mcnp_expression(
            "#99",
            SURFACES,
            known_cell_ids={1},
        )


@pytest.mark.parametrize("text", [
    "",
    "(",
    "()",
    "-1 :",
    ": -1",
    "-1 )",
    "-1 (",
    "1 foo",
])
def test_invalid_expression_raises(text):
    with pytest.raises(cell_syntax.CellSyntaxError):
        cell_syntax.parse_mcnp_expression(text, SURFACES)


@pytest.mark.parametrize("line", [
    "1 1",
    "1 1 not-a-density -1",
    "1 1 -1.0 imp:n=1",
    "0 0 -1",
])
def test_invalid_cell_card_raises(line):
    with pytest.raises(cell_syntax.CellSyntaxError):
        cell_syntax.parse_mcnp_cell(line, SURFACES)
