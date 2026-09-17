"""Stalks and germs of represented commutative-ring sheaves.

For the first executable domain, a point of a finite represented topology has an
owned finite poset of neighborhoods.  The stalk is retained as the colimit of the
section-ring diagram on the opposite neighborhood category.  The finite topology's
least neighborhood evaluates that colimit without changing its public universal
presentation.
"""

from __future__ import annotations

from collections.abc import Hashable
from dataclasses import dataclass

from sympy import false, true

from sage_categories.cat.assembly import chosen_construction
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.cones import ConeCategory, LimitConesCategory, cocone, cocones
from sage_categories.cat.functors import Functor
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.opposites import opposite_functor
from sage_categories.cat.predicates import ask
from sage_categories.geometry._ring_categories import commutative_rings as _rings
from sage_categories.geometry.ringed_spaces import RingedSpacesCategory
from sage_categories.geometry.sheaves import RingSheaf
from sage_categories.order.posets import FinitePosets, Posets, Thin

__all__ = [
    "ring_stalk",
    "ringed_stalk_map",
    "stalk_diagram",
    "stalk_germ",
    "stalk_presentation",
]


@dataclass(frozen=True, eq=False, slots=True)
class _FiniteStalkData[PointDatum: Hashable]:
    sheaf: RingSheaf[frozenset[PointDatum]]
    point: CategoryOfCategories.ElementType
    neighborhoods: CategoryOfCategories.ElementType
    neighborhood_poset: CategoryOfCategories.ElementType
    inclusion: MorphismCategory.ObjectType
    neighborhood_category: Category
    diagram: Functor
    least_key: frozenset[PointDatum]
    least_vertex: CategoryOfCategories.ElementType


def _contains_point(
    point: CategoryOfCategories.ElementType,
    open_point: CategoryOfCategories.ElementType,
):
    open_key = open_point.datum()
    assert isinstance(open_key, frozenset)
    match point.datum() in open_key:
        case True:
            return true
        case False:
            return false


def _new_stalk_data[PointDatum: Hashable](
    sheaf: RingSheaf[frozenset[PointDatum]],
    point: CategoryOfCategories.ElementType,
) -> _FiniteStalkData[PointDatum]:
    presheaf = sheaf.presheaf
    space = presheaf.space
    assert point.parent() is space.carrier(), (
        f"{point!r} is not a point of this sheaf's space"
    )
    ambient = space.opens()
    assert ambient in FinitePosets(), (
        "the first stalk evaluator requires a finite represented open poset"
    )

    subobjects = Posets().Subobjects(ambient)
    neighborhoods = subobjects.from_predicate(
        lambda open_point: _contains_point(point, open_point)
    )
    inclusion = subobjects.defining_arrow().on_object(neighborhoods)
    neighborhood_poset = inclusion.domain()
    assert neighborhood_poset in FinitePosets()
    assert ask(neighborhood_poset.is_with_bottom()) is True, (
        "the represented neighborhoods of a point must have their finite intersection"
    )
    least = neighborhood_poset.bottom()
    ambient_least = inclusion(least)
    least_key = ambient_least.datum()
    assert isinstance(least_key, frozenset)

    neighborhood_inclusion = Thin.on_morphism(inclusion)
    neighborhood_category = neighborhood_inclusion.domain()
    assert neighborhood_inclusion.codomain() is space.open_category()
    diagram = presheaf.functor * opposite_functor(neighborhood_inclusion)
    least_vertex = neighborhood_category(least)
    assert least_vertex in diagram.domain()
    return _FiniteStalkData(
        sheaf,
        point,
        neighborhoods,
        neighborhood_poset,
        inclusion,
        neighborhood_category,
        diagram,
        least_key,
        least_vertex,
    )


def _stalk_data[PointDatum: Hashable](
    sheaf: RingSheaf[frozenset[PointDatum]],
    point: CategoryOfCategories.ElementType,
) -> _FiniteStalkData[PointDatum]:
    return chosen_construction(
        sheaf.presheaf.functor,
        "finite-ring-stalk-data",
        (point,),
        lambda: _new_stalk_data(sheaf, point),
    )


def _open_key_at_vertex[PointDatum: Hashable](
    data: _FiniteStalkData[PointDatum],
    vertex: CategoryOfCategories.ElementType,
) -> frozenset[PointDatum]:
    local_point = vertex.point()
    ambient_point = data.inclusion(local_point)
    key = ambient_point.datum()
    assert isinstance(key, frozenset)
    return key


