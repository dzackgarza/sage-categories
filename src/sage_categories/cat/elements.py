"""``Cat().ElementType``: generalized elements of a category (POL-CAT-058).

A generalized element of a category ``C`` is a functor ``T -> C``, a diagram of
shape ``T`` in ``C``.  Its stage-``1`` points are the objects of ``C`` and its
stage-``[1]`` points are the morphisms of ``C``; every ``C.ObjectType`` refines
this role at stage ``1`` and every ``C.MorphismType`` at stage ``[1]``
(``kernel/roles.py``).  ``{1, [1]}`` is the stage family of ``Cat()`` (``specs/functor.md``, "Generalized elements"): ``1``
alone does not separate functors, ``[1]`` does.
"""

from __future__ import annotations

from sage_categories.kernel.roles import ElementOfObject

__all__ = ["CategoryPoint"]


class CategoryPointDeclaration(ElementOfObject):
    """The local ``Cat().ElementType`` declaration."""

    def __repr__(self) -> str:
        return f"point of {self.parent()!r} at stage {self.stage()!r}"


# The bootstrap replaces this provisional name with ``Cat().ElementType``.
CategoryPoint = CategoryPointDeclaration
