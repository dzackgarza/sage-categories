"""An exact constructed category gains all three implementation role surfaces in place."""

from sage_categories.all import Cat, Cartesian, Category, Fun, Mor, Sets
from sage_categories.algebra.abelian import presented_abelian_group
from sage_categories.cat.structured_objects import AdditiveGroups


groups = AdditiveGroups(Cartesian(Sets()))
Ab = groups.Commutative()
selected = Ab.selected_functors()
cyclic = AdditiveAbelianGroup([3])
existing = presented_abelian_group(cyclic)
point = existing.point(cyclic.gen(0))
identity = Mor(Ab)(existing, existing).one()


class ExactAbelianRoleOperations(Category):
    class ObjectType:
        def installed_object_operation(self):
            return self

    class ElementType:
        def installed_element_operation(self):
            return self

    class MorphismType:
        def installed_morphism_operation(self):
            return self

    def structure_functors(self):
        return (Fun(Ab, Ab).one(),)


Cat().implement(ExactAbelianRoleOperations)

assert Ab is groups.Commutative()
assert len(Ab.selected_functors()) == len(selected)
assert all(after is before for after, before in zip(Ab.selected_functors(), selected))
assert existing.installed_object_operation() is existing
assert point.installed_element_operation() is point
assert identity.installed_morphism_operation() is identity
assert (-point + point).datum() == cyclic.zero()
assert identity(point) is point
