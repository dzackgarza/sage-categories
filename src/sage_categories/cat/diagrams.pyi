from collections.abc import Callable, Hashable
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.functors import Functor, FunctorCategory, NaturalTransformation
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.shapes import DiscreteCategory
__all__ = ['evaluation', 'constant', 'diagonal', 'from_object_rule', 'sequence_position', 'from_sequence', 'square_set', 'square_at', 'codomain_lift', 'domain_lift', 'pointwise_limit', 'pointwise_colimit']
type Datum = Hashable
type _PointwiseLimitMediator = Callable[[NaturalTransformation], NaturalTransformation]

def evaluation(functors: FunctorCategory, vertex: CategoryOfCategories.ElementType) -> Functor:
    ...

def constant(functors: FunctorCategory, value: CategoryOfCategories.ElementType) -> Functor:
    ...

def diagonal(functors: FunctorCategory) -> Functor:
    ...

def from_object_rule(functors: FunctorCategory, rule: Callable[[DiscreteCategory.ObjectType], CategoryOfCategories.ElementType]) -> Functor:
    ...

def sequence_position(vertex: DiscreteCategory.ObjectType) -> int:
    ...

def from_sequence(ambient: Category, sequence: tuple[CategoryOfCategories.ElementType, ...]) -> Functor:
    ...

def square_set(functors: FunctorCategory) -> CategoryOfCategories.ElementType:
    ...

def square_at(functors: FunctorCategory, point: CategoryOfCategories.ElementType) -> NaturalTransformation:
    ...

def codomain_lift(functors: FunctorCategory, morphism: MorphismCategory.ObjectType, member_object: MorphismCategory.ObjectType) -> NaturalTransformation:
    ...

def domain_lift(functors: FunctorCategory, morphism: MorphismCategory.ObjectType, member_object: MorphismCategory.ObjectType) -> NaturalTransformation:
    ...

def pointwise_limit(diagram: Functor) -> CategoryOfCategories.ElementType:
    ...

def pointwise_colimit(diagram: Functor) -> CategoryOfCategories.ElementType:
    ...
