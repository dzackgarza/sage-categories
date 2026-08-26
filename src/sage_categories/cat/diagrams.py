"""Diagrams: evaluation functors of ``Fun(I, C)``, constant and discrete diagrams (D10, D16).

A diagram of shape ``I`` in ``C`` is an object of ``Fun(I, C)``.  ``Fun(I, C)``
retains one evaluation functor ``ev_i: Fun(I, C) -> C`` per object ``i`` of ``I``,
constructed through ``Fun(Fun(I, C), C)`` (Mathlib ``CategoryTheory.evaluation``;
inspected 2026-08-26): on a diagram it returns ``D(i)`` and on a natural
transformation its component at ``i``.  For ``I = [1]`` the evaluations at ``0``
and ``1`` are ``ev_0`` and ``ev_1``, the domain and codomain of a morphism.

The constant diagram at ``X`` sends every object to ``X`` and every morphism to
its identity (Mathlib ``CategoryTheory.Functor.const``; inspected 2026-08-26); it
is retained once per ``X`` so that a construction can recognize a retained
constant diagram.  A diagram over ``Discrete(S)`` is determined by its object rule
alone, since the only morphisms are identities; the sequence convenience
``(X_0, ..., X_n)`` denotes the diagram over ``Discrete([n])`` for
``[n] = Sets().Simplex(n)``.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from sage_categories.cat.category import Category
from sage_categories.cat.functors import Fun, Functor
from sage_categories.cat.shapes import Discrete, DiscreteObject, is_discrete
from sage_categories.kernel.predicates import ask
from sage_categories.kernel.roles import MorphismOfCategory, ObjectOfCategory
from sage_categories.sets.category import Sets

if TYPE_CHECKING:
    from sage_categories.cat.functors import FunctorCategory

__all__ = ["constant", "evaluation", "from_object_rule", "from_sequence", "sequence_position"]


def evaluation(functors: FunctorCategory, vertex: ObjectOfCategory) -> Functor:
    """``ev_i: Fun(I, C) -> C`` for an object ``i`` of ``I``, retained per ``i``."""
    assert vertex in functors.domain(), f"{vertex!r} is not an object of {functors.domain()!r}"
    if vertex not in functors._evaluations:
        functors._evaluations[vertex] = Fun(functors, functors.codomain())(
            lambda diagram: diagram.on_object(vertex),
            lambda transformation: transformation.component(vertex),
        )
    return functors._evaluations[vertex]


def constant(functors: FunctorCategory, value: ObjectOfCategory) -> Functor:
    """The constant diagram at ``value``, retained per value."""
    assert value in functors.codomain(), f"{value!r} is not an object of {functors.codomain()!r}"
    if value not in functors._constants:
        diagram = functors(lambda vertex: value, lambda morphism: value.identity())
        functors._constants[value] = diagram
        functors._constant_values[diagram] = value
    return functors._constants[value]


def from_object_rule(functors: FunctorCategory, rule: Callable[[DiscreteObject], ObjectOfCategory]) -> Functor:
    """A diagram over a discrete shape from its object rule; the morphism rule is forced."""
    assert is_discrete(functors.domain()), f"{functors.domain()!r} is not a discrete shape; supply a morphism rule"
    return functors(rule, lambda identity: rule(identity.domain()).identity())


def sequence_position(vertex: DiscreteObject) -> int:
    """The position ``k`` of an object of ``Discrete([n])`` at the point ``k`` of ``[n]``."""
    simplex = vertex.category().index_set()
    enumeration = Sets().Finite().chosen_enumeration(simplex)
    return next(position for position, datum in enumerate(enumeration) if ask(vertex.point() == simplex.point(datum)) is True)


def from_sequence(ambient: Category, sequence: tuple[ObjectOfCategory, ...]) -> Functor:
    """The diagram ``(X_0, ..., X_n)`` over ``Discrete([n])``; the empty sequence is over ``Discrete({})``."""
    index_set = Sets().Simplex(len(sequence) - 1) if sequence else Sets().Empty()
    return from_object_rule(Fun(Discrete(index_set), ambient), lambda vertex: sequence[sequence_position(vertex)])


def morphism_from_sequence(ambient: Category, domain: Functor, codomain: Functor, components: tuple[MorphismOfCategory, ...]) -> MorphismOfCategory:
    """The natural transformation between two sequence diagrams with the given components."""
    functors = Fun(domain.domain(), ambient)
    return functors.morphism_category(1)(domain, codomain)(lambda vertex: components[sequence_position(vertex)])
