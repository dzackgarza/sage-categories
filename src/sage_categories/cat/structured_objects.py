"""Inserters and equifiers, and algebraic structures expressed through them.

Inserters are pullbacks of comma categories along the diagonal on objects
and morphisms. Equifiers impose component equations as full subcategories.
Reference: Bird, Kelly, Power and Street, Flexible limits for 2-categories.
"""

from __future__ import annotations

__all__ = [
    "InserterCategory",
    "Inserter",
    "EquifierCategory",
    "Equifier",
    "EndofunctorAlgebras",
    "MagmaCategory",
    "Magmas",
    "PointedMagmas",
    "Monoids",
    "MonoidCategory",
    "AdditiveMagmas",
    "AdditiveMagmasCategory",
    "MultiplicativeMagmas",
    "MultiplicativeMagmasCategory",
    "AdditiveMonoids",
    "AdditiveMonoidsCategory",
    "MultiplicativeMonoids",
    "MultiplicativeMonoidsCategory",
    "Groups",
    "GroupsCategory",
    "AdditiveGroups",
    "AdditiveGroupsCategory",
    "EilenbergMoore",
]

from collections.abc import Callable
from functools import cache, partial

from sage_categories.cat.cat_constructions import LimitSubcategory, limit_of_categories
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.comma import comma_objects
from sage_categories.cat.cones import cone
from sage_categories.cat.declarations import Sets
from sage_categories.cat.diagrams import cospan_diagram, from_sequence
from sage_categories.cat.functors import Cat, Fun, Functor, NaturalTransformation
from sage_categories.cat.shapes import Discrete
from sage_categories.cat.morphisms import Mor, MorphismCategory
from sage_categories.cat.calculus import binary_product_data, pair_maps, product_functor, terminal_map
from sage_categories.cat.monoidal import Cartesian, MonoidalStructuresCategory, tensor_morphism, tensor_parentheses, tensor_units
from sage_categories.cat.predicates import Axiom, Predicate, Proposition, ask
from sage_categories.cat.properties import FullSubcategory, PropertySubcategory
from sage_categories.kernel.refinement import refine
from sage_categories.kernel.retention import identity_key
from sage_categories.kernel.sage_runtime import cached_function, cached_method


class InserterCategory(LimitSubcategory):
    class ObjectType:
        def carrier(self) -> CategoryOfCategories.ElementType:
            return self.family_component(0)

        def structure(self) -> MorphismCategory.ObjectType:
            return self.family_component(1).arrow()

    class ElementType:
        pass

    class MorphismType:
        def underlying_morphism(self) -> MorphismCategory.ObjectType:
            return self.family_component(0)

    def structure_functors(self) -> tuple[Functor, ...]:
        return (*super().structure_functors(), self.forgetful())

    @cached_method(key=identity_key)
    def algebra(
        self,
        carrier: CategoryOfCategories.ElementType,
        structure: MorphismCategory.ObjectType,
    ) -> InserterCategory.ObjectType:
        comma = self.factor(1)
        pair = self.factor(2)((carrier, carrier))
        return self((carrier, comma.from_arrow(carrier, carrier, structure), pair))

    def homomorphism(
        self,
        source: CategoryOfCategories.ElementType,
        target: CategoryOfCategories.ElementType,
        arrow: MorphismCategory.ObjectType,
    ) -> InserterCategory.MorphismType:
        comma, pairs = self.factor(1), self.factor(2)
        return self.construct_morphism(
            source,
            target,
            (
                arrow,
                comma.morphism_from_pair(
                    source.family_component(1), target.family_component(1), arrow, arrow
                ),
                pairs.construct_morphism(
                    source.family_component(2), target.family_component(2), (arrow, arrow)
                ),
            ),
        )

    @cached_method
    def forgetful(self) -> Functor:
        return Fun(self, self.factor(0)).Faithful().Isofibrations()(
            lambda value: value.carrier(), lambda arrow: arrow.underlying_morphism()
        )

    @cached_method
    def defining_transformation(self) -> NaturalTransformation:
        first, second = self.factor(1).comma_functors()
        return Mor(Fun(self, first.codomain()))(
            first * self.forgetful(), second * self.forgetful()
        )(lambda value: value.structure())


