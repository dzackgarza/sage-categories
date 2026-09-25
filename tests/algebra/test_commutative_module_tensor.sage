"""Commutative-base algebras use the selected tensor on ordinary left modules."""

from sage.groups.additive_abelian.additive_abelian_group import AdditiveAbelianGroup
from sage.modules.free_module_element import vector
from sage.rings.integer_ring import ZZ

from sage_categories.algebra.abelian import (
    AbelianModuleTensor,
    AbelianTensor,
    abelian_homomorphism,
    integer_group,
    presented_abelian_group,
    tensor_mediator,
)
from sage_categories.algebra.algebras import Algebras
from sage_categories.cat.category import ask
from sage_categories.cat.modules import Modules
from sage_categories.cat.monoidal import SelfAction, tensor_morphism, tensor_object
from sage_categories.cat.morphisms import Mor
from sage_categories.cat.structured_objects import Monoids


def cyclic_ring(order):
    """Z/order as a commutative monoid object of (Ab, tensor)."""
    engine = AdditiveAbelianGroup([order])
    group = presented_abelian_group(engine)
    element = lambda value: engine.linear_combination_of_smith_form_gens(
        vector(ZZ, [value])
    )
    multiplication = tensor_mediator(
        group,
        group,
        group,
        lambda left, right: int(left.vector()[0]) * right,
    )
    unit = abelian_homomorphism(
        integer_group(),
        group,
        lambda value: value * element(1),
    )
    return group, Monoids(AbelianTensor())(multiplication, unit)


def test_commutative_base_uses_the_selected_left_module_tensor() -> None:
    group, field = cyclic_ring(5)
    ambient = AbelianTensor()
    actegory = SelfAction(ambient)
    structure = AbelianModuleTensor(field)
    modules = Modules(field, actegory)

    assert structure.underlying_category() is modules
    assert modules.monoidal_structure() is structure

    unit = structure.unit()
    assert unit in modules
    assert modules.forgetful().on_object(unit) is group

    tensor_square = tensor_object(structure.tensor(), unit, unit)
    multiplication = structure.left_unitor().component(unit)
    identity = Mor(modules)(unit, unit).one()
    assert multiplication in Mor(modules)(tensor_square, unit)
    assert ask(multiplication * structure.left_unitor().inverse().component(unit) == identity) is True

    neutral = Monoids(structure)(multiplication, identity)
    algebras = Algebras(field, actegory)
    algebra = algebras.from_monoid(neutral)

    assert algebras.monoidal_structure() is structure
    assert algebras.monoid_category() is Monoids(structure)
    assert algebras.module_category() is modules
    assert algebras.to_modules().on_object(algebra) is unit
    assert algebras.monoid_presentation().on_object(algebra) is neutral
    assert neutral.operation() is multiplication
    assert neutral.unit_morphism() is identity

    plane_engine = AdditiveAbelianGroup([5, 5])
    plane = presented_abelian_group(plane_engine)
    action = tensor_mediator(
        group,
        plane,
        plane,
        lambda scalar, value: int(scalar.vector()[0]) * value,
    )
    module = modules(action)
    module_square = tensor_object(structure.tensor(), module, module)
    assert module_square in modules
    assert modules.forgetful().on_object(module_square) is not plane

    doubling = modules.homomorphism(
        module,
        module,
        abelian_homomorphism(plane, plane, lambda value: 2 * value),
    )
    doubled_tensor = tensor_morphism(structure.tensor(), doubling, doubling)
    assert doubled_tensor in Mor(modules)(module_square, module_square)
    assert ask(doubled_tensor == Mor(modules)(module_square, module_square).one()) is False

    left_unitor = structure.left_unitor().component(module)
    left_unitor_inverse = structure.left_unitor().inverse().component(module)
    assert left_unitor.inverse() is left_unitor_inverse
    assert ask(left_unitor * left_unitor_inverse == Mor(modules)(module, module).one()) is True

    triples = structure.associator().domain().domain()
    triple = triples((module, module, module))
    associator = structure.associator().component(triple)
    associator_inverse = structure.associator().inverse().component(triple)
    assert associator.inverse() is associator_inverse
    assert ask(
        associator_inverse * associator
        == Mor(modules)(associator.domain(), associator.domain()).one()
    ) is True
    assert ask(
        associator * associator_inverse
        == Mor(modules)(associator.codomain(), associator.codomain()).one()
    ) is True

    triple_doubling = Mor(triples)(triple, triple)((doubling, doubling, doubling))
    left_image = structure.associator().domain().on_morphism(triple_doubling)
    right_image = structure.associator().codomain().on_morphism(triple_doubling)
    assert ask(right_image * associator == associator * left_image) is True


def test_nonfield_commutative_base_retains_torsion_module_tensor() -> None:
    ring_group, ring = cyclic_ring(4)
    two_engine = AdditiveAbelianGroup([2])
    two = presented_abelian_group(two_engine)
    modules = Modules(ring, SelfAction(AbelianTensor()))
    structure = AbelianModuleTensor(ring)
    action = tensor_mediator(
        ring_group,
        two,
        two,
        lambda scalar, value: int(scalar.vector()[0]) * value,
    )
    module = modules(action)
    square = tensor_object(structure.tensor(), module, module)
    carrier = modules.forgetful().on_object(square)

    assert square in modules
    assert modules.monoidal_structure() is structure

    zero = modules.homomorphism(
        module,
        module,
        abelian_homomorphism(two, two, lambda value: 0 * value),
    )
    identity = Mor(modules)(module, module).one()
    induced_zero = tensor_morphism(structure.tensor(), zero, identity)
    zero_square = modules.homomorphism(
        square,
        square,
        abelian_homomorphism(carrier, carrier, lambda value: 0 * value),
    )
    square_identity = Mor(modules)(square, square).one()

    assert ask(induced_zero == zero_square) is True
    assert ask(zero_square == square_identity) is False

    left_unitor = structure.left_unitor().component(module)
    left_unitor_inverse = structure.left_unitor().inverse().component(module)
    assert ask(left_unitor * left_unitor_inverse == Mor(modules)(module, module).one()) is True


test_commutative_base_uses_the_selected_left_module_tensor()
test_nonfield_commutative_base_retains_torsion_module_tensor()
