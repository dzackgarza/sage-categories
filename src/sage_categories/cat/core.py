"""``Groupoids()``, the core functor, and its inclusion (D99; ``specs/functor.md``, "The core functor").

``Groupoids()`` is a declared point of ``Cat()``, and this foundation needs only that
declaration.  The one arrow the documents state is the inclusion ``U: Groupoids() ->
Cat()``, and it is the whole content here: a groupoid is a category, a functor between
groupoids is a functor, and a category isomorphic in ``Cat()`` to a groupoid is one, which
is the isofibration condition placement follows (POL-FUN-036).  No groupoid theory stands
behind it, so a category is a groupoid here exactly when it entered ``Groupoids()``, and
``Core`` is what puts one there.

``Core.on_object(C)``, written ``C.Core()``, has the objects of ``C``, and its morphisms
are the isomorphisms of ``C``: "the maximal sub-groupoid of C: the subcategory consisting
of all objects of C but with morphisms only the isomorphisms of C" (nLab "core"; Mathlib
``CategoryTheory.Core`` with ``Core.inclusion``; both inspected 2026-08-27).  Those are
the very values of ``C``: an object is a member by ``C``'s membership proposition, a
morphism by placement in ``Mor(C).Isomorphisms()``, and ``Mor(C.Core())(A, B)(data)``
constructs through the trusted constructor ``Mor(C)(A, B).Isomorphisms()``
(POL-MATH-037).  ``C.Core()`` is not ``Mor(C).Isomorphisms()``: that category has the
isomorphisms of ``C`` as its objects and lives one categorical level higher.

For ``F: C -> D``, ``Core.on_morphism(F)`` restricts ``F`` to those isomorphisms.  A
functor carries an isomorphism to an isomorphism, with ``F(f⁻¹)`` its inverse (Mathlib
``CategoryTheory.Functor.mapIso``; inspected 2026-08-29), and retaining that pair is what
places the image in ``Mor(D).Isomorphisms()``.

``epsilon_C: U(C.Core()) -> C`` is the component at ``C`` of the natural inclusion
``epsilon: U * Core => End_Cat(Cat()).one()``.  The core selects that same monomorphism as
its one structural functor, so the component and the structural inclusion are one functor.
Its image is every isomorphism of ``C``, so an isomorphism of ``C`` with an endpoint in the
core is one of the core: here, unlike a general subcategory on a multiplicative property,
the isofibration condition holds.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sage_categories.cat.category import Assignment, Category, OnMorphism, OnObject
from sage_categories.cat.declarations import Groupoids
from sage_categories.cat.functors import Cat, Fun, Functor, NaturalTransformation
from sage_categories.cat.morphisms import FixedEndpointCategory, MorphismCategory
from sage_categories.kernel.decisions import Decision
from sage_categories.kernel.predicates import Proposition, ask
from sage_categories.kernel.refinement import refine

if TYPE_CHECKING:
    from sage_categories.cat.category import CategoryOfCategories

__all__ = ["Core", "CoreCategory", "CoreFixedEndpointCategory", "CoreMorphismCategory", "GroupoidsCategory", "U", "epsilon"]


class GroupoidsCategory(Category[[OnObject, OnMorphism], [Assignment]]):
    """``Groupoids()``: the declared point of ``Cat()`` whose one stated arrow is its inclusion."""

    _implements = "Groupoids"

    # A groupoid is a category, a point of a groupoid is an object of it, and a functor
    # between groupoids is a functor.  Groupoid theory would add its mathematics to the
    # three bodies below and the documents state none, so all three are empty
    # (POL-CAT-057).  That the objects here are categories is carried by ``U``, the
    # inclusion this category selects: a selected structure functor is what makes this
    # class inherit ``Cat()``'s compiled object class (POL-CAT-053, POL-KERNEL-028).
    class ObjectType:
        """A groupoid, which is a category."""

    class ElementType:
        """A point ``* -> G`` of a groupoid, whose value is an object of it."""

    class MorphismType:
        """A functor between two groupoids."""

    def structure_functors(self) -> tuple[Functor, ...]:
        return (Fun(self, Cat()).Monomorphisms().Isofibrations()(),)

    def __repr__(self) -> str:
        return "Groupoids"


class CoreCategory[**MorphismData, **TwoMorphismData](Category[MorphismData, TwoMorphismData]):
    """``C.Core()``: the objects of ``C`` with its isomorphisms as morphisms."""

    class ObjectType:
        """An object of ``C``: the core has every one of them, as the same value."""

    class ElementType:
        """A generalized element ``t: T -> X`` whose defining morphism is an isomorphism, since those are the morphisms of the core."""

    class MorphismType:
        """An isomorphism of ``C``: the core narrows the morphisms and nothing else."""

    def __init__(self, ambient: Category[MorphismData, TwoMorphismData]) -> None:
        self._ambient = ambient
        self._isomorphisms = ambient.morphism_category(1).Isomorphisms()
        super().__init__()

    def isomorphisms(self) -> Category:
        """``Mor(C).Isomorphisms()``, whose objects are the morphisms of this category."""
        return self._isomorphisms

    def structure_functors(self) -> tuple[Functor, ...]:
        return (Fun(self, self._ambient).Monomorphisms().Isofibrations()(),)

    def morphism_category_type(self) -> type[CoreMorphismCategory]:
        return CoreMorphismCategory

    def membership_proposition(self, candidate: CategoryOfCategories.ElementType) -> Proposition:
        return self._ambient.membership_proposition(candidate)

    # -- morphisms: the isomorphisms of ``C``, as its own values (POL-MATH-037) ----------

    def construct_morphism(
        self,
        domain: CategoryOfCategories.ElementType,
        codomain: CategoryOfCategories.ElementType,
        *args: MorphismData.args,
        **kwargs: MorphismData.kwargs,
    ) -> MorphismCategory.ObjectType:
        """``Mor(C.Core())(A, B)(data)``: the trusted constructor ``Mor(C)(A, B).Isomorphisms()(data)``."""
        return self._isomorphisms(domain, codomain)(*args, **kwargs)

    def _identity_morphism_(self, member_object: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
        """The identity of ``C``, which is an isomorphism."""
        return self._isomorphisms(self._ambient.morphism_category(1)(member_object, member_object).one())

    def compose_morphisms(
        self,
        second: MorphismCategory.ObjectType,
        first: MorphismCategory.ObjectType,
    ) -> MorphismCategory.ObjectType:
        """The composite in ``C``, of two isomorphisms and so an isomorphism."""
        return self._isomorphisms(self._ambient.compose_morphisms(second, first))

    def inverse_morphism(self, morphism: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        return self._ambient.inverse_morphism(morphism)

    def retain_inverses(
        self,
        forward: MorphismCategory.ObjectType,
        backward: MorphismCategory.ObjectType,
    ) -> None:
        self._ambient.retain_inverses(forward, backward)

    def _chosen_hom_inhabited(self, hom_category: Category) -> Decision:
        """``Mor(C.Core())(A, B)`` narrowed by roots is inhabited exactly when ``Mor(C)(A, B).Isomorphisms()`` narrowed the same way is."""
        base = hom_category.narrowing_base()
        target = self._ambient.morphism_category(1)(base.domain(), base.codomain()).property_subcategory(self._isomorphisms)
        for root in hom_category.narrowing_roots():
            target = target.property_subcategory(root)
        return ask(target.is_inhabited())

    def __repr__(self) -> str:
        return f"{self._ambient!r}.Core()"


class CoreMorphismCategory(MorphismCategory):
    """``Mor(C.Core())``: a morphism of ``C`` is a member exactly when it is an isomorphism."""

    class ObjectType:
        """An isomorphism of ``C``: the core narrows the morphisms and nothing else."""

    class ElementType:
        """A generalized element of an isomorphism, read in ``Mor(C.Core())``."""

    class MorphismType:
        """A 2-morphism between two isomorphisms of ``C``."""

    def membership_proposition(self, candidate: CategoryOfCategories.ElementType) -> Proposition:
        return self._base.isomorphisms().membership_proposition(candidate)

    def fixed_endpoint_type(self) -> type[CoreFixedEndpointCategory]:
        return CoreFixedEndpointCategory


class CoreFixedEndpointCategory(FixedEndpointCategory):
    """``Mor(C.Core())(A, B)``: by definition the full subcategory ``Mor(C)(A, B).Isomorphisms()``.

    That identity needs no declaration of its own.  ``Mor(C.Core())`` reaches
    ``Mor(C).Isomorphisms()``, so the inherited full-subcategory monomorphism into
    ``Mor(C.Core())`` already carries it: membership here is the ambient's proposition and
    these endpoints, ``Mor(C.Core())(A, B)(data)`` constructs through
    ``Mor(C)(A, B).Isomorphisms()``, and ``CoreCategory._chosen_hom_inhabited`` asks that
    same category.  A second monomorphism, into ``Mor(C)(A, B).Isomorphisms()``, states the
    identity again as a second placement route, and the two disagree on the linearization
    of the object class (``compiler._assert_linearized``).
    """

    # ``Mor(C.Core())(A, B)`` is by definition ``Mor(C)(A, B).Isomorphisms()``: the same
    # objects, so each body below is empty.
    class ObjectType:
        """An isomorphism ``A -> B`` of ``C``."""

    class ElementType:
        """A generalized element of such an isomorphism."""

    class MorphismType:
        """A 2-morphism between two isomorphisms ``A -> B``."""


def _core_of(category: Category) -> Category:
    """``Core.on_object(C)``: the core, placed in ``Groupoids()`` because that is where ``Core`` lands."""
    core = CoreCategory(category)
    refine(core, Groupoids)
    return core


def _restricted(functor: Functor) -> Functor:
    """``Core.on_morphism(F)``: ``F`` restricted to the isomorphisms."""
    return Fun(functor.domain().Core(), functor.codomain().Core())(functor.on_object, lambda isomorphism: _image(functor, isomorphism))


def _image(functor: Functor, isomorphism: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
    """``F(f)``, with ``F(f⁻¹)`` retained as its inverse, which places it in ``Mor(D).Isomorphisms()``."""
    image = functor.on_morphism(isomorphism)
    functor.codomain().retain_inverses(image, functor.on_morphism(isomorphism.inverse()))
    return image


Core: Functor = Fun(Cat(), Groupoids)(_core_of, _restricted)

# The one retained identity-on-values functor out of ``Groupoids()``, which is also the
# one ``GroupoidsCategory.structure_functors`` selects.
U: Functor = Fun(Groupoids, Cat()).Monomorphisms().Isofibrations()()

_endofunctors = Fun(Cat(), Cat())
epsilon: NaturalTransformation = _endofunctors.morphism_category(1)(U * Core, _endofunctors.one())(
    lambda category: Fun(category.Core(), category).Monomorphisms().Isofibrations()()
)
