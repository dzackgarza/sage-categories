"""Discrete categories, diagrams, limits, and colimits."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import TYPE_CHECKING, Any, TypeIs

from sage_categories.abstract_categories.hom_categories import (
    HomCategory,
)
from sage_categories.category import Category
from sage_categories.values import (
    Arrow,
    MathematicalElement,
    MathematicalObject,
    registered_value,
)

if TYPE_CHECKING:
    from sage_categories.theories.sets import DiscreteObjectSet, SetElement

from sage_categories.abstract_categories.functor_core import (
    Functor,
    NaturalTransformation,
    StructuralFunctor,
    is_functor,
    is_natural_transformation_hom_category,
)


class DiscreteObject(MathematicalObject):
    """One object of a represented discrete category."""

    def __init__(
        self,
        *,
        category: DiscreteCategory,
        label: SetElement,
    ) -> None:
        self._label = label
        super().__init__(category=category)

    def label(self) -> SetElement:
        return self._label

    def __repr__(self) -> str:
        return repr(self._label)


class DiscreteIdentity(Arrow):
    """The unique arrow at one object of a discrete category."""


class DiscreteHomCategory(HomCategory):
    """A singleton hom category when both endpoints are equal."""

    ObjectType = DiscreteIdentity
    ElementType = DiscreteIdentity

    def __call__(self) -> DiscreteIdentity:
        return self.identity()

    def identity(
        self,
        value: MathematicalObject | None = None,
    ) -> DiscreteIdentity:
        assert value is None
        assert self.domain() is self.codomain()
        return self.ObjectType(hom_category=self)

    def compose(self, second: Arrow, first: Arrow) -> DiscreteIdentity:
        assert first in self and second in self
        return self.identity()

    def objects(self) -> MathematicalObject:
        from sage_categories.theories.sets import FiniteSet

        if self.domain() is self.codomain():
            return FiniteSet(frozenset({self.identity()}))
        return FiniteSet(frozenset())


class DiscreteCategory(Category):
    """The discrete category on one owned set."""

    ObjectType = DiscreteObject

    def __init__(
        self,
        *,
        category: Category,
        label_set: MathematicalObject,
    ) -> None:
        from sage_categories.theories.sets import Sets

        assert label_set in Sets()
        self._label_set = label_set
        self._objects_by_label: list[tuple[SetElement, DiscreteObject]] = []
        self._object_set: DiscreteObjectSet | None = None
        self._arrow_set: MathematicalObject | None = None
        super().__init__(object_type=DiscreteObject, category=category)

    def label_set(self) -> MathematicalObject:
        return self._label_set

    def object(self, label: SetElement) -> DiscreteObject:
        from sage_categories.theories.sets import Sets

        assert Sets().contains_set(self._label_set)
        assert label in self._label_set
        for saved_label, value in self._objects_by_label:
            if saved_label == label:
                return value
        value = self.ObjectType(category=self, label=label)
        assert self.contains_object(value)
        self._objects_by_label.append((label, value))
        return value

    def objects(self) -> DiscreteObjectSet:
        from sage_categories.theories.sets import DiscreteObjectSet, Sets

        if self._object_set is None:
            assert Sets().contains_set(self._label_set)
            self._object_set = DiscreteObjectSet(self, self._label_set)
        return self._object_set

    def object_element(self, value: MathematicalObject) -> SetElement:
        return self.objects().element(value)

    def arrows(self) -> MathematicalObject:
        from sage_categories.theories.sets import DiscreteArrowSet

        if self._arrow_set is None:
            self._arrow_set = DiscreteArrowSet(self)
        return self._arrow_set

    def __iter__(self) -> Iterator[DiscreteObject]:
        from sage_categories.theories.sets import Sets

        assert Sets().contains_set(self._label_set)
        return iter(tuple(self.object(label) for label in self._label_set))

    def __contains__(self, candidate: Any) -> bool:
        value = registered_value(candidate)
        return value is not None and value.category() is self

    def contains_object(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[DiscreteObject]:
        return candidate in self

    def _hom_category_type(self) -> type[HomCategory]:
        return DiscreteHomCategory

    def __repr__(self) -> str:
        return f"Discrete({self._label_set})"


class ObjectSetFunctor(StructuralFunctor):
    """Send a discrete category to its object set."""

    def __init__(self, domain: DiscreteCategoriesCategory) -> None:
        from sage_categories.theories.sets import Sets

        self._discrete_categories = domain
        super().__init__(domain, Sets())

    def _object_image(self, source: MathematicalObject) -> MathematicalObject:
        assert self._discrete_categories.contains_discrete_category(source)
        return source.objects()

    def _morphism_image(self, morphism: Arrow) -> Arrow:
        from sage_categories.theories.sets import Sets, is_set_hom_category

        assert is_functor(morphism)
        source = morphism.domain()
        target = morphism.codomain()
        assert self._discrete_categories.contains_discrete_category(source)
        assert self._discrete_categories.contains_discrete_category(target)
        source_objects = source.objects()
        target_objects = target.objects()
        assert Sets().contains_set(source_objects)
        assert Sets().contains_set(target_objects)

        def map_object(value: SetElement) -> SetElement:
            represented = value.value()
            assert source.contains_object(represented)
            image = morphism(represented)
            assert target.contains_object(image)
            return target_objects.element(image)

        hom_category = Sets().Hom(source_objects, target_objects)
        assert is_set_hom_category(hom_category)
        return hom_category(map_object)

    def _element_image(
        self,
        source: MathematicalObject,
        element: MathematicalElement,
    ) -> MathematicalElement:
        return element


class DiscreteCategoriesCategory(Category):
    """The category of arbitrary discrete categories."""

    ObjectType = DiscreteCategory

    def __init__(self) -> None:
        self._object_set_functor: ObjectSetFunctor | None = None
        super().__init__(object_type=DiscreteCategory)

    def __call__(self, label_set: MathematicalObject) -> DiscreteCategory:
        return self.ObjectType(category=self, label_set=label_set)

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        if self._object_set_functor is None:
            self._object_set_functor = ObjectSetFunctor(self)
        return (self._object_set_functor,)

    def contains_discrete_category(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[DiscreteCategory]:
        return candidate in self


_DISCRETE_CATEGORIES: DiscreteCategoriesCategory | None = None


def DiscreteCategories() -> DiscreteCategoriesCategory:
    global _DISCRETE_CATEGORIES

    if _DISCRETE_CATEGORIES is None:
        _DISCRETE_CATEGORIES = DiscreteCategoriesCategory()
    return _DISCRETE_CATEGORIES


class DiscreteDiagram(Functor):
    """A functor from a discrete category, given on objects."""

    def __init__(
        self,
        domain: DiscreteCategory,
        codomain: Category,
        values: Callable[[DiscreteObject], MathematicalObject],
    ) -> None:
        self._index_category = domain
        self._values = values
        super().__init__(domain, codomain)

    def domain(self) -> DiscreteCategory:
        return self._index_category

    def _object_image(self, source: MathematicalObject) -> MathematicalObject:
        assert self.domain().contains_object(source)
        image = self._values(source)
        assert image in self.codomain()
        return image

    def _morphism_image(self, morphism: Arrow) -> Arrow:
        return self.codomain().identity(self.on_object(morphism.domain()))


class ConstantDiagram(Functor):
    """The constant diagram at one object."""

    def __init__(
        self,
        index_category: Category,
        codomain: Category,
        value: MathematicalObject,
    ) -> None:
        assert value in codomain
        self._value = value
        super().__init__(index_category, codomain)

    def constant_value(self) -> MathematicalObject:
        return self._value

    def _object_image(self, source: MathematicalObject) -> MathematicalObject:
        assert source in self.domain()
        return self._value

    def _morphism_image(self, morphism: Arrow) -> Arrow:
        assert morphism in self.domain().ArrowCategory()
        return self.codomain().identity(self._value)


class DiagonalFunctor(Functor):
    """The functor sending each object to its constant diagram."""

    def __init__(self, category: Category, index_category: Category) -> None:
        self._index_category = index_category
        super().__init__(category, category.Diagram(index_category))

    def _object_image(self, source: MathematicalObject) -> ConstantDiagram:
        return ConstantDiagram(self._index_category, self.domain(), source)

    def _morphism_image(self, morphism: Arrow) -> Arrow:
        source = self.on_object(morphism.domain())
        target = self.on_object(morphism.codomain())
        assert is_functor(source)
        assert is_functor(target)
        return NaturalTransformation(source, target, lambda index: morphism)


class LimitFunctor(Functor):
    """A chosen limit functor on diagrams of one fixed shape."""

    def __init__(self, codomain: Category, index_category: Category) -> None:
        self._index_category = index_category
        super().__init__(codomain.Diagram(index_category), codomain)

    def index_category(self) -> Category:
        return self._index_category

    def _construct_image_category(self) -> Category:
        return self.codomain()._limits_of_category(self)

    def _object_image(self, source: MathematicalObject) -> MathematicalObject:
        assert is_functor(source)
        assert source in self.domain()
        from sage_categories.abstract_categories.products import (
            is_limits_of_category,
        )

        image = self.Image()
        assert is_limits_of_category(image)
        return image.limit_of(source)

    def _morphism_image(self, morphism: Arrow) -> Arrow:
        hom_category = morphism.hom_category()
        assert is_natural_transformation_hom_category(hom_category)
        assert hom_category.contains_transformation(morphism)
        source = morphism.domain()
        target = morphism.codomain()
        assert is_functor(source)
        assert is_functor(target)
        from sage_categories.abstract_categories.products import (
            Cone,
            LimitObject,
            is_limits_of_category,
        )

        image = self.Image()
        assert is_limits_of_category(image)
        source_limit = image.limit_of(source)
        target_limit = image.limit_of(target)
        source_cone = source_limit.limit_cone()
        cone = Cone(
            target,
            source_limit.apex(),
            lambda index: self.codomain().compose(
                morphism.component(index),
                source_cone.structure_morphism(index),
            ),
        )
        underlying_arrow = LimitObject.universal_morphism(target_limit, cone)
        return image.Hom(source_limit, target_limit)(underlying_arrow)


class ColimitFunctor(Functor):
    """A chosen colimit functor on diagrams of one fixed shape."""

    def __init__(self, codomain: Category, index_category: Category) -> None:
        self._index_category = index_category
        super().__init__(codomain.Diagram(index_category), codomain)

    def index_category(self) -> Category:
        return self._index_category

    def _construct_image_category(self) -> Category:
        return self.codomain()._colimits_of_category(self)

    def _object_image(self, source: MathematicalObject) -> MathematicalObject:
        assert is_functor(source)
        assert source in self.domain()
        from sage_categories.abstract_categories.products import (
            is_colimits_of_category,
        )

        image = self.Image()
        assert is_colimits_of_category(image)
        return image.colimit_of(source)

    def _morphism_image(self, morphism: Arrow) -> Arrow:
        hom_category = morphism.hom_category()
        assert is_natural_transformation_hom_category(hom_category)
        assert hom_category.contains_transformation(morphism)
        source = morphism.domain()
        target = morphism.codomain()
        assert is_functor(source)
        assert is_functor(target)
        from sage_categories.abstract_categories.products import (
            Cocone,
            ColimitObject,
            is_colimits_of_category,
        )

        image = self.Image()
        assert is_colimits_of_category(image)
        source_colimit = image.colimit_of(source)
        target_colimit = image.colimit_of(target)
        target_cocone = target_colimit.colimit_cocone()
        cocone = Cocone(
            source,
            target_colimit.apex(),
            lambda index: self.codomain().compose(
                target_cocone.costructure_morphism(index),
                morphism.component(index),
            ),
        )
        underlying_arrow = ColimitObject.universal_morphism(
            source_colimit,
            cocone,
        )
        return image.Hom(source_colimit, target_colimit)(underlying_arrow)


class ProductFunctor(LimitFunctor):
    """The chosen limit functor on diagrams with discrete domain."""

    def __init__(self, codomain: Category, index_category: Category) -> None:
        assert index_category in DiscreteCategories()
        super().__init__(codomain, index_category)

    def _construct_image_category(self) -> Category:
        return self.codomain()._products_of_category(self)


class CoproductFunctor(ColimitFunctor):
    """The chosen colimit functor on diagrams with discrete domain."""

    def __init__(self, codomain: Category, index_category: Category) -> None:
        assert index_category in DiscreteCategories()
        super().__init__(codomain, index_category)

    def _construct_image_category(self) -> Category:
        return self.codomain()._coproducts_of_category(self)
