"""R2 acceptance for the owned Cat core, using only Cat-level constructions."""

from sage_categories.cat.category import Cat
from sage_categories.cat.diagrams import cospan_diagram
from sage_categories.cat.functors import Fun


def _identity_functor(category):
    return Fun(category, category)(lambda x: x, lambda f: f)


def _identity_transformation(functor):
    category = functor.codomain()
    return Fun(functor.domain(), category).morphism_category(1)(functor, functor)(
        lambda x: category.morphism_category(1)(functor.on_object(x), functor.on_object(x)).one()
    )


def test_functors_and_two_morphisms_are_owned_and_distinct() -> None:
    category = Cat().Simplex(1)
    first = _identity_functor(category)
    second = _identity_functor(category)
    assert first is not second
    transformation = Fun(category, category).morphism_category(1)(first, second)(
        lambda x: category.morphism_category(1)(x, x).one()
    )
    assert transformation.component(category(0)) is transformation.component(category(0))

    eta = _identity_transformation(first)
    theta = _identity_transformation(second)
    assert eta.whisker_left(first).source_functor().domain() is category
    assert eta.whisker_right(first).source_functor().domain() is category
    assert eta.horizontal(theta).source_functor().domain() is category


def test_walking_arrow_evaluation_acts_on_objects_and_two_morphisms() -> None:
    category = Cat().Simplex(1)
    diagrams = Fun(Cat().Simplex(1), category)
    identity = _identity_functor(category)
    evaluation = diagrams.evaluation(Cat().Simplex(1)(0))
    assert evaluation.on_object(identity) is category(0)
    eta = _identity_transformation(identity)
    assert evaluation.on_morphism(eta) is eta.component(category(0))


def test_products_pullbacks_comma_and_fixed_slices_retain_defining_functors() -> None:
    category = Cat().Simplex(1)
    product = Cat().Products()((category, category))
    assert product.product_projection(0).domain() is product
    assert product.product_projection(1).domain() is product
    assert product.product_factors().domain() is product.index_category()

    identity = _identity_functor(category)
    diagram = cospan_diagram(Cat(), identity, identity)
    pullback = Cat().Pullbacks()(diagram)
    presentation = Cat().Pullbacks().presentation(pullback)
    assert presentation.diagram() is diagram
    assert presentation.transformation().codomain() is diagram

    comma = Cat().Comma(identity, identity)
    assert Cat().Comma(identity, identity) is comma
    assert comma in Cat().Pullbacks()
    assert comma.first_projection().domain() is comma
    assert comma.first_projection().codomain() is category
    assert comma.second_projection().domain() is comma
    assert comma.second_projection().codomain() is category
    transformation = comma.defining_transformation()
    assert transformation.source_functor().factors() == (comma.first_projection(), identity)
    assert transformation.target_functor().factors() == (comma.second_projection(), identity)

    slice_category = category.SliceOver(category(1))
    coslice_category = category.CosliceUnder(category(0))
    for fixed in (slice_category, coslice_category):
        assert fixed.defining_arrow().domain() is fixed
        assert fixed.fixed_projection().domain() is fixed
        assert fixed.fixed_projection().codomain() is category


def test_shape_indexed_functor_properties_exist_at_fixed_endpoints() -> None:
    category = Cat().Simplex(1)
    shape = Cat().Simplex(1)
    functors = Fun(category, category)
    preserves = functors.PreservesLimits(shape)
    creates = functors.CreatesLimits(shape)
    assert preserves.ambient() is functors
    assert creates.ambient() is functors
    assert preserves.shape() is shape
    assert creates.shape() is shape


def test_canonical_shapes_are_retained() -> None:
    cat = Cat()
    assert cat.Initial() is cat.Initial()
    assert cat.Terminal() is cat.Terminal()
    assert cat.Simplex(1) is cat.Simplex(1)
    assert cat.WalkingParallelPair() is cat.WalkingParallelPair()
    assert cat.WalkingIsomorphism() is cat.WalkingIsomorphism()


for name, value in tuple(globals().items()):
    if name.startswith("test_"):
        value()
