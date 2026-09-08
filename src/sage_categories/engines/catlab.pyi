from sage_categories.cat.category import Category
from sage_categories.cat.morphisms import MorphismCategory

def ensure_native_category(owner: Category) -> object: ...
def ensure_native_functor(functor: MorphismCategory.ObjectType) -> object: ...
def functor_object_image(
    functor: MorphismCategory.ObjectType, value: object
) -> object: ...
def functor_morphism_image(
    functor: MorphismCategory.ObjectType, value: object
) -> object: ...
def compose_functors(
    first: MorphismCategory.ObjectType, second: MorphismCategory.ObjectType
) -> object: ...
def callable_transformation(
    value: MorphismCategory.ObjectType,
    source: MorphismCategory.ObjectType,
    target: MorphismCategory.ObjectType,
    component: object,
) -> None: ...
def transformation_component(
    value: MorphismCategory.ObjectType, member_object: object
) -> object: ...
def identity_transformation(
    value: MorphismCategory.ObjectType, functor: MorphismCategory.ObjectType
) -> None: ...
def compose_transformations(
    value: MorphismCategory.ObjectType,
    first: MorphismCategory.ObjectType,
    second: MorphismCategory.ObjectType,
    source: MorphismCategory.ObjectType,
    target: MorphismCategory.ObjectType,
) -> None: ...
def whisker_left(
    value: MorphismCategory.ObjectType,
    functor: MorphismCategory.ObjectType,
    transformation: MorphismCategory.ObjectType,
    source: MorphismCategory.ObjectType,
    target: MorphismCategory.ObjectType,
) -> None: ...
def whisker_right(
    value: MorphismCategory.ObjectType,
    transformation: MorphismCategory.ObjectType,
    functor: MorphismCategory.ObjectType,
    source: MorphismCategory.ObjectType,
    target: MorphismCategory.ObjectType,
) -> None: ...
def horizontal_composite(
    value: MorphismCategory.ObjectType,
    first: MorphismCategory.ObjectType,
    second: MorphismCategory.ObjectType,
    source: MorphismCategory.ObjectType,
    target: MorphismCategory.ObjectType,
) -> None: ...
def retain_composite_functor(
    value: MorphismCategory.ObjectType,
    first: MorphismCategory.ObjectType,
    second: MorphismCategory.ObjectType,
) -> None: ...
def identity_functor(value: MorphismCategory.ObjectType, owner: Category) -> None: ...
def ensure_native_transformation(value: MorphismCategory.ObjectType) -> object: ...
def presented_coproduct(categories: tuple[object, ...]) -> object: ...
def presented_coproduct_data(
    value: object,
) -> tuple[
    tuple[str, ...],
    tuple[tuple[str, str, str], ...],
    tuple[tuple[tuple[str, ...], tuple[str, ...]], ...],
]: ...
def presented_coproduct_object_image(
    value: object, factor: int, object_index: int
) -> str: ...
def presented_coproduct_path_image(
    value: object,
    categories: tuple[object, ...],
    factor: int,
    word: tuple[str, ...],
    source: object,
) -> tuple[str, ...]: ...
def presented_functor(
    source: object,
    target: Category,
    object_images: tuple[object, ...],
    generator_images: tuple[object, ...],
) -> object: ...
def presented_functor_morphism_image(
    functor: object, source: object, morphism: object
) -> object: ...
