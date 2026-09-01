"""P7 acceptance tests for algebras (PHASE-foundation-p7-algebras).

Verifies the P7 acceptance criteria:
1. Algebras(R, C) constructs algebra objects over a base ring/monoid R in ambient C.
2. Algebras(R, C).monoid_presentation() is the unique immediate structure functor to Monoids(V_R).
3. Algebras(R, C).U_R() constructs the composite forgetful functor to C.
4. Algebras(R, C).Commutative() property subcategory is defined and accessible.
5. Algebras(R, C).presentation(generators, relations) retains polynomial generators, relations, and evaluation morphism.
"""

from __future__ import annotations

import pytest
from sage.rings.integer import Integer

from sage_categories.algebra import (
    AlgebraPresentation,
    Algebras,
    Modules,
    Rings,
)
from sage_categories.sets.category import Sets


# ---------------------------------------------------------------------------
# 1. Algebras Construction and Object Surface (specs/algebras.md)
# ---------------------------------------------------------------------------


def test_algebras_construction_and_object_surface() -> None:
    """Algebras(R, C) constructs algebra objects from module objects and algebra operations."""
    S = Sets()
    carrier_R = S.Simplex(2)
    square_R = carrier_R * carrier_R
    add_R = S.morphism_category(1)(square_R, carrier_R)(lambda fam: fam(0))
    zero_R = S.morphism_category(1)(S.Terminal(), carrier_R)(lambda _: 0)
    mult_R = S.morphism_category(1)(square_R, carrier_R)(lambda fam: fam(0))
    one_R = S.morphism_category(1)(S.Terminal(), carrier_R)(lambda _: 1)
    inv_R = S.morphism_category(1)(carrier_R, carrier_R)(lambda x: x)
    R = Rings(S)(carrier_R, add_R, zero_R, mult_R, one_R, inv_R)

    alg_cat = Algebras(R, S)
    assert alg_cat.base() is R
    assert alg_cat.ambient() is S
    assert alg_cat.module_category() is not None

    # Underlying module object B
    carrier_B = S.Simplex(3)
    prod_RB = carrier_R * carrier_B
    rho_B = S.morphism_category(1)(prod_RB, carrier_B)(lambda pair: pair(1))
    mod_B = alg_cat.module_category()(rho_B)

    # Algebra operations
    prod_BB = carrier_B * carrier_B
    mult_B = S.morphism_category(1)(prod_BB, carrier_B)(lambda pair: pair(0))
    unit_B = S.morphism_category(1)(carrier_R, carrier_B)(lambda _: 0)

    A = alg_cat(mod_B, mult_B, unit_B)
    assert A.module() is mod_B
    assert A.carrier() is carrier_B
    assert A.multiplication() is mult_B
    assert A.unit_morphism() is unit_B


# ---------------------------------------------------------------------------
# 2. Monoid Presentation Structure Functor (specs/algebras.md)
# ---------------------------------------------------------------------------


def test_algebras_monoid_presentation_structure_functor() -> None:
    """monoid_presentation() is the unique immediate structure functor to Monoids(V_R)."""
    S = Sets()
    carrier_R = S.Simplex(2)
    square_R = carrier_R * carrier_R
    add_R = S.morphism_category(1)(square_R, carrier_R)(lambda fam: fam(0))
    zero_R = S.morphism_category(1)(S.Terminal(), carrier_R)(lambda _: 0)
    mult_R = S.morphism_category(1)(square_R, carrier_R)(lambda fam: fam(0))
    one_R = S.morphism_category(1)(S.Terminal(), carrier_R)(lambda _: 1)
    inv_R = S.morphism_category(1)(carrier_R, carrier_R)(lambda x: x)
    R = Rings(S)(carrier_R, add_R, zero_R, mult_R, one_R, inv_R)

    alg_cat = Algebras(R, S)
    struct = alg_cat.structure_functors()
    assert len(struct) == 1

    pres_functor = alg_cat.monoid_presentation()
    assert struct[0] == pres_functor

    # Test projection on object
    carrier_B = S.Simplex(3)
    prod_RB = carrier_R * carrier_B
    rho_B = S.morphism_category(1)(prod_RB, carrier_B)(lambda pair: pair(1))
    mod_B = alg_cat.module_category()(rho_B)

    prod_BB = carrier_B * carrier_B
    mult_B = S.morphism_category(1)(prod_BB, carrier_B)(lambda pair: pair(0))
    unit_B = S.morphism_category(1)(carrier_R, carrier_B)(lambda _: 0)

    A = alg_cat(mod_B, mult_B, unit_B)
    monoid_obj = pres_functor.on_object(A)
    assert monoid_obj.carrier() is mod_B
    assert monoid_obj.multiplication() is mult_B
    assert monoid_obj.unit_morphism() is unit_B


