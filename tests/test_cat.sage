"""The owned category of categories and its arrow categories."""

import operator

from sage_categories.all import *
from sage_categories.abstract_categories.category_constructions import (
    is_opposite_category,
    is_opposite_hom_category,
    is_product_category,
    is_product_hom_category,
)
from sage_categories.abstract_categories.functors import (
    ConstantDiagram,
    InclusionFunctor,
    compose_functors,
    is_functor,
    is_functor_category,
    is_natural_transformation_hom_category,
)
from sage_categories.abstract_categories.functor_images import (
    is_functor_image_category,
)
from sage_categories.abstract_categories.hom_categories import (
    is_isomorphism,
    is_isomorphism_hom_category,
)
from sage_categories.abstract_categories.products import (
    DiagramCategory,
    DirectedSystem,
    InverseSystem,
    is_coproducts_of_category,
    is_products_of_category,
)
from sage_categories.compiler import category_compiler
from sage_categories.theories.posets import (
    PosetElement,
    PosetObject,
    is_total_order_element,
    is_poset_hom_category,
)
from sage_categories.theories.sets import SetObject, is_products_of_sets_category


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
    assert is_isomorphism(automorphism)
    assert automorphism.is_monomorphism()
    assert automorphism.is_epimorphism()
    isomorphisms = sets.Iso(finite_set, finite_set)
    assert is_isomorphism_hom_category(isomorphisms)
    assert isomorphisms.contains_isomorphism(automorphism)

    assert sets.HomCatType is sets.HomCategory().ObjectType
    assert sets.EndCatType is sets.EndCategory().ObjectType
    assert sets.MonoCatType is sets.MonoCategory().ObjectType
    assert sets.EpiCatType is sets.EpiCategory().ObjectType
    assert sets.IsoCatType is sets.IsoCategory().ObjectType
    assert sets.AutCatType is sets.AutCategory().ObjectType

    slice = sets.SliceOver(finite_set)
    slice_object = slice(identity)
    assert slice_object in slice
    assert slice.target_object() is finite_set
    assert (
        slice.Hom(
            slice_object,
            slice_object,
        ).identity()
        in slice.ArrowCategory()
    )

    coslice = sets.CosliceUnder(finite_set)
    coslice_object = coslice(identity)
    assert coslice_object in coslice
    assert (
        coslice.Hom(
            coslice_object,
            coslice_object,
        ).identity()
        in coslice.ArrowCategory()
    )

    subobject = sets.Subobjects(finite_set)(monomorphism)
    superobject = sets.Superobjects(finite_set)(monomorphism)
    covering_object = sets.CoveringObjects(finite_set)(epimorphism)
    covered_object = sets.CoveredObjects(finite_set)(epimorphism)
    assert subobject in sets.Subobjects(finite_set)
    assert superobject in sets.Superobjects(finite_set)
    assert covering_object in sets.CoveringObjects(finite_set)
    assert covered_object in sets.CoveredObjects(finite_set)
    finite_epimorphism = FiniteSets().Epi(finite_set, finite_set).identity()
    finite_coverings = FiniteSets().CoveringObjects(finite_set)
    assert finite_set.covering_objects() is finite_coverings
    finite_covering_object = finite_coverings(finite_epimorphism)
    assert finite_covering_object in finite_coverings


def test_opposites_products_functor_images_and_constant_diagrams() -> None:
    sets = Sets()
    finite_set = FiniteSet((ZZ(int(0)), ZZ(int(1))))
    identity_functor = IdentityFunctor(sets)

    opposite = sets.OppositeCategory()
    assert is_opposite_category(opposite)
    opposite_hom = opposite.Hom(finite_set, finite_set)
    assert is_opposite_hom_category(opposite_hom)
    opposite_identity = opposite_hom.identity()
    assert opposite_hom.contains_opposite_arrow(opposite_identity)

    product_category = sets.ProductCategory(sets)
    assert is_product_category(product_category)
    pair = product_category(finite_set, finite_set)
    product_hom = product_category.Hom(pair, pair)
    assert is_product_hom_category(product_hom)
    product_identity = product_hom.identity()
    assert product_hom.contains_product_arrow(product_identity)

    pair_functor = product_category.pair_functor(
        identity_functor,
        identity_functor,
    )
    assert pair_functor(finite_set) is pair

    composite = identity_functor.then(identity_functor)
    assert composite(finite_set) is finite_set
    functor_category = sets.FunctorCategory(sets)
    assert is_functor_category(functor_category)
    assert functor_category.contains_functor(composite)

    labels = FiniteSet((ZZ(int(5)),))
    index_category = DiscreteCategory(labels)
    constant_diagram = ConstantDiagram(index_category, sets, finite_set)
    assert constant_diagram.constant_value() is finite_set

    image_category = sets.ImagesOfFunctor(identity_functor)
    assert is_functor_image_category(image_category)
    image = image_category(finite_set)
    assert image.constructing_functor() is identity_functor
    assert image_category.inclusion()(image) is finite_set


