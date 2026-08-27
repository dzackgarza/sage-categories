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

from sage_categories.kernel.roles import CategoryPointKernel, ObjectOfCategory

if TYPE_CHECKING:
    from sage_categories.cat.category import Category

__all__ = ["CategoryPoint"]


def _shared_category(first: ObjectOfCategory, second: ObjectOfCategory) -> Category:
    """The one category that owns a binary construction on both operands (POL-CAT-088).

    Both operands are objects of the least category receiving both, so that category
    owns the construction.  It is the category of both operands when their placements
    agree, and the least category receiving both otherwise.  No operator casts an
    operand into a product category: an external pair is written ``(C * D)((X, Y))``.
    """
    from sage_categories.kernel.refinement import common_ancestor

    return common_ancestor(first.category(), second.category())


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


# The bootstrap replaces this provisional name with ``Cat().ElementType``.
CategoryPoint = CategoryPointDeclaration
