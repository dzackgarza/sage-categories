"""Coherence and nonidentity morphisms for supplied monoidal structures."""

from sage_categories.all import (
    Cartesian,
    Cat,
    Category,
    Composition,
    Fun,
    Mor,
    SelfAction,
    Sets,
    ask,
)
from sage_categories.cat.calculus import natural_isomorphism, pair_maps
from sage_categories.cat.modules import Modules
from sage_categories.cat.monoidal import (
    Actions,
    MonoidalStructures,
    TrivialAction,
    tensor_parentheses,
    tensor_units,
)
from sage_categories.cat.predicates import Proposition, register_handler
from sage_categories.cat.structured_objects import Magmas, Monoids


def test_functor_and_transformation_equality() -> None:
    source, target = Cat().Terminal(), Cat().WalkingParallelPair()
    diagrams = Fun(source, target)
    first = diagrams.constant(target(0))
    same = diagrams(lambda vertex: target(0), lambda arrow: Mor(target)(target(0), target(0)).one())
    second = diagrams.constant(target(1))
    assert ask(first == same) is True
    assert ask(first == second) is False
    transformations = Mor(diagrams)(first, second)
    alpha = transformations(lambda vertex: target.generator("f"))
    beta = transformations(lambda vertex: target.generator("g"))
    duplicate = transformations(lambda vertex: target.generator("f"))
    assert ask(alpha == duplicate) is True
    assert ask(alpha == beta) is False


def test_cartesian_coherence() -> None:
    structure = Cartesian(Sets)
    X, Y, Z, W = (Sets(values) for values in ((0, 1), (2, 3), (4, 5), (6, 7)))
    triples = structure.associator().domain().domain()
    alpha = structure.associator().component(triples((X, Y, Z)))
    point = alpha.domain().point(((1, 2), 5))
    assert alpha(point).datum() == (1, (2, 5))
    assert alpha(point).parent() is alpha.codomain()
    assert alpha.inverse()(alpha(point)).datum() == ((1, 2), 5)
    for unitor, datum in ((structure.left_unitor(), ((), 1)), (structure.right_unitor(), (1, ()))):
        component = unitor.component(X)
        assert component(component.domain().point(datum)).datum() == 1
        assert component.codomain() is X
        assert component.inverse()(X.point(1)).datum() == datum
    assert ask(structure.pentagon(W, X, Y, Z)) is True
    assert ask(structure.triangle(X, Y)) is True

    action = SelfAction(structure)
    f = Mor(Sets)(X, Y)(lambda n: n + 2)
    g = Mor(Sets)(Y, Z)(lambda n: n + 2)
    pairs = action.action().domain()
    image = action.action().on_morphism(Mor(pairs)(pairs((X, Y)), pairs((Y, Z)))((f, g)))
    assert image(image.domain().point((1, 2))).datum() == (3, 4)
    assert action.unitor().component(X).codomain() is X
    assert ask(action.pentagon(W, X, Y, Z)) is True
    assert ask(action.triangle(X, Y)) is True
    trivial = TrivialAction(structure, Sets)
    assert trivial is not action
    assert trivial.action().on_object(pairs((X, Y))) is Y
    assert trivial.action().on_morphism(Mor(pairs)(pairs((X, Y)), pairs((Y, Z)))((f, g))) is g
    assert trivial.unitor().component(X)(X.point(1)).datum() == 1


class ChaoticPair(Category):
    """The two-object chaotic groupoid, used to make coherence maps observably nonidentity."""

    class ObjectType:
        def __init__(self, label: int) -> None:
            self._label = label

        def label(self) -> int:
            return self._label

    class ElementType:
        pass

    class MorphismType:
        pass

    def __call__(self, label: int) -> ChaoticPair.ObjectType:
        return self.ObjectType(label)

    def _equal_objects(
        self,
        first: ChaoticPair.ObjectType,
        second: ChaoticPair.ObjectType,
        assumptions: Proposition,
    ) -> bool:
        return first.label() == second.label()

    def _equal_morphisms(
        self,
        first: ChaoticPair.MorphismType,
        second: ChaoticPair.MorphismType,
        assumptions: Proposition,
    ) -> bool:
        return first.domain() is second.domain() and first.codomain() is second.codomain()


