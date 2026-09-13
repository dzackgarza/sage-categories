"""OSCAR-backed affine schemes and the contravariant ``Spec`` functor."""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from typing import Any, cast

from sage_categories.algebra._commutative_rings_oscar import (
    oscar_element_handle,
    oscar_morphism_handle,
    oscar_object_handle,
)
from sage_categories.algebra.commutative_rings import (
    PrimeIdeal,
    _principal_localization_from_native,
    induced_stalk_map_to,
    localize_at_prime,
    prime_ideal,
)
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.functors import Fun, Functor
from sage_categories.cat.morphisms import Mor, MorphismCategory
from sage_categories.cat.native import (
    NativeMorphismRealization,
    NativeMorphismRealizations,
    NativeObjectRealization,
    NativeObjectRealizations,
)
from sage_categories.cat.opposites import opposite_morphism
from sage_categories.engines import oscar
from sage_categories.engines.julia_bridge import OscarHandle
from sage_categories.geometry.sheaves import RingPresheaf, _rings, ring_presheaf_from_functor

__all__ = [
    "AffineOpen",
    "AffineOpenCategory",
    "AffineSchemes",
    "AffineSchemesCategory",
    "AffineSpectrumPoint",
    "Spec",
    "affine_structure_sheaf",
    "native_affine_morphism",
    "native_affine_scheme",
]


@dataclass(frozen=True, eq=False, slots=True)
class AffineSchemeConstruction:
    """The exact owned coordinate ring whose spectrum this scheme represents."""

    coordinate_ring: CategoryOfCategories.ElementType


@dataclass(frozen=True, eq=False, slots=True)
class AffineSpectrumPoint:
    """A prime-spectrum point together with its exact retained local ring."""

    scheme: AffineSchemesCategory.ObjectType
    prime: PrimeIdeal
    local_ring: CategoryOfCategories.ElementType
    localization: MorphismCategory.ObjectType


_objects: NativeObjectRealizations[OscarHandle, AffineSchemeConstruction] = NativeObjectRealizations()
_morphisms: NativeMorphismRealizations[OscarHandle] = NativeMorphismRealizations()


@dataclass(frozen=True, eq=False, slots=True)
class _AffineOpenData:
    scheme: AffineSchemesCategory.ObjectType
    native: OscarHandle
    section_ring: CategoryOfCategories.ElementType
    ancestors: tuple[AffineOpenCategory.ObjectType, ...]
    restrictions: tuple[tuple[AffineOpenCategory.ObjectType, MorphismCategory.ObjectType], ...]


class AffineOpenCategory(Category[Any, Any]):
    """The retained tree of admissible OSCAR affine/principal opens of one affine scheme."""

    class ObjectType:
        def __init__(self, data: _AffineOpenData) -> None:
            self._data = data
            self._ancestors = data.ancestors
            self._restrictions = dict(data.restrictions)

        def native(self) -> OscarHandle:
            return self._data.native

        def section_ring(self) -> CategoryOfCategories.ElementType:
            return self._data.section_ring

        def restriction_to(self, ancestor: AffineOpenCategory.ObjectType) -> MorphismCategory.ObjectType:
            assert any(ancestor is retained for retained in self._ancestors)
            return self._restrictions[ancestor]

    class ElementType:
        pass

    class MorphismType:
        pass

    def __init__(self, scheme: AffineSchemesCategory.ObjectType) -> None:
        self._scheme = scheme
        native_scheme = native_affine_scheme(cast(CategoryOfCategories.ElementType, scheme)).native
        self._native_sheaf = oscar.structure_sheaf(native_scheme)
        self._root = self.ObjectType(_AffineOpenData(scheme, native_scheme, scheme.coordinate_ring(), (), ()))
        super().__init__()

    def scheme(self) -> AffineSchemesCategory.ObjectType:
        return self._scheme

    def root(self) -> AffineOpenCategory.ObjectType:
        return self._root

    def principal_open(
        self,
        parent: AffineOpenCategory.ObjectType,
        element: CategoryOfCategories.ElementType,
    ) -> AffineOpenCategory.ObjectType:
        """Retain ``D(element)`` inside ``parent`` with OSCAR's actual section ring/map."""
        assert element.parent() is parent.section_ring()
        native_open = oscar.principal_open(parent.native(), oscar_element_handle(element))
        native_ring = oscar.sheaf_value(self._native_sheaf, native_open)
        native_restriction = oscar.sheaf_restriction(self._native_sheaf, parent.native(), native_open)
        section_ring, restriction = _principal_localization_from_native(parent.section_ring(), element, native_ring, native_restriction)
        ancestor_restrictions = tuple(
            (
                ancestor,
                restriction * parent.restriction_to(ancestor),
            )
            for ancestor in parent._ancestors
        )
        return self.ObjectType(
            _AffineOpenData(
                self._scheme,
                native_open,
                section_ring,
                (parent, *parent._ancestors),
                ((parent, restriction), *ancestor_restrictions),
            )
        )

    def construct_morphism(
        self,
        domain: CategoryOfCategories.ElementType,
        codomain: CategoryOfCategories.ElementType,
        *args: Any,
        **kwargs: Any,
    ) -> MorphismCategory.ObjectType:
        source = cast(AffineOpenCategory.ObjectType, domain)
        target = cast(AffineOpenCategory.ObjectType, codomain)
        assert source is target or any(target is ancestor for ancestor in source._ancestors)
        return cast(
            MorphismCategory.ObjectType,
            cast(Any, self).MorphismType(domain=source, codomain=target),
        )

    def construct_identity(self, member_object: Any) -> Any:
        return self.construct_morphism(member_object, member_object)

    def composite(
        self,
        second: Any,
        first: Any,
    ) -> Any:
        assert first.codomain() is second.domain()
        return self.construct_morphism(first.domain(), second.codomain())

    def __repr__(self) -> str:
        return f"AffineOpens({self._scheme!r})"


