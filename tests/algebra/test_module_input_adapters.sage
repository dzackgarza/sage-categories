"""Module input adapters use their supplied endomorphism map and native Sage module."""

from sage.modules.free_module import FreeModule
from sage.rings.integer_ring import ZZ

from sage_categories.algebra import (
    AbelianGroups,
    AbelianTensor,
    integer_group,
    integer_scalar_monoid,
    simple_tensor,
)
from sage_categories.algebra.modules import sage_module_from_engine
from sage_categories.cat.calculus import binary_product_data
from sage_categories.cat.category import ask
from sage_categories.cat.modules import Modules, internal_endomorphism_module
from sage_categories.cat.monoidal import Cartesian, SelfAction
from sage_categories.cat.morphisms import Mor
from sage_categories.cat.structured_objects import Monoids
from sage_categories.sets.finite import Sets


def finite_monoid(carrier, operation_rule, unit_value):
    """A finite monoid object of ``Sets`` from an exact operation table rule."""
    structure = Cartesian(Sets())
    square = binary_product_data(Sets(), carrier, carrier).apex()
    operation = Mor(Sets)(square, carrier)(operation_rule)
    unit = Mor(Sets)(structure.unit(), carrier)(lambda _point: unit_value)
    return Monoids(structure)(operation, unit)


def test_endomorphism_action_is_restriction_along_the_supplied_map() -> None:
    structure = Cartesian(Sets())
    actegory = SelfAction(structure)
    x = Sets((0, 1))

    # End(X) for X={0,1}: a function is the pair (f(0), f(1)), with composition.
    end_carrier = Sets(((0, 0), (0, 1), (1, 0), (1, 1)))
    endomorphisms = finite_monoid(
        end_carrier,
        lambda pair: (
            pair[0][pair[1][0]],
            pair[0][pair[1][1]],
        ),
        (0, 1),
    )
    acted = binary_product_data(Sets(), end_carrier, x).apex()
    evaluation = Mor(Sets)(acted, x)(lambda pair: pair[0][pair[1]])
    tautological = internal_endomorphism_module(endomorphisms, actegory, evaluation)

    # C2 -> End(X), with the nontrivial element acting by the transposition 0 <-> 1.
    c2_carrier = Sets((0, 1))
    c2 = finite_monoid(c2_carrier, lambda pair: (pair[0] + pair[1]) % 2, 0)

    def representation_rule(value):
        match bool(value):
            case False:
                return (0, 1)
            case True:
                return (1, 0)

    representation = Monoids(structure).homomorphism(
        c2,
        endomorphisms,
        Mor(Sets)(c2_carrier, end_carrier)(representation_rule),
    )
    modules = Modules(c2, actegory)
    module = modules.from_endomorphism_action(representation)

    assert module in modules
    assert modules.forgetful().on_object(module) is x
    assert Modules(endomorphisms, actegory).forgetful().on_object(tautological) is x
    c2_acted = binary_product_data(Sets(), c2_carrier, x).apex()
    assert module.action().domain() is c2_acted
    assert module.action().codomain() is x
    assert module.action()(c2_acted.point((0, 0))).datum() == 0
    assert module.action()(c2_acted.point((1, 0))).datum() == 1
    assert module.action()(c2_acted.point((1, 1))).datum() == 0

    expected = Modules(endomorphisms, actegory).restriction(representation).on_object(tautological)
    assert ask(module.action() == expected.action()) is True


def test_sage_integer_module_reconstructs_exact_carrier_and_scalar_action() -> None:
    engine = FreeModule(ZZ, 2)
    modules = Modules(integer_scalar_monoid(), SelfAction(AbelianTensor()))
    module = sage_module_from_engine(modules, engine)
    carrier = modules.forgetful().on_object(module)
    value = engine((2, -1))
    other = engine((1, 4))

    assert module in modules
    assert carrier in AbelianGroups()
    assert carrier.point(value).datum().parent() is engine
    assert (carrier.point(value) + carrier.point(other)).datum() == value + other
    acted = simple_tensor(integer_group(), carrier, 3, value)
    image = module.action()(acted)
    assert image.parent() is carrier
    assert image.datum().parent() is engine
    assert image.datum() == 3 * value


test_endomorphism_action_is_restriction_along_the_supplied_map()
test_sage_integer_module_reconstructs_exact_carrier_and_scalar_action()