@cached_function(key=identity_key)
def Inserter(
    first: Functor,
    second: Functor,
    category_type: Callable[[Functor], InserterCategory] = InserterCategory,
) -> InserterCategory:
    """The inserter of ``first`` and ``second``, retained as the named construction ``category_type``."""
    assert first.domain() is second.domain() and first.codomain() is second.codomain()
    source = first.domain()
    comma = comma_objects(first, second)
    pairs = Cat().Products()((source, source))
    factors = pairs.product_factors()
    diagonal = pairs.universal_morphism(
        cone(factors, source, lambda vertex: Fun(source, source).one())
    )
    diagram = cospan_diagram(Cat(), diagonal, comma.pair_projection())
    return limit_of_categories(diagram, Cat().Pullbacks(), category_type)


class EquifierCategory(FullSubcategory):
    class ObjectType:
        pass

    class ElementType:
        pass

    class MorphismType:
        pass

    def __init__(
        self, first: NaturalTransformation, second: NaturalTransformation
    ) -> None:
        assert (
            first.domain() is second.domain() and first.codomain() is second.codomain()
        )
        self._equations = (first, second)
        super().__init__(first.domain().domain())

    def __call__(
        self, value: CategoryOfCategories.ElementType
    ) -> CategoryOfCategories.ElementType:
        if isinstance(self.ambient(), EquifierCategory):
            self.ambient()(value)
        assert value in self.ambient()
        first, second = self._equations
        assert ask(first.component(value) == second.component(value)) is True
        refine(value, self)
        return value


@cached_function(key=identity_key)
def Equifier(
    first: NaturalTransformation, second: NaturalTransformation
) -> EquifierCategory:
    return EquifierCategory(first, second)


@cached_function(key=identity_key)
def EndofunctorAlgebras(endofunctor: Functor) -> InserterCategory:
    """Algebras of an endofunctor, without imposed laws."""
    assert endofunctor.domain() is endofunctor.codomain()
    return Inserter(endofunctor, Fun(endofunctor.domain(), endofunctor.domain()).one())


class _CommutativePredicate(Predicate):
    """``μ ∘ τ_{X,X} = μ`` for a selected braiding ``τ``; without a selected braiding the proposition stays undecided."""

    name = "commutative_operation"


class _GroupPredicate(Predicate):
    """The shear map of a monoid object is an isomorphism; stated only for a cartesian tensor."""

    name = "group_object"


commutative_operation = _CommutativePredicate()
group_object = _GroupPredicate()


class MagmaCategory(InserterCategory):
    """Magma objects ``(X, μ: X ⊗ X -> X)`` for a selected tensor: one operation, no notation.

    A magma has one operation and nothing names it further; ``+`` and ``*`` are the
    renamed generators of the named copies ``AdditiveMagmas(V)`` and
    ``MultiplicativeMagmas(V)`` (``specs/magmas-monoids-semirings.md``, D185).
    """

    class ObjectType:
        def carrier(self) -> CategoryOfCategories.ElementType:
            return self.family_component(0)

        def structure(self) -> MorphismCategory.ObjectType:
            return self.family_component(1).arrow()

        def operation(self) -> MorphismCategory.ObjectType:
            """The operation ``μ_X: X ⊗ X -> X``, the algebra structure of the endofunctor ``X ↦ X ⊗ X``."""
            return self.structure()

    class ElementType:
        pass

    class MorphismType:
        def underlying_morphism(self) -> MorphismCategory.ObjectType:
            return self.family_component(0)

    def __init__(self, diagram: Functor, tensor: Functor) -> None:
        self._tensor = tensor
        super().__init__(diagram)

    def tensor(self) -> Functor:
        """The selected tensor bifunctor ``⊗: C × C -> C`` whose algebras these are."""
        return self._tensor

    def _commutative(self, magma: MagmaCategory.ObjectType) -> Proposition:
        """``μ ∘ τ_{X,X} == μ``: for the cartesian tensor the braiding is the swap ``⟨π_1, π_0⟩`` (nLab, commutative monoid in a symmetric monoidal category).

        A tensor without a selected braiding gives the bare predicate application, which
        no handler decides.
        """
        base = self.forgetful().codomain()
        if self.tensor() is not product_functor(base):
            return commutative_operation(magma)
        operation = magma.operation()
        data = binary_product_data(base, magma.carrier(), magma.carrier())
        return operation * pair_maps(base, data.leg(1), data.leg(0)) == operation

    Commutative = Axiom(_commutative)


