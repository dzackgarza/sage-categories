"""Cores and wide subcategories, and the inhabitation of fixed-endpoint categories.

Oracles: the core of a category is the wide subcategory on its isomorphisms (nLab
"core": all objects, morphisms only the isomorphisms; Mathlib ``CategoryTheory.Core``),
and a wide subcategory contains all objects and restricts morphisms to a
multiplicative class (nLab "wide subcategory"; Mathlib ``CategoryTheory.WideSubcategory``)
with a faithful inclusion (Mathlib ``wideSubcategory.faithful``); isomorphisms of sets
are the bijections (Mathlib ``CategoryTheory.isIso_iff_bijective``); a function
``A -> B`` exists exactly when ``A`` is empty or ``B`` is nonempty (Mathlib
``nonempty_fun``); a bijection ``A -> B`` exists exactly when ``#A = #B`` (Mathlib
``Cardinal.eq``) and an injection exactly when ``#A <= #B`` (Mathlib ``Cardinal.le_def``);
the identity of ``A`` witnesses ``Mor(C)(A, A)``.  Membership in a property category is
established placement (POL-CAT-043/044).
"""

import pytest

from sage_categories.all import *


def _integers():
    return Sets()(lambda datum: type(datum) is int)


def test_the_core_of_sets_contains_a_bijection_and_not_a_non_bijection() -> None:
    core = Sets().Core()
    two, three = Sets().Simplex(int(1)), Sets().Simplex(int(2))
    swap = Mor(Sets())(two, two).Isomorphisms()(lambda datum: int(1) - datum, lambda datum: int(1) - datum)
    constant = Mor(Sets())(two, two)(lambda datum: int(0))
    undecided = Mor(Sets())(two, two)(lambda datum: int(1) - datum)

    assert core is Sets().Core()
    assert core is Sets().WideSubcategory(Mor(Sets()).Isomorphisms())
    assert core in Cat()
    assert core.category() is Cat()
    assert two in core
    assert three in core
    assert swap in Mor(core)
    assert swap in Mor(core)(two, two)
    assert constant not in Mor(core)
    assert ask(Mor(core).membership_proposition(constant)) is False
    assert undecided not in Mor(core)
    assert ask(undecided.is_isomorphism()) is True
    assert undecided in Mor(core)
    assert two.identity() in Mor(core)(two, two)
    assert Mor(core)(two, two).identity() is two.identity()
    assert core.morphism_property() is Mor(Sets()).Isomorphisms()


def test_the_core_retains_a_faithful_inclusion_acting_by_identity() -> None:
    core = Sets().Core()
    two = Sets().Simplex(int(1))
    swap = Mor(Sets())(two, two).Isomorphisms()(lambda datum: int(1) - datum, lambda datum: int(1) - datum)
    (inclusion,) = core.structure_functors()

    assert inclusion is Fun(core, Sets()).Monomorphisms().Isofibrations()()
    assert inclusion in Fun(core, Sets()).Faithful()
    assert inclusion in Fun.Faithful()
    assert inclusion not in Fun.FullyFaithful()
    assert inclusion.domain() is core and inclusion.codomain() is Sets()
    assert inclusion.on_object(two) is two
    assert inclusion.on_morphism(swap) is swap
    with pytest.raises(AssertionError):
        inclusion.on_morphism(Mor(Sets())(two, two)(lambda datum: int(0)))


