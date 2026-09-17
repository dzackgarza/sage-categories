"""OSCAR runs outside the package-global Catlab Julia process."""

from __future__ import annotations

import json
import tomllib
from importlib import import_module
from pathlib import Path

from sage_categories.engines import oscar
from sage_categories.engines.julia_bridge import catlab_bridge

ROOT = Path(__file__).parents[2]
ENGINE = ROOT / "src/sage_categories/engines"


def test_oscar_project_is_disjoint_from_catlab_project() -> None:
    global_project = json.loads((ROOT / "src/sage_categories/juliapkg.json").read_text())
    oscar_project = tomllib.loads((ENGINE / "OscarProject.toml").read_text())

    global_packages = set(global_project["packages"])
    assert global_packages == {"Catlab", "GATlab"}
    assert "Oscar" not in global_packages

    oscar_packages = set(oscar_project["deps"])
    assert oscar_packages == {"JSON", "Oscar"}
    assert "Catlab" not in oscar_packages
    assert "GATlab" not in oscar_packages
    assert oscar_project["compat"]["julia"] == "=1.12.7"
    assert oscar_project["compat"]["Oscar"] == "=1.8.2"


def test_oscar_worker_executes_without_loading_oscar_into_catlab() -> None:
    catlab_bridge()
    main = import_module("juliacall").Main
    assert bool(main.seval("isdefined(Main, :SageCategoriesBridge)"))
    assert not bool(main.seval("isdefined(Main, :Oscar)"))

    assert oscar.version() == "1.8.2"
    field = oscar.prime_field(5)
    one = oscar.ring_one(field)
    assert oscar.ring_contains(field, one)
    assert oscar.same_native(one, one)

    assert not bool(main.seval("isdefined(Main, :Oscar)"))


def _punctured_plane_gluing(
    left_ring,
    left_generators,
    left_chart,
    right_ring,
    right_generators,
    right_chart,
):
    left_x, left_y = left_generators
    right_x, right_y = right_generators
    left_dx = oscar.principal_open(left_chart, left_x)
    left_dy = oscar.principal_open(left_chart, left_y)
    right_dx = oscar.principal_open(right_chart, right_x)
    right_dy = oscar.principal_open(right_chart, right_y)
    left_open = oscar.affine_open_union((left_dx, left_dy))
    right_open = oscar.affine_open_union((right_dx, right_dy))

    left_x_ring, left_x_localize = oscar.localization_at_element(left_ring, left_x)
    left_y_ring, left_y_localize = oscar.localization_at_element(left_ring, left_y)
    right_x_ring, right_x_localize = oscar.localization_at_element(right_ring, right_x)
    right_y_ring, right_y_localize = oscar.localization_at_element(right_ring, right_y)

    right_to_left_x_base = oscar.hom(
        right_ring,
        left_x_ring,
        tuple(oscar.map_apply(left_x_localize, generator) for generator in left_generators),
    )
    right_to_left_y_base = oscar.hom(
        right_ring,
        left_y_ring,
        tuple(oscar.map_apply(left_y_localize, generator) for generator in left_generators),
    )
    left_to_right_x_base = oscar.hom(
        left_ring,
        right_x_ring,
        tuple(oscar.map_apply(right_x_localize, generator) for generator in right_generators),
    )
    left_to_right_y_base = oscar.hom(
        left_ring,
        right_y_ring,
        tuple(oscar.map_apply(right_y_localize, generator) for generator in right_generators),
    )

    return oscar.general_gluing(
        left_chart,
        right_chart,
        left_open,
        right_open,
        (left_dx, left_dy),
        (right_dx, right_dy),
        (
            oscar.localization_hom(right_x_ring, left_x_ring, right_to_left_x_base),
            oscar.localization_hom(right_y_ring, left_y_ring, right_to_left_y_base),
        ),
        (
            oscar.localization_hom(left_x_ring, right_x_ring, left_to_right_x_base),
            oscar.localization_hom(left_y_ring, right_y_ring, left_to_right_y_base),
        ),
    ), left_open, right_open, left_dx


def test_oscar_checks_finite_general_gluing_and_triple_cocycle() -> None:
    field = oscar.prime_field(5)
    first_ring, first_generators = oscar.polynomial_ring(field, ("x1", "y1"))
    second_ring, second_generators = oscar.polynomial_ring(field, ("x2", "y2"))
    third_ring, third_generators = oscar.polynomial_ring(field, ("x3", "y3"))
    first = oscar.affine_spec(first_ring)
    second = oscar.affine_spec(second_ring)
    third = oscar.affine_spec(third_ring)

    first_second, _first_open, second_open, first_dx = _punctured_plane_gluing(
        first_ring,
        first_generators,
        first,
        second_ring,
        second_generators,
        second,
    )
    second_third, _second_again, third_open, _second_dx = _punctured_plane_gluing(
        second_ring,
        second_generators,
        second,
        third_ring,
        third_generators,
        third,
    )
    first_third, _first_again, _third_again, _first_dx_again = _punctured_plane_gluing(
        first_ring,
        first_generators,
        first,
        third_ring,
        third_generators,
        third,
    )

    assert oscar.gluing_cocycle(first_second, second_third, first_third)
    glued = oscar.finite_covered_scheme(
        (first, second, third),
        (first_second, second_third, first_third),
    )
    assert len(oscar.covered_patches(glued)) == 3
    assert oscar.covered_open_contains(glued, first_dx, second_open)
    restriction = oscar.covered_open_restriction(glued, second_open, first_dx)
    assert oscar.same_native(oscar.domain(restriction), oscar.affine_open_section_ring(second_open))
    assert oscar.same_native(oscar.codomain(restriction), oscar.affine_coordinate_ring(first_dx))

    pulled_back = oscar.covered_chart_open_preimage(glued, first, third_open)
    assert len(oscar.affine_open_complement_equations(pulled_back)) == 2
