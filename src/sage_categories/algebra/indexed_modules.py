"""Arbitrary-index free integer modules as genuine module coproducts.

The evaluator here is deliberately narrower than the category ``Modules(A,C)``:
it realizes the ordinary free module ``ZZ^(S)`` for an arbitrary owned set
``S``.  The general module category remains coordinate-free.  The additive
carrier and its universal coproduct are owned by :mod:`sage_categories.algebra.abelian`;
this file equips that carrier with the canonical action of the tensor-unit ring
``ZZ`` and retains the same universal presentation in the module category.
"""

from __future__ import annotations

from collections.abc import Hashable, Mapping
from dataclasses import dataclass

from sage_categories.algebra.abelian import (
    AbelianGroups,
    AbelianTensor,
    _indexed_free_record,
    _rule_abelian_homomorphism,
    indexed_free_abelian_coproduct,
    indexed_free_abelian_injection,
    indexed_free_abelian_mediator,
    integer_group,
)
from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.cones import cocone, cocone_apex
from sage_categories.cat.functors import Fun
from sage_categories.cat.modules import ModuleCategory, Modules
from sage_categories.cat.monoidal import SelfAction
from sage_categories.cat.morphisms import Mor, MorphismCategory
from sage_categories.cat.shapes import Discrete
from sage_categories.cat.structured_objects import Monoids
from sage_categories.kernel.refinement import refine
from sage_categories.kernel.retention import identity_key
from sage_categories.kernel.sage_runtime import MonoDict, cached_function
from sage_categories.sets.finite import Sets

__all__ = [
    "indexed_free_integer_coefficients",
    "indexed_free_integer_element",
    "indexed_free_integer_homomorphism",
    "indexed_free_integer_module",
    "indexed_free_integer_support",
    "integer_regular_module",
    "integer_scalar_monoid",
]


@dataclass(frozen=True, eq=False, slots=True)
class _IndexedFreeIntegerModuleData:
    modules: ModuleCategory
    carrier: CategoryOfCategories.ElementType


_indexed_integer_module_data: MonoDict = MonoDict()


@cached_function(key=lambda: 0)
def integer_scalar_monoid() -> CategoryOfCategories.ElementType:
    r"""The tensor-unit ring ``ZZ`` as a monoid object of ``(Ab, tensor)``.

    The multiplication ``ZZ tensor ZZ -> ZZ`` is the selected left unitor, and
    the unit ``ZZ -> ZZ`` is the identity.  Thus this is not a second integer
    object: its carrier is literally :func:`integer_group`.
    """
    monoidal = AbelianTensor()
    unit = integer_group()
    multiplication = monoidal.left_unitor().component(unit)
    identity = Mor(AbelianGroups())(unit, unit).one()
    return Monoids(monoidal)(multiplication, identity)


@cached_function(key=lambda: 0)
def integer_regular_module() -> ModuleCategory.ObjectType:
    r"""The regular left ``ZZ``-module in ``Modules(ZZ, Ab)``."""
    monoidal = AbelianTensor()
    scalars = integer_scalar_monoid()
    modules = Modules(scalars, SelfAction(monoidal))
    return modules(scalars.operation())


def _certified_integer_module(
    carrier: CategoryOfCategories.ElementType,
) -> ModuleCategory.ObjectType:
    r"""Equip an indexed free abelian group with the canonical ``ZZ`` action.

    The action is the selected tensor left unitor.  Its two module axioms are
    exactly monoidal unitality/associativity, so the native indexed-free branch
    is admitted by that theorem rather than by enumeration of the carrier.
    """
    monoidal = AbelianTensor()
    modules = Modules(integer_scalar_monoid(), SelfAction(monoidal))
    action = monoidal.left_unitor().component(carrier)
    algebra = modules._algebras.algebra(carrier, action)
    refine(algebra, modules.ambient())
    refine(algebra, modules)
    return algebra


