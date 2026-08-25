"""Compile category-owned methods along selected structural functors."""

from __future__ import annotations

import inspect
from collections.abc import Callable, Mapping
from types import FunctionType
from typing import TYPE_CHECKING, TypeVar, assert_never

from sage.structure.dynamic_class import dynamic_class

from sage_categories.descriptors import (
    ForwardedArrowMethod,
    ForwardedDescriptor,
    ForwardedElementMethod,
    ForwardedObjectMethod,
    ImplementationRole,
    MethodSignature,
    RefiningPropertyMethod,
    method_signature,
)
from sage_categories.values import (
    Arrow,
    CategoryElement,
    Decision,
    MathematicalElement,
    MathematicalObject,
)

if TYPE_CHECKING:
    from sage_categories.abstract_categories.full_subcategories import FullSubcategory
    from sage_categories.abstract_categories.functors import StructuralFunctor
    from sage_categories.abstract_categories.hom_categories import HomCategory
    from sage_categories.category import Category


# A category that declares no implementation for a role falls back to one of
# these. Such a fallback states nothing about the category graph, so it is not
# reported as a declared relation.
_KERNEL_IMPLEMENTATIONS = frozenset({MathematicalObject, MathematicalElement, CategoryElement, Arrow})


def _implementation_name(implementation: type) -> str:
    return f"{implementation.__module__}.{implementation.__qualname__}"


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
        "structural_coherences",
        "super_functors",
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
Implementation = TypeVar("Implementation", bound=MathematicalObject)


