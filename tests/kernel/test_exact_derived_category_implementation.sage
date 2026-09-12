"""An exact derived category receives an implementation without changing its identity."""

from sage.groups.additive_abelian.additive_abelian_group import AdditiveAbelianGroup

from sage_categories.algebra.abelian import presented_abelian_group
from sage_categories.cat.category import Category
from sage_categories.cat.functors import Cat, Fun
from sage_categories.cat.monoidal import Cartesian
from sage_categories.cat.morphisms import Mor
from sage_categories.cat.predicates import ask
from sage_categories.cat.structured_objects import AdditiveGroups
from sage_categories.sets.finite import Sets


def test_exact_derived_category_implementation() -> None:
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
    forgotten_existing = forget.on_object(existing)
    selected = Ab.selected_functors()

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
    assert len(Ab.selected_functors()) == len(selected)
    assert all(after is before for after, before in zip(Ab.selected_functors(), selected))
    assert Ab.forgetful().on_object(existing) is forgotten_existing
    assert Mor(Ab)(existing, existing).one() is identity


test_exact_derived_category_implementation()
