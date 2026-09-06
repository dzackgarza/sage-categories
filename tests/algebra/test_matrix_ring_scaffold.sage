"""M_2(F_2) as a noncommutative monoid object of (Ab, tensor, Z), and its standard left module F_2^2."""

from sage_categories.all import Mor, SelfAction, ask
from sage_categories.algebra import AbelianGroups, AbelianTensor, abelian_homomorphism, bilinear_map, integer_group, presented_abelian_group, tensor_mediator
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
    bilinear = bilinear_map(group, group)
    pairs = bilinear.domain()
    square = ring.operation().domain()

    def multiply_points(a, b):
        return ring.operation()(square.point(bilinear(pairs.point((a, b))).datum())).datum()

    # E12 E21 = E11 and E21 E12 = E22, so the multiplication is not commutative.
    assert multiply_points(e12, e21) == element([1, 0, 0, 0])
    assert multiply_points(e21, e12) == element([0, 0, 0, 1])
    # Two matrix units are distinct points of the ring, and the two products they form are
    # distinct points, which is noncommutativity decided through the ring's own equality.
    assert ask(group.point(e12) == group.point(e21)) is False
    assert ask(group.point(multiply_points(e12, e21)) == group.point(multiply_points(e21, e12))) is False
    # The unit is the identity matrix, and E12 is nilpotent.
    assert multiply_points(element([1, 0, 0, 1]), e12) == e12
    assert multiply_points(e12, e12) == group.zero().datum()


def test_standard_module_has_e12_acting_on_the_second_basis_vector() -> None:
    engine, element, group, ring = matrix_ring()
    plane_engine = AdditiveAbelianGroup([2, 2])
    plane = presented_abelian_group(plane_engine)
    coordinates = lambda datum: [int(c) for c in datum.vector()]
    vector_of = lambda values: plane_engine.linear_combination_of_smith_form_gens(vector(ZZ, values))

    def act(a, v):
        x, w = [int(c) for c in a.vector()], coordinates(v)
        return vector_of([x[0] * w[0] + x[1] * w[1], x[2] * w[0] + x[3] * w[1]])

    modules = Modules(ring, SelfAction(AbelianTensor()))
    standard = modules(tensor_mediator(group, plane, plane, act))
    assert standard in modules
    assert modules.forgetful().on_object(standard) is plane

    acted = standard.action().domain()
    scalars = bilinear_map(group, plane)

    def scale(a, v):
        return standard.action()(acted.point(scalars(scalars.domain().point((a, v))).datum())).datum()

    e1, e2 = vector_of([1, 0]), vector_of([0, 1])
    # E12 sends the second basis vector to the first and the first to zero.
    assert scale(element([0, 1, 0, 0]), e2) == e1
    assert scale(element([0, 1, 0, 0]), e1) == plane.zero().datum()
    assert scale(element([1, 0, 0, 1]), e2) == e2
    # The scalar, the vector, and the result keep their distinct parents.
    assert group.point(element([0, 1, 0, 0])).parent() is group
    assert standard.point(e2).parent() is standard
    assert standard.action()(acted.point(scalars(scalars.domain().point((element([0, 1, 0, 0]), e2))).datum())).parent() is plane


test_matrix_ring_is_a_noncommutative_monoid_object()
test_standard_module_has_e12_acting_on_the_second_basis_vector()
