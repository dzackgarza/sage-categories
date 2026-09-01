from sage.misc.cachefunc import cached_method
from sage_categories.cat.category import Category
from sage_categories.cat.functors import Functor
from sage_categories.cat.predicates import AppliedPredicate, Decision
from sage_categories.cat.properties import PropertySubcategory
from sage_categories.posets.category import Poset, PosetElement
from sage_categories.sets.cardinals import CardinalObject
from sage_categories.sets.maps import Rule
__all__ = ['FinitePosetsCategory']

class FinitePosetObject:

    def has_bottom(self) -> AppliedPredicate:
        ...

    def has_top(self) -> AppliedPredicate:
        ...

    def is_ranked(self) -> AppliedPredicate:
        ...

    def is_graded(self) -> AppliedPredicate:
        ...

    def height(self) -> CardinalObject:
        ...

    def width(self) -> CardinalObject:
        ...

    def covers(self, lower: PosetElement, upper: PosetElement) -> Decision:
        ...

    def lower_covers(self, member: PosetElement) -> Poset:
        ...

    def upper_covers(self, member: PosetElement) -> Poset:
        ...

    def minimal_elements(self) -> Poset:
        ...

    def maximal_elements(self) -> Poset:
        ...

    def common_lower_covers(self, members: Poset) -> Poset:
        ...

    def common_upper_covers(self, members: Poset) -> Poset:
        ...

    def open_interval(self, lower: PosetElement, upper: PosetElement) -> Poset:
        ...

    def closed_interval(self, lower: PosetElement, upper: PosetElement) -> Poset:
        ...

    def principal_order_ideal(self, member: PosetElement) -> Poset:
        ...

    def principal_order_filter(self, member: PosetElement) -> Poset:
        ...

    def order_ideal(self, members: Poset) -> Poset:
        ...

    def order_filter(self, members: Poset) -> Poset:
        ...

    def is_chain_of_poset(self, members: Poset) -> Decision:
        ...

    def is_antichain_of_poset(self, members: Poset) -> Decision:
        ...

    def linear_extension(self) -> Poset:
        ...

class WithBottomObject:

    def bottom(self) -> PosetElement:
        ...

class WithTopObject:

    def top(self) -> PosetElement:
        ...

class RankedObject:

    def rank(self) -> CardinalObject:
        ...

    def rank_of_element(self, member: PosetElement) -> CardinalObject:
        ...

    def level_sets(self) -> Functor:
        ...

class GradedObject:
    ...

class WithBottomCategory(PropertySubcategory[[Rule], []]):
    ObjectType = WithBottomObject

    class ElementType:
        ...

    class MorphismType:
        ...

class WithTopCategory(PropertySubcategory[[Rule], []]):
    ObjectType = WithTopObject

    class ElementType:
        ...

    class MorphismType:
        ...

class RankedCategory(PropertySubcategory[[Rule], []]):
    ObjectType = RankedObject

    class ElementType:
        ...

    class MorphismType:
        ...

class GradedCategory(PropertySubcategory[[Rule], []]):
    ObjectType = GradedObject

    class ElementType:
        ...

    class MorphismType:
        ...

class FinitePosetsCategory(PropertySubcategory[[Rule], []]):
    ObjectType = FinitePosetObject

    class ElementType:
        ...

    class MorphismType:
        ...

    def __init__(self, ambient: Category[[Rule], []], name: str, implications: tuple[Category, ...]) -> None:
        ...

    @cached_method
    def underlying_finite_set_functor(self) -> Functor:
        ...

    def structure_functors(self) -> tuple[Functor, ...]:
        ...

    def __call__(self, poset: Poset) -> Poset:
        ...

    def TotallyOrdered(self) -> Category[[Rule], []]:
        ...

    def WithBottom(self) -> Category[[Rule], []]:
        ...

    def WithTop(self) -> Category[[Rule], []]:
        ...

    def Ranked(self) -> Category[[Rule], []]:
        ...

    def Graded(self) -> Category[[Rule], []]:
        ...
