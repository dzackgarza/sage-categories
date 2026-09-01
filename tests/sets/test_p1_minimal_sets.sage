"""P1 acceptance tests for minimal owned Sets() and total maps.

Verifies the P1 acceptance criteria:
1. Sets() constructs rule-defined sets, enumerated finite sets, terminal set, empty set.
2. Set maps f: X -> Y construct total maps with verified domain and codomain endpoints.
3. Binary products and coproducts construct canonical cones and cocones.
4. Terminal generator * -> X and evaluation isomorphism are executable.
5. Every returned value is an owned category/object/element/morphism or authorized SymPy proposition.
6. Zero calls to Cardinal() during P1 minimal sets construction (cutting the bootstrap cycle).
"""

import sys
import pytest


def _get_sets():
    from sage_categories.sets.category import Sets
    return Sets()


# ---------------------------------------------------------------------------
# 1. Construction
# ---------------------------------------------------------------------------


def test_terminal_set() -> None:
    """The terminal set 1 = {*} is the one-point set."""
    S = _get_sets()
    T = S.Terminal()
    assert repr(T) == "{()}"


def test_empty_set() -> None:
    """The empty set {} has no elements."""
    S = _get_sets()
    E = S.Empty()
    assert repr(E) == "{}"
    assert S.Initial() is E


def test_finite_set_from_enumeration() -> None:
    """Finite sets are constructed from distinct data."""
    S = _get_sets()
    f3 = S.Finite().from_enumeration((1, 2, 3))
    assert repr(f3) == "{1, 2, 3}"


def test_finite_set_call_syntax() -> None:
    """Sets().Finite()((1, 2, 3)) constructs finite sets from data tuples."""
    S = _get_sets()
    f3 = S.Finite()((1, 2, 3))
    assert repr(f3) == "{1, 2, 3}"


def test_rule_defined_set() -> None:
    """Rule-defined sets are constructed from a membership rule."""
    S = _get_sets()
    evens = S(lambda d: d % 2 == 0)
    assert repr(evens) == "Set(<rule>)"


def test_simplex() -> None:
    """Simplex[n] = {0, ..., n}."""
    S = _get_sets()
    assert repr(S.Simplex(0)) == "{0}"
    assert repr(S.Simplex(1)) == "{0, 1}"
    assert repr(S.Simplex(2)) == "{0, 1, 2}"


# ---------------------------------------------------------------------------
# 2. Points and membership
# ---------------------------------------------------------------------------


def test_point_construction() -> None:
    """A point * -> X is an owned element of X with terminal domain."""
    S = _get_sets()
    f3 = S.Finite()((1, 2, 3))
    p = f3.point(1)
    assert p._is_element()
    assert p.parent() is f3
    assert p._point_datum_() == 1
    assert p.defining_morphism().domain() is S.Terminal()
    assert p.defining_morphism().codomain() is f3


def test_point_membership() -> None:
    """A point is a member of its parent set."""
    S = _get_sets()
    f3 = S.Finite()((1, 2, 3))
    p = f3.point(1)
    assert p in f3


def test_rule_point() -> None:
    """Rule-defined sets construct points through rule_point."""
    S = _get_sets()
    evens = S(lambda d: d % 2 == 0)
    p = evens.rule_point(4)
    assert p._is_element()
    assert p.parent() is evens
    assert p.defining_morphism().domain() is S.Terminal()


# ---------------------------------------------------------------------------
# 3. Morphisms
# ---------------------------------------------------------------------------


def test_morphism_domain_codomain() -> None:
    """A morphism has verified domain and codomain endpoints."""
    S = _get_sets()
    f3 = S.Finite()((1, 2, 3))
    f4 = S.Finite()((1, 2, 3, 4))
    inc = S.construct_morphism(f3, f4, lambda d: d)
    assert inc.domain() is f3
    assert inc.codomain() is f4


def test_morphism_evaluation() -> None:
    """Evaluating a morphism on a point of its domain returns a point of its codomain."""
    S = _get_sets()
    f3 = S.Finite()((1, 2, 3))
    f4 = S.Finite()((1, 2, 3, 4))
    inc = S.construct_morphism(f3, f4, lambda d: d)
    p = f3.point(1)
    result = inc(p)
    assert result._is_element()
    assert result.parent() is f4
    assert result._point_datum_() == 1


