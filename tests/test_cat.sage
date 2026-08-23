"""The owned category of categories and its arrow categories."""

from sage_categories.all import *


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
    element_declaration = category.declared_element_methods()["__le__"]
    arrow_declaration = category.declared_arrow_methods()["is_injective"]

    assert object_declaration.owner is Sets()
    assert object_declaration.route
    assert element_declaration.owner is TotallyOrderedSets()
    assert element_declaration.route
    assert arrow_declaration.owner is Sets()
    assert arrow_declaration.route
