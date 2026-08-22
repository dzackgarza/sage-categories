"""``Cat``: the category whose objects are categories."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeIs

from sage_categories.category import Category
from sage_categories.values import (
    Arrow,
    MathematicalElement,
    MathematicalObject,
    MembershipInput,
    registered_value,
)

if TYPE_CHECKING:
    from sage_categories.abstract_categories.functors import Functor
    from sage_categories.abstract_categories.hom_categories import HomCategory
    from sage_categories.abstract_categories.products import (
        ConeObject,
        ProductPresentation,
    )


class CategoryOfCategories(Category):
    """The represented universe of categories."""

    def __init__(
        self,
        *,
        category: CategoryOfCategories | None,
        name: str,
    ) -> None:
        self._name = name
        MathematicalObject.__init__(self, category=category)
        self._initialize_category(Category, MathematicalElement)

    def _hom_category_type(self) -> type[HomCategory]:
        from sage_categories.abstract_categories.functors import FunctorCategory

        return FunctorCategory

    def __contains__(self, candidate: MembershipInput) -> bool:
        value = registered_value(candidate)
        return value is not None and value._belongs_to(self)

    def contains_category(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[Category]:
        """Return whether ``candidate`` is an object of ``Cat``."""
        return candidate in self

    def _belongs_to(self, category: Category) -> bool:
        return Category._belongs_to(self, category)

    def chosen_limit(self, diagram: Functor) -> ProductPresentation:
        """Construct the strict pullback of one cospan in ``Cat``."""
        from sage_categories.abstract_categories.category_constructions import (
            PullbackCategory,
        )
        from sage_categories.abstract_categories.functors import (
            compose_functors,
            is_functor,
        )
        from sage_categories.abstract_categories.products import (
            Cone,
            Product,
            is_diagram_category,
        )

        assert diagram.codomain() is self
        index = diagram.domain()
        assert is_diagram_category(index)
        morphisms = index.diagram_morphisms()
        assert len(morphisms) == 2
        first, second = morphisms
        assert is_functor(first)
        assert is_functor(second)
        assert first.codomain() is second.codomain()
        assert first.domain() is not second.domain()
        pullback = PullbackCategory(first, second)
        first_projection = pullback.first_projection()
        second_projection = pullback.second_projection()
        common_projection = compose_functors(first, first_projection)

        def component(value: MathematicalObject) -> Arrow:
            if value is first.domain():
                return first_projection
            if value is second.domain():
                return second_projection
            assert value is first.codomain()
            return common_projection

        cone = Cone(diagram, pullback, component)

        def mediate(source_cone: ConeObject) -> Arrow:
            assert source_cone.diagram() is diagram
            left = source_cone.structure_morphism(first.domain())
            right = source_cone.structure_morphism(second.domain())
            assert is_functor(left)
            assert is_functor(right)
            return pullback.mediating_functor(left, right)

        return Product(cone, mediate)

    def __repr__(self) -> str:
        return self._name


_LARGE_CAT = CategoryOfCategories(category=None, name="CAT")
_CAT = CategoryOfCategories(category=_LARGE_CAT, name="Cat")


def Cat() -> CategoryOfCategories:
    """Return the category of categories."""
    return _CAT


def category_universe(
    domain: Category,
    codomain: Category,
) -> CategoryOfCategories:
    """Return the smallest represented universe containing two categories."""
    if domain in _CAT and codomain in _CAT:
        return _CAT
    assert domain in _LARGE_CAT and codomain in _LARGE_CAT
    return _LARGE_CAT


def category_universes() -> tuple[CategoryOfCategories, ...]:
    """Return the represented cumulative category universes."""
    return _CAT, _LARGE_CAT


def is_category_of_categories(
    category: Category,
) -> TypeIs[CategoryOfCategories]:
    return category is _CAT or category is _LARGE_CAT


def is_category(candidate: MathematicalObject) -> TypeIs[Category]:
    return any(universe.contains_category(candidate) for universe in category_universes())
