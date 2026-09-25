"""Base change retains the selected cartesian and cocartesian lifts."""

from sage_categories.all import Cat, Fun, Mor, ask
from sage_categories.cat.diagrams import cospan_diagram
from sage_categories.cat.predicates import assume


def shifted_interval():
    source, target = Cat().Simplex(1), Cat().Simplex(2)

    def on_object(vertex):
        return target(source.label(vertex) + 1)

    def on_morphism(arrow):
        match arrow.word():
            case ():
                image = on_object(arrow.domain())
                return Mor(target)(image, image).one()
            case _:
                return target.generator("1->2")

    return Fun(source, target)(on_object, on_morphism)


def identity_fibration(base):
    result = Fun(base, base).Fibrations()(
        lambda value: value,
        lambda morphism: morphism,
    )
    result.retain_cartesian_lifts(lambda morphism, target: morphism)
    return result


def identity_opfibration(base):
    result = Fun(base, base).Opfibrations()(
        lambda value: value,
        lambda morphism: morphism,
    )
    result.retain_cocartesian_lifts(lambda morphism, source: morphism)
    return result


def test_base_change_of_fibration_retains_cartesian_lifts():
    along = shifted_interval()
    base = along.codomain()
    defining = identity_fibration(base)
    projection = along.base_change(defining)
    assert along.base_change(defining) is projection
    pullback = projection.domain()
    presentation = Cat().Pullbacks().universal_data(
        cospan_diagram(Cat(), along, defining)
    )
    other_projection = presentation.leg(1)
    assert presentation.leg(0) is projection
    assert other_projection.domain() is pullback
    assert ask(along * projection == defining * other_projection) is True

    target = pullback((along.domain()(1), base(2), base(2)))
    arrow = along.domain().generator("0->1")
    lift = projection.cartesian_lift(arrow, target)

    assert projection in Fun(projection.domain(), projection.codomain()).Fibrations()
    assert lift.codomain() is target
    assert ask(projection.on_morphism(lift) == arrow) is True
    assert lift.domain().family_component(0) is along.domain()(0)
    assert lift.domain().family_component(1) is base(1)
    assert ask(lift.family_component(1) == base.generator("1->2")) is True
    assert ask(lift.family_component(2) == along.on_morphism(arrow)) is True


def test_base_change_of_opfibration_retains_cocartesian_lifts():
    along = shifted_interval()
    base = along.codomain()
    defining = identity_opfibration(base)
    projection = along.base_change(defining)
    assert along.base_change(defining) is projection
    pullback = projection.domain()

    source = pullback((along.domain()(0), base(1), base(1)))
    arrow = along.domain().generator("0->1")
    lift = projection.cocartesian_lift(arrow, source)

    assert projection in Fun(projection.domain(), projection.codomain()).Opfibrations()
    assert lift.domain() is source
    assert ask(projection.on_morphism(lift) == arrow) is True
    assert lift.codomain().family_component(0) is along.domain()(1)
    assert lift.codomain().family_component(1) is base(2)
    assert ask(lift.family_component(1) == base.generator("1->2")) is True
    assert ask(lift.family_component(2) == along.on_morphism(arrow)) is True


def test_terminal_identity_base_change_reuses_selected_lifts():
    terminal = Cat().Terminal()
    star = terminal(0)
    identity = Fun(terminal, terminal).one()
    arrow = Mor(terminal)(star, star).one()
    identity.retain_cartesian_lifts(lambda morphism, target: morphism)
    identity.retain_cocartesian_lifts(lambda morphism, source: morphism)
    assume(Fun.Fibrations().membership_proposition(identity))
    assume(Fun.Opfibrations().membership_proposition(identity))

    projection = identity.base_change(identity)

    assert projection is identity
    assert projection.domain() is terminal
    assert projection.cartesian_lift(arrow, star) is arrow
    assert projection.cocartesian_lift(arrow, star) is arrow


test_base_change_of_fibration_retains_cartesian_lifts()
test_base_change_of_opfibration_retains_cocartesian_lifts()
test_terminal_identity_base_change_reuses_selected_lifts()
