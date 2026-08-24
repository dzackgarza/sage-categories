"""Ordered-set public API."""

from sage_categories.theories.finite_posets import (
    FinitePosetObject,
    FinitePosetsCategory,
)
from sage_categories.theories.ordered_set_constructors import (
    SimplexOrderIndexing,
    SimplexOrders,
)
from sage_categories.theories.poset_core import (
    ForgetPosetFunctor,
    OrderRelation,
    PartiallyOrderedSets,
    PartiallyOrderedSetsCategory,
    PosetElement,
    PosetHomCategory,
    PosetMorphism,
    PosetObject,
    is_partially_ordered_sets_category,
    is_poset_element,
    is_poset_hom_category,
)
from sage_categories.theories.thin_categories import (
    ThinCategory,
    ThinCategoryArrow,
    ThinCategoryArrowElement,
    ThinCategoryArrowSet,
    ThinCategoryHom,
    ThinCategoryObjectElement,
    ThinCategoryObjectSet,
    is_thin_category,
    is_thin_category_hom,
)
from sage_categories.theories.total_orders import (
    FinitePosets,
    FiniteTotallyOrderedSets,
    FiniteTotallyOrderedSetsCategory,
    TotallyOrderedSets,
    TotallyOrderedSetsCategory,
    is_total_order_element,
    is_totally_ordered_sets_category,
)

__all__ = (
    "FinitePosetObject",
    "FinitePosets",
    "FinitePosetsCategory",
    "FiniteTotallyOrderedSets",
    "FiniteTotallyOrderedSetsCategory",
    "ForgetPosetFunctor",
    "OrderRelation",
    "PartiallyOrderedSets",
    "PartiallyOrderedSetsCategory",
    "PosetElement",
    "PosetHomCategory",
    "PosetMorphism",
    "PosetObject",
    "SimplexOrderIndexing",
    "SimplexOrders",
    "ThinCategory",
    "ThinCategoryArrow",
    "ThinCategoryArrowElement",
    "ThinCategoryArrowSet",
    "ThinCategoryHom",
    "ThinCategoryObjectElement",
    "ThinCategoryObjectSet",
    "TotallyOrderedSets",
    "TotallyOrderedSetsCategory",
    "is_partially_ordered_sets_category",
    "is_poset_element",
    "is_poset_hom_category",
    "is_thin_category",
    "is_thin_category_hom",
    "is_total_order_element",
    "is_totally_ordered_sets_category",
)
