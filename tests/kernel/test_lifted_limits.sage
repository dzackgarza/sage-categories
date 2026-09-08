"""Limits of finite structured sets through selected faithful functors."""

from __future__ import annotations

from collections.abc import Callable, Hashable
from itertools import product

from sage_categories.all import Cat, Category, Fun, Mor
from sage_categories.cat.cones import cone, cone_apex, cones, LimitConesCategory
from sage_categories.cat.diagrams import from_sequence
from sage_categories.cat.functors import Functor
from sage_categories.cat.shapes import Discrete


class FiniteSets(Category):
    """Finite sets and total maps, with the compatible-family limit construction."""

    class ObjectType:
        def __init__(self, values: frozenset[Hashable]) -> None:
            self._values = values

        def values(self) -> frozenset[Hashable]:
            return self._values

    class ElementType:
        pass

    class MorphismType:
        def __init__(self, pairs: tuple[tuple[Hashable, Hashable], ...]) -> None:
            self._function = dict(pairs)

        def apply(self, value: Hashable) -> Hashable:
            return self._function[value]

    def __call__(self, values: frozenset[Hashable]) -> FiniteSets.ObjectType:
        return self.ObjectType(values)

    def construct_morphism(self, source: FiniteSets.ObjectType, target: FiniteSets.ObjectType,
                           action: Callable[[Hashable], Hashable]) -> FiniteSets.MorphismType:
        pairs = tuple((value, action(value)) for value in source.values())
        assert all(image in target.values() for _, image in pairs)
        return self.MorphismType(domain=source, codomain=target, data=pairs)

    def construct_identity(self, source: FiniteSets.ObjectType) -> FiniteSets.MorphismType:
        return self.construct_morphism(source, source, lambda value: value)

    def composite(self, second: FiniteSets.MorphismType,
                  first: FiniteSets.MorphismType) -> FiniteSets.MorphismType:
        return self.construct_morphism(first.domain(), second.codomain(),
                                       lambda value: second.apply(first.apply(value)))

    def limit_construction(self, shape: Category) -> Callable[[Functor], FiniteSets.ObjectType]:
        # The compatible-family construction of limits in Set (Mac Lane, V.2).
        def construct(diagram: Functor) -> FiniteSets.ObjectType:
            vertices = tuple(shape(label) for label in shape.labels())
            position = {id(vertex): index for index, vertex in enumerate(vertices)}
            arrows = shape.generating_morphisms()
            values = frozenset(
                family for family in product(*(diagram.on_object(vertex).values() for vertex in vertices))
                if all(diagram.on_morphism(arrow).apply(family[position[id(arrow.domain())]])
                       == family[position[id(arrow.codomain())]] for arrow in arrows)
            )
            apex = self(values)
            limiting = cone(diagram, apex, lambda vertex: Mor(self)(apex, diagram.on_object(vertex))(
                lambda family: family[position[id(vertex)]]))
            return self.Limits(shape).with_universal_data(
                diagram, apex, limiting,
                lambda candidate: Mor(self)(cone_apex(candidate), apex)(
                    lambda value: tuple(candidate.component(vertex).apply(value) for vertex in vertices)),
            )
        return construct


class FinitePosets(Category):
    """Finite partial orders and monotone maps."""

    class ObjectType:
        def __init__(self, data: tuple[FiniteSets.ObjectType, frozenset[tuple[Hashable, Hashable]]]) -> None:
            self._poset_set, self._order = data

        def leq(self, first: Hashable, second: Hashable) -> bool:
            return (first, second) in self._order

    class ElementType:
        pass

    class MorphismType:
        def __init__(self, underlying: FiniteSets.MorphismType) -> None:
            self._monotone_map = underlying

    def __init__(self, sets: FiniteSets) -> None:
        self._sets = sets

    def __call__(self, carrier: FiniteSets.ObjectType,
                 relation: Callable[[Hashable, Hashable], bool]) -> FinitePosets.ObjectType:
        order = frozenset((x, y) for x in carrier.values() for y in carrier.values() if relation(x, y))
        return self.ObjectType((carrier, order))

    def construct_morphism(self, source: FinitePosets.ObjectType, target: FinitePosets.ObjectType,
                           underlying: FiniteSets.MorphismType) -> FinitePosets.MorphismType:
        assert all(target.leq(underlying.apply(x), underlying.apply(y))
                   for x in source.values() for y in source.values() if source.leq(x, y))
        return self.MorphismType(domain=source, codomain=target, data=underlying)

    def construct_identity(self, source: FinitePosets.ObjectType) -> FinitePosets.MorphismType:
        return self.construct_morphism(source, source, Mor(self._sets)(source._poset_set, source._poset_set).one())

    def composite(self, second: FinitePosets.MorphismType,
                  first: FinitePosets.MorphismType) -> FinitePosets.MorphismType:
        return self.construct_morphism(first.domain(), second.codomain(), second._monotone_map * first._monotone_map)

    def lift_order(self, diagram: Functor, base: LimitConesCategory.ObjectType) -> FinitePosets.ObjectType:
        vertices = tuple(diagram.domain()(label) for label in diagram.domain().labels())
        return self(base.apex(), lambda x, y: all(
            diagram.on_object(vertex).leq(base.leg(vertex).apply(x), base.leg(vertex).apply(y))
            for vertex in vertices))

    def structure_functors(self) -> tuple[Functor, ...]:
        forget = Fun(self, self._sets).Faithful().Isofibrations()(
            lambda value: value._poset_set, lambda arrow: arrow._monotone_map)
        forget.with_limit_lifting(Discrete, self.lift_order, self.construct_morphism)
        forget.with_limit_lifting(Cat().WalkingParallelPair(), self.lift_order, self.construct_morphism)
        return (forget,)


