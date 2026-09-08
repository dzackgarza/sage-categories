"""Sets presented by finite data or membership propositions, and total functions.

The primitive constructions follow Sage's finite enumerated sets and
Mathlib's CategoryTheory.Limits.Types. General finite limits and colimits
are inherited from the product/equalizer calculus in Cat.
"""

from __future__ import annotations

__all__ = ["SetsCategory", "Sets", "FiniteSets", "MapForm", "ObjectForm"]

from collections.abc import Callable, Hashable, Iterable, Iterator, Mapping
from dataclasses import dataclass
from functools import cache
from itertools import islice
from itertools import product as cartesian_product
from typing import Literal, Protocol, overload, runtime_checkable

from sage.rings.integer import Integer as SageInteger
from sage.symbolic.expression import Expression as SageExpression
from sympy import Dummy, Eq, Lambda, Tuple, expand, false, simplify, solve, sympify, true
from sympy import Integer as SympyInteger
from sympy import ask as sympy_ask
from sympy.core.basic import Basic

from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.cones import cone, cone_apex
from sage_categories.cat.declarations import NN, Sets
from sage_categories.cat.functors import Cat, Fun, Functor
from sage_categories.cat.morphisms import Mor, MorphismCategory
from sage_categories.cat.predicates import Axiom, Predicate, Proposition, Unknown, UnknownClass, ask, conjunction, register_handler
from sage_categories.cat.slices import SliceProperty, SliceLikeCategory
from sage_categories.cat.shapes import realize_discrete_object
from sage_categories.kernel.sage_runtime import MonoDict

type Map = Callable[[Hashable], Hashable]
type MembershipRule = Callable[[Hashable], Proposition]
# What a set map can be constructed from: a rule on data, a SymPy ``Lambda`` or Sage callable
# symbolic expression, or a table (``specs/sets.md``, "Morphisms").
type MapData = Map | Lambda | SageExpression | Mapping[Hashable, Hashable]


class FinitePredicate(Predicate):
    name = "finite_set"


class SetMembershipPredicate(Predicate):
    name = "set_membership"


finite_set = FinitePredicate()
set_membership = SetMembershipPredicate()


def _equal_datum(first: Hashable, second: Hashable) -> bool:
    if first is second:
        return True
    if isinstance(first, CategoryOfCategories.ElementType):
        return (
            isinstance(second, CategoryOfCategories.ElementType)
            and ask(first == second) is True
        )
    if isinstance(first, tuple):
        return (
            isinstance(second, tuple)
            and len(first) == len(second)
            and all(_equal_datum(a, b) for a, b in zip(first, second))
        )
    return first == second


def _datum_membership(value: SetsCategory.ObjectType, datum: Hashable) -> Proposition:
    """The proposition that ``datum`` is a point of ``value``: its rule, or the exact match against its enumeration."""
    presentation = value.set_presentation()
    if isinstance(presentation, tuple):
        return true if any(_equal_datum(candidate, datum) for candidate in presentation) else false
    return presentation(datum)


class _ProductRule:
    """Membership in ``prod_i X_i`` as the conjunction of component memberships; the factors stay readable for symbolic legs."""

    def __init__(self, factors: tuple[SetsCategory.ObjectType, ...]) -> None:
        self.factors = factors

    def __call__(self, datum: Hashable) -> Proposition:
        return conjunction(_datum_membership(factor, component) for factor, component in zip(self.factors, datum, strict=True))


class _PredicateRule:
    """The subset ``{x in X : P(x)}``, retaining its ambient set and predicate."""

    def __init__(self, ambient: SetsCategory.ObjectType, predicate: Callable[[SetsCategory.ElementType], Proposition]) -> None:
        self.ambient, self.predicate = ambient, predicate

    def __call__(self, datum: Hashable) -> Proposition:
        candidate = Sets((datum,)).point(datum)
        return set_membership(Sets.from_membership(self), candidate)


def _finite_data(value: SetsCategory.ObjectType) -> tuple[Hashable, ...] | UnknownClass:
    """Evaluate finite presented sets and decided predicate subsets of them."""
    presentation = value.set_presentation()
    if isinstance(presentation, tuple):
        return presentation
    if isinstance(presentation, _PredicateRule):
        points = Sets.finite_points(presentation.ambient)
        if points is Unknown:
            return Unknown
        decisions = tuple((point, ask(presentation.predicate(point))) for point in points)
        if any(decision is Unknown for _, decision in decisions):
            return Unknown
        return tuple(point.datum() for point, decision in decisions if decision is True)
    return Unknown


# -- symbolic set maps ------------------------------------------------------------------------
#
# A set map always evaluates through a rule on data.  When it was constructed from a SymPy
# ``Lambda`` or a Sage callable symbolic expression, or composed, paired, or projected from
# such maps, it also retains a symbolic form: one SymPy ``Lambda`` in a single argument shaped
# like the domain's data (a symbol, or a ``Tuple`` of factor shapes for a rule-defined
# product).  Equality of two maps on a rule-defined domain is then exact where the retained
# form decides it: a symbolic difference that simplifies to zero, or a witness datum that
# separates them; otherwise it stays undecided (``specs/sets.md``, "Equality").