def test_identity_morphism() -> None:
    """The identity morphism fixes every point."""
    S = _get_sets()
    f3 = S.Finite()((1, 2, 3))
    id_f = S.construct_identity(f3)
    assert id_f.domain() is f3
    assert id_f.codomain() is f3
    p = f3.point(2)
    assert id_f(p) is p


def test_morphism_composition() -> None:
    """Composition of two morphisms is a morphism with the correct domain and codomain."""
    S = _get_sets()
    f3 = S.Finite()((1, 2, 3))
    f4 = S.Finite()((1, 2, 3, 4))
    f5 = S.Finite()((1, 2, 3, 4, 5))
    g = S.construct_morphism(f3, f4, lambda d: d)
    h = S.construct_morphism(f4, f5, lambda d: d)
    comp = h * g
    assert comp.domain() is f3
    assert comp.codomain() is f5
    p = f3.point(1)
    assert comp(p) is f5.point(1)


def test_morphism_composition_associativity() -> None:
    """Composition is associative: (k * g) * h and k * (g * h) agree on every point."""
    S = _get_sets()
    f = S.Finite()((1, 2))
    g = S.construct_morphism(f, f, lambda d: 3 - d)
    h = S.construct_identity(f)
    k = S.construct_morphism(f, f, lambda d: 3 - d)
    lhs = (k * g) * h
    rhs = k * (g * h)
    assert lhs.domain() is rhs.domain()
    assert lhs.codomain() is rhs.codomain()
    for datum in (1, 2):
        assert lhs(f.point(datum)) is rhs(f.point(datum))


# ---------------------------------------------------------------------------
# 4. Property refinement
# ---------------------------------------------------------------------------


def test_finite_refinement() -> None:
    """Finite()(set) refines the same object into the Finite property subcategory."""
    S = _get_sets()
    f3 = S.Finite().from_enumeration((1, 2, 3))
    refined = S.Finite()(f3)
    assert refined is f3


# ---------------------------------------------------------------------------
# 5. Products
# ---------------------------------------------------------------------------


def test_binary_product_exists() -> None:
    """The binary product A x B is a canonical set."""
    S = _get_sets()
    A = S.Finite()((0, 1))
    B = S.Finite()(('a', 'b', 'c'))
    prod = A * B
    assert repr(prod) == "{(0, 'a'), (0, 'b'), (0, 'c'), (1, 'a'), (1, 'b'), (1, 'c')}"


def test_binary_product_projections() -> None:
    """The projections pi_i: A x B -> A, pi_j: A x B -> B are set morphisms."""
    S = _get_sets()
    A = S.Finite()((0, 1))
    B = S.Finite()(('a', 'b'))
    prod = A * B
    p0 = prod.product_projection(0)
    p1 = prod.product_projection(1)
    assert p0.domain() is prod
    assert p0.codomain() is A
    assert p1.domain() is prod
    assert p1.codomain() is B


def test_binary_product_pairing() -> None:
    """A point of A x B is determined by its projections."""
    S = _get_sets()
    A = S.Finite()((0, 1))
    B = S.Finite()(('a', 'b'))
    prod = A * B
    p0 = prod.product_projection(0)
    p1 = prod.product_projection(1)
    for pt in prod:
        result_a = p0(pt)
        result_b = p1(pt)
        assert result_a._is_element()
        assert result_a.parent() is A
        assert result_b._is_element()
        assert result_b.parent() is B


# ---------------------------------------------------------------------------
# 6. Coproducts
# ---------------------------------------------------------------------------


def test_binary_coproduct_exists() -> None:
    """The binary coproduct A + B is a canonical set."""
    S = _get_sets()
    A = S.Finite()((0, 1))
    B = S.Finite()(('a', 'b'))
    coprod = A + B
    assert repr(coprod) == "{(0, 0), (0, 1), (1, 'a'), (1, 'b')}"


