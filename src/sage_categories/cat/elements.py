"""``Cat().ElementType``: points ``* -> C`` of a category (POL-CAT-058).

A point of a category ``C`` is a functor from the terminal category, and its value is an
object of ``C``.  A morphism of ``C`` is an object of ``Mor(C)`` and so a point
``* -> Mor(C)``, which is why every ``C.ObjectType`` and every ``C.MorphismType`` refines
this one role (``kernel/roles.py``, ``specs/functor.md``, "Compiled implementation
classes").  A functor ``T -> C`` with nonterminal ``T`` is a generalized element and is an
object of ``Fun(T, C)``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sage_categories.kernel.roles import CategoryPoint, CategoryPointKernel, ObjectOfCategory

if TYPE_CHECKING:
    from sage_categories.cat.category import Category

__all__ = ["CategoryPoint"]


def _shared_category(first: ObjectOfCategory, second: ObjectOfCategory) -> Category:
    """The narrowest category containing both operands, which owns their construction (POL-CAT-088).

    An object refined into ``C.P()`` and an object of ``C`` are both objects of ``C``,
    so their construction is the one in ``C``.  Identity of the two strongest recorded
    placements is an implementation fact, not this precondition (POL-CAT-073).  Operands
    with no common category, such as a set and a category, fail the assertion.  No
    operator casts an operand into a product category: an external pair is written
    ``(C * D)((X, Y))``.
    """
    from sage_categories.kernel.refinement import common_ancestor

    shared = common_ancestor(first.category(), second.category())
    assert shared is not None, (
        f"{first!r} in {first.category()!r} and {second!r} in {second.category()!r} "
        f"have no least common category along subcategory monomorphisms"
    )
    return shared


class CategoryPointDeclaration(CategoryPointKernel):
    """The local ``Cat().ElementType`` declaration."""

    def __mul__(self, other: ObjectOfCategory) -> ObjectOfCategory:
        """``X * Y``: the product in the least category receiving both."""
        return _shared_category(self, other).Products()((self, other))

    def __add__(self, other: ObjectOfCategory) -> ObjectOfCategory:
        """``X + Y``: the coproduct in the least category receiving both."""
        return _shared_category(self, other).Coproducts()((self, other))

    def __matmul__(self, other: ObjectOfCategory) -> ObjectOfCategory:
        """``X @ Y``: the biproduct in the least category receiving both."""
        return _shared_category(self, other).biproduct(self, other)

    def __pow__(self, exponent: ObjectOfCategory) -> ObjectOfCategory:
        """``Y ** X``: the exponential object in the least category receiving both."""
        return _shared_category(self, exponent).exponential(exponent, self)

    def __repr__(self) -> str:
        return f"point of {self.parent()!r}"