def test_directed_and_inverse_systems_retain_their_diagrams() -> None:
    finite_set = FiniteSet((ZZ(int(0)), ZZ(int(1))))
    index_set = finite_ordered_set((ZZ(int(0)), ZZ(int(1))))
    identity = Sets().identity(finite_set)
    directed = DirectedSystem(
        Sets(),
        index_set,
        (finite_set,),
        (identity,),
    )
    inverse = InverseSystem(
        Sets(),
        index_set,
        (finite_set,),
        (identity,),
    )

    assert directed.index_set() is index_set
    assert inverse.index_set() is index_set
    assert directed.diagram_objects() == (finite_set,)
    assert inverse.diagram_objects() == (finite_set,)
    assert directed.contains_arrow(identity)
    assert inverse.contains_arrow(identity)


def test_singleton_products_coproducts_and_biproduct_presentations() -> None:
    labels = FiniteSet((ZZ(int(0)),))
    index_category = DiscreteCategory(labels)
    factor = FiniteSet((ZZ(int(2)), ZZ(int(3))))
    diagram = Sets().DiagonalFunctor(index_category)(factor)
    assert is_functor(diagram)
    index = index_category.object(labels.element(ZZ(int(0))))
    identity = Sets().identity(factor)

    cone = Cone(diagram, factor, lambda candidate: identity)
    cocone = Cocone(diagram, factor, lambda candidate: identity)
    product = Product(
        cone,
        lambda other: other.structure_morphism(index),
    )
    coproduct = Coproduct(
        cocone,
        lambda other: other.costructure_morphism(index),
    )
    biproduct = Biproduct(product, coproduct)

    assert product.product_cone() is cone
    assert coproduct.coproduct_cocone() is cocone
    assert biproduct.product_presentation() is product
    assert biproduct.coproduct_presentation() is coproduct

    coproducts = Sets().Coproducts(index_category)
    assert is_coproducts_of_category(coproducts)
    chosen_coproduct = coproducts.coproduct_of(diagram)
    assert chosen_coproduct.diagram() is diagram


def test_compiler_exposes_object_element_and_arrow_routes() -> None:
    category = FiniteTotallyOrderedSets()
    ordered_set = finite_ordered_set((ZZ(int(0)), ZZ(int(1))))
    member = next(iter(ordered_set))
    assert is_total_order_element(member)
    assert member in ordered_set
    assert member <= member
    assert (ordered_set.cardinality() == 2) is True
    finite_poset = category.finite_poset_functor()(ordered_set)
    assert FinitePosets().contains_finite_poset(finite_poset)
    assert finite_poset.height() == 2
    assert ordered_set.category() is FiniteTotallyOrderedSets()
    assert member.ambient_total_order() is ordered_set


def test_structural_coherence_identifies_parallel_forgetful_functors() -> None:
    category = FiniteTotallyOrderedSets()
    ordered_set = finite_ordered_set((ZZ(int(0)), ZZ(int(1))))
    (coherence,) = category.structural_coherences()

    assert is_isomorphism(coherence)
    first = coherence.domain()
    second = coherence.codomain()
    assert is_functor(first)
    assert is_functor(second)
    assert first(ordered_set) is second(ordered_set)


def test_structural_functor_images_have_exact_ambient_objects_and_endpoints() -> None:
    poset = PartiallyOrderedSets()(ZZ, operator.eq, theorem="Discrete order on ZZ")
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
    poset = PartiallyOrderedSets()(ZZ, operator.eq, theorem="Discrete order on ZZ")
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


