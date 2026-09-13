"""Ringed spaces and morphisms with sheaf action retained as natural transformations."""

from __future__ import annotations

from collections.abc import Callable, Hashable
from dataclasses import dataclass
from typing import Any, cast

from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.functors import Fun, Functor, NaturalTransformation
from sage_categories.cat.morphisms import Mor, MorphismCategory
from sage_categories.cat.predicates import ask
from sage_categories.geometry.sheaves import RingSheaf, _open_data, _rings
from sage_categories.geometry.spaces import TopologicalSpaces, TopologicalSpacesCategory
from sage_categories.kernel.retention import identity_key
from sage_categories.kernel.sage_runtime import cached_function, cached_method

__all__ = ["RingedSpaces", "RingedSpacesCategory"]


type SheafComponentRule = Callable[[frozenset[Hashable]], MorphismCategory.ObjectType]


@dataclass(frozen=True, eq=False, slots=True)
class _RingedSpaceData:
    space: TopologicalSpacesCategory.ObjectType
    sheaf: RingSheaf


def _component(
    transformation: NaturalTransformation,
    open_object: CategoryOfCategories.ElementType,
) -> MorphismCategory.ObjectType:
    return cast(MorphismCategory.ObjectType, cast(Any, transformation).component(open_object))


class RingedSpacesCategory(Category[[MorphismCategory.ObjectType], []]):
    """Spaces equipped with sheaves of commutative rings."""

    class ObjectType:
        def __init__(self, data: _RingedSpaceData) -> None:
            self._space, self._sheaf = data.space, data.sheaf

        def space(self) -> TopologicalSpacesCategory.ObjectType:
            return self._space

        def sheaf(self) -> RingSheaf:
            return self._sheaf

    class ElementType:
        pass

    class MorphismType:
        def __init__(self, data: tuple[MorphismCategory.ObjectType, NaturalTransformation]) -> None:
            self._continuous_map, self._sheaf_map = data

        def continuous_map(self) -> MorphismCategory.ObjectType:
            return self._continuous_map

        def sheaf_map(self) -> NaturalTransformation:
            return self._sheaf_map

    @cached_method
    def to_spaces(self) -> Functor:
        return Fun(self, TopologicalSpaces())(
            lambda value: cast(Any, value).space(),
            lambda arrow: cast(Any, arrow).continuous_map(),
        )

    def structure_functors(self) -> tuple[Functor, ...]:
        return (*super().structure_functors(), self.to_spaces())

    def __call__(
        self,
        space: TopologicalSpacesCategory.ObjectType,
        sheaf: RingSheaf,
    ) -> RingedSpacesCategory.ObjectType:
        assert sheaf.presheaf.space is space
        return self.ObjectType(_RingedSpaceData(space, sheaf))

    def homomorphism(
        self,
        source: RingedSpacesCategory.ObjectType,
        target: RingedSpacesCategory.ObjectType,
        continuous: MorphismCategory.ObjectType,
        component_rule: SheafComponentRule,
    ) -> RingedSpacesCategory.MorphismType:
        """A morphism ``X -> Y`` with ``O_Y -> O_X (f^-1)^op`` as an actual natural transformation."""
        assert continuous.domain() is source.space() and continuous.codomain() is target.space()
        inverse_op = cast(Any, continuous).inverse_image().op()
        target_sheaf = target.sheaf().presheaf.functor
        pushed_source = source.sheaf().presheaf.functor * inverse_op
        assert target_sheaf.domain() is pushed_source.domain() and target_sheaf.codomain() is pushed_source.codomain()

        def component(open_object: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
            arrow = component_rule(_open_data(open_object))
            assert arrow.domain() is target_sheaf.on_object(open_object)
            assert arrow.codomain() is pushed_source.on_object(open_object)
            return arrow

        transformation = Mor(Fun(target_sheaf.domain(), _rings()))(target_sheaf, pushed_source)(component)
        opens = target.space().open_category()
        objects = tuple(opens(point) for point in cast(Any, target.space().opens()).carrier())
        for smaller in objects:
            for larger in objects:
                if not (_open_data(smaller) <= _open_data(larger)):
                    continue
                inclusion = Mor(opens)(smaller, larger)()
                opposite = inclusion.op()
                left = pushed_source.on_morphism(opposite) * _component(transformation, larger)
                right = _component(transformation, smaller) * target_sheaf.on_morphism(opposite)
                assert ask(left == right) is True
        return cast(
            RingedSpacesCategory.MorphismType,
            cast(Any, self).MorphismType(domain=source, codomain=target, data=(continuous, transformation)),
        )

    def __repr__(self) -> str:
        return "RingedSpaces"


@cached_function(key=identity_key)
def RingedSpaces() -> RingedSpacesCategory:
    return RingedSpacesCategory()
