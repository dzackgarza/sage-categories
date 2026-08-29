"""The power object ``2 ** X`` of ``Sets()`` (POL-SET-018; ``specs/sets.md``, "Subobjects, images, and power objects").

``2 ** X`` with ``2 = [1] = Sets().Simplex(1)`` is the function set ``[1] ** X``
(``sets/exponentials.py``): one object, refined into ``Sets().PowerObjects()``,
which retains ``X`` as its base set (nLab "power set": "the set TV^S of all
functions from S to the set TV of truth values. This is often written 2^S";
inspected 2026-08-27).  Its points name the characteristic morphisms ``X -> 2``,
and ``2`` is the subobject classifier of ``Sets()`` (nLab "subobject classifier";
inspected 2026-08-27): ``from_characteristic_morphism(chi)`` is the chosen subset
``{x : chi(x) = 1}``, retained per ``chi``, and ``A.characteristic_morphism()`` is
its inverse on chosen subsets (``sets/subobjects.py``).  ``from_predicate`` is
``X.subset_from``; ``top()`` and ``bottom()`` are the chosen subsets ``X`` and
``{}`` of ``X``.

For a map ``f: Y -> X``, ``inverse_image_morphism(f): 2 ** X -> 2 ** Y`` sends the
name of ``chi`` to the name of ``chi * f``: ``chi_{f^-1(A)} = chi_A * f`` by the
definition of the preimage (Mathlib ``Set.mem_preimage``).  For ``f: X -> Y``,
``direct_image_morphism(f): 2 ** X -> 2 ** Y`` sends the name of ``chi_A`` to the
name of the characteristic morphism of ``(f * A.monomorphism()).image()``, the image
``f(A)`` (Mathlib ``Set.mem_image``; ``sets/subobjects.py``).  Both retained per map.

The cardinality ``2 ** #X`` is the function-set case ``(#2) ** (#X)`` (Mathlib
``Cardinal.mk_set``: ``#(Set α) = 2 ^ #α``; inspected 2026-08-27).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import sage_categories.sets.category as _sets
from sage_categories.cat.category import Category
from sage_categories.cat.properties import PropertySubcategory
from sage_categories.kernel.caches import retained_method
from sage_categories.kernel.decisions import Decision
from sage_categories.kernel.refinement import refine
from sage_categories.kernel.roles import ObjectOfCategory, Role
from sage_categories.sets.elements import Datum, SetElement
from sage_categories.sets.exponentials import Function, function_set
from sage_categories.sets.maps import Rule
from sage_categories.sets.objects import MembershipRule, SetObject

if TYPE_CHECKING:
    from sage_categories.sets.category import SetMap

__all__ = ["PowerObjectsCategory"]


class PowerObjectRole(ObjectOfCategory):
    """The local object role of ``Sets().PowerObjects()``: the function set ``2 ** X`` with its subset constructions."""

    def base_set(self) -> SetObject:
        """``X``, retained at construction."""
        return _sets.Sets().PowerObjects().retained_datum(self)

    def from_predicate(self, predicate: MembershipRule) -> SetObject:
        """The chosen subset ``{x in X : predicate(x)}`` with its monomorphism."""
        return self.base_set().subset_from(predicate)

    def from_characteristic_morphism(self, characteristic: SetMap) -> SetObject:
        """The chosen subset ``{x in X : chi(x) = 1}`` of a map ``chi: X -> 2``, retained per map."""
        return _sets.Sets().PowerObjects().subset_of_characteristic_morphism(self, characteristic)

    def subset_named_by(self, point: SetElement) -> SetObject:
        """The chosen subset whose characteristic morphism a point ``* -> 2 ** X`` names: the inverse of ``Sets().name_of`` on chosen subsets."""
        assert point in self, f"{point!r} is not a point of {self!r}"
        return self.from_characteristic_morphism(point._point_datum_().map())

    def top(self) -> SetObject:
        """``X`` as a chosen subset of itself."""
        return _sets.Sets().PowerObjects().extreme_subset(self, True)

    def bottom(self) -> SetObject:
        """The empty chosen subset of ``X``."""
        return _sets.Sets().PowerObjects().extreme_subset(self, False)

    def inverse_image_morphism(self, set_map: SetMap) -> SetMap:
        """``2 ** X -> 2 ** Y`` for ``f: Y -> X``: the name of ``chi`` to the name of ``chi * f``."""
        return _sets.Sets().PowerObjects().inverse_image_morphism(self, set_map)

    def direct_image_morphism(self, set_map: SetMap) -> SetMap:
        """``2 ** X -> 2 ** Y`` for ``f: X -> Y``: the name of ``chi_A`` to the name of ``chi_{f(A)}``."""
        return _sets.Sets().PowerObjects().direct_image_morphism(self, set_map)


class PowerObjectsCategory(PropertySubcategory[[Rule], []]):
    """``Sets().PowerObjects()``: the power objects ``2 ** X``, a narrowing of ``Sets()`` retaining each base set."""

    def __init__(self, ambient: Category[[Rule], []]) -> None:
        super().__init__(ambient, "PowerObjects", {Role.OBJECT: PowerObjectRole}, ())

    def __call__(self, base_set: SetObject) -> SetObject:
        """``2 ** X``: the function set ``[1] ** X`` refined here, retaining ``X``."""
        sets = _sets.Sets()
        assert base_set in sets, f"{base_set!r} is not an object of {sets!r}"
        power = function_set(base_set, sets.Simplex(1))
        if power not in self:
            self.retain_datum(power, base_set)
            refine(power, self)
        return power

    @retained_method
    def subset_of_characteristic_morphism(self, power: SetObject, characteristic: SetMap) -> SetObject:
        sets = _sets.Sets()
        base_set = self.retained_datum(power)
        assert characteristic in sets.morphism_category(1)(base_set, sets.Simplex(1)), f"{characteristic!r} is not a map {base_set!r} -> [1]"
        rule = characteristic._set_morphism_data.rule
        return base_set.subset_from(lambda datum: rule(datum) == 1)

    @retained_method
    def extreme_subset(self, power: SetObject, whole: bool) -> SetObject:
        """The top (``whole``) or bottom chosen subset of the base set, retained per power object."""
        return self.retained_datum(power).subset_from(lambda datum: whole)

    @retained_method
    def inverse_image_morphism(self, power: SetObject, set_map: SetMap) -> SetMap:
        sets = _sets.Sets()
        base_set = self.retained_datum(power)
        assert set_map in sets.morphism_category(1) and set_map.codomain() is base_set, f"{set_map!r} does not end at {base_set!r}"
        return sets.morphism_category(1)(power, self(set_map.domain()))(lambda name: Function(name.map() * set_map))

    @retained_method
    def direct_image_morphism(self, power: SetObject, set_map: SetMap) -> SetMap:
        sets = _sets.Sets()
        base_set = self.retained_datum(power)
        assert set_map in sets.morphism_category(1) and set_map.domain() is base_set, f"{set_map!r} does not start at {base_set!r}"

        def image_name(name: Datum) -> Datum:
            subset = self.subset_of_characteristic_morphism(power, name.map())
            return Function((set_map * subset.monomorphism()).image().characteristic_morphism())

        return sets.morphism_category(1)(power, self(set_map.codomain()))(image_name)