@cached_function(key=identity_key)
def Magmas(structure: Functor | MonoidalStructuresCategory.ObjectType) -> MagmaCategory:
    """Operations ``X ⊗ X -> X`` for a specified tensor bifunctor."""
    if not isinstance(structure, Functor):
        return Magmas(structure.tensor())
    tensor = structure
    source = tensor.codomain()
    pairs = tensor.domain()
    assert (
        pairs.product_projection(0).codomain() is source
        and pairs.product_projection(1).codomain() is source
    )
    diagonal = pair_maps(Cat(), Fun(source, source).one(), Fun(source, source).one())
    return Inserter(tensor * diagonal, Fun(source, source).one(), partial(MagmaCategory, tensor=tensor))


@cached_function(key=identity_key)
def PointedMagmas(
    tensor: Functor, unit: CategoryOfCategories.ElementType
) -> InserterCategory:
    """An operation together with a map from the specified unit object."""
    magmas = Magmas(tensor)
    return Inserter(Fun(magmas, tensor.codomain()).constant(unit), magmas.forgetful())


class MonoidCategory(EquifierCategory):
    """Monoid objects with one operation and a unit in their supplied ambient."""

    class ObjectType:
        def operation(self) -> MorphismCategory.ObjectType:
            """The operation ``μ_X: X ⊗ X -> X`` of the underlying magma."""
            return self.carrier().operation()

        def unit_morphism(self) -> MorphismCategory.ObjectType:
            return self.structure()

    class ElementType:
        pass

    class MorphismType:
        pass

    def __init__(self, first: NaturalTransformation, second: NaturalTransformation, monoidal: MonoidalStructuresCategory.ObjectType) -> None:
        self._monoidal = monoidal
        super().__init__(first, second)

    def monoidal_structure(self) -> MonoidalStructuresCategory.ObjectType:
        return self._monoidal

    def _group(self, monoid: MonoidCategory.ObjectType) -> Proposition:
        """The shear map ``⟨π_0, μ⟩: X × X -> X × X`` is an isomorphism (``specs/magmas-monoids-semirings.md``, "Groups").

        The shear map needs the diagonal, so a non-cartesian tensor gives the bare
        predicate application, which no handler decides.
        """
        monoidal = self.monoidal_structure()
        base = monoidal.underlying_category()
        if monoidal.tensor() is not product_functor(base):
            return group_object(monoid)
        return Mor(base).Isomorphisms().membership_proposition(_shear(monoid))

    Group = Axiom(_group)

    def __call__(self, operation: MorphismCategory.ObjectType, unit: MorphismCategory.ObjectType) -> MonoidCategory.ObjectType:
        monoidal = self.monoidal_structure()
        magma = Magmas(monoidal).algebra(operation.codomain(), operation)
        pointed = PointedMagmas(monoidal.tensor(), monoidal.unit()).algebra(magma, unit)
        return super().__call__(pointed)

    @cached_method
    def to_magmas(self) -> Functor:
        monoidal = self.monoidal_structure()
        pointed = PointedMagmas(monoidal.tensor(), monoidal.unit())
        return pointed.forgetful() * Fun.full_subcategory_monomorphism(self, pointed)


