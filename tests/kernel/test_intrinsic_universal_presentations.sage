"""Intrinsic colimits retain their ambient category, cocones, and universal maps."""

from pytest import raises

from sage_categories.all import Cat, Fun, Mor, Sets, ask
from sage_categories.algebra.abelian import AbelianGroups
from sage_categories.cat.canonical import FinitePresentedCategory
from sage_categories.cat.cones import cocone, cocones, cocone_apex, cone, cones, limit_cones
from sage_categories.cat.diagrams import from_sequence
from sage_categories.cat.properties import PredicateSubcategory
from sage_categories.cat.predicates import Proposition


class IntrinsicUpperBounds(PredicateSubcategory):
    """The full subcategory on a, b, c, e, with c the join of a and b."""

    def _predicate(self, candidate: FinitePresentedCategory.ObjectType,
                   assumptions: Proposition) -> bool:
        return self.ambient().label(candidate) in ("a", "b", "c", "e")


def test_abelian_colimit_family_has_its_intrinsic_owner() -> None:
    abelian = AbelianGroups()
    shape = Cat().WalkingParallelPair()
    family = abelian.Colimits(shape)
    assert family.ambient() is abelian
    assert family.diagrams().codomain() is abelian


def test_intrinsic_coproduct_retains_distinct_presentations() -> None:
    # In this thin category, c and d are incomparable upper bounds of a and b.
    ambient = FinitePresentedCategory(
        "Two incomparable upper bounds", ("a", "b", "c", "d", "e"),
        (("ac", "a", "c"), ("bc", "b", "c"),
         ("ad", "a", "d"), ("bd", "b", "d"), ("ce", "c", "e")), (),
    )
    intrinsic = IntrinsicUpperBounds(ambient, "IntrinsicUpperBounds", ())
    a, b, c, e = (intrinsic(label) for label in ("a", "b", "c", "e"))
    assert ask(intrinsic.membership_proposition(ambient("d"))) is False
    ac, bc = (Mor(intrinsic)(source, c)((name,))
              for source, name in ((a, "ac"), (b, "bc")))
    diagram = from_sequence(intrinsic, (a, b))
    family = intrinsic.Colimits(diagram.domain())
    assert family.ambient() is intrinsic
    assert intrinsic.op().Limits(diagram.domain().op()).ambient() is intrinsic.op()
    with raises(AssertionError):
        family.colimit_functor()
    legs = (ac, bc)
    chosen = cocone(diagram, c, lambda vertex: legs[diagram.domain().label(vertex)])

    def descend(candidate):
        (unique,) = intrinsic.hom_morphisms(c, cocone_apex(candidate))
        return unique

    family.with_universal_data(
        diagram, c, chosen, descend,
    )
    presentation = family.universal_data(diagram)
    assert presentation.diagram() is diagram
    assert presentation.apex() is c
    assert presentation.leg(0) is ac
    assert presentation.leg(1) is bc
    ce = Mor(intrinsic)(c, e)(("ce",))
    competitor = cocones(diagram)(cocone(diagram, e, lambda vertex: ce * legs[diagram.domain().label(vertex)]))
    mediator = presentation.lift(competitor)
    assert mediator.domain() is c and mediator.codomain() is e
    assert ask(mediator == ce) is True
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


def test_limiting_presentations_of_one_apex_retain_their_legs() -> None:
    sets = Sets()
    factor = sets((0, 1))
    diagram = from_sequence(sets, (factor, factor))
    family = sets.Limits(diagram.domain())
    apex = family(diagram)
    first = family.universal_data(diagram)
    shape = diagram.domain()
    swapped = cone(diagram, apex, lambda vertex: first.leg(1 - shape.label(vertex)))

    def transpose(candidate):
        return first.lift(cones(diagram)(cone(
            diagram, candidate.apex(), lambda vertex: candidate.leg(1 - shape.label(vertex)),
        )))

    second = limit_cones(diagram).with_universal_data(swapped, transpose)
    total = Fun(shape, sets).TotalCones()
    first_total, second_total = total(first), total(second)
    assert first_total.presentation() is first
    assert second_total.presentation() is second
    assert total.apex_functor().on_object(first_total) is total.apex_functor().on_object(second_total)
    point = apex.point((0, 1))
    assert ask(first.leg(0)(point) == factor.point(0)) is True
    assert ask(second.leg(0)(point) == factor.point(1)) is True
    comparison = second.lift(first)
    assert ask(first.leg(0)(comparison(point)) == factor.point(1)) is True
    assert ask(first.leg(1)(comparison(point)) == factor.point(0)) is True


test_abelian_colimit_family_has_its_intrinsic_owner()
test_intrinsic_coproduct_retains_distinct_presentations()
test_limiting_presentations_of_one_apex_retain_their_legs()
