"""Scheme points and base structure use the existing topological, Hom, and slice owners."""

from sage_categories.algebra import (
    integer_ring,
    polynomial_ring,
    presented_ring_homomorphism,
    prime_field,
)
from sage_categories.all import Mor
from sage_categories.geometry import AffineSchemes, Schemes, Spec


def test_scheme_point_domains_and_generic_base_slice() -> None:
    field = prime_field(5)
    polynomial, (t,) = polynomial_ring(field, ("t",))
    affine = Spec.on_object(polynomial)
    schemes = Schemes()
    scheme = schemes.affine(affine)

    underlying_points = scheme.underlying_points()
    assert underlying_points is scheme.space().carrier()
    spectrum_point = AffineSchemes().spectrum_point(affine, (t,))
    topological_point = underlying_points.point(spectrum_point)
    assert topological_point.datum() is spectrum_point

    field_scheme = schemes.affine(Spec.on_object(field))
    valued_points = scheme.valued_points(field)
    assert valued_points.domain() is field_scheme
    assert valued_points.codomain() is scheme
    evaluation = presented_ring_homomorphism(polynomial, field, (field.zero(),))
    field_valued_point = schemes.affine_morphism(Spec.on_morphism(evaluation.op()))
    assert field_valued_point in valued_points
    assert field_valued_point.domain() is field_scheme
    assert field_valued_point.codomain() is scheme

    integers = integer_ring()
    integer_scheme = schemes.affine(Spec.on_object(integers))
    categorical_points = scheme.categorical_points()
    assert categorical_points.domain() is integer_scheme
    assert categorical_points.codomain() is scheme
    assert scheme.categorical_points() is categorical_points

    structure_map = Mor(schemes)(scheme, scheme).one()
    over = scheme.over(scheme, structure_map)
    slice_category = schemes.SliceOver(scheme)
    assert over in slice_category
    assert slice_category.defining_arrow_of(over) is structure_map
    assert slice_category.varying_end(structure_map) is scheme
    slice_identity = Mor(slice_category)(over, over).one()
    assert slice_identity in Mor(slice_category)(over, over)


test_scheme_point_domains_and_generic_base_slice()
