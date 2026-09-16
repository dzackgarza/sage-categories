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
from sage_categories.algebra.abelian import (
    AbelianGroups,
    coequalizer_mediator,
    coequalizer_projection,
)
from sage_categories.algebra.free_modules import (
    finite_free_matrix_morphism,
    finite_free_module,
)
from sage_categories.cat.assembly import chosen_construction
from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.cones import ConeCategory, LimitConesCategory, cocone, cocones
from sage_categories.cat.functors import Cat, Functor
from sage_categories.cat.limit_basis import parallel_pair
from sage_categories.cat.modules import ModuleCategory
from sage_categories.cat.monoidal import tensor_morphism
from sage_categories.cat.morphisms import Mor, MorphismCategory
from sage_categories.cat.predicates import ask

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
    forgetful = modules.forgetful()
    additive_relation = forgetful.on_morphism(relation)
    additive_zero = forgetful.on_morphism(zero)
    additive_projection = coequalizer_projection(additive_relation, additive_zero)

    scalar = modules.carrier()
    abelian = AbelianGroups()
    scalar_identity = Mor(abelian)(scalar, scalar).one()
    action = modules.actegory().action()
    tensorized_projection = tensor_morphism(action, scalar_identity, additive_projection)
    descended_action: ModuleMap = colift_along_epimorphism(
        tensorized_projection,
        additive_projection * relation.codomain().action(),
    )
    quotient: ModuleCategory.ObjectType = modules(descended_action)
    projection = modules.homomorphism(relation.codomain(), quotient, additive_projection)

    diagram = parallel_pair(relation, zero)
    shape = Cat().WalkingParallelPair()
    source_vertex, target_vertex = shape(0), shape(1)
    assert ask(projection * relation == projection * zero) is True

    def selected_leg(vertex: CategoryOfCategories.ElementType) -> ModuleMap:
        match vertex is source_vertex:
            case True:
                return projection * relation
            case False:
                return projection

    selected = cocone(diagram, quotient, selected_leg)

    def mediator(candidate: ConeCategory.ObjectType) -> ModuleMap:
        arrow = candidate.leg(target_vertex)
        additive = coequalizer_mediator(
            additive_projection,
            forgetful.on_morphism(arrow),
        )
        return modules.homomorphism(quotient, candidate.apex(), additive)

    retained = modules.Colimits(shape).with_universal_data(
        diagram,
        quotient,
        selected,
        mediator,
    )
    assert retained is quotient
    return quotient


def finitely_presented_module(
    modules: ModuleCategory,
    entries: RelationMatrix,
) -> ModuleCategory.ObjectType:
    """The module presented by the finite relation matrix ``R^m -> R^n``."""
    relation = relation_matrix_morphism(modules, entries)
    zero = _zero_morphism(modules, relation.domain(), relation.codomain())
    result: ModuleCategory.ObjectType = chosen_construction(
        modules,
        "finite-module-presentation",
        (relation, zero),
        lambda: _new_presented_module(modules, relation, zero),
    )
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
    diagram = presented_module_diagram(modules, module)
    relation = presented_module_relation(modules, module)
    zero = presented_module_zero(modules, module)
    assert coequalizing.domain() is relation.codomain() and coequalizing.codomain() is target
    assert ask(coequalizing * relation == coequalizing * zero) is True, "the supplied map does not respect the retained module relations"
    shape = diagram.domain()
    source_vertex = shape(0)
    def candidate_leg(vertex: CategoryOfCategories.ElementType) -> ModuleMap:
        match vertex is source_vertex:
            case True:
                return coequalizing * relation
            case False:
                return coequalizing

    candidate = cocones(diagram)(cocone(diagram, target, candidate_leg))
    factor: ModuleMap = presented_module_presentation(modules, module).lift(candidate)
    return factor
