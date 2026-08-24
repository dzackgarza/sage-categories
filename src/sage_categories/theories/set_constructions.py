"""The owned category of sets and functions.

This module migrates the mathematical ownership from
``dzack_research.preamble.categories.sets``. It uses only the owned
categorical foundation. Sage is not part of this category graph.
"""

from __future__ import annotations

from collections.abc import Callable

from sage_categories.abstract_categories.functors import (
    DiscreteCategories,
    DiscreteObject,
    Functor,
    NaturalTransformation,
)
from sage_categories.abstract_categories.functors import (
    DiscreteCategory as DiscreteCategoryObject,
)
from sage_categories.abstract_categories.products import (
    Cocone,
    CoconeObject,
    Cone,
    ConeObject,
    Coproduct,
    CoproductPresentation,
    Product,
    ProductPresentation,
)
from sage_categories.theories.cardinals import (
    Cardinal,
    Cardinals,
    UnknownCardinality,
)
from sage_categories.theories.discrete_sets import (
    DiscreteCategory,
    SetFamily,
)
from sage_categories.theories.set_category import (
    FiniteSet,
    Sets,
    _set_morphism,
    is_set_hom_category,
)
from sage_categories.theories.set_colimits import (
    ColimitElements,
    ColimitSet,
    _object_set_element,
)
from sage_categories.theories.set_coproducts import (
    CoproductElements,
    CoproductSet,
    SetCoproductObject,
    is_coproducts_of_sets_category,
)
from sage_categories.theories.set_elements import (
    SetElement,
    SetMorphismFamily,
)
from sage_categories.theories.set_homs import (
    SetHomCategory,
)
from sage_categories.theories.set_limits import (
    LimitSet,
)
from sage_categories.theories.set_objects import (
    FiniteSetObject,
    SetObject,
)
from sage_categories.theories.set_products import (
    ProductSet,
    SetProductObject,
    is_products_of_sets_category,
)
from sage_categories.theories.set_subobjects import (
    SetMorphism,
)
from sage_categories.values import (
    Arrow,
    MathematicalObject,
)


def ProductOfSets(
    diagram: Functor,
) -> ProductPresentation:
    from sage_categories.theories.set_colimits import _indexed_product_cardinality

    assert diagram.codomain() is Sets()
    cardinality = _indexed_product_cardinality(
        diagram.domain().label_set(),
        lambda index: diagram(diagram.domain().object(index)),
    )
    apex = ProductSet(
        diagram,
        category=Sets(),
        cardinality=cardinality,
    )
    return _product_presentation(diagram, apex)


def _product_presentation(
    diagram: Functor,
    apex: ProductSet,
) -> ProductPresentation:
    assert apex.diagram() is diagram

    def projection(index: MathematicalObject) -> Arrow:
        index_category = diagram.domain()
        assert DiscreteCategories().contains_discrete_category(index_category)
        assert index_category.contains_object(index)
        return apex._projection(index.label())

    cone = Cone(diagram, apex, projection)

    def mediate(other: ConeObject) -> Arrow:
        source = other.apex()
        assert Sets().contains_set(source)
        return _set_morphism(
            source,
            apex,
            lambda member: apex.element(
                lambda index: _cone_component_value(
                    other,
                    apex.index_category().object(index),
                    member,
                )
            ),
        )

    return Product(cone, mediate)


def _cone_component_value(
    cone: ConeObject,
    index: MathematicalObject,
    member: SetElement,
) -> SetElement:
    component = cone.structure_morphism(index)
    assert Sets().contains_set_morphism(component)
    return component(member)


def _CoproductPresentationOfSets(
    diagram: Functor,
    *,
    cardinality: Cardinal | None = None,
) -> CoproductPresentation:
    assert diagram.codomain() is Sets()
    apex = CoproductSet(
        diagram,
        category=Sets(),
        cardinality=cardinality,
    )
    return _coproduct_presentation(diagram, apex)


def _coproduct_presentation(
    diagram: Functor,
    apex: CoproductSet,
) -> CoproductPresentation:
    assert apex.diagram() is diagram

    def injection(index: MathematicalObject) -> Arrow:
        index_category = diagram.domain()
        assert DiscreteCategories().contains_discrete_category(index_category)
        assert index_category.contains_object(index)
        return apex._injection(index.label())

    cocone = Cocone(diagram, apex, injection)

    def mediate(other: CoconeObject) -> Arrow:
        target = other.apex()
        assert Sets().contains_set(target)

        def induced(member: SetElement) -> SetElement:
            assert CoproductElements().contains_coproduct_element(member)
            component = other.costructure_morphism(apex.index_category().object(member.index()))
            assert Sets().contains_set_morphism(component)
            return component(member.value())

        return _set_morphism(apex, target, induced)

    return Coproduct(cocone, mediate)


