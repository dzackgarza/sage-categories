"""Compile category-owned methods along selected ordinary functors."""

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
    ForwardedMethod,
    ForwardedObjectMethod,
    ImplementationRole,
    MethodSignature,
    ParameterRole,
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
    from sage_categories.abstract_categories.functors import Functor
    from sage_categories.abstract_categories.hom_categories import HomCategory
    from sage_categories.category import Category


_KERNEL_IMPLEMENTATIONS = frozenset(
    {MathematicalObject, MathematicalElement, CategoryElement, Arrow}
)


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


def _all_functors(functor: Functor) -> bool:
    return True


def _inclusion_functors(functor: Functor) -> bool:
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
        "structure_functors",
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
        route: tuple[Functor, ...] = (),
        implementation_route: tuple[Functor, ...] = (),
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
    """Compile inherited methods from each category's selected functors."""

    def __init__(self) -> None:
        self._object_types: dict[int, type[MathematicalObject]] = {}
        self._element_types: dict[int, type[MathematicalElement]] = {}
        self._arrow_types: dict[int, type[Arrow]] = {}
        self._object_catalogues: dict[int, dict[str, DeclaredMethod]] = {}
        self._element_catalogues: dict[int, dict[str, DeclaredMethod]] = {}
        self._arrow_catalogues: dict[int, dict[str, DeclaredMethod]] = {}
        self._structure_functors: dict[int, tuple[Functor, ...]] = {}
        self._selected_functor_ids: set[int] = set()
        self._selecting_categories: set[int] = set()
        self._routes: dict[tuple[int, int], tuple[Functor, ...]] = {}
        self._compiled_categories: dict[int, Category] = {}

    def structure_functors(self, category: Category) -> tuple[Functor, ...]:
        """Return the canonical selected functors declared by ``category``."""
        key = id(category)
        cached = self._structure_functors.get(key)
        if cached is not None:
            return cached
        assert key not in self._selecting_categories, (
            f"constructing the selected functors of {category} is recursive"
        )
        self._selecting_categories.add(key)
        try:
            declared = category.structure_functors()
            assert isinstance(declared, tuple), (
                f"{category}.structure_functors() must return a tuple"
            )
            from sage_categories.abstract_categories.functors import is_functor

            selected: list[Functor] = []
            for functor in declared:
                assert is_functor(functor), (
                    f"{category} selected a value which is not an owned functor: "
                    f"{functor!r}"
                )
                assert functor.domain() is category, (
                    f"selected functor {functor} has domain {functor.domain()}, "
                    f"not its declaring category {category}"
                )
                assert all(functor is not previous for previous in selected), (
                    f"{category} selected the same functor twice"
                )
                selected.append(functor)
            result = tuple(selected)
            self._structure_functors[key] = result
            self._selected_functor_ids.update(id(functor) for functor in result)
            return result
        finally:
            self._selecting_categories.remove(key)

    def is_selected_functor(self, functor: Functor) -> bool:
        """Return whether the source category selected this exact functor."""
        if id(functor) in self._selected_functor_ids:
            return True
        return any(
            selected is functor
            for selected in self.structure_functors(functor.domain())
        )

    def _refined_type(
        self,
        implementation: type[Implementation],
        property_implementation: type[Implementation],
    ) -> type[Implementation]:
        """Compatibility refinement until property roles are fully migrated."""
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
        """Compatibility refinement for the existing property-category leaves."""
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
        """Compatibility refinement for the existing property-category leaves."""
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
        """Compatibility refinement for the existing property-category leaves."""
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
        """Report implementation inheritance induced by selected functors."""
        inherited = self._declared_relations(_all_functors)
        subtyping = self.declared_subtyping()
        assert all(
            set(parents).issubset(inherited[role][implementation])
            for role, relations in subtyping.items()
            for implementation, parents in relations.items()
        )
        return inherited

    def declared_subtyping(self) -> dict[str, dict[str, tuple[str, ...]]]:
        """Report implementation subtyping induced by inclusions."""
        return self._declared_relations(_inclusion_functors)

    def _declared_relations(
        self,
        includes: Callable[[Functor], bool],
    ) -> dict[str, dict[str, tuple[str, ...]]]:
        reported: dict[str, dict[str, tuple[str, ...]]] = {}
        for role in ImplementationRole:
            relations: dict[str, tuple[str, ...]] = {}
            for category in self.compiled_categories():
                local_type = _local_type(category, role)
                if local_type in _KERNEL_IMPLEMENTATIONS:
                    continue
                reached: tuple[str, ...] = ()
                for functor in self.structure_functors(category):
                    if not includes(functor):
                        continue
                    codomain = functor.codomain()
                    if codomain is category:
                        continue
                    inherited_type = _local_type(codomain, role)
                    name = _implementation_name(inherited_type)
                    if (
                        inherited_type is local_type
                        or name in reached
                        or inherited_type in _KERNEL_IMPLEMENTATIONS
                    ):
                        continue
                    reached = (*reached, name)
                if not reached:
                    continue
                declaring = _implementation_name(local_type)
                if declaring in relations:
                    recorded = relations[declaring]
                    reached = recorded + tuple(
                        name for name in reached if name not in recorded
                    )
                relations[declaring] = reached
            reported[role.value] = dict(sorted(relations.items()))
        return reported

    def compiled_object_type(
        self,
        category: Category,
        local_type: type[MathematicalObject],
    ) -> type[MathematicalObject]:
        """Return the complete object implementation for ``category``."""
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
        self._compiled_categories[key] = category
        return compiled

    def compiled_element_type(
        self,
        category: Category,
        local_type: type[MathematicalElement],
    ) -> type[MathematicalElement]:
        """Return the complete element implementation for ``category``."""
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
        self._compiled_categories[key] = category
        return compiled

    def compiled_arrow_type(
        self,
        category: Category,
        local_type: type[Arrow],
    ) -> type[Arrow]:
        """Return the complete arrow implementation for ``category``."""
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
        self._compiled_categories[key] = category
        return compiled

    def object_method_catalogue(
        self,
        category: Category,
    ) -> Mapping[str, DeclaredMethod]:
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
    ) -> tuple[Functor, ...]:
        """Return the canonical selected-functor route to ``target``."""
        if source is target:
            return ()
        key = id(source), id(target)
        cached = self._routes.get(key)
        if cached is not None:
            return cached
        routes = tuple(self._routes_from(source, target, (id(source),)))
        assert routes, f"no selected functor route from {source} to {target}"
        route = self._canonical_route(source, target, routes)
        self._routes[key] = route
        return route

    def _canonical_route(
        self,
        source: Category,
        target: Category,
        routes: tuple[tuple[Functor, ...], ...],
    ) -> tuple[Functor, ...]:
        distinct = tuple(
            route
            for position, route in enumerate(routes)
            if route not in routes[:position]
        )
        if len(distinct) == 1:
            return distinct[0]
        # Inclusions are strict in this kernel: every edge returns the exact
        # canonical ambient implementation. Hence an all-inclusion diamond has
        # one literal image and declaration order can choose its route.
        if all(functor.is_inclusion() for route in distinct for functor in route):
            return distinct[0]
        raise AssertionError(
            f"selected routes from {source} to {target} are not strictly coherent; "
            "a natural isomorphism is not literal equality"
        )

    def _method_catalogue(
        self,
        category: Category,
        local_type: ImplementationType,
        inherited_catalogue: Callable[[Category], Mapping[str, DeclaredMethod]],
        role: ImplementationRole,
    ) -> dict[str, DeclaredMethod]:
        local = self._local_methods(local_type)
        catalogue: dict[str, DeclaredMethod] = {}
        for functor in self.structure_functors(category):
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
        raise AssertionError(
            f"{category} inherits {name} from unrelated mathematical owners "
            f"{previous.owner} and {candidate.owner}"
        )

    def _preferred_implementation_route(
        self,
        category: Category,
        previous: DeclaredMethod,
        candidate: DeclaredMethod,
    ) -> DeclaredMethod:
        if previous.implementation_owner.is_subcategory(
            candidate.implementation_owner
        ):
            return previous
        if candidate.implementation_owner.is_subcategory(
            previous.implementation_owner
        ):
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

    def _validate_transport(
        self,
        declaration: DeclaredMethod,
        name: str,
    ) -> None:
        route = declaration.implementation_route
        if not route:
            return
        signature = declaration.signature
        roles = (
            signature.receiver,
            *signature.positional,
            *(role for _, role in signature.keyword),
            *((signature.variadic,) if signature.variadic is not None else ()),
            *((signature.keywords,) if signature.keywords is not None else ()),
            signature.result,
        )
        element_roles = {
            ParameterRole.ELEMENT,
            ParameterRole.ELEMENT_ITERATOR,
        }
        if any(role in element_roles for role in roles):
            assert all(functor.maps_elements() for functor in route), (
                f"cannot inherit {name}: selected route "
                f"{tuple(map(str, route))} lacks an element map"
            )

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
        for name, declaration in catalogue.items():
            if name not in available:
                self._validate_transport(declaration, name)
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
            declaration = catalogue[name]
            if isinstance(installed, ForwardedMethod):
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
                    if name not in _IGNORED_METHODS
                    and (not name.startswith("_") or name.startswith("__"))
                    and inspect.isfunction(method)
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
    ) -> list[tuple[Functor, ...]]:
        routes: list[tuple[Functor, ...]] = []
        for functor in self.structure_functors(source):
            codomain = functor.codomain()
            assert id(codomain) not in visited, (
                "the selected-functor graph has a cycle"
            )
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
