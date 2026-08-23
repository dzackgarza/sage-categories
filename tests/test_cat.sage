"""The owned category of categories and its arrow categories."""

from sage_categories.all import *
from sage_categories.abstract_categories.functors import (
    is_functor,
    is_natural_transformation_hom_category,
)
from sage_categories.abstract_categories.hom_categories import is_isomorphism
from sage_categories.theories.posets import PosetElement, TotallyOrderedSetElements
from sage_categories.theories.sets import is_products_of_sets_category


def is_equal(left: PosetElement, right: PosetElement) -> bool:
    return left == right


def test_cat_owns_functors_and_natural_transformations() -> None:
    sets = Sets()
    finite_set = FiniteSet((ZZ(int(0)), ZZ(int(1))))

    assert sets in Cat()
    assert sets.Hom(finite_set, finite_set) in Cat()

    identity = IdentityFunctor(sets)
    composite = Cat().compose(identity, identity)
    assert composite in Cat().ArrowCategory()
    assert identity(finite_set) is finite_set

    transformations = NaturalTransformations(identity, identity)
    transformation = transformations(
        lambda source: sets.identity(source),
    )
    assert transformation.component(finite_set) in sets.Hom(
        finite_set,
        finite_set,
    )
    assert transformations.compose(
        transformation,
        transformation,
    ).component(finite_set) in sets.Hom(finite_set, finite_set)


def test_arrow_hom_end_iso_slice_and_coslice_categories() -> None:
    sets = Sets()
    finite_set = FiniteSet((ZZ(int(0)), ZZ(int(1))))
    identity = sets.Hom(finite_set, finite_set).identity()
    arrows = sets.ArrowCategory()

    assert arrows in Cat()
    assert identity in arrows
    assert arrows.Hom(identity, identity).identity() in arrows.ArrowCategory()
    assert sets.DomainFunctor()(identity) is finite_set
    assert sets.CodomainFunctor()(identity) is finite_set

    endomorphism = sets.End(finite_set).identity()
    monomorphism = sets.Mono(finite_set, finite_set).identity()
    epimorphism = sets.Epi(finite_set, finite_set).identity()
    automorphism = sets.Aut(finite_set).identity()
    assert endomorphism in sets.EndArrowCategory()
    assert monomorphism in sets.MonomorphismArrowCategory()
    assert epimorphism in sets.EpimorphismArrowCategory()
    assert automorphism in sets.AutomorphismArrowCategory()
    assert automorphism in sets.IsomorphismArrowCategory()
    assert automorphism in sets.core().ArrowCategory()

    slice = sets.SliceOver(finite_set)
    slice_object = slice(identity)
    assert slice_object in slice
    assert slice.Hom(
        slice_object,
        slice_object,
    ).identity() in slice.ArrowCategory()

    coslice = sets.CosliceUnder(finite_set)
    coslice_object = coslice(identity)
    assert coslice_object in coslice
    assert coslice.Hom(
        coslice_object,
        coslice_object,
    ).identity() in coslice.ArrowCategory()

    subobject = sets.Subobjects(finite_set)(monomorphism)
    superobject = sets.Superobjects(finite_set)(monomorphism)
    covering_object = sets.CoveringObjects(finite_set)(epimorphism)
    covered_object = sets.CoveredObjects(finite_set)(epimorphism)
    assert subobject in sets.Subobjects(finite_set)
    assert superobject in sets.Superobjects(finite_set)
    assert covering_object in sets.CoveringObjects(finite_set)
    assert covered_object in sets.CoveredObjects(finite_set)


def test_compiler_exposes_object_element_and_arrow_routes() -> None:
    category = FiniteTotallyOrderedSets()
    object_declaration = category.declared_object_methods()["cardinality"]
    iteration_declaration = category.declared_object_methods()["__iter__"]
    element_declaration = category.declared_element_methods()["__le__"]
    arrow_declaration = category.declared_arrow_methods()["is_injective"]
    ordered_set = finite_ordered_set((ZZ(int(0)), ZZ(int(1))))
    member = next(iter(ordered_set))
    finite_poset = category.finite_poset_functor()(ordered_set)
    assert FinitePosets().contains_finite_poset(finite_poset)

    assert object_declaration.owner is Sets()
    assert object_declaration.route
    assert iteration_declaration.owner is Sets()
    assert iteration_declaration.route
    assert element_declaration.owner is PartiallyOrderedSets()
    assert element_declaration.route
    assert arrow_declaration.owner is Sets()
    assert arrow_declaration.route
    assert TotallyOrderedSetElements().contains_total_order_element(member)
    assert ordered_set.category() is FiniteTotallyOrderedSets()
    assert FiniteTotallyOrderedSets().inclusion()(ordered_set) is ordered_set
    assert member.ambient_total_order() is ordered_set
    assert member <= member
    assert finite_poset.height() == 2