class PointedFiniteSets(Category):
    """Finite sets with a chosen point and maps preserving it."""

    class ObjectType:
        def __init__(self, data: tuple[FiniteSets.ObjectType, Hashable]) -> None:
            self._pointed_set, self._basepoint = data

        def basepoint(self) -> Hashable:
            return self._basepoint

    class ElementType:
        pass

    class MorphismType:
        def __init__(self, underlying: FiniteSets.MorphismType) -> None:
            self._pointed_map = underlying

    def __init__(self, sets: FiniteSets) -> None:
        self._sets = sets

    def __call__(self, carrier: FiniteSets.ObjectType, basepoint: Hashable) -> PointedFiniteSets.ObjectType:
        assert basepoint in carrier.values()
        return self.ObjectType((carrier, basepoint))

    def construct_morphism(self, source: PointedFiniteSets.ObjectType, target: PointedFiniteSets.ObjectType,
                           underlying: FiniteSets.MorphismType) -> PointedFiniteSets.MorphismType:
        assert underlying.apply(source.basepoint()) == target.basepoint()
        return self.MorphismType(domain=source, codomain=target, data=underlying)

    def construct_identity(self, source: PointedFiniteSets.ObjectType) -> PointedFiniteSets.MorphismType:
        return self.construct_morphism(source, source, Mor(self._sets)(source._pointed_set, source._pointed_set).one())

    def composite(self, second: PointedFiniteSets.MorphismType,
                  first: PointedFiniteSets.MorphismType) -> PointedFiniteSets.MorphismType:
        return self.construct_morphism(first.domain(), second.codomain(), second._pointed_map * first._pointed_map)

    def lift_point(self, diagram: Functor, base: LimitConesCategory.ObjectType) -> PointedFiniteSets.ObjectType:
        singleton = self._sets(frozenset((0,)))
        points = cone(base.diagram(), singleton, lambda vertex: Mor(self._sets)(
            singleton, diagram.on_object(vertex)._pointed_set)(lambda value: diagram.on_object(vertex).basepoint()))
        point = base.lift(cones(base.diagram())(points)).apply(0)
        return self(base.apex(), point)

    def structure_functors(self) -> tuple[Functor, ...]:
        forget = Fun(self, self._sets).Faithful().Isofibrations().CreatesLimits(Discrete)(
            lambda value: value._pointed_set, lambda arrow: arrow._pointed_map)
        return (forget.with_limit_lifting(Discrete, self.lift_point, self.construct_morphism),)


