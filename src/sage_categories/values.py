"""Public mathematical values and their cached functor images."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sage_categories.errors import MissingImplementationRouteError

if TYPE_CHECKING:
    from sage_categories.category import Category


class MathematicalObject:
    """An object with one cached implementation in each reachable category."""

    def __init__(self, *, category: Category) -> None:
        self._category = category
        self._implementations: dict[Category, MathematicalObject] = {category: self}

    def category(self) -> Category:
        """Return the object's mathematical category."""
        return self._category

    def implementation_in(self, target: Category) -> MathematicalObject:
        """Return the canonical image along the structural functor graph."""
        cached = self._implementations.get(target)
        if cached is not None:
            return cached

        value = self
        route = self._category.implementation_route_to(target)
        if not route:
            raise MissingImplementationRouteError(
                f"{self._category!r} has no implementation route to {target!r}"
            )

        for functor in route:
            codomain = functor.codomain()
            cached = self._implementations.get(codomain)
            if cached is not None:
                value = cached
                continue
            value = functor.on_object(value)
            if value.category() != codomain:
                raise TypeError(
                    f"{functor!r} returned an object in {value.category()!r}; "
                    f"expected {codomain!r}"
                )
            self._implementations[codomain] = value

        return value


class MathematicalElement:
    """An element with a mathematical parent object."""

    def __init__(self, *, parent: MathematicalObject) -> None:
        self._parent = parent

    def parent(self) -> MathematicalObject:
        """Return the element's parent object."""
        return self._parent


class MathematicalMorphism:
    """A morphism with explicit source and target objects."""

    def __init__(
        self,
        *,
        category: Category,
        domain: MathematicalObject,
        codomain: MathematicalObject,
    ) -> None:
        self._category = category
        self._domain = domain
        self._codomain = codomain
        self._implementations: dict[Category, MathematicalMorphism] = {
            category: self
        }

    def category(self) -> Category:
        """Return the category which owns this arrow implementation."""
        return self._category

    def domain(self) -> MathematicalObject:
        """Return the source object."""
        return self._domain

    def codomain(self) -> MathematicalObject:
        """Return the target object."""
        return self._codomain

    def implementation_in(self, target: Category) -> MathematicalMorphism:
        """Return the canonical morphism image in a reachable category."""
        cached = self._implementations.get(target)
        if cached is not None:
            return cached

        value = self
        route = self._category.implementation_route_to(target)
        if not route:
            raise MissingImplementationRouteError(
                f"{self._category!r} has no implementation route to {target!r}"
            )
        for functor in route:
            codomain = functor.codomain()
            cached = self._implementations.get(codomain)
            if cached is not None:
                value = cached
                continue
            value = functor.on_morphism(value)
            if value.category() != codomain:
                raise TypeError(
                    f"{functor!r} returned an arrow in {value.category()!r}; "
                    f"expected {codomain!r}"
                )
            self._implementations[codomain] = value
        return value