@cached_function(key=identity_key)
def Monoids(structure: Category | MonoidalStructuresCategory.ObjectType) -> MonoidCategory:
    """Monoid objects for the supplied tensor, unit, associator, and unitors."""
    if isinstance(structure, Category):
        return Monoids(Cartesian(structure))
    base, tensor = structure.underlying_category(), structure.tensor()
    pointed = PointedMagmas(tensor, structure.unit())
    forget = Magmas(tensor).forgetful() * pointed.forgetful()

    def unital(
        value: CategoryOfCategories.ElementType, left: bool
    ) -> MorphismCategory.ObjectType:
        carrier = value.carrier().carrier()
        operation, unit = value.carrier().operation(), value.structure()
        identity = Mor(base)(carrier, carrier).one()
        return operation * tensor_morphism(
            tensor, unit if left else identity, identity if left else unit
        )

    def associative(
        value: CategoryOfCategories.ElementType, left: bool
    ) -> MorphismCategory.ObjectType:
        carrier, operation = value.carrier().carrier(), value.carrier().operation()
        identity = Mor(base)(carrier, carrier).one()
        if left:
            return operation * tensor_morphism(tensor, operation, identity)
        associator = structure.associator().component(
            structure.associator().domain().domain()((carrier, carrier, carrier)))
        return operation * tensor_morphism(tensor, identity, operation) * associator

    transformations = Mor(Fun(pointed, base))
    left_unit, right_unit = tensor_units(tensor, structure.unit())
    triples = structure.associator().domain().domain()
    diagonal = triples.universal_morphism(cone(
        triples.product_factors(), base, lambda vertex: Fun(base, base).one()))
    cube = tensor_parentheses(tensor)[0] * diagonal * forget
    equations = (
        (transformations(left_unit * forget, forget)(lambda value: unital(value, True)), structure.left_unitor().whisker_right(forget)),
        (transformations(right_unit * forget, forget)(lambda value: unital(value, False)), structure.right_unitor().whisker_right(forget)),
        (
            transformations(cube, forget)(lambda value: associative(value, True)),
            transformations(cube, forget)(lambda value: associative(value, False)),
        ),
    )
    result = pointed
    for first, second in equations[:-1]:
        inclusion = (
            Fun.full_subcategory_monomorphism(result, pointed)
            if result is not pointed
            else Fun(pointed, pointed).one()
        )
        result = Equifier(
            first.whisker_right(inclusion), second.whisker_right(inclusion)
        )
    inclusion = Fun.full_subcategory_monomorphism(result, pointed)
    first, second = equations[-1]
    return MonoidCategory(first.whisker_right(inclusion), second.whisker_right(inclusion), structure)


# -- group objects: monoid objects whose shear map is an isomorphism -----------------------------


@cached_function(key=identity_key)
def _shear(monoid: MonoidCategory.ObjectType) -> MorphismCategory.ObjectType:
    """``⟨π_0, μ⟩: X × X -> X × X``, ``(x, y) ↦ (x, xy)``: the shear map of the left regular action.

    The action is regular exactly when this map is an isomorphism (nLab, shear map,
    "Definition"), and a monoid whose left regular action is regular is a group.
    """
    operation = monoid.operation()
    base, carrier = operation.base_category(), operation.codomain()
    return pair_maps(base, binary_product_data(base, carrier, carrier).leg(0), operation)


class GroupsCategory(PropertySubcategory):
    """``Monoids(V).Group()``: monoid objects whose shear map is an isomorphism, with the inversion that isomorphism determines."""

    _base_category_class_and_axiom = (MonoidCategory, "Group")

    class ObjectType:
        @cache
        def inversion(self) -> MorphismCategory.ObjectType:
            """``ι = π_1 ∘ ⟨π_0, μ⟩⁻¹ ∘ ⟨1_X, η ∘ !_X⟩``: the shear inverse read at ``(x, e)`` gives ``(x, x⁻¹)``."""
            operation = self.operation()
            base, carrier = operation.base_category(), operation.codomain()
            shear = _shear(self)
            assert shear in Mor(base).Isomorphisms(), f"{self!r} is placed among group objects but its shear map is not an isomorphism"
            unit_everywhere = self.unit_morphism() * terminal_map(base, carrier)
            at_unit = pair_maps(base, Mor(base)(carrier, carrier).one(), unit_everywhere)
            return binary_product_data(base, carrier, carrier).leg(1) * shear.inverse() * at_unit

    class ElementType:
        pass

    class MorphismType:
        pass


