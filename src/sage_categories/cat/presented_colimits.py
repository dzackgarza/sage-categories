"""Native colimits of finite diagrams of finitely presented categories."""

from __future__ import annotations

from sage_categories.cat.canonical import FinitePresentedCategory
from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.cones import cone, cone_apex
from sage_categories.cat.finite_categories import finite_category, position
from sage_categories.cat.functors import Cat, Fun, Functor, NaturalTransformation
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.opposites import opposite_morphism
from sage_categories.cat.predicates import Unknown
from sage_categories.engines import category_limits, catlab

__all__ = ["presented_colimit_in_opposite"]


def _finite_shape_data(
    shape: CategoryOfCategories.ElementType,
) -> tuple[
    tuple[CategoryOfCategories.ElementType, ...],
    tuple[MorphismCategory.ObjectType, ...],
]:
    """The exact finite vertices and arrows of one colimit indexing shape."""
    match shape:
        case FinitePresentedCategory():
            return tuple(shape(label) for label in shape.labels()), shape.generating_morphisms()
        case _:
            finite = finite_category(shape)
            assert finite is not Unknown, "colimit evaluation requires an exact finite index category"
            return finite.objects, finite.morphisms


def _coproduct_object_classes(
    coproduct: object,
    factor_objects: tuple[tuple[CategoryOfCategories.ElementType, ...], ...],
    object_classes: tuple[tuple[int, ...], ...],
) -> dict[str, int]:
    """Match Catlab coproduct object names to the selected quotient object classes."""
    result: dict[str, int] = {}
    for factor_index, objects in enumerate(factor_objects):
        for object_index, _value in enumerate(objects):
            native_name = catlab.presented_coproduct_object_image(coproduct, factor_index, object_index)
            selected_class = object_classes[factor_index][object_index]
            match native_name in result:
                case True:
                    assert result[native_name] == selected_class
                case False:
                    result[native_name] = selected_class
    return result


def _generator_origins(
    coproduct: object,
    factors: tuple[CategoryOfCategories.ElementType, ...],
) -> dict[str, tuple[int, str]]:
    """Record which presented factor generator produced each coproduct generator."""
    origins: dict[str, tuple[int, str]] = {}
    for factor_index, factor in enumerate(factors):
        for name in factor.generator_names():
            generator = factor.generator(name)
            image = catlab.presented_coproduct_path_image(
                coproduct,
                factors,
                factor_index,
                generator.word(),
                generator.domain(),
            )
            assert len(image) == 1, "a coproduct inclusion must carry a source generator to one target generator"
            origins[image[0]] = (factor_index, name)
    return origins


def _diagram_relations(
    diagram: Functor,
    vertices: tuple[CategoryOfCategories.ElementType, ...],
    edges: tuple[MorphismCategory.ObjectType, ...],
    factors: tuple[CategoryOfCategories.ElementType, ...],
    coproduct: object,
    inherited_relations: tuple[object, ...],
) -> tuple[object, ...]:
    """Add the relations imposed by every arrow of the indexing diagram."""
    relations = list(inherited_relations)
    for edge in edges:
        first = position(vertices, edge.domain())
        second = position(vertices, edge.codomain())
        functor = diagram.on_morphism(edge)
        for name in factors[first].generator_names():
            generator = factors[first].generator(name)
            left = catlab.presented_coproduct_path_image(
                coproduct,
                factors,
                first,
                generator.word(),
                generator.domain(),
            )
            image = functor.on_morphism(generator)
            right = catlab.presented_coproduct_path_image(
                coproduct,
                factors,
                second,
                image.word(),
                image.domain(),
            )
            match left == right:
                case True:
                    pass
                case False:
                    relations.append((left, right))
    return tuple(relations)


