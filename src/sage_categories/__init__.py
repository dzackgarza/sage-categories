"""Owned categories with Sage confined to explicit realizations.

Importing this package loads ``Cat``: ``Cat()``, functors, the ``Mor(n, C)`` tower, the
shapes, the predicate boundary, and the categories ``Cat`` declares.  It loads no leaf,
because information flows from ``Cat`` into the leaves and never back (D81).
``sage_categories.all`` is the import surface for the whole owned universe.

The four layers, in the order of dependence D173 and D175 fix: the kernel
(``sage_categories.kernel``), which is engineering and states no mathematics; ``Cat``
(``sage_categories.cat``), which owns the mathematics every category shares;
``cat_kernel``, the work that needs both; then the leaves.
"""

from importlib.metadata import version as _distribution_version

from sage_categories import _bootstrap as _bootstrap
from sage_categories.cat.adjunctions import Adjunctions, Equivalences
from sage_categories.cat.calculus import (
    binary_product_data,
    curry,
    currying,
    evaluation,
    natural_isomorphism,
    pair_maps,
    power_functor,
    precompose,
    product_functor,
    transpose,
    uncurry,
)
from sage_categories.cat.category import Category
from sage_categories.cat.concrete import ConcreteCategory
from sage_categories.cat.cones import (
    cocones as Cocones,
)
from sage_categories.cat.cones import (
    colimit_cocones as ColimitCocones,
)
from sage_categories.cat.cones import (
    cones as Cones,
)
from sage_categories.cat.cones import (
    limit_cones as LimitCones,
)
from sage_categories.cat.declarations import (
    NN,
    ZZ,
    MagmaObjects,
    MonoidObjects,
    Posets,
    RingObjects,
    SemiringObjects,
    Sets,
    TotallyOrderedSets,
    omega,
)
from sage_categories.cat.functors import Cat, Fun
from sage_categories.cat.indexed import Grothendieck, IndexedCategories
from sage_categories.cat.kan import (
    left_kan_adjunction,
    left_kan_desc,
    left_kan_extension,
    left_kan_unit,
    right_kan_adjunction,
    right_kan_counit,
    right_kan_extension,
    right_kan_lift,
)
from sage_categories.cat.limit_basis import (
    DiagramPresentation,
    colimit_from_coproducts_coequalizers,
    diagram_presentation,
    limit_from_products_equalizers,
    parallel_pair,
)
from sage_categories.cat.modules import Modules
from sage_categories.cat.monoidal import (
    Actions,
    Cartesian,
    Composition,
    MonoidalStructures,
    SelfAction,
    TrivialAction,
)
from sage_categories.cat.morphisms import Mor
from sage_categories.cat.opposites import Op
from sage_categories.cat.predicates import (
    Axiom,
    Decision,
    Predicate,
    Query,
    Unknown,
    UnknownClass,
    ask,
    assume,
    retract,
)
from sage_categories.cat.profunctors import (
    Profunctors,
    compose_profunctor_transformations,
    compose_profunctors,
    identity_profunctor,
    profunctor_unitor,
)
from sage_categories.cat.relations import Relations
from sage_categories.cat.shapes import Discrete, Thin
from sage_categories.cat.structured_objects import (
    AdditiveGroups,
    AdditiveMagmas,
    AdditiveMonoids,
    EilenbergMoore,
    EndofunctorAlgebras,
    Equifier,
    Groups,
    Inserter,
    Magmas,
    Monoids,
    MultiplicativeMagmas,
    MultiplicativeMonoids,
    PointedMagmas,
    Rings,
    Semirings,
)
from sage_categories.cat.total_cones import total_cones as TotalCones
from sage_categories.cat.universal_arrows import (
    InitialObjects,
    LeftUniversalArrows,
    RightUniversalArrows,
    TerminalObjects,
    left_mate,
    right_mate,
)
from sage_categories.cat.weighted import (
    Elements,
    coend,
    coyoneda,
    element,
    element_projection,
    end,
    end_to_natural_transformation,
    hom_functor,
    natural_transformation_diagram,
    natural_transformation_to_end,
    restricted_yoneda,
    separating_evaluation,
    separating_evaluation_injection,
    weighted_colimit,
    weighted_colimit_desc,
    weighted_colimit_map,
    weighted_injection,
    weighted_limit,
    weighted_limit_lift,
    weighted_limit_map,
    weighted_projection,
    yoneda,
)

del _bootstrap

__all__ = [
    "NN",
    "ZZ",
    "Actions",
    "AdditiveGroups",
    "AdditiveMagmas",
    "AdditiveMonoids",
    "Adjunctions",
    "Axiom",
    "Cartesian",
    "Cat",
    "Category",
    "Cocones",
    "ColimitCocones",
    "Composition",
    "ConcreteCategory",
    "Cones",
    "Decision",
    "DiagramPresentation",
    "Discrete",
    "EilenbergMoore",
    "Elements",
    "EndofunctorAlgebras",
    "Equifier",
    "Equivalences",
    "Fun",
    "Grothendieck",
    "Groups",
    "IndexedCategories",
    "InitialObjects",
    "Inserter",
    "LeftUniversalArrows",
    "LimitCones",
    "MagmaObjects",
    "Magmas",
    "Modules",
    "MonoidObjects",
    "MonoidalStructures",
    "Monoids",
    "Mor",
    "MultiplicativeMagmas",
    "MultiplicativeMonoids",
    "Op",
    "PointedMagmas",
    "Posets",
    "Predicate",
    "Profunctors",
    "Query",
    "Relations",
    "RightUniversalArrows",
    "RingObjects",
    "Rings",
    "SelfAction",
    "SemiringObjects",
    "Semirings",
    "Sets",
    "TerminalObjects",
    "Thin",
    "TotalCones",
    "TotallyOrderedSets",
    "TrivialAction",
    "Unknown",
    "UnknownClass",
    "__version__",
    "ask",
    "assume",
    "binary_product_data",
    "coend",
    "colimit_from_coproducts_coequalizers",
    "compose_profunctor_transformations",
    "compose_profunctors",
    "coyoneda",
    "curry",
    "currying",
    "diagram_presentation",
    "element",
    "element_projection",
    "end",
    "end_to_natural_transformation",
    "evaluation",
    "hom_functor",
    "identity_profunctor",
    "left_kan_adjunction",
    "left_kan_desc",
    "left_kan_extension",
    "left_kan_unit",
    "left_mate",
    "limit_from_products_equalizers",
    "natural_isomorphism",
    "natural_transformation_diagram",
    "natural_transformation_to_end",
    "omega",
    "pair_maps",
    "parallel_pair",
    "power_functor",
    "precompose",
    "product_functor",
    "profunctor_unitor",
    "restricted_yoneda",
    "retract",
    "right_kan_adjunction",
    "right_kan_counit",
    "right_kan_extension",
    "right_kan_lift",
    "right_mate",
    "separating_evaluation",
    "separating_evaluation_injection",
    "transpose",
    "uncurry",
    "version",
    "weighted_colimit",
    "weighted_colimit_desc",
    "weighted_colimit_map",
    "weighted_injection",
    "weighted_limit",
    "weighted_limit_lift",
    "weighted_limit_map",
    "weighted_projection",
    "yoneda",
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