def test_generic_limit_functors_return_arrows_between_their_limit_objects() -> None:
    finite_sets = FiniteSets()
    posets = PartiallyOrderedSets()
    sets = Sets()
    index_category = DiagramCategory(
        Cat(),
        (finite_sets, posets, sets),
        (
            compose_functors(
                CountableSets().inclusion(),
                finite_sets.inclusion(),
            ),
            posets.forgetful_functor(),
        ),
    )
    diagram = InclusionFunctor(index_category, Cat())
    transformation = NaturalTransformations(diagram, diagram).identity()
    limit_functor = Cat().LimitFunctor(index_category)
    limit = limit_functor(diagram)
    image = limit_functor(transformation)

    assert Cat().contains_arrow(image)
    assert image.domain() is limit
    assert image.codomain() is limit


def test_poset_products_lift_products_of_underlying_sets() -> None:
    labels = FiniteSet((ZZ(int(0)), ZZ(int(1))))
    index_category = DiscreteCategory(labels)
    factor_set = FiniteSet((ZZ(int(0)), ZZ(int(1))))
    ordered_factor = finite_ordered_set((ZZ(int(0)), ZZ(int(1))))
    factor = TotallyOrderedSets().inclusion().on_object(ordered_factor)
    assert PartiallyOrderedSets().contains_poset(factor)
    diagram = PartiallyOrderedSets().DiagonalFunctor(index_category)(factor)
    assert is_functor(diagram)
    product = PartiallyOrderedSets().ProductFunctor(index_category)(diagram)
    assert PartiallyOrderedSets().contains_poset(product)
    product_category = product.category()
    assert is_products_of_category(product_category)
    assert product_category.contains_product(product)

    forgetful = PartiallyOrderedSets().forgetful_functor()
    underlying_product = forgetful.on_object(product)
    assert Sets().contains_set(underlying_product)
    underlying_category = underlying_product.category()
    assert is_products_of_sets_category(underlying_category)
    assert underlying_category.contains_set_product(underlying_product)

    set_zero = factor_set.element(ZZ(int(0)))
    set_one = factor_set.element(ZZ(int(1)))
    lower = product.element(underlying_product.element(lambda index: set_zero))
    upper = product.element(underlying_product.element(lambda index: set_one))

    assert lower <= upper
    assert (upper <= lower) is False

    first_index = index_category.object(labels.element(ZZ(int(0))))
    projection = product.projection(first_index)
    projection_hom = projection.hom_category()
    assert is_poset_hom_category(projection_hom)
    assert projection_hom.contains_poset_morphism(projection)
    first_factor = diagram(first_index)
    assert PartiallyOrderedSets().contains_poset(first_factor)
    assert projection(lower) is first_factor.element(set_zero)

    identity = PartiallyOrderedSets().identity(factor)
    cone = Cone(diagram, factor, lambda index: identity)
    diagonal = product.universal_morphism(cone)
    diagonal_hom = diagonal.hom_category()
    assert is_poset_hom_category(diagonal_hom)
    assert diagonal_hom.contains_poset_morphism(diagonal)
    factor_member = factor.element(set_one)
    diagonal_image = diagonal(factor_member)
    assert diagonal_image <= diagonal_image
    assert projection(diagonal_image) is first_factor.element(set_one)


def test_poset_structural_membership_and_iteration() -> None:
    ordered = finite_ordered_set((ZZ(int(10)), ZZ(int(20)), ZZ(int(30))))
    members = list(ordered)
    assert len(members) == 3
    for member in members:
        assert is_total_order_element(member)
        assert member in ordered
        assert member.ambient_object() is ordered
    a, b, c = members
    assert is_total_order_element(a)
    assert is_total_order_element(b)
    assert is_total_order_element(c)
    assert a <= b
    assert a < b
    assert b <= c
    assert (b <= a) is False
    assert (c < a) is False
    assert a <= a

    poset = TotallyOrderedSets().underlying_poset(ordered)
    poset_members = list(poset)
    assert len(poset_members) == 3
    for p_elem in poset_members:
        assert is_poset_element(p_elem)
        assert p_elem in poset


