from dataclasses import dataclass
from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.morphisms import MorphismCategory
__all__ = ['PrimeIdeal', 'prime_field', 'polynomial_ring', 'quotient_ring', 'principal_localization', 'prime_ideal', 'prime_ideal_preimage', 'localize_at_prime', 'induced_stalk_map', 'induced_stalk_map_to', 'presented_ring_homomorphism', 'localization_extension', 'inverse_unit']

@dataclass(frozen=True, eq=False, slots=True)
class _PrimeFieldConstruction:
    characteristic: int

@dataclass(frozen=True, eq=False, slots=True)
class _PolynomialConstruction:
    base: CategoryOfCategories.ElementType
    names: tuple[str, ...]

@dataclass(frozen=True, eq=False, slots=True)
class _QuotientConstruction:
    source: CategoryOfCategories.ElementType
    relations: tuple[CategoryOfCategories.ElementType, ...]

@dataclass(frozen=True, eq=False, slots=True)
class _LocalizationConstruction:
    source: CategoryOfCategories.ElementType
    element: CategoryOfCategories.ElementType

@dataclass(frozen=True, eq=False, slots=True)
class PrimeIdeal:
    ring: CategoryOfCategories.ElementType
    generators: tuple[CategoryOfCategories.ElementType, ...]

@dataclass(frozen=True, eq=False, slots=True)
class _PrimeLocalizationConstruction:
    source: CategoryOfCategories.ElementType
    prime: PrimeIdeal

def prime_field(characteristic: int) -> CategoryOfCategories.ElementType:
    ...

def polynomial_ring(base: CategoryOfCategories.ElementType, names: tuple[str, ...]) -> tuple[CategoryOfCategories.ElementType, tuple[CategoryOfCategories.ElementType, ...]]:
    ...

def quotient_ring(source: CategoryOfCategories.ElementType, relations: tuple[CategoryOfCategories.ElementType, ...]) -> tuple[CategoryOfCategories.ElementType, MorphismCategory.ObjectType]:
    ...

def principal_localization(source: CategoryOfCategories.ElementType, element: CategoryOfCategories.ElementType) -> tuple[CategoryOfCategories.ElementType, MorphismCategory.ObjectType]:
    ...

def prime_ideal(ring: CategoryOfCategories.ElementType, generators: tuple[CategoryOfCategories.ElementType, ...]) -> PrimeIdeal:
    ...

def prime_ideal_preimage(mapping: MorphismCategory.ObjectType, target_prime: PrimeIdeal) -> PrimeIdeal:
    ...

def localize_at_prime(prime: PrimeIdeal) -> tuple[CategoryOfCategories.ElementType, MorphismCategory.ObjectType]:
    ...

def induced_stalk_map(mapping: MorphismCategory.ObjectType, target_prime: PrimeIdeal) -> tuple[PrimeIdeal, CategoryOfCategories.ElementType, CategoryOfCategories.ElementType, MorphismCategory.ObjectType]:
    ...

def induced_stalk_map_to(mapping: MorphismCategory.ObjectType, target_prime: PrimeIdeal, target_local: CategoryOfCategories.ElementType, target_localization: MorphismCategory.ObjectType) -> tuple[PrimeIdeal, CategoryOfCategories.ElementType, MorphismCategory.ObjectType, MorphismCategory.ObjectType]:
    ...

def presented_ring_homomorphism(source: CategoryOfCategories.ElementType, target: CategoryOfCategories.ElementType, generator_images: tuple[CategoryOfCategories.ElementType, ...]) -> MorphismCategory.ObjectType:
    ...

def localization_extension(localized: CategoryOfCategories.ElementType, target: CategoryOfCategories.ElementType, base_map: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
    ...

def inverse_unit(element: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
    ...

def _principal_localization_from_native(source: CategoryOfCategories.ElementType, element: CategoryOfCategories.ElementType, native_localized: object, native_map: object) -> tuple[CategoryOfCategories.ElementType, MorphismCategory.ObjectType]:
    ...