# ---------------------------------------------------------------------------
# 3. Composite Functor U_R and Commutative Subcategory (specs/algebras.md)
# ---------------------------------------------------------------------------


def test_algebras_composite_U_R_and_commutative() -> None:
    """U_R constructs the composite forgetful functor to C, and Commutative() is accessible."""
    S = Sets()
    carrier_R = S.Simplex(2)
    square_R = carrier_R * carrier_R
    add_R = S.morphism_category(1)(square_R, carrier_R)(lambda fam: fam(0))
    zero_R = S.morphism_category(1)(S.Terminal(), carrier_R)(lambda _: 0)
    mult_R = S.morphism_category(1)(square_R, carrier_R)(lambda fam: fam(0))
    one_R = S.morphism_category(1)(S.Terminal(), carrier_R)(lambda _: 1)
    inv_R = S.morphism_category(1)(carrier_R, carrier_R)(lambda x: x)
    R = Rings(S)(carrier_R, add_R, zero_R, mult_R, one_R, inv_R)

    alg_cat = Algebras(R, S)
    assert alg_cat.Commutative() is not None

    U_R = alg_cat.U_R()
    carrier_B = S.Simplex(3)
    prod_RB = carrier_R * carrier_B
    rho_B = S.morphism_category(1)(prod_RB, carrier_B)(lambda pair: pair(1))
    mod_B = alg_cat.module_category()(rho_B)

    A = alg_cat(mod_B, None, None)
    assert U_R.on_object(A) is carrier_B


# ---------------------------------------------------------------------------
# 4. Finite Presentation of Commutative Algebras (specs/separating-families-and-categorical-generators.md)
# ---------------------------------------------------------------------------


def test_algebra_polynomial_presentation() -> None:
    """presentation(generators, relations) retains polynomial presentation data."""
    S = Sets()
    carrier_R = S.Simplex(2)
    square_R = carrier_R * carrier_R
    add_R = S.morphism_category(1)(square_R, carrier_R)(lambda fam: fam(0))
    zero_R = S.morphism_category(1)(S.Terminal(), carrier_R)(lambda _: 0)
    mult_R = S.morphism_category(1)(square_R, carrier_R)(lambda fam: fam(0))
    one_R = S.morphism_category(1)(S.Terminal(), carrier_R)(lambda _: 1)
    inv_R = S.morphism_category(1)(carrier_R, carrier_R)(lambda x: x)
    R = Rings(S)(carrier_R, add_R, zero_R, mult_R, one_R, inv_R)

    alg_cat = Algebras(R, S)

    # Presentation of R[x, y] / (x^2 - y)
    pres = alg_cat.presentation(("x", "y"), ("x^2 - y",))

    assert isinstance(pres, AlgebraPresentation)
    assert pres.generators == ("x", "y")
    assert pres.relations == ("x^2 - y",)
    assert pres.presented_algebra is not None
    assert pres.free_algebra_on_generators is not None
    assert pres.evaluation_morphism is not None
