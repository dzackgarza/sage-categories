"""The base-relative algebra owner is the retained presentation of monoids in relative modules."""

from sage.groups.additive_abelian.additive_abelian_group import AdditiveAbelianGroup

from sage_categories.algebra.abelian import (
    AbelianBimoduleTensor,
    AbelianGroups,
    AbelianModuleTensor,
    abelian_homomorphism,
    integer_group,
    presented_abelian_group,
)
from sage_categories.algebra.algebras import Algebras
from sage_categories.algebra.free_associative import (
    free_associative_generator,
    free_associative_substitution,
    integer_free_associative_algebra,
)
from sage_categories.algebra.indexed_modules import integer_scalar_monoid
from sage_categories.cat.category import ask
from sage_categories.cat.functors import Fun
from sage_categories.cat.monoidal import tensor_object
from sage_categories.cat.morphisms import Mor
from sage_categories.cat.structured_objects import EndofunctorAlgebras, Magmas, Monoids
from sage_categories.sets.finite import Sets


def test_relative_algebra_owner_retains_monoid_equivalence_and_forgetful_composites() -> (
    None
):
    scalars = integer_scalar_monoid()
    structure = AbelianBimoduleTensor(scalars)
    relative = structure.underlying_category()
    monoids = Monoids(structure)
    neutral = integer_free_associative_algebra(("x", "y"))
    algebras = Algebras(scalars, structure)
    presentation = algebras.monoid_presentation()
    algebra = algebras.from_monoid(neutral)

    assert algebras.base() is scalars
    assert algebras.monoidal_structure() is structure
    assert algebras.monoid_category() is monoids
    assert presentation in Fun(algebras, monoids).Equivalences()
    assert algebras.structure_functors() == (presentation,)
    assert presentation.on_object(algebra) is neutral
    assert presentation.inverse().on_object(neutral) is algebra
    assert algebras is not EndofunctorAlgebras(Fun(relative, relative).one())

    magma = monoids.to_magmas().on_object(neutral)
    carrier = Magmas(structure).forgetful().on_object(magma)
    tensor_square = tensor_object(structure.tensor(), carrier, carrier)
    assert neutral.operation() in Mor(relative)(tensor_square, carrier)
    assert neutral.unit_morphism() in Mor(relative)(structure.unit(), carrier)

    module = algebras.to_modules().on_object(algebra)
    assert module is relative.to_left().on_object(carrier)
    assert algebras.U_R().on_object(
        algebra
    ) is algebras.module_category().forgetful().on_object(module)
    assert algebras.functor_to_sets().codomain() is Sets
    assert algebras.functor_to_sets().on_object(
        algebra
    ) is algebras.module_category().functor_to_sets().on_object(module)

    x = free_associative_generator(neutral, 0)
    y = free_associative_generator(neutral, 1)
    neutral_map = free_associative_substitution(neutral, (y, x))
    magma_map = monoids.to_magmas().on_morphism(neutral_map)
    relative_map = Magmas(structure).forgetful().on_morphism(magma_map)
    algebra_map = algebras.homomorphism(algebra, algebra, relative_map)
    presented_map = presentation.on_morphism(algebra_map)

    assert algebra_map.domain() is algebra and algebra_map.codomain() is algebra
    assert ask(presented_map == neutral_map) is True
    assert (
        ask(
            algebras.to_modules().on_morphism(algebra_map)
            == relative.to_left().on_morphism(relative_map)
        )
        is True
    )


def test_algebra_presentation_retains_cartesian_lift() -> None:
    scalars = integer_scalar_monoid()
    structure = AbelianModuleTensor(scalars)
    modules = structure.underlying_category()
    monoids = Monoids(structure)
    algebras = Algebras(scalars, structure)
    presentation = algebras.monoid_presentation()
    regular = structure.unit()
    monoid = monoids(
        structure.left_unitor().component(regular),
        Mor(modules)(regular, regular).one(),
    )
    algebra = algebras.from_monoid(monoid)

    copy_engine = AdditiveAbelianGroup([0])
    copy = presented_abelian_group(copy_engine)
    generator = copy_engine.gen(0)
    forward = abelian_homomorphism(
        copy,
        integer_group(),
        lambda value: int(value.vector()[0]),
    )
    backward = abelian_homomorphism(
        integer_group(),
        copy,
        lambda value: int(value) * generator,
    )
    AbelianGroups().retain_inverses(forward, backward)

    module_map = modules.forgetful().cartesian_lift(forward, regular)
    copy_module = module_map.domain()
    reverse_module_map = modules.homomorphism(regular, copy_module, backward)
    modules.retain_inverses(module_map, reverse_module_map)

    magmas = Magmas(structure)
    magma = monoids.to_magmas().on_object(monoid)
    magma_map = magmas.forgetful().cartesian_lift(module_map, magma)
    copy_magma = magma_map.domain()
    reverse_magma_map = magmas.homomorphism(magma, copy_magma, reverse_module_map)
    magmas.retain_inverses(magma_map, reverse_magma_map)

    monoid_map = monoids.to_magmas().cartesian_lift(magma_map, monoid)
    copy_monoid = monoid_map.domain()
    reverse_monoid_map = monoids.homomorphism(monoid, copy_monoid, reverse_magma_map)
    monoids.retain_inverses(monoid_map, reverse_monoid_map)

    lift = presentation.cartesian_lift(monoid_map, algebra)

    assert presentation in Fun(algebras, monoids).Isofibrations()
    assert lift.codomain() is algebra
    assert presentation.on_morphism(lift) is monoid_map
    assert presentation.on_object(lift.domain()) is copy_monoid
    assert modules.forgetful().on_object(copy_module) is copy


test_relative_algebra_owner_retains_monoid_equivalence_and_forgetful_composites()
test_algebra_presentation_retains_cartesian_lift()
