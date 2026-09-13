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

from sage_categories.algebra.abelian import (
    AbelianGroups,
    AbelianTensor,
    _coordinates,
    _indexed_free_record,
    _rule_abelian_homomorphism,
    abelian_homomorphism,
    coequalizer_mediator,
    coequalizer_projection,
    indexed_free_abelian_coproduct,
    indexed_free_abelian_injection,
    indexed_free_abelian_mediator,
    integer_group,
    presented_abelian_group,
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
from sage_categories.kernel.sage_runtime import cached_function
from sage_categories.sets.finite import Sets

__all__ = [
    "IntegerModulePresentation",
    "finite_free_integer_module",
    "indexed_free_integer_coefficients",
    "indexed_free_integer_element",
    "indexed_free_integer_homomorphism",
    "indexed_free_integer_module",
    "indexed_free_integer_support",
    "integer_module",
    "integer_regular_module",
    "integer_scalar_monoid",
    "presented_integer_module",
]


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


def _integer_modules() -> ModuleCategory:
    """The selected category ``Modules(ZZ, Ab)`` used by integer-module constructions."""
    monoidal = AbelianTensor()
    return Modules(integer_scalar_monoid(), SelfAction(monoidal))


def _indexed_integer_carrier(
    module: ModuleCategory.ObjectType,
) -> tuple[ModuleCategory, CategoryOfCategories.ElementType]:
    """Recover and validate the indexed-free additive carrier of ``module``."""
    modules = _integer_modules()
    assert module in modules, f"{module!r} is not an integer module"
    carrier = modules.forgetful().on_object(module)
    _indexed_free_record(carrier)
    return modules, carrier


@cached_function(key=lambda: 0)
def integer_regular_module() -> ModuleCategory.ObjectType:
    r"""The regular left ``ZZ``-module in ``Modules(ZZ, Ab)``."""
    scalars = integer_scalar_monoid()
    modules = _integer_modules()
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
    modules = _integer_modules()
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
    modules = _integer_modules()
    regular = integer_regular_module()
    carrier = indexed_free_abelian_coproduct(index_set)
    module = _certified_integer_module(carrier)
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
    _modules, carrier = _indexed_integer_carrier(module)
    record = _indexed_free_record(carrier)
    native_terms = tuple((record.index_set.representative(index), coefficient) for index, coefficient in terms.items() if int(coefficient) != 0)
    datum = record.engine.sum_of_terms(native_terms, distinct=True)
    return module.point(datum)


def indexed_free_integer_support(
    module: ModuleCategory.ObjectType,
    element: CategoryOfCategories.ElementType,
) -> CategoryOfCategories.ElementType:
    r"""Return the finite owned set of indices supporting ``element``."""
    assert element.parent() is module
    _indexed_integer_carrier(module)
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
    _indexed_integer_carrier(module)
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
    modules, source_carrier = _indexed_integer_carrier(source)
    assert target in modules, "indexed free module maps require one module category"
    target_carrier = modules.forgetful().on_object(target)

    def component(index: Hashable) -> MorphismCategory.ObjectType:
        image = basis_image(index)
        assert image.parent() is target
        return _rule_abelian_homomorphism(
            integer_group(),
            target_carrier,
            lambda coefficient: int(coefficient) * image.datum(),
        )

    additive = indexed_free_abelian_mediator(source_carrier, target_carrier, component)
    return modules.homomorphism(source, target, additive)


@cached_function(key=identity_key)
def integer_module(
    additive_group: CategoryOfCategories.ElementType,
) -> ModuleCategory.ObjectType:
    r"""Equip a represented abelian group with its canonical left ``ZZ`` action."""
    assert additive_group in AbelianGroups()
    return _certified_integer_module(additive_group)


@cached_function
def finite_free_integer_module(rank: int) -> ModuleCategory.ObjectType:
    r"""The finite free left module ``ZZ^rank`` in the general integer-module category."""
    from sage.groups.additive_abelian.additive_abelian_group import AdditiveAbelianGroup

    rank = int(rank)
    if rank < 0:
        raise ValueError("a free-module rank is nonnegative")
    return integer_module(presented_abelian_group(AdditiveAbelianGroup([0] * rank)))


class IntegerModulePresentation:
    r"""A finite matrix presentation ``ZZ^m -> ZZ^n -> M`` with its cokernel map."""

    def __init__(self, relation_rows) -> None:
        from sage.matrix.constructor import matrix
        from sage.modules.free_module_element import vector
        from sage.rings.integer_ring import ZZ

        rows = tuple(tuple(int(entry) for entry in row) for row in relation_rows)
        columns = len(rows[0]) if rows else 0
        if any(len(row) != columns for row in rows):
            raise ValueError("a relation matrix has one common target rank")
        relation_matrix = matrix(ZZ, rows) if rows else matrix(ZZ, 0, columns)
        source = finite_free_integer_module(len(rows))
        target = finite_free_integer_module(columns)
        modules = _integer_modules()
        source_group = modules.forgetful().on_object(source)
        target_group = modules.forgetful().on_object(target)
        source_form = _coordinates(source_group)
        target_form = _coordinates(target_group)

        def relation_rule(datum):
            coordinates = vector(ZZ, source_form.coordinates(datum)) * relation_matrix
            return target_form.element(tuple(int(entry) for entry in coordinates))

        relation_additive = abelian_homomorphism(source_group, target_group, relation_rule)
        zero_additive = abelian_homomorphism(
            source_group,
            target_group,
            lambda datum: target_form.zero_datum(),
        )
        relation = modules.homomorphism(source, target, relation_additive)
        zero = modules.homomorphism(source, target, zero_additive)
        additive_projection = coequalizer_projection(relation_additive, zero_additive)
        quotient = integer_module(additive_projection.codomain())
        projection = modules.homomorphism(target, quotient, additive_projection)

        self._relation_matrix = relation_matrix
        self._modules = modules
        self._source = source
        self._target = target
        self._relation = relation
        self._zero = zero
        self._quotient = quotient
        self._additive_projection = additive_projection
        self._projection = projection

    def relation_matrix(self):
        return self._relation_matrix

    def module_category(self):
        return self._modules

    def source_free_module(self):
        return self._source

    def target_free_module(self):
        return self._target

    def relation_morphism(self):
        return self._relation

    def zero_morphism(self):
        return self._zero

    def module(self):
        return self._quotient

    def cokernel_projection(self):
        return self._projection

    def target_basis_element(self, index: int):
        target_group = self._modules.forgetful().on_object(self.target_free_module())
        form = _coordinates(target_group)
        coordinates = [0] * form.rank()
        coordinates[int(index)] = 1
        return self.target_free_module().point(form.element(tuple(coordinates)))

    def factor(
        self,
        target: ModuleCategory.ObjectType,
        coequalizing: MorphismCategory.ObjectType,
    ) -> MorphismCategory.ObjectType:
        r"""Factor a map killing the relation matrix through the retained CAP cokernel."""
        assert coequalizing.domain() is self.target_free_module()
        assert coequalizing.codomain() is target
        additive = self._modules.forgetful().on_morphism(coequalizing)
        mediator = coequalizer_mediator(self._additive_projection, additive)
        return self._modules.homomorphism(self.module(), target, mediator)


def presented_integer_module(relation_rows) -> IntegerModulePresentation:
    r"""Construct the finite integer-module presentation with this relation matrix."""
    return IntegerModulePresentation(relation_rows)
