"""Finitely generated abelian groups over Sage's presented-module engine, and their tensor product.

``AbelianGroups()`` is ``AdditiveGroups(Cartesian(Sets())).Commutative()``, the commutative
additive group objects of sets (``specs/magmas-monoids-semirings.md``, "Groups").  This leaf
adds two things.  ``presented_abelian_group(engine)`` constructs the object of that category
carried by the elements of a finite Sage ``AdditiveAbelianGroup`` or ``ZZ^n / W`` module, with
the engine's addition; ``integer_group()`` is the integers on their rule-defined carrier.  The
tensor product is the selected monoidal structure ``AbelianTensor()`` on ``AbelianGroups()``
with unit the integers (``specs/modules.md``, "Instances").

The private engine is Smith coordinates.  A presented group ``A = Z^n / R_A`` in Smith
generators of orders ``(d_1, ..., d_n)`` has ``A ⊗ B = Z^{nm} / (R_A ⊗ 1 + 1 ⊗ R_B)``, the
quotient of the free module on the pairs of generators by ``d_i e_{ij}`` and ``d'_j e_{ij}``
(Stacks, tag 00CV, tensor products of modules; the presentation is the standard one from
right exactness of ``⊗``).  The biadditive map sends ``(a, b)`` to ``Σ a_i b_j e_{ij}``, and
a biadditive ``f: A × B -> C`` factors through the mediator that sends the class of ``e_{ij}``
to ``f(e_i, e_j)`` and extends additively along a lift of each element.
"""

from __future__ import annotations

__all__ = ["AbelianGroups", "AbelianTensor", "abelian_homomorphism", "bilinear_map", "integer_group", "presented_abelian_group", "tensor_mediator"]

from collections.abc import Callable, Hashable
from dataclasses import dataclass

from sage.groups.additive_abelian.additive_abelian_group import AdditiveAbelianGroup_class
from sage.modules.fg_pid.fgp_module import FGP_Module_class
from sage.modules.free_module import FreeModule
from sage.modules.free_module_element import vector
from sage.rings.integer_ring import ZZ
from sage.structure.coerce_dict import MonoDict
from sympy import Lambda, Q, symbols

from sage_categories.cat.calculus import binary_product_data, natural_isomorphism
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.declarations import Sets
from sage_categories.cat.functors import Cat, Fun
from sage_categories.cat.monoidal import Cartesian, MonoidalStructures, MonoidalStructuresCategory, tensor_parentheses, tensor_units
from sage_categories.cat.morphisms import Mor, MorphismCategory
from sage_categories.cat.structured_objects import AdditiveGroups, Groups, Monoids
from sage_categories.kernel.retention import identity_key
from sage_categories.kernel.sage_runtime import cached_function

type Engine = AdditiveAbelianGroup_class | FGP_Module_class


@dataclass(frozen=True, eq=False, slots=True)
class _Presentation:
    """Smith coordinates of a presented abelian group: generator orders, and the two coordinate maps on data."""

    orders: tuple[int, ...]
    coordinates: Callable[[Hashable], tuple[int, ...]]
    element: Callable[[tuple[int, ...]], Hashable]


@dataclass(frozen=True, eq=False, slots=True)
class _TensorData:
    """The factors of a tensor product object and the free module on pairs of their generators."""

    first: CategoryOfCategories.ElementType
    second: CategoryOfCategories.ElementType
    quotient: FGP_Module_class


_presentations: MonoDict = MonoDict()
_tensor_data: MonoDict = MonoDict()


def _structure() -> MonoidalStructuresCategory.ObjectType:
    return Cartesian(Sets())


@cached_function(key=lambda: 0)
def AbelianGroups() -> Category:
    """``Ab``: commutative additive group objects of sets, ``AdditiveGroups(Cartesian(Sets())).Commutative()``."""
    return AdditiveGroups(_structure()).Commutative()


