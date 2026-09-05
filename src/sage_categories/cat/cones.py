"""Owned cone presentations and their limiting-property subcategories."""

from __future__ import annotations

from collections.abc import Callable, Hashable
from dataclasses import dataclass
from typing import TYPE_CHECKING

from sage_categories.cat.category import Category
from sage_categories.cat.functors import Fun, Functor, NaturalTransformation
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.predicates import Axiom
from sage_categories.cat.properties import PropertySubcategory
from sage_categories.kernel.refinement import refine
from sage_categories.kernel.retention import identity_key
from sage_categories.kernel.sage_runtime import cached_function, cached_method

if TYPE_CHECKING:
    from sage_categories.cat.category import CategoryOfCategories

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
    from sage_categories.cat.opposites import opposite_morphism

    dual_cone = cone(
        diagram.op(),
        apex,
        lambda vertex: opposite_morphism(components(vertex)),
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
    if index in shape:
        return index
    from sage_categories.cat.canonical import FinitePresentedCategory
    from sage_categories.cat.opposites import OppositeCategory

    if isinstance(shape, FinitePresentedCategory):
        return shape(index)
    if isinstance(shape, OppositeCategory):
        return vertex_of(shape.original(), index)
    return shape.object_at(shape.object_set().point(index))


@dataclass(frozen=True, eq=False, slots=True)
class ConeMorphismData:
    """The apex morphism retained by one morphism of cones."""

    apex_morphism: MorphismCategory.ObjectType


class ConeCategory(Category[[MorphismCategory.ObjectType], []]):
    """``Cones(D)`` for one diagram ``D: I -> C``."""

    LimitCones = Axiom()
    ColimitCocones = Axiom()

    class ObjectType:
        """A cone over the fixed diagram."""

        def __init__(self, data: NaturalTransformation) -> None:
            self._cone_transformation = data

        def diagram(self) -> Functor:
            return self.category().narrowing_base().diagram()

        def apex(self) -> CategoryOfCategories.ElementType:
            return self.category().narrowing_base().apex_of(self._cone_transformation)

        def leg(
            self,
            index: CategoryOfCategories.ElementType | Hashable,
        ) -> MorphismCategory.ObjectType:
            return self._cone_transformation.component(vertex_of(self.diagram().domain(), index))

        def transformation(self) -> NaturalTransformation:
            return self._cone_transformation

        def __repr__(self) -> str:
            return f"Cone({self.apex()!r} -> {self.diagram()!r})"

    class ElementType:
        """A generalized element of a cone presentation."""

    class MorphismType:
        """A morphism of cones, retained through its map between apexes."""

        def __init__(self, data: ConeMorphismData) -> None:
            self._apex_morphism = data.apex_morphism

        def apex_morphism(self) -> MorphismCategory.ObjectType:
            return self._apex_morphism

    def __init__(self, diagram: Functor, dual: bool = False) -> None:
        self._diagram = diagram
        self._dual = dual
        super().__init__()

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
        return self.ObjectType(data=transformation)

    def construct_morphism(
        self,
        source: ConeCategory.ObjectType,
        target: ConeCategory.ObjectType,
        apex_morphism: MorphismCategory.ObjectType,
    ) -> ConeCategory.MorphismType:
        ambient_morphisms = self._diagram.codomain().morphism_category(1)
        assert apex_morphism in ambient_morphisms(source.apex(), target.apex())
        return self.MorphismType(
            domain=source,
            codomain=target,
            data=ConeMorphismData(apex_morphism),
        )

    def construct_identity(self, member_object: ConeCategory.ObjectType) -> ConeCategory.MorphismType:
        identity = self._diagram.codomain().morphism_category(1)(
            member_object.apex(),
            member_object.apex(),
        ).one()
        return self.construct_morphism(member_object, member_object, identity)

    def composite(
        self,
        second: ConeCategory.MorphismType,
        first: ConeCategory.MorphismType,
    ) -> ConeCategory.MorphismType:
        assert first.codomain() is second.domain()
        return self.construct_morphism(
            first.domain(),
            second.codomain(),
            second.apex_morphism() * first.apex_morphism(),
        )

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
            return self._cone_lift(candidate)

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
