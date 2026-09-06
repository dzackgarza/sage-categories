"""Finitely generated abelian groups over Sage's presented-module engine, and their tensor product.

``AbelianGroups()`` is ``AdditiveGroups(Cartesian(Sets())).Commutative()``, the commutative
additive group objects of sets (``specs/magmas-monoids-semirings.md``, "Groups").  This leaf
adds two things.  ``presented_abelian_group(engine)`` constructs the object of that category
carried by the elements of a finite Sage ``AdditiveAbelianGroup`` or ``ZZ^n / W`` module, with
the engine's addition; ``integer_group()`` is the integers on their rule-defined carrier.  The
tensor product is the selected monoidal structure ``AbelianTensor()`` on ``AbelianGroups()``
with unit the integers (``specs/modules.md``, "Instances").

The private engine is Smith coordinates.  Every presented carrier registers its
``Presentation`` with ``Sets`` as the object form, and every homomorphism between presented
carriers is constructed from its ``LinearForm``, the integer matrix of its action on Smith
generators; ``Sets`` composes, pairs, and projects these forms itself and decides the
equality of two such maps by comparing matrices modulo the target orders, so no law is
decided by enumeration.  A presented group ``A = Z^n / R_A`` in Smith generators of orders
``(d_1, ..., d_n)`` has ``A ⊗ B = Z^{nm} / (R_A ⊗ 1 + 1 ⊗ R_B)``, the quotient of the free
module on the pairs of generators by ``d_i e_{ij}`` and ``d'_j e_{ij}`` (Stacks, tag 00CV,
tensor products; the presentation is the standard one from right exactness of ``⊗``).  The
biadditive map sends ``(a, b)`` to ``Σ a_i b_j e_{ij}``, and a biadditive ``f: A × B -> C``
factors through the mediator that sends the class of ``e_{ij}`` to ``f(e_i, e_j)``.
"""

from __future__ import annotations

__all__ = [
    "AbelianGroups",
    "AbelianTensor",
    "LinearForm",
    "Presentation",
    "abelian_homomorphism",
    "bilinear_map",
    "coequalizer_mediator",
    "coequalizer_projection",
    "integer_group",
    "presented_abelian_group",
    "simple_tensor",
    "tensor_mediator",
]

from collections.abc import Callable, Hashable
from dataclasses import dataclass
from functools import partial

from sage.groups.additive_abelian.additive_abelian_group import AdditiveAbelianGroup_class
from sage.matrix.constructor import block_matrix, identity_matrix, matrix, zero_matrix
from sage.matrix.matrix_integer_dense import Matrix_integer_dense
from sage.modules.fg_pid.fgp_element import FGP_Element
from sage.modules.fg_pid.fgp_module import FGP_Module_class
from sage.modules.free_module import FreeModule
from sage.modules.free_module_element import vector
from sage.rings.integer_ring import ZZ
from sympy import Q, false, true

from sage_categories.cat.calculus import binary_product_data, natural_isomorphism
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.functors import Cat, Fun
from sage_categories.cat.monoidal import Cartesian, MonoidalStructures, MonoidalStructuresCategory, tensor_parentheses, tensor_units
from sage_categories.cat.morphisms import Mor, MorphismCategory
from sage_categories.cat.predicates import Proposition
from sage_categories.cat.structured_objects import AdditiveGroups, Groups, Monoids
from sage_categories.kernel.retention import identity_key
from sage_categories.kernel.sage_runtime import MonoDict, cached_function
from sage_categories.sets.finite import Sets

type Engine = AdditiveAbelianGroup_class | FGP_Module_class


