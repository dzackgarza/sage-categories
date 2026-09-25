"""Base-relative algebra objects as a retained presentation of monoid objects.

``Algebras(R, C)`` does not introduce another algebra implementation.  It is a
distinct base-relative category whose sole immediate structure functor is an
equivalence to ``Monoids(V_R)``, where ``V_R`` is the supplied monoidal module
or ``(R,R)``-bimodule category.  Multiplication, unit, and their preserving maps
therefore remain owned by the ordinary generic monoid construction.
"""

from __future__ import annotations

from sage_categories.cat.bimodules import BimoduleCategory
from sage_categories.cat.cat_constructions import LimitSubcategory, limit_of_categories
from sage_categories.cat.choices import ChosenConstruction
from sage_categories.cat.cones import cone, cones
from sage_categories.cat.declarations import Sets
from sage_categories.cat.diagrams import from_sequence, sequence_position
from sage_categories.cat.functors import Cat, Fun, Functor
from sage_categories.cat.modules import ModuleCategory, Modules
from sage_categories.cat.monoidal import ActionsCategory, MonoidalStructuresCategory
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.shapes import Discrete
from sage_categories.cat.structured_objects import Magmas, MonoidCategory, Monoids

__all__ = [
    "AlgebraCategory",
    "Algebras",
]


_BASE_RELATIVE_ALGEBRAS = ChosenConstruction()


class AlgebraCategory(LimitSubcategory):
    """``Algebras(R,C)`` with its retained equivalence to ``Monoids(V_R)``."""

    class ObjectType:
        pass

    class ElementType:
        pass

    class MorphismType:
        pass

    def monoid_category(self) -> MonoidCategory:
        """``Monoids(V_R)``, the category that owns all algebra operations and laws."""
        target = self.factor(0)
        assert isinstance(target, MonoidCategory)
        return target

    def monoidal_structure(self) -> MonoidalStructuresCategory.ObjectType:
        """The exact supplied relative tensor structure ``V_R``."""
        return self.monoid_category().monoidal_structure()

    def base(self) -> MonoidCategory.ObjectType:
        """The retained scalar monoid ``R``."""
        underlying = self.monoidal_structure().underlying_category()
        match underlying:
            case ModuleCategory():
                return underlying.scalars()
            case BimoduleCategory():
                left = underlying.left_modules().scalars()
                right = underlying.right_modules().scalars()
                assert right.operation() is left.operation() and right.unit_morphism() is left.unit_morphism(), f"{underlying!r} is not an (R,R)-bimodule category"
                return left
            case _:
                raise AssertionError(f"{underlying!r} is not a module or (R,R)-bimodule category")

    def module_category(self) -> ModuleCategory:
        """The left ``R``-module owner reached by the algebra's relative carrier."""
        underlying = self.monoidal_structure().underlying_category()
        match underlying:
            case ModuleCategory():
                return underlying
            case BimoduleCategory():
                return underlying.left_modules()
            case _:
                raise AssertionError(f"{underlying!r} has no retained left-module owner")

    def monoid_presentation(self) -> Functor:
        """The retained equivalence ``Algebras(R,C) -> Monoids(V_R)``."""
        return self.product_projection(0)

    def structure_functors(self) -> tuple[Functor, ...]:
        """The monoid presentation is the sole immediate structure functor."""
        return (self.monoid_presentation(),)

    def from_monoid(self, monoid: MonoidCategory.ObjectType) -> AlgebraCategory.ObjectType:
        """Read a monoid object of ``V_R`` as the corresponding base-relative algebra."""
        assert monoid in self.monoid_category()
        result = self.monoid_presentation().inverse().on_object(monoid)
        assert result in self
        return result

    def algebra(
        self,
        multiplication: MorphismCategory.ObjectType,
        unit: MorphismCategory.ObjectType,
    ) -> AlgebraCategory.ObjectType:
        """Construct the algebra whose monoid presentation has these defining maps."""
        return self.from_monoid(self.monoid_category()(multiplication, unit))

    def homomorphism(
        self,
        source: AlgebraCategory.ObjectType,
        target: AlgebraCategory.ObjectType,
        arrow: MorphismCategory.ObjectType,
    ) -> AlgebraCategory.MorphismType:
        """The algebra map over a module/bimodule map preserving multiplication and unit."""
        presentation = self.monoid_presentation()
        monoid_map = self.monoid_category().homomorphism(
            presentation.on_object(source),
            presentation.on_object(target),
            arrow,
        )
        result = presentation.inverse().on_morphism(monoid_map)
        assert result.domain() is source and result.codomain() is target
        return result

    def to_modules(self) -> Functor:
        """The retained composite from algebras to their exact left ``R``-modules."""
        monoids = self.monoid_category()
        relative = self.monoidal_structure().underlying_category()
        to_relative = Magmas(self.monoidal_structure()).forgetful() * monoids.to_magmas() * self.monoid_presentation()
        match relative:
            case ModuleCategory():
                return to_relative
            case BimoduleCategory():
                return relative.to_left() * to_relative
            case _:
                raise AssertionError(f"{relative!r} has no retained left-module forgetful route")

    def U_R(self) -> Functor:
        """The named composite from algebras through modules to the ambient category ``C``."""
        return self.module_category().forgetful() * self.to_modules()

    def to_sets(self) -> Functor:
        """The inherited concrete composite from algebras through their module owner to ``Sets``."""
        return self.module_category().functor_to_sets() * self.to_modules()


