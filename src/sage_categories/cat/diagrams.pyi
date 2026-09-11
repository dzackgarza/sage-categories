from collections.abc import Callable

from sage_categories.cat.category import Cat as Cat
from sage_categories.cat.category import Category as Category
from sage_categories.cat.category import CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.cones import (
    LimitConesCategory as LimitConesCategory,
)
from sage_categories.cat.cones import (
    cocone as cocone,
)
from sage_categories.cat.cones import (
    cocone_apex as cocone_apex,
)
from sage_categories.cat.cones import (
    cone as cone,
)
from sage_categories.cat.cones import (
    cone_apex as cone_apex,
)
from sage_categories.cat.cones import (
    cones as cones,
)
from sage_categories.cat.declarations import Sets as Sets
from sage_categories.cat.dual_functor_categories import dual_functor_category_equivalence as dual_functor_category_equivalence
from sage_categories.cat.functors import Fun as Fun
from sage_categories.cat.functors import Functor as Functor
from sage_categories.cat.functors import FunctorCategory as FunctorCategory
from sage_categories.cat.functors import NaturalTransformation as NaturalTransformation
from sage_categories.cat.morphisms import MorphismCategory as MorphismCategory
from sage_categories.cat.morphisms import endpoints as endpoints
from sage_categories.cat.opposites import opposite_morphism as opposite_morphism
from sage_categories.cat.predicates import Decision as Decision
from sage_categories.cat.predicates import Unknown as Unknown
from sage_categories.cat.predicates import ask as ask
from sage_categories.cat.shapes import DiscreteCategory as DiscreteCategory
from sage_categories.kernel.retention import identity_key as identity_key
from sage_categories.kernel.sage_runtime import MonoDict as MonoDict
from sage_categories.kernel.sage_runtime import cached_function as cached_function

__all__ = [
    "codomain_lift",
    "constant",
    "diagonal",
    "domain_lift",
    "evaluation",
    "from_object_rule",
    "from_sequence",
    "pointwise_colimit",
    "pointwise_limit",
    "sequence_position",
    "square_at",
    "square_set",
]

def evaluation(functors: FunctorCategory, vertex: CategoryOfCategories.ElementType) -> Functor: ...
def constant(functors: FunctorCategory, value: CategoryOfCategories.ElementType) -> Functor: ...
def diagonal(functors: FunctorCategory) -> Functor: ...
def from_object_rule(functors: FunctorCategory, rule: Callable[[DiscreteCategory.ObjectType], CategoryOfCategories.ElementType]) -> Functor: ...
def sequence_position(vertex: DiscreteCategory.ObjectType) -> int: ...
def from_sequence(ambient: Category, sequence: tuple[CategoryOfCategories.ElementType, ...]) -> Functor: ...
def square_set(functors: FunctorCategory) -> CategoryOfCategories.ElementType: ...
def square_at(functors: FunctorCategory, point: CategoryOfCategories.ElementType) -> NaturalTransformation: ...
def codomain_lift(functors: FunctorCategory, morphism: MorphismCategory.ObjectType, member_object: MorphismCategory.ObjectType) -> NaturalTransformation: ...
def domain_lift(functors: FunctorCategory, morphism: MorphismCategory.ObjectType, member_object: MorphismCategory.ObjectType) -> NaturalTransformation: ...
def pointwise_limit(diagram: Functor) -> CategoryOfCategories.ElementType: ...
def pointwise_colimit(diagram: Functor) -> CategoryOfCategories.ElementType: ...

type _PointwiseLimitMediator = Callable[[NaturalTransformation], NaturalTransformation]

def cospan_diagram(base: Category, first: MorphismCategory.ObjectType, second: MorphismCategory.ObjectType) -> Functor: ...
def _pointwise_limit_data(diagram: Functor) -> tuple[Functor, NaturalTransformation, _PointwiseLimitMediator]: ...