@dataclass(frozen=True, eq=False, slots=True)
class Presentation:
    """Smith coordinates of a presented carrier: generator orders and the two coordinate maps on data.

    A direct sum of presented carriers, the ``Sets`` product of their carriers, records its
    factors so that projections and pairings have matrices.  This is the object form
    ``Sets`` reads (``sets.finite.ObjectForm``).
    """

    orders: tuple[int, ...]
    coordinates: Callable[[Hashable], tuple[int, ...]]
    element: Callable[[tuple[int, ...]], Hashable]
    factors: tuple[Presentation, ...] = ()

    def rank(self) -> int:
        return len(self.orders)

    def identity(self) -> LinearForm:
        return LinearForm(self, self, identity_matrix(ZZ, self.rank()))

    def direct_sum(self, factors: tuple[Presentation, ...]) -> Presentation:
        sizes = tuple(factor.rank() for factor in factors)

        def coordinates(datum: Hashable) -> tuple[int, ...]:
            return tuple(c for factor, component in zip(factors, datum, strict=True) for c in factor.coordinates(component))

        def element(coords: tuple[int, ...]) -> Hashable:
            parts, start = [], 0
            for factor, size in zip(factors, sizes):
                parts.append(factor.element(tuple(coords[start : start + size])))
                start += size
            return tuple(parts)

        return Presentation(tuple(order for factor in factors for order in factor.orders), coordinates, element, factors)

    def projection(self, index: int) -> LinearForm:
        offset = sum(factor.rank() for factor in self.factors[:index])
        factor = self.factors[index]
        matrix = zero_matrix(ZZ, self.rank(), factor.rank())
        for k in range(factor.rank()):
            matrix[offset + k, k] = 1
        return LinearForm(self, factor, matrix)

    def pair(self, components: tuple[LinearForm, ...], target: Presentation) -> LinearForm:
        assert all(component.source is self for component in components)
        if not components:
            return LinearForm(self, target, zero_matrix(ZZ, self.rank(), target.rank()))
        return LinearForm(self, target, block_matrix(ZZ, 1, len(components), [component.matrix for component in components], subdivide=False))

    def zero_datum(self) -> Hashable:
        return self.element((0,) * self.rank())

    def zero_map(self, source: Presentation) -> LinearForm:
        return LinearForm(source, self, zero_matrix(ZZ, source.rank(), self.rank()))


def _descends(matrix: Matrix_integer_dense, source_orders: tuple[int, ...], target_orders: tuple[int, ...]) -> bool:
    """Whether an integer matrix on generators defines a map of the quotients: ``d_i M_{ij} ≡ 0 (mod e_j)``."""
    return all(
        (source * matrix[i, j]) % target == 0 if target else source * matrix[i, j] == 0
        for i, source in enumerate(source_orders)
        if source
        for j, target in enumerate(target_orders)
    )


@dataclass(frozen=True, eq=False, slots=True)
class LinearForm:
    """A homomorphism between presented carriers as its integer matrix on Smith generators, ``x ↦ x · M`` on coordinate rows.

    This is the map form ``Sets`` reads (``sets.finite.MapForm``): composition is the
    matrix product, equality is equality of matrices reduced modulo the target orders,
    and a unimodular matrix between free presentations inverts.
    """

    source: Presentation
    target: Presentation
    matrix: Matrix_integer_dense

    def evaluate(self, datum: Hashable) -> Hashable:
        image = vector(ZZ, self.source.coordinates(datum)) * self.matrix
        return self.target.element(tuple(int(c) for c in image))

    def compose(self, first: LinearForm) -> LinearForm | None:
        if not isinstance(first, LinearForm) or first.target is not self.source:
            return None
        return LinearForm(first.source, self.target, first.matrix * self.matrix)

    def equals(self, other: LinearForm) -> bool | None:
        if not isinstance(other, LinearForm) or other.source is not self.source or other.target is not self.target:
            return None
        return self.reduced() == other.reduced()

    def reduced(self) -> Matrix_integer_dense:
        """The matrix with each column reduced modulo the order of its target generator."""
        matrix = self.matrix.__copy__()
        for column, order in enumerate(self.target.orders):
            if order:
                for row in range(matrix.nrows()):
                    matrix[row, column] = matrix[row, column] % order
        matrix.set_immutable()
        return matrix

    def inverse(self) -> LinearForm | None:
        """The two-sided inverse when the matrix is unimodular and both it and its integer inverse respect the relations.

        A square integer matrix of determinant ``±1`` has an integer inverse, and each of
        the two descends to the quotients exactly when ``d_i M_{ij} ≡ 0 (mod e_j)`` for the
        source orders ``d`` and target orders ``e``.  Both conditions checked, the two maps
        compose to the identity on coordinates and so on the groups.  Anything else leaves
        invertibility to another route rather than asserting it.
        """
        if self.matrix.nrows() != self.matrix.ncols() or abs(self.matrix.det()) != 1:
            return None
        candidate = self.matrix.inverse().change_ring(ZZ)
        if not _descends(candidate, self.target.orders, self.source.orders):
            return None
        return LinearForm(self.target, self.source, candidate)


@dataclass(frozen=True, eq=False, slots=True)
class _TensorData:
    """The factors of a tensor product object and the presented module on the pairs of their generators."""

    first: CategoryOfCategories.ElementType
    second: CategoryOfCategories.ElementType
    quotient: FGP_Module_class


