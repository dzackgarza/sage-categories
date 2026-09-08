"""Owned ``Mor`` values retain homotopy-core cells without changing public identity."""

from sage_categories.all import Mor, Sets
from sage_categories.engines import cells


def test_owned_morphism_cells() -> None:
    X = Sets((0, 1))
    Y = Sets((2, 3))
    Z = Sets((4, 5))
    f = Mor(Sets)(X, Y)(lambda n: n + 2)
    g = Mor(Sets)(Y, Z)(lambda n: n + 2)
    composite = g * f
    identity = Mor(Sets)(X, X).one()

    native_x = cells.native_object(Sets, X)
    native_f = cells.native_cell(Sets, f)
    native_g = cells.native_cell(Sets, g)
    native_composite = cells.native_cell(Sets, composite)
    native_identity = cells.native_cell(Sets, identity)

    assert native_x.dimension() == 0
    assert native_f.dimension() == native_g.dimension() == 1
    assert native_composite.dimension() == native_identity.dimension() == 1
    assert native_f.source().same_as(native_x)
    assert native_f.target().same_as(cells.native_object(Sets, Y))
    assert native_g.source().same_as(cells.native_object(Sets, Y))
    assert native_composite.source().same_as(native_x)
    assert native_composite.target().same_as(cells.native_object(Sets, Z))
    assert native_identity.source().same_as(native_x)
    assert native_identity.target().same_as(native_x)
    cells.typecheck(Sets, composite)


def test_native_signature_respects_invertibility_classification() -> None:
    import sage_categories_homotopy as homotopy

    signature = homotopy.Signature()
    source = signature.add_object()
    middle = signature.add_object()
    target = signature.add_object()
    directed = signature.add_generator(source, middle, invertibility="directed")
    invertible = signature.add_generator(middle, target, invertibility="invertible")

    signature.typecheck(directed, True)
    try:
        signature.typecheck(directed.inverse(), True)
    except ValueError as error:
        assert "directed generator" in str(error)
    else:
        raise AssertionError("a directed generator's inverse unexpectedly typechecked")
    signature.typecheck(invertible.inverse(), True)

    identity = directed.identity()
    signature.typecheck(identity, True)
    assert identity.boundary("source", 0).same_as(directed)
    assert identity.boundary("target", 0).same_as(directed)

    try:
        invertible.attach(directed, "target", [])
    except ValueError as error:
        assert "invalid attachment" in str(error)
    else:
        raise AssertionError("an incompatible native attachment unexpectedly succeeded")


test_owned_morphism_cells()
test_native_signature_respects_invertibility_classification()
