from sage.libs.gap.element import GapElement as GapElement

from sage_categories.engines import fp_categories as fp_categories
from sage_categories.engines.gap import FINITE_CATEGORY_PACKAGES as FINITE_CATEGORY_PACKAGES
from sage_categories.engines.gap import load_packages as load_packages

__all__ = ["finite_product_data"]

def finite_product_data(
    factors: tuple[object, ...], object_families: tuple[tuple[object, ...], ...], morphism_families: tuple[tuple[object, ...], ...]
) -> tuple[tuple[tuple[object, ...], ...], tuple[tuple[object, ...], ...]]: ...
