"""Functoriality of the tensor product over M_2(F_2): a pair of module maps, and the two unit comparisons."""

from sage_categories.all import Mor, ask
from sage_categories.algebra import (
    AbelianGroups,
    AbelianTensor,
    abelian_homomorphism,
    balanced_tensor,
    integer_group,
    presented_abelian_group,
    relative_left_unitor,
    relative_right_unitor,
    relative_tensor,
    relative_tensor_morphism,
    tensor_mediator,
)
from sage_categories.cat.monoidal import Reversed
from sage_categories.cat.structured_objects import Monoids


def matrix_ring():
    """``M_2(F_2)`` on ``(Z/2)^4`` in the entry order ``(a11, a12, a21, a22)``."""
    engine = AdditiveAbelianGroup([2, 2, 2, 2])
    entries = lambda datum: [int(c) for c in datum.vector()]
    element = lambda values: engine.linear_combination_of_smith_form_gens(vector(ZZ, values))

    def multiply(a, b):
        x, y = entries(a), entries(b)
        return element([
            x[0] * y[0] + x[1] * y[2], x[0] * y[1] + x[1] * y[3],
            x[2] * y[0] + x[3] * y[2], x[2] * y[1] + x[3] * y[3],
        ])

    group = presented_abelian_group(engine)
    operation = tensor_mediator(group, group, group, multiply)
    unit = abelian_homomorphism(integer_group(), group, lambda k: k * element([1, 0, 0, 1]))
    return entries, element, group, operation, Monoids(AbelianTensor())(operation, unit), Monoids(Reversed(AbelianTensor()))(operation, unit)


def plane():
    """``F_2^2`` as an abelian group, used once as rows and once as columns."""
    engine = AdditiveAbelianGroup([2, 2])
    return engine, presented_abelian_group(engine), lambda values: engine.linear_combination_of_smith_form_gens(vector(ZZ, values))


def test_a_nonidentity_pair_of_module_maps_induces_a_map_of_relative_tensors() -> None:
    entries, element, group, regular, ring, opposite = matrix_ring()
    product = lambda a, b: element([
        entries(a)[0] * entries(b)[0] + entries(a)[1] * entries(b)[2],
        entries(a)[0] * entries(b)[1] + entries(a)[1] * entries(b)[3],
        entries(a)[2] * entries(b)[0] + entries(a)[3] * entries(b)[2],
        entries(a)[2] * entries(b)[1] + entries(a)[3] * entries(b)[3],
    ])
    balanced = relative_tensor(regular, regular)

    # Left multiplication is a map of right modules and right multiplication a map of
    # left modules, so this pair is one the relative tensor accepts; neither is the
    # identity, and they multiply on opposite sides of the tensor sign.
    e12, e21, e22 = element([0, 1, 0, 0]), element([0, 0, 1, 0]), element([0, 0, 0, 1])
    on_the_left = abelian_homomorphism(group, group, lambda a: product(e12, a))
    on_the_right = abelian_homomorphism(group, group, lambda a: product(a, e21))
    induced = relative_tensor_morphism(balanced, balanced, on_the_left, on_the_right)
    assert induced.domain() is balanced.codomain() and induced.codomain() is balanced.codomain()

    identity = element([1, 0, 0, 1])
    over_the_ring = lambda a, b: balanced_tensor(balanced, a, b)
    # 1 (x)_S E22 goes to E12 (x)_S (E22 E21) = E12 (x)_S E21, and E12 E21 = E11 is not zero.
    assert ask(induced(over_the_ring(identity, e22)) == over_the_ring(e12, e21)) is True
    assert ask(induced(over_the_ring(identity, e22)) == balanced.codomain().zero()) is False
    # E11 E21 = 0, so 1 (x)_S E11 dies and the induced map is not the identity.
    assert ask(induced(over_the_ring(identity, element([1, 0, 0, 0]))) == balanced.codomain().zero()) is True
    assert ask(over_the_ring(identity, element([1, 0, 0, 0])) == balanced.codomain().zero()) is False
    assert ask(induced == Mor(AbelianGroups())(balanced.codomain(), balanced.codomain()).one()) is False


def test_the_unit_comparisons_are_isomorphisms_with_executable_inverses() -> None:
    entries, element, group, regular, ring, opposite = matrix_ring()
    column_engine, columns, column_of = plane()
    row_engine, rows, row_of = plane()

    def act_on_columns(a, w):
        x, u = entries(a), [int(c) for c in w.vector()]
        return column_of([x[0] * u[0] + x[1] * u[1], x[2] * u[0] + x[3] * u[1]])

    def act_on_rows(v, a):
        u, x = [int(c) for c in v.vector()], entries(a)
        return row_of([u[0] * x[0] + u[1] * x[2], u[0] * x[1] + u[1] * x[3]])

    left_action = tensor_mediator(group, columns, columns, act_on_columns)
    right_action = tensor_mediator(rows, group, rows, act_on_rows)

    # S (x)_S Y is Y and X (x)_S S is X, through the actions themselves.
    into_columns, into_rows = relative_tensor(regular, left_action), relative_tensor(right_action, regular)
    left, back_to_columns = relative_left_unitor(into_columns, left_action, ring.unit_morphism())
    right, back_to_rows = relative_right_unitor(into_rows, right_action, ring.unit_morphism())
    assert left.domain() is into_columns.codomain() and left.codomain() is columns
    assert right.domain() is into_rows.codomain() and right.codomain() is rows

    # Both composites are identities, which is what makes each pair an isomorphism.
    for comparison, section, carrier in ((left, back_to_columns, columns), (right, back_to_rows, rows)):
        quotient = comparison.domain()
        assert ask(comparison * section == Mor(AbelianGroups())(carrier, carrier).one()) is True
        assert ask(section * comparison == Mor(AbelianGroups())(quotient, quotient).one()) is True

    f1, f2 = column_of([1, 0]), column_of([0, 1])
    e1, e2 = row_of([1, 0]), row_of([0, 1])
    identity, e12 = element([1, 0, 0, 1]), element([0, 1, 0, 0])
    # E12 (x)_S f2 goes to E12 f2 = f1, and the section sends f1 back to 1 (x)_S f1.
    assert ask(left(balanced_tensor(into_columns, e12, f2)) == columns.point(f1)) is True
    assert ask(back_to_columns(columns.point(f1)) == balanced_tensor(into_columns, identity, f1)) is True
    # e1 (x)_S E12 goes to e1 E12 = e2, and the section sends e2 back to e2 (x)_S 1.
    assert ask(right(balanced_tensor(into_rows, e1, e12)) == rows.point(e2)) is True
    assert ask(back_to_rows(rows.point(e2)) == balanced_tensor(into_rows, e2, identity)) is True


test_a_nonidentity_pair_of_module_maps_induces_a_map_of_relative_tensors()
test_the_unit_comparisons_are_isomorphisms_with_executable_inverses()
