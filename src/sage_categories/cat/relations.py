"""Relations in a regular category, with inclusions as 2-morphisms.

Composition is the image of a pullback. Meets are intersections of
subobjects. Reference: https://1lab.dev/Cat.Bi.Instances.Relations.html
"""

from __future__ import annotations

__all__ = [
    "RelationsCategory",
    "RelationMorphismsCategory",
    "Relations",
    "relation_inclusion",
]

from sympy import ask as sympy_ask

from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.calculus import binary_product_data, pair_maps
from sage_categories.cat.constructions import constructed_data
from sage_categories.cat.diagrams import cospan_diagram
from sage_categories.cat.functors import Fun, Functor
from sage_categories.cat.morphisms import Mor, MorphismCategory
from sage_categories.cat.predicates import (
    Predicate,
    Proposition,
    Unknown,
    ask,
    register_handler,
)
from sage_categories.kernel.refinement import refine
from sage_categories.kernel.retention import identity_key
from sage_categories.kernel.sage_runtime import cached_function, cached_method


class _RelationInclusion(Predicate):
    name = "relation_inclusion"


relation_inclusion: Predicate = _RelationInclusion()


class RelationsCategory(
    Category[[MorphismCategory.ObjectType], [MorphismCategory.ObjectType]]
):
    class ObjectType:
        def __init__(self, carrier: CategoryOfCategories.ElementType) -> None:
            self._relation_carrier = carrier

        def carrier(self) -> CategoryOfCategories.ElementType:
            return self._relation_carrier

    class ElementType:
        pass

    class MorphismType:
        def __init__(self, subobject: CategoryOfCategories.ElementType) -> None:
            self._relation_subobject = subobject

        def subobject(self) -> CategoryOfCategories.ElementType:
            return self._relation_subobject

        def monomorphism(self) -> MorphismCategory.ObjectType:
            return self.subobject().arrow()

        def left(self) -> MorphismCategory.ObjectType:
            return (
                binary_product_data(
                    self.base_category().regular_category(),
                    self.domain().carrier(),
                    self.codomain().carrier(),
                ).leg(0)
                * self.monomorphism()
            )

        def right(self) -> MorphismCategory.ObjectType:
            return (
                binary_product_data(
                    self.base_category().regular_category(),
                    self.domain().carrier(),
                    self.codomain().carrier(),
                ).leg(1)
                * self.monomorphism()
            )

        def converse(self) -> MorphismCategory.ObjectType:
            base = self.base_category().regular_category()
            mono = pair_maps(base, self.right(), self.left())
            refine(mono, Mor(base).Monomorphisms())
            return self.base_category().construct_morphism(
                self.codomain(), self.domain(), mono
            )

        def leq(self, other: MorphismCategory.ObjectType) -> Proposition:
            return relation_inclusion(self, other)

        def is_reflexive(self) -> Proposition:
            assert self.domain() is self.codomain()
            return (
                Mor(self.base_category())(self.domain(), self.domain()).one().leq(self)
            )

        def is_transitive(self) -> Proposition:
            assert self.domain() is self.codomain()
            return (self * self).leq(self)

        def is_antisymmetric(self) -> Proposition:
            assert self.domain() is self.codomain()
            return (
                self.base_category()
                .meet(self, self.converse())
                .leq(Mor(self.base_category())(self.domain(), self.domain()).one())
            )

    def __init__(self, base: Category) -> None:
        self._regular_category = base
        super().__init__()
        register_handler(self.equality(), self._equal_relations)

    def regular_category(self) -> Category:
        return self._regular_category

    @cached_method(key=identity_key)
    def __call__(
        self, carrier: CategoryOfCategories.ElementType
    ) -> RelationsCategory.ObjectType:
        assert carrier in self._regular_category
        return self.ObjectType(carrier)

    def morphism_category_type(self) -> type[RelationMorphismsCategory]:
        return RelationMorphismsCategory

    def construct_morphism(
        self,
        source: CategoryOfCategories.ElementType,
        target: CategoryOfCategories.ElementType,
        mono: MorphismCategory.ObjectType,
    ) -> RelationsCategory.MorphismType:
        base = self._regular_category
        product = base.Products()((source.carrier(), target.carrier()))
        assert mono.codomain() is product and mono in Mor(base).Monomorphisms()
        return self.MorphismType(
            domain=source, codomain=target, data=base.Subobjects(product)(mono)
        )

    def graph(self, arrow: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        base = self._regular_category
        mono = pair_maps(base, Mor(base)(arrow.domain(), arrow.domain()).one(), arrow)
        refine(mono, Mor(base).Monomorphisms())
        return self.construct_morphism(
            self(arrow.domain()), self(arrow.codomain()), mono
        )

    def construct_identity(
        self, value: CategoryOfCategories.ElementType
    ) -> MorphismCategory.ObjectType:
        return self.graph(
            Mor(self._regular_category)(value.carrier(), value.carrier()).one()
        )

    @cached_method(key=identity_key)
    def composite(
        self, second: MorphismCategory.ObjectType, first: MorphismCategory.ObjectType
    ) -> MorphismCategory.ObjectType:
        base = self._regular_category
        pullback = constructed_data(
            base.Pullbacks(), cospan_diagram(base, first.right(), second.left())
        )
        arrow = pair_maps(
            base, first.left() * pullback.leg(0), second.right() * pullback.leg(1)
        )
        surjection, mono = base.image_factorization(arrow)
        return self.construct_morphism(first.domain(), second.codomain(), mono)

    def meet(
        self, first: MorphismCategory.ObjectType, second: MorphismCategory.ObjectType
    ) -> MorphismCategory.ObjectType:
        assert (
            first.domain() is second.domain() and first.codomain() is second.codomain()
        )
        base = self._regular_category
        pullback = constructed_data(
            base.Pullbacks(),
            cospan_diagram(base, first.monomorphism(), second.monomorphism()),
        )
        mono = first.monomorphism() * pullback.leg(0)
        refine(mono, Mor(base).Monomorphisms())
        return self.construct_morphism(first.domain(), first.codomain(), mono)

    def _equal_relations(
        self,
        first: RelationsCategory.MorphismType,
        second: RelationsCategory.MorphismType,
        assumptions: Proposition,
    ) -> bool | None:
        return sympy_ask(first.leq(second) & second.leq(first), assumptions)

    def construct_two_morphism(
        self,
        first: MorphismCategory.ObjectType,
        second: MorphismCategory.ObjectType,
        factor: MorphismCategory.ObjectType,
    ) -> MorphismCategory.ObjectType:
        assert (
            first.domain() is second.domain() and first.codomain() is second.codomain()
        )
        assert factor in Mor(self._regular_category)(
            first.monomorphism().domain(), second.monomorphism().domain()
        )
        assert ask(second.monomorphism() * factor == first.monomorphism()) is True
        return self.morphism_category(2).ObjectType(
            domain=first, codomain=second, data=factor
        )

    def identity_two_morphism(
        self, arrow: MorphismCategory.ObjectType
    ) -> MorphismCategory.ObjectType:
        carrier = arrow.monomorphism().domain()
        return self.construct_two_morphism(
            arrow, arrow, Mor(self._regular_category)(carrier, carrier).one()
        )

    def compose_two_morphisms(
        self, second: MorphismCategory.ObjectType, first: MorphismCategory.ObjectType
    ) -> MorphismCategory.ObjectType:
        return self.construct_two_morphism(
            first.domain(), second.codomain(), second.factor() * first.factor()
        )

    def inclusion(
        self, first: MorphismCategory.ObjectType, second: MorphismCategory.ObjectType
    ) -> MorphismCategory.ObjectType:
        factor = self._regular_category.factor_through_monomorphism(
            second.monomorphism(), first.monomorphism()
        )
        assert factor is not False and factor is not Unknown
        return self.construct_two_morphism(first, second, factor)

    def horizontal_composite(
        self, second: MorphismCategory.ObjectType, first: MorphismCategory.ObjectType
    ) -> MorphismCategory.ObjectType:
        """Monotonicity of relational composition, as a horizontal composite of inclusions."""
        return self.inclusion(
            second.domain() * first.domain(), second.codomain() * first.codomain()
        )

    def associator(
        self,
        third: MorphismCategory.ObjectType,
        second: MorphismCategory.ObjectType,
        first: MorphismCategory.ObjectType,
    ) -> MorphismCategory.ObjectType:
        source, target = (third * second) * first, third * (second * first)
        forward, inverse = (
            self.inclusion(source, target),
            self.inclusion(target, source),
        )
        self.morphism_category(1).retain_inverses(forward, inverse)
        return forward

    @cached_method
    def graph_functor(self) -> Functor:
        return Fun(self._regular_category, self)(self, self.graph)


class RelationMorphismsCategory(MorphismCategory):
    ObjectType = RelationsCategory.MorphismType

    class ElementType:
        pass

    class MorphismType:
        def __init__(self, factor: MorphismCategory.ObjectType) -> None:
            self._relation_factor = factor

        def factor(self) -> MorphismCategory.ObjectType:
            return self._relation_factor


def _included(
    first: RelationsCategory.MorphismType,
    second: RelationsCategory.MorphismType,
    assumptions: Proposition,
) -> bool | None:
    if (
        first.domain() is not second.domain()
        or first.codomain() is not second.codomain()
    ):
        return False
    factor = (
        first.base_category()
        .regular_category()
        .factor_through_monomorphism(second.monomorphism(), first.monomorphism())
    )
    return None if factor is Unknown else factor is not False


register_handler(relation_inclusion, _included)


@cached_function(key=identity_key)
def Relations(base: Category) -> RelationsCategory:
    """The locally ordered bicategory of relations in the supplied regular category."""
    return RelationsCategory(base)
