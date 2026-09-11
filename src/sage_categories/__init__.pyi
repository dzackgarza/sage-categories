from sage_categories.cat.adjunctions import Adjunctions as Adjunctions
from sage_categories.cat.adjunctions import Equivalences as Equivalences
from sage_categories.cat.calculus import (
    binary_product_data as binary_product_data,
)
from sage_categories.cat.calculus import (
    curry as curry,
)
from sage_categories.cat.calculus import (
    currying as currying,
)
from sage_categories.cat.calculus import (
    evaluation as evaluation,
)
from sage_categories.cat.calculus import (
    natural_isomorphism as natural_isomorphism,
)
from sage_categories.cat.calculus import (
    pair_maps as pair_maps,
)
from sage_categories.cat.calculus import (
    power_functor as power_functor,
)
from sage_categories.cat.calculus import (
    precompose as precompose,
)
from sage_categories.cat.calculus import (
    product_functor as product_functor,
)
from sage_categories.cat.calculus import (
    transpose as transpose,
)
from sage_categories.cat.calculus import (
    uncurry as uncurry,
)
from sage_categories.cat.category import Cat as Cat
from sage_categories.cat.category import Category as Category
from sage_categories.cat.concrete import ConcreteCategory as ConcreteCategory
from sage_categories.cat.cones import cocones as Cocones
from sage_categories.cat.cones import colimit_cocones as ColimitCocones
from sage_categories.cat.cones import cones as Cones
from sage_categories.cat.cones import limit_cones as LimitCones
from sage_categories.cat.declarations import (
    NN as NN,
)
from sage_categories.cat.declarations import (
    ZZ as ZZ,
)
from sage_categories.cat.declarations import (
    MagmaObjects as MagmaObjects,
)
from sage_categories.cat.declarations import (
    MonoidObjects as MonoidObjects,
)
from sage_categories.cat.declarations import (
    Posets as Posets,
)
from sage_categories.cat.declarations import (
    RingObjects as RingObjects,
)
from sage_categories.cat.declarations import (
    SemiringObjects as SemiringObjects,
)
from sage_categories.cat.declarations import (
    Sets as Sets,
)
from sage_categories.cat.declarations import (
    TotallyOrderedSets as TotallyOrderedSets,
)
from sage_categories.cat.declarations import (
    omega as omega,
)
from sage_categories.cat.functors import Fun as Fun
from sage_categories.cat.indexed import Grothendieck as Grothendieck
from sage_categories.cat.indexed import IndexedCategories as IndexedCategories
from sage_categories.cat.kan import (
    left_kan_adjunction as left_kan_adjunction,
)
from sage_categories.cat.kan import (
    left_kan_desc as left_kan_desc,
)
from sage_categories.cat.kan import (
    left_kan_extension as left_kan_extension,
)
from sage_categories.cat.kan import (
    left_kan_unit as left_kan_unit,
)
from sage_categories.cat.kan import (
    right_kan_adjunction as right_kan_adjunction,
)
from sage_categories.cat.kan import (
    right_kan_counit as right_kan_counit,
)
from sage_categories.cat.kan import (
    right_kan_extension as right_kan_extension,
)
from sage_categories.cat.kan import (
    right_kan_lift as right_kan_lift,
)
from sage_categories.cat.limit_basis import (
    DiagramPresentation as DiagramPresentation,
)
from sage_categories.cat.limit_basis import (
    colimit_from_coproducts_coequalizers as colimit_from_coproducts_coequalizers,
)
from sage_categories.cat.limit_basis import (
    diagram_presentation as diagram_presentation,
)
from sage_categories.cat.limit_basis import (
    limit_from_products_equalizers as limit_from_products_equalizers,
)
from sage_categories.cat.limit_basis import (
    parallel_pair as parallel_pair,
)
from sage_categories.cat.modules import Modules as Modules
from sage_categories.cat.monoidal import (
    Actions as Actions,
)
from sage_categories.cat.monoidal import (
    Cartesian as Cartesian,
)
from sage_categories.cat.monoidal import (
    Composition as Composition,
)
from sage_categories.cat.monoidal import (
    MonoidalStructures as MonoidalStructures,
)
from sage_categories.cat.monoidal import (
    SelfAction as SelfAction,
)
from sage_categories.cat.monoidal import (
    TrivialAction as TrivialAction,
)
from sage_categories.cat.morphisms import Mor as Mor
from sage_categories.cat.opposites import Op as Op
from sage_categories.cat.predicates import (
    Axiom as Axiom,
)
from sage_categories.cat.predicates import (
    Decision as Decision,
)
from sage_categories.cat.predicates import (
    Predicate as Predicate,
)
from sage_categories.cat.predicates import (
    Query as Query,
)
from sage_categories.cat.predicates import (
    Unknown as Unknown,
)
from sage_categories.cat.predicates import (
    UnknownClass as UnknownClass,
)
from sage_categories.cat.predicates import (
    ask as ask,
)
from sage_categories.cat.predicates import (
    assume as assume,
)
from sage_categories.cat.predicates import (
    retract as retract,
)
from sage_categories.cat.profunctors import (
    Profunctors as Profunctors,
)
from sage_categories.cat.profunctors import (
    compose_profunctor_transformations as compose_profunctor_transformations,
)
from sage_categories.cat.profunctors import (
    compose_profunctors as compose_profunctors,
)
from sage_categories.cat.profunctors import (
    identity_profunctor as identity_profunctor,
)
from sage_categories.cat.profunctors import (
    profunctor_unitor as profunctor_unitor,
)
from sage_categories.cat.relations import Relations as Relations
from sage_categories.cat.shapes import Discrete as Discrete
from sage_categories.cat.shapes import Thin as Thin
from sage_categories.cat.structured_objects import (
    AdditiveGroups as AdditiveGroups,
)
from sage_categories.cat.structured_objects import (
    AdditiveMagmas as AdditiveMagmas,
)
from sage_categories.cat.structured_objects import (
    AdditiveMonoids as AdditiveMonoids,
)
from sage_categories.cat.structured_objects import (
    EilenbergMoore as EilenbergMoore,
)
from sage_categories.cat.structured_objects import (
    EndofunctorAlgebras as EndofunctorAlgebras,
)
from sage_categories.cat.structured_objects import (
    Equifier as Equifier,
)
from sage_categories.cat.structured_objects import (
    Groups as Groups,
)
from sage_categories.cat.structured_objects import (
    Inserter as Inserter,
)
from sage_categories.cat.structured_objects import (
    Magmas as Magmas,
)
from sage_categories.cat.structured_objects import (
    Monoids as Monoids,
)
from sage_categories.cat.structured_objects import (
    MultiplicativeMagmas as MultiplicativeMagmas,
)
from sage_categories.cat.structured_objects import (
    MultiplicativeMonoids as MultiplicativeMonoids,
)
from sage_categories.cat.structured_objects import (
    PointedMagmas as PointedMagmas,
)
from sage_categories.cat.structured_objects import (
    Rings as Rings,
)
from sage_categories.cat.structured_objects import (
    Semirings as Semirings,
)
from sage_categories.cat.total_cones import total_cones as TotalCones
from sage_categories.cat.universal_arrows import (
    InitialObjects as InitialObjects,
)
from sage_categories.cat.universal_arrows import (
    LeftUniversalArrows as LeftUniversalArrows,
)
from sage_categories.cat.universal_arrows import (
    RightUniversalArrows as RightUniversalArrows,
)
from sage_categories.cat.universal_arrows import (
    TerminalObjects as TerminalObjects,
)
from sage_categories.cat.universal_arrows import (
    left_mate as left_mate,
)
from sage_categories.cat.universal_arrows import (
    right_mate as right_mate,
)
from sage_categories.cat.weighted import (
    Elements as Elements,
)
from sage_categories.cat.weighted import (
    coend as coend,
)
from sage_categories.cat.weighted import (
    coyoneda as coyoneda,
)
from sage_categories.cat.weighted import (
    element as element,
)
from sage_categories.cat.weighted import (
    element_projection as element_projection,
)
from sage_categories.cat.weighted import (
    end as end,
)
from sage_categories.cat.weighted import (
    end_to_natural_transformation as end_to_natural_transformation,
)
from sage_categories.cat.weighted import (
    hom_functor as hom_functor,
)
from sage_categories.cat.weighted import (
    natural_transformation_diagram as natural_transformation_diagram,
)
from sage_categories.cat.weighted import (
    natural_transformation_to_end as natural_transformation_to_end,
)
from sage_categories.cat.weighted import (
    weighted_colimit as weighted_colimit,
)
from sage_categories.cat.weighted import (
    weighted_colimit_desc as weighted_colimit_desc,
)
from sage_categories.cat.weighted import (
    weighted_colimit_map as weighted_colimit_map,
)
from sage_categories.cat.weighted import (
    weighted_injection as weighted_injection,
)
from sage_categories.cat.weighted import (
    weighted_limit as weighted_limit,
)
from sage_categories.cat.weighted import (
    weighted_limit_lift as weighted_limit_lift,
)
from sage_categories.cat.weighted import (
    weighted_limit_map as weighted_limit_map,
)
from sage_categories.cat.weighted import (
    weighted_projection as weighted_projection,
)
from sage_categories.cat.weighted import (
    yoneda as yoneda,
)

__all__ = [
    "Actions",
    "Cartesian",
    "Composition",
    "MonoidalStructures",
    "SelfAction",
    "TrivialAction",
    "Adjunctions",
    "Axiom",
    "NN",
    "ZZ",
    "Cat",
    "Category",
    "Cones",
    "Cocones",
    "ColimitCocones",
    "Decision",
    "Discrete",
    "Equivalences",
    "Fun",
    "Grothendieck",
    "IndexedCategories",
    "LimitCones",
    "MagmaObjects",
    "Mor",
    "MonoidObjects",
    "Op",
    "Posets",
    "Predicate",
    "Query",
    "RingObjects",
    "SemiringObjects",
    "Sets",
    "Thin",
    "TotallyOrderedSets",
    "TotalCones",
    "Unknown",
    "UnknownClass",
    "__version__",
    "ask",
    "assume",
    "omega",
    "retract",
    "version",
    "left_kan_desc",
    "left_kan_extension",
    "left_kan_unit",
    "right_kan_counit",
    "right_kan_extension",
    "right_kan_lift",
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
    "Modules",
    "ConcreteCategory",
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
__version__: str

def version() -> str: ...
