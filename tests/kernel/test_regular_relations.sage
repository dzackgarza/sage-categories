"""Relational composition and order laws through regular images."""

from sage_categories.all import Mor, ask
from sage_categories.sets import FiniteSets as S
from sage_categories.cat.relations import Relations


def test_relations_compose_by_existential_quantification():
    rel = Relations(S)
    values = S((0, 1, 2))
    product = S.Products()((values, values))
    edges = S(((0, 1), (1, 2)))
    mono = Mor(S)(edges, product).Monomorphisms()(lambda pair: pair)
    relation = rel.construct_morphism(rel(values), rel(values), mono)
    composite = relation * relation
    image = {
        composite.monomorphism()(point).datum()
        for point in composite.monomorphism().domain()
    }
    assert image == {(0, 2)}
    assert ask(relation.is_transitive()) is False
    assert ask(relation.is_reflexive()) is False
    ordered = S(((0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2)))
    order = rel.construct_morphism(
        rel(values),
        rel(values),
        Mor(S)(ordered, product).Monomorphisms()(lambda pair: pair),
    )
    assert ask(order.is_reflexive()) is True
    assert ask(order.is_transitive()) is True
    assert ask(order.is_antisymmetric()) is True
    inclusion = rel.inclusion(relation, order)
    assert (
        ask(order.monomorphism() * inclusion.factor() == relation.monomorphism())
        is True
    )
    horizontal = rel.horizontal_composite(inclusion, inclusion)
    assert (
        ask(
            horizontal.codomain().monomorphism() * horizontal.factor()
            == horizontal.domain().monomorphism()
        )
        is True
    )
    associator = rel.associator(order, relation, order)
    assert (
        ask(
            associator.inverse().factor() * associator.factor()
            == Mor(S)(
                associator.domain().monomorphism().domain(),
                associator.domain().monomorphism().domain(),
            ).one()
        )
        is True
    )
    flip = Mor(S)(values, values)(lambda value: 2 - value)
    graph = rel.graph_functor().on_morphism(flip)
    assert (
        ask(graph.converse() * graph == Mor(rel)(rel(values), rel(values)).one())
        is True
    )


test_relations_compose_by_existential_quantification()
