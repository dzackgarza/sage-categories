"""Finite scalar-general module presentations through the generic module owner.

A relation matrix presents a morphism ``R^m -> R^n`` between the retained finite
free left modules.  Rows are indexed by the target basis and columns by the source
basis, exactly as in ``finite_free_matrix_morphism``; consequently an entry acts on
source coefficients on the right, which is the correct convention for left modules
over a possibly noncommutative scalar ring.

The presented module is the actual coequalizer of that relation map and the zero
map in the supplied ``Modules(R, C)``.  Its underlying additive carrier is computed
by the existing ``Ab`` coequalizer owner, its scalar action is descended along that
quotient, and the module-category coequalizer retains the same diagram, projection,
and universal mediator.
"""

from __future__ import annotations

from sage_categories.algebra._firewall.abelian import colift_along_epimorphism
from sage_categories.algebra.abelian import AbelianGroups
from sage_categories.algebra.free_modules import (
    finite_free_matrix_morphism,
    finite_free_module,
)
from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.choices import ChosenConstruction
from sage_categories.cat.cones import LimitConesCategory
from sage_categories.cat.functors import Cat, Functor
from sage_categories.cat.limit_basis import coequalizer_factor, parallel_pair
from sage_categories.cat.modules import ModuleCategory
from sage_categories.cat.monoidal import tensor_morphism
from sage_categories.cat.morphisms import Mor, MorphismCategory

__all__ = [
    "finitely_presented_module",
    "presented_module_diagram",
    "presented_module_factor",
    "presented_module_presentation",
    "presented_module_projection",
    "presented_module_relation",
    "presented_module_zero",
    "relation_matrix_morphism",
]

_FINITE_MODULE_PRESENTATIONS = ChosenConstruction()


type ModuleMap = MorphismCategory.ObjectType
type RelationMatrix = tuple[tuple[CategoryOfCategories.ElementType, ...], ...]


def _normalized_matrix(entries: RelationMatrix) -> RelationMatrix:
    rows = tuple(tuple(row) for row in entries)
    match rows:
        case ():
            raise ValueError("a finite relation matrix requires positive source and target ranks")
        case _:
            pass
    width = len(rows[0])
    match width == 0:
        case True:
            raise ValueError("a finite relation matrix requires positive source and target ranks")
        case False:
            pass
    match any(len(row) != width for row in rows):
        case True:
            raise ValueError("a relation matrix has one common source rank")
        case False:
            return rows


def relation_matrix_morphism(
    modules: ModuleCategory,
    entries: RelationMatrix,
) -> ModuleMap:
    """The left-module map ``R^m -> R^n`` represented by ``entries``.

    ``entries`` has ``n`` rows and ``m`` columns.  The finite-free owner supplies both
    modules and interprets each entry with the left-module/right-coefficient convention.
    """
    rows = _normalized_matrix(entries)
    source = finite_free_module(modules, len(rows[0]))
    target = finite_free_module(modules, len(rows))
    return finite_free_matrix_morphism(modules, source, target, rows)


def _zero_morphism(
    modules: ModuleCategory,
    source: ModuleCategory.ObjectType,
    target: ModuleCategory.ObjectType,
) -> ModuleMap:
    underlying = modules.forgetful()
    additive = modules.underlying_category().zero_morphism(
        underlying.on_object(source),
        underlying.on_object(target),
    )
    return modules.homomorphism(source, target, additive)


def _new_presented_module(
    modules: ModuleCategory,
    relation: ModuleMap,
    zero: ModuleMap,
) -> ModuleCategory.ObjectType:
    """Construct and retain the module coequalizer of ``relation`` and ``zero``."""
    assert relation.domain() is zero.domain() and relation.codomain() is zero.codomain()
    shape = Cat().WalkingParallelPair()
    forgetful = modules.forgetful()
    if forgetful.colimit_lifting(shape) is None:
        forgetful.with_colimit_lifting(
            shape,
            lambda diagram, presentation: _coequalizer_apex(modules, diagram, presentation),
            modules.homomorphism,
        )
    diagram = parallel_pair(relation, zero)
    result = modules.Colimits(shape)(diagram)
    assert result in modules
    return result