def _monoidal_context(
    base: MonoidCategory.ObjectType,
    context: ActionsCategory.ObjectType | MonoidalStructuresCategory.ObjectType,
) -> MonoidalStructuresCategory.ObjectType:
    owner = context.category()
    match owner:
        case ActionsCategory():
            modules = Modules(base, context)
            return modules.monoidal_structure()
        case MonoidalStructuresCategory():
            relative = context.underlying_category()
            match relative:
                case ModuleCategory():
                    assert relative.scalars() is base
                case BimoduleCategory():
                    assert relative.left_modules().scalars() is base
                    right = relative.right_modules().scalars()
                    assert right.operation() is base.operation() and right.unit_morphism() is base.unit_morphism()
                case _:
                    raise AssertionError(f"{relative!r} is not a relative module category for {base!r}")
            return context
        case _:
            raise AssertionError(f"{context!r} is neither an actegory nor a supplied relative monoidal structure")


def _new_algebra_category(
    monoidal: MonoidalStructuresCategory.ObjectType,
) -> AlgebraCategory:
    """Construct one distinct copy of ``Monoids(V_R)`` and retain its strict presentation inverse."""
    monoids = Monoids(monoidal)
    tag = Discrete(Sets(("base-relative-algebra",)))
    diagram = from_sequence(Cat(), (monoids, tag))
    family = Cat().Limits(diagram.domain())
    algebras = limit_of_categories(diagram, family, AlgebraCategory)
    legs = (
        Fun(monoids, monoids).one(),
        Fun(monoids, tag).constant(tag(next(iter(tag.index_set())))),
    )
    section_cone = cone(diagram, monoids, lambda vertex: legs[sequence_position(vertex)])
    section = family.universal_data(diagram).lift(cones(diagram)(section_cone))
    Cat().retain_inverses(algebras.monoid_presentation(), section)
    return algebras


def Algebras(
    base: MonoidCategory.ObjectType,
    context: ActionsCategory.ObjectType | MonoidalStructuresCategory.ObjectType,
) -> AlgebraCategory:
    """Return the base-relative algebra category for the exact supplied relative tensor context.

    With an actegory ``C``, the exact ``Modules(R,C)`` must already have its
    relative tensor selected by :meth:`ModuleCategory.select_monoidal_structure`.  A
    noncommutative base instead supplies its monoidal ``(R,R)``-bimodule category
    directly.  Both routes produce the same base-relative presentation shape.
    """
    monoidal = _monoidal_context(base, context)
    return _BASE_RELATIVE_ALGEBRAS(monoidal, (base,), lambda: _new_algebra_category(monoidal))