def _new_ring_stalk[PointDatum: Hashable](
    data: _FiniteStalkData[PointDatum],
) -> CategoryOfCategories.ElementType:
    presheaf = data.sheaf.presheaf
    stalk = presheaf.section_ring(data.least_key)
    diagram = data.diagram

    def germ(vertex: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
        key = _open_key_at_vertex(data, vertex)
        arrow = presheaf.restriction(key, data.least_key)
        assert arrow.domain() is diagram.on_object(vertex) and arrow.codomain() is stalk
        return arrow

    selected = cocone(diagram, stalk, germ)

    def mediator(candidate: ConeCategory.ObjectType) -> MorphismCategory.ObjectType:
        return candidate.leg(data.least_vertex)

    retained = (
        _rings()
        .Colimits(diagram.domain())
        .with_universal_data(
            diagram,
            stalk,
            selected,
            mediator,
        )
    )
    assert retained is stalk
    return stalk


def ring_stalk[PointDatum: Hashable](
    sheaf: RingSheaf[frozenset[PointDatum]],
    point: CategoryOfCategories.ElementType,
) -> CategoryOfCategories.ElementType:
    """The owned stalk ring ``O_{X,point}`` as a retained neighborhood colimit."""
    data = _stalk_data(sheaf, point)
    return chosen_construction(
        sheaf.presheaf.functor,
        "finite-ring-stalk",
        (point,),
        lambda: _new_ring_stalk(data),
    )


def stalk_diagram[PointDatum: Hashable](
    sheaf: RingSheaf[frozenset[PointDatum]],
    point: CategoryOfCategories.ElementType,
) -> Functor:
    """The exact diagram of section rings over represented neighborhoods of ``point``."""
    ring_stalk(sheaf, point)
    return _stalk_data(sheaf, point).diagram


def stalk_presentation[PointDatum: Hashable](
    sheaf: RingSheaf[frozenset[PointDatum]],
    point: CategoryOfCategories.ElementType,
) -> LimitConesCategory.ObjectType:
    """The retained colimit presentation of ``ring_stalk(sheaf, point)``."""
    diagram = stalk_diagram(sheaf, point)
    return _rings().Colimits(diagram.domain()).universal_data(diagram)


def stalk_germ[PointDatum: Hashable](
    sheaf: RingSheaf[frozenset[PointDatum]],
    point: CategoryOfCategories.ElementType,
    open_key: frozenset[PointDatum],
) -> MorphismCategory.ObjectType:
    """The canonical germ map ``O(open_key) -> O_{X,point}``."""
    data = _stalk_data(sheaf, point)
    open_point = data.neighborhood_poset.point(open_key)
    vertex = data.neighborhood_category(open_point)
    return stalk_presentation(sheaf, point).leg(vertex)


def ringed_stalk_map(
    mapping: RingedSpacesCategory.MorphismType,
    source_point: CategoryOfCategories.ElementType,
) -> MorphismCategory.ObjectType:
    """The induced map ``O_{Y,f(x)} -> O_{X,x}`` of represented stalks."""
    source, target = mapping.domain(), mapping.codomain()
    assert source_point.parent() is source.space().carrier()
    target_point = mapping.continuous_map().underlying_map()(source_point)
    source_sheaf, target_sheaf = source.sheaf(), target.sheaf()
    source_stalk = ring_stalk(source_sheaf, source_point)
    target_stalk = ring_stalk(target_sheaf, target_point)
    target_data = _stalk_data(target_sheaf, target_point)
    target_diagram = target_data.diagram

    def induced_germ(
        vertex: CategoryOfCategories.ElementType,
    ) -> MorphismCategory.ObjectType:
        target_key = _open_key_at_vertex(target_data, vertex)
        target_open = target_sheaf.presheaf.open_object(target_key)
        component = mapping.sheaf_map().component(target_open)
        source_open = mapping.continuous_map().inverse_image().on_object(target_open)
        source_key = source_sheaf.presheaf.open_key(source_open)
        germ = stalk_germ(source_sheaf, source_point, source_key)
        assert component.domain() is target_diagram.on_object(vertex)
        assert germ.domain() is component.codomain() and germ.codomain() is source_stalk
        return germ * component

    candidate = cocones(target_diagram)(
        cocone(target_diagram, source_stalk, induced_germ)
    )
    result = stalk_presentation(target_sheaf, target_point).lift(candidate)
    assert result.domain() is target_stalk and result.codomain() is source_stalk
    return result