@runtime_checkable
class MapForm(Protocol):
    """A retained representation of a set map that an engine decides: it evaluates, composes, compares, and may invert.

    A leaf supplies these for the maps its engine understands, such as the integer
    matrices of homomorphisms between presented abelian groups.  ``Sets`` keeps the form
    beside the raw rule and consults it before any enumeration or symbolic reasoning.
    """

    def evaluate(self, datum: Hashable) -> Hashable: ...

    def compose(self, first: MapForm) -> MapForm | None: ...

    def equals(self, other: MapForm) -> bool | None: ...

    def inverse(self) -> MapForm | None: ...


class ObjectForm(Protocol):
    """A retained presentation of a set object, from which ``Sets`` derives the forms of the maps it constructs itself."""

    def identity(self) -> MapForm: ...

    def direct_sum(self, factors: tuple[ObjectForm, ...]) -> ObjectForm: ...

    def projection(self, index: int) -> MapForm: ...

    def pair(self, components: tuple[MapForm, ...], target: ObjectForm) -> MapForm: ...

    def zero_datum(self) -> Hashable: ...

    def zero_map(self, source: ObjectForm) -> MapForm: ...


_object_forms: MonoDict = MonoDict()
_enumerations: MonoDict = MonoDict()
_enumeration_indices: MonoDict = MonoDict()


@dataclass(frozen=True, eq=False, slots=True)
class _SetMap:
    """The evaluation rule of a set map, its symbolic form, and its engine form, each when it has one."""

    action: Map
    rule: Lambda | None
    form: MapForm | None = None


def _form_of(value: SetsCategory.ObjectType) -> ObjectForm | None:
    return _object_forms[value] if value in _object_forms else None


def _composed_form(second: SetsCategory.MorphismType, first: SetsCategory.MorphismType) -> MapForm | None:
    if second._form is None or first._form is None:
        return None
    return second._form.compose(first._form)


def _structure(value: SetsCategory.ObjectType) -> Basic:
    """A fresh symbolic datum of ``value``: a symbol, or the tuple of factor structures of a rule-defined product."""
    presentation = value.set_presentation()
    if isinstance(presentation, _ProductRule):
        return Tuple(*(_structure(factor) for factor in presentation.factors))
    if isinstance(presentation, _PredicateRule):
        return _structure(presentation.ambient)
    return Dummy("x")


def _flatten(structure: Basic) -> tuple[Basic, ...]:
    if isinstance(structure, Tuple):
        return tuple(component for part in structure for component in _flatten(part))
    return (structure,)


def _plain(value: Basic) -> Hashable:
    """A SymPy value as a datum: tuples for ``Tuple``, Python integers for SymPy integers, other expressions as they are."""
    if isinstance(value, Tuple):
        return tuple(_plain(component) for component in value)
    if isinstance(value, SympyInteger):
        return int(value)
    return value


def _sympifiable(datum: Hashable) -> bool:
    if isinstance(datum, tuple):
        return all(_sympifiable(component) for component in datum)
    return isinstance(datum, (int, SageInteger, Basic))


def _symbolic_rule(action: MapData | _SetMap) -> Lambda | None:
    """The symbolic form of a construction input, normalized to one structured argument."""
    if isinstance(action, _SetMap):
        return action.rule
    if isinstance(action, SageExpression):
        if not action.arguments():
            return None
        action = action._sympy_()
    if not isinstance(action, Lambda):
        return None
    if len(action.signature) == 1:
        return action
    return Lambda((Tuple(*action.signature),), action.expr)


def _evaluation(action: MapData | _SetMap, rule: Lambda | None) -> Map:
    """The rule on data a construction input evaluates by: its symbolic form when it has one, its table, or itself."""
    if isinstance(action, _SetMap):
        return action.action
    if rule is not None:
        return lambda datum: _plain(rule(datum))
    if isinstance(action, Mapping):
        return action.__getitem__
    return action


def _constant_rule(source: SetsCategory.ObjectType, datum: Hashable) -> Lambda | None:
    return Lambda((_structure(source),), sympify(datum)) if _sympifiable(datum) else None


def _composed_rule(second: SetsCategory.MorphismType, first: SetsCategory.MorphismType) -> Lambda | None:
    """``g ∘ f`` symbolically: ``g``'s form applied to ``f``'s expression, or a constant when ``g`` leaves a one-point set."""
    if first._symbolic is None:
        return None
    if second._symbolic is not None:
        return Lambda(first._symbolic.signature, second._symbolic(first._symbolic.expr))
    source = second.domain()
    presentation = source.set_presentation()
    if isinstance(presentation, tuple) and len(presentation) == 1:
        value = second._action(presentation[0])
        return Lambda(first._symbolic.signature, sympify(value)) if _sympifiable(value) else None
    return None