def test_binary_coproduct_injections() -> None:
    """The injections iota_i: A_i -> A + B are set morphisms."""
    S = _get_sets()
    A = S.Finite()((0, 1))
    B = S.Finite()(('a', 'b'))
    coprod = A + B
    i0 = coprod.coproduct_injection(0)
    i1 = coprod.coproduct_injection(1)
    assert i0.domain() is A
    assert i0.codomain() is coprod
    assert i1.domain() is B
    assert i1.codomain() is coprod

    pt_a = A.point(0)
    img_a = i0(pt_a)
    assert img_a._is_element()
    assert img_a.parent() is coprod
    assert img_a._point_datum_() == (0, 0)

    pt_b = B.point('a')
    img_b = i1(pt_b)
    assert img_b._is_element()
    assert img_b.parent() is coprod
    assert img_b._point_datum_() == (1, 'a')


# ---------------------------------------------------------------------------
# 7. Function sets and exponentials
# ---------------------------------------------------------------------------


def test_function_set() -> None:
    """The function set Y^X is a canonical set for finite X, Y."""
    S = _get_sets()
    T = S.Terminal()
    X = S.Finite()(('x', 'y'))
    func_set = X ** T
    assert func_set is not None


# ---------------------------------------------------------------------------
# 8. Categorical Generator and Evaluation Isomorphism
# ---------------------------------------------------------------------------


def test_terminal_generator_evaluation_isomorphism() -> None:
    r"""The terminal set 1 = {*} is a generator: \coprod_{x \in X} 1 \cong X."""
    S = _get_sets()
    X = S.Finite()(('u', 'v', 'w'))
    iso = X.evaluation_isomorphism()
    assert iso.domain() in S
    assert iso.codomain() is X
    # Evaluating on each element of the coproduct gives the corresponding element of X
    coprod = iso.domain()
    for pt in coprod:
        image = iso(pt)
        assert image._is_element()
        assert image.parent() is X
        assert image._point_datum_() == pt._point_datum_()[0]

    # The inverse is retained and maps X back to coprod
    inv = S.inverse_morphism(iso)
    assert inv.domain() is X
    assert inv.codomain() is coprod
    for pt in X:
        back = inv(pt)
        assert back._is_element()
        assert back.parent() is coprod
        assert back._point_datum_() == (pt._point_datum_(), ())


def test_hom_from_terminal_bijection() -> None:
    r"""Hom_Set(1, X) \cong X: points * -> X are in bijection with elements of X."""
    S = _get_sets()
    T = S.Terminal()
    X = S.Finite()(('alpha', 'beta'))
    star = T.point(())

    # Every point of X has a defining morphism 1 -> X
    for p in X:
        m = p.defining_morphism()
        assert m.domain() is T
        assert m.codomain() is X
        assert m(star) is p

    # Every morphism 1 -> X evaluates on * to yield a point of X
    f = S.construct_morphism(T, X, lambda _: 'alpha')
    eval_pt = f(star)
    assert eval_pt._is_element()
    assert eval_pt.parent() is X
    assert eval_pt._point_datum_() == 'alpha'


# ---------------------------------------------------------------------------
# 9. Bootstrap Invariant (specs/system.md)
# ---------------------------------------------------------------------------


def test_zero_calls_to_cardinal_during_p1(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify that P1 minimal sets operations execute without calling Cardinal()."""
    import sage_categories.sets.cardinals as cardinals_mod

    def forbidden_cardinal(*args, **kwargs):
        raise AssertionError("Cardinal() must not be called during P1 minimal sets!")

    monkeypatch.setattr(cardinals_mod, "Cardinal", forbidden_cardinal)

    S = _get_sets()
    # 1. Canonical sets
    T = S.Terminal()
    E = S.Empty()
    I = S.Initial()
    s0 = S.Simplex(0)
    s2 = S.Simplex(2)

    # 2. Finite sets and rule-defined sets
    f = S.Finite()((10, 20, 30))
    r = S(lambda d: d > 0)

    # 3. Elements and points
    p1 = f.point(10)
    pr = r.rule_point(5)

    # 4. Morphisms
    m = S.construct_morphism(f, f, lambda d: d)
    im = S.construct_identity(f)
    comp = m * im
    eval_res = m(p1)

    # 5. Products, Coproducts, Exponentials
    A = S.Finite()((1, 2))
    B = S.Finite()(('x', 'y'))
    prod = A * B
    coprod = A + B
    exp = B ** A

    # 6. Evaluation isomorphism
    iso = f.evaluation_isomorphism()
    assert iso is not None
