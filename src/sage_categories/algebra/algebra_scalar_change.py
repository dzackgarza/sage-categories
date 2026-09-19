"""Restriction of scalars for ordinary base-relative algebras.

For a ring morphism ``f: R -> S``, an ``S``-algebra is an ``R``-algebra by
restricting both bimodule actions.  Its ``R``-relative multiplication is the
unique descent of the original multiplication along ``B tensor_R B -> B tensor_S B``.
All quotient and balancing computation remains owned by the existing relative tensor
implementation.
"""

from __future__ import annotations

from sage_categories.algebra.abelian import (
    AbelianGroups,
    AbelianTensor,
    balanced_tensor,
    relative_tensor,
    relative_tensor_mediator,
)
from sage_categories.algebra.algebras import AlgebraCategory
from sage_categories.cat.bimodules import BimoduleCategory
from sage_categories.cat.choices import ChosenConstruction
from sage_categories.cat.functors import Fun, Functor
from sage_categories.cat.monoidal import tensor_morphism, tensor_object
from sage_categories.cat.morphisms import Mor, MorphismCategory
from sage_categories.cat.structured_objects import Magmas, Monoids

__all__ = ["restrict_algebra_scalars"]

_ALGEBRA_RESTRICTIONS = ChosenConstruction()


def _relative_carrier(
    algebras: AlgebraCategory,
    algebra: AlgebraCategory.ObjectType,
):
    monoid = algebras.monoid_presentation().on_object(algebra)
    magma = algebras.monoid_category().to_magmas().on_object(monoid)
    return Magmas(algebras.monoidal_structure()).forgetful().on_object(magma)


def _ordinary_bimodules(algebras: AlgebraCategory) -> BimoduleCategory:
    relative = algebras.monoidal_structure().underlying_category()
    assert isinstance(relative, BimoduleCategory), f"{algebras!r} is not presented by ordinary bimodules"
    assert relative.monoidal_structure() is AbelianTensor(), f"{algebras!r} does not use the ordinary tensor of abelian groups"
    return relative


def _underlying_scalar_map(
    scalar_morphism: MorphismCategory.ObjectType,
) -> MorphismCategory.ObjectType:
    monoids = Monoids(AbelianTensor())
    to_magmas = monoids.to_magmas()
    return to_magmas.codomain().forgetful().on_morphism(to_magmas.on_morphism(scalar_morphism))


def _restrict_object(
    source: AlgebraCategory,
    target: AlgebraCategory,
    scalar_morphism: MorphismCategory.ObjectType,
    algebra: AlgebraCategory.ObjectType,
) -> AlgebraCategory.ObjectType:
    source_relative, target_relative = (
        _ordinary_bimodules(source),
        _ordinary_bimodules(target),
    )
    source_carrier = _relative_carrier(source, algebra)
    group = source_relative.forgetful().on_object(source_carrier)
    scalar_map = _underlying_scalar_map(scalar_morphism)
    identity = Mor(AbelianGroups())(group, group).one()
    tensor = AbelianTensor().tensor()
    restricted = target_relative(
        source_carrier.left_action() * tensor_morphism(tensor, scalar_map, identity),
        source_carrier.right_action() * tensor_morphism(tensor, identity, scalar_map),
    )

    source_monoid = source.monoid_presentation().on_object(algebra)
    source_projection = relative_tensor(
        source_carrier.right_action(),
        source_carrier.left_action(),
    )
    target_projection = relative_tensor(
        restricted.right_action(),
        restricted.left_action(),
    )
    source_multiplication = source_relative.forgetful().on_morphism(source_monoid.operation())

    def multiply(left, right):
        source_tensor = balanced_tensor(source_projection, left, right)
        return source_multiplication(source_tensor).datum()

    underlying_multiplication = relative_tensor_mediator(
        target_projection,
        group,
        multiply,
    )
    tensor_square = tensor_object(target.monoidal_structure().tensor(), restricted, restricted)
    multiplication = target_relative.homomorphism(
        tensor_square,
        restricted,
        underlying_multiplication,
    )

    source_unit = source_relative.forgetful().on_morphism(source_monoid.unit_morphism())
    underlying_unit = source_unit * scalar_map
    unit = target_relative.homomorphism(
        target.monoidal_structure().unit(),
        restricted,
        underlying_unit,
    )
    return target.from_monoid(Monoids(target.monoidal_structure())(multiplication, unit))


def restrict_algebra_scalars(
    source: AlgebraCategory,
    target: AlgebraCategory,
    scalar_morphism: MorphismCategory.ObjectType,
) -> Functor:
    """Restriction of scalars ``Alg_S -> Alg_R`` along ``R -> S``.

    Both algebra categories use the ordinary relative tensor on ``(R,R)``- and
    ``(S,S)``-bimodules in ``Ab``.  Object and morphism actions preserve the exact
    base-relative owners rather than reusing one Python realization at both bases.
    """
    monoids = Monoids(AbelianTensor())
    assert scalar_morphism in Mor(monoids)(target.base(), source.base())
    source_relative, target_relative = (
        _ordinary_bimodules(source),
        _ordinary_bimodules(target),
    )

    def on_object(algebra: AlgebraCategory.ObjectType) -> AlgebraCategory.ObjectType:
        return _ALGEBRA_RESTRICTIONS(
            source,
            (target, scalar_morphism, algebra),
            lambda: _restrict_object(source, target, scalar_morphism, algebra),
        )

    def on_morphism(
        arrow: AlgebraCategory.MorphismType,
    ) -> AlgebraCategory.MorphismType:
        source_monoid = source.monoid_presentation().on_morphism(arrow)
        source_magma = source.monoid_category().to_magmas().on_morphism(source_monoid)
        source_bimodule_map = Magmas(source.monoidal_structure()).forgetful().on_morphism(source_magma)
        underlying = source_relative.forgetful().on_morphism(source_bimodule_map)
        restricted_source, restricted_target = (
            on_object(arrow.domain()),
            on_object(arrow.codomain()),
        )
        target_bimodule_map = target_relative.homomorphism(
            _relative_carrier(target, restricted_source),
            _relative_carrier(target, restricted_target),
            underlying,
        )
        return target.homomorphism(
            restricted_source,
            restricted_target,
            target_bimodule_map,
        )

    return Fun(source, target)(on_object, on_morphism)
