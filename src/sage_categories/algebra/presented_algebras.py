"""Free and presented algebras in the base-relative algebra owner.

The algebra category owns the presentation.  Concrete free-algebra arithmetic remains
behind its leaf firewall; this module only reconstructs owned algebra objects/maps and
retains quotient data as an actual coequalizer in ``Algebras(R,C)``.
"""

from __future__ import annotations

from collections.abc import Sequence

from sage_categories.algebra._firewall import free_associative as _free_backend
from sage_categories.algebra.abelian import (
    balanced_tensor,
    integer_group,
    relative_tensor,
)
from sage_categories.algebra.algebras import AlgebraCategory
from sage_categories.algebra.free_associative import (
    IntegerFreeAssociativeConstruction,
    integer_free_associative_algebra,
)
from sage_categories.algebra.indexed_modules import (
    indexed_free_integer_element,
    indexed_free_integer_homomorphism,
)
from sage_categories.cat.assembly import chosen_construction
from sage_categories.cat.category import CategoryOfCategories, ask
from sage_categories.cat.cones import ConeCategory, LimitConesCategory, cocone, cocones
from sage_categories.cat.functors import Cat, Functor
from sage_categories.cat.limit_basis import parallel_pair
from sage_categories.cat.structured_objects import Magmas

__all__ = [
    "integer_free_algebra",
    "integer_free_algebra_generator",
    "integer_free_algebra_homomorphism",
    "presented_algebra_diagram",
    "presented_algebra_factor",
    "presented_algebra_presentation",
    "presented_algebra_projection",
    "retain_split_algebra_presentation",
]

type AlgebraMap = AlgebraCategory.MorphismType


def integer_free_algebra(
    algebras: AlgebraCategory,
    names: Sequence[str],
) -> AlgebraCategory.ObjectType:
    """Read Sage's native ``ZZ<names>`` evaluator through this exact algebra owner.

    The evaluator remains the existing concrete ``ZZ`` realization.  The public value is
    the corresponding object of ``algebras`` rather than the raw monoid presentation.
    """
    neutral = integer_free_associative_algebra(names)
    assert neutral in algebras.monoid_category(), (
        f"the native integer free algebra belongs to {neutral.category()!r}, not {algebras.monoid_category()!r}"
    )
    return algebras.from_monoid(neutral)


def _free_construction(
    algebras: AlgebraCategory,
    algebra: AlgebraCategory.ObjectType,
) -> IntegerFreeAssociativeConstruction:
    neutral = algebras.monoid_presentation().on_object(algebra)
    construction = _free_backend.construction(neutral)
    assert isinstance(construction, IntegerFreeAssociativeConstruction)
    return construction


def integer_free_algebra_generator(
    algebras: AlgebraCategory,
    algebra: AlgebraCategory.ObjectType,
    position: int,
) -> CategoryOfCategories.ElementType:
    """The selected free generator as an element of the algebra's full module."""
    construction = _free_construction(algebras, algebra)
    position = int(position)
    assert 0 <= position < len(construction.names)
    module = algebras.to_modules().on_object(algebra)
    source_point = indexed_free_integer_element(
        construction.word_module,
        _free_backend.generator(
            algebras.monoid_presentation().on_object(algebra),
            position,
        ),
    )
    return module.point(source_point.datum())


def _relative_carrier(
    algebras: AlgebraCategory,
    algebra: AlgebraCategory.ObjectType,
) -> CategoryOfCategories.ElementType:
    monoid = algebras.monoid_presentation().on_object(algebra)
    monoids = algebras.monoid_category()
    magma = monoids.to_magmas().on_object(monoid)
    return Magmas(algebras.monoidal_structure()).forgetful().on_object(magma)


def _integer_algebra_one(
    algebras: AlgebraCategory,
    algebra: AlgebraCategory.ObjectType,
) -> CategoryOfCategories.ElementType:
    monoid = algebras.monoid_presentation().on_object(algebra)
    bimodules = algebras.monoidal_structure().underlying_category()
    unit_carrier = bimodules.forgetful().on_object(algebras.monoidal_structure().unit())
    assert unit_carrier is integer_group()
    underlying = bimodules.forgetful().on_morphism(monoid.unit_morphism())
    module = algebras.to_modules().on_object(algebra)
    return module.point(underlying(unit_carrier.point(1)).datum())


def _integer_algebra_product(
    algebras: AlgebraCategory,
    algebra: AlgebraCategory.ObjectType,
    first: CategoryOfCategories.ElementType,
    second: CategoryOfCategories.ElementType,
) -> CategoryOfCategories.ElementType:
    module = algebras.to_modules().on_object(algebra)
    assert first.parent() is module and second.parent() is module
    monoid = algebras.monoid_presentation().on_object(algebra)
    structure = algebras.monoidal_structure()
    bimodules = structure.underlying_category()
    carrier = _relative_carrier(algebras, algebra)
    projection = relative_tensor(carrier.right_action(), carrier.left_action())
    balanced = balanced_tensor(projection, first.datum(), second.datum())
    operation = bimodules.forgetful().on_morphism(monoid.operation())
    return module.point(operation(balanced).datum())


