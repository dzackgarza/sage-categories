"""The owned category of sets and functions.

This module migrates the mathematical ownership from
``dzack_research.preamble.categories.sets``. It uses only the owned
categorical foundation. Sage is not part of this category graph.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sage_categories.abstract_categories.category_constructions import (
    is_opposite_arrow,
    is_product_arrow,
    is_product_category,
)
from sage_categories.abstract_categories.functors import (
    Functor,
)
from sage_categories.theories.cardinals import (
    Cardinal,
    Cardinals,
    is_cardinal_hom_category,
)
from sage_categories.theories.set_elements import (
    SetElement,
)
from sage_categories.theories.set_homs import (
    SetHomCategory,
)
from sage_categories.values import (
    Arrow,
    MathematicalObject,
)

if TYPE_CHECKING:
    from sage_categories.theories.set_category import (
        SetsCategory,
    )
    from sage_categories.theories.set_subobjects import SetMorphism


class CardinalityFunctor(Functor):
    """The cardinality functor from the core of ``Sets`` to ``Cardinals``."""

    def __init__(self, sets: SetsCategory) -> None:

        self._sets = sets
        super().__init__(sets.core(), Cardinals())

    def _object_image(self, source: MathematicalObject) -> Cardinal:
        assert source in self.domain()
        assert self._sets.contains_set(source)
        return source.cardinality()

    def _morphism_image(self, morphism: Arrow) -> Arrow:
        assert morphism in self.domain().ArrowCategory()
        source = morphism.domain()
        target = morphism.codomain()
        assert self._sets.contains_set(source)
        assert self._sets.contains_set(target)
        source_cardinality = source.cardinality()
        target_cardinality = target.cardinality()
        assert source_cardinality == target_cardinality
        hom_category = Cardinals().Hom(source_cardinality, target_cardinality)
        assert is_cardinal_hom_category(hom_category)
        return hom_category()


class ExponentialFunctor(Functor):
    """The internal-hom bifunctor ``Sets^op x Sets -> Sets``."""

    def __init__(self) -> None:
        from sage_categories.theories.set_category import Sets

        super().__init__(Sets().OppositeCategory().ProductCategory(Sets()), Sets())

    def _object_image(self, source: MathematicalObject) -> SetHomCategory:
        from sage_categories.theories.set_category import Sets
        from sage_categories.theories.set_constructions import ExponentialOfSets

        domain = self.domain()
        assert is_product_category(domain)
        assert domain.contains_pair(source)
        exponent = source.first()
        base = source.second()
        assert Sets().contains_set(exponent)
        assert Sets().contains_set(base)
        return ExponentialOfSets(base, exponent)

    def _morphism_image(self, morphism: Arrow) -> SetMorphism:
        from sage_categories.theories.set_category import (
            Sets,
            _set_morphism,
            is_set_hom_category,
        )

        assert is_product_arrow(morphism)
        first = morphism.first()
        second = morphism.second()
        assert is_opposite_arrow(first)
        precompose = first.underlying_arrow()
        assert Sets().contains_set_morphism(precompose)
        assert Sets().contains_set_morphism(second)
        source = self(morphism.domain())
        target = self(morphism.codomain())
        assert is_set_hom_category(source)
        assert is_set_hom_category(target)

        def transport(candidate: SetElement) -> SetMorphism:
            from sage_categories.theories.set_category import Sets

            assert Sets().contains_set_morphism(candidate)
            return target(lambda member: second(candidate(precompose(member))))

        return _set_morphism(source, target, transport)


class InverseImagePowerSetFunctor(Functor):
    """The contravariant power-set functor ``Sets^op -> Sets``."""

    def __init__(self) -> None:
        from sage_categories.theories.set_category import Sets

        super().__init__(Sets().OppositeCategory(), Sets())

    def _object_image(self, source: MathematicalObject) -> SetHomCategory:
        from sage_categories.theories.set_category import Sets
        from sage_categories.theories.set_constructions import PowerSet

        assert Sets().contains_set(source)
        return PowerSet(source)

    def _morphism_image(self, morphism: Arrow) -> SetMorphism:
        from sage_categories.theories.set_category import (
            Sets,
            is_set_hom_category,
        )

        assert is_opposite_arrow(morphism)
        underlying = morphism.underlying_arrow()
        assert Sets().contains_set_morphism(underlying)
        source = self(morphism.domain())
        assert is_set_hom_category(source)
        return source.inverse_image_morphism(underlying)
