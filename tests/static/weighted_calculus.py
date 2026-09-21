"""The weighted/separating calculus keeps its public functor and morphism types."""

from typing import assert_type

from sage_categories.all import (
    restricted_yoneda as public_restricted_yoneda,
)
from sage_categories.all import (
    separating_evaluation as public_separating_evaluation,
)
from sage_categories.all import (
    separating_evaluation_injection as public_separating_evaluation_injection,
)
from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.functors import Functor, NaturalTransformation
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.weighted import (
    restricted_yoneda,
    separating_evaluation,
    separating_evaluation_injection,
)


def weighted_calculus_types(
    test: Functor,
    hom: Functor,
    value: CategoryOfCategories.ElementType,
    probe_point: CategoryOfCategories.ElementType,
    hom_point: CategoryOfCategories.ElementType,
) -> None:
    assert_type(restricted_yoneda(test, hom), Functor)
    assert_type(public_restricted_yoneda(test, hom), Functor)
    assert_type(test.restricted_yoneda(hom), Functor)
    assert_type(separating_evaluation(test, hom), NaturalTransformation)
    assert_type(public_separating_evaluation(test, hom), NaturalTransformation)
    assert_type(test.separating_evaluation(hom), NaturalTransformation)
    assert_type(
        separating_evaluation_injection(
            test,
            hom,
            value,
            probe_point,
            hom_point,
        ),
        MorphismCategory.ObjectType,
    )
    assert_type(
        public_separating_evaluation_injection(
            test,
            hom,
            value,
            probe_point,
            hom_point,
        ),
        MorphismCategory.ObjectType,
    )
