"""Categories which own local implementations and constructors."""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from sage_categories.values import (
    MathematicalElement,
    MathematicalMorphism,
    MathematicalObject,
)

if TYPE_CHECKING:
    from sage_categories.functor import Functor


class ImplementationKind(Enum):
    """One of the three implementation surfaces owned by a category."""

    OBJECT = "ObjectType"
    ELEMENT = "ElementType"
    ARROW = "ArrowType"


class Category:
    """A mathematical category with locally declared implementation types."""

    _local_object_type: type[MathematicalObject] = MathematicalObject
    _local_element_type: type[MathematicalElement] = MathematicalElement
    _local_arrow_type: type[MathematicalMorphism] = MathematicalMorphism

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        declarations = (
            ("ObjectType", "_local_object_type", MathematicalObject),
            ("ElementType", "_local_element_type", MathematicalElement),
            ("ArrowType", "_local_arrow_type", MathematicalMorphism),
        )
        for public_name, storage_name, base_type in declarations:
            declared_type = cls.__dict__.get(public_name)
            if declared_type is None:
                continue
            if not isinstance(declared_type, type) or not issubclass(
                declared_type, base_type
            ):
                raise TypeError(f"{cls.__name__}.{public_name} has the wrong base")
            setattr(cls, storage_name, declared_type)
            delattr(cls, public_name)

    @property
    def ObjectType(self) -> type[MathematicalObject]:
        """Return the complete object implementation type."""
        from sage_categories.compiler import category_compiler

        return category_compiler().compiled_object_type(self)

    @property
    def ElementType(self) -> type[MathematicalElement]:
        """Return the complete element implementation type."""
        from sage_categories.compiler import category_compiler

        return category_compiler().compiled_element_type(self)

    @property
    def ArrowType(self) -> type[MathematicalMorphism]:
        """Return the complete arrow implementation type."""
        from sage_categories.compiler import category_compiler

        return category_compiler().compiled_arrow_type(self)

    def local_type(
        self, kind: ImplementationKind
    ) -> type[MathematicalObject] | type[MathematicalElement] | type[MathematicalMorphism]:
        """Return the implementation type declared directly by this category."""
        if kind is ImplementationKind.OBJECT:
            return self._local_object_type
        if kind is ImplementationKind.ELEMENT:
            return self._local_element_type
        return self._local_arrow_type

    def super_functors(self) -> tuple[Functor, ...]:
        """Return the functors used for implicit implementation inheritance."""
        return ()

    def super_categories(self) -> tuple[Category, ...]:
        """Return the compatibility view derived from structural functors."""
        return tuple(functor.codomain() for functor in self.super_functors())

    def implementation_route_to(self, target: Category) -> tuple[Functor, ...]:
        """Return the unique structural functor route to a category."""
        from sage_categories.compiler import category_compiler

        return category_compiler().implementation_route(self, target)

    def declared_methods(self) -> dict[str, Category]:
        """Return each complete object method and its declaring category."""
        from sage_categories.compiler import category_compiler

        return dict(category_compiler().method_catalogue(self, ImplementationKind.OBJECT))

