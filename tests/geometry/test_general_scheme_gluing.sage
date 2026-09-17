"""Finite affine gluings retain multi-piece overlaps and locally ringed-space charts."""

from sage_categories.algebra import polynomial_ring, prime_field
from sage_categories.algebra.commutative_rings import (
    localization_extension,
    presented_ring_homomorphism,
)
from sage_categories.all import ask
from sage_categories.geometry.affine import (
    AffineSchemes,
    Spec,
    affine_structure_sheaf,
    affine_topological_space,
)
from sage_categories.geometry.schemes import (
    AffineOverlapPiece,
    Schemes,
    native_scheme,
)


def _coordinate_overlap(schemes, charts, generators, left, right):
    left_ring = charts[left].coordinate_ring()
    right_ring = charts[right].coordinate_ring()
    left_x, left_y = generators[left]
    right_x, right_y = generators[right]
    left_opens, _ = affine_structure_sheaf(charts[left])
    right_opens, _ = affine_structure_sheaf(charts[right])
    left_root, right_root = left_opens.root(), right_opens.root()
    left_dx = left_opens.principal_open(left_root, left_x)
    left_dy = left_opens.principal_open(left_root, left_y)
    right_dx = right_opens.principal_open(right_root, right_x)
    right_dy = right_opens.principal_open(right_root, right_y)

    right_to_left = presented_ring_homomorphism(
        right_ring,
        left_ring,
        (left_x, left_y),
    )
    left_to_right = presented_ring_homomorphism(
        left_ring,
        right_ring,
        (right_x, right_y),
    )

    def piece(left_open, right_open):
        right_to_left_local = localization_extension(
            right_open.section_ring(),
            left_open.section_ring(),
            left_open.restriction_to(left_root) * right_to_left,
        )
        left_to_right_local = localization_extension(
            left_open.section_ring(),
            right_open.section_ring(),
            right_open.restriction_to(right_root) * left_to_right,
        )
        return AffineOverlapPiece(
            left_open,
            right_open,
            right_to_left_local,
            left_to_right_local,
        )

    return schemes.affine_overlap(
        charts,
        left,
        right,
        (piece(left_dx, right_dx), piece(left_dy, right_dy)),
    )


def test_three_chart_gluing_uses_multi_affine_overlaps() -> None:
    field = prime_field(5)
    rings_and_generators = tuple(
        polynomial_ring(field, (f"x{index}", f"y{index}"))
        for index in range(3)
    )
    rings = tuple(item[0] for item in rings_and_generators)
    generators = tuple(item[1] for item in rings_and_generators)
    charts = tuple(Spec.on_object(ring) for ring in rings)
    schemes = Schemes()
    overlaps = (
        _coordinate_overlap(schemes, charts, generators, 0, 1),
        _coordinate_overlap(schemes, charts, generators, 0, 2),
        _coordinate_overlap(schemes, charts, generators, 1, 2),
    )

    glued = schemes.glue_affines(charts, overlaps)
    presentation = glued.finite_affine_gluing()
    assert presentation.charts == charts
    assert presentation.overlaps == overlaps
    assert all(len(overlap.left_open.covering_pieces()) == 2 for overlap in overlaps)
    assert all(len(overlap.right_open.covering_pieces()) == 2 for overlap in overlaps)

    cover = glued.affine_cover()
    assert len(cover) == 3
    assert tuple(chart.affine for chart in cover) == charts
    assert all(chart.open_immersion.codomain() is glued for chart in cover)
    assert native_scheme(glued).construction is presentation

    points = tuple(
        AffineSchemes().spectrum_point(
            chart,
            (coordinate_x - coordinate_x.parent().one(), coordinate_y),
        )
        for chart, (coordinate_x, coordinate_y) in zip(charts, generators, strict=True)
    )
    quotient_points = tuple(
        chart.open_immersion.continuous_map().underlying_map()(
            affine_topological_space(chart.affine).carrier().point(point)
        )
        for chart, point in zip(cover, points, strict=True)
    )
    assert ask(quotient_points[0] == quotient_points[1]) is True
    assert ask(quotient_points[1] == quotient_points[2]) is True
    assert glued.stalk(quotient_points[0]) is points[0].local_ring


test_three_chart_gluing_uses_multi_affine_overlaps()