def test_structural_coherence_identifies_parallel_forgetful_functors() -> None:
    category = FiniteTotallyOrderedSets()
    ordered_set = finite_ordered_set((ZZ(int(0)), ZZ(int(1))))
    coherence, = category.structural_coherences()

    assert is_isomorphism(coherence)
    first = coherence.domain()
    second = coherence.codomain()
    assert is_functor(first)
    assert is_functor(second)
    assert first(ordered_set) is second(ordered_set)


def test_structural_functor_images_have_exact_ambient_objects_and_endpoints() -> None:
    poset = PartiallyOrderedSets()(ZZ, is_equal)
    element = poset.element(ZZ(int(0)))
    identity = PartiallyOrderedSets().identity(poset)
    forgetful = PartiallyOrderedSets().forgetful_functor()

    set_image = forgetful.on_object(poset)
    element_image = forgetful.on_element(poset, element)
    arrow_image = forgetful.on_morphism(identity)

    assert set_image is ZZ
    assert element_image.ambient_object() is set_image
    assert arrow_image.domain() is set_image
    assert arrow_image.codomain() is set_image


def test_postcomposition_maps_diagrams_and_natural_transformations() -> None:
    labels = FiniteSet((ZZ(int(3)), ZZ(int(5))))
    index_category = DiscreteCategory(labels)
    poset = PartiallyOrderedSets()(ZZ, is_equal)
    diagram = PartiallyOrderedSets().DiagonalFunctor(index_category)(poset)
    assert is_functor(diagram)
    identity = PartiallyOrderedSets().identity(poset)
    transformations = NaturalTransformations(diagram, diagram)
    transformation = transformations(lambda index: identity)
    forgetful = PartiallyOrderedSets().forgetful_functor()
    postcomposition = forgetful.postcomposition(index_category)

    set_diagram = postcomposition.on_object(diagram)
    set_transformation = postcomposition.on_morphism(transformation)
    assert is_functor(set_diagram)
    hom_category = set_transformation.hom_category()
    assert is_natural_transformation_hom_category(hom_category)
    assert hom_category.contains_transformation(set_transformation)
    index = index_category.object(labels.element(ZZ(int(3))))
    component = set_transformation.component(index)

    assert set_diagram(index) is ZZ
    assert Sets().contains_set_morphism(component)
    assert component.domain() is ZZ
    assert component.codomain() is ZZ
    assert component(ZZ(int(7))) is ZZ(int(7))


def test_poset_products_lift_products_of_underlying_sets() -> None:
    labels = FiniteSet((ZZ(int(0)), ZZ(int(1))))
    index_category = DiscreteCategory(labels)
    factor_set = FiniteSet((ZZ(int(0)), ZZ(int(1))))
    factor = finite_ordered_set((ZZ(int(0)), ZZ(int(1))))
    diagram = PartiallyOrderedSets().DiagonalFunctor(index_category)(factor)
    product = PartiallyOrderedSets().ProductFunctor(index_category)(diagram)
    assert PartiallyOrderedSets().contains_poset(product)

    forgetful = PartiallyOrderedSets().forgetful_functor()
    underlying_product = forgetful.on_object(product)
    assert Sets().contains_set(underlying_product)
    underlying_category = underlying_product.category()
    assert is_products_of_sets_category(underlying_category)
    assert underlying_category.contains_set_product(underlying_product)
    assert product.category().is_subcategory(underlying_category)

    set_zero = factor_set.element(ZZ(int(0)))
    set_one = factor_set.element(ZZ(int(1)))
    lower = product.element(underlying_product.element(lambda index: set_zero))
    upper = product.element(underlying_product.element(lambda index: set_one))

    assert lower <= upper
    assert (upper <= lower) is False
