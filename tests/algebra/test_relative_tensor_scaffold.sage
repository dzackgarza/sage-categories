"""The tensor product over M_2(F_2): rows tensor columns is F_2, its mediator, and the induced outer actions."""

from sage_categories.all import ask
from sage_categories.algebra import (
    AbelianTensor,
    abelian_homomorphism,
    balanced_tensor,
    induced_left_action,
    induced_right_action,
    integer_group,
    presented_abelian_group,
    relative_tensor,
    relative_tensor_mediator,
    simple_tensor,
    tensor_mediator,
)
from sage_categories.cat.modules import Modules
from sage_categories.cat.monoidal import Reversed, SelfAction
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


def test_rows_tensor_columns_over_the_matrix_ring_is_the_field() -> None:
    entries, element, group, regular, ring, opposite = matrix_ring()
    row_engine, rows, row_of = plane()
    column_engine, columns, column_of = plane()

    # X = F_2^(1x2) is a right module by v |-> v A; Y = F_2^(2x1) is a left module by w |-> A w.
    def act_on_rows(v, a):
        u, x = [int(c) for c in v.vector()], entries(a)
        return row_of([u[0] * x[0] + u[1] * x[2], u[0] * x[1] + u[1] * x[3]])

    def act_on_columns(a, w):
        x, u = entries(a), [int(c) for c in w.vector()]
        return column_of([x[0] * u[0] + x[1] * u[1], x[2] * u[0] + x[3] * u[1]])

    right_action = tensor_mediator(rows, group, rows, act_on_rows)
    left_action = tensor_mediator(group, columns, columns, act_on_columns)
    right_modules = Modules(opposite, SelfAction(Reversed(AbelianTensor())))
    left_modules = Modules(ring, SelfAction(AbelianTensor()))
    row_module, column_module = right_modules(right_action), left_modules(left_action)
    assert row_module in right_modules and column_module in left_modules
    assert right_modules.forgetful().on_object(row_module) is rows
    assert left_modules.forgetful().on_object(column_module) is columns

    balanced = relative_tensor(right_action, left_action)
    assert balanced.domain() is not balanced.codomain()

    e1, e2 = row_of([1, 0]), row_of([0, 1])
    f1, f2 = column_of([1, 0]), column_of([0, 1])
    over_the_ring = lambda v, w: balanced_tensor(balanced, v, w)
    quotient = balanced.codomain()

    # The relative tensor is F_2: e1 (x) f1 generates it, e1 (x) f2 dies, and doubling kills it.
    assert ask(over_the_ring(e1, f1) == quotient.zero()) is False
    assert ask(over_the_ring(e1, f2) == quotient.zero()) is True
    assert ask(over_the_ring(e1, f1) + over_the_ring(e1, f1) == quotient.zero()) is True
    # E12 moves the two basis vectors across the tensor sign: e1 E12 = e2 and E12 f2 = f1.
    assert ask(over_the_ring(e2, f2) == over_the_ring(e1, f1)) is True
    # Over the integers e1 (x) f1 and e2 (x) f2 stay apart, so the middle ring did the work.
    unbalanced = balanced.domain()
    assert ask(simple_tensor(rows, columns, e1, f1) == simple_tensor(rows, columns, e2, f2)) is False
    assert unbalanced is simple_tensor(rows, columns, e1, f1).parent()


def test_the_dot_product_factors_through_the_balanced_map() -> None:
    entries, element, group, regular, ring, opposite = matrix_ring()
    row_engine, rows, row_of = plane()
    column_engine, columns, column_of = plane()
    field_engine = AdditiveAbelianGroup([2])
    field = presented_abelian_group(field_engine)

    def act_on_rows(v, a):
        u, x = [int(c) for c in v.vector()], entries(a)
        return row_of([u[0] * x[0] + u[1] * x[2], u[0] * x[1] + u[1] * x[3]])

    def act_on_columns(a, w):
        x, u = entries(a), [int(c) for c in w.vector()]
        return column_of([x[0] * u[0] + x[1] * u[1], x[2] * u[0] + x[3] * u[1]])

    balanced = relative_tensor(
        tensor_mediator(rows, group, rows, act_on_rows),
        tensor_mediator(group, columns, columns, act_on_columns),
    )

    def dot(v, w):
        """``v w``: the product of a row and a column, which is balanced because ``(vA)w = v(Aw)``."""
        u, t = [int(c) for c in v.vector()], [int(c) for c in w.vector()]
        return field_engine.linear_combination_of_smith_form_gens(vector(ZZ, [u[0] * t[0] + u[1] * t[1]]))

    mediator = relative_tensor_mediator(balanced, field, dot)
    assert mediator.domain() is balanced.codomain() and mediator.codomain() is field
    e1, e2 = row_of([1, 0]), row_of([0, 1])
    f1, f2 = column_of([1, 0]), column_of([0, 1])
    one = field_engine.gen(0)
    assert ask(mediator(balanced_tensor(balanced, e1, f1)) == field.point(one)) is True
    assert ask(mediator(balanced_tensor(balanced, e2, f2)) == field.point(one)) is True
    assert ask(mediator(balanced_tensor(balanced, e1, f2)) == field.zero()) is True
    # The factorization is the one the coequalizer promises: it agrees with the dot product
    # on the whole tensor over the integers, not only on these simple tensors.
    assert ask(mediator * balanced == tensor_mediator(rows, columns, field, dot)) is True


