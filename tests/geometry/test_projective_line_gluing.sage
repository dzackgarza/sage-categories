"""The projective line is glued from two affine charts and its swap uses the gluing mediator."""

from sage_categories.algebra import inverse_unit, prime_field
from sage_categories.all import ask
from sage_categories.geometry import Schemes, TwoChartGluing, projective_line


def test_projective_line_two_chart_gluing_and_swap() -> None:
    presentation = projective_line(prime_field(5))
    schemes = Schemes()
    construction = presentation.scheme.construction()
    assert isinstance(construction, TwoChartGluing)
    assert construction.left is presentation.left_chart
    assert construction.right is presentation.right_chart
    assert construction.left_open is presentation.left_open
    assert construction.right_open is presentation.right_open

    left_scheme = schemes.affine(presentation.left_chart)
    right_scheme = schemes.affine(presentation.right_chart)
    assert presentation.left_inclusion.domain() is left_scheme
    assert presentation.right_inclusion.domain() is right_scheme
    assert presentation.left_inclusion.codomain() is presentation.scheme
    assert presentation.right_inclusion.codomain() is presentation.scheme
    assert presentation.chart_swap.domain() is presentation.scheme
    assert presentation.chart_swap.codomain() is presentation.scheme

    sheaf = presentation.structure_sheaf
    assert sheaf.section_ring("left") is presentation.left_chart.coordinate_ring()
    assert sheaf.section_ring("right") is presentation.right_chart.coordinate_ring()
    assert sheaf.section_ring("overlap") is presentation.left_open.section_ring()
    left_restriction = sheaf.restriction("left", "overlap")
    right_restriction = sheaf.restriction("right", "overlap")
    assert left_restriction.domain() is presentation.left_chart.coordinate_ring()
    assert right_restriction.domain() is presentation.right_chart.coordinate_ring()
    assert left_restriction.codomain() is presentation.left_open.section_ring()
    assert right_restriction.codomain() is presentation.left_open.section_ring()

    localized_t = left_restriction(presentation.left_coordinate)
    assert ask(presentation.overlap_swap(localized_t) == inverse_unit(localized_t)) is True


test_projective_line_two_chart_gluing_and_swap()
