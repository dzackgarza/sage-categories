"""The horizontal operations of the strict 2-category ``Cat()``, and the exponential as a functor in its base.

``Cat()`` owns vertical composition of natural transformations, the two whiskerings, and
horizontal composition.  The exponential ``D ** I = Fun(I, D)`` is a functor in ``D``:
``Fun(I, F)`` post-composes with ``F``.

Oracles, all inspected 2026-08-27:

- nLab "whiskering", Examples: "whiskering ``H`` and ``eta`` yields the natural
  transformation ``H . eta: (H . F) -> (H . G)`` whose coordinate at ``A`` is
  ``H(eta_A)``", and "whiskering ``eta`` and ``F`` yields the natural transformation
  ``eta . F: (G . F) -> (H . F)`` whose coordinate at ``A`` is ``eta_{F(A)}``";
- Mathlib ``NatTrans.hcomp``, ``Mathlib/CategoryTheory/Functor/Category.lean:122-131``:
  ``app := fun X => β.app (F.obj X) ≫ I.map (α.app X)``, with ``hcomp_app'`` giving the
  other build ``H.map (α.app X) ≫ β.app (G.obj X)``;
- Mathlib ``CategoryTheory.whiskeringRight``,
  ``Mathlib/CategoryTheory/Whiskering.lean:95-98``: ``obj H := { obj := fun F => F ⋙ H,
  map := fun α => whiskerRight α H }``.

Naturality, the interchange law, and the exponential's universal property are trusted
declarations (POL-MATH-036, POL-MATH-037, POL-MATH-041).  Each test below witnesses one
construction on one specimen; none of them proves a law.
"""

from sage_categories.all import *


def test_the_two_whiskerings_have_their_stated_endpoints_and_components() -> None:
    """``K . eta`` and ``theta . F`` on one specimen: their endpoints are the composites and their components the stated ones.

    Naturality of each result is a trusted declaration (POL-MATH-036); this specimen
    witnesses the two constructions and proves no law.
    """
    arrow, point = Cat().Simplex(int(1)), Cat().Terminal()
    two, three, four = Sets().Simplex(int(1)), Sets().Simplex(int(2)), Sets().Simplex(int(3))
    successor_below = Mor(Sets())(two, three)(lambda datum: datum + int(1))
    successor_above = Mor(Sets())(three, four)(lambda datum: datum + int(1))
    below, above = successor_below.defining_morphism(), successor_above.defining_morphism()
    generator = arrow.generator("0->1")

    source, target = Fun(point, arrow).constant(arrow(int(0))), Fun(point, arrow).constant(arrow(int(1)))
    eta = Mor(Fun(point, arrow))(source, target)(lambda vertex: generator)

    left = Cat().whisker_left(above, eta)
    assert left in Mor(Fun(point, Sets()))
    assert left.source_functor().on_object(point(int(0))) is three
    assert left.target_functor().on_object(point(int(0))) is four
    assert left.component(point(int(0))) is above.on_morphism(generator)
    assert left.component(point(int(0))) is successor_above

    # ``theta: below => above`` is a commuting square of ``Sets()``: both routes send
    # ``n`` to ``n + 2``.  Its endpoints are the two morphisms spelled as the objects of
    # ``Fun([1], Sets())`` they are.
    square_below = Mor(Sets())(two, three)(lambda datum: datum + int(1))
    square_above = Mor(Sets())(three, four)(lambda datum: datum + int(1))
    theta = Mor(Fun(arrow, Sets()))(successor_below, successor_above)(
        lambda vertex: square_below if vertex is arrow(int(0)) else square_above
    )

    right = Cat().whisker_right(theta, source)
    assert right in Mor(Fun(point, Sets()))
    assert right.source_functor().on_object(point(int(0))) is two
    assert right.target_functor().on_object(point(int(0))) is three
    assert right.component(point(int(0))) is theta.component(source.on_object(point(int(0))))
    assert right.component(point(int(0))) is square_below