def test_the_outer_actions_survive_the_balancing() -> None:
    entries, element, group, regular, ring, opposite = matrix_ring()
    column_engine, columns, column_of = plane()
    identity = element([1, 0, 0, 1])

    def act_on_columns(a, w):
        x, u = entries(a), [int(c) for c in w.vector()]
        return column_of([x[0] * u[0] + x[1] * u[1], x[2] * u[0] + x[3] * u[1]])

    # S (x)_S Y is Y, and the left action of S on the first factor descends to it.
    left_on_columns = tensor_mediator(group, columns, columns, act_on_columns)
    balanced = relative_tensor(regular, left_on_columns)
    outer = induced_left_action(balanced, regular)
    quotient = balanced.codomain()
    assert outer.codomain() is quotient

    f1, f2 = column_of([1, 0]), column_of([0, 1])
    e12 = element([0, 1, 0, 0])
    scale = lambda a, t: outer(simple_tensor(group, quotient, a, t.datum()))
    unit_tensor = lambda w: balanced_tensor(balanced, identity, w)

    # E12 f2 = f1 and E12 f1 = 0, and the outer action moves the tensors the same way.
    assert ask(scale(e12, unit_tensor(f2)) == unit_tensor(f1)) is True
    assert ask(scale(e12, unit_tensor(f1)) == quotient.zero()) is True
    assert ask(unit_tensor(f1) == quotient.zero()) is False
    assert ask(scale(identity, unit_tensor(f2)) == unit_tensor(f2)) is True
    # Acting first and balancing second gives the same point, which is what descending means.
    assert ask(scale(e12, unit_tensor(f2)) == balanced_tensor(balanced, e12, f2)) is True


def test_the_induced_right_action_is_the_right_action_of_the_first_factor() -> None:
    entries, element, group, regular, ring, opposite = matrix_ring()
    row_engine, rows, row_of = plane()
    identity = element([1, 0, 0, 1])

    def act_on_rows(v, a):
        u, x = [int(c) for c in v.vector()], entries(a)
        return row_of([u[0] * x[0] + u[1] * x[2], u[0] * x[1] + u[1] * x[3]])

    # X (x)_S S is X, and the right action of S on the second factor descends to it.
    right_on_rows = tensor_mediator(rows, group, rows, act_on_rows)
    balanced = relative_tensor(right_on_rows, regular)
    outer = induced_right_action(balanced, regular)
    quotient = balanced.codomain()
    assert outer.codomain() is quotient

    e1, e2 = row_of([1, 0]), row_of([0, 1])
    e12 = element([0, 1, 0, 0])
    scale = lambda t, a: outer(simple_tensor(quotient, group, t.datum(), a))
    unit_tensor = lambda v: balanced_tensor(balanced, v, identity)

    # e1 E12 = e2 and e2 E12 = 0, and the outer action moves the tensors the same way.
    assert ask(scale(unit_tensor(e1), e12) == unit_tensor(e2)) is True
    assert ask(scale(unit_tensor(e2), e12) == quotient.zero()) is True
    assert ask(unit_tensor(e1) == unit_tensor(e2)) is False
    assert ask(scale(unit_tensor(e1), identity) == unit_tensor(e1)) is True
    assert ask(scale(unit_tensor(e1), e12) == balanced_tensor(balanced, e1, e12)) is True


test_rows_tensor_columns_over_the_matrix_ring_is_the_field()
test_the_dot_product_factors_through_the_balanced_map()
test_the_outer_actions_survive_the_balancing()
test_the_induced_right_action_is_the_right_action_of_the_first_factor()
