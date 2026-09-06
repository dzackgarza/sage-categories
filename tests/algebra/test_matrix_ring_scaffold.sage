"""M_2(F_2) as a noncommutative monoid object of (Ab, tensor, Z), and its standard left module F_2^2."""

from sage_categories.all import Mor, SelfAction, ask
from sage_categories.algebra import AbelianTensor, abelian_homomorphism, integer_group, presented_abelian_group, simple_tensor, tensor_mediator
from sage_categories.cat.modules import Modules
from sage_categories.cat.structured_objects import Monoids


def matrix_ring():
    """``M_2(F_2)``: the additive group ``(Z/2)^4`` in the entry order ``(a11, a12, a21, a22)`` with the matrix product."""
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
    one = element([1, 0, 0, 1])
    ring = Monoids(AbelianTensor())(
        tensor_mediator(group, group, group, multiply),
        abelian_homomorphism(integer_group(), group, lambda k: k * one),
    )
    return engine, element, group, ring


def test_matrix_ring_is_a_noncommutative_monoid_object() -> None:
    engine, element, group, ring = matrix_ring()
    assert ring in Monoids(AbelianTensor())
    e12, e21 = element([0, 1, 0, 0]), element([0, 0, 1, 0])

    def multiply(a, b):
        """``a b``: the ring's multiplication applied to the simple tensor ``a (x) b``."""
        return ring.operation()(simple_tensor(group, group, a, b))

    # E12 E21 = E11 while E21 E12 = E22, so the ring is not commutative.
    assert ask(multiply(e12, e21) == group.point(element([1, 0, 0, 0]))) is True
    assert ask(multiply(e21, e12) == group.point(element([0, 0, 0, 1]))) is True
    assert ask(group.point(e12) == group.point(e21)) is False
    assert ask(multiply(e12, e21) == multiply(e21, e12)) is False
    # The unit is the identity matrix, and E12 is nilpotent.
    assert ask(multiply(element([1, 0, 0, 1]), e12) == group.point(e12)) is True
    assert ask(multiply(e12, e12) == group.zero()) is True


def test_standard_module_has_e12_acting_on_the_second_basis_vector() -> None:
    engine, element, group, ring = matrix_ring()
    plane_engine = AdditiveAbelianGroup([2, 2])
    plane = presented_abelian_group(plane_engine)
    vector_of = lambda values: plane_engine.linear_combination_of_smith_form_gens(vector(ZZ, values))

    def act(a, v):
        x, w = [int(c) for c in a.vector()], [int(c) for c in v.vector()]
        return vector_of([x[0] * w[0] + x[1] * w[1], x[2] * w[0] + x[3] * w[1]])

    modules = Modules(ring, SelfAction(AbelianTensor()))
    standard = modules(tensor_mediator(group, plane, plane, act))
    assert standard in modules
    assert modules.forgetful().on_object(standard) is plane

    def scale(a, v):
        """``a v``: the module action applied to the simple tensor ``a (x) v``."""
        return standard.action()(simple_tensor(group, plane, a, v))

    e1, e2 = vector_of([1, 0]), vector_of([0, 1])
    # E12 carries the second basis vector to the first and the first to zero.
    assert ask(scale(element([0, 1, 0, 0]), e2) == plane.point(e1)) is True
    assert ask(scale(element([0, 1, 0, 0]), e1) == plane.zero()) is True
    assert ask(scale(element([1, 0, 0, 1]), e2) == plane.point(e2)) is True
    # The scalar, the vector, and the result keep their distinct parents.
    assert group.point(element([0, 1, 0, 0])).parent() is group
    assert standard.point(e2).parent() is standard
    assert scale(element([0, 1, 0, 0]), e2).parent() is plane


test_matrix_ring_is_a_noncommutative_monoid_object()
test_standard_module_has_e12_acting_on_the_second_basis_vector()
