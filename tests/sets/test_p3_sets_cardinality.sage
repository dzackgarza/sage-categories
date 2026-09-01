"""P3 acceptance tests for complete Sets() cardinal integration (PHASE-foundation-p3-sets-cardinality).

Verifies the P3 acceptance criteria:
1. Sets() evaluates exact Cardinal()-valued cardinality queries via ask(X.cardinality()).
2. Property categories Empty, Inhabited, Finite, Infinite, Countable, and Uncountable refine Sets().
3. Morphism category inhabitation Mor(Sets())(A, B), Monomorphisms(), and Isomorphisms().
4. Subobjects, from_predicate, images, and characteristic morphisms.
5. Power objects 2 ** X and their exact cardinality 2 ** #X.
6. Finite subsets and fixed-cardinality subsets with exact binomial / cardinal arithmetic.
7. Finitely supported function sets X^(S).
8. General limits and colimits on Sets().
9. Chosen enumerations, representative bijections, and the CardinalityFunctor.
"""

from __future__ import annotations

import pytest

from sage_categories.cat.category import Cat
from sage_categories.cat.functors import Fun
from sage_categories.cat.predicates import (
    AppliedQuery,
    Unknown,
    ask,
    assume,
    retract,
)
from sage_categories.kernel.refinement import is_placed, refine
from sage_categories.sets.cardinals import (
    Cardinal,
    aleph0,
    cardinality_functor,
    representative_bijection,
)
from sage_categories.sets.category import Sets, SetsCategory


def _get_sets() -> SetsCategory:
    return Sets()


# ---------------------------------------------------------------------------
# 1. Cardinality Query on Sets (X.cardinality())
# ---------------------------------------------------------------------------


def test_cardinality_query_structure() -> None:
    """X.cardinality() returns an AppliedQuery without evaluating."""
    S = _get_sets()
    f3 = S.Finite()((1, 2, 3))
    q = f3.cardinality()
    assert isinstance(q, AppliedQuery)
    assert q.query().name() == "cardinality"
    assert q.query().result_category() is Cardinal()

    # ask(X.cardinality()) evaluates to an exact CardinalObject
    res = ask(q)
    assert res in Cardinal()
    assert res is Cardinal()(3)


def test_cardinality_canonical_sets() -> None:
    """Canonical sets have exact cardinalities."""
    S = _get_sets()
    assert ask(S.Empty().cardinality()) is Cardinal()(0)
    assert ask(S.Initial().cardinality()) is Cardinal()(0)
    assert ask(S.Terminal().cardinality()) is Cardinal()(1)
    assert ask(S.Simplex(0).cardinality()) is Cardinal()(1)
    assert ask(S.Simplex(1).cardinality()) is Cardinal()(2)
    assert ask(S.Simplex(5).cardinality()) is Cardinal()(6)


def test_cardinality_unresolved_set() -> None:
    """An arbitrary rule-defined set without cardinal theorem returns Unknown."""
    S = _get_sets()
    unresolved = S(lambda d: d > 0)
    assert ask(unresolved.cardinality()) is Unknown


def test_cardinality_countable_infinite_set() -> None:
    """A set placed in both Countable() and Infinite() evaluates to aleph0."""
    S = _get_sets()
    naturals = S(lambda d: isinstance(d, int) and d >= 0)
    refine(naturals, S.Countable())
    refine(naturals, S.Infinite())
    assert ask(naturals.cardinality()) is aleph0


# ---------------------------------------------------------------------------
# 2. Property Categories on Sets()
# ---------------------------------------------------------------------------


def test_property_categories_empty_inhabited() -> None:
    """Empty and Inhabited property subcategories and predicates."""
    S = _get_sets()
    empty = S.Empty()
    single = S.Terminal()
    f3 = S.Finite()((1, 2, 3))

    assert ask(empty.is_empty()) is True
    assert ask(empty.is_inhabited()) is False

    assert ask(single.is_empty()) is False
    assert ask(single.is_inhabited()) is True

    assert ask(f3.is_empty()) is False
    assert ask(f3.is_inhabited()) is True


