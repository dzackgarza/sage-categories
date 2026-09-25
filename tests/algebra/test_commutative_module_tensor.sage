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
from sage_categories.cat.monoidal import SelfAction, tensor_object
from sage_categories.cat.morphisms import Mor
from sage_categories.cat.structured_objects import Monoids


def prime_field_five():
    """F_5 as a commutative monoid object of (Ab, tensor)."""
    engine = AdditiveAbelianGroup([5])
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
    group, field = prime_field_five()
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


test_commutative_base_uses_the_selected_left_module_tensor()
