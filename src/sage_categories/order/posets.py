"""Sets equipped with a binary relation, and their partial-order subcategory.

An object of ``BinaryRelations()`` is a set ``X`` together with the data of a
relation ``R <= X * X`` (Mathlib ``CategoryTheory`` relation objects; a poset is a
set with such data, not a relation).  Its structure functor to ``Sets()`` forgets the
relation, so a relation object inherits point, map, and set behavior from its carrier.
``Posets()`` is the ``PartialOrder`` property subcategory of ``BinaryRelations()``.
"""

from __future__ import annotations

__all__ = [
    "BinaryRelations",
    "BinaryRelationsCategory",
    "FiniteGradedPosetsCategory",
    "FinitePosets",
    "FinitePosetsCategory",
    "FinitePosetsWithBottomCategory",
    "FinitePosetsWithTopCategory",
    "FiniteRankedPosetsCategory",
    "FiniteTotallyOrderedSets",
    "FiniteTotallyOrderedSetsCategory",
    "Posets",
    "PosetsCategory",
    "Thin",
    "TotallyOrderedSets",
    "order_preserving",
]

from collections.abc import Callable

from sympy import ask as sympy_ask
from sympy import false, true
from sympy.logic.boolalg import Boolean

from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.cones import LimitConesCategory
from sage_categories.cat.declarations import Sets
from sage_categories.cat.functors import Cat, Fun, Functor
from sage_categories.cat.leaf_categories import FaithfulStructureCategory
from sage_categories.cat.morphisms import Mor, MorphismCategory
from sage_categories.cat.predicates import (
    Axiom,
    Predicate,
    Proposition,
    conjunction,
    disjunction,
    implication,
    register_handler,
)
from sage_categories.cat.properties import PropertySubcategory
from sage_categories.cat.shapes import Discrete, ThinCategory
from sage_categories.cat.slices import SliceProperty
from sage_categories.order._firewall import finite_posets as _finite_posets_firewall
from sage_categories.sets.cardinals import Cardinal, CardinalCategory
from sage_categories.sets.finite import SetsCategory

type OrderRule = Callable[[CategoryOfCategories.ElementType, CategoryOfCategories.ElementType], Proposition]


class _OrderRelatedPredicate(Predicate):
    name = "order_related"


class _PartialOrderPredicate(Predicate):
    name = "partial_order"


class _TotalOrderPredicate(Predicate):
    name = "total_order"


class _OrderPreservingPredicate(Predicate):
    name = "order_preserving"


class _CoverPredicate(Predicate):
    name = "covers"


class _RankedPredicate(Predicate):
    name = "ranked"


class _GradedPredicate(Predicate):
    name = "graded"


class _HasBottomPredicate(Predicate):
    name = "has_bottom"


class _HasTopPredicate(Predicate):
    name = "has_top"


order_related = _OrderRelatedPredicate()
partial_order = _PartialOrderPredicate()
total_order = _TotalOrderPredicate()
order_preserving = _OrderPreservingPredicate()
covers = _CoverPredicate()
ranked = _RankedPredicate()
graded = _GradedPredicate()
has_bottom = _HasBottomPredicate()
has_top = _HasTopPredicate()