def test_the_core_constructs_and_composes_isomorphisms_through_the_isomorphism_category() -> None:
    core = Sets().Core()
    two, pair = Sets().Simplex(int(1)), Sets().Finite()((int(10), int(20)))
    swap = Mor(core)(two, pair)(lambda datum: int(10) * (datum + int(1)), lambda datum: datum // int(10) - int(1))
    flip = Mor(core)(pair, pair)(lambda datum: int(30) - datum, lambda datum: int(30) - datum)

    assert swap in Mor(Sets())(two, pair).Isomorphisms()
    assert swap in Mor(core)(two, pair)
    assert swap.domain() is two and swap.codomain() is pair
    assert ask(swap(two.point(int(0))) == pair.point(int(10))) is True
    composite = Mor(core)(two, pair).compose(flip, swap)
    assert composite in Mor(core)
    assert composite in Mor(Sets()).Isomorphisms()
    assert ask(composite(two.point(int(0))) == pair.point(int(20))) is True
    assert ask(composite.inverse() * composite == two.identity()) is True
    assert flip * swap in Mor(core)


def test_a_wide_subcategory_on_monomorphisms_admits_an_injection_and_not_a_collapse() -> None:
    injective = Sets().WideSubcategory(Mor(Sets()).Monomorphisms())
    two, three = Sets().Simplex(int(1)), Sets().Simplex(int(2))
    include = Mor(injective)(two, three)(lambda datum: datum)
    collapse = Mor(Sets())(three, two)(lambda datum: min(datum, int(1)))

    assert injective is not Sets().Core()
    assert three in injective
    assert include in Mor(injective)
    assert include in Mor(Sets()).Monomorphisms()
    assert ask(collapse.is_monomorphism()) is False
    assert collapse not in Mor(injective)
    assert three.identity() in Mor(injective)(three, three)
    assert Mor(injective)(two, three).compose(three.identity(), include) in Mor(injective)


def test_fixed_endpoint_inhabitation_in_sets_is_decided_from_cardinalities() -> None:
    two, three, empty = Sets().Simplex(int(1)), Sets().Simplex(int(2)), Sets().Empty()
    integers, words = _integers(), Sets()(lambda datum: type(datum) is str)

    assert ask(Mor(Sets())(two, three).is_inhabited()) is True
    assert ask(Mor(Sets())(three, empty).is_inhabited()) is False
    assert ask(Mor(Sets())(three, empty).is_empty()) is True
    assert ask(Mor(Sets())(empty, three).is_inhabited()) is True
    assert ask(Mor(Sets())(empty, empty).is_inhabited()) is True
    assert ask(Mor(Sets())(integers, words).is_inhabited()) is Unknown
    assert ask(Mor(Sets())(integers, words).is_empty()) is Unknown
    assert ask(Mor(Sets())(integers, integers).is_inhabited()) is True
    assert ask(Mor(Sets())(integers, three).is_inhabited()) is True
    assert ask(Mor(Sets())(integers, empty).is_inhabited()) is Unknown
    with pytest.raises(TypeError):
        bool(Mor(Sets())(two, three).is_inhabited())


def test_fixed_endpoint_inhabitation_of_property_narrowings_and_the_core() -> None:
    two, three = Sets().Simplex(int(1)), Sets().Simplex(int(2))
    core = Sets().Core()

    assert ask(Mor(Sets()).Isomorphisms()(two, three).is_inhabited()) is False
    assert ask(Mor(Sets()).Isomorphisms()(two, two).is_inhabited()) is True
    assert ask(Mor(Sets()).Monomorphisms()(two, three).is_inhabited()) is True
    assert ask(Mor(Sets()).Monomorphisms()(three, two).is_inhabited()) is False
    assert ask(Mor(Sets()).Monomorphisms()(three, two).is_empty()) is True
    assert ask(Mor(Sets()).Epimorphisms()(two, three).is_inhabited()) is Unknown
    assert ask(Mor(core)(two, three).is_inhabited()) is False
    assert ask(Mor(core)(two, two).is_inhabited()) is True
    assert ask(Mor(core)(two, three).is_empty()) is True
    assert ask(Mor(Sets().Finite())(two, three).is_inhabited()) is True
    assert ask(Mor(Sets().Finite())(three, Sets().Empty()).is_inhabited()) is False
    assert ask(Fun(Sets(), Sets()).is_inhabited()) is True
    assert ask(Fun(Sets(), Cat()).is_inhabited()) is Unknown
