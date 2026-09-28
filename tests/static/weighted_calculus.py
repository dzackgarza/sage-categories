"""The weighted/separating calculus keeps its public functor and morphism types."""

from typing import assert_type

from sage_categories.all import (
    Representations as public_representations,
)
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
    Representations,
    RepresentationsCategory,
    coyoneda,
    restricted_yoneda,
    separating_evaluation,
    separating_evaluation_injection,
    weighted_colimit_map,
    weighted_limit_map,
    yoneda,
)


def weighted_calculus_types(
    test: Functor,
    hom: Functor,
    transformation: NaturalTransformation,
    value: CategoryOfCategories.ElementType,
    probe_point: CategoryOfCategories.ElementType,
    hom_point: CategoryOfCategories.ElementType,
) -> None:
    assert_type(coyoneda(test.domain(), hom.codomain()), Functor)
    assert_type(coyoneda(test.domain(), hom.codomain(), hom), Functor)
    assert_type(yoneda(test.domain(), hom.codomain(), hom), Functor)
    assert_type(Representations(test), RepresentationsCategory)
    assert_type(Representations(test, hom), RepresentationsCategory)
    assert_type(public_representations(test), RepresentationsCategory)
    assert_type(public_representations(test, hom), RepresentationsCategory)
    assert_type(restricted_yoneda(test, hom), Functor)
    assert_type(public_restricted_yoneda(test, hom), Functor)
    assert_type(test.restricted_yoneda(hom), Functor)
    assert_type(weighted_limit_map(test, transformation), MorphismCategory.ObjectType)
    assert_type(weighted_colimit_map(test, transformation), MorphismCategory.ObjectType)
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