def _square_factor(square: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
    """The set ``X`` of a chosen set product ``X * X``, read from its presenting diagrams.

    One chosen set can present several diagrams: the pair space of a two-element carrier
    is also the product of two two-element chains, so ``ApexCategory.presentation`` names
    both and directs the caller to the diagrams themselves (``cat/constructions.py``).
    """
    family = Sets.Products().presenting_family(square)
    factors = tuple(diagram.on_object(diagram.domain()(0)) for diagram in family.presenting_diagrams(square))
    assert all(factor is factors[0] for factor in factors), f"{square!r} presents products of unequal sets"
    return factors[0]


def _decide_order_related(
    first: CategoryOfCategories.ElementType,
    second: CategoryOfCategories.ElementType,
    assumptions: Proposition,
) -> bool | None:
    """Whether the ordered pair ``(first, second)`` lies in its object's relation.

    Membership is asked of the represented relation subobject itself.  This keeps
    predicate-defined infinite relations nonenumerative and preserves an undecided
    membership proposition when their predicate is undecided.
    """
    relation_object = first.parent()
    if second.parent() is not relation_object:
        return False
    relation = relation_object.relation()
    ambient = relation.arrow().codomain()
    selected = relation.arrow().domain()
    pair = ambient.point((first.datum(), second.datum()))
    decision = sympy_ask(selected.membership_proposition(pair), assumptions)
    return None if decision is None else bool(decision)


def _decide_partial_order(
    relation_object: BinaryRelationsCategory.ObjectType,
    assumptions: Proposition,
) -> bool | None:
    """Reflexivity, antisymmetry, and transitivity of a finite relation (Mathlib ``PartialOrder``)."""
    return _finite_posets_firewall.partial_order(relation_object)


class BinaryRelationsCategory(FaithfulStructureCategory):
    """Sets equipped with a binary endorelation, and relation-preserving maps."""

    class ObjectType:
        def __init__(self, relation: CategoryOfCategories.ElementType) -> None:
            self._relation = relation
            self._carrier = _square_factor(relation.arrow().codomain())

        def relation(self) -> CategoryOfCategories.ElementType:
            return self._relation

        def carrier(self) -> CategoryOfCategories.ElementType:
            return self._carrier

        def related(
            self,
            first: CategoryOfCategories.ElementType,
            second: CategoryOfCategories.ElementType,
        ) -> Proposition:
            """The proposition that ``first`` and ``second`` stand in the relation."""
            return order_related(first, second)

    class ElementType:
        """A point of the carrier, inherited through the structure functor to ``Sets()``."""

    class MorphismType:
        def __init__(self, underlying: MorphismCategory.ObjectType) -> None:
            self._underlying_map = underlying

        def underlying_map(self) -> MorphismCategory.ObjectType:
            return self._underlying_map

    def _partial_order(self, relation_object: BinaryRelationsCategory.ObjectType) -> Proposition:
        return partial_order(relation_object)

    PartialOrder = Axiom(_partial_order)

    def __repr__(self) -> str:
        return "BinaryRelations"

    def __call__(self, relation: CategoryOfCategories.ElementType) -> BinaryRelationsCategory.ObjectType:
        return self.ObjectType(relation)

    def from_predicate(
        self,
        carrier: CategoryOfCategories.ElementType,
        rule: OrderRule,
    ) -> BinaryRelationsCategory.ObjectType:
        """The relation object whose relation ``rule`` selects in ``carrier * carrier``."""
        product = Sets.Products()((carrier, carrier))

        def pair_rule(pair: CategoryOfCategories.ElementType) -> Boolean:
            first, second = pair.datum()
            return rule(carrier.point(first), carrier.point(second))

        subobject = Sets.Subobjects(product).from_predicate(pair_rule)
        return self.ObjectType(subobject)

    def lift_order(
        self,
        diagram: Functor,
        presentation: LimitConesCategory.ObjectType,
    ) -> BinaryRelationsCategory.ObjectType:
        """The componentwise order on the selected set-limit apex: ``x <= y`` iff every leg compares."""
        shape = diagram.domain()
        vertices = tuple(shape(label) for label in shape.labels())

        def componentwise(
            first: CategoryOfCategories.ElementType,
            second: CategoryOfCategories.ElementType,
        ) -> Proposition:
            def compares(vertex: CategoryOfCategories.ElementType) -> Proposition:
                factor, leg = diagram.on_object(vertex), presentation.leg(vertex)
                return factor.related(factor.point(leg(first).datum()), factor.point(leg(second).datum()))

            return conjunction(compares(vertex) for vertex in vertices)

        return self.from_predicate(presentation.apex(), componentwise)

    def transport(
        self,
        relation_object: BinaryRelationsCategory.ObjectType,
        bijection: MorphismCategory.ObjectType,
    ) -> BinaryRelationsCategory.MorphismType:
        """Transport a relation along a retained set isomorphism (D183).

        The inverse is supplied by the isomorphism itself.  No carrier is enumerated:
        ``y S y'`` is defined by ``f^-1(y) R f^-1(y')`` pointwise, so this works equally
        for finite, infinite and predicate-defined carriers.
        """
        carrier = relation_object.carrier()
        assert bijection.domain() is carrier, f"{bijection!r} does not start at the carrier of {relation_object!r}"
        inverse = bijection.inverse()
        image = bijection.codomain()
        assert inverse.domain() is image and inverse.codomain() is carrier

        def transported_rule(
            first: CategoryOfCategories.ElementType,
            second: CategoryOfCategories.ElementType,
        ) -> Proposition:
            return relation_object.related(
                relation_object.point(inverse(first).datum()),
                relation_object.point(inverse(second).datum()),
            )

        transported = self.from_predicate(image, transported_rule)
        # Preservation in both directions is the defining equation above, so this
        # named transport must not re-enumerate the source relation merely to
        # rediscover it pointwise.
        forward = self._morphism_from_data(relation_object, transported, bijection)
        backward = self._morphism_from_data(transported, relation_object, inverse)
        self.retain_inverses(forward, backward)
        return forward

    def to_sets(self) -> Functor:
        """The faithful isofibration ``(X, R) |-> X`` forgetting the relation (D163).

        It carries the chosen lift of a discrete set limit: the componentwise order on
        the selected set apex (D183, ``specs/ordered-sets.md``, "Products").
        """
        return next(functor for functor in self.selected_functors() if functor.codomain() is Sets)

    def structure_functors(self) -> tuple[Functor, ...]:
        underlying = (
            Fun(self, Sets)
            .Faithful()
            .Isofibrations()(
                lambda relation_object: relation_object.carrier(),
                lambda arrow: arrow.underlying_map(),
            )
            .with_limit_lifting(Discrete, self.lift_order, self.construct_morphism)
        )
        return (underlying,)

    def construct_morphism(
        self,
        source: BinaryRelationsCategory.ObjectType,
        target: BinaryRelationsCategory.ObjectType,
        underlying: MorphismCategory.ObjectType,
    ) -> BinaryRelationsCategory.MorphismType:
        source_carrier, target_carrier = source.carrier(), target.carrier()
        assert underlying.domain() is source_carrier and underlying.codomain() is target_carrier
        assert sympy_ask(order_preserving(source, target, underlying)) is True, f"{underlying!r} is not established to preserve the relation of {source!r}"
        return self._morphism_from_data(source, target, underlying)


class PosetsCategory(PropertySubcategory):
    """``BinaryRelations().PartialOrder()``: relation objects whose relation is a partial order."""

    _base_category_class_and_axiom = (BinaryRelationsCategory, "PartialOrder")

    class ObjectType:
        """A partial order: a relation object satisfying the order laws (POL-CAT-079)."""

    class ElementType:
        """A point of a poset, comparable through its owned order."""

        def __le__(self, other: CategoryOfCategories.ElementType) -> Proposition:
            return self.parent().related(self, other)

    class MorphismType:
        """A monotone map: a relation-preserving map between two posets."""

    def _total(self, poset_object: CategoryOfCategories.ElementType) -> Proposition:
        return total_order(poset_object)

    Total = Axiom(_total)

    def to_sets(self) -> Functor:
        """The underlying-set functor ``U: Posets() -> Sets()``.

        ``Posets()`` is the full partial-order subcategory of ``BinaryRelations()``;
        restricting the relation projection is therefore the one owned underlying-set
        functor, with no second object or morphism action in the poset leaf.
        """
        return BinaryRelations().to_sets().restrict(self, Sets)

    Finite = SetsCategory.Finite.inverse_image(lambda category: category.to_sets())

    def subobjects_type(self) -> type[PosetSubobjects]:
        """The induced-poset realization of ``Posets().Subobjects(P)``."""
        return PosetSubobjects


class PosetSubobjects(SliceProperty):
    """Induced subposets of one fixed ambient poset, with their retained inclusions."""

    class ObjectType:
        """An induced subposet together with its monomorphism into the fixed poset."""

    class ElementType:
        """A generalized element inherited from the subobject category."""

    class MorphismType:
        """A commuting triangle between induced subposets."""

    def from_predicate(
        self,
        predicate: Callable[[PosetsCategory.ElementType], Proposition],
    ) -> PosetSubobjects.ObjectType:
        """Construct the induced subposet selected by ``predicate`` and its inclusion.

        The carrier is the owned predicate subobject of the exact ambient carrier.  The
        order is the restriction of the ambient order along that set inclusion, and the
        resulting poset inclusion retains that same set map as its underlying morphism.
        No backend or Python collection is the public subobject.
        """
        ambient = self.ambient().fixed_object()
        carrier_subobjects = Sets.Subobjects(ambient.carrier())
        carrier_subobject = carrier_subobjects.from_predicate(lambda point: predicate(ambient.point(point.datum())))
        carrier_inclusion = carrier_subobjects.defining_arrow().on_object(carrier_subobject)
        selected_carrier = carrier_inclusion.domain()

        def induced_order(
            first: CategoryOfCategories.ElementType,
            second: CategoryOfCategories.ElementType,
        ) -> Proposition:
            return ambient.related(
                ambient.point(carrier_inclusion(first).datum()),
                ambient.point(carrier_inclusion(second).datum()),
            )

        induced_relation = BinaryRelations().from_predicate(selected_carrier, induced_order)
        match sympy_ask(Sets.Finite().membership_proposition(selected_carrier)):
            case True:
                induced = FinitePosets()(induced_relation.relation())
            case _:
                induced = Posets()(induced_relation.relation())
        inclusion = BinaryRelations()._morphism_from_data(induced, ambient, carrier_inclusion)
        return self(inclusion)


def _strictly_less(
    first: PosetsCategory.ElementType,
    second: PosetsCategory.ElementType,
) -> Proposition:
    """Strict order expressed through the owned order and equality predicates."""
    return (first <= second) & ~(first == second)


def _owned_subobject_inclusion(
    ambient: FinitePosetsCategory.ObjectType,
    members: PosetSubobjects.ObjectType,
) -> MorphismCategory.ObjectType:
    """The retained inclusion of an owned subobject of ``ambient``."""
    subobjects = Posets().Subobjects(ambient)
    assert members in subobjects, f"{members!r} is not an owned subobject of {ambient!r}"
    inclusion = subobjects.defining_arrow().on_object(members)
    assert inclusion.codomain() is ambient
    return inclusion


def _owned_subobject_members(
    ambient: FinitePosetsCategory.ObjectType,
    members: PosetSubobjects.ObjectType,
) -> tuple[FinitePosetsCategory.ElementType, ...]:
    """The selected ambient elements of an owned finite subobject."""
    inclusion = _owned_subobject_inclusion(ambient, members)
    return tuple(inclusion(member) for member in inclusion.domain())


class FinitePosetsCategory(Category):
    """The implementation surface of the exact derived category ``Posets().Finite()``.

    The category itself is the inverse image selected by ``PosetsCategory.Finite``.
    This implementation claims that exact value in place so finite-poset operations can
    live on its three ordinary roles without constructing a second property category.
    """

    class ObjectType:
        """A finite poset; finite algorithms are owned by this role."""

        def covers(
            self,
            lower: FinitePosetsCategory.ElementType,
            upper: FinitePosetsCategory.ElementType,
        ) -> Proposition:
            """The proposition that ``upper`` covers ``lower``."""
            assert lower.parent() is self and upper.parent() is self
            return covers(self, lower, upper)

        def height(self) -> CardinalCategory.ObjectType:
            """The owned cardinality of a largest chain."""
            value = _finite_posets_firewall.height(self)
            assert value is not None
            return Cardinal()(value)

        def width(self) -> CardinalCategory.ObjectType:
            """The owned cardinality of a largest antichain."""
            value = _finite_posets_firewall.width(self)
            assert value is not None
            return Cardinal()(value)

        def linear_extension(self) -> FiniteTotallyOrderedSetsCategory.ObjectType:
            """A finite total order on this exact carrier extending the source order."""
            carrier = self.carrier()
            relation = BinaryRelations().from_predicate(
                carrier,
                lambda first, second: (
                    true
                    if _finite_posets_firewall.linear_extension_leq(
                        self,
                        self.point(first.datum()),
                        self.point(second.datum()),
                    )
                    else false
                ),
            )
            return FiniteTotallyOrderedSets()(relation.relation())

        def lower_covers(self, member: FinitePosetsCategory.ElementType) -> PosetSubobjects.ObjectType:
            """The induced subposet of elements covered by ``member``."""
            assert member.parent() is self
            return Posets().Subobjects(self).from_predicate(lambda candidate: self.covers(candidate, member))

        def upper_covers(self, member: FinitePosetsCategory.ElementType) -> PosetSubobjects.ObjectType:
            """The induced subposet of elements covering ``member``."""
            assert member.parent() is self
            return Posets().Subobjects(self).from_predicate(lambda candidate: self.covers(member, candidate))

        def open_interval(
            self,
            lower: FinitePosetsCategory.ElementType,
            upper: FinitePosetsCategory.ElementType,
        ) -> PosetSubobjects.ObjectType:
            """The induced open interval ``{z : lower < z < upper}``."""
            assert lower.parent() is self and upper.parent() is self
            return Posets().Subobjects(self).from_predicate(lambda candidate: conjunction((_strictly_less(lower, candidate), _strictly_less(candidate, upper))))

        def closed_interval(
            self,
            lower: FinitePosetsCategory.ElementType,
            upper: FinitePosetsCategory.ElementType,
        ) -> PosetSubobjects.ObjectType:
            """The induced closed interval ``{z : lower <= z <= upper}``."""
            assert lower.parent() is self and upper.parent() is self
            return Posets().Subobjects(self).from_predicate(lambda candidate: conjunction((lower <= candidate, candidate <= upper)))

        def principal_order_ideal(
            self,
            member: FinitePosetsCategory.ElementType,
        ) -> PosetSubobjects.ObjectType:
            """The principal order ideal ``{z : z <= member}``."""
            assert member.parent() is self
            return Posets().Subobjects(self).from_predicate(lambda candidate: candidate <= member)

        def principal_order_filter(
            self,
            member: FinitePosetsCategory.ElementType,
        ) -> PosetSubobjects.ObjectType:
            """The principal order filter ``{z : member <= z}``."""
            assert member.parent() is self
            return Posets().Subobjects(self).from_predicate(lambda candidate: member <= candidate)

        def common_lower_covers(
            self,
            members: PosetSubobjects.ObjectType,
        ) -> PosetSubobjects.ObjectType:
            """The elements covered by every member of the supplied owned subobject."""
            selected = _owned_subobject_members(self, members)
            return Posets().Subobjects(self).from_predicate(lambda candidate: conjunction(self.covers(candidate, member) for member in selected))

        def common_upper_covers(
            self,
            members: PosetSubobjects.ObjectType,
        ) -> PosetSubobjects.ObjectType:
            """The elements covering every member of the supplied owned subobject."""
            selected = _owned_subobject_members(self, members)
            return Posets().Subobjects(self).from_predicate(lambda candidate: conjunction(self.covers(member, candidate) for member in selected))

        def order_ideal(
            self,
            members: PosetSubobjects.ObjectType,
        ) -> PosetSubobjects.ObjectType:
            """The down-closure of the supplied owned subobject."""
            selected = _owned_subobject_members(self, members)
            return Posets().Subobjects(self).from_predicate(lambda candidate: disjunction(candidate <= member for member in selected))

        def order_filter(
            self,
            members: PosetSubobjects.ObjectType,
        ) -> PosetSubobjects.ObjectType:
            """The up-closure of the supplied owned subobject."""
            selected = _owned_subobject_members(self, members)
            return Posets().Subobjects(self).from_predicate(lambda candidate: disjunction(member <= candidate for member in selected))

        def minimal_elements(self) -> PosetSubobjects.ObjectType:
            """The induced subposet of minimal elements."""
            return Posets().Subobjects(self).from_predicate(lambda candidate: conjunction(~_strictly_less(other, candidate) for other in self))

        def maximal_elements(self) -> PosetSubobjects.ObjectType:
            """The induced subposet of maximal elements."""
            return Posets().Subobjects(self).from_predicate(lambda candidate: conjunction(~_strictly_less(candidate, other) for other in self))

        def is_chain_of_poset(self, members: PosetSubobjects.ObjectType) -> Proposition:
            """Chainhood is totality of the induced order on the owned subobject."""
            return _owned_subobject_inclusion(self, members).domain().is_total()

        def is_antichain_of_poset(self, members: PosetSubobjects.ObjectType) -> Proposition:
            """Antichainhood is equality of the induced order with equality."""
            induced = _owned_subobject_inclusion(self, members).domain()
            points = tuple(induced)
            return conjunction(
                conjunction(
                    (
                        implication(first <= second, first == second),
                        implication(first == second, first <= second),
                    )
                )
                for first in points
                for second in points
            )

    class ElementType:
        """An element inherited from the ambient poset."""

    class MorphismType:
        """A monotone map between finite posets."""

    def _ranked(self, poset_object: FinitePosetsCategory.ObjectType) -> Proposition:
        return ranked(poset_object)

    def _graded(self, poset_object: FinitePosetsCategory.ObjectType) -> Proposition:
        return graded(poset_object)

    def _with_bottom(self, poset_object: FinitePosetsCategory.ObjectType) -> Proposition:
        return has_bottom(poset_object)

    def _with_top(self, poset_object: FinitePosetsCategory.ObjectType) -> Proposition:
        return has_top(poset_object)

    Ranked = Axiom(_ranked)
    Graded = Axiom(_graded, full_subcategory_of=(Ranked,))
    WithBottom = Axiom(_with_bottom)
    WithTop = Axiom(_with_top)

    def structure_functors(self) -> tuple[Functor, ...]:
        finite_posets = FinitePosets()
        return (Fun(finite_posets, finite_posets).one(),)


class FiniteRankedPosetsCategory(PropertySubcategory):
    """Finite ranked posets and their rank-valued operations."""

    _base_category_class_and_axiom = (FinitePosetsCategory, "Ranked")

    class ObjectType:
        def rank_of_element(
            self,
            member: FinitePosetsCategory.ElementType,
        ) -> CardinalCategory.ObjectType:
            """The owned natural cardinal rank of ``member``."""
            assert member.parent() is self
            return Cardinal()(_finite_posets_firewall.rank_of_element(self, member))

        def rank(self) -> CardinalCategory.ObjectType:
            """The maximum element rank of a nonempty finite ranked poset."""
            assert len(self) > 0, "the rank of the empty poset is not defined"
            return Cardinal()(_finite_posets_firewall.rank(self))

        def level_sets(self) -> Functor:
            """The rank-level predicate subobjects as an owned discrete indexed family."""
            rank_value = int(self.rank())
            indices = Sets(tuple(range(rank_value + 1)))
            shape = Discrete.on_object(indices)
            subobjects = Posets().Subobjects(self)

            def level(vertex: CategoryOfCategories.ElementType) -> PosetSubobjects.ObjectType:
                target_rank = Cardinal()(int(vertex.point().datum()))
                return subobjects.from_predicate(lambda member: self.rank_of_element(member) == target_rank)

            return Fun(shape, subobjects).from_object_rule(level)

    class ElementType:
        """An element of a ranked finite poset."""

    class MorphismType:
        """A monotone morphism between ranked finite posets."""


class FiniteGradedPosetsCategory(PropertySubcategory):
    """Finite graded posets; grading implies rankedness and adds no new operation."""

    _base_category_class_and_axiom = (FinitePosetsCategory, "Graded")

    class ObjectType:
        """A finite graded poset."""

    class ElementType:
        """An element of a finite graded poset."""

    class MorphismType:
        """A monotone morphism between finite graded posets."""


class FinitePosetsWithBottomCategory(PropertySubcategory):
    """Finite posets with a bottom element."""

    _base_category_class_and_axiom = (FinitePosetsCategory, "WithBottom")

    class ObjectType:
        def bottom(self) -> FinitePosetsCategory.ElementType:
            return self.point(_finite_posets_firewall.bottom(self))

    class ElementType:
        """An element of a finite poset with bottom."""

    class MorphismType:
        """A monotone morphism between finite posets with bottom."""


class FinitePosetsWithTopCategory(PropertySubcategory):
    """Finite posets with a top element."""

    _base_category_class_and_axiom = (FinitePosetsCategory, "WithTop")

    class ObjectType:
        def top(self) -> FinitePosetsCategory.ElementType:
            return self.point(_finite_posets_firewall.top(self))

    class ElementType:
        """An element of a finite poset with top."""

    class MorphismType:
        """A monotone morphism between finite posets with top."""


class FiniteTotallyOrderedSetsCategory(Category):
    """The implementation surface of the exact finite-total-order narrowing."""

    class ObjectType:
        """A finite total order."""

    class ElementType:
        """An element of a finite total order."""

    class MorphismType:
        """A monotone map between finite total orders."""

    def structure_functors(self) -> tuple[Functor, ...]:
        category = FiniteTotallyOrderedSets()
        return (Fun(category, category).one(),)


_BINARY_RELATIONS = BinaryRelationsCategory()


def BinaryRelations() -> BinaryRelationsCategory:
    """The category of sets equipped with a binary relation."""
    return _BINARY_RELATIONS


def Posets() -> Category:
    """The category of partial orders: ``BinaryRelations().PartialOrder()``."""
    return BinaryRelations().PartialOrder()


def TotallyOrderedSets() -> Category:
    """The category of total orders: ``Posets().Total()``."""
    return Posets().Total()


def FinitePosets() -> FinitePosetsCategory:
    """Finite posets: ``U.inverse_image(Sets().Finite())`` for ``U: Posets() -> Sets()``."""
    return Posets().Finite()


def FiniteTotallyOrderedSets() -> FiniteTotallyOrderedSetsCategory:
    """Finite total orders: the finite inverse image along ``TotallyOrderedSets() -> Posets()``."""
    return TotallyOrderedSets().Finite()


def _decide_total_order(
    poset_object: BinaryRelationsCategory.ObjectType,
    assumptions: Proposition,
) -> bool | None:
    """Totality of a finite order through Sage's finite-poset implementation."""
    return _finite_posets_firewall.total_order(poset_object)


def _decide_order_preserving(
    source: BinaryRelationsCategory.ObjectType,
    target: BinaryRelationsCategory.ObjectType,
    underlying: MorphismCategory.ObjectType,
    assumptions: Proposition,
) -> bool | None:
    """Exact finite monotonicity, delegated to the private finite-order boundary."""
    return _finite_posets_firewall.order_preserving(source, target, underlying, assumptions)


def _decide_covers(
    poset_object: FinitePosetsCategory.ObjectType,
    lower: FinitePosetsCategory.ElementType,
    upper: FinitePosetsCategory.ElementType,
    assumptions: Proposition,
) -> bool | None:
    return _finite_posets_firewall.covers(poset_object, lower, upper)


def _decide_ranked(
    poset_object: FinitePosetsCategory.ObjectType,
    assumptions: Proposition,
) -> bool | None:
    return _finite_posets_firewall.is_ranked(poset_object)


def _decide_graded(
    poset_object: FinitePosetsCategory.ObjectType,
    assumptions: Proposition,
) -> bool | None:
    return _finite_posets_firewall.is_graded(poset_object)


def _decide_has_bottom(
    poset_object: FinitePosetsCategory.ObjectType,
    assumptions: Proposition,
) -> bool | None:
    return _finite_posets_firewall.has_bottom(poset_object)


def _decide_has_top(
    poset_object: FinitePosetsCategory.ObjectType,
    assumptions: Proposition,
) -> bool | None:
    return _finite_posets_firewall.has_top(poset_object)


register_handler(order_related, _decide_order_related)
register_handler(partial_order, _decide_partial_order)
register_handler(total_order, _decide_total_order)
register_handler(order_preserving, _decide_order_preserving)
register_handler(covers, _decide_covers)
register_handler(ranked, _decide_ranked)
register_handler(graded, _decide_graded)
register_handler(has_bottom, _decide_has_bottom)
register_handler(has_top, _decide_has_top)
Cat().implement(FinitePosetsCategory)
Cat().implement(FiniteTotallyOrderedSetsCategory)


def _thin_category(poset_object: BinaryRelationsCategory.ObjectType) -> ThinCategory:
    """The thin category of a poset: its points, one arrow ``x -> y`` exactly when ``x <= y``."""
    return ThinCategory(poset_object, order_related)


def _thin_functor(monotone: BinaryRelationsCategory.MorphismType) -> Functor:
    """The functor a monotone map induces: a point to its image, a comparison to the compared images."""
    source, target = Thin.on_object(monotone.domain()), Thin.on_object(monotone.codomain())

    def on_object(member_object: ThinCategory.ObjectType) -> ThinCategory.ObjectType:
        return target(monotone(member_object.point()))

    def on_morphism(comparison: ThinCategory.MorphismType) -> ThinCategory.MorphismType:
        return Mor(target)(on_object(comparison.domain()), on_object(comparison.codomain()))()

    return Fun(source, target)(on_object, on_morphism)


Thin: Functor = Fun(Posets(), Cat())(_thin_category, _thin_functor)
