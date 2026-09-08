"""An exact derived category receives an implementation without changing its identity."""

from sage_categories.all import Cat, Cartesian, Category, Fun, Mor, Sets, ask
from sage_categories.algebra import presented_abelian_group
from sage_categories.cat.structured_objects import AdditiveGroups

groups = AdditiveGroups(Cartesian(Sets()))
Ab = groups.Commutative()
inclusion = Ab.subcategory_monomorphism()
monoids = groups.named_monoids()
magmas = monoids.named_magmas()
forget = magmas.to_carrier() * monoids.to_named_magmas() * groups.to_named_monoids() * inclusion
cyclic = AdditiveAbelianGroup([3])
existing = presented_abelian_group(cyclic)
point = existing.point(cyclic.gen(0))
identity = Mor(Ab)(existing, existing).one()


class AbelianOperations(Category):
    class ObjectType:
        pass

    class ElementType:
        pass

    class MorphismType:
        pass

    def forgetful(self):
        return forget

    def structure_functors(self):
        return (Fun(Ab, Ab).one(),)


Cat().implement(AbelianOperations)
assert Ab is groups.Commutative()
assert Ab.forgetful() is forget
assert Ab.subcategory_monomorphism() is inclusion
assert existing in Ab
assert ask(existing.is_commutative()) is True
assert point.parent() is existing
assert identity(point) is point
assert (-point + point).datum() == cyclic.zero()
assert Ab.forgetful().on_object(existing) is forget.on_object(existing)
assert Mor(Ab)(existing, existing).one() is identity