def _identically_zero(first: Basic, second: Basic) -> bool:
    """Whether two symbolic values agree as expressions, componentwise on tuples."""
    if isinstance(first, Tuple) or isinstance(second, Tuple):
        return (
            isinstance(first, Tuple)
            and isinstance(second, Tuple)
            and len(first) == len(second)
            and all(_identically_zero(a, b) for a, b in zip(first, second))
        )
    return simplify(expand(first - second)) == 0


def _samples(value: SetsCategory.ObjectType) -> Iterator[Hashable]:
    """A few data of ``value`` to separate maps on: its enumeration, small integers its rule admits, or tuples of factor samples."""
    presentation = value.set_presentation()
    values = _finite_data(value)
    if values is not Unknown:
        return iter(values)
    if isinstance(presentation, _ProductRule):
        return islice(cartesian_product(*(tuple(_samples(factor)) for factor in presentation.factors)), 64)
    if isinstance(presentation, _PredicateRule):
        return (datum for datum in _samples(presentation.ambient) if ask(presentation(datum)) is True)
    return (candidate for candidate in range(-2, 3) if ask(presentation(candidate)) is True)


def _separated(domain: SetsCategory.ObjectType, first: SetsCategory.MorphismType, second: SetsCategory.MorphismType) -> bool:
    """Whether some sample datum of the domain has different images under the two maps."""
    return any(not _equal_datum(first._action(sample), second._action(sample)) for sample in _samples(domain))


def _representative(values: tuple[Hashable, ...], datum: Hashable) -> Hashable:
    for value in values:
        if _equal_datum(value, datum):
            return value
    raise AssertionError(f"{datum!r} is outside the finite codomain")