def test_internal_monoid_uses_a_supplied_nonstrict_associator() -> None:
    category = ChaoticPair()
    register_handler(category.equality(), category._equal_objects)
    register_handler(category.equality(), category._equal_morphisms)
    zero, one = category(0), category(1)
    pairs = Cat().Products()((category, category))

    # x tensor y = not x.  Thus tensor is intentionally nonassociative on
    # objects, while the chaotic groupoid supplies the unique comparison map.
    tensor_values = (one, zero)

    def tensor_object(pair):
        return tensor_values[pair.family_component(0).label()]

    def unique(source, target):
        return category.construct_morphism(source, target, (source.label(), target.label()))

    tensor = Fun(pairs, category)(
        tensor_object,
        lambda arrow: unique(tensor_object(arrow.domain()), tensor_object(arrow.codomain())),
    )
    left, right = tensor_parentheses(tensor)
    triples = left.domain()
    associator = natural_isomorphism(
        left,
        right,
        lambda triple: unique(left.on_object(triple), right.on_object(triple)),
        lambda triple: unique(right.on_object(triple), left.on_object(triple)),
    )
    left_unit, right_unit = tensor_units(tensor, zero)
    identity = Fun(category, category).one()
    left_unitor = natural_isomorphism(
        left_unit,
        identity,
        lambda value: unique(left_unit.on_object(value), value),
        lambda value: unique(value, left_unit.on_object(value)),
    )
    right_unitor = natural_isomorphism(
        right_unit,
        identity,
        lambda value: unique(right_unit.on_object(value), value),
        lambda value: unique(value, right_unit.on_object(value)),
    )
    structure = MonoidalStructures(category)(tensor, zero, associator, left_unitor, right_unitor)

    triple_zero = triples((zero, zero, zero))
    comparison = structure.associator().component(triple_zero)
    assert comparison.domain() is zero
    assert comparison.codomain() is one
    assert ask(structure.pentagon(zero, zero, zero, zero)) is True
    assert ask(structure.triangle(zero, zero)) is True

    operation = unique(tensor.on_object(pairs((zero, zero))), zero)
    unit = Mor(category)(zero, zero).one()
    monoids = Monoids(structure)
    monoid = monoids(operation, unit)
    assert monoid in monoids
    assert monoid.operation() is operation
    assert monoid.unit_morphism() is unit
    assert monoids.to_magmas().on_object(monoid).operation() is operation

    acted = Sets((0, 1, 2))
    trivial = TrivialAction(structure, Sets)
    assert trivial.monoidal_structure() is structure
    assert trivial.underlying_category() is Sets
    assert ask(trivial.pentagon(zero, one, zero, acted)) is True
    assert ask(trivial.triangle(one, acted)) is True

    modules = Modules(monoid, trivial)
    module = modules(trivial.unitor().component(acted))
    assert module in modules
    assert modules.forgetful().on_object(module) is acted
    assert module.action()(acted.point(2)).datum() == 2

    acted_category = ChaoticPair()
    register_handler(acted_category.equality(), acted_category._equal_objects)
    register_handler(acted_category.equality(), acted_category._equal_morphisms)
    acted_zero, acted_one = acted_category(0), acted_category(1)
    action_pairs = Cat().Products()((category, acted_category))

    def acted_unique(source, target):
        return acted_category.construct_morphism(source, target, (source.label(), target.label()))

    def action_object(pair):
        scalar, value = pair.family_component(0), pair.family_component(1)
        return acted_category((scalar.label() + value.label()) % 2)

    def action_morphism(arrow):
        return acted_unique(action.on_object(arrow.domain()), action.on_object(arrow.codomain()))

    action = Fun(action_pairs, acted_category)(action_object, action_morphism)
    action_triples = Cat().Products()((category, category, acted_category))
    first, second, third = (action_triples.product_projection(index) for index in range(3))
    action_left = action * pair_maps(Cat(), tensor * pair_maps(Cat(), first, second), third)
    action_right = action * pair_maps(Cat(), first, action * pair_maps(Cat(), second, third))
    action_associator = natural_isomorphism(
        action_left,
        action_right,
        lambda triple: acted_unique(action_left.on_object(triple), action_right.on_object(triple)),
        lambda triple: acted_unique(action_right.on_object(triple), action_left.on_object(triple)),
    )
    acted_identity = Fun(acted_category, acted_category).one()
    unit_constant = Fun(acted_category, category).constant(zero)
    action_unital = action * pair_maps(Cat(), unit_constant, acted_identity)
    action_unitor = natural_isomorphism(
        action_unital,
        acted_identity,
        lambda value: acted_unique(action_unital.on_object(value), value),
        lambda value: acted_unique(value, action_unital.on_object(value)),
    )
    nontrivial = Actions(structure, acted_category)(action, action_associator, action_unitor)
    assert nontrivial.underlying_category() is acted_category
    assert ask(action.on_object(action_pairs((one, acted_zero))) == acted_one) is True
    assert ask(nontrivial.pentagon(zero, one, zero, acted_zero)) is True
    assert ask(nontrivial.triangle(one, acted_zero)) is True

    nontrivial_modules = Modules(monoid, nontrivial)
    acted_module = nontrivial_modules(Mor(acted_category)(acted_zero, acted_zero).one())
    transport_isomorphism = acted_unique(acted_zero, acted_one)
    acted_category.retain_inverses(transport_isomorphism, acted_unique(acted_one, acted_zero))
    changed = nontrivial_modules.transport(acted_module, transport_isomorphism)
    assert nontrivial_modules.forgetful().on_object(changed) is acted_one
    assert ask(changed.action().domain() == action.on_object(action_pairs((zero, acted_one)))) is True
    assert changed.action().codomain() is acted_one