def test_property_categories_finite_infinite() -> None:
    """Finite and Infinite property categories."""
    S = _get_sets()
    f3 = S.Finite()((1, 2, 3))
    assert ask(f3.is_finite()) is True
    assert ask(f3.is_infinite()) is False

    inf_set = S(lambda d: True)
    refine(inf_set, S.Infinite())
    assert ask(inf_set.is_infinite()) is True
    assert ask(inf_set.is_finite()) is False


def test_property_categories_countable_uncountable() -> None:
    """Countable and Uncountable property categories and implications."""
    S = _get_sets()
    f3 = S.Finite()((1, 2, 3))
    # Finite implies Countable
    assert ask(f3.is_countable()) is True
    assert ask(f3.is_uncountable()) is False

    unc_set = S(lambda d: True)
    refine(unc_set, S.Uncountable())
    assert ask(unc_set.is_uncountable()) is True
    assert ask(unc_set.is_countable()) is False
    # Uncountable implies Infinite
    assert ask(unc_set.is_infinite()) is True
    assert ask(unc_set.is_finite()) is False


# ---------------------------------------------------------------------------
# 3. Subobjects, from_predicate, Images, and Characteristic Morphisms
# ---------------------------------------------------------------------------


def test_subobjects_from_predicate() -> None:
    """Sets().Subobjects(X).from_predicate(predicate) constructs the subobject."""
    S = _get_sets()
    f5 = S.Finite()((1, 2, 3, 4, 5))
    sub = S.Subobjects(f5).from_predicate(lambda x: x % 2 == 1)
    assert sub in S.Subobjects(f5)

    arrow = sub._structure  # the monomorphism j: S -> f5
    assert arrow.codomain() is f5
    domain = arrow.domain()
    assert ask(domain.cardinality()) is Cardinal()(3)


def test_image_of_monomorphism() -> None:
    """The image of a monomorphism retains domain cardinality."""
    S = _get_sets()
    f3 = S.Finite()((1, 2, 3))
    f5 = S.Finite()((1, 2, 3, 4, 5))
    inc = S.construct_morphism(f3, f5, lambda x: x)
    refine(inc, S.morphism_category(1).Monomorphisms())

    img = inc.image()
    assert ask(img.cardinality()) is Cardinal()(3)
    assert img.monomorphism().codomain() is f5


def test_characteristic_morphism() -> None:
    """A chosen subset has a characteristic morphism chi: X -> 2."""
    S = _get_sets()
    f4 = S.Finite()((1, 2, 3, 4))
    evens = f4.subset_from(lambda x: x % 2 == 0)
    chi = evens.characteristic_morphism()
    assert chi.domain() is f4
    assert chi.codomain() is S.Simplex(1)
    assert chi(f4.point(2)).defining_morphism()._set_morphism_data.rule(()) == 1
    assert chi(f4.point(1)).defining_morphism()._set_morphism_data.rule(()) == 0


# ---------------------------------------------------------------------------
# 4. Power Objects (2 ** X and Sets().PowerObjects()(X))
# ---------------------------------------------------------------------------


def test_power_object_construction_and_cardinality() -> None:
    """2 ** X has cardinality 2 ** #X and retains its base set."""
    S = _get_sets()
    f3 = S.Finite()((1, 2, 3))
    P = S.PowerObjects()(f3)
    assert P.base_set() is f3
    assert ask(P.cardinality()) is Cardinal()(8)

    # Top and bottom subsets
    top = P.top()
    bottom = P.bottom()
    assert ask(top.cardinality()) is Cardinal()(3)
    assert ask(bottom.cardinality()) is Cardinal()(0)


# ---------------------------------------------------------------------------
# 5. Finite Subsets and Fixed-Cardinality Subsets
# ---------------------------------------------------------------------------


def test_finite_subsets_cardinality() -> None:
    """Sets().FiniteSubsets()(X) has cardinality 2 ** #X for finite X."""
    S = _get_sets()
    f3 = S.Finite()((10, 20, 30))
    fin_subsets = S.FiniteSubsets()(f3)
    assert fin_subsets.base_set() is f3
    assert ask(fin_subsets.cardinality()) is Cardinal()(8)