class SetsCategory(Category[[Map], []]):
    def __repr__(self) -> str:
        return "Sets"

    def structure_functors(self) -> tuple[Functor, ...]:
        return (Fun(Sets, Sets).one(),)

    def _finite(self, value: SetsCategory.ObjectType) -> Proposition:
        return finite_set(value)

    Finite = Axiom(_finite)

    class ObjectType:
        def __init__(self, presentation: tuple[Hashable, ...] | MembershipRule) -> None:
            self._presentation = presentation
            realize_discrete_object(self)

        def set_presentation(self) -> tuple[Hashable, ...] | MembershipRule:
            """The defining ordered finite set data, or the predicate deciding membership."""
            return self._presentation

        @property
        @cache
        def _lookup(self) -> dict[Hashable, Hashable]:
            return {value: value for value in self._values}

        @property
        def _values(self) -> tuple[Hashable, ...]:
            values = _finite_data(self)
            assert values is not Unknown, "this set has no chosen finite enumeration"
            return values

        def representative(self, datum: Hashable) -> Hashable:
            presentation = self.set_presentation()
            if isinstance(presentation, tuple):
                if datum in self._lookup:
                    return self._lookup[datum]
                return _representative(presentation, datum)
            assert ask(presentation(datum)) is True, "set membership is not established"
            return datum

        @cache
        def point(self, datum: Hashable) -> SetsCategory.ElementType:
            datum = self.representative(datum)
            return self.ObjectType(datum)

        def __iter__(self) -> Iterator[SetsCategory.ElementType]:
            return (self.point(value) for value in self._values)

        def __len__(self) -> int:
            return len(self._values)

        def __contains__(self, point: CategoryOfCategories.ElementType) -> bool:
            return ask(self.membership_proposition(point)) is True

        def membership_proposition(self, point: CategoryOfCategories.ElementType) -> Proposition:
            return set_membership(self, point)

        def __repr__(self) -> str:
            return f"Set({self.set_presentation()!r})"

    class ElementType:
        def __init__(self, datum: Hashable) -> None:
            self._datum = datum

        def datum(self) -> Hashable:
            return self._datum

    class MorphismType:
        def __init__(self, data: Map | _SetMap) -> None:
            if isinstance(data, _SetMap):
                self._action, self._symbolic, self._form = data.action, data.rule, data.form
            else:
                self._action, self._symbolic, self._form = data, None, None

        @property
        def _table(self) -> dict[Hashable, Hashable]:
            return {value: self._action(value) for value in self.domain()._values}

        def __call__(
            self, point: CategoryOfCategories.ElementType
        ) -> SetsCategory.ElementType:
            assert point in self.domain()
            return self.codomain().point(self._action(point.datum()))

    def _equal_objects(
        self,
        first: SetsCategory.ObjectType,
        second: SetsCategory.ObjectType,
        assumptions: Proposition,
    ) -> bool | None:
        if not isinstance(first.set_presentation(), tuple) or not isinstance(second.set_presentation(), tuple):
            return None
        return len(first) == len(second) and all(
            any(_equal_datum(a, b) for b in second._values) for a in first._values
        )

    def _equal_morphisms(
        self,
        first: SetsCategory.MorphismType,
        second: SetsCategory.MorphismType,
        assumptions: Proposition,
    ) -> bool | None:
        if first.domain() is not second.domain() or first.codomain() is not second.codomain():
            return False
        domain = first.domain()
        if first._form is not None and second._form is not None:
            decision = first._form.equals(second._form)
            if decision is not None:
                return decision
        values = _finite_data(domain)
        if values is not Unknown:
            from sage_categories.engines import finite_sets

            return finite_sets.equal_morphisms(first, second)
        if domain in _enumerations:
            points = self.finite_points(domain)
            if points is not Unknown:
                return sympy_ask(conjunction(first(point) == second(point) for point in points), assumptions)
        if first._symbolic is not None and second._symbolic is not None:
            argument = _structure(domain)
            if _identically_zero(first._symbolic(argument), second._symbolic(argument)):
                return True
        return False if _separated(domain, first, second) else None

    def _equal_points(
        self,
        first: SetsCategory.ElementType,
        second: SetsCategory.ElementType,
        assumptions: Proposition,
    ) -> bool:
        return first.parent() is second.parent() and _equal_datum(
            first.datum(), second.datum()
        )

    # -- monomorphisms, epimorphisms, isomorphisms (``specs/sets.md``, "Morphisms") ------------

    def _injective(self, arrow: SetsCategory.MorphismType, assumptions: Proposition) -> bool | None:
        """Monic: no two points identified, read off the table, a separating pair of samples, or the solved inverse."""
        if isinstance(arrow.domain().set_presentation(), tuple):
            from sage_categories.engines import finite_sets

            return finite_sets.is_monomorphism(arrow)
        samples = tuple(islice(_samples(arrow.domain()), 16))
        images = tuple(arrow._action(sample) for sample in samples)
        if any(_equal_datum(images[i], images[j]) for i in range(len(images)) for j in range(i)):
            return False
        return self._symbolic_injective(arrow)

    def _surjective(self, arrow: SetsCategory.MorphismType, assumptions: Proposition) -> bool | None:
        """Epic: every codomain point is a value, read off the tables or from the solved inverse."""
        if isinstance(arrow.domain().set_presentation(), tuple) and isinstance(arrow.codomain().set_presentation(), tuple):
            from sage_categories.engines import finite_sets

            return finite_sets.is_epimorphism(arrow)
        return self._symbolic_surjective(arrow)

    def _bijective(self, arrow: SetsCategory.MorphismType, assumptions: Proposition) -> bool | None:
        if arrow._form is not None and arrow._form.inverse() is not None:
            return True
        injective, surjective = self._injective(arrow, assumptions), self._surjective(arrow, assumptions)
        return None if injective is None or surjective is None else injective and surjective

    def _symbolic_injective(self, arrow: SetsCategory.MorphismType) -> bool | None:
        """``f(x) = f(y)`` has only the solution ``y = x``: solved symbolically for a map out of a rule-defined set."""
        if arrow._symbolic is None or isinstance(arrow.domain().set_presentation(), tuple):
            return None
        first, second = _structure(arrow.domain()), _structure(arrow.domain())
        unknowns = _flatten(second)
        equations = [Eq(left, right) for left, right in zip(_flatten(arrow._symbolic(first)), _flatten(arrow._symbolic(second)))]
        solutions = solve(equations, list(unknowns), dict=True)
        if len(solutions) != 1 or set(solutions[0]) != set(unknowns):
            return None
        return True if all(solutions[0][symbol] == original for symbol, original in zip(unknowns, _flatten(first))) else None

    def _symbolic_surjective(self, arrow: SetsCategory.MorphismType) -> bool | None:
        """A solved inverse makes the map epic; a codomain sample whose only preimage the domain rule rejects makes it not epic."""
        if self._solved_inverse(arrow) is not None:
            return True
        preimage = self._generic_preimage(arrow)
        if preimage is None:
            return None
        target, formula = preimage
        for sample in islice(_samples(arrow.codomain()), 16):
            candidate = formula.xreplace(dict(zip(_flatten(target), _flatten(sympify(sample)))))
            if sympy_ask(_datum_membership(arrow.domain(), candidate)) is False:
                return False
        return None

    @cache
    def _generic_preimage(self, arrow: SetsCategory.MorphismType) -> tuple[Basic, Basic] | None:
        """The codomain structure ``a`` and the one symbolic preimage of ``a`` under a symbolic map, when solving gives exactly one."""
        domain, codomain = arrow.domain(), arrow.codomain()
        if arrow._symbolic is None or isinstance(domain.set_presentation(), tuple) or isinstance(codomain.set_presentation(), tuple):
            return None
        source, target = _structure(domain), _structure(codomain)
        image, unknowns, targets = _flatten(arrow._symbolic(source)), _flatten(source), _flatten(target)
        if len(image) != len(targets):
            return None
        solutions = solve([Eq(left, right) for left, right in zip(image, targets)], list(unknowns), dict=True)
        if len(solutions) != 1 or set(solutions[0]) != set(unknowns):
            return None
        return target, source.xreplace(solutions[0])

    @cache
    def _solved_inverse(self, arrow: SetsCategory.MorphismType) -> Lambda | None:
        """The inverse rule of a symbolic map between rule-defined sets, when solving its equations gives one preimage that the domain rule admits.

        ``f(x) = a`` is solved for the domain symbols ``x`` in terms of codomain symbols
        ``a``.  One solution covering every domain symbol, whose membership in the domain
        follows from the codomain membership of ``a``, is a two-sided inverse.  Anything
        else, several solutions, none, or an undecided membership, leaves the question open.
        """
        preimage = self._generic_preimage(arrow)
        if preimage is None:
            return None
        target, formula = preimage
        admitted = sympy_ask(_datum_membership(arrow.domain(), formula), _datum_membership(arrow.codomain(), target))
        return Lambda((target,), formula) if admitted is True else None

    def inverse_morphism(self, morphism: SetsCategory.MorphismType) -> SetsCategory.MorphismType:
        """The inverse of a bijection: the table read backwards, or the solved inverse rule of a symbolic map."""
        if self.retained_inverse(morphism) is None:
            domain, codomain = morphism.domain(), morphism.codomain()
            inverse_form = None if morphism._form is None else morphism._form.inverse()
            if inverse_form is not None:
                self.retain_inverses(
                    morphism,
                    self.MorphismType(domain=codomain, codomain=domain, data=_SetMap(inverse_form.evaluate, None, inverse_form)),
                )
            elif isinstance(domain.set_presentation(), tuple) and isinstance(codomain.set_presentation(), tuple) and self._bijective(morphism, true) is True:
                from sage_categories.engines import finite_sets

                self.retain_inverses(morphism, finite_sets.inverse_morphism(morphism))
            elif (rule := self._solved_inverse(morphism)) is not None:
                self.retain_inverses(
                    morphism,
                    self.MorphismType(domain=codomain, codomain=domain, data=_SetMap(lambda datum: _plain(rule(datum)), rule)),
                )
        return super().inverse_morphism(morphism)

    @overload
    def __call__(self) -> SetsCategory: ...

    @overload
    def __call__(self, values: Iterable[Hashable]) -> SetsCategory.ObjectType: ...

    def __call__(self, values: Iterable[Hashable] | None = None) -> SetsCategory | SetsCategory.ObjectType:
        if values is None:
            return self
        return self.ObjectType(tuple(dict.fromkeys(values)))

    def from_membership(self, rule: MembershipRule) -> SetsCategory.ObjectType:
        """Represent a set by its membership proposition, without choosing an enumeration."""
        return self.ObjectType(rule)

    def has_chosen_enumeration(self, value: SetsCategory.ObjectType) -> bool:
        """Whether this set has a supplied enumeration or an ordered finite presentation."""
        return self.chosen_enumeration(value) is not Unknown

    def chosen_enumeration(self, value: SetsCategory.ObjectType) -> MorphismCategory.ObjectType | UnknownClass:
        """The retained isomorphism ``e: I -> X`` for the supplied enumeration of ``X``."""
        if value in _enumerations:
            return _enumerations[value]
        placement = value.category()
        for family in (placement, *placement.narrowing_roots()):
            for diagram in family.presenting_diagrams(value):
                shape = diagram.domain()
                if shape.is_discrete() and family is self.Limits(shape):
                    return self._product_enumeration(diagram)
        return self._finite_enumeration(value)

    def _finite_enumeration(self, value: SetsCategory.ObjectType) -> MorphismCategory.ObjectType | UnknownClass:
        """Index the defining finite list by ``{1, ..., n}``."""
        if value in _enumerations:
            return _enumerations[value]
        values = _finite_data(value)
        if values is Unknown:
            return Unknown
        indices = self(range(1, len(values) + 1))
        enumeration = Mor(self)(indices, value)(lambda index: values[int(index) - 1])
        positions = {datum: index for index, datum in enumerate(values, start=1)}
        inverse = Mor(self)(value, indices)(lambda datum: positions[value.representative(datum)])
        self.retain_inverses(enumeration, inverse)
        _enumerations[value] = enumeration
        return enumeration

    def _product_enumeration(self, diagram: Functor) -> MorphismCategory.ObjectType | UnknownClass:
        """``(prod_i e_i) * c``, with ``c`` the finite enumeration of ``prod_i I_i``."""
        from sage_categories.cat.finite_categories import finite_objects

        shape = diagram.domain()
        vertices = finite_objects(shape)
        if vertices is Unknown:
            return Unknown
        enumerations: dict[CategoryOfCategories.ElementType, MorphismCategory.ObjectType] = {}
        for vertex in vertices:
            enumeration = self.chosen_enumeration(diagram.on_object(vertex))
            if enumeration is Unknown:
                return Unknown
            enumerations[vertex] = enumeration
        indices = Fun(shape, self).from_object_rule(lambda vertex: enumerations[vertex].domain())
        family = self.Limits(shape)
        limit = family.limit_functor()
        index_product = limit.on_object(indices)
        index_enumeration = self._finite_enumeration(index_product)
        if index_enumeration is Unknown:
            return Unknown
        forward = Mor(Fun(shape, self))(indices, diagram)(lambda vertex: enumerations[vertex])
        backward = Mor(Fun(shape, self))(diagram, indices)(lambda vertex: enumerations[vertex].inverse())
        enumeration = limit.on_morphism(forward) * index_enumeration
        inverse = index_enumeration.inverse() * limit.on_morphism(backward)
        self.retain_inverses(enumeration, inverse)
        _enumerations[enumeration.codomain()] = enumeration
        return enumeration

    def finite_points(self, value: SetsCategory.ObjectType) -> tuple[SetsCategory.ElementType, ...] | UnknownClass:
        """The points listed by a chosen enumeration with a finite presented index set."""
        enumeration = self.chosen_enumeration(value)
        if enumeration is Unknown:
            return Unknown
        if _finite_data(enumeration.domain()) is Unknown:
            return Unknown
        return tuple(enumeration(index) for index in enumeration.domain())

    def enumeration_index_inclusion(self, enumeration: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        """The retained inclusion of the enumeration's positive index set into ``NN``."""
        if enumeration not in _enumeration_indices:
            assert enumeration in Mor(self).Isomorphisms()
            _enumeration_indices[enumeration] = Mor(self)(enumeration.domain(), NN).Monomorphisms()(lambda index: index)
        return _enumeration_indices[enumeration]

    def retain_enumeration(
        self, enumeration: MorphismCategory.ObjectType, inclusion: MorphismCategory.ObjectType
    ) -> None:
        """Retain a supplied enumeration and the inclusion of its index set into ``NN``."""
        assert enumeration in Mor(self).Isomorphisms()
        assert inclusion in Mor(self).Monomorphisms()
        assert inclusion.domain() is enumeration.domain() and inclusion.codomain() is NN
        value = enumeration.codomain()
        if value in _enumerations:
            assert _enumerations[value] is enumeration, "this set already has a different chosen enumeration"
        _enumerations[value] = enumeration
        _enumeration_indices[enumeration] = inclusion

    def constant(self, source: SetsCategory.ObjectType, point: SetsCategory.ElementType) -> SetsCategory.MorphismType:
        """The total constant map with the supplied value; at a presented target's zero it is the zero map."""
        source_form, target_form = _form_of(source), _form_of(point.parent())
        form = None
        if source_form is not None and target_form is not None and _equal_datum(point.datum(), target_form.zero_datum()):
            form = target_form.zero_map(source_form)
        return self.MorphismType(
            domain=source, codomain=point.parent(), data=_SetMap(lambda datum: point.datum(), _constant_rule(source, point.datum()), form)
        )

    def retain_form(self, value: SetsCategory.ObjectType, form: ObjectForm) -> None:
        """Retain the presentation a leaf supplies for one of this category's objects; its products and their legs then carry forms."""
        assert value not in _object_forms, f"{value!r} already carries a presentation"
        _object_forms[value] = form

    def form_of(self, value: SetsCategory.ObjectType) -> ObjectForm | None:
        return _form_of(value)

    def map_form(self, arrow: SetsCategory.MorphismType) -> MapForm | None:
        """The form a map carries, which composition, pairing, and projection propagate.

        A leaf that supplies forms reads its own back here rather than keeping a second
        record of them: the form of a composite is the composite of the forms, which this
        category already computed.
        """
        return arrow._form

    def Initial(self) -> SetsCategory.ObjectType:
        return self(())

    def subobjects_type(self) -> type[SetSubobjects]:
        return SetSubobjects

    def Terminal(self) -> SetsCategory.ObjectType:
        return self(((),))

    def point_morphism(self, point: SetsCategory.ElementType) -> SetsCategory.MorphismType:
        """The constant map ``1 -> X`` at a point of ``X``."""
        return self.constant(self.Terminal(), point)

    def element_from_defining_morphism(
        self, arrow: MorphismCategory.ObjectType
    ) -> SetsCategory.ElementType:
        assert arrow.domain() is self.Terminal()
        return arrow.codomain().point(arrow._action(()))

    def construct_morphism(
        self,
        source: CategoryOfCategories.ElementType,
        target: CategoryOfCategories.ElementType,
        action: MapData | _SetMap,
    ) -> MorphismCategory.ObjectType:
        """The map with this rule: tabulated over an enumerated domain, evaluated by its rule otherwise, with its symbolic or engine form retained."""
        form = action.form if isinstance(action, _SetMap) else action if isinstance(action, MapForm) else None
        rule = _symbolic_rule(action)
        evaluate = form.evaluate if form is not None and not isinstance(action, _SetMap) else _evaluation(action, rule)
        if not isinstance(source.set_presentation(), tuple):
            # A rule needs no enumeration (``specs/sets.md``, "Morphisms").
            return self.MorphismType(domain=source, codomain=target, data=_SetMap(lambda datum: target.representative(evaluate(datum)), rule, form))
        table = {value: target.representative(evaluate(value)) for value in source._values}
        if len(table) == 1:
            value = next(iter(table.values()))
            rule = rule if rule is not None else _constant_rule(source, value)
            source_form, target_form = _form_of(source), _form_of(target)
            if form is None and source_form is not None and target_form is not None and _equal_datum(value, target_form.zero_datum()):
                form = target_form.zero_map(source_form)
        return self.MorphismType(domain=source, codomain=target, data=_SetMap(table.__getitem__, rule, form))

    def construct_identity(
        self, value: CategoryOfCategories.ElementType
    ) -> MorphismCategory.ObjectType:
        structure, object_form = _structure(value), _form_of(value)
        form = None if object_form is None else object_form.identity()
        return self.MorphismType(domain=value, codomain=value, data=_SetMap(lambda datum: datum, Lambda((structure,), structure), form))

    def composite(
        self, second: MorphismCategory.ObjectType, first: MorphismCategory.ObjectType
    ) -> MorphismCategory.ObjectType:
        return self.MorphismType(
            domain=first.domain(),
            codomain=second.codomain(),
            data=_SetMap(lambda value: second._action(first._action(value)), _composed_rule(second, first), _composed_form(second, first)),
        )

    def limit_construction(
        self, shape: Category
    ) -> Callable[[Functor], CategoryOfCategories.ElementType]:
        if (
            shape.is_discrete()
            or shape is Cat().WalkingParallelPair()
            or shape.op() is Cat().WalkingParallelPair()
        ):
            return self._primitive_limit
        from sage_categories.cat.finite_categories import finite_category
        from sage_categories.engines import finite_sets

        if finite_category(shape) is not Unknown:
            return finite_sets.finite_limit
        return Category.limit_construction(self, shape)

    def colimit_construction(
        self, shape: Category
    ) -> Callable[[Functor], CategoryOfCategories.ElementType]:
        if (
            shape.is_discrete()
            or shape is Cat().WalkingParallelPair()
            or shape.op() is Cat().WalkingParallelPair()
        ):
            return self._primitive_colimit
        from sage_categories.cat.finite_categories import finite_category
        from sage_categories.engines import finite_sets

        if finite_category(shape) is not Unknown:
            return finite_sets.finite_colimit
        return Category.colimit_construction(self, shape)

    def _represented_product(
        self,
        diagram: Functor,
        vertices: tuple[CategoryOfCategories.ElementType, ...],
    ) -> CategoryOfCategories.ElementType:
        """Represent a product whose factors cannot all enter ``FinSetsForCAP``.

        The apex retains the full factor family as a membership rule.  Projections and
        mediators evaluate only the supplied tuple or source point; neither operation
        enumerates a factor.  Exact finite products take the separate CAP path in
        ``_primitive_limit``.
        """
        factors = tuple(diagram.on_object(vertex) for vertex in vertices)
        apex = self.from_membership(_ProductRule(factors))
        forms = tuple(_form_of(factor) for factor in factors)
        presented = bool(factors) and all(form is not None for form in forms)
        if presented and apex not in _object_forms:
            _object_forms[apex] = forms[0].direct_sum(forms)
        apex_form = _form_of(apex)
        position = {id(vertex): index for index, vertex in enumerate(vertices)}

        def leg(vertex: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
            index = position[id(vertex)]
            structure = _structure(apex)
            symbolic = Lambda((structure,), structure[index])
            form = None if apex_form is None else apex_form.projection(index)
            return Mor(self)(apex, diagram.on_object(vertex))(
                _SetMap(lambda value: value[index], symbolic, form)
            )

        def lift(candidate: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
            components = tuple(candidate.component(vertex) for vertex in vertices)
            source = cone_apex(candidate)
            structure = _structure(source)
            symbolic = None
            if all(component._symbolic is not None for component in components):
                symbolic = Lambda(
                    (structure,),
                    Tuple(*(component._symbolic(structure) for component in components)),
                )
            source_form = _form_of(source)
            component_forms = tuple(component._form for component in components)
            form = None
            if (
                apex_form is not None
                and source_form is not None
                and all(component_form is not None for component_form in component_forms)
            ):
                form = source_form.pair(component_forms, apex_form)
            return Mor(self)(source, apex)(
                _SetMap(
                    lambda value: tuple(component._action(value) for component in components),
                    symbolic,
                    form,
                )
            )

        return self.Limits(diagram.domain()).with_universal_data(
            diagram, apex, cone(diagram, apex, leg), lift
        )

    def _primitive_limit(self, diagram: Functor) -> CategoryOfCategories.ElementType:
        from sage_categories.cat.finite_categories import finite_category
        from sage_categories.engines import finite_sets

        shape = diagram.domain()
        vertices = tuple(finite_category(shape).objects)
        if shape.is_discrete():
            factors = tuple(diagram.on_object(vertex) for vertex in vertices)
            if all(_finite_data(factor) is not Unknown for factor in factors):
                return finite_sets.primitive_limit(diagram)
            return self._represented_product(diagram, vertices)
        return finite_sets.primitive_limit(diagram)

    def _primitive_colimit(self, diagram: Functor) -> CategoryOfCategories.ElementType:
        from sage_categories.engines import finite_sets

        return finite_sets.primitive_colimit(diagram)

    def image_factorization(
        self, arrow: MorphismCategory.ObjectType
    ) -> tuple[MorphismCategory.ObjectType, MorphismCategory.ObjectType]:
        """The surjection onto the image and its inclusion into the codomain."""
        from sage_categories.engines import finite_sets

        return finite_sets.image_factorization(arrow)

    def factor_through_monomorphism(
        self, mono: MorphismCategory.ObjectType, arrow: MorphismCategory.ObjectType
    ) -> MorphismCategory.ObjectType | Literal[False]:
        assert mono.codomain() is arrow.codomain()
        from sage_categories.engines import finite_sets

        return finite_sets.factor_through_monomorphism(mono, arrow)

    @cache
    def hom_morphisms(
        self,
        source: CategoryOfCategories.ElementType,
        target: CategoryOfCategories.ElementType,
    ) -> tuple[MorphismCategory.ObjectType, ...]:
        from sage_categories.engines import finite_sets

        return finite_sets.hom_morphisms(source, target)


def _finite_presentation(value: SetsCategory.ObjectType, assumptions: Proposition) -> bool | None:
    presentation = value.set_presentation()
    if isinstance(presentation, tuple):
        return True
    if isinstance(presentation, _PredicateRule) and sympy_ask(finite_set(presentation.ambient), assumptions) is True:
        return True
    if value in _enumerations:
        index_presentation = _enumerations[value].domain().set_presentation()
        while isinstance(index_presentation, _PredicateRule):
            index_presentation = index_presentation.ambient.set_presentation()
        if isinstance(index_presentation, tuple):
            return True
    return None


def _set_member(
    value: SetsCategory.ObjectType,
    point: SetsCategory.ElementType,
    assumptions: Proposition,
) -> bool | None:
    if point.parent() is value:
        return True
    presentation = value.set_presentation()
    if isinstance(presentation, _PredicateRule):
        ambient_membership = sympy_ask(_datum_membership(presentation.ambient, point.datum()), assumptions)
        if ambient_membership is not True:
            return ambient_membership
        ambient_point = presentation.ambient.point(point.datum())
        return sympy_ask(presentation.predicate(ambient_point), assumptions)
    return False


class SetSubobjects(SliceProperty):
    class ObjectType:
        """A set with its inclusion into the fixed set."""

    class ElementType:
        """A point inherited from the slice."""

    class MorphismType:
        """A commuting triangle of set inclusions."""

    def from_predicate(
        self, predicate: Callable[[SetsCategory.ElementType], Proposition]
    ) -> SliceLikeCategory.ObjectType:
        ambient = self.ambient().fixed_object()
        subset = Sets.from_membership(_PredicateRule(ambient, predicate))
        inclusion = Mor(Sets)(subset, ambient).Monomorphisms()(lambda datum: datum)
        return self(inclusion)


Cat().implement(SetsCategory)
register_handler(finite_set, _finite_presentation)
register_handler(set_membership, _set_member)
FiniteSets = Sets.Finite()
register_handler(Sets.equality(), Sets._equal_objects)
register_handler(Sets.equality(), Sets._equal_morphisms)
register_handler(Sets.equality(), Sets._equal_points)
register_handler(Mor(Sets).Monomorphisms().predicate(), Sets._injective)
register_handler(Mor(Sets).Epimorphisms().predicate(), Sets._surjective)
register_handler(Mor(Sets).Isomorphisms().predicate(), Sets._bijective)


def _finite_cartesian_comparison(operation: str, *arguments: object) -> MorphismCategory.ObjectType:
    from sage_categories.engines import finite_sets

    match operation, arguments:
        case "associator_forward", (first, second, third, left, right):
            return finite_sets.cartesian_associator(first, second, third, left, right, forward=True)
        case "associator_inverse", (first, second, third, left, right):
            return finite_sets.cartesian_associator(first, second, third, right, left, forward=False)
        case "left_unitor_forward", (value, product):
            return finite_sets.cartesian_left_unitor(value, product, value, forward=True)
        case "left_unitor_inverse", (value, product):
            return finite_sets.cartesian_left_unitor(value, value, product, forward=False)
        case "right_unitor_forward", (value, product):
            return finite_sets.cartesian_right_unitor(value, product, value, forward=True)
        case "right_unitor_inverse", (value, product):
            return finite_sets.cartesian_right_unitor(value, value, product, forward=False)
    raise ValueError(f"unknown finite Cartesian comparison {operation!r}")


def _register_finite_cartesian_comparisons() -> None:
    from sage_categories.cat.monoidal import register_cartesian_comparisons

    register_cartesian_comparisons(SetsCategory, _finite_cartesian_comparison)


_register_finite_cartesian_comparisons()
