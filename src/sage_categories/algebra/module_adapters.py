"""Semantic adapters into the ordinary generic module owner.

The public result is always an object of the supplied ``Modules(A,C)``.  Native
Sage data is lowered only inside :mod:`sage_categories.algebra._firewall.modules`;
this module reconstructs the owned additive carrier and its actual scalar action.
"""

from __future__ import annotations

from sympy import false, true

import sage_categories.algebra.abelian as _abelian
from sage_categories.algebra._firewall import modules as _backend
from sage_categories.algebra.indexed_modules import integer_scalar_monoid
from sage_categories.cat.calculus import binary_product_data
from sage_categories.cat.certified_structures import certified_additive_group
from sage_categories.cat.choices import ChosenConstruction
from sage_categories.cat.modules import ModuleCategory, select_native_module_adapter
from sage_categories.cat.monoidal import Cartesian
from sage_categories.cat.morphisms import Mor
from sage_categories.sets.finite import Sets

__all__ = ["install_sage_module_adapter", "sage_module_from_engine"]

_SAGE_MODULE_ADDITIVE_CARRIERS = ChosenConstruction()
_SAGE_MODULES = ChosenConstruction()


def _owned_additive_carrier(engine_module: object):
    """Reconstruct the native module's exact additive group as an owned object of ``Ab``."""
    native = _backend.require_integer_module(engine_module)

    def construct():
        def member(datum):
            match _backend.module_member(native, datum):
                case True:
                    return true
                case False:
                    return false

        carrier = Sets.from_membership(member)
        square = binary_product_data(Sets(), carrier, carrier).apex()
        addition = Mor(Sets)(square, carrier)(lambda pair: _backend.module_add(native, pair[0], pair[1]))
        cartesian = Cartesian(Sets())
        zero = Mor(Sets)(cartesian.unit(), carrier)(lambda _point: _backend.module_zero(native))
        inverse_shear = Mor(Sets)(square, square)(lambda pair: (pair[0], _backend.module_subtract(native, pair[1], pair[0])))
        group = certified_additive_group(carrier, addition, zero, inverse_shear, cartesian, commutative=True)
        coordinates = _abelian._CoordinateBridge(
            (0,) * _backend.module_rank(native),
            lambda datum: _backend.module_coordinates(native, datum),
            lambda entries: _backend.module_element(native, entries),
        )
        _abelian._retain_coordinates(group, coordinates)
        return group

    return _SAGE_MODULE_ADDITIVE_CARRIERS(_abelian.AbelianGroups(), (native,), construct)


def sage_module_from_engine(
    modules: ModuleCategory,
    engine_module: object,
) -> ModuleCategory.ObjectType:
    """Reconstruct a Sage ``ZZ``-module inside the exact supplied generic module category.

    The adapter currently supports the canonical integer scalar monoid, where the native
    base is unambiguous.  The owned carrier is reconstructed from native membership,
    addition, and zero; the action is the native scalar multiplication factored through
    the retained abelian tensor product.  No native module object is exposed publicly.
    """
    assert modules.scalars() is integer_scalar_monoid(), f"the Sage module adapter currently requires the canonical integer scalar monoid, not {modules.scalars()!r}"
    native = _backend.require_integer_module(engine_module)

    def construct() -> ModuleCategory.ObjectType:
        carrier = _owned_additive_carrier(native)
        action = _abelian.tensor_mediator(
            _abelian.integer_group(),
            carrier,
            carrier,
            lambda scalar, value: _backend.integer_scale(native, scalar, value),
        )
        return modules(action)

    return _SAGE_MODULES(modules, (native,), construct)


def _selected_sage_adapter(modules: ModuleCategory, engine_module: object) -> ModuleCategory.ObjectType:
    return sage_module_from_engine(modules, engine_module)


def install_sage_module_adapter() -> None:
    """Select the Sage-ingestion rule on the exact ordinary additive owner."""
    # Native ingestion is a capability of the exact acted-on category, not of Cat
    # itself. ModuleCategory.from_sage_module reads this selection and returns through
    # its own owner.
    select_native_module_adapter(_abelian.AbelianGroups(), _selected_sage_adapter)
