from sage_categories.engines import fp_categories as fp_categories
from sage_categories.engines.gap import SLICE_CATEGORIES as SLICE_CATEGORIES, load_repository_package as load_repository_package
from sage_categories.kernel.sage_runtime import MonoDict as MonoDict

def slice_category(category: object, base: object, arrows: tuple[object, ...]):
    ...