class DeclaredMethod:
    """One operation owner and its selected implementation."""

    def __init__(
        self,
        owner: Category,
        implementation_owner: Category,
        method: FunctionType,
        role: ImplementationRole,
        route: tuple[StructuralFunctor, ...] = (),
        implementation_route: tuple[StructuralFunctor, ...] = (),
    ) -> None:
        self.owner = owner
        self.implementation_owner = implementation_owner
        self.method = method
        self.role = role
        self._signature: MethodSignature | None = None
        self.route = route
        self.implementation_route = implementation_route

    @property
    def signature(self) -> MethodSignature:
        if self._signature is None:
            self._signature = method_signature(self.method, self.role)
        return self._signature


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

    def _refined_type(
        self,
        implementation: type[Implementation],
        property_implementation: type[Implementation],
    ) -> type[Implementation]:
        if issubclass(implementation, property_implementation):
            return implementation
        if issubclass(property_implementation, implementation):
            return property_implementation
        name = f"{implementation.__name__}_with_{property_implementation.__name__}"
        return dynamic_class(
            name,
            (property_implementation, implementation),
            reduction=None,
        )

    def _property_refinement_category(
        self,
        current: Category,
        property_category: FullSubcategory,
    ) -> Category:
        if current.is_subcategory(property_category):
            return current
        if property_category.is_subcategory(current):
            return property_category
        lower_bounds = tuple(
            category
            for category in self._compiled_categories.values()
            if category.is_subcategory(current)
            and category.is_subcategory(property_category)
        )
        joins = tuple(
            category
            for category in lower_bounds
            if not any(
                category is not other
                and category.is_subcategory(other)
                and not other.is_subcategory(category)
                for other in lower_bounds
            )
        )
        assert len(joins) == 1, (
            f"the category graph declares no unique property join of "
            f"{current} and {property_category}"
        )
        return joins[0]

    def refine_object(
        self,
        category: FullSubcategory,
        ambient: MathematicalObject,
    ) -> MathematicalObject:
        """Refine ``ambient`` into ``category`` without changing its identity."""
        current = ambient.category()
        if current is category or current.is_subcategory(category):
            return ambient
        assert category.is_subcategory(current) or current.is_subcategory(
            category.ambient_category()
        )
        refined_category = self._property_refinement_category(current, category)
        ambient.__class__ = self._refined_type(
            type(ambient),
            refined_category.ObjectType,
        )
        ambient._category = refined_category
        ambient._object_structural_images[
            (id(ambient), id(ambient), id(refined_category))
        ] = ambient
        return ambient

    def refine_element(
        self,
        category: FullSubcategory,
        source: MathematicalObject,
        ambient: MathematicalElement,
    ) -> MathematicalElement:
        """Refine ``ambient`` into ``category`` without changing its identity."""
        assert ambient.ambient_object() is source
        refined_category = source.category()
        assert refined_category.is_subcategory(category)
        ambient.__class__ = self._refined_type(
            type(ambient),
            refined_category.ElementType,
        )
        ambient._category = refined_category
        return ambient

    def refine_arrow(
        self,
        category: FullSubcategory,
        hom_category: HomCategory,
        ambient: Arrow,
    ) -> Arrow:
        """Refine ``ambient`` into ``category`` without changing its identity."""
        assert ambient.domain() is hom_category.domain()
        assert ambient.codomain() is hom_category.codomain()
        ambient.__class__ = self._refined_type(type(ambient), category.ArrowType)
        ambient._hom_category = hom_category
        ambient._category = category.ArrowCategory()
        return ambient

    def compiled_categories(self) -> tuple[Category, ...]:
        """Return every category whose implementation types this has compiled."""
        return tuple(self._compiled_categories.values())

    def register_object_property(
        self,
        ambient_category: Category,
        property_category: FullSubcategory,
        predicate: Callable[[MathematicalObject], Decision],
    ) -> None:
        """Connect an ambient predicate to its property self-refinement."""
        implementation = ambient_category.local_object_type()
        name = predicate.__name__
        installed = inspect.getattr_static(implementation, name, None)
        if isinstance(installed, RefiningPropertyMethod):
            installed.register(ambient_category, property_category, predicate)
            return
        assert installed is predicate or isinstance(installed, ForwardedObjectMethod)
        type.__setattr__(
            implementation,
            name,
            RefiningPropertyMethod(
                ambient_category,
                property_category,
                predicate,
            ),
        )

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
                local_type = _local_type(category, role)
                if local_type in _KERNEL_IMPLEMENTATIONS:
                    continue
                reached: tuple[str, ...] = ()
                for functor in category.super_functors():
                    if not includes(functor):
                        continue
                    codomain = functor.codomain()
                    if codomain is category:
                        continue
                    inherited_type = _local_type(codomain, role)
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
            ImplementationRole.OBJECT,
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
            ImplementationRole.ELEMENT,
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
            ImplementationRole.ARROW,
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
        if not all(route == canonical for route in normalized):
            assert all(
                functor.is_inclusion()
                for route in normalized
                for functor in route
            ), f"structural routes from {source} to {target} are not declared coherent"
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
        role: ImplementationRole,
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
                    role,
                    (functor, *declaration.route),
                    (functor, *declaration.implementation_route),
                )
                previous = catalogue.get(name)
                if previous is None:
                    catalogue[name] = candidate
                    continue
                catalogue[name] = self._merge_inherited_declarations(
                    category,
                    name,
                    previous,
                    candidate,
                    local.get(name),
                    role,
                )
        for name, method in local.items():
            catalogue[name] = self._local_declaration(
                category,
                method,
                catalogue.get(name),
                role,
            )
        return catalogue

    def _merge_inherited_declarations(
        self,
        category: Category,
        name: str,
        previous: DeclaredMethod,
        candidate: DeclaredMethod,
        local_method: FunctionType | None,
        role: ImplementationRole,
    ) -> DeclaredMethod:
        if previous.owner is candidate.owner:
            return self._preferred_implementation_route(category, previous, candidate)
        if previous.owner.is_subcategory(candidate.owner):
            return previous
        if candidate.owner.is_subcategory(previous.owner):
            return candidate
        if local_method is not None:
            return DeclaredMethod(category, category, local_method, role)
        coherent = self._coherent_declaration(category, previous, candidate)
        assert coherent is not None, f"{category} inherits {name} from unrelated categories {previous.owner} and {candidate.owner}"
        return coherent

    def _preferred_implementation_route(
        self,
        category: Category,
        previous: DeclaredMethod,
        candidate: DeclaredMethod,
    ) -> DeclaredMethod:
        if previous.implementation_owner.is_subcategory(candidate.implementation_owner):
            return previous
        if candidate.implementation_owner.is_subcategory(previous.implementation_owner):
            return candidate
        canonical = self.implementation_route(category, previous.owner)
        if candidate.route == canonical:
            return candidate
        assert previous.route == canonical
        return previous

    def _local_declaration(
        self,
        category: Category,
        method: FunctionType,
        inherited: DeclaredMethod | None,
        role: ImplementationRole,
    ) -> DeclaredMethod:
        if inherited is not None and method is inherited.method:
            return inherited
        if inherited is None or inherited.owner is category:
            return DeclaredMethod(category, category, method, role)
        return DeclaredMethod(
            inherited.owner,
            category,
            method,
            role,
            self.implementation_route(category, inherited.owner),
        )

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

        first_inclusions = sum(functor.is_inclusion() for functor in first.route)
        second_inclusions = sum(functor.is_inclusion() for functor in second.route)
        if first_inclusions > second_inclusions:
            return first
        if second_inclusions > first_inclusions:
            return second

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
        available = {
            name
            for name, declaration in catalogue.items()
            if inspect.getattr_static(local_type, name, None) is declaration.method
        }
        inherited: dict[str, ForwardedDescriptor]
        match role:
            case ImplementationRole.OBJECT:
                inherited = {
                    name: ForwardedObjectMethod(
                        category,
                        declaration.implementation_route,
                        declaration.method,
                        declaration.signature,
                    )
                    for name, declaration in catalogue.items()
                    if name not in available
                }
            case ImplementationRole.ELEMENT:
                inherited = {
                    name: ForwardedElementMethod(
                        category,
                        declaration.implementation_route,
                        declaration.method,
                        declaration.signature,
                    )
                    for name, declaration in catalogue.items()
                    if name not in available
                }
            case ImplementationRole.ARROW:
                available.update(_ARROW_PROTOCOL_METHODS & catalogue.keys())
                inherited = {
                    name: ForwardedArrowMethod(
                        category,
                        declaration.implementation_route,
                        declaration.method,
                        declaration.signature,
                    )
                    for name, declaration in catalogue.items()
                    if name not in available
                }
            case _:
                assert_never(role)
        for name, descriptor in inherited.items():
            installed = vars(local_type).get(name)
            if isinstance(installed, ForwardedObjectMethod):
                assert isinstance(descriptor, ForwardedObjectMethod)
                declaration = catalogue[name]
                installed.register(
                    category,
                    declaration.implementation_route,
                    declaration.method,
                    declaration.signature,
                )
                continue
            if isinstance(installed, ForwardedElementMethod):
                assert isinstance(descriptor, ForwardedElementMethod)
                declaration = catalogue[name]
                installed.register(
                    category,
                    declaration.implementation_route,
                    declaration.method,
                    declaration.signature,
                )
                continue
            if isinstance(installed, ForwardedArrowMethod):
                assert isinstance(descriptor, ForwardedArrowMethod)
                declaration = catalogue[name]
                installed.register(
                    category,
                    declaration.implementation_route,
                    declaration.method,
                    declaration.signature,
                )
                continue
            assert installed is None
            type.__setattr__(local_type, name, descriptor)
        return local_type

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
            methods.update(
                {
                    name: descriptor.declaration()
                    for name, descriptor in vars(implementation_type).items()
                    if isinstance(descriptor, RefiningPropertyMethod)
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