@cached_function(key=identity_key)
def Groups(structure: Category | MonoidalStructuresCategory.ObjectType) -> GroupsCategory:
    """``Monoids(V).Group()`` for a cartesian monoidal ``V``: group objects, a full property subcategory of the monoid objects."""
    if isinstance(structure, Category):
        return Groups(Cartesian(structure))
    return Monoids(structure).Group()


# -- named operations: a structure category tagged by the one-object category of a symbol (D185) --
#
# Notation is not mathematics.  ``+`` and ``*`` are renamings of the one generator of the
# magma theory, and renaming a generator is an isomorphism of presented theories, so its
# models form a category isomorphic to ``Magmas(V)`` and distinct from it.  That category
# is the product ``Magmas(V) × 1_s`` with the one-object category on the symbol ``s``:
# distinct in ``Cat`` because ``1_+`` and ``1_*`` are distinct objects, isomorphic to
# ``Magmas(V)`` through its first projection.  The projection is the restriction along the
# renaming and is retained for access only, so no neutral name crosses it; the surface a
# named copy writes is its renamed generator, and its carrier reaches ``X`` through a
# declared faithful isofibration (``specs/magmas-monoids-semirings.md``, "Named operations").


def _symbol_category(symbol: str) -> Category:
    """``1_s``: the one-object category on the formal symbol ``s``, the discrete category of ``{s}``."""
    return Discrete(Sets((symbol,)))


def _named_copy(neutral: Category, symbol: str, category_type: type[NamedOperationCategory]) -> NamedOperationCategory:
    """``neutral × 1_s`` in ``Cat``, retained as ``category_type`` with its projections.

    The retained first projection is also selected on the copy as a plain functor: it
    supplies access, so the axioms of the neutral category reach the copy as inverse
    images along it, and carries no inheritance (D167, D185).
    """
    diagram = from_sequence(Cat(), (neutral, _symbol_category(symbol)))
    copy = limit_of_categories(diagram, Cat().Limits(diagram.domain()), category_type)
    copy._retain_structure_functor(copy.product_projection(0))
    return copy


def _carrier_point(point: CategoryOfCategories.ElementType) -> tuple[Category, MorphismCategory.ObjectType]:
    """The point read in the carrier through the retained point comparison, as its morphism ``1_C -> X``, with ``C``."""
    comparison = point.parent().point_comparison()
    carrier = comparison.codomain().index_set()
    base = carrier.category()
    return base, base.point_morphism(comparison.on_object(point).point())


def _apply(point: CategoryOfCategories.ElementType, arrow: MorphismCategory.ObjectType) -> CategoryOfCategories.ElementType:
    """``f ∘ x``: an endomorphism of the carrier applied to a point, re-owned by the structured object."""
    base, x = _carrier_point(point)
    return point.parent().object_at(base.element_from_defining_morphism(arrow * x))


def _combine(
    first: CategoryOfCategories.ElementType,
    second: CategoryOfCategories.ElementType,
    operation: MorphismCategory.ObjectType,
) -> CategoryOfCategories.ElementType:
    """``μ ∘ ⟨x, y⟩``: two points of a structured object combined through its operation.

    The points are read in the carrier through the retained point comparison, paired
    through the chosen product, sent along the operation, and the resulting point of the
    carrier is re-owned by the structured object (``specs/magmas-monoids-semirings.md``,
    "Named operations", the generalized-element diagram).
    """
    owner = first.parent()
    assert second.parent() is owner, f"{first!r} and {second!r} are points of different objects"
    base, x = _carrier_point(first)
    _, y = _carrier_point(second)
    return owner.object_at(base.element_from_defining_morphism(operation * pair_maps(base, x, y)))


def _unit_point(owner: CategoryOfCategories.ElementType, unit: MorphismCategory.ObjectType) -> CategoryOfCategories.ElementType:
    """The point ``1 -> X`` a unit morphism selects when the monoidal unit is terminal, re-owned by the structured object."""
    return owner.object_at(unit.codomain().category().element_from_defining_morphism(unit))


