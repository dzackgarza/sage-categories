"""Partially ordered sets and their structural category."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING, Any, Self, TypeIs

from sage_categories.abstract_categories.functors import (
    DiscreteCategories,
    Functor,
    StructuralFunctor,
)
from sage_categories.abstract_categories.hom_categories import HomCategory
from sage_categories.abstract_categories.products import (
    ProductPresentation,
)
from sage_categories.category import Category
from sage_categories.theories.sets import (
    FiniteSet,
    FiniteSets,
    FiniteSetsCategory,
    ProductElements,
    SetElement,
    SetElements,
    SetMorphism,
    SetObject,
    Sets,
    SetsCategory,
    is_products_of_sets_category,
    is_set_hom_category,
)
from sage_categories.values import (
    UNKNOWN,
    Arrow,
    Decision,
    MathematicalElement,
    MathematicalObject,
    registered_element,
    registered_value,
)

if TYPE_CHECKING:
    from sage_categories.theories.finite_posets import (
        FinitePosetObject,
        FinitePosetsCategory,
    )
    from sage_categories.theories.thin_categories import ThinCategory

type OrderRelation = Callable[[PosetElement, PosetElement], Decision]


class PosetElement(MathematicalElement):
    """An element of one partially ordered set."""

    def __init__(
        self,
        *,
        ambient_object: PosetObject | FinitePosetObject,
        set_element: SetElement,
    ) -> None:
        assert ambient_object in PartiallyOrderedSets()
        underlying_set = PartiallyOrderedSets().underlying_set(ambient_object)
        assert set_element.ambient_set() is underlying_set
        assert set_element in underlying_set
        self._set_element = set_element
        super().__init__(
            category=ambient_object.category(),
            ambient_object=ambient_object,
        )

    def _set_implementation(self) -> SetElement:
        return self._set_element

    @classmethod
    def _refined_element_from_ambient(
        cls,
        *,
        category: Category,
        ambient_object: MathematicalObject,
        ambient_implementation: MathematicalElement,
    ) -> Self:
        assert is_partially_ordered_sets_category(category)
        assert PartiallyOrderedSets().contains_poset(ambient_object)
        assert SetElements().contains_set_element(ambient_implementation)
        return cls(
            ambient_object=ambient_object,
            set_element=ambient_implementation,
        )

    def ambient_poset(self) -> PosetObject:
        ambient = self.ambient_object()
        assert PartiallyOrderedSets().contains_poset(ambient)
        return ambient

    def __le__(self, other: PosetElement) -> Decision:
        return self.ambient_poset()._is_lequal(self, other)

    def __lt__(self, other: PosetElement) -> Decision:
        comparison = self <= other
        if comparison is UNKNOWN:
            return UNKNOWN
        return comparison and self != other

    def __repr__(self) -> str:
        return repr(self._set_element)


def validate_finite_partial_order(
    poset: PosetObject,
    underlying_set: SetObject,
    relation: OrderRelation,
) -> None:
    """Establish reflexivity, antisymmetry, and transitivity for finite posets."""
    members = tuple(poset.element(s) for s in underlying_set)
    for x in members:
        rx = relation(x, x)
        assert rx is True, f"reflexivity failed for {x}: got {rx}"
    for i, x in enumerate(members):
        for y in members[i + 1 :]:
            r_xy = relation(x, y)
            r_yx = relation(y, x)
            if r_xy is False or r_yx is False:
                continue
            assert not (r_xy is True and r_yx is True), f"antisymmetry failed: {x} and {y} mutually <= "
            assert False, f"antisymmetry unknown for {x} and {y}"
    for x in members:
        for y in members:
            r_xy = relation(x, y)
            for z in members:
                r_yz = relation(y, z)
                if r_xy is False or r_yz is False:
                    continue
                r_xz = relation(x, z)
                if r_xy is True and r_yz is True:
                    assert r_xz is True, f"transitivity failed for {x} <= {y} <= {z}"
                    continue
                assert False, f"transitivity unknown for {x}, {y}, {z}"


class PosetObject(MathematicalObject):
    """A set equipped with one chosen partial order."""

    def __init__(
        self,
        *,
        category: PartiallyOrderedSetsCategory,
        underlying_set: SetObject,
        relation: OrderRelation,
    ) -> None:
        assert underlying_set in Sets()
        self._underlying_set = underlying_set
        self._relation = relation
        self._elements: dict[int, PosetElement] = {}
        self._thin_category: ThinCategory | None = None
        super().__init__(category=category)
        if underlying_set.is_finite() is True:
            validate_finite_partial_order(self, underlying_set, relation)

    def _set_implementation(self) -> SetObject:
        return self._underlying_set

    def category(self) -> PartiallyOrderedSetsCategory:
        category = super().category()
        assert category is PartiallyOrderedSets()
        return PartiallyOrderedSets()

    def relation(self) -> OrderRelation:
        """Return the chosen order relation."""
        return self._relation

    def __contains__(self, candidate: Any) -> bool:
        element = registered_element(candidate)
        return element is not None and element.ambient_object() is self

    def element(self, set_element: SetElement) -> PosetElement:
        underlying_set = self._set_implementation()
        assert set_element.ambient_set() is underlying_set
        assert set_element in underlying_set
        key = id(set_element)
        cached = self._elements.get(key)
        if cached is None:
            element_type = self.category().ElementType
            cached = element_type._refined_element_from_ambient(
                category=self.category(),
                ambient_object=self,
                ambient_implementation=set_element,
            )
            self._elements[key] = cached
        return cached

    def _is_lequal(self, left: PosetElement, right: PosetElement) -> Decision:
        assert left in self
        assert right in self
        return self._relation(left, right)

    def thin_category(self) -> ThinCategory:
        from sage_categories.theories.thin_categories import ThinCategory

        if self._thin_category is None:
            self._thin_category = ThinCategory(self)
        return self._thin_category

    def __repr__(self) -> str:
        return f"Partially ordered {self._underlying_set}"


class PosetMorphism(Arrow):
    """An order-preserving map with its underlying set function."""

    def __init__(
        self,
        *,
        hom_category: PosetHomCategory,
        underlying_function: SetMorphism,
    ) -> None:
        source = hom_category.domain()
        target = hom_category.codomain()
        category = hom_category.base_category()
        assert is_partially_ordered_sets_category(category)
        assert PartiallyOrderedSets().contains_poset(source)
        assert PartiallyOrderedSets().contains_poset(target)
        assert underlying_function in Sets().Hom(
            PartiallyOrderedSets().underlying_set(source),
            PartiallyOrderedSets().underlying_set(target),
        )
        self._underlying_function = underlying_function
        super().__init__(hom_category=hom_category)

    def _set_implementation(self) -> SetMorphism:
        return self._underlying_function

    def __call__(self, member: PosetElement) -> PosetElement:
        source = self.domain()
        target = self.codomain()
        category = self.base_category()
        assert is_partially_ordered_sets_category(category)
        assert PartiallyOrderedSets().contains_poset(source)
        assert PartiallyOrderedSets().contains_poset(target)
        if member.ambient_object() is not source:
            route = (
                member.ambient_object()
                .category()
                .structural_route_to(
                    source.category(),
                )
            )
            image_member = member._element_image_along(route)
            assert is_poset_element(image_member)
            assert image_member.ambient_object() is source
            member = image_member
        assert member.ambient_object() is source
        forgetful_functor = PartiallyOrderedSets().forgetful_functor()
        set_member = forgetful_functor.on_element(source, member)
        assert SetElements().contains_set_element(set_member)
        image = self._underlying_function(set_member)
        return target.element(image)

    def is_order_preserving(self) -> bool:
        return True

    def is_order_reflecting(self) -> Decision:
        source = self.domain()
        target = self.codomain()
        category = self.base_category()
        assert is_partially_ordered_sets_category(category)
        assert PartiallyOrderedSets().contains_poset(source)
        assert PartiallyOrderedSets().contains_poset(target)
        underlying_set = PartiallyOrderedSets().underlying_set(source)
        if underlying_set.is_finite() is not True:
            return UNKNOWN
        answer: Decision = True
        for left in source:
            assert is_poset_element(left)
            for right in source:
                assert is_poset_element(right)
                image_comparison = self(left) <= self(right)
                source_comparison = left <= right
                if image_comparison is True and source_comparison is False:
                    return False
                if image_comparison is UNKNOWN or source_comparison is UNKNOWN:
                    answer = UNKNOWN
        return answer

    def is_order_embedding(self) -> Decision:
        return self.is_order_reflecting()

    def is_order_isomorphism(self) -> Decision:
        bijective = self._underlying_function.is_bijective()
        reflecting = self.is_order_reflecting()
        if bijective is False or reflecting is False:
            return False
        if bijective is UNKNOWN or reflecting is UNKNOWN:
            return UNKNOWN
        return True

    def inverse(self) -> PosetMorphism:
        assert self.is_order_isomorphism() is True
        category = self.base_category()
        assert is_partially_ordered_sets_category(category)
        inverse = self._underlying_function.inverse()
        hom_category = category.Hom(self.codomain(), self.domain())
        assert is_poset_hom_category(hom_category)
        return hom_category.ObjectType(
            hom_category=hom_category,
            underlying_function=inverse,
        )


def check_order_preserving(
    source: PosetObject,
    target: PosetObject,
    morphism: Callable[[PosetElement], PosetElement],
) -> Decision:
    underlying_set = PartiallyOrderedSets().underlying_set(source)
    if underlying_set.is_finite() is not True:
        return UNKNOWN
    decision: Decision = True
    for left in source:
        assert is_poset_element(left)
        f_left = morphism(left)
        assert is_poset_element(f_left)
        assert f_left in target
        for right in source:
            assert is_poset_element(right)
            f_right = morphism(right)
            assert is_poset_element(f_right)
            assert f_right in target
            left_le = left <= right
            if left_le is True:
                image_le = f_left <= f_right
                if image_le is False:
                    return False
                if image_le is UNKNOWN:
                    decision = UNKNOWN
            elif left_le is UNKNOWN:
                image_le = f_left <= f_right
                if image_le is False:
                    decision = UNKNOWN
    return decision


class PosetHomCategory(HomCategory):
    """The order-preserving maps between two posets."""

    ObjectType = PosetMorphism
    ElementType = PosetMorphism

    def __call__(
        self,
        action: SetMorphism | PosetMorphism,
    ) -> PosetMorphism:
        existing = registered_value(action)
        if existing is not None and self.contains_poset_morphism(existing):
            return existing
        source = self.domain()
        target = self.codomain()
        category = self.base_category()
        assert is_partially_ordered_sets_category(category)
        assert PartiallyOrderedSets().contains_poset(source)
        assert PartiallyOrderedSets().contains_poset(target)
        set_hom = Sets().Hom(
            PartiallyOrderedSets().underlying_set(source),
            PartiallyOrderedSets().underlying_set(target),
        )
        assert is_set_hom_category(set_hom)
        assert Sets().contains_set_morphism(action)
        assert action.domain() is set_hom.domain()
        assert action.codomain() is set_hom.codomain()
        underlying = action

        def candidate_map(member: PosetElement) -> PosetElement:
            set_member = PartiallyOrderedSets().forgetful_functor().on_element(source, member)
            assert SetElements().contains_set_element(set_member)
            return target.element(underlying(set_member))

        underlying_source = PartiallyOrderedSets().underlying_set(source)
        assert underlying_source.is_finite() is True, f"Candidate map from nonfinite {source} cannot enter PosetHomCategory without an established theorem"
        order_preserving = check_order_preserving(source, target, candidate_map)
        assert order_preserving is True, f"candidate map from {source} to {target} is not order preserving (decision={order_preserving})"

        return self.ObjectType(
            hom_category=self,
            underlying_function=underlying,
        )

    def identity(self) -> PosetMorphism:
        assert self.domain() is self.codomain()
        category = self.base_category()
        assert is_partially_ordered_sets_category(category)
        source = self.domain()
        assert PartiallyOrderedSets().contains_poset(source)
        underlying = Sets().identity(PartiallyOrderedSets().underlying_set(source))
        assert Sets().contains_set_morphism(underlying)
        return self.ObjectType(
            hom_category=self,
            underlying_function=underlying,
        )

    def compose(self, second: Arrow, first: Arrow) -> PosetMorphism:
        second_hom = second.hom_category()
        first_hom = first.hom_category()
        assert is_poset_hom_category(second_hom)
        assert is_poset_hom_category(first_hom)
        assert second_hom.contains_poset_morphism(second)
        assert first_hom.contains_poset_morphism(first)
        assert first.domain() is self.domain()
        assert first.codomain() is second.domain()
        assert second.codomain() is self.codomain()
        category = self.base_category()
        assert is_partially_ordered_sets_category(category)
        forgetful_functor = PartiallyOrderedSets().forgetful_functor()
        underlying = Sets().compose(
            forgetful_functor.on_morphism(second),
            forgetful_functor.on_morphism(first),
        )
        assert Sets().contains_set_morphism(underlying)
        return self.ObjectType(
            hom_category=self,
            underlying_function=underlying,
        )

    def contains_poset_morphism(
        self,
        arrow: MathematicalObject,
    ) -> TypeIs[PosetMorphism]:
        return arrow in self


class ForgetPosetFunctor(StructuralFunctor):
    """Forget the chosen order and retain the underlying set and function."""

    def __init__(
        self,
        posets: PartiallyOrderedSetsCategory | FinitePosetsCategory,
        sets: SetsCategory | FiniteSetsCategory,
    ) -> None:
        super().__init__(posets, sets)

    def _object_image(self, source: MathematicalObject) -> SetObject:
        assert PartiallyOrderedSets().contains_poset(source)
        if source.category() is not self.domain():
            route = source.category().structural_route_to(self.domain())
            source = source._object_image_along(route)
            assert PartiallyOrderedSets().contains_poset(source)
        image = source._set_implementation()
        assert image in self.codomain()
        return image

    def _morphism_image(self, morphism: Arrow) -> SetMorphism:
        hom_category = morphism.hom_category()
        assert is_poset_hom_category(hom_category)
        assert hom_category.contains_poset_morphism(morphism)
        return morphism._set_implementation()

    def _element_image(
        self,
        source: MathematicalObject,
        element: MathematicalElement,
    ) -> SetElement:
        assert PartiallyOrderedSets().contains_poset(source)
        assert is_poset_element(element)
        if source.category() is not self.domain():
            route = source.category().structural_route_to(self.domain())
            source = source._object_image_along(route)
            element = element._element_image_along(route)
            assert PartiallyOrderedSets().contains_poset(source)
            assert is_poset_element(element)
        return element._set_implementation()

    def _element_preimage(
        self,
        source: MathematicalObject,
        element: MathematicalElement,
    ) -> PosetElement:
        assert PartiallyOrderedSets().contains_poset(source)
        assert SetElements().contains_set_element(element)
        return source.element(element)

    def is_faithful(self) -> bool:
        return True


class PartiallyOrderedSetsCategory(Category):
    """Sets equipped with a chosen partial order."""

    ObjectType = PosetObject
    ElementType = PosetElement

    def __init__(self) -> None:
        self._forgetful_functor: ForgetPosetFunctor | None = None
        self._finite_posets: FinitePosetsCategory | None = None
        super().__init__()

    def __call__(
        self,
        underlying_set: SetObject,
        relation: OrderRelation,
    ) -> PosetObject:
        if underlying_set in FiniteSets():
            return self.Finite()(underlying_set, relation)
        assert False, f"Arbitrary infinite relation on {underlying_set} cannot enter PartiallyOrderedSets() without an established construction theorem"

    def discrete_order(self, underlying_set: SetObject) -> PosetObject:
        """Return the discrete poset on ``underlying_set`` with equality order."""
        assert underlying_set in Sets()
        return self.ObjectType(
            category=self,
            underlying_set=underlying_set,
            relation=lambda left, right: left == right,
        )

    def _ordinal_order(
        self,
        underlying_set: SetObject,
        relation: OrderRelation,
    ) -> PosetObject:
        """Construct a poset from the ordinal well-ordering theorem.

        The order on ordinals is reflexive, antisymmetric, and transitive
        by the well-ordering of ordinals (Sierpiński §II.7).  This is a
        theorem-backed entry path for infinite ordinal-valued sets.
        """
        return self.ObjectType(
            category=self,
            underlying_set=underlying_set,
            relation=relation,
        )

    def _hom_category_type(self) -> type[HomCategory]:
        return PosetHomCategory

    def Hom(
        self,
        domain: MathematicalObject,
        codomain: MathematicalObject,
    ) -> PosetHomCategory:
        category = Category.Hom(self, domain, codomain)
        assert is_poset_hom_category(category)
        return category

    def forgetful_functor(self) -> ForgetPosetFunctor:
        if self._forgetful_functor is None:
            self._forgetful_functor = ForgetPosetFunctor(self, Sets())
        return self._forgetful_functor

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        return (self.forgetful_functor(),)

    def contains_poset(self, candidate: MathematicalObject) -> TypeIs[PosetObject]:
        return candidate in self

    def underlying_set(self, source: MathematicalObject) -> SetObject:
        assert source in self
        image = self.forgetful_functor()(source)
        assert Sets().contains_set(image)
        return image

    def Finite(self) -> FinitePosetsCategory:
        from sage_categories.theories.finite_posets import FinitePosetsCategory

        if self._finite_posets is None:
            self._finite_posets = FinitePosetsCategory(self)
        return self._finite_posets

    def _products_of_category(self, functor: Functor) -> Category:
        return super()._products_of_category(functor)

    def chosen_limit(self, diagram: Functor) -> ProductPresentation:
        assert diagram.codomain() is self
        assert diagram.domain() in DiscreteCategories()
        forgetful = self.forgetful_functor()
        inherited_product = forgetful.inherited_product(diagram)
        underlying_product = inherited_product
        product_category = underlying_product.category()
        assert is_products_of_sets_category(product_category)
        assert product_category.contains_set_product(underlying_product)

        def componentwise(left: PosetElement, right: PosetElement) -> Decision:
            left_components = left._set_implementation()
            right_components = right._set_implementation()
            assert ProductElements().contains_product_element(left_components)
            assert ProductElements().contains_product_element(right_components)
            indices = underlying_product.index_set()
            if indices.is_finite() is not True:
                return UNKNOWN
            answer: Decision = True
            for index in indices:
                factor = diagram(underlying_product.index_category().object(index))
                assert self.contains_poset(factor)
                comparison = factor.element(left_components[index]) <= factor.element(
                    right_components[index],
                )
                if comparison is False:
                    return False
                if comparison is UNKNOWN:
                    answer = UNKNOWN
            return answer

        # Theorem: the componentwise order on a product of posets is a partial
        # order (Davey & Priestley, Introduction to Lattices and Order, §1.28).
        apex = self._componentwise_product_order(underlying_product, componentwise)

        return forgetful.lift_product(
            diagram,
            apex,
            inherited_product,
            lift_morphism=self._monotone_product_arrow,
        )

    def _componentwise_product_order(
        self,
        underlying_set: SetObject,
        relation: OrderRelation,
    ) -> PosetObject:
        """Construct a poset from the componentwise product-order theorem.

        The componentwise order on a product of posets inherits reflexivity,
        antisymmetry, and transitivity from its factors.  This is a theorem-
        backed entry path that bypasses finite exhaustive validation.
        """
        # Davey & Priestley, Introduction to Lattices and Order, §1.28.
        return self.ObjectType(
            category=self,
            underlying_set=underlying_set,
            relation=relation,
        )

    def _monotone_product_arrow(
        self,
        source: MathematicalObject,
        target: MathematicalObject,
        set_arrow: Arrow,
    ) -> PosetMorphism:
        """Construct a monotone map from a product-projection or mediating arrow.

        Product projections and mediating arrows are monotone by the product-
        order theorem.  This is a theorem-backed entry path that bypasses
        finite monotonicity verification.
        """
        hom = self.Hom(source, target)
        assert Sets().contains_set_morphism(set_arrow)
        return hom.ObjectType(
            hom_category=hom,
            underlying_function=set_arrow,
        )

    def __repr__(self) -> str:
        return "Partially ordered sets"


_PARTIALLY_ORDERED_SETS: PartiallyOrderedSetsCategory | None = None


def PartiallyOrderedSets() -> PartiallyOrderedSetsCategory:
    global _PARTIALLY_ORDERED_SETS

    if _PARTIALLY_ORDERED_SETS is None:
        _PARTIALLY_ORDERED_SETS = PartiallyOrderedSetsCategory()
    return _PARTIALLY_ORDERED_SETS


def Poset(
    members_and_relation: tuple[
        Iterable[SetElement],
        Callable[[SetElement, SetElement], Decision],
    ],
) -> FinitePosetObject:
    """Construct the finite poset defined by ``(members, leq)``."""
    members, relation = members_and_relation
    values = tuple(dict.fromkeys(members))
    underlying_set = FiniteSet(values)

    def transported_relation(left: PosetElement, right: PosetElement) -> Decision:
        forgetful_functor = PartiallyOrderedSets().forgetful_functor()
        left_element = forgetful_functor.on_element(left.ambient_poset(), left)
        right_element = forgetful_functor.on_element(right.ambient_poset(), right)
        assert SetElements().contains_set_element(left_element)
        assert SetElements().contains_set_element(right_element)
        left_value = left_element.value()
        right_value = right_element.value()
        assert SetElements().contains_set_element(left_value)
        assert SetElements().contains_set_element(right_value)
        return relation(left_value, right_value)

    poset = PartiallyOrderedSets()(underlying_set, transported_relation)
    finite_posets = PartiallyOrderedSets().Finite()
    assert finite_posets.contains_finite_poset(poset)
    return poset


def is_partially_ordered_sets_category(
    category: Category,
) -> TypeIs[PartiallyOrderedSetsCategory]:
    return category is PartiallyOrderedSets() or category.is_subcategory(PartiallyOrderedSets())


def is_poset_hom_category(
    category: HomCategory,
) -> TypeIs[PosetHomCategory]:
    base = category.base_category()
    return is_partially_ordered_sets_category(base) and category in base.HomCategory()


def is_poset_element(candidate: MathematicalObject) -> TypeIs[PosetElement]:
    element = registered_element(candidate)
    return element is candidate and element.ambient_object() in PartiallyOrderedSets()
