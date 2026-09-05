"""Colimits of finite diagrams of finitely presented categories.

The presentation identifies objects and generating arrows along the diagram.
Its paths inherit the factor relations and the diagram relations. This is the
generators-and-relations construction of colimits in Cat; GAP KBMAG completes
the resulting path equations through the existing presented-category owner.
"""

from __future__ import annotations

from sage_categories.cat.canonical import FinitePresentedCategory
from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.cones import cone, cone_apex
from sage_categories.cat.functors import Cat, Fun, Functor, NaturalTransformation
from sage_categories.cat.finite_categories import finite_category, position
from sage_categories.cat.morphisms import Mor, MorphismCategory
from sage_categories.cat.opposites import opposite_morphism
from sage_categories.cat.predicates import Unknown
from sage_categories.kernel.sage_runtime import DisjointSet

__all__ = ["presented_colimit_in_opposite"]


def presented_colimit_in_opposite(dual_diagram: Functor) -> CategoryOfCategories.ElementType:
    diagram = dual_diagram.op()
    shape = diagram.domain()
    if isinstance(shape, FinitePresentedCategory):
        vertices = tuple(shape(label) for label in shape.labels())
        edges = shape.generating_morphisms()
    else:
        finite = finite_category(shape)
        assert finite is not Unknown, "colimit evaluation requires an exact finite index category"
        vertices, edges = finite.objects, finite.morphisms
    factors = tuple(diagram.on_object(vertex) for vertex in vertices)
    assert all(isinstance(factor, FinitePresentedCategory) for factor in factors), "colimit evaluation requires presented factor categories"
    objects = tuple((index, label) for index, factor in enumerate(factors) for label in factor.labels())
    object_indices = {datum: index for index, datum in enumerate(objects)}
    classes = DisjointSet(len(objects))
    for edge in edges:
        first, second = position(vertices, edge.domain()), position(vertices, edge.codomain())
        functor = diagram.on_morphism(edge)
        for label in factors[first].labels():
            image = functor.on_object(factors[first](label))
            classes.union(object_indices[(first, label)], object_indices[(second, factors[second].label(image))])

    def vertex_class(index: int, value: CategoryOfCategories.ElementType) -> int:
        return int(classes.find(object_indices[(index, factors[index].label(value))]))

    generator_names = {
        (index, name): f"g{position}"
        for position, (index, name) in enumerate(
            (index, name) for index, factor in enumerate(factors) for name in factor.generator_names()
        )
    }
    generator_origins = {name: datum for datum, name in generator_names.items()}
    generators = tuple(
        (name, vertex_class(index, factors[index].generator(original).domain()), vertex_class(index, factors[index].generator(original).codomain()))
        for (index, original), name in generator_names.items()
    )

    def word(index: int, names: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(generator_names[(index, name)] for name in names)

    relations = [
        (word(index, left), word(index, right))
        for index, factor in enumerate(factors) for left, right in factor.relations()
    ]
    for edge in edges:
        first, second = position(vertices, edge.domain()), position(vertices, edge.codomain())
        functor = diagram.on_morphism(edge)
        for name in factors[first].generator_names():
            image = functor.on_morphism(factors[first].generator(name))
            relations.append(((generator_names[(first, name)],), word(second, image.word())))
    labels = tuple(sorted({int(classes.find(index)) for index in range(len(objects))}))
    colimit = FinitePresentedCategory("Colimit", labels, generators, tuple((left, right) for left, right in relations if left != right))
    injections = tuple(
        Fun(factor, colimit)(
            lambda value, index=index: colimit(vertex_class(index, value)),
            lambda morphism, index=index: colimit.construct_morphism(
                colimit(vertex_class(index, morphism.domain())), colimit(vertex_class(index, morphism.codomain())), word(index, morphism.word()),
            ),
        )
        for index, factor in enumerate(factors)
    )

    def mediator(candidate: NaturalTransformation) -> MorphismCategory.ObjectType:
        target = cone_apex(candidate)
        legs = tuple(opposite_morphism(candidate.component(vertex)) for vertex in vertices)

        def on_object(value: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
            index, label = objects[colimit.label(value)]
            return legs[index].on_object(factors[index](label))

        def on_morphism(morphism: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
            source = on_object(morphism.domain())
            result = Mor(target)(source, source).one()
            for name in morphism.word():
                index, original = generator_origins[name]
                result = legs[index].on_morphism(factors[index].generator(original)) * result
            return result

        return opposite_morphism(Fun(colimit, target)(on_object, on_morphism))

    family = Cat().op().Limits(dual_diagram.domain())
    return family.with_universal_data(
        dual_diagram, colimit,
        cone(dual_diagram, colimit, lambda vertex: opposite_morphism(injections[position(vertices, vertex)])),
        mediator,
    )
