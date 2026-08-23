"""Compile category-owned methods along selected structural functors."""

from __future__ import annotations

import inspect
from collections.abc import Callable, Mapping
from types import FunctionType, new_class
from typing import TYPE_CHECKING, TypeVar

from sage_categories.descriptors import ForwardedMethod
from sage_categories.values import Arrow, MathematicalElement, MathematicalObject

if TYPE_CHECKING:
    from sage_categories.abstract_categories.functors import StructuralFunctor
    from sage_categories.category import Category


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

type ImplementationType = type[MathematicalObject] | type[MathematicalElement]
type CompiledClassMember = ForwardedMethod | str

Implementation = TypeVar("Implementation", bound=MathematicalObject)


class DeclaredMethod:
    """A method and the category which declares it."""

    def __init__(
        self,
        owner: Category,
        method: FunctionType,
        route: tuple[StructuralFunctor, ...] = (),
    ) -> None:
        self.owner = owner
        self.method = method
        self.route = route


class CategoryCompiler:
    """Compile object and element method surfaces from a functor graph."""

    def __init__(self) -> None:
        self._object_types: dict[int, type[MathematicalObject]] = {}
        self._element_types: dict[int, type[MathematicalElement]] = {}
        self._arrow_types: dict[int, type[Arrow]] = {}
        self._object_catalogues: dict[int, dict[str, DeclaredMethod]] = {}
        self._element_catalogues: dict[int, dict[str, DeclaredMethod]] = {}
        self._arrow_catalogues: dict[int, dict[str, DeclaredMethod]] = {}
        self._routes: dict[tuple[int, int], tuple[StructuralFunctor, ...]] = {}

    def compiled_object_type(
        self,
        category: Category,
        local_type: type[MathematicalObject],
    ) -> type[MathematicalObject]:
        """Return the complete implementation type for objects of ``category``."""
        key = id(category)
        cached = self._object_types.get(key)
        if cached is not None:
            return cached
        compiled = self._compile_type(
            category,
            local_type,
            self.object_method_catalogue(category),
            element_methods=False,
            morphism_methods=False,
        )
        self._object_types[key] = compiled
        return compiled

    def compiled_element_type(
        self,
        category: Category,
        local_type: type[MathematicalElement],
    ) -> type[MathematicalElement]:
        """Return the complete implementation type for elements of ``category``."""
        key = id(category)
        cached = self._element_types.get(key)
        if cached is not None:
            return cached
        compiled = self._compile_type(
            category,
            local_type,
            self.element_method_catalogue(category),
            element_methods=True,
            morphism_methods=False,
        )
        self._element_types[key] = compiled
        return compiled

    def compiled_arrow_type(
        self,
        category: Category,
        local_type: type[Arrow],
    ) -> type[Arrow]:
        """Return the complete implementation type for arrows of ``category``."""
        key = id(category)
        cached = self._arrow_types.get(key)
        if cached is not None:
            return cached
        compiled = self._compile_type(
            category,
            local_type,
            self.arrow_method_catalogue(category),
            element_methods=False,
            morphism_methods=True,
        )
        self._arrow_types[key] = compiled
        return compiled

    def object_method_catalogue(
        self,
        category: Category,
    ) -> Mapping[str, DeclaredMethod]:
        """Return the object methods visible in ``category``."""
        key = id(category)
        cached = self._object_catalogues.get(key)
        if cached is not None:
            return cached
        catalogue = self._method_catalogue(
            category,
            category.local_object_type(),
            self.object_method_catalogue,
        )
        self._object_catalogues[key] = catalogue
        return catalogue

    def element_method_catalogue(
        self,
        category: Category,
    ) -> Mapping[str, DeclaredMethod]:
        """Return the element methods visible in ``category``."""
        key = id(category)
        cached = self._element_catalogues.get(key)
        if cached is not None:
            return cached
        catalogue = self._method_catalogue(
            category,
            category.local_element_type(),
            self.element_method_catalogue,
        )
        self._element_catalogues[key] = catalogue
        return catalogue

    def arrow_method_catalogue(
        self,
        category: Category,
    ) -> Mapping[str, DeclaredMethod]:
        """Return the arrow methods visible in ``category``."""
        key = id(category)
        cached = self._arrow_catalogues.get(key)
        if cached is not None:
            return cached
        catalogue = self._method_catalogue(
            category,
            category.local_arrow_type(),
            self.arrow_method_catalogue,
        )
        self._arrow_catalogues[key] = catalogue
        return catalogue

    def implementation_route(
        self,
        source: Category,
        target: Category,
    ) -> tuple[StructuralFunctor, ...]:
        """Return the unique structural-functor route from source to target."""
        if source is target:
            return ()
        key = id(source), id(target)
        cached = self._routes.get(key)
        if cached is not None:
            return cached
        routes = tuple(self._routes_from(source, target, (id(source),)))
        assert routes, f"no structural route from {source} to {target}"
        route = source._canonical_implementation_route(target, routes)
        assert route in routes
        self._routes[key] = route
        return route

    def _method_catalogue(
        self,
        category: Category,
        local_type: ImplementationType,
        inherited_catalogue: Callable[[Category], Mapping[str, DeclaredMethod]],
    ) -> dict[str, DeclaredMethod]:
        local = self._local_methods(local_type)
        catalogue: dict[str, DeclaredMethod] = {}
        for functor in category.super_functors():
            inherited = inherited_catalogue(functor.codomain())
            for name, declaration in inherited.items():
                previous = catalogue.get(name)
                if previous is None or previous.owner is declaration.owner:
                    if previous is not None:
                        assert previous.method is declaration.method
                    catalogue[name] = declaration
                    continue
                if previous.owner.is_subcategory(declaration.owner):
                    continue
                if declaration.owner.is_subcategory(previous.owner):
                    catalogue[name] = declaration
                    continue
                assert name in local, f"{category} inherits {name} from unrelated categories {previous.owner} and {declaration.owner}"
        for name, method in local.items():
            catalogue[name] = DeclaredMethod(category, method)
        return {
            name: DeclaredMethod(
                declaration.owner,
                declaration.method,
                self.implementation_route(category, declaration.owner),
            )
            for name, declaration in catalogue.items()
        }

    def _compile_type(
        self,
        category: Category,
        local_type: type[Implementation],
        catalogue: Mapping[str, DeclaredMethod],
        *,
        element_methods: bool,
        morphism_methods: bool,
    ) -> type[Implementation]:
        available = {name for name, declaration in catalogue.items() if inspect.getattr_static(local_type, name, None) is declaration.method}
        inherited = {
            name: ForwardedMethod(
                declaration.route,
                declaration.method,
                element_method=element_methods,
                morphism_method=morphism_methods,
            )
            for name, declaration in catalogue.items()
            if name not in available
        }
        if not inherited:
            return local_type

        def install(namespace: dict[str, CompiledClassMember]) -> None:
            namespace.update(inherited)
            namespace["__module__"] = local_type.__module__

        name = f"Complete{category.__class__.__name__}{local_type.__name__}"
        return new_class(name, (local_type,), exec_body=install)

    def _local_methods(
        self,
        local_type: ImplementationType,
    ) -> dict[str, FunctionType]:
        methods: dict[str, FunctionType] = {}
        kernel_types = {
            object,
            MathematicalObject,
            MathematicalElement,
            Arrow,
        }
        from sage_categories.category import Category

        kernel_types.add(Category)
        for implementation_type in reversed(local_type.__mro__):
            if implementation_type in kernel_types:
                continue
            methods.update(
                {
                    name: method
                    for name, method in vars(implementation_type).items()
                    if name not in _IGNORED_METHODS and (not name.startswith("_") or name.startswith("__")) and inspect.isfunction(method)
                }
            )
        return methods

    def _routes_from(
        self,
        source: Category,
        target: Category,
        visited: tuple[int, ...],
    ) -> list[tuple[StructuralFunctor, ...]]:
        routes: list[tuple[StructuralFunctor, ...]] = []
        for functor in source.super_functors():
            codomain = functor.codomain()
            assert id(codomain) not in visited, "the structural-functor graph has a cycle"
            if codomain is target:
                routes.append((functor,))
                continue
            for suffix in self._routes_from(
                codomain,
                target,
                (*visited, id(codomain)),
            ):
                routes.append((functor, *suffix))
        return routes


_CATEGORY_COMPILER = CategoryCompiler()


def category_compiler() -> CategoryCompiler:
    """Return the compiler for the current Python process."""
    return _CATEGORY_COMPILER
