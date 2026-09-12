from sage.all import PolynomialRing, ZZ

from sage_categories.engines.presented_modules import kernel_presentation


def test_cap_kernel_presentation_over_integer_polynomial_ring_keeps_the_actual_kernel_map() -> None:
    ring = PolynomialRing(ZZ, "x")
    x = ring.gen()
    kernel = kernel_presentation(
        variable_names=("x",),
        owned_ring=ring,
        source_rank=2,
        target_rank=1,
        source_relation_rows=(),
        target_relation_rows=(),
        morphism_rows=((x,), (ring.one(),)),
    )

    inclusion = kernel.inclusion_rows()
    assert len(inclusion) == 1
    first, second = inclusion[0]
    assert first * x + second == 0
    assert kernel.relation_rows() == ()

    lifted = kernel.lift_row((ring.one(), -x))
    assert len(lifted) == 1
    assert lifted[0] * first == ring.one()
    assert lifted[0] * second == -x