def test_composition_tensor() -> None:
    C = Cat().Simplex(2)
    E = Fun(C, C)
    identity, bottom, top = E.one(), E.constant(C(0)), E.constant(C(2))
    edge = lambda i, j: Mor(C)(C(i), C(j))(tuple(f"{k}->{k + 1}" for k in range(i, j)))
    theta = Mor(E)(identity, top)(lambda x: edge(C.label(x), 2))
    eta = Mor(E)(bottom, identity)(lambda x: edge(0, C.label(x)))
    structure = Composition(C)
    pairs = structure.tensor().domain()
    arrow = Mor(pairs)(pairs((identity, bottom)), pairs((top, identity)))((theta, eta))
    composite = structure.tensor().on_morphism(arrow)
    assert ask(composite.component(C(1)) == edge(0, 2)) is True
    assert structure.unit() is identity
    assert structure.unit().on_object(C(0)) is C(0)
    assert top.on_object(C(0)) is C(2)
    action = SelfAction(structure)
    assert ask(action.action().on_morphism(arrow).component(C(1)) == edge(0, 2)) is True
    assert action.unitor().component(bottom).component(C(1)).domain() is C(0)

    closure = E(lambda x: C(max(1, C.label(x))),
        lambda f: edge(max(1, C.label(f.domain())), max(1, C.label(f.codomain()))))
    multiplication = Mor(E)(closure * closure, closure)(lambda x: edge(max(1, C.label(x)), max(1, C.label(x))))
    unit = Mor(E)(identity, closure)(lambda x: edge(C.label(x), max(1, C.label(x))))
    magma = Magmas(structure).algebra(closure, multiplication)
    assert magma.on_object(C(0)) is closure.on_object(C(0))
    assert magma.domain() is C and magma.codomain() is C
    assert ask(magma.on_morphism(edge(0, 2)) == edge(1, 2)) is True
    top_multiplication = Mor(E)(top * top, top)(lambda x: edge(2, 2))
    top_magma = Magmas(structure).algebra(top, top_multiplication)
    comparison = Mor(E)(closure, top)(lambda x: edge(max(1, C.label(x)), 2))
    magma_map = Magmas(structure).homomorphism(magma, top_magma, comparison)
    assert ask(Magmas(structure).forgetful().on_morphism(magma_map).component(C(1)) == edge(1, 2)) is True
    monoids = Monoids(structure)
    monoid = monoids(multiplication, unit)
    assert monoid in Monoids(structure)
    assert monoid.carrier().carrier() is closure
    assert monoid.operation() is multiplication
    assert monoid.unit_morphism() is unit
    assert ask(monoid.unit_morphism().component(C(0)) == edge(0, 1)) is True
    assert monoid.unit_morphism().domain() is identity
    assert monoid.unit_morphism().codomain() is closure
    assert monoid.operation().component(C(2)).codomain() is C(2)
    assert monoids.structure_functors() == (monoids.to_magmas(),)
    assert Fun.declares_inheritance(monoids.to_magmas())
    assert monoids.to_magmas().on_object(monoid) is magma


def test_closure_monad_on_two_element_chain() -> None:
    interval = Cat().Simplex(1)
    endofunctors = Fun(interval, interval)
    identity = endofunctors.one()
    closure = endofunctors.constant(interval(1))
    edge = interval.generator("0->1")
    identity_at_top = Mor(interval)(interval(1), interval(1)).one()
    unit = Mor(endofunctors)(identity, closure)(
        lambda vertex: edge if interval.label(vertex) == 0 else identity_at_top
    )
    multiplication = Mor(endofunctors)(closure * closure, closure)(
        lambda vertex: identity_at_top
    )
    structure = Composition(interval)
    monad = Monoids(structure)(multiplication, unit)
    assert monad in Monoids(structure)
    assert structure.unit() is identity
    assert ask(identity == endofunctors.Terminal()) is False
    assert ask(monad.unit_morphism().component(interval(0)) == edge) is True
    assert monad.operation().component(interval(0)).domain() is interval(1)
    assert monad.operation().component(interval(0)).codomain() is interval(1)


test_functor_and_transformation_equality()
test_cartesian_coherence()
test_internal_monoid_uses_a_supplied_nonstrict_associator()
test_composition_tensor()
test_closure_monad_on_two_element_chain()
