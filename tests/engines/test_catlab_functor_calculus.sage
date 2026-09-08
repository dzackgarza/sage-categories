"""Catlab executes functor and transformation composites over a nonfinite source."""

from __future__ import annotations

from sage_categories.all import Cat, Category, Fun, Mor
from sage_categories.cat.native import (
    has_native_functor,
    has_native_transformation,
)


class IntegerLabels(Category):
    """An unenumerated category with one owned object for every integer label."""

    class ObjectType:
        def __init__(self, label: int) -> None:
            self._label = label

        def label(self) -> int:
            return self._label

    class ElementType:
        pass

    class MorphismType:
        def __init__(self, label: str) -> None:
            self._label = label

        def label(self) -> str:
            return self._label

    def __call__(self, label: int) -> IntegerLabels.ObjectType:
        return self.ObjectType(label)


SOURCE = IntegerLabels()
MIDDLE = IntegerLabels()
TARGET = IntegerLabels()


def affine_functor(
    source: IntegerLabels,
    target: IntegerLabels,
    scale: int,
    shift: int,
) -> Cat().MorphismType:
    def on_object(value: IntegerLabels.ObjectType) -> IntegerLabels.ObjectType:
        return target(scale * value.label() + shift)

    def on_morphism(arrow: IntegerLabels.MorphismType) -> IntegerLabels.MorphismType:
        return Mor(target)(on_object(arrow.domain()), on_object(arrow.codomain()))(
            arrow.label()
        )

    return Fun(source, target)(on_object, on_morphism)


first = affine_functor(SOURCE, MIDDLE, 1, 1)
second = affine_functor(MIDDLE, TARGET, 2, 0)
composite = second * first

# No source-object enumeration exists.  Evaluation at an arbitrary object enters the
# Catlab CompositeFunctor and returns the exact owned reconstruction in TARGET.
value = SOURCE(10**6)
assert not has_native_functor(first)
assert composite.on_object(value).label() == 2 * (10**6 + 1)
assert has_native_functor(first)
assert has_native_functor(second)
assert has_native_functor(composite)

arrow = Mor(SOURCE)(SOURCE(-3), SOURCE(11))("f")
image = composite.on_morphism(arrow)
assert image.domain().label() == -4
assert image.codomain().label() == 24
assert image.label() == "f"


# Three parallel functors and two callable transformations exercise component lookup and
# vertical composition without a finite component table.
parallel0 = affine_functor(SOURCE, TARGET, 1, 0)
parallel1 = affine_functor(SOURCE, TARGET, 1, 1)
parallel2 = affine_functor(SOURCE, TARGET, 1, 2)


def component_between(
    source: Cat().MorphismType,
    target: Cat().MorphismType,
    label: str,
):
    return lambda value: Mor(source.codomain())(
        source.on_object(value), target.on_object(value)
    )(label)


eta = Mor(Fun(SOURCE, TARGET))(parallel0, parallel1)(
    component_between(parallel0, parallel1, "eta")
)
theta = Mor(Fun(SOURCE, TARGET))(parallel1, parallel2)(
    component_between(parallel1, parallel2, "theta")
)
vertical = theta * eta
component = vertical.component(SOURCE(10**9))
assert component.domain().label() == 10**9
assert component.codomain().label() == 10**9 + 2
first_factor, second_factor = component.factors()
assert first_factor.label() == "eta"
assert second_factor.label() == "theta"
assert has_native_transformation(eta)
assert has_native_transformation(theta)
assert has_native_transformation(vertical)
assert eta.cell_dimension() == 2
assert theta.cell_dimension() == 2
assert vertical.cell_dimension() == 2
assert eta.boundary("source") is parallel0
assert eta.boundary("target") is parallel1
assert vertical.boundary("source") is parallel0
assert vertical.boundary("target") is parallel2
assert eta.boundary("source", 1) is SOURCE
assert eta.boundary("target", 1) is TARGET
eta.typecheck_cell()
vertical.typecheck_cell()


# Both whiskerings retain native transformations and evaluate their components only at
# the supplied object.  There is still no source enumeration or finite component map.
post = affine_functor(TARGET, MIDDLE, 3, 5)
left = eta.whisker_left(post)
left_component = left.component(SOURCE(17))
assert left_component.domain().label() == 56
assert left_component.codomain().label() == 59
assert left_component.label() == "eta"
assert has_native_transformation(left)
assert left.cell_dimension() == 2
assert left.boundary("source") is left.domain()
assert left.boundary("target") is left.codomain()
assert left.boundary("source", 1) is SOURCE
assert left.boundary("target", 1) is MIDDLE
left.typecheck_cell()

pre = affine_functor(MIDDLE, SOURCE, 2, -4)
right = eta.whisker_right(pre)
right_component = right.component(MIDDLE(23))
assert right_component.domain().label() == 42
assert right_component.codomain().label() == 43
assert right_component.label() == "eta"
assert has_native_transformation(right)
assert right.cell_dimension() == 2
assert right.boundary("source") is right.domain()
assert right.boundary("target") is right.codomain()
assert right.boundary("source", 1) is MIDDLE
assert right.boundary("target", 1) is TARGET
right.typecheck_cell()


# Horizontal composition uses both lower-boundary whiskerings and then the native
# top-boundary attachment, while Catlab supplies the semantic component.
post1 = affine_functor(TARGET, MIDDLE, 3, 6)
sigma = Mor(Fun(TARGET, MIDDLE))(post, post1)(
    component_between(post, post1, "sigma")
)
horizontal = eta.horizontal(sigma)
horizontal_component = horizontal.component(SOURCE(17))
assert horizontal_component.domain().label() == 56
assert horizontal_component.codomain().label() == 60
assert has_native_transformation(horizontal)
assert horizontal.cell_dimension() == 2
assert horizontal.boundary("source") is horizontal.domain()
assert horizontal.boundary("target") is horizontal.codomain()
assert horizontal.boundary("source", 1) is SOURCE
assert horizontal.boundary("target", 1) is MIDDLE
horizontal.typecheck_cell()
