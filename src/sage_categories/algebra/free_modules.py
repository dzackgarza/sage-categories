"""Finite free ordinary left modules over owned ring objects.

An ordinary scalar ring here is a monoid object of ``(Ab, tensor, ZZ)``.  Its
module category is the exact generic owner ``Modules(R, SelfAction(AbelianTensor()))``.
The regular module is ``R`` with its multiplication action, and ``R^n`` is the
finite biproduct/direct sum of copies of that regular module.  The retained
discrete basis family and its injections are the mathematical presentation;
matrices are only the finite chosen-basis spelling of a resulting module map.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from sage_categories.algebra.abelian import (
    AbelianGroups,
    AbelianTensor,
    abelian_homomorphism,
    indexed_free_abelian_coproduct,
    simple_tensor,
)
from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.choices import ChosenConstruction, SelectedChoice
from sage_categories.cat.cones import (
    cocone,
    cocone_apex,
    cocones,
    cone,
    cone_apex,
    cones,
)
from sage_categories.cat.diagrams import from_sequence
from sage_categories.cat.functors import Fun, Functor
from sage_categories.cat.modules import ModuleCategory, Modules
from sage_categories.cat.monoidal import SelfAction, tensor_morphism
from sage_categories.cat.morphisms import Mor, MorphismCategory
from sage_categories.cat.shapes import Discrete
from sage_categories.cat.structured_objects import MonoidCategory, Monoids
from sage_categories.sets.finite import Sets

__all__ = [
    "finite_free_basis",
    "finite_free_basis_family",
    "finite_free_injection",
    "finite_free_matrix_morphism",
    "finite_free_module",
    "finite_free_projection",
    "free_module_homomorphism",
    "ordinary_modules",
    "regular_module",
]


type ModuleMap = MorphismCategory.ObjectType
type PairRule = Callable[[tuple[ModuleMap, ...]], ModuleMap]
type BasisImageRule = Callable[[CategoryOfCategories.ElementType], ModuleMap]

_REGULAR_MODULES = ChosenConstruction()
_FINITE_FREE_MODULES = ChosenConstruction()
_FINITE_FREE_FAMILIES: SelectedChoice[Functor] = SelectedChoice()


def ordinary_modules(scalars: MonoidCategory.ObjectType) -> ModuleCategory:
    """The ordinary category of left modules over ``scalars`` in ``(Ab, tensor)``."""
    monoidal = AbelianTensor()
    assert scalars in Monoids(monoidal), f"{scalars!r} is not a ring/scalar monoid in {monoidal.underlying_category()!r}"
    return Modules(scalars, SelfAction(monoidal))


def _require_ordinary(modules: ModuleCategory) -> None:
    monoidal = AbelianTensor()
    assert modules.underlying_category() is AbelianGroups(), f"{modules!r} is not an ordinary module category in Ab"
    assert modules.actegory() is SelfAction(monoidal), f"{modules!r} does not use the selected ordinary self-action of Ab"
    assert modules.scalars() in Monoids(monoidal)


def regular_module(modules: ModuleCategory) -> ModuleCategory.ObjectType:
    """The regular left module ``R`` in this exact ordinary module category."""
    _require_ordinary(modules)
    return _REGULAR_MODULES(modules, (), lambda: modules(modules.scalars().operation()))


def _binary_module_biproduct(
    modules: ModuleCategory,
    first: ModuleCategory.ObjectType,
    second: ModuleCategory.ObjectType,
) -> tuple[
    ModuleCategory.ObjectType,
    tuple[ModuleMap, ModuleMap],
    tuple[ModuleMap, ModuleMap],
    Callable[[ModuleMap, ModuleMap], ModuleMap],
    Callable[[ModuleMap, ModuleMap], ModuleMap],
]:
    """The owned binary product/direct sum of two ordinary modules."""
    underlying = modules.forgetful()
    abelian = modules.underlying_category()
    first_carrier, second_carrier = underlying.on_object(first), underlying.on_object(second)
    apex = abelian.biproduct(first_carrier, second_carrier)
    diagram = from_sequence(abelian, (first_carrier, second_carrier))
    shape = diagram.domain()
    product = abelian.Limits(shape).universal_data(diagram)
    coproduct = abelian.Colimits(shape).universal_data(diagram)
    assert product.apex() is apex and coproduct.apex() is apex

    scalar = modules.carrier()
    scalar_identity = Mor(abelian)(scalar, scalar).one()
    action = modules.actegory().action()
    product_legs = (product.leg(shape(0)), product.leg(shape(1)))
    action_components = (
        first.action() * tensor_morphism(action, scalar_identity, product_legs[0]),
        second.action() * tensor_morphism(action, scalar_identity, product_legs[1]),
    )
    action_source = action_components[0].domain()
    module_action = product.lift(
        cones(diagram)(
            cone(
                diagram,
                action_source,
                lambda vertex: action_components[shape.label(vertex)],
            )
        )
    )
    result = modules(module_action)

    injections = tuple(modules.homomorphism(source, result, coproduct.leg(shape(position))) for position, source in enumerate((first, second)))
    projections = tuple(modules.homomorphism(result, target, product.leg(shape(position))) for position, target in enumerate((first, second)))

    def pair(left: ModuleMap, right: ModuleMap) -> ModuleMap:
        assert left.domain() is right.domain()
        source = left.domain()
        carrier_source = underlying.on_object(source)
        components = (underlying.on_morphism(left), underlying.on_morphism(right))
        arrow = product.lift(
            cones(diagram)(
                cone(
                    diagram,
                    carrier_source,
                    lambda vertex: components[shape.label(vertex)],
                )
            )
        )
        return modules.homomorphism(source, result, arrow)

    def copair(left: ModuleMap, right: ModuleMap) -> ModuleMap:
        assert left.codomain() is right.codomain()
        target = left.codomain()
        carrier_target = underlying.on_object(target)
        components = (underlying.on_morphism(left), underlying.on_morphism(right))
        arrow = coproduct.lift(
            cocones(diagram)(
                cocone(
                    diagram,
                    carrier_target,
                    lambda vertex: components[shape.label(vertex)],
                )
            )
        )
        return modules.homomorphism(result, target, arrow)

    module_diagram = from_sequence(modules, (first, second))
    module_shape = module_diagram.domain()
    modules.Limits(module_shape).with_universal_data(
        module_diagram,
        result,
        cone(module_diagram, result, lambda vertex: projections[module_shape.label(vertex)]),
        lambda candidate: pair(
            candidate.component(module_shape(0)),
            candidate.component(module_shape(1)),
        ),
    )
    modules.Colimits(module_shape).with_universal_data(
        module_diagram,
        result,
        cocone(module_diagram, result, lambda vertex: injections[module_shape.label(vertex)]),
        lambda candidate: copair(
            candidate.leg(module_shape(0)),
            candidate.leg(module_shape(1)),
        ),
    )
    return result, injections, projections, pair, copair


@dataclass(frozen=True, eq=False, slots=True)
class _FreeStage:
    module: ModuleCategory.ObjectType
    injections: tuple[ModuleMap, ...]
    projections: tuple[ModuleMap, ...]
    pair: PairRule
    copair: PairRule


def _extend_free_stage(
    modules: ModuleCategory,
    stage: _FreeStage,
    regular: ModuleCategory.ObjectType,
) -> _FreeStage:
    result, binary_injections, binary_projections, binary_pair, binary_copair = _binary_module_biproduct(modules, stage.module, regular)

    def pair(components: tuple[ModuleMap, ...]) -> ModuleMap:
        assert len(components) == len(stage.injections) + 1
        return binary_pair(stage.pair(components[:-1]), components[-1])

    def copair(components: tuple[ModuleMap, ...]) -> ModuleMap:
        assert len(components) == len(stage.injections) + 1
        return binary_copair(stage.copair(components[:-1]), components[-1])

    return _FreeStage(
        result,
        tuple(binary_injections[0] * injection for injection in stage.injections) + (binary_injections[1],),
        tuple(projection * binary_projections[0] for projection in stage.projections) + (binary_projections[1],),
        pair,
        copair,
    )


def _zero_module_morphism(
    modules: ModuleCategory,
    source: ModuleCategory.ObjectType,
    target: ModuleCategory.ObjectType,
) -> ModuleMap:
    """The additive zero map, lifted through the exact module owner."""
    underlying = modules.forgetful()
    arrow = modules.underlying_category().zero_morphism(
        underlying.on_object(source),
        underlying.on_object(target),
    )
    return modules.homomorphism(source, target, arrow)


def _zero_module(modules: ModuleCategory) -> ModuleCategory.ObjectType:
    """The zero ordinary module as the empty direct sum of regular modules."""
    empty = Sets(())
    carrier = indexed_free_abelian_coproduct(empty)
    action = modules.actegory().action()
    action_source = action.on_object(action.domain()((modules.carrier(), carrier)))
    zero_action = modules.underlying_category().zero_morphism(action_source, carrier)
    return modules(zero_action)


def _new_finite_free_module(modules: ModuleCategory, rank: int) -> ModuleCategory.ObjectType:
    assert rank >= 0
    regular = regular_module(modules)
    basis = Sets(range(rank))
    shape = Discrete(basis)
    family = Fun(shape, modules).constant(regular)

    match rank:
        case 0:
            module = _zero_module(modules)
            modules.Limits(shape).with_universal_data(
                family,
                module,
                cone(
                    family,
                    module,
                    lambda vertex: _zero_module_morphism(modules, module, family.on_object(vertex)),
                ),
                lambda candidate: _zero_module_morphism(modules, cone_apex(candidate), module),
            )
            modules.Colimits(shape).with_universal_data(
                family,
                module,
                cocone(
                    family,
                    module,
                    lambda vertex: _zero_module_morphism(modules, family.on_object(vertex), module),
                ),
                lambda candidate: _zero_module_morphism(modules, module, cocone_apex(candidate)),
            )
            _FINITE_FREE_FAMILIES.select(modules, (module,), family)
            return module
        case _:
            pass

    identity = Mor(modules)(regular, regular).one()
    stage = _FreeStage(
        regular,
        (identity,),
        (identity,),
        lambda components: components[0],
        lambda components: components[0],
    )
    for _ in range(1, rank):
        stage = _extend_free_stage(modules, stage, regular)

    vertices = tuple(shape.object_at(point) for point in basis)
    modules.Limits(shape).with_universal_data(
        family,
        stage.module,
        cone(family, stage.module, lambda vertex: stage.projections[int(vertex.point().datum())]),
        lambda candidate: stage.pair(tuple(candidate.component(vertex) for vertex in vertices)),
    )
    modules.Colimits(shape).with_universal_data(
        family,
        stage.module,
        cocone(family, stage.module, lambda vertex: stage.injections[int(vertex.point().datum())]),
        lambda candidate: stage.copair(tuple(candidate.leg(vertex) for vertex in vertices)),
    )
    _FINITE_FREE_FAMILIES.select(modules, (stage.module,), family)
    return stage.module


def finite_free_module(modules: ModuleCategory, rank: int) -> ModuleCategory.ObjectType:
    """The finite free left module ``R^rank`` as an owned direct sum of regular modules.

    ``rank`` is nonnegative.  The construction retains the finite owned basis set, its
    constant family of regular modules, and both the product and coproduct universal
    presentations.  Rank zero is the empty product/direct sum.  No matrix or coordinate
    presentation defines the object.
    """
    _require_ordinary(modules)
    rank = int(rank)
    match rank < 0:
        case True:
            raise ValueError("a free-module rank is nonnegative")
        case False:
            pass
    return _FINITE_FREE_MODULES(modules, (rank,), lambda: _new_finite_free_module(modules, rank))


def _free_family(modules: ModuleCategory, module: ModuleCategory.ObjectType) -> Functor:
    assert module in modules
    assert _FINITE_FREE_FAMILIES.has(modules, (module,)), f"{module!r} has no retained finite free-module basis"
    return _FINITE_FREE_FAMILIES.selected(modules, (module,))


def finite_free_basis(modules: ModuleCategory, module: ModuleCategory.ObjectType) -> CategoryOfCategories.ElementType:
    """The owned finite index set of the retained basis of ``module``."""
    return _free_family(modules, module).domain().object_set()


def finite_free_basis_family(modules: ModuleCategory, module: ModuleCategory.ObjectType) -> Functor:
    """The retained family ``i |-> R`` whose direct sum is ``module``."""
    return _free_family(modules, module)


def _basis_position(family: Functor, index: CategoryOfCategories.ElementType) -> int:
    basis = family.domain().object_set()
    assert index.parent() is basis, f"{index!r} is not a point of this free module's basis index"
    position = int(index.datum())
    assert 0 <= position < len(basis)
    return position


def _basis_vertex(family: Functor, index: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
    _basis_position(family, index)
    return family.domain().object_at(index)


def finite_free_injection(
    modules: ModuleCategory,
    module: ModuleCategory.ObjectType,
    index: CategoryOfCategories.ElementType,
) -> ModuleMap:
    """The basis-family injection ``R -> R^n`` at the owned basis index ``index``."""
    family = _free_family(modules, module)
    return modules.Colimits(family.domain()).universal_data(family).leg(_basis_vertex(family, index))


def finite_free_projection(
    modules: ModuleCategory,
    module: ModuleCategory.ObjectType,
    index: CategoryOfCategories.ElementType,
) -> ModuleMap:
    """The biproduct projection ``R^n -> R`` at the owned basis index ``index``."""
    family = _free_family(modules, module)
    return modules.Limits(family.domain()).universal_data(family).leg(_basis_vertex(family, index))


def free_module_homomorphism(
    modules: ModuleCategory,
    source: ModuleCategory.ObjectType,
    target: ModuleCategory.ObjectType,
    basis_image: BasisImageRule,
) -> ModuleMap:
    """The map out of a finite free module determined by its owned basis-family maps.

    ``basis_image(i)`` is a module morphism ``R -> target`` for a point ``i`` of the
    retained owned basis.  The retained coproduct presentation supplies the unique map
    from ``source``; the family need not be materialized and no coordinates are read.
    """
    family = _free_family(modules, source)
    regular = regular_module(modules)

    def component(vertex: CategoryOfCategories.ElementType) -> ModuleMap:
        arrow = basis_image(vertex.point())
        assert arrow.domain() is regular and arrow.codomain() is target
        return arrow

    return modules.Colimits(family.domain()).universal_data(family).lift(cocones(family)(cocone(family, target, component)))


def _right_scalar_morphism(
    modules: ModuleCategory,
    coefficient: CategoryOfCategories.ElementType,
) -> ModuleMap:
    """The left-module endomorphism ``r |-> r coefficient`` of the regular module."""
    carrier = modules.carrier()
    assert coefficient.parent() is carrier
    regular = regular_module(modules)
    multiplication = modules.scalars().operation()

    def right_multiply(datum: object) -> object:
        return multiplication(simple_tensor(carrier, carrier, datum, coefficient.datum())).datum()

    underlying = abelian_homomorphism(carrier, carrier, right_multiply)
    return modules.homomorphism(regular, regular, underlying)


def finite_free_matrix_morphism(
    modules: ModuleCategory,
    source: ModuleCategory.ObjectType,
    target: ModuleCategory.ObjectType,
    entries: tuple[tuple[CategoryOfCategories.ElementType, ...], ...],
) -> ModuleMap:
    """The finite chosen-basis specialization of a map ``R^m -> R^n``.

    Rows are indexed by the target basis and columns by the source basis.  For left
    modules, the entry ``a[j][i]`` acts on a source coefficient on the **right**:
    ``r e_i |-> (r a[j][i]) e_j``.  This convention is observable over a
    noncommutative scalar ring and is not used to define either module.
    """
    source_family, target_family = _free_family(modules, source), _free_family(modules, target)
    source_basis, target_basis = source_family.domain().object_set(), target_family.domain().object_set()
    source_rank, target_rank = len(source_basis), len(target_basis)
    if len(entries) != target_rank or any(len(row) != source_rank for row in entries):
        raise ValueError(f"matrix shape must be {target_rank} by {source_rank}")
    carrier = modules.carrier()
    if any(entry.parent() is not carrier for row in entries for entry in row):
        raise ValueError("matrix entries must be elements of the exact scalar carrier")

    def column_image(index: CategoryOfCategories.ElementType) -> ModuleMap:
        column = _basis_position(source_family, index)
        target_product = modules.Limits(target_family.domain()).universal_data(target_family)

        def component(vertex: CategoryOfCategories.ElementType) -> ModuleMap:
            row = _basis_position(target_family, vertex.point())
            return _right_scalar_morphism(modules, entries[row][column])

        return target_product.lift(
            cones(target_family)(
                cone(
                    target_family,
                    regular_module(modules),
                    component,
                )
            )
        )

    return free_module_homomorphism(modules, source, target, column_image)
