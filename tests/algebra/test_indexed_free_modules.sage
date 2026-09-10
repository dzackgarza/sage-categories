"""Arbitrary-index free integer modules retain the full index and coproduct universal map."""

from sympy import Q

from sage_categories.algebra import (
    AbelianTensor,
    abelian_homomorphism,
    indexed_free_integer_element,
    indexed_free_integer_module,
    indexed_free_integer_support,
    integer_group,
    integer_regular_module,
    integer_scalar_monoid,
)
from sage_categories.cat.category import Unknown
from sage_categories.cat.cones import cocone, cocones
from sage_categories.cat.functors import Fun
from sage_categories.cat.modules import Modules
from sage_categories.cat.monoidal import SelfAction
from sage_categories.cat.shapes import Discrete
from sage_categories.sets.finite import Sets


def test_infinite_free_integer_module_retains_all_indices_and_finite_support() -> None:
    indices = Sets.from_membership(lambda value: Q.integer(value))
    assert Sets.chosen_enumeration(indices) is Unknown

    module = indexed_free_integer_module(indices)
    element = indexed_free_integer_element(module, {2: 3, 1000: -4})
    support = indexed_free_integer_support(module, element)

    assert {point.datum() for point in support} == {2, 1000}
    assert element.parent() is module


def test_infinite_free_integer_module_has_rule_supplied_coproduct_mediator() -> None:
    indices = Sets.from_membership(lambda value: Q.integer(value))
    monoidal = AbelianTensor()
    modules = Modules(integer_scalar_monoid(), SelfAction(monoidal))
    regular = integer_regular_module()
    module = indexed_free_integer_module(indices)
    shape = Discrete(indices)
    diagram = Fun(shape, modules).constant(regular)
    presentation = modules.Colimits(shape).universal_data(diagram)

    def component(vertex):
        index = int(vertex.point().datum())
        additive = abelian_homomorphism(integer_group(), integer_group(), lambda value, index=index: index * value)
        return modules.homomorphism(regular, regular, additive)

    candidate = cocones(diagram)(cocone(diagram, regular, component))
    mediator = presentation.lift(candidate)
    element = indexed_free_integer_element(module, {2: 3, 1000: -4})

    assert presentation.apex() is module
    assert mediator.domain() is module and mediator.codomain() is regular
    assert mediator(element).datum() == -3994
    assert mediator(presentation.leg(1000)(regular.point(3))).datum() == 3000


test_infinite_free_integer_module_retains_all_indices_and_finite_support()
test_infinite_free_integer_module_has_rule_supplied_coproduct_mediator()
