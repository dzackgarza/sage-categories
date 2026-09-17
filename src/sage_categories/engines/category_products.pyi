from sage.libs.gap.element import GapElement as GapElement
from sage_categories.engines import fp_categories as fp_categories
from sage_categories.engines.gap import FINITE_CATEGORY_PACKAGES as FINITE_CATEGORY_PACKAGES, load_packages as load_packages

def finite_product_data(factors: tuple[object, ...], object_families: tuple[tuple[object, ...], ...], morphism_families: tuple[tuple[object, ...], ...]) -> tuple[tuple[tuple[object, ...], ...], tuple[tuple[object, ...], ...]]:
    ...
