"""``Cat().Concrete()``: the categories a faithful functor carries to ``Sets()``.

A category is concrete when it has a faithful functor to ``Sets()``.  ``Sets()`` is
concrete by its identity, and a category with a faithful selected structure functor to a
concrete category is concrete along it, because a composite of faithful functors is
faithful (Mathlib ``CategoryTheory.Functor.Faithful.comp``; the composite this repository
builds is refined into ``Fun.Faithful()`` by ``Category.composite``).

That recursion is what keeps ``Sets()`` out of the leaves.  A lattice ``(L, b)`` declares
one faithful structure functor, to the modules over its base; that category declares one
to the abelian groups; that one declares one to ``Sets()``.  No leaf names ``Sets()``, and
``functor_to_sets`` composes the chain the declarations already state.

The axiom is declared on ``CategoryOfCategories`` because concreteness is a property of
the objects of ``Cat()``, which are the categories; ``cat_kernel`` generates
``C.is_concrete()`` from it and this class implements its subcategory.
"""

from __future__ import annotations

__all__ = ["ConcreteCategory"]

from sage_categories.cat.category import Category, CategoryDeclaration, CategoryOfCategories, concrete_category
from sage_categories.cat.declarations import Sets
from sage_categories.cat.functors import Fun, Functor
from sage_categories.cat.predicates import Proposition, ask, register_handler
from sage_categories.cat.properties import PropertySubcategory
from sage_categories.kernel.sage_runtime import cached_method


def _faithful_route(category: Category, visited: tuple[Category, ...] = ()) -> tuple[Functor, ...] | None:
    """The declared faithful structure functors composing to ``Sets()``, innermost first, or ``None``.

    ``Sets()`` is reached by the empty chain.  Any other category is searched through the
    selected functors that carry inheritance and are placed in ``Fun.Faithful()``; the
    visited categories are carried so a declaration that leads back cannot recur.
    """
    from sage_categories.kernel.compiler import inheriting_functors
    from sage_categories.kernel.refinement import is_placed

    if category is Sets:
        return ()
    if any(category is known for known in visited):
        return None
    for functor in inheriting_functors(category):
        target = functor.codomain()
        if target is category or not is_placed(functor, Fun.Faithful()):
            continue
        rest = _faithful_route(target, (*visited, category))
        if rest is not None:
            return (functor, *rest)
    return None


def _decide_concrete(category: CategoryDeclaration, assumptions: Proposition) -> bool | None:
    """A faithful route to ``Sets()`` decides concreteness; its absence leaves the question open.

    The answer places the category asked, as an exact positive property result does.  Each
    tail of the route is itself a faithful route, so every category on it is concrete for
    the same reason, and asking it places that one in turn.  No route through the declared
    structure functors is not a proof that no faithful functor exists, so the negative case
    stays undecided.
    """
    return True if _faithful_route(category) is not None else None


register_handler(concrete_category, _decide_concrete)


class ConcreteCategory(PropertySubcategory):
    """``Cat().Concrete()``: the implementation of the ``Concrete`` axiom of ``Cat()``."""

    _base_category_class_and_axiom = (CategoryOfCategories, "Concrete")

    class ObjectType:
        """A concrete category: it owns the faithful functor to ``Sets()`` that its declarations compose."""

        @cached_method
        def functor_to_sets(self) -> Functor:
            """``U_C: C -> Sets()``: the composite of the declared faithful structure functors.

            The identity for ``Sets()`` itself.  For any other concrete category it is
            built from the chain that decided its concreteness, so it is the composite the
            declarations already state rather than a second functor beside them.
            """
            route = _faithful_route(self)
            assert route is not None, (
                f"{self!r} is placed among the concrete categories but declares no faithful route to {Sets!r}"
            )
            composite = Fun(Sets, Sets).one()
            for functor in reversed(route):
                composite = composite * functor
            return composite

        def underlying_set(self, member_object: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
            """``U_C(X)``: the set carrying an object of this category."""
            return self.functor_to_sets().on_object(member_object)

        def underlying_map(self, arrow: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
            """``U_C(f)``: the set map carrying a morphism of this category."""
            return self.functor_to_sets().on_morphism(arrow)

    class ElementType:
        """A point of a concrete category: an object of it, which concreteness does not change."""

    class MorphismType:
        """A functor between two concrete categories; concreteness constrains neither endpoint's morphisms."""
