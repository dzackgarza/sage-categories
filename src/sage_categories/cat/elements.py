"""``Cat().ElementType``: generalized elements of a category (POL-CAT-058).

A generalized element of a category ``C`` is a functor ``T -> C``, a diagram of
shape ``T`` in ``C``.  Its stage-``1`` points are the objects of ``C`` and its
stage-``[1]`` points are the morphisms of ``C``; every ``C.ObjectType`` refines
this role at stage ``1`` and every ``C.MorphismType`` at stage ``[1]``
(``kernel/roles.py``).  ``{1, [1]}`` is the stage family of ``Cat()`` (``specs/functor.md``, "Generalized elements"): ``1``
alone does not separate functors, ``[1]`` does.
"""

from __future__ import annotations

from sage_categories.cat.category import Category
from sage_categories.cat.functors import Functor
from sage_categories.kernel.roles import CategoryPoint as KernelCategoryPoint

__all__ = ["CategoryPoint"]


class CategoryPointDeclaration(KernelCategoryPoint):
    """The local ``Cat().ElementType`` declaration."""

    def __init__(self, defining_functor: Functor) -> None:
        self._defining_functor = defining_functor

    def defining_morphism(self) -> Functor:
        return self._defining_functor

    def stage(self) -> Category:
        return self._defining_functor.domain()

    def parent(self) -> Category:
        return self._defining_functor.codomain()

    def __repr__(self) -> str:
        return f"point of {self.parent()!r} at stage {self.stage()!r}"


# The bootstrap replaces this provisional name with ``Cat().ElementType``.
CategoryPoint = CategoryPointDeclaration
