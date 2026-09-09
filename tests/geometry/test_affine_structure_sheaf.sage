"""Affine principal opens use OSCAR's actual structure-sheaf restriction data."""

from sage_categories.algebra import polynomial_ring, prime_field
from sage_categories.all import ask
from sage_categories.geometry import Spec, affine_structure_sheaf


def test_principal_open_retains_localization_and_restriction() -> None:
    field = prime_field(5)
    polynomial, (t,) = polynomial_ring(field, ("t",))
    scheme = Spec.on_object(polynomial)
    opens, sheaf = affine_structure_sheaf(scheme)

    root = opens.root()
    principal = opens.principal_open(root, t)
    assert root.section_ring() is polynomial
    assert sheaf.section_ring(root) is polynomial
    assert sheaf.section_ring(principal) is principal.section_ring()

    restriction = sheaf.restriction(root, principal)
    assert restriction.domain() is polynomial
    assert restriction.codomain() is principal.section_ring()
    localized_t = restriction(t)

    second = opens.principal_open(principal, localized_t)
    second_restriction = sheaf.restriction(principal, second)
    composite = sheaf.restriction(root, second)
    assert composite.domain() is polynomial
    assert composite.codomain() is second.section_ring()
    assert composite is not restriction
    assert second_restriction.domain() is principal.section_ring()
    assert second_restriction.codomain() is second.section_ring()
    assert ask(second_restriction * restriction == composite) is True


test_principal_open_retains_localization_and_restriction()
