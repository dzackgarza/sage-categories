"""Comma objects and commuting pairs.

The primitive is the explicit comma construction of Mathlib's
``CategoryTheory.Comma``. Its pullback presentation is supplied by slices.py.
https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Comma/Basic.html
"""

from __future__ import annotations

__all__ = ["CommaCategory", "CommaSpecialization", "comma_objects"]

from dataclasses import dataclass

from sympy import ask as sympy_ask

from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.functors import Cat, Fun, Functor, NaturalTransformation
from sage_categories.cat.morphisms import Mor, MorphismCategory
from sage_categories.cat.predicates import Proposition, ask, register_handler
from sage_categories.kernel.retention import identity_key
from sage_categories.kernel.sage_runtime import cached_function, cached_method


@dataclass(frozen=True, eq=False)
class CommaObject:
    first: CategoryOfCategories.ElementType
    second: CategoryOfCategories.ElementType
    arrow: MorphismCategory.ObjectType


@dataclass(frozen=True, eq=False)
class CommaMorphism:
    first: MorphismCategory.ObjectType
    second: MorphismCategory.ObjectType


class CommaCategory(
    Category[[MorphismCategory.ObjectType, MorphismCategory.ObjectType], []]
):
    """Objects ``(a,b,F(a) -> G(b))`` and commuting pairs of arrows."""

    class ObjectType:
        def __init__(self, data: CommaObject) -> None:
            self._comma_object = data

        def first(self) -> CategoryOfCategories.ElementType:
            return self._comma_object.first

        def second(self) -> CategoryOfCategories.ElementType:
            return self._comma_object.second

        def arrow(self) -> MorphismCategory.ObjectType:
            return self._comma_object.arrow

    class ElementType:
        pass

    class MorphismType:
        def __init__(self, data: CommaMorphism) -> None:
            self._comma_morphism = data

        def first(self) -> MorphismCategory.ObjectType:
            return self._comma_morphism.first

        def second(self) -> MorphismCategory.ObjectType:
            return self._comma_morphism.second

    def __init__(self, first: Functor, second: Functor) -> None:
        assert first.codomain() is second.codomain()
        self._comma_functors = (first, second)
        super().__init__()
        register_handler(self._equality, self._equal_objects)
        register_handler(self._equality, self._equal_morphisms)

    def comma_functors(self) -> tuple[Functor, Functor]:
        return self._comma_functors

    def _equal_objects(
        self,
        first: CommaCategory.ObjectType,
        second: CommaCategory.ObjectType,
        assumptions: Proposition,
    ) -> bool | None:
        return sympy_ask(
            (first.first() == second.first())
            & (first.second() == second.second())
            & (first.arrow() == second.arrow()),
            assumptions,
        )

    def _equal_morphisms(
        self,
        first: CommaCategory.MorphismType,
        second: CommaCategory.MorphismType,
        assumptions: Proposition,
    ) -> bool | None:
        return sympy_ask(
            (first.first() == second.first()) & (first.second() == second.second()),
            assumptions,
        )

    @cached_method(key=identity_key)
    def from_arrow(
        self,
        first: CategoryOfCategories.ElementType,
        second: CategoryOfCategories.ElementType,
        arrow: MorphismCategory.ObjectType,
    ) -> CommaCategory.ObjectType:
        forward, backward = self.comma_functors()
        assert first in forward.domain() and second in backward.domain()
        assert arrow in Mor(forward.codomain())(
            forward.on_object(first), backward.on_object(second)
        )
        return self.ObjectType(CommaObject(first, second, arrow))

    def morphism_from_pair(
        self,
        source: CommaCategory.ObjectType,
        target: CommaCategory.ObjectType,
        first: MorphismCategory.ObjectType,
        second: MorphismCategory.ObjectType,
    ) -> CommaCategory.MorphismType:
        forward, backward = self.comma_functors()
        assert source in self and target in self
        assert first in Mor(forward.domain())(source.first(), target.first())
        assert second in Mor(backward.domain())(source.second(), target.second())
        assert (
            ask(
                backward.on_morphism(second) * source.arrow()
                == target.arrow() * forward.on_morphism(first)
            )
            is not False
        )
        return self.MorphismType(
            domain=source, codomain=target, data=CommaMorphism(first, second)
        )

    def construct_morphism(
        self,
        source: CommaCategory.ObjectType,
        target: CommaCategory.ObjectType,
        first: MorphismCategory.ObjectType,
        second: MorphismCategory.ObjectType,
    ) -> CommaCategory.MorphismType:
        return self.morphism_from_pair(source, target, first, second)

    def construct_identity(
        self, value: CommaCategory.ObjectType
    ) -> CommaCategory.MorphismType:
        forward, backward = self.comma_functors()
        return self.morphism_from_pair(
            value,
            value,
            Mor(forward.domain())(value.first(), value.first()).one(),
            Mor(backward.domain())(value.second(), value.second()).one(),
        )

    def composite(
        self, second: CommaCategory.MorphismType, first: CommaCategory.MorphismType
    ) -> CommaCategory.MorphismType:
        assert first.codomain() is second.domain()
        return self.morphism_from_pair(
            first.domain(),
            second.codomain(),
            second.first() * first.first(),
            second.second() * first.second(),
        )

    @cached_method
    def first_projection(self) -> Functor:
        return Fun(self, self.comma_functors()[0].domain())(
            lambda value: value.first(), lambda arrow: arrow.first()
        )

    @cached_method
    def second_projection(self) -> Functor:
        return Fun(self, self.comma_functors()[1].domain())(
            lambda value: value.second(), lambda arrow: arrow.second()
        )

    @cached_method
    def defining_transformation(self) -> NaturalTransformation:
        first, second = self.comma_functors()
        return Mor(Fun(self, first.codomain()))(
            first * self.first_projection(), second * self.second_projection()
        )(lambda value: value.arrow())

    @cached_method
    def arrow_projection(self) -> Functor:
        base = self.comma_functors()[0].codomain()
        arrows = Fun(Cat().Simplex(1), base)
        return Fun(self, arrows)(
            lambda value: value.arrow(),
            lambda arrow: Mor(arrows)(arrow.domain().arrow(), arrow.codomain().arrow())(
                lambda vertex: (
                    self.defining_transformation().domain().on_morphism(arrow)
                    if Cat().Simplex(1).label(vertex) == 0
                    else self.defining_transformation().codomain().on_morphism(arrow)
                )
            ),
        )

    @cached_method
    def pair_projection(self) -> Functor:
        from sage_categories.cat.cones import cone

        first, second = self.comma_functors()
        target = Cat().Products()((first.domain(), second.domain()))
        diagram = target.product_factors()
        return target.universal_morphism(
            cone(
                diagram,
                self,
                lambda vertex: (self.first_projection(), self.second_projection())[
                    diagram.domain().label(vertex)
                ],
            )
        )

    def __repr__(self) -> str:
        return f"Comma({self._comma_functors[0]!r}, {self._comma_functors[1]!r})"


@cached_function(key=identity_key)
def comma_objects(first: Functor, second: Functor) -> CommaCategory:
    """The retained category before selection of a universal presentation."""
    return CommaCategory(first, second)


class CommaSpecialization(CommaCategory):
    """A named category with the objects and morphisms of its defining comma."""

    class ObjectType:
        pass

    class ElementType:
        pass

    class MorphismType:
        pass

    def structure_functors(self) -> tuple[Functor, ...]:
        return (
            Fun.full_subcategory_monomorphism(
                self, comma_objects(*self.comma_functors())
            ),
        )
