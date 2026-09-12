"""A supplied nonstrict associator is interpreted semantically, not normalized away."""

from __future__ import annotations

from fractions import Fraction

from sage_categories.all import Category, Cat, Fun, Mor, ask
from sage_categories.cat.calculus import natural_isomorphism
from sage_categories.cat.monoidal import (
    MonoidalStructures,
    tensor_morphism,
    tensor_parentheses,
    tensor_units,
)
from sage_categories.cat.category import is_placed
from sage_categories.cat.predicates import Proposition, register_handler
from sage_categories.engines import cells


class RationalLine(Category):
    """The one-object category of one-dimensional rational linear maps."""

    class ObjectType:
        def __init__(self, name: str) -> None:
            self._name = name

    class ElementType:
        pass

    class MorphismType:
        def __init__(self, data: object) -> None:
            self._written_scalar = Fraction(data) if data is not None else None

        def scalar(self) -> Fraction:
            if self._written_scalar is not None:
                return self._written_scalar
            if self.is_composite():
                first, second = self.factors()
                return second.scalar() * first.scalar()
            return Fraction(1)

    def __call__(self, name: str) -> RationalLine.ObjectType:
        return self.ObjectType(name)

    def _equal_objects(
        self,
        first: RationalLine.ObjectType,
        second: RationalLine.ObjectType,
        assumptions: Proposition,
    ) -> bool:
        return first is second

    def _equal_morphisms(
        self,
        first: RationalLine.MorphismType,
        second: RationalLine.MorphismType,
        assumptions: Proposition,
    ) -> bool:
        return (
            first.domain() is second.domain()
            and first.codomain() is second.codomain()
            and first.scalar() == second.scalar()
        )


def test_scaled_associator_pentagon_retains_eight_versus_four() -> None:
    category = RationalLine()
    register_handler(category.equality(), category._equal_objects)
    register_handler(category.equality(), category._equal_morphisms)
    line = category("Q")
    pairs = Cat().Products()((category, category))
    tensor = Fun(pairs, category)(
        lambda pair: line,
        lambda arrow: category.construct_morphism(
            line,
            line,
            arrow.family_component(0).scalar() * arrow.family_component(1).scalar(),
        ),
    )
    left, right = tensor_parentheses(tensor)
    triples = left.domain()
    associator = natural_isomorphism(
        left,
        right,
        lambda triple: category.construct_morphism(line, line, 2),
        lambda triple: category.construct_morphism(line, line, Fraction(1, 2)),
    )
    left_unit, right_unit = tensor_units(tensor, line)
    identity = Fun(category, category).one()
    left_unitor = natural_isomorphism(
        left_unit,
        identity,
        lambda value: category.construct_morphism(line, line, 1),
        lambda value: category.construct_morphism(line, line, 1),
    )
    right_unitor = natural_isomorphism(
        right_unit,
        identity,
        lambda value: category.construct_morphism(line, line, 1),
        lambda value: category.construct_morphism(line, line, 1),
    )
    structure = MonoidalStructures(category)(
        tensor,
        line,
        associator,
        left_unitor,
        right_unitor,
    )

    # The public diagram interpretation uses this supplied associator rather than
    # silently strictifying tensor words.  The right box has a two-wire formal source,
    # so tensoring it with the left box crosses the comparison
    # E((Q),(Q,Q)) -> E(Q) tensor E(Q,Q), whose semantic value is this associator.
    identity_arrow = category.construct_morphism(line, line, 1)
    left_box = structure.diagram_box("left", (line,), (line,), identity_arrow)
    right_box = structure.diagram_box("right", (line, line), (line,), identity_arrow)
    interpreted_tensor = structure.interpret(left_box @ right_box)
    assert interpreted_tensor.scalar() == 2

    # A formal box carrying an ordinary noninvertible arrow remains that exact arrow
    # after interpretation.  Native syntax does not manufacture an inverse for it.
    zero = category.construct_morphism(line, line, 0)
    interpreted_zero = structure.interpret(
        structure.diagram_box("zero", (line,), (line,), zero)
    )
    assert interpreted_zero is zero
    assert not is_placed(interpreted_zero, Mor(category).Isomorphisms())
    native_zero = cells.native_cell(category, interpreted_zero)
    cells.typecheck(category, interpreted_zero)
    try:
        cells.native_signature(category).typecheck(native_zero.inverse(), True)
    except ValueError as error:
        assert "directed generator" in str(error)
    else:
        raise AssertionError("a noninvertible interpreted arrow acquired a native inverse")

    native_associator = cells.native_cell(category, associator.component(triples((line, line, line))))
    cells.native_signature(category).typecheck(native_associator.inverse(), True)

    def component(x, y, z):
        return associator.component(triples((x, y, z)))
    xy = tensor.on_object(pairs((line, line)))
    yz = tensor.on_object(pairs((line, line)))
    first = tensor_morphism(tensor, component(line, line, line), Mor(category)(line, line).one())
    middle = component(line, xy, line)
    last = tensor_morphism(tensor, Mor(category)(line, line).one(), component(line, line, line))
    long = last * middle * first
    short = component(line, line, yz) * component(xy, line, line)

    assert long.scalar() == 8
    assert short.scalar() == 4
    assert ask(structure.pentagon(line, line, line, line)) is False


test_scaled_associator_pentagon_retains_eight_versus_four()
