"""The positive integers as the named set ``NN`` (POL-SET-032)."""

from collections.abc import Hashable

from sympy import Q

from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.declarations import NN, omega
from sage_categories.cat.functors import Cat, Fun, Functor
from sage_categories.cat.predicates import Proposition
from sage_categories.cat.shapes import ThinCategory
from sage_categories.sets.finite import MembershipRule, Sets


def positive_integer(value: Hashable) -> Proposition:
    """Membership in ``NN = {n in ZZ : n > 0}``."""
    return Q.integer(value) & Q.positive(value)


class PositiveIntegersCategory(Category):
    """The discrete category of positive integers, placed as an object of Sets."""

    class ObjectType:
        pass

    class ElementType:
        pass

    class MorphismType:
        pass

    def set_presentation(self) -> MembershipRule:
        return positive_integer

    def structure_functors(self) -> tuple[Functor, ...]:
        return (Fun(NN, NN).one(), Sets.Point())


Cat().implement(PositiveIntegersCategory)


def natural_order(first: CategoryOfCategories.ElementType, second: CategoryOfCategories.ElementType) -> bool:
    """The natural order on the positive-integer points underlying ``omega``."""
    return first.datum() <= second.datum()


class SequentialCategory(ThinCategory):
    """``omega = Thin(NN, <=)`` with the owned positive integers as stages."""

    def __init__(self) -> None:
        super().__init__(NN, natural_order)

    def structure_functors(self) -> tuple[Functor, ...]:
        return (Fun(omega, omega).one(),)


Cat().implement(SequentialCategory)
