from collections.abc import Callable
from dataclasses import dataclass
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.cones import LimitConesCategory
from sage_categories.cat.functors import Functor, NaturalTransformation
from sage_categories.cat.morphisms import MorphismCategory
__all__ = ['DiagramPresentation', 'diagram_presentation', 'parallel_pair', 'limit_from_products_equalizers', 'colimit_from_coproducts_coequalizers']

@dataclass(frozen=True)
class DiagramPresentation:
    vertices: Functor
    source: Functor
    target: Functor
    arrows: NaturalTransformation

def diagram_presentation(shape: Category) -> DiagramPresentation:
    ...

def parallel_pair(first: MorphismCategory.ObjectType, second: MorphismCategory.ObjectType) -> Functor:
    ...
type LimitChoice = Callable[[Functor], LimitConesCategory.ObjectType]

def limit_from_products_equalizers(diagram: Functor) -> CategoryOfCategories.ElementType:
    ...

def colimit_from_coproducts_coequalizers(diagram: Functor) -> CategoryOfCategories.ElementType:
    ...