_presentations: MonoDict = MonoDict()
_tensor_data: MonoDict = MonoDict()
_forms: MonoDict = MonoDict()
_quotient_covers: MonoDict = MonoDict()

_terminal_presentation = Presentation((), lambda datum: (), lambda coords: ())
Sets.retain_form(Sets.Terminal(), _terminal_presentation)


def _structure() -> MonoidalStructuresCategory.ObjectType:
    return Cartesian(Sets())


@cached_function(key=lambda: 0)
def AbelianGroups() -> Category:
    """``Ab``: commutative additive group objects of sets, ``AdditiveGroups(Cartesian(Sets())).Commutative()``."""
    return AdditiveGroups(_structure()).Commutative()


def _points(group: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
    """The set of points of a group object: its image under the carrier functors of the named copies."""
    groups = AdditiveGroups(_structure())
    monoids, magmas = groups.named_monoids(), groups.named_monoids().named_magmas()
    return magmas.to_carrier().on_object(monoids.to_named_magmas().on_object(groups.to_named_monoids().on_object(group)))


def presentation(group: CategoryOfCategories.ElementType) -> Presentation:
    """The Smith presentation this leaf retained for a group object; a group built elsewhere has none."""
    assert group in _presentations, f"{group!r} was not constructed from a presented engine, so it has no Smith coordinates"
    return _presentations[group]


def _group_from_operations(
    carrier: CategoryOfCategories.ElementType,
    form: Presentation,
    zero: Hashable,
) -> CategoryOfCategories.ElementType:
    """The object of ``Ab`` on a presented carrier: addition is the linear form ``(x, y) ↦ x + y``, decided a commutative group on the way."""
    structure = _structure()
    Sets.retain_form(carrier, form)
    square = binary_product_data(Sets(), carrier, carrier).apex()
    identity = identity_matrix(ZZ, form.rank())
    addition = Mor(Sets)(square, carrier)(LinearForm(Sets.form_of(square), form, identity.stack(identity)))
    unit = Mor(Sets)(structure.unit(), carrier)(lambda _: zero)
    monoid = Monoids(structure)(addition, unit)
    assert monoid in Groups(structure), f"{addition!r} is not a group operation"
    group = AdditiveGroups(structure).renamed(monoid)
    assert group in AbelianGroups(), f"{addition!r} is not commutative"
    _presentations[group] = form
    return group


def _group_from_engine(engine: Engine) -> CategoryOfCategories.ElementType:
    """A fresh object of ``Ab`` whose carrier is the set the engine's membership states.

    The carrier is stated by that membership and never materialized: the tensor square of a
    four-generator group already has ``2^16`` elements and its cube ``2^64``, while every
    operation on it is a matrix on four generators.

    Sage identifies presented modules with equal relations, so two tensor products can share
    one engine; each tensor product is nevertheless its own object of ``Ab``, which is why
    this constructor is not retained by engine.
    """
    form = Presentation(
        tuple(int(order) for order in engine.invariants()),
        lambda datum: tuple(int(c) for c in datum.vector()),
        lambda coordinates: engine.linear_combination_of_smith_form_gens(vector(ZZ, coordinates)),
    )
    return _group_from_operations(Sets.from_membership(partial(_engine_membership, engine)), form, engine.zero())


def _engine_membership(engine: Engine, datum: Hashable) -> Proposition:
    """Whether a datum is an element of the engine; the engine decides its own membership exactly."""
    return true if isinstance(datum, FGP_Element) and datum.parent() is engine else false


@cached_function(key=identity_key)
def presented_abelian_group(engine: Engine) -> CategoryOfCategories.ElementType:
    """The object of ``Ab`` whose points are the elements of a finite presented Sage abelian group, with its addition; one object per engine."""
    return _group_from_engine(engine)


@cached_function(key=lambda: 0)
def integer_group() -> CategoryOfCategories.ElementType:
    """``Z`` as an object of ``Ab``: the rule-defined integers, the free group on one generator."""
    integers = Sets.from_membership(lambda n: Q.integer(n))
    form = Presentation((0,), lambda datum: (int(datum),), lambda coordinates: int(coordinates[0]))
    return _group_from_operations(integers, form, 0)


def _linear_homomorphism(
    source: CategoryOfCategories.ElementType,
    target: CategoryOfCategories.ElementType,
    form: LinearForm,
) -> MorphismCategory.ObjectType:
    """The morphism of ``Ab`` with this linear form; the monoid constructor checks additivity and the unit through the forms."""
    structure = _structure()
    renaming = AdditiveGroups(structure).product_projection(0)
    carrier_map = Mor(Sets)(_points(source), _points(target))(form)
    monoid_map = Monoids(structure).homomorphism(renaming.on_object(source), renaming.on_object(target), carrier_map)
    result = AdditiveGroups(structure).homomorphism(source, target, monoid_map)
    _forms[result] = form
    return result


def linear_form(arrow: MorphismCategory.ObjectType) -> LinearForm:
    """The integer matrix on Smith generators of a homomorphism this leaf built."""
    assert arrow in _forms, f"{arrow!r} was not built by this leaf, so it carries no matrix"
    return _forms[arrow]


def _generators(form: Presentation) -> tuple[Hashable, ...]:
    return tuple(form.element(tuple(int(i == k) for k in range(form.rank()))) for i in range(form.rank()))


def _matrix_of_rows(rows: list, width: int) -> Matrix_integer_dense:
    """The integer matrix with these coordinate rows; a vector is a row here, not a column."""
    return matrix(ZZ, len(rows), width, [entry for row in rows for entry in row])


def abelian_homomorphism(
    source: CategoryOfCategories.ElementType,
    target: CategoryOfCategories.ElementType,
    rule: Callable[[Hashable], Hashable],
) -> MorphismCategory.ObjectType:
    """The morphism of ``Ab`` that extends a rule's values on the generators linearly.

    The matrix is the rule read on the source's generators, and the morphism it defines is
    that linear extension.  The zero, the generators, and their pairwise sums are compared
    with it, which refutes a rule that is not the additive map it presents itself as.
    """
    left, right = presentation(source), presentation(target)
    form = LinearForm(left, right, _matrix_of_rows([vector(ZZ, right.coordinates(rule(generator))) for generator in _generators(left)], right.rank()))
    generators = _generators(left)
    samples = (left.zero_datum(), *generators, *(first + second for first in generators for second in generators))
    assert all(rule(sample) == form.evaluate(sample) for sample in samples), f"{rule!r} differs from its linear extension on {source!r}"
    return _linear_homomorphism(source, target, form)


@cached_function(key=identity_key)
def coequalizer_projection(
    first: MorphismCategory.ObjectType,
    second: MorphismCategory.ObjectType,
) -> MorphismCategory.ObjectType:
    """The universal map ``q: B -> B / im(f - g)`` coequalizing two homomorphisms ``f, g: A -> B`` of ``Ab``.

    Two parallel homomorphisms of abelian groups are coequalized by the quotient of their
    common target by the subgroup their difference generates.  In Smith generators that
    adjoins the rows of ``M_f - M_g`` to the relations of the target, so the quotient is
    again a presented group and needs no enumeration.

    The coequalizer object is the codomain of this map, and ``coequalizer_mediator``
    factors a coequalizing homomorphism through it.
    """
    source, target = first.domain(), first.codomain()
    assert second.domain() is source and second.codomain() is target, f"{first!r} and {second!r} are not parallel"
    into = presentation(target)
    difference = linear_form(first).matrix - linear_form(second).matrix
    free = FreeModule(ZZ, into.rank())
    relations = [free.gen(j) * order for j, order in enumerate(into.orders) if order]
    relations += [free(vector(ZZ, difference.row(i))) for i in range(difference.nrows())]
    engine = free / free.span(relations)
    apex = _group_from_engine(engine)
    _quotient_covers[apex] = (free, engine)
    apex_form = presentation(apex)
    rows = [vector(ZZ, apex_form.coordinates(engine(free.gen(j)))) for j in range(into.rank())]
    return _linear_homomorphism(target, apex, LinearForm(into, apex_form, _matrix_of_rows(rows, apex_form.rank())))


def coequalizer_mediator(
    projection: MorphismCategory.ObjectType,
    coequalizing: MorphismCategory.ObjectType,
) -> MorphismCategory.ObjectType:
    """The one homomorphism ``h`` out of a quotient with ``h ∘ q = k``, for a ``k`` that kills the same subgroup.

    A Smith generator of the quotient goes along its lift to the free cover and then
    through ``k``, which is well defined exactly because ``k`` vanishes on the relations
    the quotient adjoined.
    """
    apex = projection.codomain()
    assert apex in _quotient_covers, f"{apex!r} is not a quotient this leaf constructed"
    assert coequalizing.domain() is projection.domain(), f"{coequalizing!r} does not start at {projection.domain()!r}"
    free, engine = _quotient_covers[apex]
    target = coequalizing.codomain()
    matrix, into = linear_form(coequalizing).matrix, presentation(target)
    rows = [vector(ZZ, generator.lift()) * matrix for generator in engine.smith_form_gens()]
    assert all(
        into.element(tuple(int(c) for c in vector(ZZ, relation) * matrix)) == into.zero_datum()
        for relation in engine.W().gens()
    ), f"{coequalizing!r} does not vanish on the relations of {apex!r}, so it does not factor through it"
    return _linear_homomorphism(apex, target, LinearForm(presentation(apex), into, _matrix_of_rows(rows, into.rank())))


def _pair_generators(first: Presentation, second: Presentation) -> FGP_Module_class:
    """``Z^{nm} / (d_i e_{ij}, d'_j e_{ij})``: the presented tensor product in the pair generators."""
    n, m = first.rank(), second.rank()
    free = FreeModule(ZZ, n * m)
    relations = [free.gen(i * m + j) * order for i, order in enumerate(first.orders) for j in range(m)]
    relations += [free.gen(i * m + j) * order for j, order in enumerate(second.orders) for i in range(n)]
    return free / free.span(relations)


def _pair_vector(data: _TensorData, a: Hashable, b: Hashable) -> Hashable:
    """``Σ a_i b_j e_{ij}`` as an element of the tensor engine: the image of ``(a, b)`` under the biadditive map."""
    left, right = presentation(data.first).coordinates(a), presentation(data.second).coordinates(b)
    m = len(right)
    return data.quotient(vector(ZZ, [left[i] * right[j] for i in range(len(left)) for j in range(m)]))


@cached_function(key=identity_key)
def _tensor_object(first: CategoryOfCategories.ElementType, second: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
    quotient = _pair_generators(presentation(first), presentation(second))
    assert quotient.is_finite(), f"the tensor of {first!r} and {second!r} is infinite; only finite tensor products are enumerated"
    result = _group_from_engine(quotient)
    _tensor_data[result] = _TensorData(first, second, quotient)
    return result


def bilinear_map(first: CategoryOfCategories.ElementType, second: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
    """The universal biadditive map ``U(A) × U(B) -> U(A ⊗ B)``, a morphism of ``Sets()``.

    It is a morphism of ``Sets()`` and not of ``Ab``: a biadditive map is not additive, and
    were this one a morphism of ``Ab`` the tensor product would be a coproduct.  Its
    universal property is what ``tensor_mediator`` factors through.
    """
    result = _tensor_object(first, second)
    data = _tensor_data[result]
    product = binary_product_data(Sets(), _points(first), _points(second)).apex()
    return Mor(Sets)(product, _points(result))(lambda pair: _pair_vector(data, pair[0], pair[1]))


def simple_tensor(
    first: CategoryOfCategories.ElementType,
    second: CategoryOfCategories.ElementType,
    left: Hashable,
    right: Hashable,
) -> CategoryOfCategories.ElementType:
    """``a ⊗ b``: the point of ``A ⊗ B`` that the universal biadditive map sends ``(a, b)`` to.

    That map lands in the carrier ``U(A ⊗ B)``, since it is a morphism of ``Sets()``, and a
    morphism out of ``A ⊗ B`` takes points of ``A ⊗ B``.  This crosses between the two
    through the object's own realization, so a consumer writes ``μ(a ⊗ b)`` rather than
    unwrapping the carrier point and rewrapping it in the tensor.
    """
    result = _tensor_object(first, second)
    universal = bilinear_map(first, second)
    return result.object_at(universal(universal.domain().point((left, right))))


def tensor_mediator(
    first: CategoryOfCategories.ElementType,
    second: CategoryOfCategories.ElementType,
    target: CategoryOfCategories.ElementType,
    biadditive: Callable[[Hashable, Hashable], Hashable],
) -> MorphismCategory.ObjectType:
    """The morphism ``A ⊗ B -> C`` of ``Ab`` through which a biadditive rule ``(a, b) ↦ f(a, b)`` on data factors.

    The class of ``e_{ij}`` goes to ``f(e_i, e_j)``; a Smith generator of the tensor is sent
    along its lift to the free module on the pairs, which is well defined because ``f``
    respects the relations.
    """
    result = _tensor_object(first, second)
    data = _tensor_data[result]
    left, right, into, form = presentation(first), presentation(second), presentation(target), presentation(result)
    m = right.rank()
    images = [[vector(ZZ, into.coordinates(biadditive(a, b))) for b in _generators(right)] for a in _generators(left)]
    rows = []
    for generator in data.quotient.smith_form_gens():
        row = vector(ZZ, [0] * into.rank())
        for position, coefficient in enumerate(generator.lift()):
            if coefficient:
                row += int(coefficient) * images[position // m][position % m]
        rows.append(row)
    return _linear_homomorphism(result, target, LinearForm(form, into, _matrix_of_rows(rows, into.rank())))


def _tensor_morphism(first: MorphismCategory.ObjectType, second: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
    """``f ⊗ g``: the mediator of ``(a, b) ↦ f(a) ⊗ g(b)``."""
    target = _tensor_object(first.codomain(), second.codomain())
    target_data = _tensor_data[target]
    return tensor_mediator(
        first.domain(),
        second.domain(),
        target,
        lambda a, b: _pair_vector(target_data, first(first.domain().point(a)).datum(), second(second.domain().point(b)).datum()),
    )


def _rebracket(triple: CategoryOfCategories.ElementType, forward: bool) -> MorphismCategory.ObjectType:
    """``(A ⊗ B) ⊗ C -> A ⊗ (B ⊗ C)`` and back, each the mediator of a biadditive rule written through lifts."""
    a, b, c = (triple.family_component(index) for index in range(3))
    ab, bc = _tensor_object(a, b), _tensor_object(b, c)
    ab_data, bc_data = _tensor_data[ab], _tensor_data[bc]
    generators_a, generators_b, generators_c = _generators(presentation(a)), _generators(presentation(b)), _generators(presentation(c))
    if forward:
        target = _tensor_object(a, bc)
        target_data, m = _tensor_data[target], presentation(b).rank()

        def rule(t: Hashable, x: Hashable) -> Hashable:
            total = target_data.quotient.zero()
            for position, coefficient in enumerate(t.lift()):
                if coefficient:
                    total = total + int(coefficient) * _pair_vector(target_data, generators_a[position // m], _pair_vector(bc_data, generators_b[position % m], x))
            return total

        return tensor_mediator(ab, c, target, rule)
    target = _tensor_object(ab, c)
    target_data, p = _tensor_data[target], presentation(c).rank()

    def rule_back(x: Hashable, t: Hashable) -> Hashable:
        total = target_data.quotient.zero()
        for position, coefficient in enumerate(t.lift()):
            if coefficient:
                total = total + int(coefficient) * _pair_vector(target_data, _pair_vector(ab_data, x, generators_b[position // p]), generators_c[position % p])
        return total

    return tensor_mediator(a, bc, target, rule_back)


@cached_function(key=lambda: 0)
def AbelianTensor() -> MonoidalStructuresCategory.ObjectType:
    """``(Ab, ⊗, Z)``: the tensor product of abelian groups as a selected monoidal structure on ``AbelianGroups()``."""
    base, unit = AbelianGroups(), integer_group()
    pairs = Cat().Products()((base, base))
    tensor = Fun(pairs, base)(
        lambda pair: _tensor_object(pair.family_component(0), pair.family_component(1)),
        lambda arrow: _tensor_morphism(arrow.family_component(0), arrow.family_component(1)),
    )
    left, right = tensor_parentheses(tensor)
    associator = natural_isomorphism(left, right, lambda triple: _rebracket(triple, True), lambda triple: _rebracket(triple, False))
    left_unit, right_unit = tensor_units(tensor, unit)
    identity = Fun(base, base).one()

    def scalar(group: CategoryOfCategories.ElementType, k: Hashable, a: Hashable) -> Hashable:
        into = presentation(group)
        return into.element(tuple(int(k) * coordinate for coordinate in into.coordinates(a)))

    left_unitor = natural_isomorphism(
        left_unit,
        identity,
        lambda group: tensor_mediator(unit, group, group, lambda k, a: scalar(group, k, a)),
        lambda group: abelian_homomorphism(group, _tensor_object(unit, group), lambda a: _pair_vector(_tensor_data[_tensor_object(unit, group)], 1, a)),
    )
    right_unitor = natural_isomorphism(
        right_unit,
        identity,
        lambda group: tensor_mediator(group, unit, group, lambda a, k: scalar(group, k, a)),
        lambda group: abelian_homomorphism(group, _tensor_object(group, unit), lambda a: _pair_vector(_tensor_data[_tensor_object(group, unit)], a, 1)),
    )
    return MonoidalStructures(base)(tensor, unit, associator, left_unitor, right_unitor)
