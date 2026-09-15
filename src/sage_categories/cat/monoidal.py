"""Selected monoidal structures and actions, with their coherence morphisms.

The defining data and equations follow Mathlib's ``MonoidalCategoryStruct``
and ``MonoidalCategory``. Parameters form discrete categories of choices.
https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Monoidal/Category.html
"""

from __future__ import annotations

from collections.abc import Callable
from functools import singledispatch
from typing import Generic, NamedTuple

from typing_extensions import TypeVar

from sage_categories.cat.calculus import (
    binary_product_data,
    natural_isomorphism,
    pair_maps,
    product_functor,
    terminal_map,
)
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.functors import Cat, Fun, Functor, NaturalTransformation
from sage_categories.cat.morphisms import Mor, MorphismCategory
from sage_categories.cat.predicates import Proposition
from sage_categories.engines.diagrams import (
    DiagramBox,
    NonstrictMonoidalModel,
    evaluate_path,
)
from sage_categories.kernel.retention import identity_key
from sage_categories.kernel.sage_runtime import cached_function

__all__ = [
    "Actions",
    "ActionsCategory",
    "Cartesian",
    "Composition",
    "MonoidalStructures",
    "MonoidalStructuresCategory",
    "Reversed",
    "SelfAction",
    "TrivialAction",
    "register_cartesian_comparisons",
]


type CartesianComparisonHandler = Callable[..., MorphismCategory.ObjectType]


BaseCategory = TypeVar("BaseCategory", default="Category[..., ...]")
ActingCategory = TypeVar("ActingCategory", default="Category[..., ...]")
ActedCategory = TypeVar("ActedCategory", default="Category[..., ...]")


@singledispatch
def _native_cartesian_comparison(
    base: Category,
    operation: str,
    *arguments: object,
) -> MorphismCategory.ObjectType | None:
    """Use the native Cartesian comparison selected for ``base``'s concrete category type."""
    return None


def register_cartesian_comparisons(
    category_type: type[Category],
    handler: CartesianComparisonHandler,
) -> None:
    """Register one leaf category's native Cartesian comparison engine."""

    @_native_cartesian_comparison.register(category_type)
    def comparison(
        _base: Category,
        operation: str,
        *arguments: object,
    ) -> MorphismCategory.ObjectType | None:
        match type(_base) is category_type:
            case True:
                return handler(operation, *arguments)
            case False:
                return None


