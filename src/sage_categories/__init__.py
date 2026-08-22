"""Owned categories with Sage confined to explicit realizations."""

from importlib.metadata import version as _distribution_version

from sage_categories.abstract_categories.arrow_categories import (
    ArrowCategory,
    Core,
    WideSubcategory,
    declare_isomorphism,
)
from sage_categories.abstract_categories.cat import Cat
from sage_categories.abstract_categories.functors import (
    ComposedFunctor,
    Functor,
    IdentityFunctor,
    NaturalIsomorphism,
    NaturalTransformation,
    NaturalTransformations,
    StructuralFunctor,
)
from sage_categories.abstract_categories.products import (
    Biproduct,
    Cocone,
    Cone,
    Coproduct,
    Product,
)
from sage_categories.abstract_categories.slice_categories import (
    Coslice,
    Covered,
    Covering,
    Slice,
    Subobject,
    Superobject,
)
from sage_categories.category import Category
from sage_categories.theories.cardinals import Cardinals
from sage_categories.theories.sets import (
    CoproductOfSets,
    DiscreteCategories,
    DiscreteCategory,
    FiniteDiscreteCategories,
    FiniteSet,
    ProductOfSets,
    SetFamily,
    SetMap,
    Sets,
)
from sage_categories.values import (
    Arrow,
    MathematicalElement,
    MathematicalObject,
)

__all__ = [
    "Arrow",
    "ArrowCategory",
    "Biproduct",
    "Cardinals",
    "Cat",
    "Category",
    "ComposedFunctor",
    "Cone",
    "Cocone",
    "Coproduct",
    "CoproductOfSets",
    "Core",
    "Covered",
    "Covering",
    "Coslice",
    "DiscreteCategories",
    "DiscreteCategory",
    "FiniteDiscreteCategories",
    "FiniteSet",
    "Functor",
    "IdentityFunctor",
    "MathematicalElement",
    "MathematicalObject",
    "NaturalIsomorphism",
    "NaturalTransformation",
    "NaturalTransformations",
    "Product",
    "ProductOfSets",
    "SetFamily",
    "SetMap",
    "Sets",
    "Slice",
    "StructuralFunctor",
    "Subobject",
    "Superobject",
    "WideSubcategory",
    "__version__",
    "declare_isomorphism",
    "version",
]

# One source of truth. The version is declared once, in pyproject.toml, and
# read back from the installed distribution metadata rather than restated
# here, so a package built from this tree cannot disagree with itself.
__version__: str = _distribution_version("sage-categories")


def version() -> str:
    """Return the installed version of this package.

    At a Sage prompt the result prints on its own, so this is also the
    version print: ``import sage_categories; sage_categories.version()``.
    """
    return __version__
