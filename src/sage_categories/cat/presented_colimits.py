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


def presented_colimit_in_opposite(
    dual_diagram: Functor,
) -> CategoryOfCategories.ElementType:
    """Selected finite presented colimit, computed by native presentation engines."""
    diagram = dual_diagram.op()
    shape = diagram.domain()
    if isinstance(shape, FinitePresentedCategory):
        vertices = tuple(shape(label) for label in shape.labels())
        edges = shape.generating_morphisms()
    else:
        finite = finite_category(shape)
        assert finite is not Unknown, (
            "colimit evaluation requires an exact finite index category"
        )
        vertices, edges = finite.objects, finite.morphisms

    factors = tuple(diagram.on_object(vertex) for vertex in vertices)
    assert all(isinstance(factor, FinitePresentedCategory) for factor in factors), (
        "colimit evaluation requires presented factor categories"
    )
    factor_objects = tuple(
        tuple(factor(label) for label in factor.labels()) for factor in factors
    )

    class_count, object_classes = category_limits.identified_objects(
        vertices,
        edges,
        factor_objects,
        lambda edge, value: diagram.on_morphism(edge).on_object(value),
        position,
    )

    def vertex_class(index: int, value: CategoryOfCategories.ElementType) -> int:
        return object_classes[index][position(factor_objects[index], value)]

    coproduct = catlab.presented_coproduct(factors)
    coproduct_objects, coproduct_homs, inherited_relations = (
        catlab.presented_coproduct_data(coproduct)
    )
    coproduct_object_classes: dict[str, int] = {}
    for factor_index, objects in enumerate(factor_objects):
        for object_index, value in enumerate(objects):
            native_name = catlab.presented_coproduct_object_image(
                coproduct, factor_index, object_index
            )
            selected_class = object_classes[factor_index][object_index]
            if native_name in coproduct_object_classes:
                assert coproduct_object_classes[native_name] == selected_class
            else:
                coproduct_object_classes[native_name] = selected_class
    assert set(coproduct_object_classes) == set(coproduct_objects)

    generators = tuple(
        (
            name,
            coproduct_object_classes[source],
            coproduct_object_classes[target],
        )
        for name, source, target in coproduct_homs
    )

    generator_origins: dict[str, tuple[int, str]] = {}
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
            assert len(image) == 1, (
                "a coproduct inclusion must carry a source generator to one target generator"
            )
            generator_origins[image[0]] = (factor_index, name)
    assert set(generator_origins) == {name for name, _, _ in coproduct_homs}

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
            if left != right:
                relations.append((left, right))

    colimit = FinitePresentedCategory(
        "Colimit",
        tuple(range(class_count)),
        generators,
        tuple(relations),
    )

    def injection(index: int) -> Functor:
        factor = factors[index]

        def on_object(
            value: CategoryOfCategories.ElementType,
        ) -> CategoryOfCategories.ElementType:
            return colimit(vertex_class(index, value))

        def on_morphism(
            morphism: MorphismCategory.ObjectType,
        ) -> MorphismCategory.ObjectType:
            word = catlab.presented_coproduct_path_image(
                coproduct,
                factors,
                index,
                morphism.word(),
                morphism.domain(),
            )
            return colimit.construct_morphism(
                on_object(morphism.domain()),
                on_object(morphism.codomain()),
                word,
            )

        return Fun(factor, colimit)(on_object, on_morphism)

    injections = tuple(injection(index) for index in range(len(factors)))

    representatives: list[tuple[int, CategoryOfCategories.ElementType] | None] = [
        None
    ] * class_count
    for factor_index, objects in enumerate(factor_objects):
        for object_index, value in enumerate(objects):
            selected_class = object_classes[factor_index][object_index]
            if representatives[selected_class] is None:
                representatives[selected_class] = (factor_index, value)
    assert all(representative is not None for representative in representatives)

    def mediator(candidate: NaturalTransformation) -> MorphismCategory.ObjectType:
        target = cone_apex(candidate)
        legs = tuple(
            opposite_morphism(candidate.component(vertex)) for vertex in vertices
        )
        object_images = tuple(
            legs[representative[0]].on_object(representative[1])
            for representative in representatives
            if representative is not None
        )
        generator_images = tuple(
            legs[generator_origins[name][0]].on_morphism(
                factors[generator_origins[name][0]].generator(
                    generator_origins[name][1]
                )
            )
            for name in colimit.generator_names()
        )
        native = catlab.presented_functor(
            colimit,
            target,
            object_images,
            generator_images,
        )

        def on_object(
            value: CategoryOfCategories.ElementType,
        ) -> CategoryOfCategories.ElementType:
            return object_images[colimit.label(value)]

        def on_morphism(
            morphism: MorphismCategory.ObjectType,
        ) -> MorphismCategory.ObjectType:
            return catlab.presented_functor_morphism_image(native, colimit, morphism)

        return opposite_morphism(Fun(colimit, target)(on_object, on_morphism))

    family = Cat().op().Limits(dual_diagram.domain())
    return family.with_universal_data(
        dual_diagram,
        colimit,
        cone(
            dual_diagram,
            colimit,
            lambda vertex: opposite_morphism(injections[position(vertices, vertex)]),
        ),
        mediator,
    )