def _points(group: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
    """The set of points of a group object: its image under the carrier functors of the named copies."""
    groups = AdditiveGroups(_structure())
    monoids, magmas = groups.named_monoids(), groups.named_monoids().named_magmas()
    return magmas.to_carrier().on_object(monoids.to_named_magmas().on_object(groups.to_named_monoids().on_object(group)))


def presentation(group: CategoryOfCategories.ElementType) -> _Presentation:
    """The Smith presentation this leaf retained for a group object; a group built elsewhere has none."""
    assert group in _presentations, f"{group!r} was not constructed from a presented engine, so it has no Smith coordinates"
    return _presentations[group]


def _group_from_operations(
    carrier: CategoryOfCategories.ElementType,
    addition: MorphismCategory.ObjectType,
    zero: MorphismCategory.ObjectType,
) -> CategoryOfCategories.ElementType:
    """The object of ``Ab`` with these operations: the monoid is decided a group and commutative on the way."""
    structure = _structure()
    monoid = Monoids(structure)(addition, zero)
    assert monoid in Groups(structure), f"{addition!r} is not a group operation"
    group = AdditiveGroups(structure).renamed(monoid)
    assert group in AbelianGroups(), f"{addition!r} is not commutative"
    return group


@cached_function(key=identity_key)
def presented_abelian_group(engine: Engine) -> CategoryOfCategories.ElementType:
    """The object of ``Ab`` whose points are the elements of a finite presented Sage abelian group, with its addition."""
    assert engine.is_finite(), f"{engine!r} is infinite; only the integers are represented without an enumeration"
    carrier = Sets(tuple(engine))
    square = binary_product_data(Sets(), carrier, carrier).apex()
    addition = Mor(Sets)(square, carrier)(lambda pair: pair[0] + pair[1])
    zero = Mor(Sets)(_structure().unit(), carrier)(lambda _: engine.zero())
    group = _group_from_operations(carrier, addition, zero)
    _presentations[group] = _Presentation(
        tuple(int(order) for order in engine.invariants()),
        lambda datum: tuple(int(c) for c in datum.vector()),
        lambda coordinates: engine.linear_combination_of_smith_form_gens(vector(ZZ, coordinates)),
    )
    return group


@cached_function(key=lambda: 0)
def integer_group() -> CategoryOfCategories.ElementType:
    """``Z`` as an object of ``Ab``: the rule-defined integers with symbolic addition, the free group on one generator."""
    integers = Sets.from_membership(lambda n: Q.integer(n))
    square = binary_product_data(Sets(), integers, integers).apex()
    a, b = symbols("a b")
    addition = Mor(Sets)(square, integers)(Lambda((a, b), a + b))
    zero = Mor(Sets)(_structure().unit(), integers)(lambda _: 0)
    group = _group_from_operations(integers, addition, zero)
    _presentations[group] = _Presentation((0,), lambda datum: (int(datum),), lambda coordinates: int(coordinates[0]))
    return group


def abelian_homomorphism(
    source: CategoryOfCategories.ElementType,
    target: CategoryOfCategories.ElementType,
    rule: Callable[[Hashable], Hashable],
) -> MorphismCategory.ObjectType:
    """The morphism of ``Ab`` over a rule on data; additivity and the unit are checked by the monoid constructor."""
    structure = _structure()
    renaming = AdditiveGroups(structure).product_projection(0)
    carrier_map = Mor(Sets)(_points(source), _points(target))(rule)
    monoid_map = Monoids(structure).homomorphism(renaming.on_object(source), renaming.on_object(target), carrier_map)
    return AdditiveGroups(structure).homomorphism(source, target, monoid_map)


def _pair_generators(first: _Presentation, second: _Presentation) -> FGP_Module_class:
    """``Z^{nm} / (d_i e_{ij}, d'_j e_{ij})``: the presented tensor product in the pair generators."""
    n, m = len(first.orders), len(second.orders)
    free = FreeModule(ZZ, n * m)
    relations = [free.gen(i * m + j) * order for i, order in enumerate(first.orders) for j in range(m)]
    relations += [free.gen(i * m + j) * order for j, order in enumerate(second.orders) for i in range(n)]
    return free / free.span(relations)


def _pair_vector(data: _TensorData, a: Hashable, b: Hashable) -> Hashable:
    """``Σ a_i b_j e_{ij}`` as an element of the tensor engine: the image of ``(a, b)`` under the biadditive map."""
    first, second = presentation(data.first), presentation(data.second)
    left, right = first.coordinates(a), second.coordinates(b)
    m = len(right)
    return data.quotient(vector(ZZ, [left[i] * right[j] for i in range(len(left)) for j in range(m)]))


@cached_function(key=identity_key)
def _tensor_object(first: CategoryOfCategories.ElementType, second: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
    quotient = _pair_generators(presentation(first), presentation(second))
    assert quotient.is_finite(), f"the tensor of {first!r} and {second!r} is infinite; only finite tensor products are enumerated"
    result = presented_abelian_group(quotient)
    _tensor_data[result] = _TensorData(first, second, quotient)
    return result


def bilinear_map(first: CategoryOfCategories.ElementType, second: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
    """The universal biadditive map ``A × B -> A ⊗ B`` as a set map on the product of the carriers."""
    result = _tensor_object(first, second)
    data = _tensor_data[result]
    product = binary_product_data(Sets(), _points(first), _points(second)).apex()
    return Mor(Sets)(product, _points(result))(lambda pair: _pair_vector(data, pair[0], pair[1]))


def tensor_mediator(
    first: CategoryOfCategories.ElementType,
    second: CategoryOfCategories.ElementType,
    target: CategoryOfCategories.ElementType,
    biadditive: Callable[[Hashable, Hashable], Hashable],
) -> MorphismCategory.ObjectType:
    """The morphism ``A ⊗ B -> C`` of ``Ab`` through which a biadditive rule ``(a, b) ↦ f(a, b)`` on data factors.

    The class of ``e_{ij}`` goes to ``f(e_i, e_j)``; an element is sent along any lift to the
    free module on the pairs, which is well defined because ``f`` respects the relations.
    """
    result = _tensor_object(first, second)
    data = _tensor_data[result]
    left, right, into = presentation(first), presentation(second), presentation(target)
    n, m = len(left.orders), len(right.orders)
    generators = [
        [biadditive(left.element(tuple(int(i == k) for k in range(n))), right.element(tuple(int(j == k) for k in range(m)))) for j in range(m)]
        for i in range(n)
    ]
    zero = into.element(tuple(0 for _ in into.orders))

    def rule(datum: Hashable) -> Hashable:
        total = zero
        for position, coefficient in enumerate(datum.lift()):
            if coefficient:
                total = total + int(coefficient) * generators[position // m][position % m]
        return total

    return abelian_homomorphism(result, target, rule)


def _tensor_morphism(first: MorphismCategory.ObjectType, second: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
    """``f ⊗ g``: the mediator of ``(a, b) ↦ f(a) ⊗ g(b)``."""
    target = _tensor_object(first.codomain(), second.codomain())
    target_data = _tensor_data[target]
    return tensor_mediator(
        first.domain(),
        second.domain(),
        target,
        lambda a, b: _pair_vector(target_data, first(first.domain().point(a)).datum(), second(second.domain().point(b)).datum()),
    )


def _rebracket(triple: CategoryOfCategories.ElementType, forward: bool) -> MorphismCategory.ObjectType:
    """``(A ⊗ B) ⊗ C -> A ⊗ (B ⊗ C)`` and back, each the mediator of a biadditive rule written through lifts."""
    a, b, c = (triple.family_component(index) for index in range(3))
    ab, bc = _tensor_object(a, b), _tensor_object(b, c)
    ab_data, bc_data = _tensor_data[ab], _tensor_data[bc]
    if forward:
        target = _tensor_object(a, bc)
        target_data, m = _tensor_data[target], len(presentation(b).orders)

        def rule(t: Hashable, x: Hashable) -> Hashable:
            total = target_data.quotient.zero()
            for position, coefficient in enumerate(t.lift()):
                if coefficient:
                    e_i = presentation(a).element(tuple(int(position // m == k) for k in range(len(presentation(a).orders))))
                    e_j = presentation(b).element(tuple(int(position % m == k) for k in range(m)))
                    total = total + int(coefficient) * _pair_vector(target_data, e_i, _pair_vector(bc_data, e_j, x))
            return total

        return tensor_mediator(ab, c, target, rule)
    target = _tensor_object(ab, c)
    target_data, p = _tensor_data[target], len(presentation(c).orders)

    def rule_back(x: Hashable, t: Hashable) -> Hashable:
        total = target_data.quotient.zero()
        for position, coefficient in enumerate(t.lift()):
            if coefficient:
                e_j = presentation(b).element(tuple(int(position // p == k) for k in range(len(presentation(b).orders))))
                e_k = presentation(c).element(tuple(int(position % p == k) for k in range(p)))
                total = total + int(coefficient) * _pair_vector(target_data, _pair_vector(ab_data, x, e_j), e_k)
        return total

    return tensor_mediator(a, bc, target, rule_back)


@cached_function(key=lambda: 0)
def AbelianTensor() -> MonoidalStructuresCategory.ObjectType:
    """``(Ab, ⊗, Z)``: the tensor product of abelian groups as a selected monoidal structure on ``AbelianGroups()``."""
    base, unit = AbelianGroups(), integer_group()
    pairs = Cat().Products()((base, base))
    tensor = Fun(pairs, base)(
        lambda pair: _tensor_object(pair.family_component(0), pair.family_component(1)),
        lambda arrow: _tensor_morphism(arrow.family_component(0), arrow.family_component(1)),
    )
    left, right = tensor_parentheses(tensor)
    associator = natural_isomorphism(left, right, lambda triple: _rebracket(triple, True), lambda triple: _rebracket(triple, False))
    left_unit, right_unit = tensor_units(tensor, unit)
    identity = Fun(base, base).one()

    def scalar(group: CategoryOfCategories.ElementType, k: Hashable, a: Hashable) -> Hashable:
        into = presentation(group)
        return into.element(tuple(int(k) * coordinate for coordinate in into.coordinates(a)))

    left_unitor = natural_isomorphism(
        left_unit,
        identity,
        lambda group: tensor_mediator(unit, group, group, lambda k, a: scalar(group, k, a)),
        lambda group: abelian_homomorphism(group, _tensor_object(unit, group), lambda a: _pair_vector(_tensor_data[_tensor_object(unit, group)], 1, a)),
    )
    right_unitor = natural_isomorphism(
        right_unit,
        identity,
        lambda group: tensor_mediator(group, unit, group, lambda a, k: scalar(group, k, a)),
        lambda group: abelian_homomorphism(group, _tensor_object(group, unit), lambda a: _pair_vector(_tensor_data[_tensor_object(group, unit)], a, 1)),
    )
    return MonoidalStructures(base)(tensor, unit, associator, left_unitor, right_unitor)
