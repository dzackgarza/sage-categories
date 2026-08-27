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

The file also carries the specimens for two further declared surfaces that no test
exercised: the represented underlying functor ``U_C = Mor(C)(G_C, -)`` of a category with a
separator, and the inherited execution of a receiver-valued declaration.  Toy
categories for the latter live only in this file (POL-TEST-006).
"""

from dataclasses import dataclass
from typing import Self

from sage_categories.all import *
from sage_categories.kernel.construction import retained_morphism_input, retained_object_input
from sage_categories.kernel.roles import MorphismOfCategory, ObjectOfCategory


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

    Its object action keeps the spelling of a point of ``Posets()`` with domain ``I``, so a
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

    # With domain ``1`` the points are the objects, including one refined into a property
    # subcategory: ``chain`` is placed in ``FinitePosets()``, which is contained in
    # ``Posets()``, so it is a diagram of shape ``1`` in ``Posets()``.
    assert chain in FinitePosets()
    assert chain in Fun(point, Posets())
    assert Fun(point, underlying).on_object(chain) is underlying.on_object(chain)
    assert Fun(point, underlying).on_object(chain) is three

    # On an object of ``Fun(I, Posets())`` that is a functor rather than a point, the same
    # action is the composite ``U . G``.
    constant = Fun(point, Posets()).constant(chain)
    assert Fun(point, underlying).on_object(constant).on_object(point(int(0))) is underlying.on_object(chain)

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


@dataclass(eq=False, slots=True)
class AnchorData:
    """The carrier set of an anchored object."""

    carrier: object


class Anchored(Category):
    """Objects named by a carrier set, with one receiver-valued declaration.

    ``this_object`` is the declaration ``D18`` describes: its body is ``return self``, so
    executing it on a descendant instance returns that descendant.
    """

    class DeclaredObjectType(ObjectOfCategory):
        def __init__(self, data):
            self._anchor_data = data
            super().__init__()

        def carrier(self) -> ObjectOfCategory:
            return self._anchor_data.carrier

        def this_object(self) -> Self:
            return self

    def __call__(self, carrier):
        return self.ObjectType(self, AnchorData(carrier))

    def __repr__(self):
        return "Anchored"


@dataclass(eq=False, slots=True)
class LabelData:
    """The anchored object a labelled object is built on."""

    anchored: object


@dataclass(frozen=True, eq=False, slots=True)
class LabelMapData:
    """The anchored morphism a labelled morphism is built on."""

    underlying: object


class Labelled(Category):
    """Objects built on a chosen anchored object, related to it by a non-inclusion faithful functor.

    The functor is not an inclusion, so the image of a labelled object is a different
    object and an inherited result transported to the image would be visible.
    """

    class DeclaredObjectType(ObjectOfCategory):
        def __init__(self, data):
            self._label_data = data
            super().__init__()

        def anchored_object(self) -> ObjectOfCategory:
            return self._label_data.anchored

    class DeclaredMorphismType(MorphismOfCategory):
        def __init__(self, data):
            self._label_map_data = data
            super().__init__()

        def underlying_morphism(self) -> MorphismOfCategory:
            return self._label_map_data.underlying

    def __init__(self, anchored):
        self._anchored = anchored
        self._selected = {}
        super().__init__()

    def structure_functors(self):
        if "forgetful" not in self._selected:
            forgetful = Fun(self, self._anchored).Faithful()(
                lambda member: member.anchored_object(),
                lambda morphism: morphism.underlying_morphism(),
            )
            forgetful.retain_object_constructor_conversion(lambda source: retained_object_input(source.datum.anchored))
            forgetful.retain_morphism_constructor_conversion(lambda source: retained_morphism_input(source.datum.underlying))
            self._selected["forgetful"] = forgetful
        return (self._selected["forgetful"],)

    def __call__(self, anchored):
        return self.ObjectType(self, LabelData(anchored))

    def __repr__(self):
        return "Labelled"


def test_an_inherited_receiver_valued_method_returns_the_descendant() -> None:
    """``X.f() := F(X).f()`` for a declaration whose body is ``return self`` returns ``X``, not ``F(X)``.

    Every ancestor initializer stores its typed state on the descendant instance, so the
    inherited method executes there (D18, POL-KERNEL-028).  This witnesses that on one
    specimen through a selected functor that is not an inclusion, so the image is a
    distinct object and a transported result would be visible.
    """
    anchored = Anchored()
    labelled = Labelled(anchored)
    carrier = Sets().Finite()((int(3), int(4)))
    member = labelled(anchored(carrier))
    image = labelled.structure_functors()[int(0)].on_object(member)

    assert member in labelled
    assert member not in anchored
    assert image in anchored
    assert image is not member

    assert member.this_object() is member
    assert image.this_object() is image
    assert member.carrier() is carrier


def test_the_chosen_separator_represents_the_underlying_set_functor() -> None:
    """``U_C = Mor(C)(G_C, -): C -> Sets()`` for ``C = Posets()``, whose separator is the one-point order.

    The value at ``X`` is the set of morphisms ``G_C -> X`` and the value at ``f`` is
    postcomposition.  Faithfulness of ``U_C`` follows from the writer's assertion that the
    separating family separates and is a trusted declaration (POL-MATH-037); this specimen
    witnesses the construction and proves no such property.
    """
    underlying_points = Posets().represented_functor()
    (separator,) = Posets().separating_family()
    chain, pair = Posets().Simplex(int(2)), Posets().Simplex(int(1))
    collapse = Mor(Posets())(chain, pair)(lambda datum: min(datum, int(1)))

    assert underlying_points in Fun(Posets(), Sets())
    assert underlying_points.domain() is Posets()
    assert underlying_points.codomain() is Sets()

    top = Mor(Posets())(separator, chain)(lambda datum: int(2))
    assert underlying_points.on_object(chain) in Sets()
    assert underlying_points.on_object(chain).point(top) in underlying_points.on_object(chain)
    assert ask(underlying_points.on_object(chain).membership_proposition(collapse)) is False

    image = collapse * top
    assert image in Mor(Posets())(separator, pair)
    postcomposition = underlying_points.on_morphism(collapse)
    assert postcomposition in Mor(Sets())(underlying_points.on_object(chain), underlying_points.on_object(pair))
    assert ask(postcomposition(underlying_points.on_object(chain).point(top)) == underlying_points.on_object(pair).point(image)) is True

    identity = underlying_points.on_morphism(chain.identity())
    assert ask(identity(underlying_points.on_object(chain).point(top)) == underlying_points.on_object(chain).point(chain.identity() * top)) is True
