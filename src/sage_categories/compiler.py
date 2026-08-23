"""Compile category-owned methods along selected structural functors."""

from __future__ import annotations

import inspect
from collections.abc import Callable, Mapping
from types import FunctionType, new_class
from typing import TYPE_CHECKING, TypeVar, assert_never

from sage_categories.descriptors import ForwardedMethod, ImplementationRole
from sage_categories.values import (
    Arrow,
    CategoryElement,
    MathematicalElement,
    MathematicalObject,
)

if TYPE_CHECKING:
    from sage_categories.abstract_categories.functors import StructuralFunctor
    from sage_categories.category import Category


# A category that declares no implementation for a role falls back to one of
# these. Such a fallback states nothing about the category graph, so it is not
# reported as a declared relation.
_KERNEL_IMPLEMENTATIONS = frozenset({MathematicalObject, MathematicalElement, CategoryElement, Arrow})


# Names the source class a generated one completes. A generated class exists
# only at runtime, so a reader of the report resolves it back to the class its
# module actually declares.
_COMPILED_FROM = "_compiled_from"


def _source_implementation(implementation: type) -> type:
    declared = vars(implementation).get(_COMPILED_FROM)
    return declared if isinstance(declared, type) else implementation


def _implementation_name(implementation: type) -> str:
    source = _source_implementation(implementation)
    return f"{source.__module__}.{source.__qualname__}"


def _local_type(category: Category, role: ImplementationRole) -> type:
    match role:
        case ImplementationRole.OBJECT:
            return category.local_object_type()
        case ImplementationRole.ELEMENT:
            return category.local_element_type()
        case ImplementationRole.ARROW:
            return category.local_arrow_type()
        case _:
            assert_never(role)


def _all_structural_functors(functor: StructuralFunctor) -> bool:
    return True


def _inclusion_functors(functor: StructuralFunctor) -> bool:
    return functor.is_inclusion()


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

_ARROW_PROTOCOL_METHODS = frozenset(
    {
        "__mul__",
        "base_category",
        "codomain",
        "domain",
        "forward",
        "hom_category",
        "source",
        "target",
    }
)

type ImplementationType = type[MathematicalObject | MathematicalElement]
# A compiled namespace holds forwarding descriptors, the module it belongs to,
# and the source class it completes.
type CompiledClassMember = ForwardedMethod | str | type

Implementation = TypeVar("Implementation", bound=MathematicalObject)


