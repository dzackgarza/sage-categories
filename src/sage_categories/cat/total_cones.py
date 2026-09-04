"""The total category of cones of one fixed shape."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from sage_categories.cat.cat_constructions import limit_of_categories
from sage_categories.cat.cones import ConeCategory, LimitConesCategory, cones, limit_cones
from sage_categories.cat.diagrams import cospan_diagram
from sage_categories.cat.functors import Cat, Fun, Functor, FunctorCategory, NaturalTransformation
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.predicates import Axiom, ask
from sage_categories.cat.properties import PropertySubcategory
from sage_categories.cat.slices import CommaCategory, _endpoint_functor, _pair_functor
from sage_categories.kernel.refinement import is_placed, refine
from sage_categories.kernel.sage_runtime import MonoDict

if TYPE_CHECKING:
    from sage_categories.cat.category import Category, CategoryOfCategories

__all__ = ["TotalConesCategory", "TotalLimitConesCategory", "total_cones"]


@dataclass(frozen=True, eq=False, slots=True)
class TotalConeMorphismData:
    """The two components of a morphism in ``(Delta_I downarrow Id)``."""

    apex: MorphismCategory.ObjectType
    diagram: NaturalTransformation


class TotalConesCategory(CommaCategory):
    """The comma category ``(Delta_I downarrow Id)`` for ``Fun(I, C)``."""

    LimitCones = Axiom()

    class ObjectType:
        """A cone presentation over one diagram of shape ``I``."""

        def presentation(self) -> ConeCategory.ObjectType:
            return self.category().narrowing_base().retained_datum(self)

    class ElementType:
        """A generalized element of a cone presentation."""

    class MorphismType:
        """An apex morphism and a diagram transformation satisfying the cone square."""

        def apex_morphism(self) -> MorphismCategory.ObjectType:
            data = self.base_category().narrowing_base().retained_datum(self)
            return data.apex

        def diagram_transformation(self) -> NaturalTransformation:
            data = self.base_category().narrowing_base().retained_datum(self)
            return data.diagram

    def __init__(
        self,
        defining_diagram: Functor,
        diagrams: FunctorCategory,
        diagonal: Functor,
        identity: Functor,
    ) -> None:
        self._diagrams = diagrams
        self._objects: MonoDict = MonoDict()
        super().__init__(defining_diagram, diagonal, identity)

    def diagrams(self) -> FunctorCategory:
        """Return ``Fun(I, C)``."""
        return self._diagrams

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
        assert diagram in self._diagrams
        assert presentation in cones(diagram)
        if presentation not in self._objects:
            shape = self.shape()
            apex = presentation.apex()
            constant = self._diagrams.constant(apex)
            values = {
                0: self.factor(shape(0))((apex, diagram)),
                1: self._diagrams.arrow_functor(presentation.transformation()),
                2: self.factor(shape(2))((constant, diagram)),
            }
            member = super().__call__(lambda vertex: values[shape.label(vertex)])
            self.retain_datum(member, presentation)
            self._objects[presentation] = member
        member = self._objects[presentation]
        if is_placed(presentation, limit_cones(diagram)):
            refine(member, self.LimitCones())
        return member

    def construct_morphism(
        self,
        source: TotalConesCategory.ObjectType,
        target: TotalConesCategory.ObjectType,
        apex: MorphismCategory.ObjectType,
        diagram: NaturalTransformation,
    ) -> TotalConesCategory.MorphismType:
        """Construct a comma morphism satisfying the cone square."""
        assert source in self and target in self
        source_presentation = source.presentation()
        target_presentation = target.presentation()
        ambient = self._diagrams.codomain()
        assert apex in ambient.morphism_category(1)(
            source_presentation.apex(),
            target_presentation.apex(),
        )
        assert diagram in self._diagrams.morphism_category(1)(
            source_presentation.diagram(),
            target_presentation.diagram(),
        )

        constant_source = self._diagrams.constant(source_presentation.apex())
        constant_target = self._diagrams.constant(target_presentation.apex())
        diagonal_apex = self._diagrams.morphism_category(1)(constant_source, constant_target)(
            lambda vertex: apex
        )
        assert ask(
            diagram * source_presentation.transformation()
            == target_presentation.transformation() * diagonal_apex
        ) is not False, "the apex morphism and diagram transformation do not satisfy the cone square"

        shape = self.shape()
        pair = self.factor(shape(0))
        arrows = self.factor(shape(1))
        endpoints = self.factor(shape(2))
        pair_morphism = pair.construct_morphism(
            source.component(shape(0)),
            target.component(shape(0)),
            (apex, diagram),
        )
        arrow_components = {0: diagonal_apex, 1: diagram}
        arrow_morphism = arrows.morphism_category(1)(
            source.component(shape(1)),
            target.component(shape(1)),
        )(lambda vertex: arrow_components[arrows.domain().label(vertex)])
        endpoint_morphism = endpoints.construct_morphism(
            source.component(shape(2)),
            target.component(shape(2)),
            (diagonal_apex, diagram),
        )
        components = {0: pair_morphism, 1: arrow_morphism, 2: endpoint_morphism}
        morphism = super().construct_morphism(
            source,
            target,
            lambda vertex: components[shape.label(vertex)],
        )
        self.retain_datum(morphism, TotalConeMorphismData(apex, diagram))
        return morphism

    def construct_identity(
        self,
        member_object: TotalConesCategory.ObjectType,
    ) -> TotalConesCategory.MorphismType:
        presentation = member_object.presentation()
        apex = presentation.apex()
        apex_identity = apex.category().morphism_category(1)(apex, apex).one()
        diagram = presentation.diagram()
        diagram_identity = self._diagrams.morphism_category(1)(diagram, diagram).one()
        return self.construct_morphism(
            member_object,
            member_object,
            apex_identity,
            diagram_identity,
        )

    def composite(
        self,
        second: TotalConesCategory.MorphismType,
        first: TotalConesCategory.MorphismType,
    ) -> TotalConesCategory.MorphismType:
        assert first.codomain() is second.domain()
        return self.construct_morphism(
            first.domain(),
            second.codomain(),
            second.apex_morphism() * first.apex_morphism(),
            second.diagram_transformation() * first.diagram_transformation(),
        )

    def __repr__(self) -> str:
        return f"TotalCones({self._diagrams!r})"


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


_total_cones: MonoDict = MonoDict()


def total_cones(diagrams: FunctorCategory) -> TotalConesCategory:
    """Return the retained total cone category ``(Delta_I downarrow Id)``."""
    if diagrams not in _total_cones:
        diagonal = diagrams.diagonal()
        identity = Fun(diagrams, diagrams).one()
        defining_diagram = cospan_diagram(
            Cat(),
            _pair_functor(diagonal, identity),
            _endpoint_functor(diagrams),
        )
        result = limit_of_categories(
            defining_diagram,
            Cat().Pullbacks(),
            lambda retained_diagram: TotalConesCategory(
                retained_diagram,
                diagrams,
                diagonal,
                identity,
            ),
        )
        assert isinstance(result, TotalConesCategory)
        result.defining_transformation()
        _total_cones[diagrams] = result
    return _total_cones[diagrams]
