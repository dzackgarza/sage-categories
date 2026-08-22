"""First-class functors between implementation-owning categories."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, overload

from sage_categories.values import (
    MathematicalElement,
    MathematicalMorphism,
    MathematicalObject,
)

if TYPE_CHECKING:
    from sage_categories.category import Category


class Functor(ABC):
    """Construct object and arrow implementations in a codomain category."""

    def __init__(self, domain: Category, codomain: Category) -> None:
        self._domain = domain
        self._codomain = codomain

    def domain(self) -> Category:
        """Return the domain category."""
        return self._domain

    def codomain(self) -> Category:
        """Return the codomain category."""
        return self._codomain

    @abstractmethod
    def on_object(self, source: MathematicalObject) -> MathematicalObject:
        """Construct the codomain implementation of an object."""

    @abstractmethod
    def on_morphism(self, morphism: MathematicalMorphism) -> MathematicalMorphism:
        """Construct the codomain implementation of a morphism."""

    @overload
    def __call__(self, value: MathematicalObject) -> MathematicalObject: ...

    @overload
    def __call__(self, value: MathematicalMorphism) -> MathematicalMorphism: ...

    def __call__(self, value: MathematicalObject | MathematicalMorphism) -> MathematicalObject | MathematicalMorphism:
        """Apply the functor to an object or morphism."""
        if isinstance(value, MathematicalMorphism):
            morphism_image = self.on_morphism(value)
            if morphism_image.category() != self._codomain:
                raise TypeError(f"functor image belongs to {morphism_image.category()!r}, not {self._codomain!r}")
            return morphism_image

        object_image = self.on_object(value)
        if object_image.category() != self._codomain:
            raise TypeError(f"functor image belongs to {object_image.category()!r}, not {self._codomain!r}")
        return object_image

    def then(self, following: Functor) -> ComposedFunctor:
        """Compose this functor with a functor from its codomain."""
        return ComposedFunctor(self, following)


class ConcreteFunctor(Functor):
    """A functor which also maps separately represented elements."""

    @abstractmethod
    def on_element(
        self,
        source: MathematicalObject,
        element: MathematicalElement,
    ) -> MathematicalElement:
        """Construct the element image in the codomain object."""


class IdentityFunctor(ConcreteFunctor):
    """The identity functor of a category."""

    def __init__(self, category: Category) -> None:
        super().__init__(category, category)

    def on_object(self, source: MathematicalObject) -> MathematicalObject:
        return source

    def on_morphism(self, morphism: MathematicalMorphism) -> MathematicalMorphism:
        return morphism

    def on_element(
        self,
        source: MathematicalObject,
        element: MathematicalElement,
    ) -> MathematicalElement:
        return element


class ComposedFunctor(Functor):
    """The composite of two composable functors."""

    def __init__(self, first: Functor, second: Functor) -> None:
        if first.codomain() != second.domain():
            raise ValueError("functor domain and codomain do not compose")
        self._first = first
        self._second = second
        super().__init__(first.domain(), second.codomain())

    def on_object(self, source: MathematicalObject) -> MathematicalObject:
        return self._second.on_object(self._first.on_object(source))

    def on_morphism(self, morphism: MathematicalMorphism) -> MathematicalMorphism:
        return self._second.on_morphism(self._first.on_morphism(morphism))


@dataclass(frozen=True)
class NaturalTransformation:
    """A natural transformation with an explicit object component."""

    source: Functor
    target: Functor
    component: Callable[[MathematicalObject], MathematicalMorphism]

    def __post_init__(self) -> None:
        if self.source.domain() != self.target.domain():
            raise ValueError("natural transformation domains differ")
        if self.source.codomain() != self.target.codomain():
            raise ValueError("natural transformation codomains differ")

    def at(self, value: MathematicalObject) -> MathematicalMorphism:
        """Return the component at an object."""
        return self.component(value)
