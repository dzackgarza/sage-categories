"""Native handles never replace owned object, construction, or endpoint identity."""

from sage.groups.additive_abelian.additive_abelian_group import AdditiveAbelianGroup

from sage_categories.algebra._presented_modules_cap import (
    presented_native_object,
    retain_presented_native_object,
)
from sage_categories.algebra._commutative_rings_oscar import (
    oscar_native_morphism,
    oscar_native_object,
    retain_oscar_native_morphism,
    retain_oscar_native_object,
)
from sage_categories.algebra.abelian import AbelianGroups, presented_abelian_group
from sage_categories.cat.calculus import binary_product_data
from sage_categories.cat.cones import cone, limit_cones, vertex_of
from sage_categories.cat.diagrams import from_sequence
from sage_categories.cat.morphisms import Mor
from sage_categories.cat.monoidal import Cartesian
from sage_categories.cat.native import (
    native_universal_presentation,
    retain_native_universal_presentation,
)
from sage_categories.cat.structured_objects import Rings
from sage_categories.sets._finite_cap import (
    finite_native_morphism,
    finite_native_object,
    retain_finite_native_morphism,
    retain_finite_native_object,
)
from sage_categories.sets.finite import Sets


def test_native_reconstruction() -> None:
    shared_native_set = object()
    left = Sets(("a", "b"))
    right = Sets((7, 9))
    left_record = retain_finite_native_object(left, shared_native_set, ("a", "b"))
    right_record = retain_finite_native_object(right, shared_native_set, (7, 9))
    assert left_record.native is right_record.native
    assert left_record.value is left and right_record.value is right
    assert left_record.value is not right_record.value
    assert finite_native_object(left) is left_record
    assert left_record.construction.data == ("a", "b")
    assert right_record.construction.data == (7, 9)

    shared_native_map = object()
    left_identity = Mor(Sets)(left, left).one()
    right_identity = Mor(Sets)(right, right).one()
    retain_finite_native_morphism(left_identity, shared_native_map)
    retain_finite_native_morphism(right_identity, shared_native_map)
    assert finite_native_morphism(left_identity).source is left
    assert finite_native_morphism(left_identity).target is left
    assert finite_native_morphism(right_identity).source is right
    assert finite_native_morphism(right_identity).target is right

    shared_native_module = object()
    first_engine = AdditiveAbelianGroup([4])
    second_engine = AdditiveAbelianGroup([4])
    first = presented_abelian_group(first_engine)
    second = presented_abelian_group(second_engine)
    first_record = retain_presented_native_object(first, shared_native_module, first_engine)
    second_record = retain_presented_native_object(second, shared_native_module, second_engine)
    assert first_record.native is second_record.native
    assert first_record.owner is AbelianGroups() and second_record.owner is AbelianGroups()
    assert first_record.value is first and second_record.value is second
    assert first_record.value is not second_record.value

    assert presented_native_object(first).construction.data is first_engine
    assert presented_native_object(second).construction.data is second_engine

    # OSCAR may use one native presentation for several isomorphic rings; owned identity and
    # construction remain distinct, and a retained map keeps its exact ring endpoints.
    rings = Rings(Sets)
    structure = Cartesian(Sets)

    def residue_ring(modulus):
        carrier = Sets(tuple(range(modulus)))
        square = binary_product_data(Sets, carrier, carrier).apex()
        addition = Mor(Sets)(square, carrier)(lambda pair: (pair[0] + pair[1]) % modulus)
        multiplication = Mor(Sets)(square, carrier)(lambda pair: (pair[0] * pair[1]) % modulus)
        zero = Mor(Sets)(structure.unit(), carrier)(lambda _: 0)
        one = Mor(Sets)(structure.unit(), carrier)(lambda _: 1)
        return rings(addition, zero, multiplication, one)

    first_ring, second_ring = residue_ring(2), residue_ring(3)
    shared_native_ring = object()
    first_ring_record = retain_oscar_native_object(first_ring, shared_native_ring, ("residue", 2))
    second_ring_record = retain_oscar_native_object(second_ring, shared_native_ring, ("residue", 3))
    assert first_ring_record.native is second_ring_record.native
    assert first_ring_record.value is first_ring and second_ring_record.value is second_ring
    assert first_ring_record.value is not second_ring_record.value
    assert oscar_native_object(first_ring).construction.data == ("residue", 2)
    assert oscar_native_object(second_ring).construction.data == ("residue", 3)

    first_identity = Mor(rings)(first_ring, first_ring).one()
    second_identity = Mor(rings)(second_ring, second_ring).one()
    shared_native_ring_map = object()
    retain_oscar_native_morphism(first_identity, shared_native_ring_map)
    retain_oscar_native_morphism(second_identity, shared_native_ring_map)
    assert oscar_native_morphism(first_identity).source is first_ring
    assert oscar_native_morphism(first_identity).target is first_ring
    assert oscar_native_morphism(second_identity).source is second_ring
    assert oscar_native_morphism(second_identity).target is second_ring

    # A native apex may underlie several selected universal presentations.  Selection is by
    # the owned presentation, not by that apex or by its native handle.
    product_presentation = binary_product_data(Sets, left, right)
    shared_apex = product_presentation.apex()
    singleton_diagram = from_sequence(Sets, (shared_apex,))
    singleton_vertex = vertex_of(singleton_diagram.domain(), 0)
    singleton_identity = Mor(Sets)(shared_apex, shared_apex).one()
    singleton_presentation = limit_cones(singleton_diagram).with_universal_data(
        cone(singleton_diagram, shared_apex, lambda _: singleton_identity),
        lambda candidate: candidate.leg(singleton_vertex),
    )
    assert singleton_presentation is not product_presentation
    assert singleton_presentation.apex() is product_presentation.apex()

    shared_native_apex = object()
    product_vertices = tuple(vertex_of(product_presentation.diagram().domain(), index) for index in (0, 1))
    first_native = retain_native_universal_presentation(
        Sets,
        product_presentation.diagram(),
        product_presentation,
        object(),
        tuple((vertex, object()) for vertex in product_vertices),
        (),
        object(),
        shared_native_apex,
        tuple((vertex, object()) for vertex in product_vertices),
        lambda candidate: ("product-factor", candidate),
    )
    second_native = retain_native_universal_presentation(
        Sets,
        singleton_diagram,
        singleton_presentation,
        object(),
        ((singleton_vertex, object()),),
        (),
        object(),
        shared_native_apex,
        ((singleton_vertex, object()),),
        lambda candidate: ("singleton-factor", candidate),
    )
    assert first_native.native_apex is second_native.native_apex
    assert native_universal_presentation(product_presentation).diagram is product_presentation.diagram()
    assert native_universal_presentation(singleton_presentation).diagram is singleton_diagram
    assert native_universal_presentation(product_presentation).presentation is product_presentation
    assert native_universal_presentation(singleton_presentation).presentation is singleton_presentation
    assert first_native.mediator("candidate") == ("product-factor", "candidate")
    assert second_native.mediator("candidate") == ("singleton-factor", "candidate")


test_native_reconstruction()
