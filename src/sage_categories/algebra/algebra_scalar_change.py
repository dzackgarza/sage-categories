"""Restriction of scalars for ordinary base-relative algebras.

For a ring morphism ``f: R -> S``, an ``S``-algebra is an ``R``-algebra by
restricting both bimodule actions.  Its ``R``-relative multiplication is the
unique descent of the original multiplication along ``B tensor_R B -> B tensor_S B``.
All quotient and balancing computation remains owned by the existing relative tensor
implementation.
"""

from __future__ import annotations

from sage_categories.algebra.abelian import (
    AbelianTensor,
    relative_tensor,
)
from sage_categories.algebra.algebras import AlgebraCategory
from sage_categories.cat.bimodules import BimoduleCategory, relative_tensor_factor
from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.choices import ChosenConstruction
from sage_categories.cat.functors import Fun, Functor
from sage_categories.cat.monoidal import tensor_object
from sage_categories.cat.morphisms import Mor, MorphismCategory
from sage_categories.cat.structured_objects import Magmas, MonoidCategory, Monoids

_ALGEBRA_RESTRICTIONS = ChosenConstruction()
_ALGEBRA_RESTRICTION_FUNCTORS = ChosenConstruction()


def _to_relative(algebras: AlgebraCategory) -> Functor:
    """The retained composite from algebras to their relative bimodule carrier."""
    monoids = algebras.monoid_category()
    return Magmas(algebras.monoidal_structure()).forgetful() * monoids.to_magmas() * algebras.monoid_presentation()


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
    to_relative = _to_relative(source)
    source_carrier = to_relative.on_object(algebra)
    restriction = source_relative.restriction(scalar_morphism, scalar_morphism)
    assert restriction.codomain() is target_relative
    restricted = restriction.on_object(source_carrier)
    scalar_map = _underlying_scalar_map(scalar_morphism)

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
    underlying_multiplication = relative_tensor_factor(
        AbelianTensor(),
        target_projection,
        source_multiplication * source_projection,
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


def _restrict_algebra_scalars[
    SourceScalar: "MonoidCategory.ObjectType",
    TargetScalar: "MonoidCategory.ObjectType",
](
    source: AlgebraCategory[SourceScalar],
    target: AlgebraCategory[TargetScalar],
    scalar_morphism: MorphismCategory.ObjectType,
) -> CategoryOfCategories.MorphismType[
    AlgebraCategory[SourceScalar],
    AlgebraCategory[TargetScalar],
    AlgebraCategory.ObjectType,
    AlgebraCategory.ElementType,
    AlgebraCategory.MorphismType,
    AlgebraCategory.ObjectType,
    AlgebraCategory.ElementType,
    AlgebraCategory.MorphismType,
]:
    """Restriction of scalars ``Alg_S -> Alg_R`` along ``R -> S``.

    Both algebra categories use the ordinary relative tensor on ``(R,R)``- and
    ``(S,S)``-bimodules in ``Ab``.  Object and morphism actions preserve the exact
    base-relative owners rather than reusing one Python realization at both bases.
    """
    return _ALGEBRA_RESTRICTION_FUNCTORS(
        source,
        (target, scalar_morphism),
        lambda: _new_restrict_algebra_scalars(source, target, scalar_morphism),
    )


def _new_restrict_algebra_scalars(
    source: AlgebraCategory,
    target: AlgebraCategory,
    scalar_morphism: MorphismCategory.ObjectType,
) -> Functor:
    """Construct the named restriction functor on one exact scalar-change datum."""
    monoids = Monoids(AbelianTensor())
    assert scalar_morphism in Mor(monoids)(target.base(), source.base())
    source_relative, target_relative = (
        _ordinary_bimodules(source),
        _ordinary_bimodules(target),
    )
    relative_restriction = source_relative.restriction(
        scalar_morphism,
        scalar_morphism,
    )
    assert relative_restriction.codomain() is target_relative

    def on_object(algebra: AlgebraCategory.ObjectType) -> AlgebraCategory.ObjectType:
        return _ALGEBRA_RESTRICTIONS(
            source,
            (target, scalar_morphism, algebra),
            lambda: _restrict_object(source, target, scalar_morphism, algebra),
        )

    def on_morphism(
        arrow: AlgebraCategory.MorphismType,
    ) -> AlgebraCategory.MorphismType:
        source_bimodule_map = _to_relative(source).on_morphism(arrow)
        restricted_source, restricted_target = (
            on_object(arrow.domain()),
            on_object(arrow.codomain()),
        )
        target_bimodule_map = relative_restriction.on_morphism(source_bimodule_map)
        return target.homomorphism(
            restricted_source,
            restricted_target,
            target_bimodule_map,
        )

    return Fun(source, target)(on_object, on_morphism)
