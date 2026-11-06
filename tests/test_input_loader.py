import pytest

import geom_syntax
from _geom_syntax_core import CellSyntaxError, InputSyntaxError
from mcnp_geom_syntax import load_mcnp_text
from phits_geom_syntax import load_phits_text


MCNP_TEXT = """Simple MCNP model
1 0 -1
2 0 1

1 SO 1
"""


PHITS_TEXT = """Simple PHITS model
[Cell]
1 0 -1
2 0 1

[Surface]
1 so 1
"""


def test_load_mcnp_text():
    model = load_mcnp_text(MCNP_TEXT)

    assert model.syntax == "mcnp"
    assert model.title == "Simple MCNP model"
    assert model.geometry.cell_ids == [1, 2]
    assert set(model.surfaces) == {1}
    assert model.geometry.find_cell(0.0, 0.0, 0.0) == 0
    assert model.geometry.find_cell(2.0, 0.0, 0.0) == 1


def test_load_phits_text():
    model = load_phits_text(PHITS_TEXT)

    assert model.syntax == "phits"
    assert model.title == "Simple PHITS model"
    assert model.geometry.cell_ids == [1, 2]
    assert model.geometry.find_cell(0.0, 0.0, 0.0) == 0
    assert model.geometry.find_cell(2.0, 0.0, 0.0) == 1


def test_mcnp_cell_reference_and_options():
    text = """MCNP reference
1 0 -1
2 0 #1
3 0 1 imp:n=1

1 SO 1
"""
    model = load_mcnp_text(text)

    assert model.geometry.find_cell(0.0, 0.0, 0.0) == 0
    assert model.geometry.find_cell(2.0, 0.0, 0.0) == 1
    assert model.cells[2].options == ("imp:n=1",)


def test_mcnp_material_and_density():
    text = """Material model
1 2 -1.5 -1

1 SO 1
"""
    model = load_mcnp_text(text)
    parsed = model.cells[0]

    assert parsed.material == 2
    assert parsed.density == -1.5
    assert model.geometry.entries[0].material == 2
    assert model.geometry.entries[0].density == -1.5


def test_phits_cell_keyword():
    text = """PHITS keyword
[Cell]
cell 1 0 -1

[Surface]
1 so 1
"""
    model = load_phits_text(text)

    assert model.geometry.cell_ids == [1]
    assert model.geometry.find_cell(0.0, 0.0, 0.0) == 0


def test_detect_syntax_and_auto_parse():
    assert geom_syntax.detect_syntax(MCNP_TEXT) == "mcnp"
    assert geom_syntax.detect_syntax(PHITS_TEXT) == "phits"

    mcnp_model = geom_syntax.parse_geometry(MCNP_TEXT)
    phits_model = geom_syntax.parse_geometry(PHITS_TEXT)

    assert mcnp_model.syntax == "mcnp"
    assert phits_model.syntax == "phits"


def test_get_syntax_is_case_insensitive():
    assert geom_syntax.get_syntax("MCNP").name == "mcnp"
    assert geom_syntax.get_syntax("phits").name == "phits"

    with pytest.raises(ValueError):
        geom_syntax.get_syntax("unknown")


def test_load_geometry_from_path(tmp_path):
    path = tmp_path / "model.inp"
    path.write_text(MCNP_TEXT, encoding="utf-8")

    model = geom_syntax.load_geometry(path)

    assert model.syntax == "mcnp"
    assert model.geometry.cell_ids == [1, 2]


def test_load_geometry_from_text():
    model = geom_syntax.load_geometry(PHITS_TEXT)

    assert model.syntax == "phits"


def test_missing_mcnp_surface_block():
    with pytest.raises(InputSyntaxError):
        load_mcnp_text("Title\n1 0 -1\n")


def test_missing_phits_section():
    with pytest.raises(InputSyntaxError):
        load_phits_text("[Cell]\n1 0 -1\n")


def test_like_cell_inherits_geometry_and_overrides_parameters():
    text = """title
1 0 -10
2 1 -1.0 11 -12
3 LIKE 2 BUT TRCL=1 MAT=2 RHO=2.5

10 SO 5
11 PX -2
12 PX 2

TR1 10 0 0 1 0 0 0 1 0 0 0 1
"""
    model = load_mcnp_text(text)

    assert [cell.cell_id for cell in model.cells] == [1, 2, 3]
    assert model.cells[2].material == 2
    assert model.cells[2].density == 2.5
    assert model.cells[2].transform_id == 1
    assert model.geometry.find_cell(10.0, 0.0, 0.0) == 2


def test_like_cell_requires_prior_target():
    text = """title
2 LIKE 1 BUT MAT=1
1 0 -1

1 SO 2
"""
    with pytest.raises(CellSyntaxError, match="not defined"):
        load_mcnp_text(text)


@pytest.mark.parametrize("option", ["u=1", "lat=1", "fill=2"])
def test_unsupported_geometry_options_are_rejected(option):
    text = f"""title
1 0 -1 {option}

1 SO 2
"""
    with pytest.raises(CellSyntaxError, match="not supported"):
        load_mcnp_text(text)