def test_the_horizontal_composite_has_the_component_its_two_whiskerings_give() -> None:
    """``theta * eta: H F => K G`` on one specimen, in both of the builds interchange identifies.

    The interchange law is a trusted declaration (POL-MATH-036).  This specimen witnesses
    the constructed component against two independent formulas here; it proves no law.
    """
    arrow, point = Cat().Simplex(int(1)), Cat().Terminal()
    two, three, four = Sets().Simplex(int(1)), Sets().Simplex(int(2)), Sets().Simplex(int(3))
    successor_below = Mor(Sets())(two, three)(lambda datum: datum + int(1))
    successor_above = Mor(Sets())(three, four)(lambda datum: datum + int(1))
    below, above = successor_below.defining_morphism(), successor_above.defining_morphism()
    generator = arrow.generator("0->1")

    source, target = Fun(point, arrow).constant(arrow(int(0))), Fun(point, arrow).constant(arrow(int(1)))
    eta = Mor(Fun(point, arrow))(source, target)(lambda vertex: generator)
    square_below = Mor(Sets())(two, three)(lambda datum: datum + int(1))
    square_above = Mor(Sets())(three, four)(lambda datum: datum + int(1))
    theta = Mor(Fun(arrow, Sets()))(successor_below, successor_above)(
        lambda vertex: square_below if vertex is arrow(int(0)) else square_above
    )

    composite = Cat().horizontal_composite(theta, eta)
    assert composite in Mor(Fun(point, Sets()))
    assert composite.source_functor().on_object(point(int(0))) is two
    assert composite.target_functor().on_object(point(int(0))) is four

    component = composite.component(point(int(0)))
    assert component in Mor(Sets())(two, four)
    assert ask(component == Mor(Sets())(two, four)(lambda datum: datum + int(2))) is True
    # ``K(eta_X) . theta_{F(X)}`` and ``theta_{G(X)} . H(eta_X)``.
    assert ask(component == above.on_morphism(generator) * theta.component(arrow(int(0)))) is True
    assert ask(component == theta.component(arrow(int(1))) * below.on_morphism(generator)) is True


def test_the_exponential_acts_on_a_morphism_of_cat_and_keeps_one_value_per_morphism() -> None:
    """``Fun(I, U)`` for the underlying-set functor ``U: Posets() -> Sets()``: post-composition with ``U``.

    Its object action keeps the spelling of a point of ``Posets()`` at stage ``I``, so a
    monotone map has one image whether it is read as a morphism of ``Posets()`` or as an
    object of ``Fun([1], Posets())``.  The exponential's universal property is a trusted
    declaration (POL-MATH-041) and is not proved here.
    """
    arrow, point = Cat().Simplex(int(1)), Cat().Terminal()
    underlying = Posets().structure_functors()[int(0)]
    chain, pair = Posets().Simplex(int(2)), Posets().Simplex(int(1))
    three, two = Sets().Simplex(int(2)), Sets().Simplex(int(1))
    collapse = Mor(Posets())(chain, pair)(lambda datum: min(datum, int(1)))
    include = Mor(Posets())(pair, chain)(lambda datum: datum)

    action = Fun(arrow, underlying)
    assert action in Fun(Fun(arrow, Posets()), Fun(arrow, Sets()))
    assert action.domain() is Fun(arrow, Posets())
    assert action.codomain() is Fun(arrow, Sets())
    assert action is Fun(arrow, underlying)

    assert action.on_object(collapse) is underlying.on_morphism(collapse)
    assert action.on_object(collapse) in Mor(Sets())(three, two)

    # On an object of ``Fun(I, Posets())`` that is a functor rather than a point, the same
    # action is the composite ``U . G``.
    constant = Fun(point, Posets()).constant(chain)
    assert Fun(point, underlying).on_object(constant).on_object(point(int(0))) is underlying.on_object(chain)
    assert underlying.on_object(chain) is three

    # ``collapse . include = 1_pair``, so ``(include, collapse)`` is a commuting square
    # from ``include`` to ``collapse``; its image is the square of underlying set maps.
    square = Mor(Fun(arrow, Posets()))(include, collapse)(
        lambda vertex: include if vertex is arrow(int(0)) else collapse
    )
    whiskered = action.on_morphism(square)
    assert whiskered in Mor(Fun(arrow, Sets()))
    assert whiskered.domain() is action.on_object(include)
    assert whiskered.codomain() is action.on_object(collapse)
    assert whiskered.component(arrow(int(0))) is underlying.on_morphism(include)
    assert whiskered.component(arrow(int(1))) is underlying.on_morphism(collapse)
