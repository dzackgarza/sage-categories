"""``Cat().Point(X)``, the one-object category on a distinguished object (POL-CAT-083).

``{X}`` has one object, ``X``, and one morphism, ``1_X``.  Its point functors are the
faithful inclusions into the categories that already have ``X`` among their objects
(``specs/functor.md``, "Point categories and point functors").  ``{X}`` has one hom
category, so every functor out of it is faithful.

``Cat().Point(X)`` is not ``Cat().Terminal()``: the terminal category's sole object is an
abstract vertex, while ``{X}``'s sole object is ``X`` itself.  ``Category.point_functor``
is a third thing again, the stage-``1`` generalized element ``1 -> C`` selecting an
object; ``{X}`` uses it below, but is not it.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sage_categories.cat.category import Category
from sage_categories.kernel.caches import MonoDict
from sage_categories.kernel.refinement import refine
from sage_categories.kernel.roles import ElementOfObject, MorphismOfCategory, ObjectOfCategory

if TYPE_CHECKING:
    from sage_categories.cat.functors import Functor

__all__ = ["PointCategory"]


class PointCategory(Category[[], []]):
    """``{X}``: the one-object category whose sole object is ``X`` and whose sole morphism is ``1_X``."""

    class ObjectType(ObjectOfCategory):
        """The sole object ``X``; ``{X}`` declares no operation of its own."""

    class ElementType(ElementOfObject):
        """A generalized element of ``X``.

        For a category ``X = C`` these are the objects of ``C`` at stage ``1`` and the
        morphisms of ``C`` at stage ``[1]`` (``specs/functor.md``, "The level shift").
        """

    class MorphismType(MorphismOfCategory):
        """The sole morphism ``1_X``."""

    def __init__(self, member: ObjectOfCategory, targets: tuple[Category, ...]) -> None:
        self._member = member
        self._targets = targets
        self._elements: MonoDict = MonoDict()
        super().__init__()
        # ``{X}`` is the strongest established placement of ``X``: it is a subcategory of
        # ``X``'s own category, and its object surface is what a point functor supplies
        # to ``X`` (``specs/functor.md``, "The level shift", row 1).
        refine(member, self)

    def structure_functors(self) -> tuple[Functor, ...]:
        """The inclusion into ``Cat()``, then one point functor per target category (POL-FUN-027).

        ``{X}`` is a subcategory of ``Cat()`` on one object and one morphism, so its
        inclusion there comes first and is its ambient.  Each further entry states one
        more placement of ``X`` as an object of that target.
        """
        from sage_categories.cat.functors import Fun

        universe = self._member.category().category()
        return (
            Fun(self, universe).Faithful().inclusion(),
            *(Fun(self, target).Faithful().inclusion() for target in self._targets),
        )

    def element_from_defining_morphism(self, defining_morphism: Functor) -> ElementOfObject:
        """The generalized element of the sole object named by a functor ``T -> X``, retained by identity.

        Not the ambient's: ``{X}``'s elements are the generalized elements of ``X``, named
        by functors into ``X``, while ``{X}``'s own only morphism is ``1_X``.

        One value per defining functor.  Two selected routes to this node must produce
        the same image, and a fresh element each call would make them differ
        (POL-CAT-012); a morphism of ``X`` placed in several property subcategories is
        reached by exactly such routes.
        """
        assert defining_morphism.codomain() is self._member, (
            f"{defining_morphism!r} does not name a generalized element of {self._member!r}"
        )
        if defining_morphism not in self._elements:
            self._elements[defining_morphism] = self.ElementType(defining_morphism)
        return self._elements[defining_morphism]

    def member(self) -> ObjectOfCategory:
        """The distinguished object."""
        return self._member

    def __call__(self) -> ObjectOfCategory:
        """The sole object, retained by identity."""
        return self._member

    def __repr__(self) -> str:
        return f"{{{self._member!r}}}"