def tensor_object(tensor: Functor, first: CategoryOfCategories.ElementType, second: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
    return tensor.on_object(tensor.domain()((first, second)))


def tensor_morphism(tensor: Functor, first: MorphismCategory.ObjectType, second: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
    pairs = tensor.domain()
    return tensor.on_morphism(
        Mor(pairs)(
            pairs((first.domain(), second.domain())),
            pairs((first.codomain(), second.codomain())),
        )((first, second))
    )


def _identity_only_morphism[Morphism](
    source: CategoryOfCategories.ElementType,
    target: CategoryOfCategories.ElementType,
    constructor: Callable[..., Morphism],
) -> Morphism:
    """Construct the unique arrow of a discrete category of supplied structures."""
    assert source is target, "a morphism in this discrete category is an identity"
    return constructor(domain=source, codomain=target)


def _word_interpretation(
    monoidal: MonoidalStructuresCategory.ObjectType,
    word: tuple[CategoryOfCategories.ElementType, ...],
) -> CategoryOfCategories.ElementType:
    """The selected left-associated interpretation ``E(word)`` of a tensor word."""
    match word:
        case ():
            return monoidal.unit()
        case (first, *rest):
            value = first
            for following in rest:
                value = tensor_object(monoidal.tensor(), value, following)
            return value
    raise AssertionError("tensor-word interpretation is exhaustive")


def _word_comparison(
    monoidal: MonoidalStructuresCategory.ObjectType,
    first: tuple[CategoryOfCategories.ElementType, ...],
    second: tuple[CategoryOfCategories.ElementType, ...],
) -> MorphismCategory.ObjectType:
    """The supplied comparison ``c_{u,v}: E(uv) -> E(u) tensor E(v)``.

    This constructs the comparison from the selected associator and unitors; DisCoPy
    remains the evaluator of diagrams that consume it.  The recursion is on the formal
    tensor word, not on a DisCoPy diagram.
    """
    base, tensor = monoidal.underlying_category(), monoidal.tensor()
    match first, second:
        case (), _:
            value = _word_interpretation(monoidal, second)
            return monoidal.left_unitor().inverse().component(value)
        case _, ():
            value = _word_interpretation(monoidal, first)
            return monoidal.right_unitor().inverse().component(value)
        case _, (_single,):
            source = _word_interpretation(monoidal, first + second)
            return Mor(base)(source, source).one()
        case _, (*prefix, last):
            prefix_word = tuple(prefix)
            previous = _word_comparison(monoidal, first, prefix_word)
            last_value = last
            first_value = _word_interpretation(monoidal, first)
            prefix_value = _word_interpretation(monoidal, prefix_word)
            tensored = tensor_morphism(tensor, previous, Mor(base)(last_value, last_value).one())
            triples = monoidal.associator().domain().domain()
            associator = monoidal.associator().component(triples((first_value, prefix_value, last_value)))
            return associator * tensored
    raise AssertionError("tensor-word comparison is exhaustive")


@cached_function(key=identity_key)
def _diagram_model(
    monoidal: MonoidalStructuresCategory.ObjectType,
) -> NonstrictMonoidalModel[CategoryOfCategories.ElementType, MorphismCategory.ObjectType]:
    """DisCoPy interpretation into this exact supplied nonstrict monoidal structure."""
    base, tensor = monoidal.underlying_category(), monoidal.tensor()
    return NonstrictMonoidalModel(
        unit=monoidal.unit(),
        tensor_object=lambda first, second: tensor_object(tensor, first, second),
        tensor_morphism=lambda first, second: tensor_morphism(tensor, first, second),
        identity=lambda value: Mor(base)(value, value).one(),
        compose=lambda second, first: second * first,
        inverse=lambda arrow: arrow.inverse(),
        comparison=lambda first, second: _word_comparison(monoidal, first, second),
    )


def _diagram_box(
    model: NonstrictMonoidalModel[CategoryOfCategories.ElementType, MorphismCategory.ObjectType],
    name: str,
    arrow: MorphismCategory.ObjectType,
) -> DiagramBox:
    """One native generating box carrying an exact owned semantic morphism."""
    return model.box(name, (arrow.domain(),), (arrow.codomain(),), arrow)


@cached_function(key=identity_key)
def tensor_parentheses(tensor: Functor) -> tuple[Functor, Functor]:
    base = tensor.codomain()
    triples = Cat().Products()((base, base, base))
    first, second, third = (triples.product_projection(index) for index in range(3))
    return (
        tensor * pair_maps(Cat(), tensor * pair_maps(Cat(), first, second), third),
        tensor * pair_maps(Cat(), first, tensor * pair_maps(Cat(), second, third)),
    )


@cached_function(key=identity_key)
def tensor_units(tensor: Functor, unit: CategoryOfCategories.ElementType) -> tuple[Functor, Functor]:
    base = tensor.codomain()
    identity = Fun(base, base).one()
    constant = Fun(base, base).constant(unit)
    return tensor * pair_maps(Cat(), constant, identity), tensor * pair_maps(Cat(), identity, constant)


class _MonoidalData(NamedTuple):
    tensor: Functor
    unit: CategoryOfCategories.ElementType
    associator: NaturalTransformation
    left_unitor: NaturalTransformation
    right_unitor: NaturalTransformation


class MonoidalStructuresCategory(
    Category[[], []],
    Generic[BaseCategory],
):
    """The discrete category of supplied coherent monoidal structures on C."""

    class ObjectType(Generic[BaseCategory]):
        def __init__(self, data: _MonoidalData) -> None:
            self._monoidal_data = data

        def underlying_category(self) -> BaseCategory:
            return self.tensor().codomain()

        def tensor(self) -> Functor:
            return self._monoidal_data.tensor

        def unit(self) -> CategoryOfCategories.ElementType:
            return self._monoidal_data.unit

        def associator(self) -> NaturalTransformation:
            return self._monoidal_data.associator

        def left_unitor(self) -> NaturalTransformation:
            return self._monoidal_data.left_unitor

        def right_unitor(self) -> NaturalTransformation:
            return self._monoidal_data.right_unitor

        def diagram_wire(self, value: CategoryOfCategories.ElementType):
            """Return the formal DisCoPy wire carrying this exact owned object."""
            assert value in self.underlying_category()
            return _diagram_model(self).wire(value)

        def diagram_box(
            self,
            name: str,
            domain: tuple[CategoryOfCategories.ElementType, ...],
            codomain: tuple[CategoryOfCategories.ElementType, ...],
            arrow: MorphismCategory.ObjectType,
        ) -> DiagramBox:
            """Return one formal box with this structure's selected word endpoints.

            The formal words are interpreted by the fixed left-associated convention
            ``E``.  The supplied semantic arrow must have those exact owned endpoints;
            the box therefore cannot silently strictify or retarget a comparison map.
            """
            domain = tuple(domain)
            codomain = tuple(codomain)
            expected_domain = _word_interpretation(self, domain)
            expected_codomain = _word_interpretation(self, codomain)
            assert arrow.domain() is expected_domain and arrow.codomain() is expected_codomain
            return _diagram_model(self).box(name, domain, codomain, arrow)

        def interpret(self, diagram) -> MorphismCategory.ObjectType:
            """Interpret a formal DisCoPy diagram through this supplied structure.

            Tensor layers use the retained associator and unitor comparisons of this
            exact structure via ``c_{u,v}: E(uv) -> E(u) tensor E(v)``.  Ordinary boxes
            retain their supplied semantic arrows, including noninvertible ones.
            """
            return _diagram_model(self).evaluate(diagram)

        def pentagon(
            self,
            w: CategoryOfCategories.ElementType,
            x: CategoryOfCategories.ElementType,
            y: CategoryOfCategories.ElementType,
            z: CategoryOfCategories.ElementType,
        ) -> Proposition:
            tensor, associator = self.tensor(), self.associator()
            triples = associator.domain().domain()

            def a(
                p: CategoryOfCategories.ElementType,
                q: CategoryOfCategories.ElementType,
                r: CategoryOfCategories.ElementType,
            ) -> MorphismCategory.ObjectType:
                return associator.component(triples((p, q, r)))

            wx, xy, yz = tensor_object(tensor, w, x), tensor_object(tensor, x, y), tensor_object(tensor, y, z)
            base = self.underlying_category()
            model = _diagram_model(self)
            first_leg = model.evaluate(_diagram_box(model, "a_wxy", a(w, x, y)) @ _diagram_box(model, "1_z", Mor(base)(z, z).one()))
            middle_leg = model.evaluate(_diagram_box(model, "a_w_xy_z", a(w, xy, z)))
            last_leg = model.evaluate(_diagram_box(model, "1_w", Mor(base)(w, w).one()) @ _diagram_box(model, "a_xyz", a(x, y, z)))
            long = evaluate_path(
                (first_leg, middle_leg, last_leg),
                domain=first_leg.domain(),
                codomain=last_leg.codomain(),
                identity=lambda value: Mor(base)(value, value).one(),
                compose=lambda second, first: second * first,
            )
            short_first = model.evaluate(_diagram_box(model, "a_wx_y_z", a(wx, y, z)))
            short_last = model.evaluate(_diagram_box(model, "a_w_x_yz", a(w, x, yz)))
            short = evaluate_path(
                (short_first, short_last),
                domain=short_first.domain(),
                codomain=short_last.codomain(),
                identity=lambda value: Mor(base)(value, value).one(),
                compose=lambda second, first: second * first,
            )
            return long == short

        def triangle(self, x: CategoryOfCategories.ElementType, y: CategoryOfCategories.ElementType) -> Proposition:
            base = self.underlying_category()
            associator = self.associator().component(self.associator().domain().domain()((x, self.unit(), y)))
            model = _diagram_model(self)
            last = model.evaluate(_diagram_box(model, "1_x", Mor(base)(x, x).one()) @ _diagram_box(model, "lambda_y", self.left_unitor().component(y)))
            left = evaluate_path(
                (associator, last),
                domain=associator.domain(),
                codomain=last.codomain(),
                identity=lambda value: Mor(base)(value, value).one(),
                compose=lambda second, first: second * first,
            )
            right = model.evaluate(_diagram_box(model, "rho_x", self.right_unitor().component(x)) @ _diagram_box(model, "1_y", Mor(base)(y, y).one()))
            return left == right

    class ElementType:
        pass

    class MorphismType:
        pass

    def __init__(self, base: BaseCategory) -> None:
        self._base = base

    def __call__(
        self,
        tensor: Functor,
        unit: CategoryOfCategories.ElementType,
        associator: NaturalTransformation,
        left_unitor: NaturalTransformation,
        right_unitor: NaturalTransformation,
    ) -> MonoidalStructuresCategory.ObjectType:
        assert tensor.codomain() is self._base
        assert all(tensor.domain().product_projection(index).codomain() is self._base for index in (0, 1))
        assert unit in self._base
        left, right = tensor_parentheses(tensor)
        left_unit, right_unit = tensor_units(tensor, unit)
        identity = Fun(self._base, self._base).one()
        for comparison, source, target in ((associator, left, right), (left_unitor, left_unit, identity), (right_unitor, right_unit, identity)):
            assert comparison in Mor(Fun(source.domain(), self._base))(source, target).Isomorphisms()
        return self.ObjectType(_MonoidalData(tensor, unit, associator, left_unitor, right_unitor))

    def construct_morphism(self, source: MonoidalStructuresCategory.ObjectType, target: MonoidalStructuresCategory.ObjectType) -> MonoidalStructuresCategory.MorphismType:
        return _identity_only_morphism(source, target, self.MorphismType)


@cached_function(key=identity_key)
def MonoidalStructures[BaseCategory: "Category[..., ...]"](base: BaseCategory) -> MonoidalStructuresCategory[BaseCategory]:
    return MonoidalStructuresCategory(base)


def _cartesian_rebracket(
    base: Category,
    triple: CategoryOfCategories.ElementType,
    forward: bool,
) -> MorphismCategory.ObjectType:
    """One component of the cartesian associator, native when available and universal otherwise."""
    x, y, z = (triple.family_component(index) for index in range(3))
    xy, yz = binary_product_data(base, x, y), binary_product_data(base, y, z)
    left_product = binary_product_data(base, xy.apex(), z)
    right_product = binary_product_data(base, x, yz.apex())
    operation = "associator_forward" if forward else "associator_inverse"
    native = _native_cartesian_comparison(
        base,
        operation,
        x,
        y,
        z,
        left_product.apex(),
        right_product.apex(),
    )
    match native:
        case None:
            pass
        case _:
            return native
    match forward:
        case True:
            source = left_product
            return pair_maps(base, xy.leg(0) * source.leg(0), pair_maps(base, xy.leg(1) * source.leg(0), source.leg(1)))
        case False:
            source = right_product
            return pair_maps(base, pair_maps(base, source.leg(0), yz.leg(0) * source.leg(1)), yz.leg(1) * source.leg(1))


def _cartesian_unitor_component(
    base: Category,
    unit: CategoryOfCategories.ElementType,
    value: CategoryOfCategories.ElementType,
    side: str,
    forward: bool,
) -> MorphismCategory.ObjectType:
    """One cartesian unitor component, sharing native/fallback selection for both sides."""
    match side:
        case "left":
            product = binary_product_data(base, unit, value)
            forward_leg = 1
        case "right":
            product = binary_product_data(base, value, unit)
            forward_leg = 0
        case _:
            raise AssertionError(f"unknown cartesian unitor side {side!r}")
    operation = f"{side}_unitor_{'forward' if forward else 'inverse'}"
    native = _native_cartesian_comparison(base, operation, value, product.apex())
    match native:
        case None:
            pass
        case _:
            return native
    match side, forward:
        case _, True:
            return product.leg(forward_leg)
        case "left", False:
            return pair_maps(base, terminal_map(base, value), Mor(base)(value, value).one())
        case "right", False:
            return pair_maps(base, Mor(base)(value, value).one(), terminal_map(base, value))
        case _:
            raise AssertionError(f"unknown cartesian unitor direction {side!r}, {forward!r}")


@cached_function(key=identity_key)
def Cartesian(base: Category) -> MonoidalStructuresCategory.ObjectType:
    tensor, unit = product_functor(base), base.Terminal()
    left, right = tensor_parentheses(tensor)
    associator = natural_isomorphism(
        left,
        right,
        lambda triple: _cartesian_rebracket(base, triple, True),
        lambda triple: _cartesian_rebracket(base, triple, False),
    )
    left_unit, right_unit = tensor_units(tensor, unit)
    identity = Fun(base, base).one()

    left_unitor = natural_isomorphism(
        left_unit,
        identity,
        lambda x: _cartesian_unitor_component(base, unit, x, "left", True),
        lambda x: _cartesian_unitor_component(base, unit, x, "left", False),
    )
    right_unitor = natural_isomorphism(
        right_unit,
        identity,
        lambda x: _cartesian_unitor_component(base, unit, x, "right", True),
        lambda x: _cartesian_unitor_component(base, unit, x, "right", False),
    )
    return MonoidalStructures(base)(tensor, unit, associator, left_unitor, right_unitor)


@cached_function(key=identity_key)
def Reversed(monoidal: MonoidalStructuresCategory.ObjectType) -> MonoidalStructuresCategory.ObjectType:
    """``V^rev``: the same category and unit with ``x (x)^rev y = y (x) x``.

    Reversing a monoidal category needs no braiding: it exchanges the arguments of the
    tensor and reads each coherence isomorphism at the reversed triple.  The associator
    is ``a^rev_{x,y,z} = a_{z,y,x}^{-1}`` and the two unitors trade places.
    (Mathlib ``CategoryTheory.Monoidal.Braided`` builds the same reversal as
    ``MonoidalCategory.reverse``; nLab, monoidal category, "Opposite and reverse".)

    Its use here is that a right action is a left action of the reverse.  A monoid object
    of ``V`` is a monoid object of ``V^rev`` on the same multiplication and unit, because
    ``S (x)^rev S`` is ``S (x) S``; that monoid is the opposite monoid, and its left
    modules in ``V^rev`` are the right ``S``-modules of ``V`` (``specs/bimodules.md``).
    """
    base, unit = monoidal.underlying_category(), monoidal.unit()
    pairs = monoidal.tensor().domain()
    swap = pair_maps(Cat(), pairs.product_projection(1), pairs.product_projection(0))
    tensor = monoidal.tensor() * swap
    left, right = tensor_parentheses(tensor)
    triples = left.domain()
    original, opposed = monoidal.associator(), monoidal.associator().inverse()

    def reverse(triple: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
        return triples(tuple(triple.family_component(index) for index in (2, 1, 0)))

    associator = natural_isomorphism(
        left,
        right,
        lambda triple: opposed.component(reverse(triple)),
        lambda triple: original.component(reverse(triple)),
    )
    left_unit, right_unit = tensor_units(tensor, unit)
    identity = Fun(base, base).one()
    right_first, left_second = monoidal.right_unitor(), monoidal.left_unitor()
    return MonoidalStructures(base)(
        tensor,
        unit,
        associator,
        natural_isomorphism(left_unit, identity, right_first.component, right_first.inverse().component),
        natural_isomorphism(right_unit, identity, left_second.component, left_second.inverse().component),
    )


@cached_function(key=identity_key)
def Composition(base: Category) -> MonoidalStructuresCategory.ObjectType:
    endofunctors = Fun(base, base)
    pairs = Cat().Products()((endofunctors, endofunctors))
    tensor = Fun(pairs, endofunctors)(
        lambda pair: pair.family_component(0) * pair.family_component(1), lambda arrow: Cat().horizontal_composite(arrow.family_component(0), arrow.family_component(1))
    )
    unit = endofunctors.one()
    left, right = tensor_parentheses(tensor)
    left_unit, right_unit = tensor_units(tensor, unit)
    identity = Fun(endofunctors, endofunctors).one()

    def comparison(first: Functor, second: Functor) -> NaturalTransformation:
        return natural_isomorphism(
            first,
            second,
            lambda x: Mor(endofunctors)(first.on_object(x), second.on_object(x)).one(),
            lambda x: Mor(endofunctors)(second.on_object(x), first.on_object(x)).one(),
        )

    return MonoidalStructures(endofunctors)(tensor, unit, comparison(left, right), comparison(left_unit, identity), comparison(right_unit, identity))


class _ActionData(NamedTuple):
    action: Functor
    associator: NaturalTransformation
    unitor: NaturalTransformation


class ActionsCategory(
    Category[[], []],
    Generic[ActingCategory, ActedCategory],
):
    """The discrete category of supplied coherent left actions of M on C."""

    class ObjectType(Generic[ActingCategory, ActedCategory]):
        def __init__(self, data: _ActionData) -> None:
            self._action_data = data

        def monoidal_structure(self) -> MonoidalStructuresCategory.ObjectType[ActingCategory]:
            return self.category()._monoidal

        def underlying_category(self) -> ActedCategory:
            return self.action().codomain()

        def action(self) -> Functor:
            return self._action_data.action

        def associator(self) -> NaturalTransformation:
            return self._action_data.associator

        def unitor(self) -> NaturalTransformation:
            return self._action_data.unitor

        def pentagon(
            self,
            m: CategoryOfCategories.ElementType,
            n: CategoryOfCategories.ElementType,
            p: CategoryOfCategories.ElementType,
            x: CategoryOfCategories.ElementType,
        ) -> Proposition:
            monoidal, action = self.monoidal_structure(), self.action()
            tensor = monoidal.tensor()
            triples = self.associator().domain().domain()

            def a(
                first: CategoryOfCategories.ElementType,
                second: CategoryOfCategories.ElementType,
                value: CategoryOfCategories.ElementType,
            ) -> MorphismCategory.ObjectType:
                return self.associator().component(triples((first, second, value)))

            mn, np = tensor_object(tensor, m, n), tensor_object(tensor, n, p)
            px = tensor_object(action, p, x)
            alpha = monoidal.associator().component(monoidal.associator().domain().domain()((m, n, p)))
            identity_m = Mor(monoidal.underlying_category())(m, m).one()
            identity_x = Mor(self.underlying_category())(x, x).one()
            left_first, left_last = a(mn, p, x), a(m, n, px)
            left = evaluate_path(
                (left_first, left_last),
                domain=left_first.domain(),
                codomain=left_last.codomain(),
                identity=lambda value: Mor(self.underlying_category())(value, value).one(),
                compose=lambda second, first: second * first,
            )
            right_first = tensor_morphism(action, alpha, identity_x)
            right_middle = a(m, np, x)
            right_last = tensor_morphism(action, identity_m, a(n, p, x))
            right = evaluate_path(
                (right_first, right_middle, right_last),
                domain=right_first.domain(),
                codomain=right_last.codomain(),
                identity=lambda value: Mor(self.underlying_category())(value, value).one(),
                compose=lambda second, first: second * first,
            )
            return left == right

        def triangle(self, m: CategoryOfCategories.ElementType, x: CategoryOfCategories.ElementType) -> Proposition:
            monoidal, action = self.monoidal_structure(), self.action()
            associator = self.associator().component(self.associator().domain().domain()((m, monoidal.unit(), x)))
            identity_m = Mor(monoidal.underlying_category())(m, m).one()
            identity_x = Mor(self.underlying_category())(x, x).one()
            last = tensor_morphism(action, identity_m, self.unitor().component(x))
            left = evaluate_path(
                (associator, last),
                domain=associator.domain(),
                codomain=last.codomain(),
                identity=lambda value: Mor(self.underlying_category())(value, value).one(),
                compose=lambda second, first: second * first,
            )
            right = tensor_morphism(action, monoidal.right_unitor().component(m), identity_x)
            return left == right

    class ElementType:
        pass

    class MorphismType:
        pass

    def __init__(self, monoidal: MonoidalStructuresCategory.ObjectType[ActingCategory], base: ActedCategory) -> None:
        self._monoidal, self._base = monoidal, base

    def __call__(self, action: Functor, associator: NaturalTransformation, unitor: NaturalTransformation) -> ActionsCategory.ObjectType[ActingCategory, ActedCategory]:
        monoidal = self._monoidal
        assert action in Fun(Cat().Products()((monoidal.underlying_category(), self._base)), self._base)
        triples = Cat().Products()((monoidal.underlying_category(), monoidal.underlying_category(), self._base))
        first, second, third = (triples.product_projection(index) for index in range(3))
        left = action * pair_maps(Cat(), monoidal.tensor() * pair_maps(Cat(), first, second), third)
        right = action * pair_maps(Cat(), first, action * pair_maps(Cat(), second, third))
        identity = Fun(self._base, self._base).one()
        constant = Fun(self._base, monoidal.underlying_category()).constant(monoidal.unit())
        unital = action * pair_maps(Cat(), constant, identity)
        assert associator in Mor(Fun(triples, self._base))(left, right).Isomorphisms()
        assert unitor in Mor(Fun(self._base, self._base))(unital, identity).Isomorphisms()
        return self.ObjectType(_ActionData(action, associator, unitor))

    def construct_morphism(self, source: ActionsCategory.ObjectType, target: ActionsCategory.ObjectType) -> ActionsCategory.MorphismType:
        return _identity_only_morphism(source, target, self.MorphismType)


@cached_function(key=identity_key)
def Actions[ActingCategory: "Category[..., ...]", ActedCategory: "Category[..., ...]"](
    monoidal: MonoidalStructuresCategory.ObjectType[ActingCategory],
    base: ActedCategory,
) -> ActionsCategory[ActingCategory, ActedCategory]:
    return ActionsCategory(monoidal, base)


@cached_function(key=identity_key)
def SelfAction(monoidal: MonoidalStructuresCategory.ObjectType) -> ActionsCategory.ObjectType:
    return Actions(monoidal, monoidal.underlying_category())(monoidal.tensor(), monoidal.associator(), monoidal.left_unitor())


@cached_function(key=identity_key)
def TrivialAction(monoidal: MonoidalStructuresCategory.ObjectType, base: Category) -> ActionsCategory.ObjectType:
    """The action through the second projection, with identity coherence maps."""
    pairs = Cat().Products()((monoidal.underlying_category(), base))
    action = pairs.product_projection(1)
    triples = Cat().Products()((monoidal.underlying_category(), monoidal.underlying_category(), base))
    first, second, third = (triples.product_projection(index) for index in range(3))
    left = action * pair_maps(Cat(), monoidal.tensor() * pair_maps(Cat(), first, second), third)
    right = action * pair_maps(Cat(), first, action * pair_maps(Cat(), second, third))
    identity = Fun(base, base).one()
    constant = Fun(base, monoidal.underlying_category()).constant(monoidal.unit())
    unital = action * pair_maps(Cat(), constant, identity)
    associator = natural_isomorphism(
        left,
        right,
        lambda triple: Mor(base)(triple.family_component(2), triple.family_component(2)).one(),
        lambda triple: Mor(base)(triple.family_component(2), triple.family_component(2)).one(),
    )
    unitor = natural_isomorphism(unital, identity, lambda value: Mor(base)(value, value).one(), lambda value: Mor(base)(value, value).one())
    return Actions(monoidal, base)(action, associator, unitor)
