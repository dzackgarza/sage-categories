"""Universal arrows and adjunctions from chosen terminal comma objects.

Reference: Riehl, Category Theory in Context, Theorem 4.6.1.
"""

from __future__ import annotations

__all__ = [
    "TerminalObjectsCategory",
    "TerminalObjects",
    "InitialObjectsCategory",
    "InitialObjects",
    "RightUniversalArrows",
    "LeftUniversalArrows",
    "right_mate",
    "left_mate",
]

from collections.abc import Callable
from dataclasses import dataclass

from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.comma import comma_objects
from sage_categories.cat.functors import Cat, Fun, Functor, NaturalTransformation
from sage_categories.cat.morphisms import Mor, MorphismCategory
from sage_categories.cat.properties import FullSubcategory
from sage_categories.kernel.refinement import refine
from sage_categories.kernel.retention import identity_key
from sage_categories.kernel.sage_runtime import cached_function, cached_method

type Factor = Callable[[CategoryOfCategories.ElementType], MorphismCategory.ObjectType]
type Choice = Callable[
    [CategoryOfCategories.ElementType], CategoryOfCategories.ElementType
]


class TerminalObjectsCategory(FullSubcategory):
    """Terminal objects equipped with their unique incoming arrows."""

    class ObjectType:
        def unique_from(
            self, source: CategoryOfCategories.ElementType
        ) -> MorphismCategory.ObjectType:
            arrow = self._terminal_factor(source)
            assert arrow.domain() is source and arrow.codomain() is self
            return arrow

    class ElementType:
        pass

    class MorphismType:
        pass

    def __call__(
        self, value: CategoryOfCategories.ElementType, factor: Factor
    ) -> CategoryOfCategories.ElementType:
        assert value in self.ambient()
        value._terminal_factor = factor
        refine(value, self)
        return value


@cached_function(key=identity_key)
def TerminalObjects(category: Category) -> TerminalObjectsCategory:
    return TerminalObjectsCategory(category)


class InitialObjectsCategory(FullSubcategory):
    """Initial objects equipped with their unique outgoing arrows."""

    class ObjectType:
        def unique_to(
            self, target: CategoryOfCategories.ElementType
        ) -> MorphismCategory.ObjectType:
            arrow = self._initial_factor(target)
            assert arrow.domain() is self and arrow.codomain() is target
            return arrow

    class ElementType:
        pass

    class MorphismType:
        pass

    def __call__(
        self, value: CategoryOfCategories.ElementType, factor: Factor
    ) -> CategoryOfCategories.ElementType:
        assert value in self.ambient()
        value._initial_factor = factor
        refine(value, self)
        return value


@cached_function(key=identity_key)
def InitialObjects(category: Category) -> InitialObjectsCategory:
    return InitialObjectsCategory(category)


@dataclass(eq=False)
class RightUniversalArrows:
    """A chosen terminal object of ``(F ↓ d)`` for every ``d``."""

    forward: Functor
    choose: Choice

    @cached_method(key=identity_key)
    def presentation(
        self, value: CategoryOfCategories.ElementType
    ) -> CategoryOfCategories.ElementType:
        result = self.choose(value)
        comma = comma_objects(
            self.forward, self.forward.codomain().point_functor(value)
        )
        assert result in TerminalObjects(comma)
        return result

    def factor(
        self,
        target: CategoryOfCategories.ElementType,
        source: CategoryOfCategories.ElementType,
        arrow: MorphismCategory.ObjectType,
    ) -> MorphismCategory.ObjectType:
        presentation = self.presentation(target)
        comma = comma_objects(
            self.forward, self.forward.codomain().point_functor(target)
        )
        candidate = comma.from_arrow(source, Cat().Terminal()(0), arrow)
        return presentation.unique_from(candidate).first()

    @cached_method
    def functor(self) -> Functor:
        return Fun(self.forward.codomain(), self.forward.domain())(
            lambda value: self.presentation(value).first(),
            lambda arrow: self.factor(
                arrow.codomain(),
                self.presentation(arrow.domain()).first(),
                arrow * self.presentation(arrow.domain()).arrow(),
            ),
        )

    @cached_method
    def adjunction(self) -> CategoryOfCategories.ElementType:
        from sage_categories.cat.adjunctions import Adjunctions

        forward, inverse = self.forward, self.functor()
        source, target = forward.domain(), forward.codomain()
        unit = Mor(Fun(source, source))(Fun(source, source).one(), inverse * forward)(
            lambda value: self.factor(
                forward.on_object(value),
                value,
                Mor(target)(forward.on_object(value), forward.on_object(value)).one(),
            )
        )
        counit = Mor(Fun(target, target))(forward * inverse, Fun(target, target).one())(
            lambda value: self.presentation(value).arrow()
        )
        return Adjunctions(forward, inverse)(unit, counit)


