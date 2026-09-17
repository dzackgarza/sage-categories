"""The projective line is glued from two affine charts and its swap uses the gluing mediator."""

from sage_categories.algebra import inverse_unit, prime_field
from sage_categories.all import Mor, ask
from sage_categories.geometry import AffineSchemes, Schemes, affine_structure_sheaf, projective_line
from sage_categories.geometry.schemes import FiniteAffineGluing, native_scheme, native_scheme_morphism


def test_projective_line_two_chart_gluing_and_swap() -> None:
    field = prime_field(5)
    presentation = projective_line(field)
    schemes = Schemes()
    construction = presentation.scheme.finite_affine_gluing()
    assert isinstance(construction, FiniteAffineGluing)
    assert construction.charts == (presentation.left_chart, presentation.right_chart)
    overlap = construction.overlap(0, 1)
    assert len(overlap.pieces) == 1
    assert overlap.pieces[0].left_open is presentation.left_open
    assert overlap.pieces[0].right_open is presentation.right_open
    assert presentation.scheme in schemes
    assert presentation.structure_sheaf is presentation.scheme.sheaf()

    left_scheme = schemes.affine(presentation.left_chart)
    right_scheme = schemes.affine(presentation.right_chart)
    assert presentation.left_inclusion.domain() is left_scheme
    assert presentation.right_inclusion.domain() is right_scheme
    assert presentation.left_inclusion.codomain() is presentation.scheme
    assert presentation.right_inclusion.codomain() is presentation.scheme
    assert presentation.chart_swap.domain() is presentation.scheme
    assert presentation.chart_swap.codomain() is presentation.scheme
    identity = Mor(schemes)(presentation.scheme, presentation.scheme).one()
    assert ask(presentation.chart_swap * presentation.chart_swap == identity) is True
    assert native_scheme(presentation.scheme).construction is construction
    for arrow, source in (
        (presentation.left_inclusion, left_scheme),
        (presentation.right_inclusion, right_scheme),
    ):
        native = native_scheme_morphism(arrow)
        assert native.value is arrow
        assert native.source is source
        assert native.target is presentation.scheme
    native_swap = native_scheme_morphism(presentation.chart_swap)
    assert native_swap.value is presentation.chart_swap
    assert native_swap.source is presentation.scheme
    assert native_swap.target is presentation.scheme

    left_entry, right_entry = presentation.scheme.affine_cover()
    assert left_entry.open_immersion is presentation.left_inclusion
    assert right_entry.open_immersion is presentation.right_inclusion
    left_opens, left_sheaf = affine_structure_sheaf(presentation.left_chart)
    right_opens, right_sheaf = affine_structure_sheaf(presentation.right_chart)
    left_root, right_root = left_opens.root(), right_opens.root()
    sheaf = presentation.structure_sheaf.presheaf
    left_global, right_global = presentation.left_scheme_open, presentation.right_scheme_open
    overlap_global = presentation.overlap_scheme_open
    left_comparison = left_entry.structure_sheaf_comparison.component(left_root)
    right_comparison = right_entry.structure_sheaf_comparison.component(right_root)
    overlap_comparison = left_entry.structure_sheaf_comparison.component(presentation.left_open)
    assert left_comparison.domain() is sheaf.section_ring(left_global)
    assert left_comparison.codomain() is left_sheaf.section_ring(left_root)
    assert right_comparison.domain() is sheaf.section_ring(right_global)
    assert right_comparison.codomain() is right_sheaf.section_ring(right_root)
    assert overlap_comparison.domain() is sheaf.section_ring(overlap_global)
    assert overlap_comparison.codomain() is presentation.left_open.section_ring()
    left_restriction = (
        overlap_comparison * sheaf.restriction(left_global, overlap_global)
        * left_comparison.inverse()
    )
    right_restriction = (
        overlap_comparison * sheaf.restriction(right_global, overlap_global)
        * right_comparison.inverse()
    )
    assert left_restriction.domain() is presentation.left_chart.coordinate_ring()
    assert right_restriction.domain() is presentation.right_chart.coordinate_ring()
    assert left_restriction.codomain() is presentation.left_open.section_ring()
    assert right_restriction.codomain() is presentation.left_open.section_ring()

    localized_t = left_restriction(presentation.left_coordinate)
    assert ask(localized_t == presentation.left_open.restriction_to(left_root)(presentation.left_coordinate)) is True
    assert ask(right_restriction(presentation.right_coordinate) == inverse_unit(localized_t)) is True
    assert ask(presentation.overlap_swap(localized_t) == inverse_unit(localized_t)) is True

    swap = presentation.chart_swap
    assert swap.inverse() is swap
    assert ask(swap.inverse() * swap == identity) is True
    assert ask(swap * swap.inverse() == identity) is True

    def chart_point(chart, inclusion, generator, scalar):
        point = AffineSchemes().spectrum_point(chart, (generator - scalar,))
        carrier = schemes.affine(chart).underlying_points()
        return inclusion.continuous_map().underlying_map()(carrier.point(point))

    t, u = presentation.left_coordinate, presentation.right_coordinate
    left_ring, right_ring = t.parent(), u.parent()
    zero = chart_point(presentation.left_chart, presentation.left_inclusion, t, left_ring.zero())
    infinity = chart_point(presentation.right_chart, presentation.right_inclusion, u, right_ring.zero())
    two = left_ring.one() + left_ring.one()
    three = two + left_ring.one()
    point_two = chart_point(presentation.left_chart, presentation.left_inclusion, t, two)
    point_three = chart_point(presentation.left_chart, presentation.left_inclusion, t, three)
    underlying = swap.continuous_map().underlying_map()
    assert ask(zero == infinity) is False
    for source, target in ((zero, infinity), (infinity, zero), (point_two, point_three), (point_three, point_two)):
        assert ask(underlying(source) == target) is True
        assert ask(underlying(underlying(source)) == source) is True

    # Evaluate the two sheaf actions before using the retained inverse equation.
    inverse_image = swap.continuous_map().inverse_image()
    for global_open, comparison, coordinate in (
        (left_global, left_comparison, t),
        (right_global, right_comparison, u),
        (overlap_global, overlap_comparison, localized_t),
    ):
        middle_open = inverse_image.on_object(global_open)
        round_trip_open = inverse_image.on_object(middle_open)
        first_pullback = swap.sheaf_map().component(global_open)
        second_pullback = swap.sheaf_map().component(middle_open)
        section = comparison.inverse()(coordinate)
        round_trip = second_pullback(first_pullback(section))
        comparison_back = sheaf.restriction(round_trip_open, global_open)
        assert ask(comparison_back(round_trip) == section) is True

    structure = presentation.structure_map
    assert structure.domain() is presentation.scheme
    assert structure.codomain() is presentation.base
    assert ask(structure * swap == structure) is True
    base_chart = presentation.base.affine_cover()[0].affine
    assert base_chart.coordinate_ring() is field
    base_root = affine_structure_sheaf(base_chart)[0].root()
    whole = structure.continuous_map().inverse_image().on_object(base_root)
    coefficient_map = structure.sheaf_map().component(base_root)
    assert coefficient_map.domain() is field
    assert coefficient_map.codomain() is sheaf.section_ring(whole)
    constant = coefficient_map(field.one() + field.one())
    for chart, inclusion in (
        (presentation.left_chart, presentation.left_inclusion),
        (presentation.right_chart, presentation.right_inclusion),
    ):
        local_constant = inclusion.sheaf_map().component(whole)(constant)
        ring = chart.coordinate_ring()
        assert ask(local_constant == ring.one() + ring.one()) is True
    over = presentation.over_base
    slice_category = schemes.SliceOver(presentation.base)
    assert over in slice_category
    assert slice_category.defining_arrow_of(over) is structure
    assert slice_category.fixed_projection().on_object(over) is presentation.scheme
    over_swap = presentation.swap_over_base
    assert over_swap in Mor(slice_category)(over, over)
    assert slice_category.fixed_projection().on_morphism(over_swap) is swap
    assert over_swap.inverse() is over_swap
    over_identity = Mor(slice_category)(over, over).one()
    assert ask(over_swap.inverse() * over_swap == over_identity) is True
    assert ask(over_swap * over_swap.inverse() == over_identity) is True


test_projective_line_two_chart_gluing_and_swap()