def test_rejection_of_invalid_partial_orders() -> None:
    non_reflexive_failed = False
    try:
        Poset(((ZZ(int(1)),), lambda x, y: False))
    except AssertionError:
        non_reflexive_failed = True
    assert non_reflexive_failed

    non_antisymmetric_failed = False
    try:
        Poset(((ZZ(int(1)), ZZ(int(2))), lambda x, y: True))
    except AssertionError:
        non_antisymmetric_failed = True
    assert non_antisymmetric_failed

    def non_trans_leq(left: SetElement, right: SetElement) -> bool:
        assert ZZ.contains_integer(left)
        assert ZZ.contains_integer(right)
        l_val = int(left)
        r_val = int(right)
        return (l_val == r_val) or (l_val == 1 and r_val == 2) or (l_val == 2 and r_val == 3)

    non_transitive_failed = False
    try:
        Poset(((ZZ(int(1)), ZZ(int(2)), ZZ(int(3))), non_trans_leq))
    except AssertionError:
        non_transitive_failed = True
    assert non_transitive_failed

    def unknown_leq(left: SetElement, right: SetElement) -> Decision:
        assert ZZ.contains_integer(left)
        assert ZZ.contains_integer(right)
        return True if int(left) == int(right) else UNKNOWN

    unknown_failed = False
    try:
        Poset(((ZZ(int(1)), ZZ(int(2))), unknown_leq))
    except AssertionError:
        unknown_failed = True
    assert unknown_failed


def test_totality_verification_and_rejection() -> None:
    def discrete_leq(left: SetElement, right: SetElement) -> bool:
        assert ZZ.contains_integer(left)
        assert ZZ.contains_integer(right)
        return int(left) == int(right)

    def chain_leq(left: SetElement, right: SetElement) -> bool:
        assert ZZ.contains_integer(left)
        assert ZZ.contains_integer(right)
        return int(left) <= int(right)

    discrete_poset = Poset(((ZZ(int(0)), ZZ(int(1))), discrete_leq))
    assert is_total_order(discrete_poset) is False
    assert discrete_poset in PartiallyOrderedSets()
    assert discrete_poset not in TotallyOrderedSets()

    refinement_failed = False
    try:
        TotallyOrderedSets()(discrete_poset)
    except AssertionError:
        refinement_failed = True
    assert refinement_failed

    chain = Poset(((ZZ(int(0)), ZZ(int(1))), chain_leq))
    assert is_total_order(chain) is True
    total_order = TotallyOrderedSets()(chain)
    assert total_order in TotallyOrderedSets()
    assert total_order in FiniteTotallyOrderedSets()


def test_poset_hom_monotonicity_admission_and_rejection() -> None:
    def chain_leq(left: SetElement, right: SetElement) -> bool:
        assert ZZ.contains_integer(left)
        assert ZZ.contains_integer(right)
        return int(left) <= int(right)

    chain = Poset(((ZZ(int(0)), ZZ(int(1))), chain_leq))
    hom = PartiallyOrderedSets().Hom(chain, chain)

    def reverse_chain(member: PosetElement) -> PosetElement:
        set_elem = PartiallyOrderedSets().forgetful_functor().on_element(chain, member)
        assert ZZ.contains_integer(set_elem)
        return chain.element(ZZ(int(1) - int(set_elem)))

    reversing_rejected = False
    try:
        hom(reverse_chain)
    except AssertionError:
        reversing_rejected = True
    assert reversing_rejected

    constant_map = hom(lambda member: chain.element(ZZ(int(0))))
    assert constant_map.is_order_preserving()
    assert constant_map in hom
    zero_elem = chain.element(ZZ(int(0)))
    one_elem = chain.element(ZZ(int(1)))
    assert constant_map(zero_elem) == zero_elem
    assert constant_map(one_elem) == zero_elem


def test_finite_total_order_routes_coherence() -> None:
    ordered = finite_ordered_set((ZZ(int(1)), ZZ(int(2))))
    route1 = (
        FiniteTotallyOrderedSets().inclusion(),
        TotallyOrderedSets().inclusion(),
    )
    route2 = (
        FiniteTotallyOrderedSets().finite_poset_functor(),
        FinitePosets().inclusion(),
    )
    img1 = ordered._object_image_along(route1)
    img2 = ordered._object_image_along(route2)
    assert img1 is img2

    set_img1 = img1._object_image_along((PartiallyOrderedSets().forgetful_functor(),))
    set_img2 = img2._object_image_along((PartiallyOrderedSets().forgetful_functor(),))
    assert set_img1 is set_img2