def _coequalizer_apex(
    modules: ModuleCategory,
    diagram: Functor,
    presentation: LimitConesCategory.ObjectType,
) -> ModuleCategory.ObjectType:
    """Lift the additive coequalizer apex by descending the scalar action."""
    target_vertex = Cat().WalkingParallelPair()(1)
    target_module = diagram.on_object(target_vertex)
    additive_projection = presentation.leg(target_vertex)

    scalar = modules.carrier()
    abelian = AbelianGroups()
    scalar_identity = Mor(abelian)(scalar, scalar).one()
    action = modules.actegory().action()
    tensorized_projection = tensor_morphism(action, scalar_identity, additive_projection)
    descended_action: ModuleMap = colift_along_epimorphism(
        tensorized_projection,
        additive_projection * target_module.action(),
    )
    return modules(descended_action)


def finitely_presented_module(
    modules: ModuleCategory,
    entries: RelationMatrix,
) -> ModuleCategory.ObjectType:
    """The module presented by the finite relation matrix ``R^m -> R^n``."""
    relation = relation_matrix_morphism(modules, entries)
    zero = _zero_morphism(modules, relation.domain(), relation.codomain())
    result: ModuleCategory.ObjectType = _FINITE_MODULE_PRESENTATIONS(modules, (relation, zero), lambda: _new_presented_module(modules, relation, zero))
    return result


def presented_module_diagram(
    modules: ModuleCategory,
    module: ModuleCategory.ObjectType,
) -> Functor:
    """The retained parallel-pair diagram presenting ``module``."""
    family = modules.Colimits(Cat().WalkingParallelPair())
    diagrams = family.presenting_diagrams(module)
    assert len(diagrams) == 1, f"{module!r} has {len(diagrams)} retained module coequalizer presentations"
    diagram: Functor = diagrams[0]
    return diagram


def presented_module_presentation(
    modules: ModuleCategory,
    module: ModuleCategory.ObjectType,
) -> LimitConesCategory.ObjectType:
    """The retained module-category coequalizer presentation of ``module``."""
    diagram = presented_module_diagram(modules, module)
    presentation: LimitConesCategory.ObjectType = modules.Colimits(diagram.domain()).universal_data(diagram)
    return presentation


def presented_module_relation(
    modules: ModuleCategory,
    module: ModuleCategory.ObjectType,
) -> ModuleMap:
    """The relation morphism ``R^m -> R^n`` retained by ``module``."""
    diagram = presented_module_diagram(modules, module)
    relation: ModuleMap = diagram.on_morphism(Cat().WalkingParallelPair().generator("f"))
    return relation


def presented_module_zero(
    modules: ModuleCategory,
    module: ModuleCategory.ObjectType,
) -> ModuleMap:
    """The zero morphism parallel to the retained relation morphism."""
    diagram = presented_module_diagram(modules, module)
    zero: ModuleMap = diagram.on_morphism(Cat().WalkingParallelPair().generator("g"))
    return zero


def presented_module_projection(
    modules: ModuleCategory,
    module: ModuleCategory.ObjectType,
) -> ModuleMap:
    """The universal projection ``R^n -> module`` of the retained coequalizer."""
    presentation = presented_module_presentation(modules, module)
    projection: ModuleMap = presentation.leg(Cat().WalkingParallelPair()(1))
    return projection


def presented_module_factor(
    modules: ModuleCategory,
    module: ModuleCategory.ObjectType,
    target: ModuleCategory.ObjectType,
    coequalizing: ModuleMap,
) -> ModuleMap:
    """The unique factor of a relation-respecting map ``R^n -> target`` through ``module``."""
    relation = presented_module_relation(modules, module)
    assert coequalizing.domain() is relation.codomain() and coequalizing.codomain() is target
    factor: ModuleMap = coequalizer_factor(
        presented_module_presentation(modules, module),
        coequalizing,
    )
    return factor