def test_sized_subsets_cardinality_and_indexing() -> None:
    """Sets().SubsetsOfSize(k)(X) has cardinality binom(#X, k)."""
    S = _get_sets()
    f4 = S.Finite()((1, 2, 3, 4))
    pairs = S.SubsetsOfSize(2)(f4)
    assert ask(pairs.cardinality()) is Cardinal()(6)

    # Induced enumeration position indexing
    pt = list(pairs)[0]
    sub = pairs.subset_at(pt)
    assert ask(sub.cardinality()) is Cardinal()(2)


# ---------------------------------------------------------------------------
# 6. Finitely Supported Functions (X^(S))
# ---------------------------------------------------------------------------


def test_finitely_supported_functions_cardinality() -> None:
    """Sets().FinitelySupportedFunctions()(S, x0) for finite S."""
    S = _get_sets()
    base_set = S.Finite()((0, 1, 2))
    zero_pt = base_set.point(0)
    index_set = S.Finite()(('a', 'b'))

    finsupp = S.FinitelySupportedFunctions()(index_set, zero_pt)
    assert ask(finsupp.cardinality()) is Cardinal()(9)


# ---------------------------------------------------------------------------
# 7. Hom-Category Inhabitation on Sets()
# ---------------------------------------------------------------------------


def test_hom_inhabitation_cases() -> None:
    """Mor(Sets())(A, B).is_inhabited() respects nonemptiness conditions."""
    S = _get_sets()
    E = S.Empty()
    f3 = S.Finite()((1, 2, 3))
    f5 = S.Finite()((1, 2, 3, 4, 5))

    # Mor(E, f3) is inhabited (unique empty map)
    assert ask(S.morphism_category(1)(E, f3).is_inhabited()) is True
    # Mor(f3, E) is empty
    assert ask(S.morphism_category(1)(f3, E).is_inhabited()) is False
    # Mor(f3, f5) is inhabited
    assert ask(S.morphism_category(1)(f3, f5).is_inhabited()) is True

    # Monomorphisms: #A <= #B
    assert ask(S.morphism_category(1).Monomorphisms()(f3, f5).is_inhabited()) is True
    assert ask(S.morphism_category(1).Monomorphisms()(f5, f3).is_inhabited()) is False

    # Isomorphisms: #A == #B
    assert ask(S.morphism_category(1).Isomorphisms()(f3, f5).is_inhabited()) is False
    f3_other = S.Finite()(('a', 'b', 'c'))
    assert ask(S.morphism_category(1).Isomorphisms()(f3, f3_other).is_inhabited()) is True


# ---------------------------------------------------------------------------
# 8. Chosen Enumerations, Representative Bijections, and CardinalityFunctor
# ---------------------------------------------------------------------------


def test_chosen_enumeration_and_representative_transport() -> None:
    """Chosen enumerations supply exact representative bijections."""
    S = _get_sets()
    f3 = S.Finite()((10, 20, 30))
    assert S.Finite().chosen_enumeration(f3) == (10, 20, 30)

    # Representative bijection X -> R_3
    bij = representative_bijection(f3)
    assert bij.domain() is f3
    assert ask(bij.codomain().cardinality()) is Cardinal()(3)

    # Cardinality functor on Core(Sets())
    card_fun = cardinality_functor()
    assert card_fun.on_object(f3) is Cardinal()(3)
    assert card_fun.on_object(S.Empty()) is Cardinal()(0)
    assert card_fun.on_object(S.Terminal()) is Cardinal()(1)


# ---------------------------------------------------------------------------
# 9. General Limits and Colimits on Sets()
# ---------------------------------------------------------------------------


def test_general_limits_and_colimits() -> None:
    """General limits and colimits on Sets() over discrete shapes."""
    from sage_categories.cat.shapes import Discrete

    S = _get_sets()
    f2 = S.Finite()((0, 1))
    f3 = S.Finite()((10, 20, 30))
    I = Discrete(f2)
    diag = Fun(I, S).from_object_rule(lambda v: f3)

    lim = S.Limits(I)(diag)
    assert lim in S

    colim = S.Colimits(I)(diag)
    assert colim in S

