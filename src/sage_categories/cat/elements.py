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
from sage_categories.kernel.roles import ElementOfObject

__all__ = ["CategoryPoint"]


class CategoryPoint(ElementOfObject):
    """A functor ``T -> C`` regarded as a point of ``C`` at stage ``T``.

    A generalized element of a category is a generalized element like any other, so this
    is ``ElementOfObject`` with the stage and parent it already defines: the domain and
    codomain of the defining functor.
    """

    def __repr__(self) -> str:
        return f"point of {self.parent()!r} at stage {self.stage()!r}"
