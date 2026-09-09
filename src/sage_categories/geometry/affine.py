"""OSCAR-backed affine schemes and the contravariant ``Spec`` functor."""

from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from typing import Any, cast

from sage_categories.algebra._commutative_rings_oscar import (
    oscar_native_morphism,
    oscar_native_object,
)
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.declarations import Sets
from sage_categories.cat.functors import Fun, Functor
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.native import (
    NativeMorphismRealization,
    NativeMorphismRealizations,
    NativeObjectRealization,
    NativeObjectRealizations,
)
from sage_categories.cat.opposites import opposite_morphism
from sage_categories.engines import oscar
from sage_categories.kernel.retention import identity_key
from sage_categories.kernel.sage_runtime import cached_function

__all__ = [
    "AffineSchemes",
    "AffineSchemesCategory",
    "Spec",
    "native_affine_morphism",
    "native_affine_scheme",
]


@dataclass(frozen=True, eq=False, slots=True)
class AffineSchemeConstruction:
    """The exact owned coordinate ring whose spectrum this scheme represents."""

    coordinate_ring: CategoryOfCategories.ElementType


_objects: NativeObjectRealizations[object, AffineSchemeConstruction] = NativeObjectRealizations()
_morphisms: NativeMorphismRealizations[object] = NativeMorphismRealizations()


def _commutative_rings() -> Any:
    return import_module("sage_categories.cat.structured_objects").Rings(Sets).Commutative()


class AffineSchemesCategory(Category[[MorphismCategory.ObjectType], []]):
    """Affine schemes whose computational realization is retained privately in OSCAR."""

    class ObjectType:
        def __init__(self, coordinate_ring: CategoryOfCategories.ElementType) -> None:
            self._coordinate_ring = coordinate_ring

        def coordinate_ring(self) -> CategoryOfCategories.ElementType:
            return self._coordinate_ring

    class ElementType:
        pass

    class MorphismType:
        def __init__(self, pullback: MorphismCategory.ObjectType) -> None:
            self._pullback = pullback

        def pullback(self) -> MorphismCategory.ObjectType:
            """The contravariant map on coordinate rings."""
            return self._pullback

    def from_native(
        self,
        coordinate_ring: CategoryOfCategories.ElementType,
        native: object,
    ) -> AffineSchemesCategory.ObjectType:
        """Wrap ``Spec(coordinate_ring)`` with exact owned/native correspondence."""
        assert coordinate_ring in _commutative_rings()
        native_ring = oscar_native_object(coordinate_ring).native
        native_sections = oscar.structure_sheaf(native)
        assert oscar.same_native(native_sections, native_ring)
        value = self.ObjectType(coordinate_ring)
        _objects.retain(
            self,
            cast(CategoryOfCategories.ElementType, value),
            native,
            AffineSchemeConstruction(coordinate_ring),
        )
        return value

    def from_native_morphism(
        self,
        source: AffineSchemesCategory.ObjectType,
        target: AffineSchemesCategory.ObjectType,
        pullback: MorphismCategory.ObjectType,
        native: object,
    ) -> AffineSchemesCategory.MorphismType:
        """Wrap a native affine map and require its defining pullback and endpoints."""
        assert pullback.domain() is target.coordinate_ring()
        assert pullback.codomain() is source.coordinate_ring()
        source_value = cast(CategoryOfCategories.ElementType, source)
        target_value = cast(CategoryOfCategories.ElementType, target)
        assert oscar.same_native(oscar.affine_domain(native), native_affine_scheme(source_value).native)
        assert oscar.same_native(oscar.affine_codomain(native), native_affine_scheme(target_value).native)
        assert oscar.same_native(oscar.affine_pullback(native), oscar_native_morphism(pullback).native)
        arrow = cast(
            AffineSchemesCategory.MorphismType,
            cast(Any, self).MorphismType(domain=source, codomain=target, data=pullback),
        )
        _morphisms.retain(
            self,
            cast(MorphismCategory.ObjectType, arrow),
            source_value,
            target_value,
            native,
        )
        return arrow

    def __repr__(self) -> str:
        return "AffineSchemes"


@cached_function(key=identity_key)
def AffineSchemes() -> AffineSchemesCategory:
    return AffineSchemesCategory()


def native_affine_scheme(
    value: CategoryOfCategories.ElementType,
) -> NativeObjectRealization[object, AffineSchemeConstruction]:
    return _objects.realization(value)


def native_affine_morphism(
    value: MorphismCategory.ObjectType,
) -> NativeMorphismRealization[object]:
    return _morphisms.realization(value)


def _spec_object(ring: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
    native = oscar.affine_spec(oscar_native_object(ring).native)
    return cast(CategoryOfCategories.ElementType, AffineSchemes().from_native(ring, native))


def _spec_morphism(opposite_ring_map: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
    ring_map = opposite_morphism(opposite_ring_map)
    source = cast(AffineSchemesCategory.ObjectType, _spec_object(ring_map.codomain()))
    target = cast(AffineSchemesCategory.ObjectType, _spec_object(ring_map.domain()))
    native = oscar.affine_morphism(
        native_affine_scheme(cast(CategoryOfCategories.ElementType, source)).native,
        native_affine_scheme(cast(CategoryOfCategories.ElementType, target)).native,
        oscar_native_morphism(ring_map).native,
    )
    return cast(
        MorphismCategory.ObjectType,
        AffineSchemes().from_native_morphism(source, target, ring_map, native),
    )


Spec: Functor = Fun(_commutative_rings().op(), AffineSchemes())(_spec_object, _spec_morphism)