AffineOpen = AffineOpenCategory.ObjectType


class AffineSchemesCategory(Category[Any, Any]):
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
        native: OscarHandle,
    ) -> AffineSchemesCategory.ObjectType:
        """Wrap ``Spec(coordinate_ring)`` with exact owned/native correspondence."""
        assert coordinate_ring in _rings()
        native_ring = oscar_object_handle(coordinate_ring)
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
        native: OscarHandle,
    ) -> AffineSchemesCategory.MorphismType:
        """Wrap a native affine map and require its defining pullback and endpoints."""
        assert pullback.domain() is target.coordinate_ring()
        assert pullback.codomain() is source.coordinate_ring()
        source_value = cast(CategoryOfCategories.ElementType, source)
        target_value = cast(CategoryOfCategories.ElementType, target)
        assert oscar.same_native(oscar.affine_domain(native), native_affine_scheme(source_value).native)
        assert oscar.same_native(oscar.affine_codomain(native), native_affine_scheme(target_value).native)
        assert oscar.same_native(oscar.affine_pullback(native), oscar_morphism_handle(pullback))
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

    def spectrum_point(
        self,
        scheme: AffineSchemesCategory.ObjectType,
        generators: tuple[CategoryOfCategories.ElementType, ...],
    ) -> AffineSpectrumPoint:
        """A point of ``Spec(A)`` represented by a checked prime ideal of ``A``."""
        prime = prime_ideal(scheme.coordinate_ring(), generators)
        local_ring, localization = localize_at_prime(prime)
        return AffineSpectrumPoint(scheme, prime, local_ring, localization)

    def map_spectrum_point(
        self,
        mapping: AffineSchemesCategory.MorphismType,
        point: AffineSpectrumPoint,
    ) -> tuple[AffineSpectrumPoint, MorphismCategory.ObjectType]:
        """Map a source point and retain the induced local homomorphism on stalks."""
        assert point.scheme is mapping.domain()
        image_prime, image_local, image_localization, stalk = induced_stalk_map_to(
            mapping.pullback(),
            point.prime,
            point.local_ring,
            point.localization,
        )
        image = AffineSpectrumPoint(mapping.codomain(), image_prime, image_local, image_localization)
        assert stalk.domain() is image.local_ring and stalk.codomain() is point.local_ring
        return image, stalk

    def __repr__(self) -> str:
        return "AffineSchemes"


@cache
def AffineSchemes() -> AffineSchemesCategory:
    return AffineSchemesCategory()


def native_affine_scheme(
    value: CategoryOfCategories.ElementType,
) -> NativeObjectRealization[OscarHandle, AffineSchemeConstruction]:
    return _objects.realization(value)


def native_affine_morphism(
    value: MorphismCategory.ObjectType,
) -> NativeMorphismRealization[OscarHandle]:
    return _morphisms.realization(value)


def _spec_object(ring: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
    native = oscar.affine_spec(oscar_object_handle(ring))
    return cast(CategoryOfCategories.ElementType, AffineSchemes().from_native(ring, native))


def _spec_morphism(opposite_ring_map: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
    ring_map = opposite_morphism(opposite_ring_map)
    source = cast(AffineSchemesCategory.ObjectType, _spec_object(ring_map.codomain()))
    target = cast(AffineSchemesCategory.ObjectType, _spec_object(ring_map.domain()))
    native = oscar.affine_morphism(
        native_affine_scheme(cast(CategoryOfCategories.ElementType, source)).native,
        native_affine_scheme(cast(CategoryOfCategories.ElementType, target)).native,
        oscar_morphism_handle(ring_map),
    )
    return cast(
        MorphismCategory.ObjectType,
        AffineSchemes().from_native_morphism(source, target, ring_map, native),
    )


Spec: Functor = Fun(_rings().op(), AffineSchemes())(_spec_object, _spec_morphism)


def affine_structure_sheaf(
    scheme: AffineSchemesCategory.ObjectType,
) -> tuple[AffineOpenCategory, RingPresheaf]:
    """The OSCAR structure sheaf on the retained principal-open tree of ``scheme``."""
    opens = AffineOpenCategory(scheme)
    rings = _rings()

    def on_object(open_object: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
        return cast(AffineOpenCategory.ObjectType, open_object).section_ring()

    def on_morphism(opposite_inclusion: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        inclusion = opposite_morphism(opposite_inclusion)
        smaller = cast(AffineOpenCategory.ObjectType, inclusion.domain())
        larger = cast(AffineOpenCategory.ObjectType, inclusion.codomain())
        match smaller is larger:
            case True:
                return Mor(rings)(larger.section_ring(), larger.section_ring()).one()
            case False:
                return smaller.restriction_to(larger)

    def key_to_open(key: object) -> CategoryOfCategories.ElementType:
        return cast(CategoryOfCategories.ElementType, cast(AffineOpenCategory.ObjectType, key))

    functor = Fun(opens.op(), rings)(on_object, on_morphism)
    presheaf = ring_presheaf_from_functor(
        scheme,
        opens,
        functor,
        key_to_open,
        lambda open_object: open_object,
    )
    return opens, presheaf
