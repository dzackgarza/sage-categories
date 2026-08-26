"""Wide subcategories and cores (``specs/functor.md``, "Inclusion functors"; POL-CAT-054, POL-FUN-027, POL-MATH-037).

A wide subcategory ``W = C.WideSubcategory(P)`` retains every object of ``C`` and
restricts the morphisms to those placed in a property subcategory ``P`` of
``Mor(C)`` (nLab "wide subcategory": "a subcategory containing all the objects of
C"; Mathlib ``CategoryTheory.WideSubcategory`` for a ``MorphismProperty`` that
``IsMultiplicative``; both inspected 2026-08-27).  That ``P`` contains the
identities and is closed under composition is the writer's trusted declaration
(POL-MATH-037): ``W.identity_morphism`` returns the identity of ``C`` and
``W.compose_morphisms`` returns the composite of ``C`` refined into ``P``.  The
objects and morphisms of ``W`` are the very values of ``C``: an object is a member
by ``C``'s membership proposition, a morphism of ``Mor(W)`` by placement in ``P``,
and ``Mor(W)(A, B)(data)`` constructs through the trusted constructor
``Mor(C)(A, B).P()``.

Its one selected structural functor is the identity-on-value inclusion
``Fun(W, C).Faithful().inclusion()`` (Mathlib ``wideSubcategory.faithful``;
inspected 2026-08-27).  It is not full unless ``P`` is all of ``Mor(C)``, so ``W``
owns its own constructions, identities, and composites rather than inheriting them
definitionally from ``C`` (``Category.has_full_ambient``).

``C.Core()`` is the wide subcategory on ``Mor(C).Isomorphisms()``: "the maximal
sub-groupoid of C: the subcategory consisting of all objects of C but with
morphisms only the isomorphisms of C" (nLab "core"; Mathlib ``CategoryTheory.Core``
with ``Core.inclusion``; inspected 2026-08-27).

The inhabitation of ``Mor(W)(A, B)``, or of a narrowing of it, is decided as the
inhabitation of ``Mor(C)(A, B).P()`` narrowed the same way: the hom category of
``W`` is by definition that full subcategory of ``Mor(C)(A, B)``.
"""

from __future__ import annotations

from sage_categories.cat.category import Category
from sage_categories.cat.functors import Fun, Functor
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.kernel.compiler import empty_local_role
from sage_categories.kernel.decisions import Decision
from sage_categories.kernel.predicates import Proposition, ask
from sage_categories.kernel.roles import CategoryPoint, MorphismOfCategory, ObjectOfCategory, Role

__all__ = ["WideMorphismCategory", "WideSubcategory", "wide_subcategory"]


class WideMorphismCategory(MorphismCategory):
    """``Mor(W)``: a morphism of ``C`` is a member exactly when it is placed in ``P``."""

    def membership_proposition(self, candidate: CategoryPoint) -> Proposition:
        return self._base.morphism_property().membership_proposition(candidate)


class WideSubcategory[**MorphismData, **TwoMorphismData](Category[MorphismData, TwoMorphismData]):
    """The wide subcategory of ``C`` on the morphisms of a multiplicative property subcategory ``P`` of ``Mor(C)``."""

    def __init__(self, ambient: Category[MorphismData, TwoMorphismData], morphism_property: Category) -> None:
        assert morphism_property.narrowing_base() is ambient.morphism_category(1), f"{morphism_property!r} is not a property subcategory of {ambient.morphism_category(1)!r}"
        self._ambient = ambient
        self._morphism_property = morphism_property
        super().__init__()

    def morphism_property(self) -> Category:
        """The property subcategory of ``Mor(C)`` whose objects are the morphisms of this subcategory."""
        return self._morphism_property

    def local_role_class(self, role: Role) -> type[CategoryPoint]:
        return empty_local_role(self, role)

    def structure_functors(self) -> tuple[Functor, ...]:
        return (Fun(self, self._ambient).Faithful().inclusion(),)

    def morphism_category_type(self) -> type[WideMorphismCategory]:
        return WideMorphismCategory

    def classical_stages(self) -> tuple[ObjectOfCategory, ...]:
        """Every object of ``C`` is an object of ``W``, so the stages are those of ``C``."""
        return self._ambient.classical_stages()

    def membership_proposition(self, candidate: CategoryPoint) -> Proposition:
        return self._ambient.membership_proposition(candidate)

    # -- morphisms: the values of ``C`` placed in ``P`` (POL-MATH-037) --------------------

    def construct_morphism(self, domain: ObjectOfCategory, codomain: ObjectOfCategory, *args: MorphismData.args, **kwargs: MorphismData.kwargs) -> MorphismOfCategory:
        """``Mor(W)(A, B)(data)``: the trusted constructor ``Mor(C)(A, B).P()(data)``."""
        return self._morphism_property(domain, codomain)(*args, **kwargs)

    def identity_morphism(self, member_object: ObjectOfCategory) -> MorphismOfCategory:
        """The identity of ``C``, which ``P`` contains by declaration."""
        return self._morphism_property(self._ambient.identity_morphism(member_object))

    def compose_morphisms(self, second: MorphismOfCategory, first: MorphismOfCategory) -> MorphismOfCategory:
        """The composite in ``C``, which ``P`` contains by declaration."""
        return self._morphism_property(self._ambient.compose_morphisms(second, first))

    def inverse_morphism(self, morphism: MorphismOfCategory) -> MorphismOfCategory:
        return self._ambient.inverse_morphism(morphism)

    def retain_inverses(self, forward: MorphismOfCategory, backward: MorphismOfCategory) -> None:
        self._ambient.retain_inverses(forward, backward)

    def hom_inhabited(self, hom_category: Category) -> Decision:
        """``Mor(W)(A, B)`` narrowed by roots is inhabited exactly when ``Mor(C)(A, B).P()`` narrowed by the same roots is."""
        base = hom_category.narrowing_base()
        target = self._ambient.morphism_category(1)(base.domain(), base.codomain()).property_subcategory(self._morphism_property)
        for root in hom_category.narrowing_roots():
            target = target.property_subcategory(root)
        return ask(target.is_inhabited())

    def __repr__(self) -> str:
        if self._morphism_property is self._ambient.morphism_category(1).Isomorphisms():
            return f"{self._ambient!r}.Core()"
        return f"{self._ambient!r}.WideSubcategory({self._morphism_property!r})"


def wide_subcategory(ambient: Category, morphism_property: Category) -> WideSubcategory:
    """``C.WideSubcategory(P)``: constructed once per ``P`` by ``Category.WideSubcategory``."""
    return WideSubcategory(ambient, morphism_property)
