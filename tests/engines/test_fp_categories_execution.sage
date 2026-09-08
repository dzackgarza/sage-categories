"""Finite presented category path computation is owned by GAP FpCategories."""

from sage_categories.cat.canonical import (
    FinitePresentedCategory,
    simplex,
    walking_isomorphism,
)
from sage_categories.cat.predicates import Unknown, ask


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
    assert (iso.generator("g") * iso.generator("f")).word() == ()
    assert (iso.generator("f") * iso.generator("g")).word() == ()
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
    assert (idempotent.generator("x") * idempotent.generator("x")) is idempotent.generator("x")
    finite = idempotent.finite_morphisms()
    assert finite is not Unknown and len(finite) == 2
    assert ask(finite[0] == finite[0]) is True

    free_loop = FinitePresentedCategory("free loop", (0,), (("x", 0, 0),), ())
    assert free_loop.finite_morphisms() is Unknown


test_native_finite_presented_category_paths()
