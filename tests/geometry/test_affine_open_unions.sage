"""Finite unions of principal affine opens retain genuine section rings and inclusions."""

from sage_categories.algebra import polynomial_ring, prime_field
from sage_categories.all import Mor
from sage_categories.geometry.affine import Spec, affine_structure_sheaf


def test_two_principal_open_union_is_one_represented_open() -> None:
    field = prime_field(5)
    ring, (x, y) = polynomial_ring(field, ("x", "y"))
    scheme = Spec.on_object(ring)
    opens, sheaf = affine_structure_sheaf(scheme)
    root = opens.root()
    dx = opens.principal_open(root, x)
    dy = opens.principal_open(root, y)
    punctured_plane = opens.finite_union((dx, dy))

    assert punctured_plane.covering_pieces() == (dx, dy)
    assert punctured_plane.scheme() is scheme
    assert sheaf.section_ring(punctured_plane) is punctured_plane.section_ring()
    dx_in_union = Mor(opens)(dx, punctured_plane)()
    dy_in_union = Mor(opens)(dy, punctured_plane)()
    union_in_root = Mor(opens)(punctured_plane, root)()
    assert dx_in_union.domain() is dx and dx_in_union.codomain() is punctured_plane
    assert dy_in_union.domain() is dy and dy_in_union.codomain() is punctured_plane
    assert union_in_root.domain() is punctured_plane and union_in_root.codomain() is root

    root_to_union = punctured_plane.restriction_to(root)
    union_to_dx = dx.restriction_to(punctured_plane)
    union_to_dy = dy.restriction_to(punctured_plane)
    assert root_to_union.domain() is ring
    assert root_to_union.codomain() is punctured_plane.section_ring()
    assert union_to_dx.domain() is punctured_plane.section_ring()
    assert union_to_dx.codomain() is dx.section_ring()
    assert union_to_dy.domain() is punctured_plane.section_ring()
    assert union_to_dy.codomain() is dy.section_ring()

    intersection_equations = opens.principal_open(root, x * y)
    assert opens._admits_morphism(intersection_equations, punctured_plane) is True
    through_union = intersection_equations.restriction_to(punctured_plane)
    assert through_union.domain() is punctured_plane.section_ring()
    assert through_union.codomain() is intersection_equations.section_ring()


test_two_principal_open_union_is_one_represented_open()
