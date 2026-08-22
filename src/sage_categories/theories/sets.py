"""The category of finite sets, built only from the owned categorical kernel."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Iterator
from itertools import product as cartesian_product
from typing import Any, TypeIs

from sage_categories.abstract_categories.functors import (
    Functor,
    InclusionFunctor,
    StructuralFunctor,
    is_functor,
)
from sage_categories.abstract_categories.hom_categories import (
    HomCategory,
    HomCategoryFamily,
)
from sage_categories.abstract_categories.products import (
    Cocone,
    CoconeObject,
    Cone,
    ConeObject,
    Coproduct,
    CoproductPresentation,
    Product,
    ProductPresentation,
)
from sage_categories.category import Category
from sage_categories.theories.cardinals import Cardinals, FiniteCardinal
from sage_categories.values import (
    Arrow,
    MathematicalElement,
    MathematicalObject,
    MembershipInput,
    registered_value,
)

type SetValue = int | str | MathematicalObject | ProductChoice | CoproductValue
type SetFunctionRule = Callable[[SetValue], SetValue]


class SetObject(MathematicalObject):
    """A finite set."""

    def __init__(
        self,
        *,
        category: SetsCategory,
        members: frozenset[SetValue],
    ) -> None:
        self._members = members
        super().__init__(category=category)

    def cardinality(self) -> FiniteCardinal:
        """Return the number of members."""
        return Cardinals()(len(self._members))

    def __contains__(self, candidate: MembershipInput) -> bool:
        return any(member == candidate for member in self._members)

    def __eq__(self, other: Any) -> bool:
        if other is self:
            return True
        value = registered_value(other)
        if value is None or not Sets().contains_set(value):
            return False
        return self.cardinality() == value.cardinality() and all(member in value for member in self._members)

    def __hash__(self) -> int:
        return hash(self._members)

    def __repr__(self) -> str:
        return "{" + ", ".join(sorted(repr(member) for member in self._members)) + "}"

    def __iter__(self) -> Iterator[SetValue]:
        return iter(self._members)


class SetFunction(Arrow):
    """A function between two finite sets."""

    def __init__(
        self,
        *,
        hom_category: HomCategory,
        mapping: SetFunctionRule,
    ) -> None:
        domain = hom_category.domain()
        codomain = hom_category.codomain()
        assert Sets().contains_set(domain)
        assert Sets().contains_set(codomain)
        assert all(mapping(member) in codomain for member in domain)
        self._mapping = mapping
        super().__init__(hom_category=hom_category)

    def __call__(self, value: SetValue) -> SetValue:
        domain = self.domain()
        assert Sets().contains_set(domain)
        assert value in domain
        image = self._mapping(value)
        codomain = self.codomain()
        assert Sets().contains_set(codomain)
        assert image in codomain
        return image

    def __eq__(self, other: Any) -> bool:
        if other is self:
            return True
        value = registered_value(other)
        if value is None or not Sets().contains_function(value):
            return False
        if self.domain() is not value.domain() or self.codomain() is not value.codomain():
            return False
        domain = self.domain()
        assert Sets().contains_set(domain)
        return all(self(member) == value(member) for member in domain)

    def __hash__(self) -> int:
        domain = self.domain()
        assert Sets().contains_set(domain)
        return hash(
            (
                id(domain),
                id(self.codomain()),
                tuple(self(member) for member in domain),
            )
        )


class SetHomCategory(HomCategory):
    """The discrete category of functions between two finite sets."""

    ObjectType = SetFunction
    ElementType = SetFunction

    def __init__(
        self,
        *,
        domain: MathematicalObject,
        codomain: MathematicalObject,
        hom_category: HomCategoryFamily,
    ) -> None:
        self._object_set: SetObject | None = None
        super().__init__(
            domain=domain,
            codomain=codomain,
            hom_category=hom_category,
        )

    def __call__(self, mapping: SetFunctionRule) -> SetFunction:
        result = self.ObjectType(hom_category=self, mapping=mapping)
        assert Sets().contains_function(result)
        return result

    def identity(
        self,
        value: MathematicalObject | None = None,
    ) -> SetFunction:
        assert value is None
        assert self.domain() is self.codomain()
        return self(lambda value: value)

    def compose(self, second: Arrow, first: Arrow) -> SetFunction:
        second = second.forward()
        first = first.forward()
        assert Sets().contains_function(second)
        assert Sets().contains_function(first)
        assert first.codomain() is second.domain()
        return self(lambda value: second(first(value)))

    def objects(self) -> SetObject:
        """Return the set of all functions in this hom category."""
        if self._object_set is not None:
            return self._object_set
        domain = self.domain()
        codomain = self.codomain()
        assert Sets().contains_set(domain)
        assert Sets().contains_set(codomain)
        domain_members = tuple(domain)
        codomain_members = tuple(codomain)
        functions: set[SetValue] = set()
        for images in cartesian_product(
            codomain_members,
            repeat=len(domain_members),
        ):

            def mapping(value: SetValue, images: tuple[SetValue, ...] = images) -> SetValue:
                position = next(index for index, member in enumerate(domain_members) if member == value)
                return images[position]

            functions.add(self(mapping))
        self._object_set = FiniteSet(frozenset(functions))
        return self._object_set

    def contains_object(self, candidate: SetValue) -> TypeIs[SetFunction]:
        """Return whether ``candidate`` is one function in this hom category."""
        return candidate in self


class SetHomCategoryFamily(HomCategoryFamily):
    """The hom categories of finite sets, all discrete."""

    ObjectType = SetHomCategory

    def __init__(
        self,
        base_category: Category,
        *,
        hom_category_type: type[HomCategory],
    ) -> None:
        self._discrete_inclusion: InclusionFunctor | None = None
        super().__init__(
            base_category,
            hom_category_type=hom_category_type,
        )

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        if self._discrete_inclusion is None:
            self._discrete_inclusion = InclusionFunctor(
                self,
                DiscreteCategories(),
            )
        return (self._discrete_inclusion,)


class SetsCategory(Category):
    """The category of finite sets and functions."""

    ObjectType = SetObject

    def __init__(self) -> None:
        super().__init__(object_type=SetsCategory.ObjectType)

    def _hom_category_type(self) -> type[HomCategory]:
        return SetHomCategory

    def _hom_category_family_type(self) -> type[HomCategoryFamily]:
        return SetHomCategoryFamily

    def __call__(self, members: frozenset[SetValue]) -> SetObject:
        result = self.ObjectType(category=self, members=members)
        assert self.contains_set(result)
        return result

    def Hom(
        self,
        domain: MathematicalObject,
        codomain: MathematicalObject | None = None,
    ) -> HomCategory:
        if codomain is None:
            return Category.Hom(self, domain)
        category = Category.Hom(self, domain, codomain)
        assert category in self.HomCategory()
        assert is_set_hom_category(category)
        return category

    def contains_set(self, candidate: MathematicalObject) -> TypeIs[SetObject]:
        return candidate in self

    def contains_function(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[SetFunction]:
        return candidate in self.ArrowCategory()

    def __repr__(self) -> str:
        return "Sets"


_SETS = SetsCategory()


def Sets() -> SetsCategory:
    """Return the owned category of finite sets."""
    return _SETS


def is_set_hom_category(
    category: HomCategory,
) -> TypeIs[SetHomCategory]:
    """Return whether ``category`` contains functions between finite sets."""
    return category in Sets().HomCategory()


def FiniteSet(members: frozenset[SetValue]) -> SetObject:
    """Construct the finite set with exactly these members."""
    return Sets()(members)


def SetMap(
    domain: SetObject,
    codomain: SetObject,
    mapping: SetFunctionRule,
) -> SetFunction:
    """Construct a function between two finite sets."""
    hom_category = Sets().Hom(domain, codomain)
    assert is_set_hom_category(hom_category)
    return hom_category(mapping)


class DiscreteCategoryObject(Category, ABC):
    """A discrete category together with its set of objects."""

    @abstractmethod
    def objects(self) -> SetObject:
        """Return the set of objects."""

    @abstractmethod
    def contains_object(
        self,
        candidate: SetValue,
    ) -> TypeIs[DiscreteObject]:
        """Return whether ``candidate`` is an object of this category."""


class DiscreteIdentity(Arrow):
    """The unique identity arrow at one object of a discrete category."""


class DiscreteHomCategory(HomCategory):
    """A hom category with one identity or no objects."""

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
        assert second in self and first in self
        return self.identity()


class DiscreteObject(MathematicalObject):
    """One object of a finite discrete category."""

    def __init__(
        self,
        *,
        category: FiniteDiscreteCategory,
        label: SetValue,
    ) -> None:
        self._label = label
        super().__init__(category=category)

    def label(self) -> SetValue:
        return self._label

    def __repr__(self) -> str:
        return repr(self._label)


class FiniteDiscreteCategory(DiscreteCategoryObject):
    """The discrete category on one finite set."""

    ObjectType = DiscreteObject

    def __init__(
        self,
        *,
        category: FiniteDiscreteCategoriesCategory,
        label_set: SetObject,
    ) -> None:
        self._label_set = label_set
        self._objects = tuple(DiscreteObject(category=self, label=label) for label in label_set)
        self._object_set = FiniteSet(frozenset(self._objects))
        Category.__init__(
            self,
            object_type=DiscreteObject,
            category=category,
        )

    def objects(self) -> SetObject:
        return self._object_set

    def __iter__(self) -> Iterator[DiscreteObject]:
        return iter(self._objects)

    def object(self, label: SetValue) -> DiscreteObject:
        assert label in self._label_set
        return next(value for value in self._objects if value.label() == label)

    def contains_object(
        self,
        candidate: SetValue,
    ) -> TypeIs[DiscreteObject]:
        return candidate in self

    def __contains__(self, candidate: MembershipInput) -> bool:
        return candidate in self._object_set

    def _hom_category_type(self) -> type[HomCategory]:
        return DiscreteHomCategory

    def __repr__(self) -> str:
        return f"Discrete({self._label_set})"


class ObjectSetFunctor(StructuralFunctor):
    """Send a discrete category to its set of objects."""

    def __init__(self, domain: DiscreteCategoriesCategory) -> None:
        self._discrete_categories = domain
        super().__init__(domain, Sets())

    def on_object(self, source: MathematicalObject) -> MathematicalObject:
        assert self._discrete_categories.contains_discrete_category(source)
        return source.objects()

    def on_morphism(self, morphism: Arrow) -> Arrow:
        assert is_functor(morphism)
        source = morphism.domain()
        target = morphism.codomain()
        assert self._discrete_categories.contains_discrete_category(source)
        assert self._discrete_categories.contains_discrete_category(target)

        def map_object(value: SetValue) -> SetValue:
            assert source.contains_object(value)
            image = morphism(value)
            assert target.contains_object(image)
            return image

        return SetMap(source.objects(), target.objects(), map_object)

    def on_element(
        self,
        source: MathematicalObject,
        element: MathematicalElement,
    ) -> MathematicalElement:
        return element


class DiscreteCategoriesCategory(Category):
    """The category of discrete categories."""

    ObjectType = DiscreteCategoryObject

    def __init__(self) -> None:
        self._objects_functor: ObjectSetFunctor | None = None
        super().__init__(object_type=DiscreteCategoryObject)

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        if self._objects_functor is None:
            self._objects_functor = ObjectSetFunctor(self)
        return (self._objects_functor,)

    def contains_discrete_category(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[DiscreteCategoryObject]:
        return candidate in self


class FiniteDiscreteCategoriesCategory(Category):
    """The category of finite discrete categories."""

    ObjectType = FiniteDiscreteCategory

    def __init__(self) -> None:
        self._inclusion: InclusionFunctor | None = None
        super().__init__(object_type=FiniteDiscreteCategory)

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        if self._inclusion is None:
            self._inclusion = InclusionFunctor(self, _DISCRETE_CATEGORIES)
        return (self._inclusion,)

    def __call__(self, label_set: SetObject) -> FiniteDiscreteCategory:
        result = self.ObjectType(category=self, label_set=label_set)
        assert self.contains_finite_discrete_category(result)
        return result

    def contains_finite_discrete_category(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[FiniteDiscreteCategory]:
        return candidate in self


_DISCRETE_CATEGORIES = DiscreteCategoriesCategory()
_FINITE_DISCRETE_CATEGORIES = FiniteDiscreteCategoriesCategory()


def DiscreteCategories() -> DiscreteCategoriesCategory:
    return _DISCRETE_CATEGORIES


def FiniteDiscreteCategories() -> FiniteDiscreteCategoriesCategory:
    return _FINITE_DISCRETE_CATEGORIES


def DiscreteCategory(label_set: SetObject) -> FiniteDiscreteCategory:
    """Construct the discrete category on ``label_set``."""
    return FiniteDiscreteCategories()(label_set)


class DiscreteDiagram(Functor):
    """A functor from a finite discrete category, given on objects."""

    def __init__(
        self,
        domain: FiniteDiscreteCategory,
        codomain: Category,
        values: Callable[[DiscreteObject], MathematicalObject],
    ) -> None:
        self._index_category = domain
        self._values = values
        super().__init__(domain, codomain)

    def domain(self) -> FiniteDiscreteCategory:
        return self._index_category

    def on_object(self, source: MathematicalObject) -> MathematicalObject:
        assert self.domain().contains_object(source)
        image = self._values(source)
        assert image in self.codomain()
        return image

    def on_morphism(self, morphism: Arrow) -> Arrow:
        return self.codomain().identity(self.on_object(morphism.domain()))


def SetFamily(
    index_category: FiniteDiscreteCategory,
    values: Callable[[DiscreteObject], SetObject],
) -> DiscreteDiagram:
    """Construct a finite family of sets as a discrete diagram."""
    return DiscreteDiagram(index_category, Sets(), values)


class ProductChoice(MathematicalObject):
    """A choice function representing one member of a product of sets."""

    def __init__(
        self,
        graph: tuple[tuple[DiscreteObject, SetValue], ...],
    ) -> None:
        self._graph = graph
        super().__init__(category=ProductChoices())

    def value(self, index: DiscreteObject) -> SetValue:
        return next(value for candidate, value in self._graph if candidate is index)

    def __eq__(self, other: Any) -> bool:
        if other is self:
            return True
        value = registered_value(other)
        return value is not None and ProductChoices().contains_choice(value) and self._graph == value._graph

    def __hash__(self) -> int:
        return hash(self._graph)

    def __repr__(self) -> str:
        return repr(self._graph)


class CoproductValue(MathematicalObject):
    """A tagged member of one cofactor in a coproduct of sets."""

    def __init__(self, index: DiscreteObject, value: SetValue) -> None:
        self._index = index
        self._value = value
        super().__init__(category=CoproductValues())

    def index(self) -> DiscreteObject:
        return self._index

    def value(self) -> SetValue:
        return self._value

    def __eq__(self, other: Any) -> bool:
        if other is self:
            return True
        candidate = registered_value(other)
        return candidate is not None and CoproductValues().contains_value(candidate) and self._index is candidate._index and self._value == candidate._value

    def __hash__(self) -> int:
        return hash((self._index, self._value))

    def __repr__(self) -> str:
        return f"({self._index}: {self._value!r})"


class ProductChoicesCategory(Category):
    """The category containing finite product choice functions."""

    def __init__(self) -> None:
        super().__init__(object_type=ProductChoice)

    def contains_choice(
        self,
        candidate: SetValue,
    ) -> TypeIs[ProductChoice]:
        return candidate in self


class CoproductValuesCategory(Category):
    """The category containing tagged coproduct values."""

    def __init__(self) -> None:
        super().__init__(object_type=CoproductValue)

    def contains_value(
        self,
        candidate: SetValue,
    ) -> TypeIs[CoproductValue]:
        return candidate in self


_PRODUCT_CHOICES = ProductChoicesCategory()
_COPRODUCT_VALUES = CoproductValuesCategory()


def ProductChoices() -> ProductChoicesCategory:
    return _PRODUCT_CHOICES


def CoproductValues() -> CoproductValuesCategory:
    return _COPRODUCT_VALUES


def ProductOfSets(diagram: DiscreteDiagram) -> ProductPresentation:
    """Construct the categorical product of a finite family of sets."""
    assert diagram.codomain() is Sets()
    domain = diagram.domain()
    assert FiniteDiscreteCategories().contains_finite_discrete_category(domain)
    indices = tuple(domain)

    def factor(index: DiscreteObject) -> SetObject:
        value = diagram(index)
        assert Sets().contains_set(value)
        return value

    factors = tuple(factor(index) for index in indices)
    choices = frozenset(ProductChoice(tuple(zip(indices, values, strict=True))) for values in cartesian_product(*(tuple(factor) for factor in factors)))
    apex = FiniteSet(choices)

    def projection(index: MathematicalObject) -> Arrow:
        assert domain.contains_object(index)

        def project(choice: SetValue) -> SetValue:
            assert ProductChoices().contains_choice(choice)
            return choice.value(index)

        return SetMap(apex, factor(index), project)

    cone = Cone(
        diagram,
        apex,
        projection,
    )

    def mediate(other: ConeObject) -> Arrow:
        other_apex = other.apex()
        assert Sets().contains_set(other_apex)

        def choice(value: SetValue) -> SetValue:
            def component_value(index: DiscreteObject) -> SetValue:
                component = other.structure_morphism(index)
                assert Sets().contains_function(component)
                return component(value)

            return ProductChoice(tuple((index, component_value(index)) for index in indices))

        return SetMap(
            other_apex,
            apex,
            choice,
        )

    return Product(cone, mediate)


def CoproductOfSets(diagram: DiscreteDiagram) -> CoproductPresentation:
    """Construct the categorical coproduct of a finite family of sets."""
    assert diagram.codomain() is Sets()
    domain = diagram.domain()
    assert FiniteDiscreteCategories().contains_finite_discrete_category(domain)
    indices = tuple(domain)

    def factor(index: DiscreteObject) -> SetObject:
        value = diagram(index)
        assert Sets().contains_set(value)
        return value

    factors = tuple(factor(index) for index in indices)
    members = frozenset(CoproductValue(index, value) for index, factor in zip(indices, factors, strict=True) for value in factor)
    apex = FiniteSet(members)

    def injection(index: MathematicalObject) -> Arrow:
        assert domain.contains_object(index)
        return SetMap(
            factor(index),
            apex,
            lambda value: CoproductValue(index, value),
        )

    cocone = Cocone(
        diagram,
        apex,
        injection,
    )

    def mediate(other: CoconeObject) -> Arrow:
        other_apex = other.apex()
        assert Sets().contains_set(other_apex)

        def induced(tagged: SetValue) -> SetValue:
            assert CoproductValues().contains_value(tagged)
            component = other.costructure_morphism(tagged.index())
            assert Sets().contains_function(component)
            return component(tagged.value())

        return SetMap(
            apex,
            other_apex,
            induced,
        )

    return Coproduct(cocone, mediate)
