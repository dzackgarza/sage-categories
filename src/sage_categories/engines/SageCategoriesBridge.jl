module SageCategoriesBridge

using Catlab
using Catlab.BasicSets: SetOb
using Catlab.CategoricalAlgebra
using Catlab.CategoricalAlgebra.Cats
using GATlab

export callable_category, callable_functor, callable_transformation,
       compose_functors, identity_functor, functor_object_image, functor_morphism_image,
       transformation_component, identity_transformation, compose_transformations,
       whisker_left, whisker_right, horizontal_composite, presented_coproduct,
       presented_coproduct_data, presented_coproduct_object_image,
       presented_coproduct_path_image, presented_functor, presented_functor_morphism_image

"""A Catlab category whose primitive operations are supplied by the owned runtime.

The callbacks are primitive semantic operations.  Catlab owns all higher execution
constructed from this category: functor composition, transformation composition, and
whiskering.
"""
struct CallableCategory
    domain::Any
    codomain::Any
    identity::Any
    composition::Any
end

@instance ThCategoryExplicitSets{Any,Any} [model::CallableCategory] begin
    dom(f::Any) = model.domain(f)
    codom(f::Any) = model.codomain(f)
    id(x::Any) = model.identity(x)
    compose(f::Any, g::Any) = model.composition(f, g)
    ob_set() = SetOb(Any)
    hom_set() = SetOb(Any)
end

callable_category(domain, codomain, identity, composition) =
    Category(CallableCategory(domain, codomain, identity, composition))

callable_functor(on_object, on_morphism, source::Cat, target::Cat) =
    Functor(value -> on_object(value), arrow -> on_morphism(arrow), source, target)

functor_object_image(functor::AbsFunctor, value) = ob_map(functor, value)
functor_morphism_image(functor::AbsFunctor, value) = hom_map(functor, value)
compose_functors(first::AbsFunctor, second::AbsFunctor) = compose[Cat2()](first, second)
identity_functor(category::Cat) = id[Cat2()](category)

"""A natural transformation represented by one callable component operation.

Unlike Catlab's finite component map, this model never enumerates the source objects.
It is the callable `ThTransformation` extension required by the owned runtime.
"""
struct CallableTransformation{DF<:AbsFunctor,CF<:AbsFunctor}
    component::Any
    source::DF
    target::CF
end

@instance ThTransformation{Any,Any,DF,CF} [model::CallableTransformation{DF,CF}] where {DF,CF} begin
    dom()::DF = model.source
    codom()::CF = model.target
    component(x::Any)::Any = model.component(x)
end

callable_transformation(component, source::AbsFunctor, target::AbsFunctor) =
    Transformation(CallableTransformation(component, source, target))

transformation_component(transformation::Transformation, value) = component(transformation, value)
identity_transformation(functor::AbsFunctor) = callable_transformation(
    value -> id(codom(functor), ob_map(functor, value)), functor, functor,
)

function compose_transformations(first::Transformation, second::Transformation)
    codom(first) == dom(second) || error("natural transformations are not vertically composable")
    source = dom(first)
    target = codom(second)
    category = codom(source)
    callable_transformation(
        value -> compose(category, component(first, value), component(second, value)),
        source,
        target,
    )
end

function whisker_left(functor::AbsFunctor, transformation::Transformation)
    source, target = dom(transformation), codom(transformation)
    codom(source) == dom(functor) || error("functor cannot left-whisker this transformation")
    callable_transformation(
        value -> hom_map(functor, component(transformation, value)),
        compose_functors(source, functor),
        compose_functors(target, functor),
    )
end

function whisker_right(transformation::Transformation, functor::AbsFunctor)
    source, target = dom(transformation), codom(transformation)
    codom(functor) == dom(source) || error("functor cannot right-whisker this transformation")
    callable_transformation(
        value -> component(transformation, ob_map(functor, value)),
        compose_functors(functor, source),
        compose_functors(functor, target),
    )
end

function horizontal_composite(first::Transformation, second::Transformation)
    outer = whisker_right(second, dom(first))
    inner = whisker_left(codom(second), first)
    compose_transformations(outer, inner)
end



"""Build a Catlab FinCat presentation from index-based owned presentation data."""
function _presented_fincat(object_names, generator_data, relation_data)
    p = Presentation(FreeSchema)
    objects = [add_generator!(p, Ob(FreeSchema.Ob, Symbol(name))) for name in object_names]
    generators = map(generator_data) do datum
        name, source, target = datum
        add_generator!(p, Hom(Symbol(name), objects[source], objects[target]))
    end
    function path(indices, source)
        isempty(indices) && return id(objects[source])
        length(indices) == 1 && return generators[only(indices)]
        compose(generators[indices]...)
    end
    for relation in relation_data
        source, left, right = relation
        add_equation!(p, path(left, source), path(right, source))
    end
    FinCat(p)
end

function _fincat_path(category, indices, source)
    generators = collect(hom_generators(category))
    objects = collect(ob_generators(category))
    isempty(indices) && return id(category, objects[source])
    length(indices) == 1 && return generators[only(indices)]
    compose(category, generators[indices]...)
end

function _path_names(category, morphism)
    [String(Symbol(edge)) for edge in edges(decompose(getvalue(category), morphism))]
end

struct PresentedCoproduct
    categories::Any
    cocone::Any
    target::Any
end

"""Catlab-owned coproduct presentation retained as one opaque native value."""
function presented_coproduct(presentations)
    categories = [
        _presented_fincat(data[1], data[2], data[3])
        for data in presentations
    ]
    cocone = Catlab.CategoricalAlgebra.Pointwise.Chase.coproduct_fincat(categories)
    PresentedCoproduct(categories, cocone, apex(cocone))
end

function presented_coproduct_data(value::PresentedCoproduct)
    target = value.target
    object_names = [String(Symbol(object)) for object in ob_generators(target)]
    homs = [
        (String(Symbol(hom)), String(Symbol(dom(target, hom))), String(Symbol(codom(target, hom))))
        for hom in hom_generators(target)
    ]
    relations = [
        (_path_names(target, left), _path_names(target, right))
        for (left, right) in equations(target)
    ]
    (object_names, homs, relations)
end

function presented_coproduct_object_image(value::PresentedCoproduct, factor, object)
    leg = legs(value.cocone)[factor]
    String(Symbol(ob_map(leg, collect(ob_generators(value.categories[factor]))[object])))
end

function presented_coproduct_path_image(value::PresentedCoproduct, factor, indices, source)
    category = value.categories[factor]
    leg = legs(value.cocone)[factor]
    _path_names(value.target, hom_map(leg, _fincat_path(category, indices, source)))
end

"""Native functor from a finite presentation into an arbitrary Catlab category."""
function presented_functor(presentation, object_images, generator_images, target::Cat)
    source = _presented_fincat(presentation[1], presentation[2], presentation[3])
    objects = collect(object_images)
    generators = collect(generator_images)
    object_map = Dict(zip(collect(ob_generators(source)), objects))
    generator_map = Dict(zip(collect(hom_generators(source)), generators))
    FinDomFunctor(object_map, generator_map, source, target; homtype=:hom)
end

function presented_functor_morphism_image(functor, indices, source)
    hom_map(functor, _fincat_path(dom(functor), indices, source))
end

end