class NamedOperationCategory(LimitSubcategory):
    """``N × 1_s``: the neutral structure category ``N`` tagged by the one-object category of a symbol.

    An object is the pair of a neutral object and the symbol; ``renamed`` constructs it
    over a neutral object.  ``product_projection(0)`` is the renaming isomorphism onto
    ``N``, a retained leg carrying no inheritance.  Each concrete copy writes its own
    role declarations (POL-CAT-057): ``neutral()`` and ``neutral_morphism()`` read the
    first component, the renamed generator is its surface, and its structure functor
    carries the carrier.
    """

    class ObjectType:
        pass

    class ElementType:
        pass

    class MorphismType:
        pass

    def neutral_category(self) -> Category:
        return self.factor(0)

    def symbol_category(self) -> Category:
        return self.factor(1)

    def symbol(self) -> CategoryOfCategories.ElementType:
        """The one object of ``1_s``."""
        tag = self.symbol_category()
        return tag(next(iter(tag.index_set())))

    def renamed(self, neutral_object: CategoryOfCategories.ElementType) -> NamedOperationCategory.ObjectType:
        """The object of this category over an object of the neutral one."""
        return self((neutral_object, self.symbol()))

    def homomorphism(
        self,
        source: NamedOperationCategory.ObjectType,
        target: NamedOperationCategory.ObjectType,
        arrow: MorphismCategory.ObjectType,
    ) -> NamedOperationCategory.MorphismType:
        """The morphism over a morphism of the neutral category."""
        tag = self.symbol_category()
        return self.construct_morphism(
            source, target, (arrow, Mor(tag)(source.family_component(1), target.family_component(1)).one())
        )

    @cached_method
    def to_carrier(self) -> Functor:
        """``(X, μ, s) ↦ X``: restriction along the inclusion of the empty theory, declared to carry inheritance."""
        carrier = self.neutral_category().forgetful()
        return Fun(self, carrier.codomain()).Faithful().Isofibrations()(
            lambda value: carrier.on_object(value.neutral()),
            lambda arrow: carrier.on_morphism(arrow.neutral_morphism()),
        )

    @cached_method
    def to_named_magmas(self) -> Functor:
        """``(M, s) ↦ (M's magma, s)``: restriction along the inclusion of presentations ``{s} ⊂ {s, e}``."""
        neutral = self.neutral_category()
        magmas, to_magmas = self.named_magmas(), neutral.to_magmas()

        def on_object(value: NamedOperationCategory.ObjectType) -> NamedOperationCategory.ObjectType:
            return magmas.renamed(to_magmas.on_object(value.neutral()))

        def on_morphism(arrow: NamedOperationCategory.MorphismType) -> NamedOperationCategory.MorphismType:
            return magmas.homomorphism(
                on_object(arrow.domain()), on_object(arrow.codomain()), to_magmas.on_morphism(arrow.neutral_morphism())
            )

        return Fun(self, magmas).Faithful().Isofibrations()(on_object, on_morphism)

    def named_magmas(self) -> NamedOperationCategory:
        """The magma copy under the same symbol this category restricts to."""
        raise AssertionError(f"{self!r} names no magma copy its structure functor restricts to")

    @cached_method
    def to_named_monoids(self) -> Functor:
        """``(G, s) ↦ (G, s)``: restriction along the inclusion of presentations ``{s, e} ⊂ {s, e, ι}``; a group object is its monoid object."""
        monoids = self.named_monoids()

        def on_object(value: NamedOperationCategory.ObjectType) -> NamedOperationCategory.ObjectType:
            return monoids.renamed(value.neutral())

        def on_morphism(arrow: NamedOperationCategory.MorphismType) -> NamedOperationCategory.MorphismType:
            return monoids.homomorphism(on_object(arrow.domain()), on_object(arrow.codomain()), arrow.neutral_morphism())

        return Fun(self, monoids).Faithful().Isofibrations()(on_object, on_morphism)

    def named_monoids(self) -> NamedOperationCategory:
        """The monoid copy under the same symbol this category restricts to."""
        raise AssertionError(f"{self!r} names no monoid copy its structure functor restricts to")


