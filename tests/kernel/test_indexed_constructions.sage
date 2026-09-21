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
    unit, counit = equivalence.unit(), equivalence.counit()
    adjunction = equivalence.adjunction()
    assert adjunction.unit() is unit and adjunction.counit() is counit
    assert unit.domain() is Fun(fiber, fiber).one()
    assert unit.codomain() is equivalence.inverse() * equivalence.forward()
    fiber_category = equivalence.forward().codomain()
    assert counit.domain() is equivalence.forward() * equivalence.inverse()
    assert counit.codomain() is Fun(fiber_category, fiber_category).one()

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


def test_nonconstant_pseudofunctor_transports_nonstrict_comparisons() -> None:
    base = Cat().Simplex(2)
    fiber = FinitePresentedCategory(
        "B(C2) plus a point",
        (0, 1),
        (("s", 0, 0),),
        ((("s", "s"), ()),),
    )
    functors = Fun(fiber, fiber)
    identity = functors.one()
    collapse = functors.constant(fiber(0))
    twist = fiber.generator("s")

    def reindex(morphism):
        match morphism.domain() is morphism.codomain():
            case True:
                return identity
            case False:
                return collapse

    def identity_iso(source, target):
        return Mor(functors)(source, target).Isomorphisms()(
            lambda value: Mor(fiber)(source.on_object(value), target.on_object(value)).one()
        )

    def twist_iso(source, target):
        return Mor(functors)(source, target).Isomorphisms()(lambda value: twist)

    def unit(value):
        return identity_iso(identity, reindex(Mor(base)(value, value).one()))

    def compositor(second, first):
        source = reindex(first) * reindex(second)
        target = reindex(second * first)
        match first.domain() is not first.codomain() and second.domain() is not second.codomain():
            case True:
                return twist_iso(source, target)
            case False:
                return identity_iso(source, target)

    indexed = IndexedCategories(base)(lambda value: fiber, reindex, unit, compositor)
    total = Grothendieck(indexed)
    first, second = base.generator("0->1"), base.generator("1->2")
    target = total(base(2), fiber(1))
    second_lift = total.projection().cartesian_lift(second, target)
    first_lift = total.projection().cartesian_lift(first, second_lift.domain())
    composite = second_lift * first_lift
    assert composite.fiber_morphism() is twist
    factor = total.factor_cartesian(second_lift, composite, first)
    assert ask(factor == first_lift) is True

    def comparison(morphism):
        source = identity * indexed.reindex(morphism)
        target_functor = indexed.reindex(morphism) * identity
        match len(morphism.word()) == 1:
            case True:
                return twist_iso(source, target_functor)
            case False:
                return identity_iso(source, target_functor)

    transformation = Mor(IndexedCategories(base))(indexed, indexed)(
        lambda value: identity,
        comparison,
    )
    comparison_component = transformation.comparison(second).component(target.fiber_object())
    assert comparison_component is twist
    induced = transformation.induced_functor()
    object_image = induced.on_object(target)
    assert object_image.base_object() is target.base_object()
    assert object_image.fiber_object() is target.fiber_object()
    image = induced.on_morphism(second_lift)
    assert image.domain() is second_lift.domain()
    assert image.codomain() is second_lift.codomain()
    assert image.base_morphism() is second
    assert image.fiber_morphism() is twist


test_cartesian_transport_and_fiber_equivalence()
test_pseudofunctor_composition_uses_its_nonidentity_compositor()
test_nonconstant_pseudofunctor_transports_nonstrict_comparisons()
