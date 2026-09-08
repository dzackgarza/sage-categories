module SageCategoriesBridge

using Catlab
using Catlab.BasicSets: SetOb
using Catlab.CategoricalAlgebra
using Catlab.CategoricalAlgebra.Cats
using GATlab

export callable_category, callable_functor, callable_transformation,
       compose_functors, identity_functor, functor_object_image, functor_morphism_image,
       transformation_component, identity_transformation, compose_transformations,
       whisker_left, whisker_right, horizontal_composite

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

end
