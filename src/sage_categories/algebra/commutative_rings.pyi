from dataclasses import dataclass

from sage_categories.algebra._commutative_rings_oscar import (
    OscarRingConstruction as OscarRingConstruction,
)
from sage_categories.algebra._commutative_rings_oscar import (
    oscar_element_handle as oscar_element_handle,
)
from sage_categories.algebra._commutative_rings_oscar import (
    oscar_morphism_handle as oscar_morphism_handle,
)
from sage_categories.algebra._commutative_rings_oscar import (
    oscar_native_object as oscar_native_object,
)
from sage_categories.algebra._commutative_rings_oscar import (
    oscar_object_handle as oscar_object_handle,
)
from sage_categories.algebra._commutative_rings_oscar import (
    reconstruct_oscar_morphism as reconstruct_oscar_morphism,
)
from sage_categories.algebra._commutative_rings_oscar import (
    reconstruct_oscar_object as reconstruct_oscar_object,
)
from sage_categories.cat.category import CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.morphisms import MorphismCategory as MorphismCategory
from sage_categories.engines import oscar as oscar
from sage_categories.engines.julia_bridge import OscarHandle as OscarHandle

__all__ = [
    "PrimeIdeal",
    "induced_stalk_map",
    "induced_stalk_map_to",
    "inverse_unit",
    "localization_extension",
    "localize_at_prime",
    "polynomial_ring",
    "presented_ring_homomorphism",
    "prime_field",
    "prime_ideal",
    "prime_ideal_preimage",
    "principal_localization",
    "quotient_ring",
]

@dataclass(frozen=True, eq=False, slots=True)
class PrimeIdeal:
    ring: CategoryOfCategories.ElementType
    generators: tuple[CategoryOfCategories.ElementType, ...]

def prime_field(characteristic: int) -> CategoryOfCategories.ElementType: ...
def polynomial_ring(
    base: CategoryOfCategories.ElementType, names: tuple[str, ...]
) -> tuple[CategoryOfCategories.ElementType, tuple[CategoryOfCategories.ElementType, ...]]: ...
def quotient_ring(
    source: CategoryOfCategories.ElementType, relations: tuple[CategoryOfCategories.ElementType, ...]
) -> tuple[CategoryOfCategories.ElementType, MorphismCategory.ObjectType]: ...
def principal_localization(
    source: CategoryOfCategories.ElementType, element: CategoryOfCategories.ElementType
) -> tuple[CategoryOfCategories.ElementType, MorphismCategory.ObjectType]: ...
def prime_ideal(ring: CategoryOfCategories.ElementType, generators: tuple[CategoryOfCategories.ElementType, ...]) -> PrimeIdeal: ...
def prime_ideal_preimage(mapping: MorphismCategory.ObjectType, target_prime: PrimeIdeal) -> PrimeIdeal: ...
def localize_at_prime(prime: PrimeIdeal) -> tuple[CategoryOfCategories.ElementType, MorphismCategory.ObjectType]: ...
def induced_stalk_map(
    mapping: MorphismCategory.ObjectType, target_prime: PrimeIdeal
) -> tuple[PrimeIdeal, CategoryOfCategories.ElementType, CategoryOfCategories.ElementType, MorphismCategory.ObjectType]: ...
def induced_stalk_map_to(
    mapping: MorphismCategory.ObjectType, target_prime: PrimeIdeal, target_local: CategoryOfCategories.ElementType, target_localization: MorphismCategory.ObjectType
) -> tuple[PrimeIdeal, CategoryOfCategories.ElementType, MorphismCategory.ObjectType, MorphismCategory.ObjectType]: ...
def presented_ring_homomorphism(
    source: CategoryOfCategories.ElementType, target: CategoryOfCategories.ElementType, generator_images: tuple[CategoryOfCategories.ElementType, ...]
) -> MorphismCategory.ObjectType: ...
def localization_extension(
    localized: CategoryOfCategories.ElementType, target: CategoryOfCategories.ElementType, base_map: MorphismCategory.ObjectType
) -> MorphismCategory.ObjectType: ...
def inverse_unit(element: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType: ...
def _principal_localization_from_native(
    source: CategoryOfCategories.ElementType, element: CategoryOfCategories.ElementType, native_localized: OscarHandle, native_map: OscarHandle
) -> tuple[CategoryOfCategories.ElementType, MorphismCategory.ObjectType]: ...