class AdditiveMagmasCategory(NamedOperationCategory):
    """``Magmas(V) × 1_+``: the operation is written ``addition()`` and ``+`` on points."""

    class ObjectType:
        def neutral(self) -> CategoryOfCategories.ElementType:
            return self.family_component(0)

        def addition(self) -> MorphismCategory.ObjectType:
            return self.neutral().operation()

    class ElementType:
        def __add__(self, other: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
            return _combine(self, other, self.parent().addition())

    class MorphismType:
        def neutral_morphism(self) -> MorphismCategory.ObjectType:
            return self.family_component(0)

    def structure_functors(self) -> tuple[Functor, ...]:
        return (*super().structure_functors(), self.to_carrier())


class MultiplicativeMagmasCategory(NamedOperationCategory):
    """``Magmas(V) × 1_*``: the operation is written ``multiplication()`` and ``*`` on points."""

    class ObjectType:
        def neutral(self) -> CategoryOfCategories.ElementType:
            return self.family_component(0)

        def multiplication(self) -> MorphismCategory.ObjectType:
            return self.neutral().operation()

    class ElementType:
        def __mul__(self, other: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
            return _combine(self, other, self.parent().multiplication())

    class MorphismType:
        def neutral_morphism(self) -> MorphismCategory.ObjectType:
            return self.family_component(0)

    def structure_functors(self) -> tuple[Functor, ...]:
        return (*super().structure_functors(), self.to_carrier())


class AdditiveMonoidsCategory(NamedOperationCategory):
    """``Monoids(V) × 1_+``: the unit is written ``zero()``; ``addition()`` and ``+`` arrive from ``AdditiveMagmas(V)``."""

    class ObjectType:
        def neutral(self) -> CategoryOfCategories.ElementType:
            return self.family_component(0)

        def zero(self) -> CategoryOfCategories.ElementType:
            """The point the unit selects, when the monoidal unit is terminal."""
            return _unit_point(self, self.neutral().unit_morphism())

    class ElementType:
        pass

    class MorphismType:
        def neutral_morphism(self) -> MorphismCategory.ObjectType:
            return self.family_component(0)

    def named_magmas(self) -> AdditiveMagmasCategory:
        return AdditiveMagmas(self.neutral_category().monoidal_structure())

    def structure_functors(self) -> tuple[Functor, ...]:
        return (*super().structure_functors(), self.to_named_magmas())


class MultiplicativeMonoidsCategory(NamedOperationCategory):
    """``Monoids(V) × 1_*``: the unit is written ``one()``; ``multiplication()`` and ``*`` arrive from ``MultiplicativeMagmas(V)``."""

    class ObjectType:
        def neutral(self) -> CategoryOfCategories.ElementType:
            return self.family_component(0)

        def one(self) -> CategoryOfCategories.ElementType:
            """The point the unit selects, when the monoidal unit is terminal."""
            return _unit_point(self, self.neutral().unit_morphism())

    class ElementType:
        pass

    class MorphismType:
        def neutral_morphism(self) -> MorphismCategory.ObjectType:
            return self.family_component(0)

    def named_magmas(self) -> MultiplicativeMagmasCategory:
        return MultiplicativeMagmas(self.neutral_category().monoidal_structure())

    def structure_functors(self) -> tuple[Functor, ...]:
        return (*super().structure_functors(), self.to_named_magmas())


class AdditiveGroupsCategory(NamedOperationCategory):
    """``Groups(V) × 1_+``: the inversion is written ``negation()``, ``-x``, and ``x - y := x + (-y)``; ``zero()``, ``addition()``, and ``+`` arrive from ``AdditiveMonoids(V)``."""

    class ObjectType:
        def neutral(self) -> CategoryOfCategories.ElementType:
            return self.family_component(0)

        def negation(self) -> MorphismCategory.ObjectType:
            """``ι_X: X -> X``, the inversion of the group object."""
            return self.neutral().inversion()

    class ElementType:
        def __neg__(self) -> CategoryOfCategories.ElementType:
            return _apply(self, self.parent().negation())

        def __sub__(self, other: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
            return self + (-other)

    class MorphismType:
        def neutral_morphism(self) -> MorphismCategory.ObjectType:
            return self.family_component(0)

    def named_monoids(self) -> AdditiveMonoidsCategory:
        return AdditiveMonoids(self.neutral_category().ambient().monoidal_structure())

    def structure_functors(self) -> tuple[Functor, ...]:
        return (*super().structure_functors(), self.to_named_monoids())


@cached_function(key=identity_key)
def AdditiveGroups(structure: Category | MonoidalStructuresCategory.ObjectType) -> AdditiveGroupsCategory:
    """``Groups(V) × 1_+``: group objects whose operation is written ``+``, with ``zero()``, ``negation()``, and ``-``."""
    if isinstance(structure, Category):
        return AdditiveGroups(Cartesian(structure))
    return _named_copy(Groups(structure), "+", AdditiveGroupsCategory)


@cached_function(key=identity_key)
def AdditiveMagmas(structure: Functor | MonoidalStructuresCategory.ObjectType) -> AdditiveMagmasCategory:
    """``Magmas(V) × 1_+``: magma objects whose operation is written ``+``."""
    if not isinstance(structure, Functor):
        return AdditiveMagmas(structure.tensor())
    return _named_copy(Magmas(structure), "+", AdditiveMagmasCategory)


@cached_function(key=identity_key)
def MultiplicativeMagmas(structure: Functor | MonoidalStructuresCategory.ObjectType) -> MultiplicativeMagmasCategory:
    """``Magmas(V) × 1_*``: magma objects whose operation is written ``*``."""
    if not isinstance(structure, Functor):
        return MultiplicativeMagmas(structure.tensor())
    return _named_copy(Magmas(structure), "*", MultiplicativeMagmasCategory)


@cached_function(key=identity_key)
def AdditiveMonoids(structure: Category | MonoidalStructuresCategory.ObjectType) -> AdditiveMonoidsCategory:
    """``Monoids(V) × 1_+``: monoid objects whose operation is written ``+`` and whose unit is ``zero()``."""
    if isinstance(structure, Category):
        return AdditiveMonoids(Cartesian(structure))
    return _named_copy(Monoids(structure), "+", AdditiveMonoidsCategory)


@cached_function(key=identity_key)
def MultiplicativeMonoids(structure: Category | MonoidalStructuresCategory.ObjectType) -> MultiplicativeMonoidsCategory:
    """``Monoids(V) × 1_*``: monoid objects whose operation is written ``*`` and whose unit is ``one()``."""
    if isinstance(structure, Category):
        return MultiplicativeMonoids(Cartesian(structure))
    return _named_copy(Monoids(structure), "*", MultiplicativeMonoidsCategory)


@cached_function(key=identity_key)
def EilenbergMoore(
    endofunctor: Functor,
    unit: NaturalTransformation,
    multiplication: NaturalTransformation,
) -> EquifierCategory:
    """Algebras of the supplied monad, with both algebra laws imposed by equifiers.

    The supplied unit and multiplication must satisfy the monad laws.
    Reference: Mathlib CategoryTheory.Monad.Algebra.
    """
    base = endofunctor.domain()
    assert endofunctor.codomain() is base
    assert unit.domain() is Fun(base, base).one() and unit.codomain() is endofunctor
    assert (
        multiplication.domain() is endofunctor * endofunctor
        and multiplication.codomain() is endofunctor
    )
    algebras = EndofunctorAlgebras(endofunctor)
    forget = algebras.forgetful()
    action = algebras.defining_transformation()
    unital = Equifier(
        action * unit.whisker_right(forget),
        Mor(Fun(algebras, base))(forget, forget).one(),
    )
    inclusion = Fun.full_subcategory_monomorphism(unital, algebras)
    left = (action * multiplication.whisker_right(forget)).whisker_right(inclusion)
    right = (action * action.whisker_left(endofunctor)).whisker_right(inclusion)
    return Equifier(left, right)
