"""Grothendieck composition, cartesian transport, fibers, and pseudonatural maps."""

from sage_categories.all import Cat, Fun, Mor, IndexedCategories, Grothendieck, ask
from sage_categories.cat.canonical import FinitePresentedCategory
from sage_categories.cat.opposites import opposite_morphism


def test_cartesian_transport_and_fiber_equivalence() -> None:
    base, fiber = Cat().Simplex(2), Cat().Simplex(2)
    identity = Fun(fiber, fiber).one()
    collapse = Fun(fiber, fiber).constant(fiber(0))
    functor = Fun(base.op(), Cat())(
        lambda vertex: fiber,
        lambda arrow: identity if arrow.domain() is arrow.codomain() else collapse,
    )
    indexed = IndexedCategories(base).strict(functor)
    total = Grothendieck(indexed)
    first, second = base.generator("0->1"), base.generator("1->2")
    target = total(base(2), fiber(2))
    lift = total.projection().cartesian_lift(second, target)
    assert lift.domain().fiber_object() is fiber(0)
    assert lift.codomain() is target
    assert total.projection().on_morphism(lift) is second
    source = total(base(0), fiber(0))
    arrow = total.construct_morphism(source, target, second * first, Mor(fiber)(fiber(0), fiber(0)).one())
    factor = total.factor_cartesian(lift, arrow, first)
    assert total.projection().on_morphism(factor) is first
    assert ask(lift * factor == arrow) is True

    equivalence = total.fiber_equivalence(base(1))
    fiber_arrow = fiber.generator("0->1")
    image = equivalence.forward().on_morphism(fiber_arrow)
    assert equivalence.inverse().on_object(equivalence.forward().on_object(fiber(1))) is fiber(1)
    assert ask(equivalence.inverse().on_morphism(image) == fiber_arrow) is True
    assert equivalence.forward().codomain() is total.projection().Fiber(base(1))

    def comparison(morphism):
        source = collapse * indexed.reindex(morphism)
        destination = indexed.reindex(morphism) * collapse
        return Mor(Fun(fiber, fiber))(source, destination).Isomorphisms()(
            lambda value: Mor(fiber)(fiber(0), fiber(0)).one()
        )

    transformation = Mor(IndexedCategories(base))(indexed, indexed)(lambda value: collapse, comparison)
    induced = transformation.induced_functor()
    assert induced.domain() is total and induced.codomain() is total
    assert induced.on_object(target).fiber_object() is fiber(0)
    assert induced.on_object(target).base_object() is base(2)
    assert induced.on_morphism(arrow).base_morphism() is second * first


def test_pseudofunctor_composition_uses_its_nonidentity_compositor() -> None:
    base = Cat().Simplex(2)
    fiber = FinitePresentedCategory("B(C2)", (0,), (("s", 0, 0),), ((("s", "s"), ()),))
    identity = Fun(fiber, fiber).one()
    functors = Fun(fiber, fiber)
    natural_identity = Mor(functors)(identity, identity).one()
    twist = Mor(functors)(identity, identity).Isomorphisms()(lambda value: fiber.generator("s"))

    def compositor(second, first):
        return twist if first.domain() is not first.codomain() and second.domain() is not second.codomain() else natural_identity

    indexed = IndexedCategories(base)(lambda value: fiber, lambda arrow: identity, lambda value: natural_identity, compositor)
    total = Grothendieck(indexed)
    source, middle, target = (total(base(i), fiber(0)) for i in range(3))
    fiber_identity = Mor(fiber)(fiber(0), fiber(0)).one()
    first = total.construct_morphism(source, middle, base.generator("0->1"), fiber_identity)
    second = total.construct_morphism(middle, target, base.generator("1->2"), fiber_identity)
    composite = second * first
    assert composite.fiber_morphism() is fiber.generator("s")
    assert ask(composite * Mor(total)(source, source).one() == composite) is True
    assert ask(Mor(total)(target, target).one() * composite == composite) is True


test_cartesian_transport_and_fiber_equivalence()
test_pseudofunctor_composition_uses_its_nonidentity_compositor()
