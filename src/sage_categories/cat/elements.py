"""``Cat().ElementType``: generalized elements of a category (POL-CAT-058).

A generalized element of a category ``C`` is a functor ``T -> C``, a diagram of
shape ``T`` in ``C``.  Its stage-``1`` points are the objects of ``C`` and its
stage-``[1]`` points are the morphisms of ``C``; every ``C.ObjectType`` refines
this role at stage ``1`` and every ``C.MorphismType`` at stage ``[1]``
(``kernel/roles.py``).  ``{1, [1]}`` is the stage family of ``Cat()`` (``specs/functor.md``, "Generalized elements"): ``1``
alone does not separate functors, ``[1]`` does.
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
        f"have no least common category along retained inclusions"
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
        return f"point of {self.parent()!r} at stage {self.stage()!r}"