def LimitOfSets(
    diagram: Functor,
) -> ProductPresentation:
    return LimitOfSetsWithCardinality(diagram, UnknownCardinality())


def LimitOfSetsWithCardinality(
    diagram: Functor,
    cardinality: Cardinal,
) -> ProductPresentation:
    assert diagram.codomain() is Sets()
    apex = LimitSet(
        diagram,
        category=Sets(),
        cardinality=cardinality,
    )
    return _limit_presentation(diagram, apex)


def _limit_presentation(
    diagram: Functor,
    apex: LimitSet,
) -> ProductPresentation:
    assert apex.diagram() is diagram
    cone = Cone(
        diagram,
        apex,
        lambda index: apex._limit_projection(index),
    )

    def mediate(other: ConeObject) -> Arrow:
        source = other.apex()
        assert Sets().contains_set(source)
        return _set_morphism(
            source,
            apex,
            lambda member: apex._compatible_element(
                lambda index: _cone_component_value(
                    other,
                    index.value(),
                    member,
                )
            ),
        )

    return Product(cone, mediate)


def ColimitOfSets(
    diagram: Functor,
) -> CoproductPresentation:
    return ColimitOfSetsWithCardinality(diagram, UnknownCardinality())


def ColimitOfSetsWithCardinality(
    diagram: Functor,
    cardinality: Cardinal,
) -> CoproductPresentation:
    assert diagram.codomain() is Sets()
    apex = ColimitSet(
        diagram,
        category=Sets(),
        cardinality=cardinality,
    )
    return _colimit_presentation(diagram, apex)


def _colimit_presentation(
    diagram: Functor,
    apex: ColimitSet,
) -> CoproductPresentation:
    assert apex.diagram() is diagram

    def injection(index: MathematicalObject) -> Arrow:
        return apex._injection(_object_set_element(diagram.domain(), index))

    cocone = Cocone(diagram, apex, injection)

    def mediate(other: CoconeObject) -> Arrow:
        target = other.apex()
        assert Sets().contains_set(target)

        def induced(member: SetElement) -> SetElement:
            assert ColimitElements().contains_colimit_element(member)
            representative = member.representative()
            component = other.costructure_morphism(representative.index().value())
            assert Sets().contains_set_morphism(component)
            return component(representative.value())

        return _set_morphism(apex, target, induced)

    return Coproduct(cocone, mediate)


def CartesianProductOfSets(
    factors: tuple[SetObject, ...],
) -> SetProductObject:
    labels = _finite_ordinal(len(factors))
    index = DiscreteCategory(labels)

    def factor(value: DiscreteObject) -> SetObject:
        from sage_categories.theories.ordinals import Ordinals

        label = value.label()
        ordinal_index = label.value()
        assert Ordinals().contains_ordinal(ordinal_index)
        return factors[ordinal_index.finite_value()]

    diagram = SetFamily(index, factor)
    size = Cardinals().product(*(factor.cardinality() for factor in factors))
    products = Sets().Products(index)
    assert is_products_of_sets_category(products)
    image = products(diagram)
    return image


def CartesianProductOfFamily(
    index_set: SetObject,
    factors: Callable[[SetElement], SetObject],
) -> SetProductObject:
    index_category = DiscreteCategory(index_set)
    diagram = SetFamily(
        index_category,
        lambda index: factors(index.label()),
    )
    products = Sets().Products(index_category)
    assert is_products_of_sets_category(products)
    image = products(diagram)
    return image


def CartesianProductMorphismOfFamily(
    index_category: DiscreteCategoryObject,
    functions: SetMorphismFamily,
) -> SetMorphism:
    def function(index: DiscreteObject) -> SetMorphism:
        value = functions(index)
        assert Sets().contains_set_morphism(value)
        return value

    def domain(index: DiscreteObject) -> SetObject:
        value = function(index).domain()
        assert Sets().contains_set(value)
        return value

    def codomain(index: DiscreteObject) -> SetObject:
        value = function(index).codomain()
        assert Sets().contains_set(value)
        return value

    source = SetFamily(index_category, domain)
    target = SetFamily(index_category, codomain)

    def component(index: MathematicalObject) -> Arrow:
        assert index_category.contains_object(index)
        return function(index)

    transformation = NaturalTransformation(
        source,
        target,
        component,
    )
    products = Sets().Products(index_category)
    assert is_products_of_sets_category(products)
    products(source)
    products(target)
    image = Sets().ProductFunctor(index_category)(transformation)
    assert Sets().contains_set_morphism(image)
    return image


def _domain_cardinality(morphism: SetMorphism) -> Cardinal:
    domain = morphism.domain()
    assert Sets().contains_set(domain)
    return domain.cardinality()


def _codomain_cardinality(morphism: SetMorphism) -> Cardinal:
    codomain = morphism.codomain()
    assert Sets().contains_set(codomain)
    return codomain.cardinality()


