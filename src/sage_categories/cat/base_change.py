"""Change of base through the generic pullback in ``Cat()``."""

from __future__ import annotations

from sage_categories.cat.cat_constructions import LimitCategory, _retained_object_component
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.constructions import LimitsCategory
from sage_categories.cat.diagrams import cospan_diagram
from sage_categories.cat.functors import Cat, Fun, Functor
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.kernel.refinement import is_placed, refine
from sage_categories.kernel.retention import identity_key
from sage_categories.kernel.sage_runtime import cached_function

__all__ = ["base_change"]


def _cartesian_lift(
    base_functor: Functor,
    defining_functor: Functor,
    pullback: LimitCategory,
    morphism: MorphismCategory.ObjectType,
    target: CategoryOfCategories.ElementType,
) -> MorphismCategory.ObjectType:
    """Pull back one selected cartesian lift componentwise."""
    image = base_functor.on_morphism(morphism)
    lifted = defining_functor.cartesian_lift(image, _retained_object_component(target, 1))
    source = pullback((morphism.domain(), lifted.domain(), image.domain()))
    return pullback.construct_morphism(source, target, (morphism, lifted, image))


def _cocartesian_lift(
    base_functor: Functor,
    defining_functor: Functor,
    pullback: LimitCategory,
    morphism: MorphismCategory.ObjectType,
    source: CategoryOfCategories.ElementType,
) -> MorphismCategory.ObjectType:
    """Pull back one selected cocartesian lift componentwise."""
    image = base_functor.on_morphism(morphism)
    lifted = defining_functor.cocartesian_lift(image, _retained_object_component(source, 1))
    target = pullback((morphism.codomain(), lifted.codomain(), image.codomain()))
    return pullback.construct_morphism(source, target, (morphism, lifted, image))


@cached_function(key=identity_key)
def _base_change_data(
    base_functor: Functor,
    defining_functor: Functor,
) -> tuple[Category, Functor]:
    """Return the retained pullback category and its projection to the new base."""
    assert base_functor.codomain() is defining_functor.codomain(), f"{base_functor!r} and {defining_functor!r} have different codomains"
    ambient = Cat()
    diagram = cospan_diagram(ambient, base_functor, defining_functor)
    pullbacks = ambient.Pullbacks()
    assert isinstance(pullbacks, LimitsCategory)
    pullback = pullbacks(diagram)
    assert isinstance(pullback, Category)
    presentation = pullbacks.universal_data(diagram)
    projection = presentation.leg(0)
    assert isinstance(projection, Functor)
    assert projection.domain() is pullback
    return pullback, projection


@cached_function(key=identity_key)
def _retain_cartesian_base_change(
    base_functor: Functor,
    defining_functor: Functor,
) -> None:
    """Install the cartesian lifts supplied by a fibration exactly once."""
    pullback, projection = _base_change_data(base_functor, defining_functor)
    if projection is defining_functor:
        return
    assert isinstance(pullback, LimitCategory), f"{pullback!r} is not the strict Cat pullback"
    refine(projection, Fun.Fibrations())
    projection.retain_cartesian_lifts(
        lambda morphism, target: _cartesian_lift(
            base_functor,
            defining_functor,
            pullback,
            morphism,
            target,
        )
    )


@cached_function(key=identity_key)
def _retain_cocartesian_base_change(
    base_functor: Functor,
    defining_functor: Functor,
) -> None:
    """Install the cocartesian lifts supplied by an opfibration exactly once."""
    pullback, projection = _base_change_data(base_functor, defining_functor)
    if projection is defining_functor:
        return
    assert isinstance(pullback, LimitCategory), f"{pullback!r} is not the strict Cat pullback"
    refine(projection, Fun.Opfibrations())
    projection.retain_cocartesian_lifts(
        lambda morphism, source: _cocartesian_lift(
            base_functor,
            defining_functor,
            pullback,
            morphism,
            source,
        )
    )


def base_change(base_functor: Functor, defining_functor: Functor) -> Functor:
    """Return ``D ×_C E -> D`` for ``D -> C <- E``.

    The pullback's retained limiting presentation owns both projections and the
    common composite to ``C``.  Fibration data can be supplied after the
    pullback is first constructed; each positive property installs its selected
    lifts once when it is first available.
    """
    _pullback, projection = _base_change_data(base_functor, defining_functor)

    match is_placed(defining_functor, Fun.Fibrations()):
        case True:
            _retain_cartesian_base_change(base_functor, defining_functor)
        case False:
            pass
    match is_placed(defining_functor, Fun.Opfibrations()):
        case True:
            _retain_cocartesian_base_change(base_functor, defining_functor)
        case False:
            pass
    return projection
