"""Install category structure on the identity retained by object construction."""

from __future__ import annotations

from sage_categories.kernel.compiler import realize_implementation_class
from sage_categories.kernel.construction import (
    active_object_context,
    install_object_realization,
    retained_object_input,
)
from sage_categories.kernel.refinement import place
from sage_categories.kernel.roles import ObjectOfCategory


def realize_object(value: ObjectOfCategory, category_type: type[ObjectOfCategory]) -> None:
    """Realize the current object over its retained selected image."""
    from sage_categories.cat.category import CategoryDeclaration
    from sage_categories.cat.functors import Cat

    identity = retained_object_input(value).identity
    if identity.universe is not None:
        return
    context = active_object_context()
    assert context is not None and context.canonical_image is value
    assert context.initializing_image is not None
    placement = value.category()
    realize_implementation_class(value, category_type)
    value._index_set = context.initializing_image
    CategoryDeclaration._initialize(value, Cat())
    place(value, placement)


def install() -> None:
    """Supply the compiler with the joint category realization operation."""
    install_object_realization(realize_object)
