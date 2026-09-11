from collections.abc import Callable, Hashable

from sage_categories.cat.calculus import binary_product_data as binary_product_data
from sage_categories.cat.category import CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.declarations import Sets as Sets
from sage_categories.cat.monoidal import Cartesian as Cartesian
from sage_categories.cat.morphisms import Mor as Mor
from sage_categories.cat.morphisms import MorphismCategory as MorphismCategory
from sage_categories.cat.structured_objects import (
    AdditiveGroups as AdditiveGroups,
)
from sage_categories.cat.structured_objects import (
    AdditiveMonoids as AdditiveMonoids,
)
from sage_categories.cat.structured_objects import (
    Groups as Groups,
)
from sage_categories.cat.structured_objects import (
    Magmas as Magmas,
)
from sage_categories.cat.structured_objects import (
    Monoids as Monoids,
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
from sage_categories.kernel.refinement import refine as refine

def certified_commutative_ring(
    carrier: CategoryOfCategories.ElementType,
    addition_rule: Callable[[tuple[Hashable, Hashable]], Hashable],
    multiplication_rule: Callable[[tuple[Hashable, Hashable]], Hashable],
    zero_value: Hashable,
    one_value: Hashable,
) -> CategoryOfCategories.ElementType: ...
