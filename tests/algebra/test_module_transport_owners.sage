"""Transport a nonconstant scalar action in Sets and in Sets × 1."""

from sage_categories.all import Cat, Fun, Mor, Sets, Cartesian, SelfAction, ask
from sage_categories.cat.calculus import binary_product_data, natural_isomorphism, pair_maps
from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.functors import Functor
from sage_categories.cat.modules import Modules
from sage_categories.cat.monoidal import Actions, ActionsCategory, MonoidalStructuresCategory
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.structured_objects import Monoids


def action_on_product(structure: MonoidalStructuresCategory.ObjectType) -> tuple[ActionsCategory.ObjectType, Functor, Functor]:
    """Transport Cartesian multiplication across Sets × 1 ⇄ Sets."""
    monoidal = structure.underlying_category()
    one = Cat().Terminal()
    product = binary_product_data(Cat(), monoidal, one)
    base, projection = product.apex(), product.leg(0)
    section = pair_maps(Cat(), Fun(monoidal, monoidal).one(), Fun(monoidal, one).constant(one(0)))
    pairs = binary_product_data(Cat(), monoidal, base)
    action = section * structure.tensor() * pair_maps(Cat(), pairs.leg(0), projection * pairs.leg(1))

    triples = Cat().Products()((monoidal, monoidal, base))
    first, second, third = (triples.product_projection(index) for index in range(3))
    left = action * pair_maps(Cat(), structure.tensor() * pair_maps(Cat(), first, second), third)
    right = action * pair_maps(Cat(), first, action * pair_maps(Cat(), second, third))
    change_triples = Cat().Products()((monoidal, monoidal, monoidal))

    def associator_at(triple: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
        return structure.associator().component(change_triples((
            triple.family_component(0),
            triple.family_component(1),
            projection.on_object(triple.family_component(2)),
        )))

    associator = natural_isomorphism(
        left, right,
        lambda triple: section.on_morphism(associator_at(triple)),
        lambda triple: section.on_morphism(associator_at(triple).inverse()),
    )

    identity = Fun(base, base).one()
    constant = Fun(base, monoidal).constant(structure.unit())
    unital = action * pair_maps(Cat(), constant, identity)

    def counit_at(value: CategoryOfCategories.ElementType, forward: bool) -> MorphismCategory.ObjectType:
        lifted = section.on_object(projection.on_object(value))
        components = (
            Mor(monoidal)(projection.on_object(value), projection.on_object(value)).one(),
            Mor(one)(value.family_component(1), value.family_component(1)).one(),
        )
        if forward:
            return Mor(base)(lifted, value)(components)
        return Mor(base)(value, lifted)(components)

    unitor = natural_isomorphism(
        unital, identity,
        lambda value: counit_at(value, True) * section.on_morphism(structure.left_unitor().component(projection.on_object(value))),
        lambda value: section.on_morphism(structure.left_unitor().inverse().component(projection.on_object(value))) * counit_at(value, False),
    )
    return Actions(structure, base)(action, associator, unitor), projection, section


def transport_boolean_action(actegory: ActionsCategory.ObjectType, projection: Functor, section: Functor) -> None:
    structure = actegory.monoidal_structure()
    monoidal, base = structure.underlying_category(), actegory.underlying_category()
    scalars = Sets((0, 1))
    square = binary_product_data(monoidal, scalars, scalars).apex()
    monoid = Monoids(structure)(
        Mor(monoidal)(square, scalars)(lambda pair: min(pair)),
        Mor(monoidal)(structure.unit(), scalars)(lambda point: 1),
    )
    source_set, target_set = Sets((0, 1, 2)), Sets((10, 20, 30))
    source, target = section.on_object(source_set), section.on_object(target_set)
    acted_set = binary_product_data(monoidal, scalars, source_set).apex()
    original_action = Mor(monoidal)(acted_set, source_set)(lambda pair: pair[1] if pair[0] == 1 else 2)
    modules = Modules(monoid, actegory)
    module = modules(section.on_morphism(original_action))
    forward = Mor(monoidal)(source_set, target_set)(lambda value: {0: 30, 1: 10, 2: 20}[value])
    backward = Mor(monoidal)(target_set, source_set)(lambda value: {30: 0, 10: 1, 20: 2}[value])
    monoidal.retain_inverses(forward, backward)
    isomorphism = section.on_morphism(forward)

    transported = modules.transport(module, isomorphism)
    action = actegory.action()
    pairs = action.domain()
    acted_source, acted_target = pairs((scalars, source)), pairs((scalars, target))
    scalar_identity = Mor(monoidal)(scalars, scalars).one()
    change = action.on_morphism(Mor(pairs)(acted_source, acted_target)((scalar_identity, isomorphism)))
    assert transported in modules
    assert modules.forgetful().on_object(transported) is target
    assert transported.action().domain() is action.on_object(acted_target)
    assert transported.action().codomain() is target
    assert transported.action() in Mor(base)(action.on_object(acted_target), target)
    assert ask(transported.action() * change == isomorphism * module.action()) is True

    observed = projection.on_morphism(transported.action())
    assert ask(observed(observed.domain().point((0, 10))) == target_set.point(20)) is True
    assert ask(observed(observed.domain().point((1, 10))) == target_set.point(10)) is True
    recovered = modules.transport(transported, isomorphism.inverse())
    assert modules.forgetful().on_object(recovered) is source
    assert ask(recovered.action() == module.action()) is True
    assert ask(recovered == module) is True


def test_distinct_acting_and_acted_categories() -> None:
    actegory, projection, section = action_on_product(Cartesian(Sets))
    assert actegory.monoidal_structure().underlying_category() is Sets
    assert actegory.underlying_category() is not Sets
    transport_boolean_action(actegory, projection, section)


def test_self_action_transport() -> None:
    identity = Fun(Sets, Sets).one()
    transport_boolean_action(SelfAction(Cartesian(Sets)), identity, identity)


test_distinct_acting_and_acted_categories()
test_self_action_transport()