class DeclaredMethod:
    """One operation owner and its selected implementation."""

    def __init__(
        self,
        owner: Category,
        implementation_owner: Category,
        method: FunctionType,
        route: tuple[StructuralFunctor, ...] = (),
        implementation_route: tuple[StructuralFunctor, ...] = (),
    ) -> None:
        self.owner = owner
        self.implementation_owner = implementation_owner
        self.method = method
        self.route = route
        self.implementation_route = implementation_route


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
        self._compiled_categories: dict[int, Category] = {}

    def compiled_categories(self) -> tuple[Category, ...]:
        """Return every category whose implementation types this has compiled."""
        return tuple(self._compiled_categories.values())

    def declared_inheritance(self) -> dict[str, dict[str, tuple[str, ...]]]:
        """Report, per role, the implementation types each category inherits from.

        The compiled surface follows selected structural functors, so nothing
        states this relation in source and a static checker cannot infer it.
        POL-TYPE-024 makes reporting it the compiler's obligation: a checker
        plugin reads the declarations from their owner here rather than from a
        second graph kept somewhere else.
        """
        inherited = self._declared_relations(_all_structural_functors)
        subtyping = self.declared_subtyping()
        assert all(set(parents).issubset(inherited[role][implementation]) for role, relations in subtyping.items() for implementation, parents in relations.items())
        return inherited

    def declared_subtyping(self) -> dict[str, dict[str, tuple[str, ...]]]:
        """Report implementation subtyping declared by inclusion functors."""
        return self._declared_relations(_inclusion_functors)

    def _declared_relations(
        self,
        includes: Callable[[StructuralFunctor], bool],
    ) -> dict[str, dict[str, tuple[str, ...]]]:
        reported: dict[str, dict[str, tuple[str, ...]]] = {}
        for role in ImplementationRole:
            relations: dict[str, tuple[str, ...]] = {}
            for category in self.compiled_categories():
                local_type = _source_implementation(_local_type(category, role))
                if local_type in _KERNEL_IMPLEMENTATIONS:
                    continue
                reached: tuple[str, ...] = ()
                for functor in category.super_functors():
                    if not includes(functor):
                        continue
                    codomain = functor.codomain()
                    if codomain is category:
                        continue
                    inherited_type = _source_implementation(_local_type(codomain, role))
                    name = _implementation_name(inherited_type)
                    if inherited_type is local_type or name in reached:
                        continue
                    if inherited_type in _KERNEL_IMPLEMENTATIONS:
                        continue
                    reached = (*reached, name)
                if not reached:
                    continue
                # Two categories can share one local type, so the relations
                # already recorded for it stay and this adds what is new.
                declaring = _implementation_name(local_type)
                if declaring in relations:
                    recorded = relations[declaring]
                    reached = recorded + tuple(name for name in reached if name not in recorded)
                relations[declaring] = reached
            reported[role.value] = dict(sorted(relations.items()))
        return reported

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
            role=ImplementationRole.OBJECT,
        )
        self._object_types[key] = compiled
        self._compiled_categories[id(category)] = category
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
            role=ImplementationRole.ELEMENT,
        )
        self._element_types[key] = compiled
        self._compiled_categories[id(category)] = category
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
            role=ImplementationRole.ARROW,
        )
        self._arrow_types[key] = compiled
        self._compiled_categories[id(category)] = category
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
        route = self._canonical_route(source, target, routes)
        assert route in routes
        self._routes[key] = route
        return route

    def _canonical_route(
        self,
        source: Category,
        target: Category,
        routes: tuple[tuple[StructuralFunctor, ...], ...],
    ) -> tuple[StructuralFunctor, ...]:
        distinct = tuple(route for position, route in enumerate(routes) if route not in routes[:position])
        normalized = tuple(self._normalize_route(source, route) for route in distinct)
        canonical = normalized[0]
        assert all(route == canonical for route in normalized), f"structural routes from {source} to {target} are not declared coherent"
        assert canonical in distinct
        return canonical

    def _normalize_route(
        self,
        source: Category,
        route: tuple[StructuralFunctor, ...],
    ) -> tuple[StructuralFunctor, ...]:
        if not route:
            return ()
        first = route[0]
        assert first.domain() is source
        current = (
            first,
            *self._normalize_route(first.codomain(), route[1:]),
        )
        seen: set[tuple[int, ...]] = set()
        while True:
            key = tuple(id(functor) for functor in current)
            assert key not in seen, f"structural coherences of {source} contain a cycle"
            seen.add(key)
            replacement = self._coherent_replacement(source, current)
            if replacement is None:
                return current
            replacement_first = replacement[0]
            current = (
                replacement_first,
                *self._normalize_route(
                    replacement_first.codomain(),
                    replacement[1:],
                ),
            )

    def _coherent_replacement(
        self,
        source: Category,
        route: tuple[StructuralFunctor, ...],
    ) -> tuple[StructuralFunctor, ...] | None:
        # Bundled natural isomorphisms between parallel composites follow
        # Mathlib's ``CategoryTheory.NatIso`` construction:
        # https://github.com/leanprover-community/mathlib4/blob/master/Mathlib/CategoryTheory/Grothendieck.lean
        from sage_categories.abstract_categories.functors import (
            is_functor,
            is_structural_functor,
        )
        from sage_categories.abstract_categories.hom_categories import (
            is_isomorphism,
        )

        for coherence in source.structural_coherences():
            assert is_isomorphism(coherence)
            canonical_functor = coherence.domain()
            equivalent_functor = coherence.codomain()
            assert is_functor(canonical_functor)
            assert is_functor(equivalent_functor)
            assert canonical_functor.domain() is source
            assert equivalent_functor.domain() is source
            assert canonical_functor.codomain() is equivalent_functor.codomain()
            canonical: tuple[StructuralFunctor, ...] = ()
            for factor in canonical_functor.factors():
                assert is_structural_functor(factor)
                canonical = (*canonical, factor)
            equivalent: tuple[StructuralFunctor, ...] = ()
            for factor in equivalent_functor.factors():
                assert is_structural_functor(factor)
                equivalent = (*equivalent, factor)
            assert canonical
            assert equivalent
            if route[: len(equivalent)] == equivalent:
                return canonical + route[len(equivalent) :]
        return None

    def _method_catalogue(
        self,
        category: Category,
        local_type: ImplementationType,
        inherited_catalogue: Callable[[Category], Mapping[str, DeclaredMethod]],
    ) -> dict[str, DeclaredMethod]:
        local = self._local_methods(local_type)
        catalogue: dict[str, DeclaredMethod] = {}
        for functor in category.super_functors():
            inherited_methods = inherited_catalogue(functor.codomain())
            for name, declaration in inherited_methods.items():
                candidate = DeclaredMethod(
                    declaration.owner,
                    declaration.implementation_owner,
                    declaration.method,
                    (functor, *declaration.route),
                    (functor, *declaration.implementation_route),
                )
                previous = catalogue.get(name)
                if previous is None:
                    catalogue[name] = candidate
                    continue
                if previous.owner is candidate.owner:
                    canonical = self.implementation_route(category, previous.owner)
                    if candidate.route == canonical:
                        catalogue[name] = candidate
                        continue
                    assert previous.route == canonical
                    continue
                if previous.owner.is_subcategory(candidate.owner):
                    continue
                if candidate.owner.is_subcategory(previous.owner):
                    catalogue[name] = candidate
                    continue
                local_method = local.get(name)
                if local_method is not None:
                    catalogue[name] = DeclaredMethod(
                        category,
                        category,
                        local_method,
                    )
                    continue
                coherent = self._coherent_declaration(
                    category,
                    previous,
                    candidate,
                )
                assert coherent is not None, f"{category} inherits {name} from unrelated categories {previous.owner} and {declaration.owner}"
                catalogue[name] = coherent
        for name, method in local.items():
            inherited_declaration = catalogue.get(name)
            if inherited_declaration is not None and method is inherited_declaration.method:
                continue
            if inherited_declaration is None or inherited_declaration.owner is category:
                catalogue[name] = DeclaredMethod(
                    category,
                    category,
                    method,
                )
                continue
            catalogue[name] = DeclaredMethod(
                inherited_declaration.owner,
                category,
                method,
                self.implementation_route(
                    category,
                    inherited_declaration.owner,
                ),
            )
        return catalogue

    def _coherent_declaration(
        self,
        category: Category,
        first: DeclaredMethod,
        second: DeclaredMethod,
    ) -> DeclaredMethod | None:
        # A natural isomorphism is oriented from its chosen representative to
        # an equivalent composite, as in Mathlib's ``NatIso`` constructions:
        # https://github.com/leanprover-community/mathlib4/blob/master/Mathlib/CategoryTheory/Grothendieck.lean
        from sage_categories.abstract_categories.functors import (
            is_functor,
            is_structural_functor,
        )
        from sage_categories.abstract_categories.hom_categories import (
            is_isomorphism,
        )

        preferred: DeclaredMethod | None = None
        for coherence in category.structural_coherences():
            assert is_isomorphism(coherence)
            canonical_functor = coherence.domain()
            equivalent_functor = coherence.codomain()
            assert is_functor(canonical_functor)
            assert is_functor(equivalent_functor)
            canonical: tuple[StructuralFunctor, ...] = ()
            for factor in canonical_functor.factors():
                assert is_structural_functor(factor)
                canonical = (*canonical, factor)
            equivalent: tuple[StructuralFunctor, ...] = ()
            for factor in equivalent_functor.factors():
                assert is_structural_functor(factor)
                equivalent = (*equivalent, factor)
            divergence = next(
                (position for position, pair in enumerate(zip(canonical, equivalent, strict=False)) if pair[0] is not pair[1]),
                None,
            )
            assert divergence is not None

            def follows(
                declaration: DeclaredMethod,
                route: tuple[StructuralFunctor, ...],
                divergence_position: int = divergence,
            ) -> bool:
                return len(declaration.route) > divergence_position and declaration.route[: divergence_position + 1] == route[: divergence_position + 1]

            if follows(first, canonical) and follows(second, equivalent):
                candidate = first
            elif follows(second, canonical) and follows(first, equivalent):
                candidate = second
            else:
                continue
            if preferred is not None:
                assert candidate is preferred
            preferred = candidate
        return preferred

    def _compile_type(
        self,
        category: Category,
        local_type: type[Implementation],
        catalogue: Mapping[str, DeclaredMethod],
        *,
        role: ImplementationRole,
    ) -> type[Implementation]:
        available = {name for name, declaration in catalogue.items() if inspect.getattr_static(local_type, name, None) is declaration.method}
        match role:
            case ImplementationRole.OBJECT | ImplementationRole.ELEMENT:
                pass
            case ImplementationRole.ARROW:
                available.update(_ARROW_PROTOCOL_METHODS & catalogue.keys())
            case _:
                assert_never(role)
        inherited = {
            name: ForwardedMethod(
                declaration.implementation_route,
                declaration.method,
                role=role,
            )
            for name, declaration in catalogue.items()
            if name not in available
        }
        if not inherited:
            return local_type

        def install(namespace: dict[str, CompiledClassMember]) -> None:
            namespace.update(inherited)
            namespace["__module__"] = local_type.__module__
            namespace[_COMPILED_FROM] = local_type

        name = f"Complete{type(category).__name__}{local_type.__name__}"
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
