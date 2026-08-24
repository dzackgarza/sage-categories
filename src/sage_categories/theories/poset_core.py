"""Partially ordered sets and their structural category."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING, Any, Self, TypeIs

from sage_categories.assumptions import Hypothesis, HypothesisContext

from sage_categories.abstract_categories.functors import (
    DiscreteCategories,
    Functor,
    StructuralFunctor,
)
from sage_categories.abstract_categories.hom_categories import HomCategory
from sage_categories.abstract_categories.products import (
    ProductPresentation,
)
from sage_categories.abstract_categories.product_presentations import (
    ConstructionLiftFunctor,
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
    SetSubset,
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
    TransportedElement,
    registered_element,
    registered_value,
)

if TYPE_CHECKING:
    from sage_categories.theories.finite_posets import (
        FinitePosetObject,
        FinitePosetsCategory,
    )
    from sage_categories.theories.thin_categories import ThinCategory

type OrderRelation = SetSubset


class PosetElement(TransportedElement):
    """An element of one partially ordered set."""

    def _set_implementation(self) -> SetElement:
        value = self._ambient_implementation()
        assert SetElements().contains_set_element(value)
        return value

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
        return repr(self._set_implementation())


def check_reflexive(
    poset: PosetObject,
    underlying_set: SetObject,
) -> Decision:
    """Return the exact result of the available reflexivity check."""
    if underlying_set.is_finite() is not True:
        return UNKNOWN
    members = tuple(poset.element(s) for s in underlying_set)
    decision: Decision = True
    for x in members:
        reflexive = x <= x
        if reflexive is False:
            return False
        if reflexive is UNKNOWN:
            decision = UNKNOWN
    return decision


def check_antisymmetric(
    poset: PosetObject,
    underlying_set: SetObject,
) -> Decision:
    """Return the exact result of the available antisymmetry check."""
    if underlying_set.is_finite() is not True:
        return UNKNOWN
    members = tuple(poset.element(s) for s in underlying_set)
    decision: Decision = True
    for i, x in enumerate(members):
        for y in members[i + 1 :]:
            r_xy = x <= y
            r_yx = y <= x
            if r_xy is True and r_yx is True:
                return False
            if r_xy is UNKNOWN or r_yx is UNKNOWN:
                decision = UNKNOWN
    return decision


def check_transitive(
    poset: PosetObject,
    underlying_set: SetObject,
) -> Decision:
    """Return the exact result of the available transitivity check."""
    if underlying_set.is_finite() is not True:
        return UNKNOWN
    members = tuple(poset.element(s) for s in underlying_set)
    decision: Decision = True
    for x in members:
        for y in members:
            r_xy = x <= y
            for z in members:
                r_yz = y <= z
                if r_xy is True and r_yz is True:
                    r_xz = x <= z
                    if r_xz is False:
                        return False
                    if r_xz is UNKNOWN:
                        decision = UNKNOWN
    return decision


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
        self._thin_category: ThinCategory | None = None
        super().__init__(category=category)

    def _set_implementation(self) -> SetObject:
        return self._underlying_set

    def relation(self) -> OrderRelation:
        """Return the chosen order relation."""
        return self._relation

    def __contains__(self, candidate: Any) -> bool:
        element = registered_element(candidate)
        return element is not None and element.ambient_object() is self

    def _is_lequal(self, left: PosetElement, right: PosetElement) -> Decision:
        assert left in self
        assert right in self
        product = self._relation.base_set()
        indices = tuple(product.index_set())
        assert len(indices) == 2
        pair = product.element(
            lambda index: (
                left._set_implementation()
                if index is indices[0]
                else right._set_implementation()
            ),
        )
        assert ProductElements().contains_product_element(pair)
        return self._relation.membership(pair)

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
    morphism: SetMorphism,
) -> Decision:
    underlying_set = PartiallyOrderedSets().underlying_set(source)
    if underlying_set.is_finite() is not True:
        return UNKNOWN
    decision: Decision = True
    forgetful = PartiallyOrderedSets().forgetful_functor()
    for left in source:
        assert is_poset_element(left)
        set_left = forgetful.on_element(source, left)
        assert SetElements().contains_set_element(set_left)
        f_left = target.element(morphism(set_left))
        assert is_poset_element(f_left)
        assert f_left in target
        for right in source:
            assert is_poset_element(right)
            set_right = forgetful.on_element(source, right)
            assert SetElements().contains_set_element(set_right)
            f_right = target.element(morphism(set_right))
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

        order_preserving = check_order_preserving(source, target, underlying)
        assert order_preserving is True, f"candidate map from {source} to {target} is not order preserving (decision={order_preserving})"

        return self._construct(underlying)

    def _construct(self, underlying: SetMorphism) -> PosetMorphism:
        assert Sets().contains_set_morphism(underlying)
        assert underlying.domain() is PartiallyOrderedSets().underlying_set(self.domain())
        assert underlying.codomain() is PartiallyOrderedSets().underlying_set(self.codomain())
        return self.ObjectType(
            hom_category=self,
            underlying_function=underlying,
        )

    def from_theorem(
        self,
        underlying: SetMorphism,
        owner: MathematicalObject,
    ) -> PosetMorphism:
        """Construct a morphism established by the owning construction."""
        assert registered_value(owner) is owner
        return self._construct(underlying)

    def from_hypothesis(
        self,
        underlying: SetMorphism,
        hypothesis: Hypothesis,
        assumptions: HypothesisContext,
    ) -> PosetMorphism:
        """Construct a morphism under an active monotonicity hypothesis."""
        assert hypothesis.category() is self
        assert hypothesis.candidate() is underlying
        assert assumptions.establishes(hypothesis) is True
        return self._construct(underlying)

    def identity(self) -> PosetMorphism:
        assert self.domain() is self.codomain()
        category = self.base_category()
        assert is_partially_ordered_sets_category(category)
        source = self.domain()
        assert PartiallyOrderedSets().contains_poset(source)
        underlying = Sets().identity(PartiallyOrderedSets().underlying_set(source))
        assert Sets().contains_set_morphism(underlying)
        return self.from_theorem(underlying, self)

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
        return self.from_theorem(underlying, self)

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
        return element._set_implementation()

    def is_faithful(self) -> bool:
        return True


class PosetProductLiftFunctor(ConstructionLiftFunctor):
    """Lift product-cone set arrows by the componentwise-order theorem."""

    def _lifted_morphism(
        self,
        source: MathematicalObject,
        target: MathematicalObject,
        image: Arrow,
    ) -> PosetMorphism:
        assert Sets().contains_set_morphism(image)
        hom = PartiallyOrderedSets().Hom(source, target)
        return hom.from_theorem(image, PartiallyOrderedSets())


class PartiallyOrderedSetsCategory(Category):
    """Sets equipped with a chosen partial order."""

    ObjectType = PosetObject
    ElementType = PosetElement
    ArrowType = PosetMorphism

    def __init__(self) -> None:
        self._forgetful_functor: ForgetPosetFunctor | None = None
        self._finite_posets: FinitePosetsCategory | None = None
        super().__init__()

    def __call__(
        self,
        underlying_set: SetObject,
        relation: OrderRelation,
    ) -> PosetObject:
        candidate = self._construct(underlying_set, relation)
        reflexive = check_reflexive(candidate, underlying_set)
        antisymmetric = check_antisymmetric(candidate, underlying_set)
        transitive = check_transitive(candidate, underlying_set)
        assert reflexive is True, f"relation on {underlying_set} is not established as reflexive (decision={reflexive})"
        assert antisymmetric is True, f"relation on {underlying_set} is not established as antisymmetric (decision={antisymmetric})"
        assert transitive is True, f"relation on {underlying_set} is not established as transitive (decision={transitive})"
        return self._strongest_result(candidate, underlying_set)

    def _construct(
        self,
        underlying_set: SetObject,
        relation: OrderRelation,
    ) -> PosetObject:
        assert underlying_set in Sets()
        return self.ObjectType(
            category=self,
            underlying_set=underlying_set,
            relation=relation,
        )

    def _strongest_result(
        self,
        candidate: PosetObject,
        underlying_set: SetObject,
    ) -> PosetObject:
        if underlying_set in FiniteSets():
            return self.Finite().refine_from_theorem(candidate, self)
        return candidate

    def discrete_order(self, underlying_set: SetObject) -> PosetObject:
        """Return the discrete poset on ``underlying_set`` with equality order."""
        assert underlying_set in Sets()
        return self.from_theorem(
            underlying_set,
            Sets().relation(
                underlying_set,
                Sets().binary_predicate(
                    underlying_set,
                    lambda left, right: left == right,
                ),
            ),
            self,
        )

    def from_theorem(
        self,
        underlying_set: SetObject,
        relation: OrderRelation,
        owner: MathematicalObject,
    ) -> PosetObject:
        """Construct a poset whose order laws follow from its owner."""
        assert registered_value(owner) is owner
        candidate = self._construct(underlying_set, relation)
        return self._strongest_result(candidate, underlying_set)

    def from_hypothesis(
        self,
        underlying_set: SetObject,
        relation: OrderRelation,
        hypothesis: Hypothesis,
        assumptions: HypothesisContext,
    ) -> PosetObject:
        """Construct a poset under active partial-order hypotheses."""
        assert hypothesis.category() is self
        assert hypothesis.candidate() is relation
        assert assumptions.establishes(hypothesis) is True
        candidate = self._construct(underlying_set, relation)
        return self._strongest_result(candidate, underlying_set)

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
        return self.from_theorem(underlying_set, relation, self)

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
            PosetProductLiftFunctor(forgetful),
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
        return self.from_theorem(underlying_set, relation, self)

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

    def transported_relation(left: SetElement, right: SetElement) -> Decision:
        return relation(left.value(), right.value())

    poset = PartiallyOrderedSets()(
        underlying_set,
        Sets().relation(
            underlying_set,
            Sets().binary_predicate(underlying_set, transported_relation),
        ),
    )
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
