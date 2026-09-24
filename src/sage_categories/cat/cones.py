"""Owned cone presentations and their limiting-property subcategories."""

from __future__ import annotations

from collections.abc import Callable, Hashable
from types import ModuleType

from sage_categories.cat.category import (
    Category,
    CategoryOfCategories,
    retain_deferred_universal_composite,
    retain_universal_composite,
)
from sage_categories.cat.comma import CommaSpecialization
from sage_categories.cat.functors import Fun, Functor, NaturalTransformation
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.predicates import Axiom, ask
from sage_categories.cat.properties import PropertySubcategory
from sage_categories.kernel.refinement import refine
from sage_categories.kernel.retention import identity_key
from sage_categories.kernel.sage_runtime import MonoDict, cached_function, cached_method

__all__ = [
    "ConeCategory",
    "LimitConesCategory",
    "cocone",
    "cocone_apex",
    "cocones",
    "colimit_cocones",
    "cone",
    "cone_apex",
    "cones",
    "limit_cones",
    "vertex_of",
]

type Components = Callable[[CategoryOfCategories.ElementType], MorphismCategory.ObjectType]
type Lift = Callable[[ConeCategory.ObjectType], MorphismCategory.ObjectType]


_PRESENTATION_LEGS: MonoDict = MonoDict()
_PRESENTATION_FACTORS: MonoDict = MonoDict()


def _is_cocone_presentation(presentation: ConeCategory.ObjectType) -> bool:
    """Whether ``presentation`` belongs to the cocone orientation of its cone category."""
    return presentation.category().narrowing_base()._dual


def _retain_universal_equation(
    presentation: ConeCategory.ObjectType,
    candidate: ConeCategory.ObjectType,
    mediator: MorphismCategory.ObjectType,
    vertex: CategoryOfCategories.ElementType,
    leg: MorphismCategory.ObjectType,
) -> None:
    """Retain the one leg equation selected by a universal factorization."""

    def component() -> MorphismCategory.ObjectType:
        result = candidate.leg(vertex)
        transformation = candidate.transformation()
        match transformation.is_composite():
            case True:
                first, second = transformation.factors()
                retain_universal_composite(
                    second.component(vertex),
                    first.component(vertex),
                    result,
                )
            case False:
                pass
        return result

    match _is_cocone_presentation(presentation):
        case True:
            retain_deferred_universal_composite(mediator, leg, component)
        case False:
            retain_deferred_universal_composite(leg, mediator, component)


def _retain_presentation_leg(
    presentation: ConeCategory.ObjectType,
    vertex: CategoryOfCategories.ElementType,
    leg: MorphismCategory.ObjectType,
) -> None:
    """Retain one requested leg and all universal equations already known at it."""
    legs = _PRESENTATION_LEGS[presentation] if presentation in _PRESENTATION_LEGS else ()
    if any(known_vertex is vertex and known_leg is leg for known_vertex, known_leg in legs):
        return
    _PRESENTATION_LEGS[presentation] = (*legs, (vertex, leg))
    factors = _PRESENTATION_FACTORS[presentation] if presentation in _PRESENTATION_FACTORS else ()
    for candidate, mediator in factors:
        _retain_universal_equation(presentation, candidate, mediator, vertex, leg)


def _retain_factorization(
    presentation: ConeCategory.ObjectType,
    candidate: ConeCategory.ObjectType,
    mediator: MorphismCategory.ObjectType,
) -> None:
    """Retain one universal factor and its equations at every leg already requested."""
    factors = _PRESENTATION_FACTORS[presentation] if presentation in _PRESENTATION_FACTORS else ()
    if any(known_candidate is candidate and known_mediator is mediator for known_candidate, known_mediator in factors):
        return
    _PRESENTATION_FACTORS[presentation] = (*factors, (candidate, mediator))
    legs = _PRESENTATION_LEGS[presentation] if presentation in _PRESENTATION_LEGS else ()
    for vertex, leg in legs:
        _retain_universal_equation(presentation, candidate, mediator, vertex, leg)


def _opposites() -> ModuleType:
    """Load opposite-category operations at the cycle-safe cone boundary."""
    from sage_categories.cat import opposites

    return opposites


def _terminal_category_and_star() -> tuple[Category, CategoryOfCategories.ElementType]:
    """Load ``Cat().Terminal()`` once at the cycle-safe cone construction boundary."""
    from sage_categories.cat.functors import Cat

    terminal = Cat().Terminal()
    return terminal, terminal(0)


def cone(
    diagram: Functor,
    apex: CategoryOfCategories.ElementType,
    components: Components,
) -> NaturalTransformation:
    """Construct the cone ``constant(apex) => diagram``."""
    functors = Fun(diagram.domain(), diagram.codomain())
    return functors.morphism_category(1)(functors.constant(apex), diagram)(components)


def cocone(
    diagram: Functor,
    apex: CategoryOfCategories.ElementType,
    components: Components,
) -> NaturalTransformation:
    """Construct the cocone ``diagram => constant(apex)`` through ``Op``."""
    dual_cone = cone(
        diagram.op(),
        apex,
        lambda vertex: _opposites().opposite_morphism(components(vertex)),
    )
    return dual_cone.op()


def cone_apex(transformation: NaturalTransformation) -> CategoryOfCategories.ElementType:
    """Return the apex retained by a cone transformation."""
    constant = transformation.domain()
    return Fun(constant.domain(), constant.codomain()).constant_value(constant)


def cocone_apex(transformation: NaturalTransformation) -> CategoryOfCategories.ElementType:
    """Return the apex of the cone in the opposite category that represents a cocone."""
    return cone_apex(transformation.op())


