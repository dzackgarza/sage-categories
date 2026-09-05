"""Opposite categories, functors, and natural transformations.

``Op: Cat() -> Cat()`` sends a category to its opposite and a functor to its
opposite.  A natural transformation ``eta: F => G`` gives
``eta.op(): G.op() => F.op()``.  Opposite construction is involutive by retained
identity, and ``Op * Op`` retains its natural isomorphism with the identity
endofunctor (``specs/functor.md``, "Opposites and dualization").
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING

from sage_categories.cat.category import Category
from sage_categories.cat.functors import Cat, Fun, Functor, NaturalTransformation
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.predicates import Proposition, UnknownClass
from sage_categories.kernel.refinement import is_placed, refine
from sage_categories.kernel.retention import deferred_category, identity_key, retained_involution
from sage_categories.kernel.sage_runtime import cached_function
from sage_categories.kernel.roles import Role

if TYPE_CHECKING:
    from sage_categories.cat.category import CategoryOfCategories

__all__ = [
    "Op",
    "OppositeCategory",
    "op_squared_isomorphism",
    "opposite_category",
    "opposite_functor",
    "opposite_morphism",
    "opposite_transformation",
]


@dataclass(frozen=True, eq=False, slots=True)
class _OppositeMorphismData:
    original: MorphismCategory.ObjectType


class OppositeCategory[**MorphismData, **TwoMorphismData](
    Category[[MorphismCategory.ObjectType], []]
):
    """``C.op()``: the objects of ``C`` with every morphism reversed."""

    class ObjectType:
        """An object of ``C``, read as an object of ``C.op()``."""

    class ElementType:
        """A generalized element in the opposite category."""

    class MorphismType:
        """The opposite of one morphism of ``C``."""

        def __init__(self, data: _OppositeMorphismData) -> None:
            self._opposite_original = data.original

        def original(self) -> MorphismCategory.ObjectType:
            """The morphism of ``C`` represented in the opposite direction."""
            return self._opposite_original

    def __init__(self, original: Category[MorphismData, TwoMorphismData]) -> None:
        self._original = original
        super().__init__()

    def original(self) -> Category[MorphismData, TwoMorphismData]:
        """The category whose opposite this is."""
        return self._original

    def is_discrete(self) -> bool:
        """A discrete category is its own opposite's representation."""
        return self._original.is_discrete()

    def role_source(self, role: Role) -> tuple[Category, Role]:
        """A category and its opposite have the same objects."""
        return (self._original, role) if role is Role.OBJECT else (self, role)

    def narrowing_base(self) -> Category:
        """The opposite of the original narrowing base."""
        return self._original.narrowing_base().op()

    def narrowing_roots(self) -> tuple[Category, ...]:
        """The retained opposites of the original narrowing roots."""
        return tuple(root.op() for root in self._original.narrowing_roots())

    def structure_functors(self) -> tuple[Functor, ...]:
        """The opposites of the original category's selected functors."""
        return tuple(opposite_functor(functor) for functor in self._original.selected_functors())

    def membership_proposition(self, candidate: CategoryOfCategories.ElementType) -> Proposition:
        return self._original.membership_proposition(candidate)

    def __call__(self, value: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
        """Regard an object of ``C`` as the same object of ``C.op()``, or construct via ``C(value)``."""
        if value in self._original:
            return value
        return self._original(value)

    def object_set(self) -> CategoryOfCategories.ElementType:
        return self._original.object_set()

    def object_at(self, point: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
        """A category and its opposite share their objects."""
        return self._original.object_at(point)

    def object_point(self, member_object: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
        return self._original.object_point(member_object)

    def generating_morphisms(self) -> tuple[MorphismCategory.ObjectType, ...] | UnknownClass:
        from sage_categories.cat.predicates import Unknown

        arrows = self._original.generating_morphisms()
        return Unknown if arrows is Unknown else tuple(opposite_morphism(arrow) for arrow in arrows)

    def construct_morphism(
        self,
        domain: CategoryOfCategories.ElementType,
        codomain: CategoryOfCategories.ElementType,
        original: MorphismCategory.ObjectType,
    ) -> MorphismCategory.ObjectType:
        """Construct ``f.op(): domain -> codomain`` from ``f: codomain -> domain``."""
        assert original in self._original.morphism_category(1)(codomain, domain)
        return self.MorphismType(
            domain=domain,
            codomain=codomain,
            data=_OppositeMorphismData(original),
        )

    def construct_identity(
        self,
        member_object: CategoryOfCategories.ElementType,
    ) -> MorphismCategory.ObjectType:
        identity = self._original.morphism_category(1)(member_object, member_object).one()
        return opposite_morphism(identity)

    def composite(
        self,
        second: MorphismCategory.ObjectType,
        first: MorphismCategory.ObjectType,
    ) -> MorphismCategory.ObjectType:
        original = self._original.compose_morphisms(first.original(), second.original())
        return self.construct_morphism(first.domain(), second.codomain(), original)

    def _symbolic_inverse_(self, morphism: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        original = self._original.inverse_morphism(morphism.original())
        return self.construct_morphism(morphism.codomain(), morphism.domain(), original)

    def limit_construction(self, shape: Category) -> Callable[[Functor], CategoryOfCategories.ElementType]:
        return Category.limit_construction(self, shape)

    def colimit_construction(self, shape: Category) -> Callable[[Functor], CategoryOfCategories.ElementType]:
        shape_orig = shape._original if isinstance(shape, OppositeCategory) else shape
        return self._original.limit_construction(shape_orig)

    def __repr__(self) -> str:
        return f"{self._original!r}.op()"


def opposite_category(category: Category) -> Category:
    """Return the retained opposite category, with ``C.op().op() is C``."""
    base, roots = category.narrowing_base(), category.narrowing_roots()
    if base is not category and not any(root is category for root in roots):
        return base.op().intersection(tuple(root.op() for root in roots))
    return _opposite_category(category)


@retained_involution
def _opposite_category(category: Category) -> Category:
    return deferred_category(OppositeCategory, category)


@cached_function(key=identity_key)
def _opposite_morphism(
    category: Category,
    morphism: MorphismCategory.ObjectType,
) -> MorphismCategory.ObjectType:
    """Reverse one morphism while preserving the retained double-opposite identity."""
    if isinstance(category.narrowing_base(), OppositeCategory):
        assert morphism in category.morphism_category(1)
        return morphism.original()
    opposite = opposite_category(category)
    return opposite.morphism_category(1)(morphism.codomain(), morphism.domain())(morphism)


def opposite_morphism(morphism: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
    """Return the retained opposite of a categorical morphism."""
    return _opposite_morphism(morphism.base_category(), morphism)


@retained_involution
def _construct_opposite_functor(functor: Functor) -> Functor:
    """Dualize both actions, preserving a declared subcategory inclusion."""
    source = opposite_category(functor.domain())
    target = opposite_category(functor.codomain())
    diagrams = Fun(functor.domain(), functor.codomain())
    if diagrams.has_constant_value(functor):
        return Fun(source, target).constant(diagrams.constant_value(functor))
    if Fun.declares_subcategory(functor):
        if is_placed(functor, Fun.Full()):
            return Fun.full_subcategory_monomorphism(source, target)
        return Fun.subcategory_monomorphism(source, target)

    def on_object(
        value: CategoryOfCategories.ElementType,
    ) -> CategoryOfCategories.ElementType:
        return functor.on_object(value)

    def on_morphism(morphism: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        original = _opposite_morphism(source, morphism)
        return _opposite_morphism(functor.codomain(), functor.on_morphism(original))

    opposite = Fun(source, target)(on_object, on_morphism)
    if is_placed(functor, Fun.Fibrations()):
        refine(opposite, Fun(source, target).Opfibrations())
        opposite.retain_cocartesian_lifts(
            lambda arrow, value: _opposite_morphism(
                functor.domain(),
                functor.cartesian_lift(_opposite_morphism(target, arrow), value),
            )
        )
    if is_placed(functor, Fun.Opfibrations()):
        refine(opposite, Fun(source, target).Fibrations())
        opposite.retain_cartesian_lifts(
            lambda arrow, value: _opposite_morphism(
                functor.domain(),
                functor.cocartesian_lift(_opposite_morphism(target, arrow), value),
            )
        )
    return opposite


Op: Functor = Fun(Cat(), Cat())(opposite_category, _construct_opposite_functor)


def opposite_functor(functor: Functor) -> Functor:
    """Return ``F.op(): C.op() -> D.op()`` through the retained ``Op`` action."""
    return Op.on_morphism(functor)


@retained_involution
def opposite_transformation(transformation: NaturalTransformation) -> NaturalTransformation:
    """Return ``eta.op(): G.op() => F.op()`` for ``eta: F => G``."""
    source = transformation.source_functor()
    target = transformation.target_functor()
    source_op = opposite_functor(source)
    target_op = opposite_functor(target)
    functors = Fun(source_op.domain(), source_op.codomain())
    return functors.morphism_category(1)(target_op, source_op)(
        lambda value: _opposite_morphism(source.codomain(), transformation.component(value))
    )


def _construct_op_squared_isomorphism() -> NaturalTransformation:
    endofunctors = Fun(Cat(), Cat())
    doubled = Op * Op
    identity = endofunctors.one()

    def component(category: Category) -> Functor:
        return Fun(category, category).one()

    forward = endofunctors.morphism_category(1)(doubled, identity)(component)
    backward = endofunctors.morphism_category(1)(identity, doubled)(component)
    endofunctors.retain_inverses(forward, backward)
    return forward


_op_squared_isomorphism = _construct_op_squared_isomorphism()


def op_squared_isomorphism() -> NaturalTransformation:
    """Return the retained natural isomorphism ``Op * Op => Id_Cat``."""
    return _op_squared_isomorphism
