"""``Cat().ElementType``: generalized elements of a category (POL-CAT-058).

A generalized element of a category ``C`` is a functor ``T -> C``, a diagram of
shape ``T`` in ``C``.  Its stage-``1`` points are the objects of ``C`` and its
stage-``[1]`` points are the morphisms of ``C``; every ``C.ObjectType`` refines
this role at stage ``1`` and every ``C.MorphismType`` at stage ``[1]``
(``kernel/roles.py``).  ``{1, [1]}`` is the stage family of ``Cat()`` (``specs/functor.md``, "Generalized elements"): ``1``
alone does not separate functors, ``[1]`` does.
"""

from __future__ import annotations

from sage_categories.kernel.roles import CategoryPointKernel, ObjectOfCategory

__all__ = ["CategoryPoint"]


class CategoryPointDeclaration(CategoryPointKernel):
    """The local ``Cat().ElementType`` declaration."""

    def __mul__(self, other: ObjectOfCategory) -> ObjectOfCategory:
        """``X * Y``: the product in their category."""
        category = self.category()
        assert category is other.category(), "object product operands must have one category"
        return category.Products()((self, other))

    def __add__(self, other: ObjectOfCategory) -> ObjectOfCategory:
        """``X + Y``: the coproduct in their category."""
        category = self.category()
        assert category is other.category(), "object coproduct operands must have one category"
        return category.Coproducts()((self, other))

    def __matmul__(self, other: ObjectOfCategory) -> ObjectOfCategory:
        """``X @ Y``: the biproduct in their category."""
        category = self.category()
        assert category is other.category(), "object biproduct operands must have one category"
        return category.biproduct(self, other)

    def __pow__(self, exponent: ObjectOfCategory) -> ObjectOfCategory:
        """``Y ** X``: the exponential object in their category."""
        category = self.category()
        assert category is exponent.category(), "object exponential operands must have one category"
        return category.exponential(exponent, self)

    def __repr__(self) -> str:
        return f"point of {self.parent()!r} at stage {self.stage()!r}"


# The bootstrap replaces this provisional name with ``Cat().ElementType``.
CategoryPoint = CategoryPointDeclaration