def test_poset_product_lifts_order_projections_and_mediator() -> None:
    sets = FiniteSets()
    posets = FinitePosets(sets)
    two, three = sets(frozenset((0, 1))), sets(frozenset((0, 1, 2)))
    p, q = posets(two, lambda x, y: x <= y), posets(three, lambda x, y: x <= y)
    result = posets.Products()(p, q)
    assert result.values() == frozenset(product((0, 1), (0, 1, 2)))
    assert result.leq((0, 1), (1, 2))
    assert not result.leq((1, 0), (0, 2))
    assert not result.leq((0, 2), (1, 1))
    assert result.product_projection(0).apply((1, 2)) == 1
    assert result.product_projection(1).apply((1, 2)) == 2
    assert posets.Products()(p, q) is result
    forget = posets.selected_functors()[0]
    image_diagram = forget * result.diagram()
    base = sets.Limits(image_diagram.domain()).universal_data(image_diagram)
    assert forget.on_object(result) is base.apex()
    assert forget.on_morphism(result.product_projection(0)) is base.leg(0)

    source = posets(three, lambda x, y: x <= y)
    first = Mor(posets)(source, p)(Mor(sets)(three, two)(lambda x: min(x, 1)))
    second = Mor(posets)(source, q)(Mor(sets)(three, three)(lambda x: x))
    candidate = cone(result.diagram(), source, lambda vertex: (first, second)[result.diagram().domain().label(vertex)])
    mediator = result.universal_morphism(candidate)
    assert tuple(mediator.apply(x) for x in (0, 1, 2)) == ((0, 0), (1, 1), (1, 2))
    for index, leg in enumerate((first, second)):
        composite = result.product_projection(index) * mediator
        assert all(composite.apply(x) == leg.apply(x) for x in source.values())

    discrete = posets(two, lambda x, y: x == y)
    other = posets.Products()(discrete, q)
    assert not other.leq((0, 0), (1, 1))
    assert other.leq((0, 0), (0, 1))

    triple = posets.Products()(p, q, p)
    assert triple.values() == frozenset(product((0, 1), (0, 1, 2), (0, 1)))
    assert triple.leq((0, 0, 0), (1, 2, 1))
    assert not triple.leq((0, 0, 1), (1, 2, 0))

    shape = result.diagram().domain()
    swapped_diagram = from_sequence(posets, (q, p))
    maps = (Mor(posets)(p, q)(Mor(sets)(two, three)(lambda x: x)),
            Mor(posets)(q, p)(Mor(sets)(three, two)(lambda x: min(x, 1))))
    transformation = Mor(Fun(shape, posets))(result.diagram(), swapped_diagram)(
        lambda vertex: maps[shape.label(vertex)])
    induced = posets.Limits(shape).limit_functor().on_morphism(transformation)
    assert induced.domain() is result
    assert induced.codomain() is posets.Products()(q, p)
    assert induced.apply((0, 2)) == (0, 1)
    assert induced.apply((1, 0)) == (1, 0)


def test_lifted_limit_respects_nonidentity_diagram_arrows() -> None:
    sets = FiniteSets()
    posets = FinitePosets(sets)
    three, two = sets(frozenset((0, 1, 2))), sets(frozenset((0, 1)))
    p, q = posets(three, lambda x, y: x <= y), posets(two, lambda x, y: x <= y)
    first = Mor(posets)(p, q)(Mor(sets)(three, two)(lambda x: int(x == 2)))
    second = Mor(posets)(p, q)(Mor(sets)(three, two)(lambda x: int(x >= 1)))
    shape = Cat().WalkingParallelPair()
    arrows = shape.generating_morphisms()
    source, target = arrows[0].domain(), arrows[0].codomain()
    diagram = Fun(shape, posets)(lambda vertex: p if vertex is source else q,
        lambda arrow: Mor(posets)(p if arrow.domain() is source else q,
                                 p if arrow.domain() is source else q).one() if not arrow.word()
        else first if arrow.word() == arrows[0].word() else second)
    result = posets.Limits(shape)(diagram)
    presentation = posets.Limits(shape).universal_data(diagram)
    projection = presentation.leg(source)
    assert frozenset(projection.apply(value) for value in result.values()) == frozenset((0, 2))
    low = next(value for value in result.values() if projection.apply(value) == 0)
    high = next(value for value in result.values() if projection.apply(value) == 2)
    assert result.leq(low, high)
    source_cone = posets(two, lambda x, y: x <= y)
    to_source = Mor(posets)(source_cone, p)(Mor(sets)(two, three)(lambda x: 2*x))
    to_target = first * to_source
    candidate = cones(diagram)(cone(diagram, source_cone,
        lambda vertex: to_source if vertex is source else to_target))
    mediator = presentation.lift(candidate)
    assert mediator.apply(0) == low
    assert mediator.apply(1) == high


def test_created_pointed_product_retains_the_point_and_maps() -> None:
    sets = FiniteSets()
    pointed = PointedFiniteSets(sets)
    two, three = sets(frozenset((0, 1))), sets(frozenset((0, 1, 2)))
    p, q = pointed(two, 1), pointed(three, 2)
    result = pointed.Products()(p, q)
    assert result.basepoint() == (1, 2)
    assert result.product_projection(0).apply(result.basepoint()) == p.basepoint()
    assert result.product_projection(1).apply(result.basepoint()) == q.basepoint()
    source = pointed(two, 1)
    first = Mor(pointed)(source, p)(Mor(sets)(two, two).one())
    second = Mor(pointed)(source, q)(Mor(sets)(two, three)(lambda x: 2*x))
    mediator = result.universal_morphism(cone(result.diagram(), source,
        lambda vertex: (first, second)[result.diagram().domain().label(vertex)]))
    assert mediator.apply(0) == (0, 0)
    assert mediator.apply(source.basepoint()) == result.basepoint()
    for index, leg in enumerate((first, second)):
        composite = result.product_projection(index) * mediator
        assert all(composite.apply(x) == leg.apply(x) for x in source.values())


test_poset_product_lifts_order_projections_and_mediator()
test_lifted_limit_respects_nonidentity_diagram_arrows()
test_created_pointed_product_retains_the_point_and_maps()
