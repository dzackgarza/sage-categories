"""Finite presented category path computation is owned by GAP FpCategories."""

from sage_categories.cat.canonical import (
    FinitePresentedCategory,
    simplex,
    walking_isomorphism,
)
from sage_categories.cat.predicates import Unknown, ask
from sage_categories.engines import fp_categories


def test_native_finite_presented_category_paths() -> None:
    triangle = simplex(2)
    arrows = triangle.finite_morphisms()
    assert arrows is not Unknown
    assert tuple((triangle.label(a.domain()), triangle.label(a.codomain()), a.word()) for a in arrows) == (
        (0, 0, ()),
        (0, 1, ("0->1",)),
        (1, 1, ()),
        (0, 2, ("0->1", "1->2")),
        (1, 2, ("1->2",)),
        (2, 2, ()),
    )

    iso = walking_isomorphism()
    assert fp_categories.is_isomorphism(iso, iso.generator("f")) is True
    assert (iso.generator("g") * iso.generator("f")).word() == ()
    assert (iso.generator("f") * iso.generator("g")).word() == ()
    assert iso.inverse_morphism(iso.generator("f")) is iso.generator("g")
    iso_arrows = iso.finite_morphisms()
    assert iso_arrows is not Unknown and len(iso_arrows) == 4

    labelled = FinitePresentedCategory(
        "labelled",
        (("source", 7), frozenset({"target"})),
        (("public generator", ("source", 7), frozenset({"target"})),),
        (),
    )
    labelled_arrows = labelled.finite_morphisms()
    assert labelled_arrows is not Unknown and len(labelled_arrows) == 3
    assert labelled.generator("public generator").word() == ("public generator",)

    idempotent = FinitePresentedCategory(
        "idempotent",
        ("v",),
        (("x", "v", "v"),),
        ((("x", "x"), ("x",)),),
    )
    assert fp_categories.is_isomorphism(idempotent, idempotent.generator("x")) is False
    assert (idempotent.generator("x") * idempotent.generator("x")) is idempotent.generator("x")
    finite = idempotent.finite_morphisms()
    assert finite is not Unknown and len(finite) == 2
    assert ask(finite[0] == finite[0]) is True

    commuting = FinitePresentedCategory(
        "commuting loops",
        (0,),
        (("a", 0, 0), ("b", 0, 0)),
        ((("a", "b"), ("b", "a")),),
    )
    assert fp_categories.is_isomorphism(commuting, commuting.generator("a")) is None

    parallel = FinitePresentedCategory(
        "parallel relation",
        ("source", "target"),
        (("f", "source", "target"), ("g", "source", "target")),
        ((("f",), ("g",)),),
    )
    assert parallel("source") is not parallel("target")
    assert ask(parallel.generator("f") == parallel.generator("g")) is True
    parallel_arrows = parallel.finite_morphisms()
    assert parallel_arrows is not Unknown and len(parallel_arrows) == 3

    free_loop = FinitePresentedCategory("free loop", (0,), (("x", 0, 0),), ())
    assert free_loop.finite_morphisms() is Unknown
    loop = free_loop.generator("x")
    power = loop
    for exponent in range(2, 65):
        power = loop * power
        assert power.word() == ("x",) * exponent
        assert power.domain() is free_loop(0)
        assert power.codomain() is free_loop(0)
    assert free_loop.finite_morphisms() is Unknown


def test_native_parallel_length_two_relation() -> None:
    square = FinitePresentedCategory(
        "commuting square",
        ("source", "upper", "lower", "target"),
        (
            ("up", "source", "upper"),
            ("across upper", "upper", "target"),
            ("down", "source", "lower"),
            ("across lower", "lower", "target"),
        ),
        ((("up", "across upper"), ("down", "across lower")),),
    )
    upper = square.generator("across upper") * square.generator("up")
    lower = square.generator("across lower") * square.generator("down")

    assert upper.domain() is square("source")
    assert upper.codomain() is square("target")
    assert lower.domain() is square("source")
    assert lower.codomain() is square("target")
    assert ask(upper == lower) is True
    assert upper.word() == lower.word()

    arrows = square.finite_morphisms()
    assert arrows is not Unknown and len(arrows) == 9


test_native_finite_presented_category_paths()
test_native_parallel_length_two_relation()
