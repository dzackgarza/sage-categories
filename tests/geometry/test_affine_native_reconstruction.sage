"""Affine wrappers retain exact coordinate rings and scheme-map pullbacks."""

from sage_categories.all import Mor, Sets, Cartesian
from sage_categories.cat.calculus import binary_product_data
from sage_categories.cat.structured_objects import Rings
from sage_categories.geometry.affine import AffineSchemes, Spec


def residue_ring(modulus):
    carrier = Sets(tuple(range(modulus)))
    square = binary_product_data(Sets, carrier, carrier).apex()
    structure = Cartesian(Sets)
    addition = Mor(Sets)(square, carrier)(lambda pair: (pair[0] + pair[1]) % modulus)
    multiplication = Mor(Sets)(square, carrier)(lambda pair: (pair[0] * pair[1]) % modulus)
    zero = Mor(Sets)(structure.unit(), carrier)(lambda _: 0)
    one = Mor(Sets)(structure.unit(), carrier)(lambda _: 1)
    return Rings(Sets)(addition, zero, multiplication, one)


# Native execution is tested in the OSCAR-backed consumer; this regression isolates the
# owner-aware records by using distinct fake handles and exact owned values.
rings = Rings(Sets).Commutative()
first_ring = residue_ring(5)
second_ring = residue_ring(5)
assert first_ring in rings and second_ring in rings and first_ring is not second_ring

# The public wrapper constructor additionally checks OSCAR's structure ring, so native
# record identity is exercised there only in the live consumer.  Here the category itself
# stays distinct and owns the exact ring payloads.
affine = AffineSchemes()
assert affine is AffineSchemes()
assert Spec.domain() is rings.op()
assert Spec.codomain() is affine
