from collections.abc import Callable as Callable, Hashable
from sage_categories.cat.calculus import binary_product_data as binary_product_data
from sage_categories.cat.category import CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.declarations import Sets as Sets
from sage_categories.cat.monoidal import Cartesian as Cartesian
from sage_categories.cat.morphisms import Mor as Mor, MorphismCategory as MorphismCategory
from sage_categories.cat.structured_objects import AdditiveGroups as AdditiveGroups, AdditiveMonoids as AdditiveMonoids, Groups as Groups, Magmas as Magmas, Monoids as Monoids, MultiplicativeMonoids as MultiplicativeMonoids, PointedMagmas as PointedMagmas, Rings as Rings, Semirings as Semirings
from sage_categories.kernel.refinement import refine as refine

def certified_commutative_ring(carrier: CategoryOfCategories.ElementType, addition_rule: Callable[[tuple[Hashable, Hashable]], Hashable], multiplication_rule: Callable[[tuple[Hashable, Hashable]], Hashable], zero_value: Hashable, one_value: Hashable) -> CategoryOfCategories.ElementType:
    ...
