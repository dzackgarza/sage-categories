"""The theory of ``Cat()``: categories, functors, morphism categories, properties, shapes."""

from sage_categories.cat import category as _category

_category.bootstrap()
del _category

from sage_categories.cat.functors import Cat, Fun
from sage_categories.cat.morphisms import Mor
from sage_categories.cat.adjunctions import Adjunctions, Equivalences
from sage_categories.cat.cones import cones as Cones
from sage_categories.cat.cones import limit_cones as LimitCones
from sage_categories.cat.opposites import Op
from sage_categories.cat.total_cones import total_cones as TotalCones

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
from sage_categories.cat.kan import left_kan_adjunction, right_kan_adjunction
from sage_categories.cat.limit_basis import (
    DiagramPresentation,
    colimit_from_coproducts_coequalizers,
    diagram_presentation,
    limit_from_products_equalizers,
    parallel_pair,
)
from sage_categories.cat.profunctors import (
    Profunctors,
    compose_profunctor_transformations,
    compose_profunctors,
    identity_profunctor,
    profunctor_unitor,
)
from sage_categories.cat.relations import Relations
from sage_categories.cat.monoidal import Actions, Cartesian, Composition, MonoidalStructures, SelfAction, TrivialAction
from sage_categories.cat.structured_objects import (
    EndofunctorAlgebras,
    Groups,
    EilenbergMoore,
    Equifier,
    Inserter,
    AdditiveGroups,
    AdditiveMagmas,
    AdditiveMonoids,
    Magmas,
    Monoids,
    MultiplicativeMagmas,
    MultiplicativeMonoids,
    PointedMagmas,
    Rings,
    Semirings,
)
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

__all__ = [
    "Actions", "Cartesian", "Composition", "MonoidalStructures", "SelfAction", "TrivialAction",
    "Adjunctions",
    "Cat",
    "Cones",
    "Equivalences",
    "Fun",
    "LimitCones",
    "Mor",
    "Op",
    "TotalCones",
    "binary_product_data",
    "curry",
    "currying",
    "evaluation",
    "pair_maps",
    "power_functor",
    "precompose",
    "product_functor",
    "transpose",
    "uncurry",
    "EndofunctorAlgebras",
    "Groups",
    "EilenbergMoore",
    "Equifier",
    "Inserter",
    "AdditiveGroups",
    "AdditiveMagmas",
    "AdditiveMonoids",
    "Magmas",
    "Monoids",
    "MultiplicativeMagmas",
    "MultiplicativeMonoids",
    "PointedMagmas",
    "Rings",
    "Semirings",
    "InitialObjects",
    "LeftUniversalArrows",
    "RightUniversalArrows",
    "TerminalObjects",
    "left_mate",
    "right_mate",
    "DiagramPresentation",
    "colimit_from_coproducts_coequalizers",
    "diagram_presentation",
    "limit_from_products_equalizers",
    "parallel_pair",
    "Elements",
    "coend",
    "end",
    "element",
    "element_projection",
    "end_to_natural_transformation",
    "hom_functor",
    "natural_transformation_diagram",
    "natural_transformation_to_end",
    "weighted_colimit",
    "weighted_colimit_desc",
    "weighted_colimit_map",
    "weighted_injection",
    "weighted_limit",
    "weighted_limit_lift",
    "weighted_limit_map",
    "weighted_projection",
    "yoneda",
    "Profunctors",
    "compose_profunctors",
    "compose_profunctor_transformations",
    "identity_profunctor",
    "profunctor_unitor",
    "Relations",
    "left_kan_adjunction",
    "right_kan_adjunction",
    "coyoneda",
    "natural_isomorphism",
]
