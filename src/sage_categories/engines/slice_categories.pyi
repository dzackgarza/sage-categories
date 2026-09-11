from sage_categories.engines import fp_categories as fp_categories
from sage_categories.engines.gap import SLICE_CATEGORIES as SLICE_CATEGORIES
from sage_categories.engines.gap import load_repository_package as load_repository_package

__all__ = ["slice_category"]

def slice_category(category: object, base: object, arrows: tuple[object, ...]): ...