def cartesian_product_morphism(*functions: SetMorphism) -> SetMorphism:
    labels = _finite_ordinal(len(functions))
    index_category = DiscreteCategory(labels)

    def function(index: DiscreteObject) -> SetMorphism:
        from sage_categories.theories.ordinals import Ordinals

        label = index.label()
        ordinal_index = label.value()
        assert Ordinals().contains_ordinal(ordinal_index)
        value = functions[ordinal_index.finite_value()]
        assert Sets().contains_set_morphism(value)
        return value

    return CartesianProductMorphismOfFamily(
        index_category,
        function,
    )


def DisjointUnionOfSets(
    cofactors: tuple[SetObject, ...],
) -> SetCoproductObject:
    labels = _finite_ordinal(len(cofactors))
    index = DiscreteCategory(labels)

    def cofactor(value: DiscreteObject) -> SetObject:
        from sage_categories.theories.ordinals import Ordinals

        label = value.label()
        ordinal_index = label.value()
        assert Ordinals().contains_ordinal(ordinal_index)
        return cofactors[ordinal_index.finite_value()]

    diagram = SetFamily(index, cofactor)
    coproducts = Sets().Coproducts(index)
    assert is_coproducts_of_sets_category(coproducts)
    image = coproducts(
        diagram,
        cardinality=Cardinals().sum(*(cofactor.cardinality() for cofactor in cofactors)),
    )
    return image


def CoproductOfSets(
    cofactors: tuple[SetObject, ...],
) -> SetCoproductObject:
    return DisjointUnionOfSets(cofactors)


def CoproductOfFamily(
    index_set: SetObject,
    cofactors: Callable[[SetElement], SetObject],
    *,
    cardinality: Cardinal | None = None,
) -> SetCoproductObject:
    index_category = DiscreteCategory(index_set)
    diagram = SetFamily(
        index_category,
        lambda index: cofactors(index.label()),
    )
    coproducts = Sets().Coproducts(index_category)
    assert is_coproducts_of_sets_category(coproducts)
    image = coproducts(diagram, cardinality=cardinality)
    return image


def CoproductMorphismOfFamily(
    index_category: DiscreteCategoryObject,
    functions: SetMorphismFamily,
    *,
    domain_cardinality: Cardinal | None = None,
    codomain_cardinality: Cardinal | None = None,
) -> SetMorphism:
    def function(index: DiscreteObject) -> SetMorphism:
        value = functions(index)
        assert Sets().contains_set_morphism(value)
        return value

    def domain(index: DiscreteObject) -> SetObject:
        value = function(index).domain()
        assert Sets().contains_set(value)
        return value

    def codomain(index: DiscreteObject) -> SetObject:
        value = function(index).codomain()
        assert Sets().contains_set(value)
        return value

    source = SetFamily(index_category, domain)
    target = SetFamily(index_category, codomain)

    def component(index: MathematicalObject) -> Arrow:
        assert index_category.contains_object(index)
        return function(index)

    transformation = NaturalTransformation(
        source,
        target,
        component,
    )
    coproducts = Sets().Coproducts(index_category)
    assert is_coproducts_of_sets_category(coproducts)
    coproducts(source, cardinality=domain_cardinality)
    coproducts(target, cardinality=codomain_cardinality)
    image = Sets().CoproductFunctor(index_category)(transformation)
    assert Sets().contains_set_morphism(image)
    return image


def coproduct_morphism(*functions: SetMorphism) -> SetMorphism:
    labels = _finite_ordinal(len(functions))
    index_category = DiscreteCategory(labels)

    def function(index: DiscreteObject) -> SetMorphism:
        from sage_categories.theories.ordinals import Ordinals

        label = index.label()
        ordinal_index = label.value()
        assert Ordinals().contains_ordinal(ordinal_index)
        value = functions[ordinal_index.finite_value()]
        assert Sets().contains_set_morphism(value)
        return value

    return CoproductMorphismOfFamily(
        index_category,
        function,
        domain_cardinality=Cardinals().sum(*(_domain_cardinality(morphism) for morphism in functions)),
        codomain_cardinality=Cardinals().sum(*(_codomain_cardinality(morphism) for morphism in functions)),
    )


def ExponentialOfSets(codomain: SetObject, exponent: SetObject) -> SetHomCategory:
    category = Sets().Hom(exponent, codomain)
    assert is_set_hom_category(category)
    return category


def _finite_ordinal(number_of_members: int) -> FiniteSetObject:
    from sage_categories.theories.ordinals import ordinal

    assert number_of_members >= 0
    return FiniteSet(ordinal(index) for index in range(number_of_members))


def TruthValues() -> FiniteSetObject:
    return _finite_ordinal(2)


def PowerSet(base_set: SetObject) -> SetHomCategory:
    return ExponentialOfSets(TruthValues(), base_set)
