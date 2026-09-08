"""Contravariant indexed categories and their Grothendieck construction.

The composition and transport formulas follow Mathlib's
``Pseudofunctor.CoGrothendieck`` (the contravariant convention):
https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Bicategory/Grothendieck.html
The chosen unit and composition isomorphisms are part of the pseudofunctor.
Their coherence laws, and the pseudonaturality laws for morphisms, are the
mathematical contracts of these data constructors.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from sympy import ask as sympy_ask

from sage_categories.cat.adjunctions import Equivalences, EquivalencesCategory
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.functors import Cat, Fun, Functor, NaturalTransformation
from sage_categories.cat.morphisms import Mor, MorphismCategory
from sage_categories.cat.opposites import opposite_morphism
from sage_categories.cat.predicates import Proposition, ask, register_handler
from sage_categories.kernel.sage_runtime import MonoDict, TripleDict, cached_method

__all__ = ["Grothendieck", "GrothendieckCategory", "IndexedCategories", "IndexedCategoriesCategory"]

type FiberRule = Callable[[CategoryOfCategories.ElementType], Category]
type ReindexingRule = Callable[[MorphismCategory.ObjectType], Functor]
type UnitRule = Callable[[CategoryOfCategories.ElementType], NaturalTransformation]
type CompositionRule = Callable[[MorphismCategory.ObjectType, MorphismCategory.ObjectType], NaturalTransformation]
type ComponentRule = Callable[[CategoryOfCategories.ElementType], Functor]
type ComparisonRule = Callable[[MorphismCategory.ObjectType], NaturalTransformation]


@dataclass(frozen=True, eq=False, slots=True)
class _IndexedData:
    fibers: FiberRule
    reindexing: ReindexingRule
    unit: UnitRule
    composition: CompositionRule


@dataclass(frozen=True, eq=False, slots=True)
class _IndexedTransformationData:
    components: ComponentRule
    comparisons: ComparisonRule


class IndexedCategoriesCategory(Category[[ComponentRule, ComparisonRule], []]):
    """Pseudofunctors ``C.op() -> Cat`` and pseudonatural transformations."""

    class ObjectType:
        def __init__(self, data: _IndexedData) -> None:
            self._indexed_data = data

        def domain(self) -> Category:
            return self.category().narrowing_base().base().op()

        def codomain(self) -> Category:
            return Cat()

        @cached_method(key=lambda self, value: id(value))
        def on_object(self, value: CategoryOfCategories.ElementType) -> Category:
            assert value in self.domain()
            result = self._indexed_data.fibers(value)
            assert result in Cat()
            return result

        @cached_method(key=lambda self, morphism: id(morphism))
        def reindex(self, morphism: MorphismCategory.ObjectType) -> Functor:
            """The contravariant action on an arrow of the base category."""
            assert morphism in Mor(self.domain().op())
            result = self._indexed_data.reindexing(morphism)
            assert result in Fun(self.on_object(morphism.codomain()), self.on_object(morphism.domain()))
            return result

        def on_morphism(self, morphism: MorphismCategory.ObjectType) -> Functor:
            assert morphism in Mor(self.domain())
            return self.reindex(opposite_morphism(morphism))

        @cached_method(key=lambda self, value: id(value))
        def unit(self, value: CategoryOfCategories.ElementType) -> NaturalTransformation:
            fiber = self.on_object(value)
            base = self.domain().op()
            target = self.reindex(Mor(base)(value, value).one())
            result = self._indexed_data.unit(value)
            assert result in Mor(Fun(fiber, fiber))(Fun(fiber, fiber).one(), target)
            assert result in Mor(Fun(fiber, fiber)).Isomorphisms()
            return result

        @cached_method(key=lambda self, second, first: (id(second), id(first)))
        def compositor(self, second: MorphismCategory.ObjectType, first: MorphismCategory.ObjectType) -> NaturalTransformation:
            """``P(first) P(second) => P(second first)``."""
            assert first.codomain() is second.domain()
            source = self.reindex(first) * self.reindex(second)
            target = self.reindex(second * first)
            result = self._indexed_data.composition(second, first)
            functors = Fun(source.domain(), source.codomain())
            assert result in Mor(functors)(source, target)
            assert result in Mor(functors).Isomorphisms()
            return result

        def total_category(self) -> GrothendieckCategory:
            return Grothendieck(self)

    class ElementType:
        pass

    class MorphismType:
        def __init__(self, data: _IndexedTransformationData) -> None:
            self._indexed_transformation = data

        @cached_method(key=lambda self, value: id(value))
        def component(self, value: CategoryOfCategories.ElementType) -> Functor:
            result = self._indexed_transformation.components(value)
            assert result in Fun(self.domain().on_object(value), self.codomain().on_object(value))
            return result

        @cached_method(key=lambda self, morphism: id(morphism))
        def comparison(self, morphism: MorphismCategory.ObjectType) -> NaturalTransformation:
            """``eta_c P(f) => Q(f) eta_d`` for ``f: c -> d``."""
            source = self.component(morphism.domain()) * self.domain().reindex(morphism)
            target = self.codomain().reindex(morphism) * self.component(morphism.codomain())
            result = self._indexed_transformation.comparisons(morphism)
            functors = Fun(source.domain(), source.codomain())
            assert result in Mor(functors)(source, target)
            assert result in Mor(functors).Isomorphisms()
            return result

        def induced_functor(self) -> Functor:
            return self.base_category().grothendieck_functor().on_morphism(self)

    def __init__(self, base: Category) -> None:
        self._base = base
        self._grothendieck_functor: Functor | None = None

    def base(self) -> Category:
        return self._base

    def __call__(self, fibers: FiberRule, reindexing: ReindexingRule, unit: UnitRule, composition: CompositionRule) -> IndexedCategoriesCategory.ObjectType:
        return self.ObjectType(_IndexedData(fibers, reindexing, unit, composition))

    @cached_method(key=lambda self, functor: id(functor))
    def strict(self, functor: Functor) -> IndexedCategoriesCategory.ObjectType:
        """Regard a strict contravariant functor as an indexed category."""
        assert functor in Fun(self._base.op(), Cat())

        def reindexing(morphism: MorphismCategory.ObjectType) -> Functor:
            return functor.on_morphism(opposite_morphism(morphism))

        def unit(value: CategoryOfCategories.ElementType) -> NaturalTransformation:
            fiber = functor.on_object(value)
            identity = Fun(fiber, fiber).one()
            target = reindexing(Mor(self._base)(value, value).one())
            return Mor(Fun(fiber, fiber))(identity, target).Isomorphisms()(
                lambda member: Mor(fiber)(member, member).one()
            )

        def composition(second: MorphismCategory.ObjectType, first: MorphismCategory.ObjectType) -> NaturalTransformation:
            source = reindexing(first) * reindexing(second)
            target = reindexing(second * first)
            return Mor(Fun(source.domain(), source.codomain()))(source, target).Isomorphisms()(
                lambda member: Mor(source.codomain())(source.on_object(member), target.on_object(member)).one()
            )

        return self(functor.on_object, reindexing, unit, composition)

    def construct_morphism(self, source: IndexedCategoriesCategory.ObjectType, target: IndexedCategoriesCategory.ObjectType, components: ComponentRule, comparisons: ComparisonRule) -> IndexedCategoriesCategory.MorphismType:
        assert source in self and target in self
        return self.MorphismType(domain=source, codomain=target, data=_IndexedTransformationData(components, comparisons))

    def construct_identity(self, value: IndexedCategoriesCategory.ObjectType) -> IndexedCategoriesCategory.MorphismType:
        def comparison(morphism: MorphismCategory.ObjectType) -> NaturalTransformation:
            functor = value.reindex(morphism)
            return Mor(Fun(functor.domain(), functor.codomain()))(functor, functor).one()

        return self.construct_morphism(value, value, lambda base: Fun(value.on_object(base), value.on_object(base)).one(), comparison)

    def composite(self, second: IndexedCategoriesCategory.MorphismType, first: IndexedCategoriesCategory.MorphismType) -> IndexedCategoriesCategory.MorphismType:
        assert first.codomain() is second.domain()
        return self.construct_morphism(
            first.domain(), second.codomain(),
            lambda value: second.component(value) * first.component(value),
            lambda morphism: second.comparison(morphism).whisker_right(first.component(morphism.codomain()))
            * first.comparison(morphism).whisker_left(second.component(morphism.domain())),
        )

    def grothendieck_functor(self) -> Functor:
        if self._grothendieck_functor is None:
            self._grothendieck_functor = Fun(self, Cat())(GrothendieckCategory, _induced_functor)
        return self._grothendieck_functor


@dataclass(frozen=True, eq=False, slots=True)
class _TotalObject:
    base: CategoryOfCategories.ElementType
    fiber: CategoryOfCategories.ElementType


@dataclass(frozen=True, eq=False, slots=True)
class _TotalMorphism:
    base: MorphismCategory.ObjectType
    fiber: MorphismCategory.ObjectType


class GrothendieckCategory(Category[[MorphismCategory.ObjectType, MorphismCategory.ObjectType], []]):
    """Pairs ``(c,x)`` and arrows ``(f,phi: x -> P(f)y)``."""

    class ObjectType:
        def __init__(self, data: _TotalObject) -> None:
            self._total_object = data

        def base_object(self) -> CategoryOfCategories.ElementType:
            return self._total_object.base

        def fiber_object(self) -> CategoryOfCategories.ElementType:
            return self._total_object.fiber

    class ElementType:
        pass

    class MorphismType:
        def __init__(self, data: _TotalMorphism) -> None:
            self._total_morphism = data

        def base_morphism(self) -> MorphismCategory.ObjectType:
            return self._total_morphism.base

        def fiber_morphism(self) -> MorphismCategory.ObjectType:
            return self._total_morphism.fiber

    def __init__(self, indexed: IndexedCategoriesCategory.ObjectType) -> None:
        self._indexed = indexed
        self._objects: TripleDict = TripleDict(weak_values=False)
        self._projection: Functor | None = None
        super().__init__()
        register_handler(self._equality, self._equal_objects)
        register_handler(self._equality, self._equal_morphisms)

    def _equal_objects(self, first: GrothendieckCategory.ObjectType, second: GrothendieckCategory.ObjectType, assumptions: Proposition) -> bool | None:
        return sympy_ask((first.base_object() == second.base_object()) & (first.fiber_object() == second.fiber_object()), assumptions)

    def _equal_morphisms(self, first: GrothendieckCategory.MorphismType, second: GrothendieckCategory.MorphismType, assumptions: Proposition) -> bool | None:
        return sympy_ask((first.base_morphism() == second.base_morphism()) & (first.fiber_morphism() == second.fiber_morphism()), assumptions)

    def indexed_category(self) -> IndexedCategoriesCategory.ObjectType:
        return self._indexed

    def __call__(self, base: CategoryOfCategories.ElementType, fiber: CategoryOfCategories.ElementType) -> GrothendieckCategory.ObjectType:
        assert fiber in self._indexed.on_object(base)
        key = (base, fiber, self)
        if key not in self._objects:
            self._objects[key] = self.ObjectType(_TotalObject(base, fiber))
        return self._objects[key]

    def construct_morphism(self, source: GrothendieckCategory.ObjectType, target: GrothendieckCategory.ObjectType, base: MorphismCategory.ObjectType, fiber: MorphismCategory.ObjectType) -> GrothendieckCategory.MorphismType:
        assert source in self and target in self
        assert base in Mor(self._indexed.domain().op())(source.base_object(), target.base_object())
        reindex = self._indexed.reindex(base)
        assert fiber in Mor(reindex.codomain())(source.fiber_object(), reindex.on_object(target.fiber_object()))
        return self.MorphismType(domain=source, codomain=target, data=_TotalMorphism(base, fiber))

    def construct_identity(self, value: GrothendieckCategory.ObjectType) -> GrothendieckCategory.MorphismType:
        base = Mor(self._indexed.domain().op())(value.base_object(), value.base_object()).one()
        return self.construct_morphism(value, value, base, self._indexed.unit(value.base_object()).component(value.fiber_object()))

    def composite(self, second: GrothendieckCategory.MorphismType, first: GrothendieckCategory.MorphismType) -> GrothendieckCategory.MorphismType:
        assert first.codomain() is second.domain()
        upper, lower = second.base_morphism(), first.base_morphism()
        fiber = self._indexed.compositor(upper, lower).component(second.codomain().fiber_object())
        fiber = fiber * self._indexed.reindex(lower).on_morphism(second.fiber_morphism()) * first.fiber_morphism()
        return self.construct_morphism(first.domain(), second.codomain(), upper * lower, fiber)

    def projection(self) -> Functor:
        if self._projection is None:
            self._projection = Fun(self, self._indexed.domain().op()).Fibrations()(
                lambda value: value.base_object(), lambda morphism: morphism.base_morphism(),
            )
            self._projection.retain_cartesian_lifts(self._cartesian_lift)
        return self._projection

    def structure_functors(self) -> tuple[Functor, ...]:
        return (self.projection(),)

    def _cartesian_lift(self, morphism: MorphismCategory.ObjectType, target: GrothendieckCategory.ObjectType) -> GrothendieckCategory.MorphismType:
        assert morphism.codomain() is target.base_object()
        reindex = self._indexed.reindex(morphism)
        image = reindex.on_object(target.fiber_object())
        source = self(morphism.domain(), image)
        return self.construct_morphism(source, target, morphism, Mor(reindex.codomain())(image, image).one())

    def factor_cartesian(self, lift: GrothendieckCategory.MorphismType, arrow: GrothendieckCategory.MorphismType, base: MorphismCategory.ObjectType) -> GrothendieckCategory.MorphismType:
        """Factor an arrow through the selected cartesian lift over a specified base arrow."""
        assert arrow.codomain() is lift.codomain()
        assert ask(lift.base_morphism() * base == arrow.base_morphism()) is True
        comparison = self._indexed.compositor(lift.base_morphism(), base).component(lift.codomain().fiber_object())
        return self.construct_morphism(arrow.domain(), lift.domain(), base, comparison.inverse() * arrow.fiber_morphism())

    @cached_method(key=lambda self, base: id(base))
    def fiber_equivalence(self, base: CategoryOfCategories.ElementType) -> EquivalencesCategory.ObjectType:
        """The selected equivalence ``P(c) -> projection.Fiber(c)``."""
        source = self._indexed.on_object(base)
        target = self.projection().Fiber(base)
        star = Cat().Terminal()(0)
        star_identity = Mor(Cat().Terminal())(star, star).one()
        base_identity = Mor(self._indexed.domain().op())(base, base).one()
        unit = self._indexed.unit(base)

        def into(value: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
            return target((self(base, value), star, base))

        def into_arrow(morphism: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
            total = self.construct_morphism(self(base, morphism.domain()), self(base, morphism.codomain()), base_identity, unit.component(morphism.codomain()) * morphism)
            return target.construct_morphism(into(morphism.domain()), into(morphism.codomain()), (total, star_identity, base_identity))

        forward = Fun(source, target)(into, into_arrow)
        inclusion = target.inclusion()

        def out_arrow(morphism: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
            total = inclusion.on_morphism(morphism)
            return unit.component(total.codomain().fiber_object()).inverse() * total.fiber_morphism()

        inverse = Fun(target, source)(lambda value: inclusion.on_object(value).fiber_object(), out_arrow)
        source_functors, target_functors = Fun(source, source), Fun(target, target)
        source_roundtrip, target_roundtrip = inverse * forward, forward * inverse
        source_identity, target_identity = source_functors.one(), target_functors.one()
        eta = Mor(source_functors)(source_identity, source_roundtrip)(lambda value: Mor(source)(value, value).one())
        eta_inverse = Mor(source_functors)(source_roundtrip, source_identity)(lambda value: Mor(source)(value, value).one())
        source_functors.retain_inverses(eta, eta_inverse)

        def comparison(value: CategoryOfCategories.ElementType, reverse: bool) -> MorphismCategory.ObjectType:
            canonical = target_roundtrip.on_object(value)
            domain, codomain = (value, canonical) if reverse else (canonical, value)
            total = inclusion.on_object(value)
            return target.construct_morphism(domain, codomain, (Mor(self)(total, total).one(), star_identity, base_identity))

        epsilon = Mor(target_functors)(target_roundtrip, target_identity)(lambda value: comparison(value, False))
        epsilon_inverse = Mor(target_functors)(target_identity, target_roundtrip)(lambda value: comparison(value, True))
        target_functors.retain_inverses(epsilon, epsilon_inverse)
        return Equivalences(source, target)(forward, inverse, eta, epsilon)


def _induced_functor(transformation: IndexedCategoriesCategory.MorphismType) -> Functor:
    source, target = Grothendieck(transformation.domain()), Grothendieck(transformation.codomain())

    def on_object(value: GrothendieckCategory.ObjectType) -> GrothendieckCategory.ObjectType:
        return target(value.base_object(), transformation.component(value.base_object()).on_object(value.fiber_object()))

    def on_morphism(morphism: GrothendieckCategory.MorphismType) -> GrothendieckCategory.MorphismType:
        base = morphism.base_morphism()
        fiber = transformation.component(base.domain()).on_morphism(morphism.fiber_morphism())
        fiber = transformation.comparison(base).component(morphism.codomain().fiber_object()) * fiber
        return target.construct_morphism(on_object(morphism.domain()), on_object(morphism.codomain()), base, fiber)

    return Fun(source, target)(on_object, on_morphism)


_indexed_categories: MonoDict = MonoDict()


def IndexedCategories(base: Category) -> IndexedCategoriesCategory:
    if base not in _indexed_categories:
        _indexed_categories[base] = IndexedCategoriesCategory(base)
    return _indexed_categories[base]


def Grothendieck(indexed: IndexedCategoriesCategory.ObjectType) -> GrothendieckCategory:
    return indexed.category().narrowing_base().grothendieck_functor().on_object(indexed)