def _colimit_injection(
    index: int,
    factor: CategoryOfCategories.ElementType,
    colimit: FinitePresentedCategory,
    object_classes: tuple[tuple[int, ...], ...],
    factor_objects: tuple[tuple[CategoryOfCategories.ElementType, ...], ...],
    coproduct: object,
    factors: tuple[CategoryOfCategories.ElementType, ...],
) -> Functor:
    """The selected inclusion of one presented factor into the presented colimit."""

    def on_object(value: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
        return colimit(_vertex_class(object_classes, factor_objects, index, value))

    def on_morphism(morphism: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        word = catlab.presented_coproduct_path_image(
            coproduct,
            factors,
            index,
            morphism.word(),
            morphism.domain(),
        )
        return colimit.construct_morphism(on_object(morphism.domain()), on_object(morphism.codomain()), word)

    return Fun(factor, colimit)(on_object, on_morphism)


def _class_representatives(
    class_count: int,
    factor_objects: tuple[tuple[CategoryOfCategories.ElementType, ...], ...],
    object_classes: tuple[tuple[int, ...], ...],
) -> tuple[tuple[int, CategoryOfCategories.ElementType], ...]:
    """Choose one owned factor object representing each quotient object class."""
    representatives: list[tuple[int, CategoryOfCategories.ElementType] | None] = [None] * class_count
    for factor_index, objects in enumerate(factor_objects):
        for object_index, value in enumerate(objects):
            selected_class = object_classes[factor_index][object_index]
            match representatives[selected_class]:
                case None:
                    representatives[selected_class] = (factor_index, value)
                case _:
                    pass
    assert all(representative is not None for representative in representatives)
    return tuple(representative for representative in representatives if representative is not None)


def _factor_presentations(
    diagram: Functor,
    vertices: tuple[CategoryOfCategories.ElementType, ...],
) -> tuple[
    tuple[CategoryOfCategories.ElementType, ...],
    tuple[tuple[CategoryOfCategories.ElementType, ...], ...],
]:
    """The presented factors of ``diagram`` and their exact finite object families."""
    factors = tuple(diagram.on_object(vertex) for vertex in vertices)
    assert all(isinstance(factor, FinitePresentedCategory) for factor in factors), "colimit evaluation requires presented factor categories"
    return factors, tuple(tuple(factor(label) for label in factor.labels()) for factor in factors)


def _quotient_object_classes(
    diagram: Functor,
    vertices: tuple[CategoryOfCategories.ElementType, ...],
    edges: tuple[MorphismCategory.ObjectType, ...],
    factor_objects: tuple[tuple[CategoryOfCategories.ElementType, ...], ...],
) -> tuple[int, tuple[tuple[int, ...], ...]]:
    """The object quotient imposed by the indexing diagram."""
    return category_limits.identified_objects(
        vertices,
        edges,
        factor_objects,
        lambda edge, value: diagram.on_morphism(edge).on_object(value),
        position,
    )


def _vertex_class(
    object_classes: tuple[tuple[int, ...], ...],
    factor_objects: tuple[tuple[CategoryOfCategories.ElementType, ...], ...],
    index: int,
    value: CategoryOfCategories.ElementType,
) -> int:
    """The quotient object class of one object in one presented factor."""
    return object_classes[index][position(factor_objects[index], value)]


def _presented_colimit_category(
    diagram: Functor,
    vertices: tuple[CategoryOfCategories.ElementType, ...],
    edges: tuple[MorphismCategory.ObjectType, ...],
    factors: tuple[CategoryOfCategories.ElementType, ...],
    factor_objects: tuple[tuple[CategoryOfCategories.ElementType, ...], ...],
    class_count: int,
    object_classes: tuple[tuple[int, ...], ...],
) -> tuple[FinitePresentedCategory, object, dict[str, tuple[int, str]]]:
    """Build the selected quotient presentation after object classes are fixed."""
    coproduct = catlab.presented_coproduct(factors)
    coproduct_objects, coproduct_homs, inherited_relations = catlab.presented_coproduct_data(coproduct)
    coproduct_object_classes = _coproduct_object_classes(coproduct, factor_objects, object_classes)
    assert set(coproduct_object_classes) == set(coproduct_objects)
    generators = tuple((name, coproduct_object_classes[source], coproduct_object_classes[target]) for name, source, target in coproduct_homs)
    generator_origins = _generator_origins(coproduct, factors)
    assert set(generator_origins) == {name for name, _, _ in coproduct_homs}
    relations = _diagram_relations(diagram, vertices, edges, factors, coproduct, inherited_relations)
    return FinitePresentedCategory("Colimit", tuple(range(class_count)), generators, relations), coproduct, generator_origins


def _colimit_mediator(
    candidate: NaturalTransformation,
    *,
    vertices: tuple[CategoryOfCategories.ElementType, ...],
    representatives: tuple[tuple[int, CategoryOfCategories.ElementType], ...],
    generator_origins: dict[str, tuple[int, str]],
    factors: tuple[CategoryOfCategories.ElementType, ...],
    colimit: FinitePresentedCategory,
) -> MorphismCategory.ObjectType:
    """Factor one cocone through the selected presented colimit."""
    target = cone_apex(candidate)
    legs = tuple(opposite_morphism(candidate.component(vertex)) for vertex in vertices)
    object_images = tuple(legs[factor_index].on_object(value) for factor_index, value in representatives)
    generator_images = tuple(
        legs[generator_origins[name][0]].on_morphism(factors[generator_origins[name][0]].generator(generator_origins[name][1])) for name in colimit.generator_names()
    )
    native = catlab.presented_functor(colimit, target, object_images, generator_images)

    def on_object(value: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
        return object_images[colimit.label(value)]

    def on_morphism(morphism: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        return catlab.presented_functor_morphism_image(native, colimit, morphism)

    return opposite_morphism(Fun(colimit, target)(on_object, on_morphism))


def presented_colimit_in_opposite(
    dual_diagram: Functor,
) -> CategoryOfCategories.ElementType:
    """Selected finite presented colimit, computed by native presentation engines."""
    diagram = dual_diagram.op()
    shape = diagram.domain()
    vertices, edges = _finite_shape_data(shape)
    factors, factor_objects = _factor_presentations(diagram, vertices)
    class_count, object_classes = _quotient_object_classes(diagram, vertices, edges, factor_objects)
    colimit, coproduct, generator_origins = _presented_colimit_category(
        diagram,
        vertices,
        edges,
        factors,
        factor_objects,
        class_count,
        object_classes,
    )
    injections = tuple(_colimit_injection(index, factors[index], colimit, object_classes, factor_objects, coproduct, factors) for index in range(len(factors)))
    representatives = _class_representatives(class_count, factor_objects, object_classes)

    family = Cat().op().Limits(dual_diagram.domain())
    return family.with_universal_data(
        dual_diagram,
        colimit,
        cone(
            dual_diagram,
            colimit,
            lambda vertex: opposite_morphism(injections[position(vertices, vertex)]),
        ),
        lambda candidate: _colimit_mediator(
            candidate,
            vertices=vertices,
            representatives=representatives,
            generator_origins=generator_origins,
            factors=factors,
            colimit=colimit,
        ),
    )
