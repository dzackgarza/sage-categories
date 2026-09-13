"""Catlab executes functor and transformation composites over a nonfinite source."""

from sage_categories.all import Cat, Category, Fun, Mor, ask
from sage_categories.cat.canonical import FinitePresentedCategory
from sage_categories.cat.category import is_placed
from sage_categories.cat.native import (
    has_native_category,
    has_native_functor,
    has_native_transformation,
)
from sage_categories.engines import cells


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


def test_catlab_functor_calculus() -> None:
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

    # No source-object enumeration exists. Public application enters the retained Catlab
    # callable functor, and composition executes through Catlab's composite functor rather
    # than a second Python evaluator.
    value = SOURCE(10**6)
    assert not has_native_functor(first)
    assert not has_native_functor(second)
    assert not has_native_functor(composite)
    assert not has_native_category(SOURCE)
    assert not has_native_category(MIDDLE)
    assert first.on_object(value).label() == 10**6 + 1
    assert has_native_category(SOURCE)
    assert has_native_category(MIDDLE)
    assert has_native_functor(first)
    assert not has_native_functor(second)
    assert not has_native_functor(composite)
    assert composite.on_object(value).label() == 2 * (10**6 + 1)
    assert has_native_category(TARGET)
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
    assert not has_native_transformation(eta)
    # Exercise the homotopy-cell boundary before any public component lookup.  Primitive
    # transformations have no parallel Catlab recipe, so this order pins the bootstrap
    # path that reconstructs their boundaries from the retained declaration assignment.
    eta.typecheck_cell()
    assert eta.cell_dimension() == 2
    assert eta.boundary("source") is parallel0
    assert eta.boundary("target") is parallel1
    assert eta.boundary("source", 1) is SOURCE
    assert eta.boundary("target", 1) is TARGET
    primitive_component = eta.component(SOURCE(10**8))
    assert primitive_component.label() == "eta"
    assert has_native_transformation(eta)
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
    assert not is_placed(eta, Mor(Fun(SOURCE, TARGET)).Isomorphisms())
    assert theta.cell_dimension() == 2
    assert vertical.cell_dimension() == 2
    assert vertical.boundary("source") is parallel0
    assert vertical.boundary("target") is parallel2
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


def test_horizontal_interchange_uses_nonidentity_components() -> None:
    category = FinitePresentedCategory(
        "commuting loops",
        (0,),
        (("a", 0, 0), ("b", 0, 0)),
        ((("a", "b"), ("b", "a")),),
    )
    point = category(0)
    identity = Fun(category, category).one()

    def transformation(name: str):
        component = category.generator(name)
        return Mor(Fun(category, category))(identity, identity)(lambda _: component)

    eta = transformation("a")
    theta = transformation("b")
    sigma = transformation("a")
    tau = transformation("b")
    identity_component = Mor(category)(point, point).one()
    assert ask(eta.component(point) == identity_component) is False
    assert ask(theta.component(point) == identity_component) is False
    native_eta = cells.native_cell(eta.base_category(), eta)
    try:
        cells.native_signature(eta.base_category()).typecheck(native_eta.inverse(), True)
    except ValueError as error:
        assert "directed generator" in str(error)
    else:
        raise AssertionError("a noninvertible primitive transformation acquired a native inverse")

    vertical_then_horizontal = (theta * eta).horizontal(tau * sigma)
    horizontal_then_vertical = theta.horizontal(tau) * eta.horizontal(sigma)
    first_component = vertical_then_horizontal.component(point)
    second_component = horizontal_then_vertical.component(point)
    a, b = category.generator("a"), category.generator("b")
    expected = b * b * a * a

    assert ask(first_component == identity_component) is False
    assert ask(second_component == identity_component) is False
    assert ask(first_component == expected) is True
    assert ask(second_component == expected) is True
    assert ask(first_component == second_component) is True
    assert vertical_then_horizontal.domain() is horizontal_then_vertical.domain()
    assert vertical_then_horizontal.codomain() is horizontal_then_vertical.codomain()


test_catlab_functor_calculus()
test_horizontal_interchange_uses_nonidentity_components()
