"""The total category of cones of one fixed shape."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sage_categories.cat.cones import ConeCategory, cones, limit_cones
from sage_categories.cat.functors import Cat, Fun, Functor, FunctorCategory, NaturalTransformation
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.predicates import Axiom
from sage_categories.cat.properties import PropertySubcategory
from sage_categories.cat.slices import CommaCategory, _construct_comma_category
from sage_categories.cat.comma import CommaSpecialization
from sage_categories.kernel.refinement import is_placed, refine
from sage_categories.kernel.retention import identity_key
from sage_categories.kernel.sage_runtime import cached_function

if TYPE_CHECKING:
    from sage_categories.cat.category import Category, CategoryOfCategories

__all__ = ["TotalConesCategory", "TotalLimitConesCategory", "total_cones"]


class TotalConesCategory(CommaSpecialization):
    """The comma category ``(Delta_I downarrow Id)`` for ``Fun(I, C)``."""

    LimitCones = Axiom()

    class ObjectType:
        """A cone presentation over one diagram of shape ``I``."""

        def presentation(self) -> ConeCategory.ObjectType:
            return cones(self.second())(self.arrow())

    class ElementType:
        """A generalized element of a cone presentation."""

    class MorphismType:
        """An apex morphism and a diagram transformation satisfying the cone square."""

        def apex_morphism(self) -> MorphismCategory.ObjectType:
            return self.first()

        def diagram_transformation(self) -> NaturalTransformation:
            return self.second()

    def diagrams(self) -> FunctorCategory:
        """Return ``Fun(I, C)``."""
        return self.identity_functor().domain()

    def diagonal_functor(self) -> Functor:
        """Return the retained diagonal functor ``Delta_I``."""
        return self.comma_functors()[0]

    def identity_functor(self) -> Functor:
        """Return the retained identity functor on ``Fun(I, C)``."""
        return self.comma_functors()[1]

    def diagram_projection(self) -> Functor:
        """Return the comma projection to ``Fun(I, C)``."""
        return self.second_projection()

    def apex_functor(self) -> Functor:
        """Return the comma projection to ``C``."""
        return self.first_projection()

    def apex_fiber(self, apex: CategoryOfCategories.ElementType) -> Category:
        """Return the generic fiber of the apex functor over ``apex``."""
        return self.apex_functor().Fiber(apex)

    def __call__(self, presentation: ConeCategory.ObjectType) -> TotalConesCategory.ObjectType:
        """Retain an existing owned cone presentation in the total category."""
        diagram = presentation.diagram()
        assert diagram in self.diagrams()
        assert presentation in cones(diagram)
        member = self.from_arrow(presentation.apex(), diagram, presentation.transformation())
        if is_placed(presentation, limit_cones(diagram)):
            refine(member, self.LimitCones())
        return member

    def __repr__(self) -> str:
        return f"TotalCones({self.diagrams()!r})"


class TotalLimitConesCategory(
    PropertySubcategory[[MorphismCategory.ObjectType, NaturalTransformation], []]
):
    """The selected limiting presentations in a fixed-shape total cone category."""

    _base_category_class_and_axiom = (TotalConesCategory, "LimitCones")

    class ObjectType:
        """A total cone whose retained presentation is limiting."""

    class ElementType:
        """A generalized element of a selected limiting presentation."""

    class MorphismType:
        """A morphism between selected limiting presentations."""


@cached_function(key=identity_key)
def total_cones(diagrams: FunctorCategory) -> TotalConesCategory:
    """Return the retained total cone category ``(Delta_I downarrow Id)``."""
    return _construct_comma_category(diagrams.diagonal(), Fun(diagrams, diagrams).one(), TotalConesCategory)
