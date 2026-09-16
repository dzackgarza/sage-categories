"""Private Sage/CAP execution boundary for abelian-group leaves."""

from __future__ import annotations

from collections.abc import Callable, Hashable, Iterable, Mapping
from dataclasses import dataclass
from operator import add, neg
from types import ModuleType

from sage.categories.sets_cat import Sets as SageSets
from sage.combinat.free_module import CombinatorialFreeModule
from sage.groups.additive_abelian.additive_abelian_group import AdditiveAbelianGroup_class
from sage.groups.generic import multiple
from sage.modules.fg_pid.fgp_element import FGP_Element
from sage.modules.fg_pid.fgp_module import FGP_Module_class
from sage.modules.free_module_element import vector
from sage.rings.integer_ring import ZZ
from sage.structure.element import Element as SageElement
from sage.structure.parent import Parent

from sage_categories.cat.category import CategoryOfCategories

type Engine = AdditiveAbelianGroup_class | FGP_Module_class


def presented_modules() -> ModuleType:
    from sage_categories.engines import presented_modules as engine

    return engine


def has_native_parent(value: object, parent: object) -> bool:
    return isinstance(value, SageElement) and value.parent() is parent


def engine_orders(engine: Engine) -> tuple[int, ...]:
    return tuple(int(order) for order in engine.invariants())


def engine_coordinates(value: object) -> tuple[int, ...]:
    assert isinstance(value, FGP_Element)
    return tuple(int(coefficient) for coefficient in value.vector())


def engine_element(engine: Engine, coordinates: tuple[int, ...]) -> Hashable:
    return engine.linear_combination_of_smith_form_gens(vector(ZZ, coordinates))


def engine_zero(engine: Engine) -> Hashable:
    return engine.zero()


def engine_member(engine: Engine, value: object) -> bool:
    return isinstance(value, FGP_Element) and value.parent() is engine


def finite_free_engine(rank: int) -> Engine:
    from sage.groups.additive_abelian.additive_abelian_group import AdditiveAbelianGroup

    return AdditiveAbelianGroup([0] * rank)


_relation_matrices: dict[tuple[tuple[int, ...], ...], object] = {}


def relation_matrix(rows: tuple[tuple[int, ...], ...]):
    from sage.matrix.constructor import matrix

    if rows not in _relation_matrices:
        columns = len(rows[0]) if rows else 0
        _relation_matrices[rows] = matrix(ZZ, rows) if rows else matrix(ZZ, 0, columns)
    return _relation_matrices[rows]


def relation_image(rows: tuple[tuple[int, ...], ...], coordinates: tuple[int, ...]) -> tuple[int, ...]:
    result = vector(ZZ, coordinates) * relation_matrix(rows)
    return tuple(int(entry) for entry in result)


class _OwnedIndexFacade(Parent):
    def __init__(self, index_set: CategoryOfCategories.ElementType) -> None:
        self._owned_index_set = index_set
        Parent.__init__(self, facade=True, category=SageSets())

    def __contains__(self, datum: object) -> bool:
        return datum in self._owned_index_set

    def _element_constructor_(self, datum: Hashable) -> Hashable:
        return self._owned_index_set.representative(datum)

    def _repr_(self) -> str:
        return f"native basis keys for {self._owned_index_set!r}"


@dataclass(frozen=True, eq=False, slots=True)
class _IndexedRecord:
    index_set: CategoryOfCategories.ElementType
    engine: CombinatorialFreeModule


_indexed: dict[CategoryOfCategories.ElementType, _IndexedRecord] = {}
_tensor_quotients: dict[CategoryOfCategories.ElementType, FGP_Module_class] = {}


def new_indexed_engine(index_set: CategoryOfCategories.ElementType) -> object:
    return CombinatorialFreeModule(ZZ, _OwnedIndexFacade(index_set))


def indexed_member(engine: object, value: object) -> bool:
    return has_native_parent(value, engine)


def indexed_zero(engine: object) -> Hashable:
    assert isinstance(engine, CombinatorialFreeModule)
    return engine.zero()


def retain_indexed(group: CategoryOfCategories.ElementType, index_set: CategoryOfCategories.ElementType, engine: object) -> None:
    assert isinstance(engine, CombinatorialFreeModule)
    _indexed[group] = _IndexedRecord(index_set, engine)


def is_indexed(group: CategoryOfCategories.ElementType) -> bool:
    return group in _indexed


def indexed_index_set(group: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
    return _indexed[group].index_set


def indexed_monomial(group: CategoryOfCategories.ElementType, index: Hashable) -> Hashable:
    return _indexed[group].engine.monomial(index)


def indexed_coefficients(group: CategoryOfCategories.ElementType, value: object) -> Mapping[Hashable, object]:
    record = _indexed[group]
    assert has_native_parent(value, record.engine)
    return value.monomial_coefficients(copy=False)


def indexed_sum_terms(
    group: CategoryOfCategories.ElementType,
    terms: Iterable[tuple[Hashable, int]],
    *,
    distinct: bool,
) -> Hashable:
    return _indexed[group].engine.sum_of_terms(tuple(terms), distinct=distinct)


def integer_multiple(group: CategoryOfCategories.ElementType, coefficient: int, point: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
    return multiple(point, int(coefficient), operation="other", identity=group.zero(), inverse=neg, op=add)


def equal_morphisms(first, second) -> bool:
    return presented_modules().equal_morphisms(first, second)


def homomorphism_from_rule(source, target, rule):
    return presented_modules().homomorphism_from_rule(source, target, rule)


def zero_morphism(source, target):
    return presented_modules().zero_morphism(source, target)


def retain_binary_biproduct(first, second, apex):
    return presented_modules().retain_binary_biproduct(first, second, apex)


def direct_sum_product_lift(factors, apex, source, components):
    return presented_modules().direct_sum_product_lift(factors, apex, source, components)


def direct_sum_coproduct_lift(factors, apex, target, components):
    return presented_modules().direct_sum_coproduct_lift(factors, apex, target, components)


def coequalizer_projection(first, second):
    return presented_modules().coequalizer_projection(first, second)


def coequalizer_mediator(projection, coequalizing, first, second):
    return presented_modules().coequalizer_mediator(projection, coequalizing, first, second)


def tensor_object(first, second):
    result, quotient = presented_modules().tensor_object(first, second)
    _tensor_quotients[result] = quotient
    return result


def tensor_zero(result: CategoryOfCategories.ElementType) -> Hashable:
    return _tensor_quotients[result].zero()


def tensor_element(first, second, result, a, b):
    return presented_modules().tensor_element(first, second, result, a, b)


def tensor_mediator(first, second, result, target, biadditive):
    return presented_modules().tensor_mediator(first, second, result, target, biadditive)


def tensor_morphism(first, second, source, target):
    return presented_modules().tensor_morphism(first, second, source, target)


def tensor_associator(a, b, c, source, target, *, left_to_right: bool):
    return presented_modules().tensor_associator(a, b, c, source, target, left_to_right=left_to_right)


def tensor_left_unitor(group, tensor_group, *, inverse: bool):
    return presented_modules().tensor_left_unitor(group, tensor_group, inverse=inverse)


def tensor_right_unitor(group, tensor_group, *, inverse: bool):
    return presented_modules().tensor_right_unitor(group, tensor_group, inverse=inverse)


def colift_along_epimorphism(epimorphism, arrow):
    return presented_modules().colift_along_epimorphism(epimorphism, arrow)
