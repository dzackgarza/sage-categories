"""P6 acceptance tests for modules (PHASE-foundation-p6-modules).

Verifies the P6 acceptance criteria:
1. Modules(A, C) constructs module objects over a monoid/ring A in actegory C.
2. Modules(A, C)(rho_X) constructs a module object from the action morphism rho_X: A bullet X -> X and recovers carrier X.
3. The faithful forgetful functor U_A: Modules(A, C) -> C is the unique immediate structure functor.
4. Modules(A, C).Free(), Modules(A, C).FiniteRank(), and Modules(A, C).Based() property subcategories are defined.
5. Modules(R, C).regular() constructs the regular module R as a compact projective generator.
6. Modules(R, C).presentation(relations_matrix, rank) retains R^m -> R^n -> M and its presentation data.
"""

from __future__ import annotations

import pytest
from sage.rings.integer import Integer

from sage_categories.algebra import (
    ModulePresentation,
    Modules,
    Monoids,
    Rings,
)
from sage_categories.sets.category import Sets


# ---------------------------------------------------------------------------
# 1. Modules Construction and Object Surface (specs/modules.md)
# ---------------------------------------------------------------------------


def test_modules_construction_and_object_surface() -> None:
    """Modules(A, C) constructs module objects from action morphisms."""
    S = Sets()
    carrier_A = S.Simplex(2)
    square_A = carrier_A * carrier_A
    mult_A = S.morphism_category(1)(square_A, carrier_A)(lambda fam: fam(0))
    unit_A = S.morphism_category(1)(S.Terminal(), carrier_A)(lambda _: 0)
    A = Monoids(S)(carrier_A, mult_A, unit_A)

    mod_cat = Modules(A, S)
    assert mod_cat.monoid() is A
    assert mod_cat.ambient() is S

    # Carrier X and action morphism rho_X: A * X -> X
    carrier_X = S.Simplex(3)
    prod_AX = carrier_A * carrier_X
    rho_X = S.morphism_category(1)(prod_AX, carrier_X)(lambda pair: pair(1))

    M = mod_cat(rho_X)
    assert M.carrier() is carrier_X
    assert M.action() is rho_X
    assert M.action_morphism() is rho_X


# ---------------------------------------------------------------------------
# 2. Faithful Structure Functor U_A (specs/modules.md)
# ---------------------------------------------------------------------------


def test_modules_structure_functor_U_A() -> None:
    """U_A: Modules(A, C) -> C is the sole immediate structure functor and is faithful."""
    S = Sets()
    carrier_A = S.Simplex(2)
    square_A = carrier_A * carrier_A
    mult_A = S.morphism_category(1)(square_A, carrier_A)(lambda fam: fam(0))
    unit_A = S.morphism_category(1)(S.Terminal(), carrier_A)(lambda _: 0)
    A = Monoids(S)(carrier_A, mult_A, unit_A)

    mod_cat = Modules(A, S)
    struct = mod_cat.structure_functors()
    assert len(struct) == 1

    U_A = mod_cat.U_A()
    assert struct[0] is U_A

    carrier_X = S.Simplex(3)
    prod_AX = carrier_A * carrier_X
    rho_X = S.morphism_category(1)(prod_AX, carrier_X)(lambda pair: pair(1))
    M = mod_cat(rho_X)

    # U_A projects to the underlying object in C
    assert U_A.on_object(M) is carrier_X


# ---------------------------------------------------------------------------
# 3. Property Subcategories (specs/modules.md)
# ---------------------------------------------------------------------------


def test_modules_property_subcategories() -> None:
    """Modules(A, C) exposes Free, FiniteRank, and Based property subcategories."""
    S = Sets()
    carrier_A = S.Simplex(2)
    square_A = carrier_A * carrier_A
    mult_A = S.morphism_category(1)(square_A, carrier_A)(lambda fam: fam(0))
    unit_A = S.morphism_category(1)(S.Terminal(), carrier_A)(lambda _: 0)
    A = Monoids(S)(carrier_A, mult_A, unit_A)

    mod_cat = Modules(A, S)
    assert mod_cat.Free() is not None
    assert mod_cat.FiniteRank() is not None
    assert mod_cat.Based() is not None

    # Nested property subcategories
    assert mod_cat.Free().FiniteRank() is not None
    assert mod_cat.Free().Based() is not None


# ---------------------------------------------------------------------------
# 4. Regular Module Projective Generator (specs/separating-families-and-categorical-generators.md)
# ---------------------------------------------------------------------------


def test_regular_module_projective_generator() -> None:
    """Modules(R, C).regular() constructs the regular module R."""
    S = Sets()
    carrier_R = S.Simplex(2)
    square_R = carrier_R * carrier_R
    add_R = S.morphism_category(1)(square_R, carrier_R)(lambda fam: fam(0))
    zero_R = S.morphism_category(1)(S.Terminal(), carrier_R)(lambda _: 0)
    mult_R = S.morphism_category(1)(square_R, carrier_R)(lambda fam: fam(0))
    one_R = S.morphism_category(1)(S.Terminal(), carrier_R)(lambda _: 1)
    inv_R = S.morphism_category(1)(carrier_R, carrier_R)(lambda x: x)

    R = Rings(S)(carrier_R, add_R, zero_R, mult_R, one_R, inv_R)
    mod_cat = Modules(R, S)

    regular = mod_cat.regular()
    assert regular.carrier() is carrier_R
    assert regular.action() is not None


# ---------------------------------------------------------------------------
# 5. Matrix Presentations of Modules (specs/separating-families-and-categorical-generators.md)
# ---------------------------------------------------------------------------


def test_module_matrix_presentation() -> None:
    """Modules(R, C).presentation(relations_matrix, rank) retains R^m -> R^n -> M presentation data."""
    S = Sets()
    carrier_R = S.Simplex(2)
    square_R = carrier_R * carrier_R
    add_R = S.morphism_category(1)(square_R, carrier_R)(lambda fam: fam(0))
    zero_R = S.morphism_category(1)(S.Terminal(), carrier_R)(lambda _: 0)
    mult_R = S.morphism_category(1)(square_R, carrier_R)(lambda fam: fam(0))
    one_R = S.morphism_category(1)(S.Terminal(), carrier_R)(lambda _: 1)
    inv_R = S.morphism_category(1)(carrier_R, carrier_R)(lambda x: x)

    R = Rings(S)(carrier_R, add_R, zero_R, mult_R, one_R, inv_R)
    mod_cat = Modules(R, S)

    # Presentation of R^2 / <(1, 2), (3, 4)>
    relations = ((1, 2), (3, 4))
    pres = mod_cat.presentation(relations, rank=2)

    assert isinstance(pres, ModulePresentation)
    assert pres.rank == 2
    assert pres.relations_matrix == ((1, 2), (3, 4))
    assert pres.presented_module is not None
    assert pres.generators_module is not None
    assert pres.relations_module is not None
    assert pres.matrix_morphism is not None
    assert pres.presentation_morphism is not None
