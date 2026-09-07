"""Intrinsic colimits retain their ambient category, cocones, and universal maps."""

from sage_categories.all import Cat, Fun, Mor, ask
from sage_categories.algebra.abelian import AbelianGroups
from sage_categories.cat.canonical import FinitePresentedCategory
from sage_categories.cat.cones import cocone, cocones, cocone_apex
from sage_categories.cat.diagrams import from_sequence
from sage_categories.cat.properties import PropertySubcategory


def test_abelian_colimit_family_has_its_intrinsic_owner() -> None:
    abelian = AbelianGroups()
    shape = Cat().WalkingParallelPair()
    family = abelian.Colimits(shape)
    assert family.ambient() is abelian
    assert family.diagrams().codomain() is abelian


def test_intrinsic_coproduct_retains_distinct_presentations() -> None:
    # In this thin category, c and d are incomparable upper bounds of a and b.
    ambient = FinitePresentedCategory(
        "Two incomparable upper bounds", ("a", "b", "c", "d"),
        (("ac", "a", "c"), ("bc", "b", "c"),
         ("ad", "a", "d"), ("bd", "b", "d")), (),
    )
    intrinsic = PropertySubcategory(ambient, "OnABC", ())
    a, b, c = (intrinsic(label) for label in ("a", "b", "c"))
    ac, bc = (Mor(intrinsic)(source, c)((name,))
              for source, name in ((a, "ac"), (b, "bc")))
    diagram = from_sequence(intrinsic, (a, b))
    family = intrinsic.Colimits(diagram.domain())
    assert family.ambient() is intrinsic
    legs = (ac, bc)
    chosen = cocone(diagram, c, lambda vertex: legs[diagram.domain().label(vertex)])
    family.with_universal_data(
        diagram, c, chosen,
        lambda candidate: Mor(intrinsic)(c, cocone_apex(candidate)).one(),
    )
    presentation = family.universal_data(diagram)
    assert presentation.diagram() is diagram
    assert presentation.apex() is c
    assert presentation.leg(0) is ac
    assert presentation.leg(1) is bc
    competitor = cocones(diagram)(cocone(diagram, c, lambda vertex: legs[diagram.domain().label(vertex)]))
    mediator = presentation.lift(competitor)
    assert mediator.domain() is c and mediator.codomain() is c
    for index in (0, 1):
        assert ask(mediator * presentation.leg(index) == competitor.leg(index)) is True

    second = from_sequence(intrinsic, (a, c))
    second_legs = (ac, Mor(intrinsic)(c, c).one())
    family.with_universal_data(
        second, c, cocone(second, c, lambda vertex: second_legs[second.domain().label(vertex)]),
        lambda candidate: candidate.component(second.domain()(1)),
    )
    other = family.universal_data(second)
    assert other.apex() is presentation.apex()
    assert other.leg(1).domain() is c
    assert presentation.leg(1).domain() is b
    assert family.universal_data(diagram) is presentation
    assert family.universal_data(second) is other


test_abelian_colimit_family_has_its_intrinsic_owner()
test_intrinsic_coproduct_retains_distinct_presentations()
