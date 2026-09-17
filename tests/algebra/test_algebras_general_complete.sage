"""Terminal integration of the base-relative algebra public surface."""

from sage.groups.additive_abelian.additive_abelian_group import AdditiveAbelianGroup
from sage.modules.free_module_element import vector
from sage.rings.integer_ring import ZZ

from sage_categories.algebra.abelian import (
    AbelianBimoduleTensor,
    AbelianTensor,
    abelian_homomorphism,
    integer_group,
    presented_abelian_group,
    simple_tensor,
    tensor_mediator,
)
from sage_categories.algebra.algebra_objects import (
    Algebras,
    integer_free_algebra,
    integer_free_algebra_generator,
    integer_free_algebra_homomorphism,
    restrict_algebra_scalars,
)
from sage_categories.algebra.indexed_modules import integer_scalar_monoid
from sage_categories.cat.category import ask
from sage_categories.cat.morphisms import Mor
from sage_categories.cat.structured_objects import Magmas, Monoids


def field_two():
    engine = AdditiveAbelianGroup([2])
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
    return element, group, Monoids(AbelianTensor())(multiplication, unit)


def test_scalar_change_and_free_maps_use_one_relative_algebra_owner() -> None:
    integers = integer_scalar_monoid()
    field_element, field_group, field = field_two()
    scalar_map = Monoids(AbelianTensor()).homomorphism(
        integers,
        field,
        field.unit_morphism(),
    )

    field_structure = AbelianBimoduleTensor(field)
    integer_structure = AbelianBimoduleTensor(integers)
    field_algebras = Algebras(field, field_structure)
    integer_algebras = Algebras(integers, integer_structure)

    # The monoidal unit is the scalar ring as an algebra over itself.
    field_bimodules = field_structure.underlying_category()
    regular = field_structure.unit()
    regular_monoid = Monoids(field_structure)(
        field_structure.left_unitor().component(regular),
        Mor(field_bimodules)(regular, regular).one(),
    )
    field_algebra = field_algebras.from_monoid(regular_monoid)

    restriction = restrict_algebra_scalars(
        field_algebras,
        integer_algebras,
        scalar_map,
    )
    restricted = restriction.on_object(field_algebra)
    assert restricted in integer_algebras
    assert integer_algebras.base() is integers
    assert field_algebras.base() is field

    # The same F_2 carrier now has the canonical ZZ-action, and the retained unit
    # is the supplied scalar map ZZ -> F_2 rather than a reused S-algebra object.
    module = integer_algebras.to_modules().on_object(restricted)
    generator = field_element(1)
    acted = simple_tensor(integer_group(), field_group, 3, generator)
    assert ask(module.action()(acted) == field_group.point(generator)) is True
    restricted_monoid = integer_algebras.monoid_presentation().on_object(restricted)
    restricted_bimodules = integer_structure.underlying_category()
    underlying_unit = restricted_bimodules.forgetful().on_morphism(
        restricted_monoid.unit_morphism()
    )
    assert (
        ask(underlying_unit(integer_group().point(1)) == field_group.point(generator))
        is True
    )

    restricted_identity = restriction.on_morphism(
        Mor(field_algebras)(field_algebra, field_algebra).one()
    )
    assert restricted_identity.domain() is restricted
    assert restricted_identity.codomain() is restricted
    assert (
        ask(restricted_identity == Mor(integer_algebras)(restricted, restricted).one())
        is True
    )

    # The pre-existing ZZ<x,y> evaluator is now consumed only through the same
    # base-relative owner.  A nonidentity generator permutation is an algebra map
    # whose module image has the exact owner supplied by that algebra category.
    free = integer_free_algebra(integer_algebras, ("x", "y"))
    x = integer_free_algebra_generator(integer_algebras, free, 0)
    y = integer_free_algebra_generator(integer_algebras, free, 1)
    swap = integer_free_algebra_homomorphism(
        integer_algebras,
        free,
        free,
        (y, x),
    )
    underlying_swap = integer_algebras.to_modules().on_morphism(swap)
    assert swap in Mor(integer_algebras)(free, free)
    assert ask(underlying_swap(x) == y) is True
    assert ask(underlying_swap(x) == x) is False

    free_monoid = integer_algebras.monoid_presentation().on_object(free)
    free_magma = integer_algebras.monoid_category().to_magmas().on_object(free_monoid)
    free_bimodule = Magmas(integer_structure).forgetful().on_object(free_magma)
    assert integer_algebras.to_modules().on_object(
        free
    ) is integer_structure.underlying_category().to_left().on_object(free_bimodule)


test_scalar_change_and_free_maps_use_one_relative_algebra_owner()