@dataclass(eq=False)
class LeftUniversalArrows:
    """A chosen initial object of ``(c ↓ G)`` for every ``c``."""

    inverse: Functor
    choose: Choice

    @cached_method(key=identity_key)
    def presentation(
        self, value: CategoryOfCategories.ElementType
    ) -> CategoryOfCategories.ElementType:
        result = self.choose(value)
        comma = comma_objects(
            self.inverse.codomain().point_functor(value), self.inverse
        )
        assert result in InitialObjects(comma)
        return result

    def factor(
        self,
        source: CategoryOfCategories.ElementType,
        target: CategoryOfCategories.ElementType,
        arrow: MorphismCategory.ObjectType,
    ) -> MorphismCategory.ObjectType:
        presentation = self.presentation(source)
        comma = comma_objects(
            self.inverse.codomain().point_functor(source), self.inverse
        )
        candidate = comma.from_arrow(Cat().Terminal()(0), target, arrow)
        return presentation.unique_to(candidate).second()

    @cached_method
    def functor(self) -> Functor:
        return Fun(self.inverse.codomain(), self.inverse.domain())(
            lambda value: self.presentation(value).second(),
            lambda arrow: self.factor(
                arrow.domain(),
                self.presentation(arrow.codomain()).second(),
                self.presentation(arrow.codomain()).arrow() * arrow,
            ),
        )

    @cached_method
    def adjunction(self) -> CategoryOfCategories.ElementType:
        from sage_categories.cat.adjunctions import Adjunctions

        forward, inverse = self.functor(), self.inverse
        source, target = forward.domain(), forward.codomain()
        unit = Mor(Fun(source, source))(Fun(source, source).one(), inverse * forward)(
            lambda value: self.presentation(value).arrow()
        )
        counit = Mor(Fun(target, target))(forward * inverse, Fun(target, target).one())(
            lambda value: self.factor(
                inverse.on_object(value),
                value,
                Mor(source)(inverse.on_object(value), inverse.on_object(value)).one(),
            )
        )
        return Adjunctions(forward, inverse)(unit, counit)


def right_mate(
    first: CategoryOfCategories.ElementType,
    second: CategoryOfCategories.ElementType,
    top: Functor,
    bottom: Functor,
    transformation: NaturalTransformation,
) -> NaturalTransformation:
    """For ``L ⊣ R``, ``L' ⊣ R'``, send ``L' H => K L`` to ``H R => R' K``.

    Reference: Mathlib CategoryTheory.Adjunction.Mates.mateEquiv.
    """
    assert transformation.domain() is second.forward() * top
    assert transformation.codomain() is bottom * first.forward()
    return (
        first.counit().whisker_left(second.inverse() * bottom)
        * transformation.whisker_right(first.inverse()).whisker_left(second.inverse())
        * second.unit().whisker_right(top * first.inverse())
    )


def left_mate(
    first: CategoryOfCategories.ElementType,
    second: CategoryOfCategories.ElementType,
    top: Functor,
    bottom: Functor,
    transformation: NaturalTransformation,
) -> NaturalTransformation:
    """Inverse mate correspondence ``H R => R' K`` to ``L' H => K L``."""
    assert transformation.domain() is top * first.inverse()
    assert transformation.codomain() is second.inverse() * bottom
    return (
        second.counit().whisker_right(bottom * first.forward())
        * transformation.whisker_right(first.forward()).whisker_left(second.forward())
        * first.unit().whisker_left(second.forward() * top)
    )
