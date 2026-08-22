"""Compile category-local declarations into complete implementation types."""

from __future__ import annotations

from collections.abc import Mapping
from types import FunctionType, new_class

from sage_categories.category import Category, ImplementationKind
from sage_categories.descriptors import ForwardedAttribute
from sage_categories.errors import IncoherentRouteError, MethodCollisionError
from sage_categories.functor import Functor
from sage_categories.values import (
    MathematicalElement,
    MathematicalMorphism,
    MathematicalObject,
)

_IGNORED_METHODS = frozenset(
    {
        "__class__",
        "__dict__",
        "__doc__",
        "__init__",
        "__module__",
        "__weakref__",
    }
)

type ClassNamespaceValue = ForwardedAttribute | str


class CategoryCompiler:
    """Compile method surfaces and structural implementation routes."""

    def __init__(self) -> None:
        self._object_types: dict[Category, type[MathematicalObject]] = {}
        self._element_types: dict[Category, type[MathematicalElement]] = {}
        self._arrow_types: dict[Category, type[MathematicalMorphism]] = {}
        self._catalogues: dict[
            tuple[Category, ImplementationKind], dict[str, Category]
        ] = {}
        self._routes: dict[
            tuple[Category, Category], tuple[Functor, ...]
        ] = {}

    def compiled_object_type(self, category: Category) -> type[MathematicalObject]:
        """Return the complete object implementation type."""
        cached = self._object_types.get(category)
        if cached is not None:
            return cached
        compiled = self._compile_type(category, ImplementationKind.OBJECT)
        if not issubclass(compiled, MathematicalObject):
            raise TypeError("compiled object type has the wrong base")
        self._object_types[category] = compiled
        return compiled

    def compiled_element_type(
        self, category: Category
    ) -> type[MathematicalElement]:
        """Return the complete element implementation type."""
        cached = self._element_types.get(category)
        if cached is not None:
            return cached
        compiled = self._compile_type(category, ImplementationKind.ELEMENT)
        if not issubclass(compiled, MathematicalElement):
            raise TypeError("compiled element type has the wrong base")
        self._element_types[category] = compiled
        return compiled

    def compiled_arrow_type(
        self, category: Category
    ) -> type[MathematicalMorphism]:
        """Return the complete arrow implementation type."""
        cached = self._arrow_types.get(category)
        if cached is not None:
            return cached
        compiled = self._compile_type(category, ImplementationKind.ARROW)
        if not issubclass(compiled, MathematicalMorphism):
            raise TypeError("compiled arrow type has the wrong base")
        self._arrow_types[category] = compiled
        return compiled

    def method_catalogue(
        self,
        category: Category,
        kind: ImplementationKind,
    ) -> Mapping[str, Category]:
        """Map exposed method names to their declaring categories."""
        key = (category, kind)
        cached = self._catalogues.get(key)
        if cached is not None:
            return cached

        local_names = self._local_method_names(category, kind)
        catalogue: dict[str, Category] = {}
        for functor in category.super_functors():
            inherited = self.method_catalogue(functor.codomain(), kind)
            for name, declaring_category in inherited.items():
                previous_owner = catalogue.get(name)
                if previous_owner is None or previous_owner == declaring_category:
                    catalogue[name] = declaring_category
                    continue
                if name not in local_names:
                    raise MethodCollisionError(
                        f"{category!r} inherits {name!r} from both "
                        f"{previous_owner!r} and {declaring_category!r}"
                    )
        catalogue.update(dict.fromkeys(local_names, category))
        self._catalogues[key] = catalogue
        return catalogue

    def implementation_route(
        self, source: Category, target: Category
    ) -> tuple[Functor, ...]:
        """Return the unique selected structural route to a target."""
        if source == target:
            return ()
        key = (source, target)
        cached = self._routes.get(key)
        if cached is not None:
            return cached

        routes = self._routes_from(source, target, (source,))
        if len(routes) > 1:
            raise IncoherentRouteError(
                f"{source!r} has {len(routes)} structural routes to {target!r}"
            )
        if not routes:
            return ()
        self._routes[key] = routes[0]
        return routes[0]

    def _compile_type(
        self,
        category: Category,
        kind: ImplementationKind,
    ) -> type[MathematicalObject] | type[MathematicalElement] | type[MathematicalMorphism]:
        local_type = category.local_type(kind)
        local_names = self._local_method_names(category, kind)
        catalogue = self.method_catalogue(category, kind)
        inherited = {
            name: ForwardedAttribute(owner, name)
            for name, owner in catalogue.items()
            if name not in local_names
        }

        def install(namespace: dict[str, ClassNamespaceValue]) -> None:
            namespace.update(inherited)
            namespace["__module__"] = local_type.__module__

        name = f"Complete{type(category).__name__}{kind.value}"
        return new_class(name, (local_type,), exec_body=install)

    def _local_method_names(
        self, category: Category, kind: ImplementationKind
    ) -> frozenset[str]:
        local_type = category.local_type(kind)
        return frozenset(
            name
            for name, member in vars(local_type).items()
            if name not in _IGNORED_METHODS
            and (not name.startswith("_") or name.startswith("__"))
            and isinstance(member, FunctionType)
        )

    def _routes_from(
        self,
        source: Category,
        target: Category,
        visited: tuple[Category, ...],
    ) -> list[tuple[Functor, ...]]:
        routes: list[tuple[Functor, ...]] = []
        for functor in source.super_functors():
            codomain = functor.codomain()
            if codomain in visited:
                raise IncoherentRouteError("the structural functor graph has a cycle")
            if codomain == target:
                routes.append((functor,))
                continue
            for suffix in self._routes_from(codomain, target, (*visited, codomain)):
                routes.append((functor, *suffix))
        return routes


_CATEGORY_COMPILER = CategoryCompiler()


def category_compiler() -> CategoryCompiler:
    """Return the process-wide category compiler."""
    return _CATEGORY_COMPILER
