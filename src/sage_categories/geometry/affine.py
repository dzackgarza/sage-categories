"""OSCAR-backed affine schemes and the contravariant ``Spec`` functor."""

from __future__ import annotations

from collections.abc import Hashable
from dataclasses import dataclass
from typing import Any, cast

from sympy import false, true

from sage_categories.algebra.commutative_rings import (
    PrimeIdeal,
    induced_stalk_map_to,
    localization_extension,
    localize_at_prime,
    prime_ideal,
)
from sage_categories.cat.assembly import chosen_construction
from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.declarations import Sets
from sage_categories.cat.functors import Cat, Fun, Functor
from sage_categories.cat.leaf_categories import (
    ContravariantFaithfulStructureCategory,
    ParameterizedThinCategory,
)
from sage_categories.cat.morphisms import Mor, MorphismCategory
from sage_categories.cat.opposites import opposite_morphism
from sage_categories.geometry._firewall import affine as _backend
from sage_categories.geometry._ring_categories import commutative_rings as _rings
from sage_categories.geometry.sheaves import RingPresheaf, ring_presheaf_from_functor
from sage_categories.geometry.spaces import TopologicalSpaces, TopologicalSpacesCategory

__all__ = [
    "AffineOpen",
    "AffineOpenCategory",
    "AffineSchemes",
    "AffineSchemesCategory",
    "AffineSpectrumPoint",
    "Spec",
    "affine_continuous_map",
    "affine_open_preimage",
    "affine_structure_sheaf",
    "affine_topological_space",
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


@dataclass(frozen=True, eq=False, slots=True)
class _AffineOpenData:
    scheme: AffineSchemesCategory.ObjectType
    section_ring: CategoryOfCategories.ElementType
    parent: AffineOpenCategory.ObjectType | None
    localizing_element: CategoryOfCategories.ElementType | None
    ancestors: tuple[AffineOpenCategory.ObjectType, ...]
    restrictions: tuple[tuple[AffineOpenCategory.ObjectType, MorphismCategory.ObjectType], ...]


class AffineOpenCategory(ParameterizedThinCategory):
    """The retained tree of admissible OSCAR affine/principal opens of one affine scheme."""

    class ObjectType:
        def __init__(self, data: _AffineOpenData) -> None:
            self._data = data
            self._ancestors = data.ancestors
            self._restrictions = dict(data.restrictions)

        def section_ring(self) -> CategoryOfCategories.ElementType:
            return self._data.section_ring

        def scheme(self) -> AffineSchemesCategory.ObjectType:
            return self._data.scheme

        def parent_open(self) -> AffineOpenCategory.ObjectType | None:
            return self._data.parent

        def localizing_element(self) -> CategoryOfCategories.ElementType | None:
            return self._data.localizing_element

        def restriction_to(self, ancestor: AffineOpenCategory.ObjectType) -> MorphismCategory.ObjectType:
            assert any(ancestor is retained for retained in self._ancestors)
            return self._restrictions[ancestor]

    class ElementType:
        pass

    class MorphismType:
        pass

    def scheme(self) -> AffineSchemesCategory.ObjectType:
        return cast(AffineSchemesCategory.ObjectType, self.parameter(0))

    def root(self) -> AffineOpenCategory.ObjectType:
        scheme = self.scheme()

        def construct() -> AffineOpenCategory.ObjectType:
            value = _backend.root_open(
                cast(CategoryOfCategories.ElementType, scheme),
                lambda: self.assemble_object(
                    _AffineOpenData(
                        scheme,
                        scheme.coordinate_ring(),
                        None,
                        None,
                        (),
                        (),
                    )
                ),
            )
            return cast(AffineOpenCategory.ObjectType, value)

        return chosen_construction(self, "root-open", (), construct)

    def principal_open(
        self,
        parent: AffineOpenCategory.ObjectType,
        element: CategoryOfCategories.ElementType,
    ) -> AffineOpenCategory.ObjectType:
        """Retain ``D(element)`` inside ``parent`` with OSCAR's actual section ring/map."""
        assert element.parent() is parent.section_ring()

        def build() -> AffineOpenCategory.ObjectType:
            def construct(
                section_ring: CategoryOfCategories.ElementType,
                restriction: MorphismCategory.ObjectType,
            ) -> CategoryOfCategories.ElementType:
                ancestor_restrictions = tuple(
                    (ancestor, restriction * parent.restriction_to(ancestor))
                    for ancestor in parent._ancestors
                )
                return self.assemble_object(
                    _AffineOpenData(
                        self.scheme(),
                        section_ring,
                        parent,
                        element,
                        (parent, *parent._ancestors),
                        ((parent, restriction), *ancestor_restrictions),
                    )
                )

            return cast(
                AffineOpenCategory.ObjectType,
                _backend.principal_open(parent, element, construct),
            )

        return chosen_construction(
            self,
            "principal-open",
            (parent, element),
            build,
        )

    def _admits_morphism(
        self,
        domain: AffineOpenCategory.ObjectType,
        codomain: AffineOpenCategory.ObjectType,
    ) -> bool:
        return domain is codomain or any(codomain is ancestor for ancestor in domain._ancestors)

    def __repr__(self) -> str:
        return f"AffineOpens({self.scheme()!r})"


AffineOpen = AffineOpenCategory.ObjectType


class AffineSchemesCategory(ContravariantFaithfulStructureCategory):
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

    def structure_functors(self) -> tuple[Functor, ...]:
        opposite_rings = _rings().op()
        coordinate_ring = Fun(self, opposite_rings).Faithful().Isofibrations()(
            lambda scheme: scheme.coordinate_ring(),
            lambda arrow: opposite_morphism(arrow.pullback()),
        )
        return (*super().structure_functors(), coordinate_ring)

    def from_coordinate_ring(
        self,
        coordinate_ring: CategoryOfCategories.ElementType,
    ) -> AffineSchemesCategory.ObjectType:
        """Construct ``Spec(coordinate_ring)`` and retain its private OSCAR realization."""
        assert coordinate_ring in _rings()
        value = cast(AffineSchemesCategory.ObjectType, self.assemble_object(coordinate_ring))
        _backend.retain_spectrum(
            self,
            cast(CategoryOfCategories.ElementType, value),
            coordinate_ring,
            AffineSchemeConstruction(coordinate_ring),
        )
        return value

    def construct_morphism(
        self,
        source: AffineSchemesCategory.ObjectType,
        target: AffineSchemesCategory.ObjectType,
        pullback: MorphismCategory.ObjectType,
    ) -> AffineSchemesCategory.MorphismType:
        """Construct an affine map from its contravariant coordinate-ring homomorphism."""
        assert pullback.domain() is target.coordinate_ring()
        assert pullback.codomain() is source.coordinate_ring()
        return cast(AffineSchemesCategory.MorphismType, self._morphism_from_data(source, target, pullback))

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


def AffineSchemes() -> AffineSchemesCategory:
    return cast(AffineSchemesCategory, chosen_construction(Cat(), "affine-schemes", (), AffineSchemesCategory))


def native_affine_scheme(
    value: CategoryOfCategories.ElementType,
):
    return _backend.native_affine_scheme(value)


def native_affine_morphism(
    value: MorphismCategory.ObjectType,
):
    return _backend.native_affine_morphism(value)


def _spec_object(ring: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
    return cast(CategoryOfCategories.ElementType, AffineSchemes().from_coordinate_ring(ring))


def _spec_morphism(opposite_ring_map: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
    ring_map = opposite_morphism(opposite_ring_map)
    source = cast(AffineSchemesCategory.ObjectType, _spec_object(ring_map.codomain()))
    target = cast(AffineSchemesCategory.ObjectType, _spec_object(ring_map.domain()))
    return cast(MorphismCategory.ObjectType, AffineSchemes().construct_morphism(source, target, ring_map))


Spec: Functor = Fun(_rings().op(), AffineSchemes())(_spec_object, _spec_morphism)


def affine_structure_sheaf(
    scheme: AffineSchemesCategory.ObjectType,
) -> tuple[AffineOpenCategory, RingPresheaf[AffineOpenCategory.ObjectType]]:
    """The OSCAR structure sheaf on the retained principal-open tree of ``scheme``."""
    opens = cast(
        AffineOpenCategory,
        chosen_construction(
            AffineSchemes(),
            "affine-open-category",
            (scheme,),
            lambda: AffineOpenCategory(scheme),
        ),
    )
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

    def key_to_open(key: AffineOpenCategory.ObjectType) -> CategoryOfCategories.ElementType:
        return key

    functor = Fun(opens.op(), rings)(on_object, on_morphism)
    presheaf = ring_presheaf_from_functor(
        scheme,
        opens,
        functor,
        key_to_open,
        lambda open_object: open_object,
    )
    return opens, presheaf


def affine_topological_space(
    scheme: AffineSchemesCategory.ObjectType,
) -> TopologicalSpacesCategory.ObjectType[AffineOpenCategory.ObjectType]:
    """The represented prime spectrum with its retained principal-open basis."""

    def construct() -> TopologicalSpacesCategory.ObjectType[AffineOpenCategory.ObjectType]:
        opens, _ = affine_structure_sheaf(scheme)

        def point_member(value: Hashable):
            match isinstance(value, AffineSpectrumPoint):
                case True:
                    match value.scheme is scheme:
                        case True:
                            return true
                        case False:
                            return false
                case False:
                    return false

        def open_member(value: Hashable):
            match isinstance(value, AffineOpenCategory.ObjectType):
                case True:
                    match value.scheme() is scheme:
                        case True:
                            return true
                        case False:
                            return false
                case False:
                    return false

        carrier = Sets.from_membership(point_member)
        open_carrier = Sets.from_membership(open_member)

        def open_point(
            key: AffineOpenCategory.ObjectType,
        ) -> CategoryOfCategories.ElementType:
            assert key.scheme() is scheme
            return cast(CategoryOfCategories.ElementType, cast(Any, open_carrier).point(key))

        return TopologicalSpaces().from_open_category(
            carrier,
            open_carrier,
            opens,
            open_point,
            lambda key: key,
        )

    return cast(
        TopologicalSpacesCategory.ObjectType[AffineOpenCategory.ObjectType],
        chosen_construction(
            AffineSchemes(),
            "affine-topological-space",
            (scheme,),
            construct,
        ),
    )


def affine_open_preimage(
    mapping: AffineSchemesCategory.MorphismType,
    target_open: AffineOpenCategory.ObjectType,
) -> tuple[AffineOpenCategory.ObjectType, MorphismCategory.ObjectType]:
    """The principal-open inverse image and induced structure-sheaf map."""
    assert target_open.scheme() is mapping.codomain()
    source_opens, _ = affine_structure_sheaf(mapping.domain())

    def construct() -> tuple[AffineOpenCategory.ObjectType, MorphismCategory.ObjectType]:
        match target_open.parent_open():
            case None:
                source_open = source_opens.root()
                return source_open, mapping.pullback()
            case target_parent:
                source_parent, parent_pullback = affine_open_preimage(
                    mapping,
                    target_parent,
                )
                element = target_open.localizing_element()
                assert element is not None
                image_element = parent_pullback(element)
                source_open = source_opens.principal_open(source_parent, image_element)
                base_map = source_open.restriction_to(source_parent) * parent_pullback
                section_map = localization_extension(
                    target_open.section_ring(),
                    source_open.section_ring(),
                    base_map,
                )
                return source_open, section_map

    return chosen_construction(
        AffineSchemes(),
        "affine-open-preimage",
        (mapping, target_open),
        construct,
    )


def affine_continuous_map(
    mapping: AffineSchemesCategory.MorphismType,
) -> TopologicalSpacesCategory.MorphismType:
    """The continuous prime-spectrum map underlying an affine scheme morphism."""

    def construct() -> TopologicalSpacesCategory.MorphismType:
        source = affine_topological_space(mapping.domain())
        target = affine_topological_space(mapping.codomain())
        target_opens, _ = affine_structure_sheaf(mapping.codomain())
        source_opens, _ = affine_structure_sheaf(mapping.domain())

        def point_image(value: Hashable) -> Hashable:
            assert isinstance(value, AffineSpectrumPoint)
            image, _ = AffineSchemes().map_spectrum_point(mapping, value)
            return image

        underlying = Mor(Sets)(source.carrier(), target.carrier())(point_image)

        def preimage(
            open_object: CategoryOfCategories.ElementType,
        ) -> CategoryOfCategories.ElementType:
            target_open = cast(AffineOpenCategory.ObjectType, open_object)
            return affine_open_preimage(mapping, target_open)[0]

        inverse = Fun(target_opens, source_opens)(
            preimage,
            lambda inclusion: Mor(source_opens)(
                preimage(inclusion.domain()),
                preimage(inclusion.codomain()),
            )(),
        )
        return TopologicalSpaces().morphism_with_inverse_image(
            source,
            target,
            underlying,
            inverse,
        )

    return cast(
        TopologicalSpacesCategory.MorphismType,
        chosen_construction(
            AffineSchemes(),
            "affine-continuous-map",
            (mapping,),
            construct,
        ),
    )