def vertex_of(
    shape: Category,
    index: CategoryOfCategories.ElementType | Hashable,
) -> CategoryOfCategories.ElementType:
    """Return the shape object selected by an object or an index datum."""
    if ask(shape.membership_proposition(index)) is True:
        return index
    from sage_categories.cat.canonical import FinitePresentedCategory

    if isinstance(shape, _opposites().OppositeCategory):
        if ask(shape.original().membership_proposition(index)) is True:
            return index
        return vertex_of(shape.original(), index)
    if isinstance(shape, FinitePresentedCategory):
        return shape(index)
    return shape.object_at(shape.object_set().point(index))


class ConeCategory(CommaSpecialization):
    """``Cones(D)`` for one diagram ``D: I -> C``."""

    LimitCones = Axiom()
    ColimitCocones = Axiom()

    class ObjectType:
        """A cone over the fixed diagram."""

        def diagram(self) -> Functor:
            return self.category().narrowing_base().diagram()

        def apex(self) -> CategoryOfCategories.ElementType:
            return self.category().narrowing_base().apex_of(self.arrow())

        def leg(
            self,
            index: CategoryOfCategories.ElementType | Hashable,
        ) -> MorphismCategory.ObjectType:
            vertex = vertex_of(self.diagram().domain(), index)
            leg = self.arrow().component(vertex)
            _retain_presentation_leg(self, vertex, leg)
            return leg

        def transformation(self) -> NaturalTransformation:
            return self.arrow()

        def __repr__(self) -> str:
            return f"Cone({self.apex()!r} -> {self.diagram()!r})"

    class ElementType:
        """A generalized element of a cone presentation."""

    class MorphismType:
        """A morphism of cones, retained through its map between apexes."""

        def apex_morphism(self) -> MorphismCategory.ObjectType:
            return self.second() if self.base_category().narrowing_base()._dual else self.first()

    def __init__(self, diagram: Functor, dual: bool = False) -> None:
        self._diagram = diagram
        self._dual = dual

        diagrams = Fun(diagram.domain(), diagram.codomain())
        point = diagrams.point_functor(diagram)
        diagonal = diagrams.diagonal()
        super().__init__(point if dual else diagonal, diagonal if dual else point)

    def diagram(self) -> Functor:
        return self._diagram

    def apex_of(self, transformation: NaturalTransformation) -> CategoryOfCategories.ElementType:
        """The apex with this category's cone or cocone orientation."""
        return cocone_apex(transformation) if self._dual else cone_apex(transformation)

    def __call__(
        self,
        transformation: NaturalTransformation,
    ) -> ConeCategory.ObjectType:
        functors = Fun(self._diagram.domain(), self._diagram.codomain())
        assert transformation in functors.morphism_category(1)
        defining = transformation.op() if self._dual else transformation
        expected = self._diagram.op() if self._dual else self._diagram
        assert defining.codomain() is expected
        assert Fun(expected.domain(), expected.codomain()).has_constant_value(defining.domain())
        apex = self.apex_of(transformation)
        _, star = _terminal_category_and_star()
        return self.from_arrow(star if self._dual else apex, apex if self._dual else star, transformation)

    def construct_morphism(
        self,
        source: ConeCategory.ObjectType,
        target: ConeCategory.ObjectType,
        apex_morphism: MorphismCategory.ObjectType,
    ) -> ConeCategory.MorphismType:
        terminal, star = _terminal_category_and_star()
        identity = terminal.morphism_category(1)(star, star).one()
        return self.morphism_from_pair(source, target, identity if self._dual else apex_morphism, apex_morphism if self._dual else identity)

    @cached_method
    def apex_functor(self) -> Functor:
        """The retained apex functor ``Cones(D) -> C``."""
        return Fun(self, self._diagram.codomain())(
            lambda presentation: presentation.apex(),
            lambda morphism: morphism.apex_morphism(),
        )

    def __repr__(self) -> str:
        return f"Cones({self._diagram!r})"


class LimitConesCategory(PropertySubcategory[[MorphismCategory.ObjectType], []]):
    """``LimitCones(D)``: terminal objects of ``Cones(D)``."""

    _base_category_class_and_axiom = (ConeCategory, "LimitCones")

    class ObjectType:
        """A limiting cone with its unique-lift operation."""

        def lift(self, candidate: ConeCategory.ObjectType) -> MorphismCategory.ObjectType:
            assert candidate.diagram() is self.diagram()
            mediator = self._cone_lift(candidate)
            _retain_factorization(self, candidate, mediator)
            return mediator

    class ElementType:
        """A generalized element of a limiting cone."""

    class MorphismType:
        """A morphism between limiting cones."""

    def with_universal_data(
        self,
        transformation: NaturalTransformation,
        lift: Lift,
    ) -> LimitConesCategory.ObjectType:
        presentation = self.ambient()(transformation)
        presentation._cone_lift = lift
        refine(presentation, self)
        return presentation

    def __repr__(self) -> str:
        return f"LimitCones({self.ambient().diagram()!r})"


ConeCategory.ColimitCocones.implemented_by(LimitConesCategory)


@cached_function(key=identity_key)
def cones(diagram: Functor) -> ConeCategory:
    """Return the retained cone category of ``diagram``."""
    return ConeCategory(diagram)


def limit_cones(diagram: Functor) -> LimitConesCategory:
    """Return the terminal-cone property category of ``diagram``."""
    return cones(diagram).LimitCones()


@cached_function(key=identity_key)
def cocones(diagram: Functor) -> ConeCategory:
    """Return cocones under ``diagram``, with the original diagram and leg orientation."""
    return ConeCategory(diagram, dual=True)


def colimit_cocones(diagram: Functor) -> LimitConesCategory:
    """Return the full subcategory of initial cocones under ``diagram``."""
    return cocones(diagram).ColimitCocones()