def integer_free_algebra_homomorphism(
    algebras: AlgebraCategory,
    source: AlgebraCategory.ObjectType,
    target: AlgebraCategory.ObjectType,
    generator_images: Sequence[CategoryOfCategories.ElementType],
) -> AlgebraCategory.MorphismType:
    """The algebra map from a free integer algebra with these generator images.

    The source's indexed-free module supplies the linear extension.  Basis words are
    interpreted only through the target algebra's retained unit and multiplication, so
    the target need not share the source's native free-algebra representation.
    """
    construction = _free_construction(algebras, source)
    images = tuple(generator_images)
    assert len(images) == len(construction.names), (
        "one image is required for every free generator"
    )
    source_module = algebras.to_modules().on_object(source)
    target_module = algebras.to_modules().on_object(target)
    assert all(image.parent() is target_module for image in images)

    def basis_image(word: object) -> CategoryOfCategories.ElementType:
        assert isinstance(word, tuple)
        result = _integer_algebra_one(algebras, target)
        for position in word:
            assert isinstance(position, int) and 0 <= position < len(images)
            result = _integer_algebra_product(
                algebras, target, result, images[position]
            )
        return result

    linear = indexed_free_integer_homomorphism(
        source_module,
        target_module,
        basis_image,
    )
    bimodules = algebras.monoidal_structure().underlying_category()
    carrier_map = algebras.module_category().forgetful().on_morphism(linear)
    bimodule_map = bimodules.homomorphism(
        _relative_carrier(algebras, source),
        _relative_carrier(algebras, target),
        carrier_map,
    )
    return algebras.homomorphism(source, target, bimodule_map)


def _new_split_algebra_presentation(
    algebras: AlgebraCategory,
    first: AlgebraMap,
    second: AlgebraMap,
    projection: AlgebraMap,
    section: AlgebraMap,
) -> AlgebraCategory.ObjectType:
    """Retain a supplied split coequalizer as universal data in ``algebras``."""
    assert first.domain() is second.domain() and first.codomain() is second.codomain()
    assert first in algebras.morphism_category(
        1
    ) and second in algebras.morphism_category(1)
    quotient = projection.codomain()
    target = first.codomain()
    assert projection.domain() is target and quotient in algebras
    assert section.domain() is quotient and section.codomain() is target
    assert section in algebras.morphism_category(1)
    assert ask(projection * first == projection * second) is True
    assert (
        ask(
            projection * section
            == algebras.morphism_category(1)(quotient, quotient).one()
        )
        is True
    )

    diagram = parallel_pair(first, second)
    shape = diagram.domain()
    source_vertex, target_vertex = shape(0), shape(1)

    def selected_leg(vertex: CategoryOfCategories.ElementType) -> AlgebraMap:
        match vertex is source_vertex:
            case True:
                return projection * first
            case False:
                return projection

    selected = cocone(diagram, quotient, selected_leg)

    def mediator(candidate: ConeCategory.ObjectType) -> AlgebraMap:
        coequalizing = candidate.leg(target_vertex)
        factor = coequalizing * section
        assert ask(factor * projection == coequalizing) is True, (
            "the supplied split quotient does not factor this coequalizing algebra map"
        )
        return factor

    retained = algebras.Colimits(shape).with_universal_data(
        diagram,
        quotient,
        selected,
        mediator,
    )
    assert retained is quotient
    return quotient


def retain_split_algebra_presentation(
    algebras: AlgebraCategory,
    first: AlgebraMap,
    second: AlgebraMap,
    projection: AlgebraMap,
    section: AlgebraMap,
) -> AlgebraCategory.ObjectType:
    """Retain a split algebra quotient of the actual relation pair ``first, second``.

    Engine-specific quotient construction may supply the projection and a splitting in
    any concrete evaluation domain.  The mathematical result is stored only as the
    ordinary coequalizer presentation of the exact base-relative algebra category.
    """
    return chosen_construction(
        algebras,
        "split-algebra-presentation",
        (first, second, projection, section),
        lambda: _new_split_algebra_presentation(
            algebras,
            first,
            second,
            projection,
            section,
        ),
    )


def presented_algebra_diagram(
    algebras: AlgebraCategory,
    algebra: AlgebraCategory.ObjectType,
) -> Functor:
    """The retained parallel pair presenting ``algebra``."""
    family = algebras.Colimits(Cat().WalkingParallelPair())
    diagrams = family.presenting_diagrams(algebra)
    assert len(diagrams) == 1, (
        f"{algebra!r} has {len(diagrams)} retained algebra presentations"
    )
    return diagrams[0]


def presented_algebra_presentation(
    algebras: AlgebraCategory,
    algebra: AlgebraCategory.ObjectType,
) -> LimitConesCategory.ObjectType:
    """The retained coequalizer presentation of ``algebra``."""
    diagram = presented_algebra_diagram(algebras, algebra)
    return algebras.Colimits(diagram.domain()).universal_data(diagram)


def presented_algebra_projection(
    algebras: AlgebraCategory,
    algebra: AlgebraCategory.ObjectType,
) -> AlgebraMap:
    """The universal quotient map of the retained algebra presentation."""
    presentation = presented_algebra_presentation(algebras, algebra)
    return presentation.leg(presentation.diagram().domain()(1))


def presented_algebra_factor(
    algebras: AlgebraCategory,
    algebra: AlgebraCategory.ObjectType,
    target: AlgebraCategory.ObjectType,
    coequalizing: AlgebraMap,
) -> AlgebraMap:
    """Factor a relation-respecting algebra map through the retained quotient."""
    diagram = presented_algebra_diagram(algebras, algebra)
    shape = diagram.domain()
    first = diagram.on_morphism(shape.generator("f"))
    second = diagram.on_morphism(shape.generator("g"))
    assert (
        coequalizing.domain() is first.codomain() and coequalizing.codomain() is target
    )
    assert ask(coequalizing * first == coequalizing * second) is True, (
        "the supplied algebra map does not respect the retained relations"
    )

    source_vertex = shape(0)

    def candidate_leg(vertex: CategoryOfCategories.ElementType) -> AlgebraMap:
        match vertex is source_vertex:
            case True:
                return coequalizing * first
            case False:
                return coequalizing

    candidate = cocones(diagram)(cocone(diagram, target, candidate_leg))
    return presented_algebra_presentation(algebras, algebra).lift(candidate)
