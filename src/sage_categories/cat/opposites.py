"""Opposite categories, functors, and natural transformations.

``Op: Cat() -> Cat()`` sends a category to its opposite and a functor to its
opposite.  A natural transformation ``eta: F => G`` gives
``eta.op(): G.op() => F.op()``.  Opposite construction is involutive by retained
identity, and ``Op * Op`` retains its natural isomorphism with the identity
endofunctor (``specs/functor.md``, "Opposites and dualization").
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from sage.structure.coerce_dict import MonoDict

from sage_categories.cat.category import Category
from sage_categories.cat.functors import Cat, Fun, Functor, NaturalTransformation
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.predicates import Proposition
from sage_categories.kernel.refinement import refine

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
            super().__init__()

        def original(self) -> MorphismCategory.ObjectType:
            """The morphism of ``C`` represented in the opposite direction."""
            return self._opposite_original

    def __init__(self, original: Category[MorphismData, TwoMorphismData]) -> None:
        self._original = original
        super().__init__()

    def original(self) -> Category[MorphismData, TwoMorphismData]:
        """The category whose opposite this is."""
        return self._original

    def membership_proposition(self, candidate: CategoryOfCategories.ElementType) -> Proposition:
        return self._original.membership_proposition(candidate)

    def __call__(self, value: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
        """Regard an object of ``C`` as the same object of ``C.op()``."""
        assert value in self._original, f"{value!r} is not an object of {self._original!r}"
        refine(value, self)
        return value

    def construct_morphism(
        self,
        domain: CategoryOfCategories.ElementType,
        codomain: CategoryOfCategories.ElementType,
        original: MorphismCategory.ObjectType,
    ) -> MorphismCategory.ObjectType:
        """Construct ``f.op(): domain -> codomain`` from ``f: codomain -> domain``."""
        assert original in self._original.morphism_category(1)(codomain, domain)
        return self.MorphismType(
            category=self.morphism_category(1),
            domain=domain,
            codomain=codomain,
            data=_OppositeMorphismData(original),
        )

    def construct_identity(
        self,
        member_object: CategoryOfCategories.ElementType,
    ) -> MorphismCategory.ObjectType:
        identity = self._original.morphism_category(1)(member_object, member_object).one()
        return self.construct_morphism(member_object, member_object, identity)

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

    def __repr__(self) -> str:
        return f"{self._original!r}.op()"


_opposite_categories: MonoDict = MonoDict()
_opposite_functors: MonoDict = MonoDict()
_opposite_transformations: MonoDict = MonoDict()


def opposite_category(category: Category) -> Category:
    """Return the retained opposite category, with ``C.op().op() is C``."""
    if category not in _opposite_categories:
        opposite = OppositeCategory(category)
        _opposite_categories[category] = opposite
        _opposite_categories[opposite] = category
    return _opposite_categories[category]


def _opposite_morphism(
    category: Category,
    morphism: MorphismCategory.ObjectType,
) -> MorphismCategory.ObjectType:
    """Reverse one morphism while preserving the retained double-opposite identity."""
    if isinstance(category, OppositeCategory):
        assert morphism in category.morphism_category(1)
        return morphism.original()
    opposite = opposite_category(category)
    return opposite.morphism_category(1)(morphism.codomain(), morphism.domain())(morphism)


def opposite_morphism(morphism: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
    """Return the retained opposite of a categorical morphism."""
    return _opposite_morphism(morphism.base_category(), morphism)


def _construct_opposite_functor(functor: Functor) -> Functor:
    if functor in _opposite_functors:
        return _opposite_functors[functor]

    source = opposite_category(functor.domain())
    target = opposite_category(functor.codomain())

    def on_object(
        value: CategoryOfCategories.ElementType,
    ) -> CategoryOfCategories.ElementType:
        return functor.on_object(value)

    def on_morphism(morphism: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        original = _opposite_morphism(source, morphism)
        return _opposite_morphism(functor.codomain(), functor.on_morphism(original))

    opposite = Fun(source, target)(on_object, on_morphism)
    _opposite_functors[functor] = opposite
    _opposite_functors[opposite] = functor
    return opposite


Op: Functor = Fun(Cat(), Cat())(opposite_category, _construct_opposite_functor)


def opposite_functor(functor: Functor) -> Functor:
    """Return ``F.op(): C.op() -> D.op()`` through the retained ``Op`` action."""
    return Op.on_morphism(functor)


def opposite_transformation(transformation: NaturalTransformation) -> NaturalTransformation:
    """Return ``eta.op(): G.op() => F.op()`` for ``eta: F => G``."""
    if transformation in _opposite_transformations:
        return _opposite_transformations[transformation]

    source = transformation.source_functor()
    target = transformation.target_functor()
    source_op = opposite_functor(source)
    target_op = opposite_functor(target)
    functors = Fun(source_op.domain(), source_op.codomain())
    opposite = functors.morphism_category(1)(target_op, source_op)(
        lambda value: _opposite_morphism(source.codomain(), transformation.component(value))
    )
    _opposite_transformations[transformation] = opposite
    _opposite_transformations[opposite] = transformation
    return opposite


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