@cached_function(key=identity_key)
def indexed_free_integer_module(
    index_set: CategoryOfCategories.ElementType,
) -> ModuleCategory.ObjectType:
    r"""Return ``ZZ^(S)`` as the coproduct of ``S`` copies of the regular module.

    ``S`` may be infinite or nonenumerable.  Every element is represented by a
    native finite-support sum whose keys lie in the whole supplied ``S``.  The
    returned object retains the discrete diagram, its canonical injections,
    and the universal mediator in ``Modules(ZZ, Ab)``.
    """
    assert index_set in Sets
    monoidal = AbelianTensor()
    modules = Modules(integer_scalar_monoid(), SelfAction(monoidal))
    regular = integer_regular_module()
    carrier = indexed_free_abelian_coproduct(index_set)
    module = _certified_integer_module(carrier)
    _indexed_integer_module_data[module] = _IndexedFreeIntegerModuleData(modules, carrier)
    shape = Discrete(index_set)
    diagram = Fun(shape, modules).constant(regular)

    def leg(vertex: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
        additive = indexed_free_abelian_injection(carrier, vertex.point().datum())
        return modules.homomorphism(regular, module, additive)

    selected = cocone(diagram, module, leg)

    def mediator(candidate) -> MorphismCategory.ObjectType:
        target = cocone_apex(candidate)
        target_carrier = modules.forgetful().on_object(target)

        def component(index: Hashable) -> MorphismCategory.ObjectType:
            vertex = shape.object_at(index_set.point(index))
            return modules.forgetful().on_morphism(candidate.component(vertex))

        additive = indexed_free_abelian_mediator(carrier, target_carrier, component)
        return modules.homomorphism(module, target, additive)

    return modules.Colimits(shape).with_universal_data(
        diagram,
        module,
        selected,
        mediator,
    )


def indexed_free_integer_element(
    module: ModuleCategory.ObjectType,
    terms: Mapping[Hashable, int],
) -> CategoryOfCategories.ElementType:
    r"""Return the finite-support element ``sum_i terms[i] e_i`` of ``module``."""
    assert module in _indexed_integer_module_data, f"{module!r} is not an indexed free integer module"
    module_data = _indexed_integer_module_data[module]
    record = _indexed_free_record(module_data.carrier)
    native_terms = tuple((record.index_set.representative(index), coefficient) for index, coefficient in terms.items() if int(coefficient) != 0)
    datum = record.engine.sum_of_terms(native_terms, distinct=True)
    return module.point(datum)


def indexed_free_integer_support(
    module: ModuleCategory.ObjectType,
    element: CategoryOfCategories.ElementType,
) -> CategoryOfCategories.ElementType:
    r"""Return the finite owned set of indices supporting ``element``."""
    assert element.parent() is module
    assert module in _indexed_integer_module_data, f"{module!r} is not an indexed free integer module"
    module_data = _indexed_integer_module_data[module]
    _indexed_free_record(module_data.carrier)
    support = tuple(element.datum().monomial_coefficients(copy=False))
    return Sets(support)


def indexed_free_integer_coefficients(
    module: ModuleCategory.ObjectType,
    element: CategoryOfCategories.ElementType,
) -> dict[Hashable, int]:
    r"""Return the finite coefficient map of ``element`` in the selected basis of ``ZZ^(S)``.

    This is the coordinate surface of the indexed-free construction itself.  It
    exposes the owned basis labels and integer coefficients, not the private
    ``CombinatorialFreeModule`` element that stores them.
    """
    assert element.parent() is module
    assert module in _indexed_integer_module_data, f"{module!r} is not an indexed free integer module"
    module_data = _indexed_integer_module_data[module]
    _indexed_free_record(module_data.carrier)
    return {index: int(coefficient) for index, coefficient in element.datum().monomial_coefficients(copy=False).items() if int(coefficient) != 0}


def indexed_free_integer_homomorphism(
    source: ModuleCategory.ObjectType,
    target: ModuleCategory.ObjectType,
    basis_image,
) -> MorphismCategory.ObjectType:
    r"""Return the unique ``ZZ``-linear map with the supplied images of basis indices.

    ``basis_image(i)`` is a point of ``target``.  Evaluation is the universal
    map of the indexed coproduct and therefore inspects only the finite support
    of each supplied source element; it never traverses the full index set.
    """
    assert source in _indexed_integer_module_data, f"{source!r} is not an indexed free integer module"
    source_data = _indexed_integer_module_data[source]
    assert target in source_data.modules, "indexed free module maps require one module category"
    source_carrier = source_data.carrier
    target_carrier = source_data.modules.forgetful().on_object(target)

    def component(index: Hashable) -> MorphismCategory.ObjectType:
        image = basis_image(index)
        assert image.parent() is target
        return _rule_abelian_homomorphism(
            integer_group(),
            target_carrier,
            lambda coefficient: int(coefficient) * image.datum(),
        )

    additive = indexed_free_abelian_mediator(source_carrier, target_carrier, component)
    return source_data.modules.homomorphism(source, target, additive)
