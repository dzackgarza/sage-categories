"""Products transported through structural functors."""

from __future__ import annotations

from collections.abc import Callable

from sage_categories.abstract_categories.arrow_categories import declare_isomorphism
from sage_categories.abstract_categories.functor_core import Functor, StructuralFunctor
from sage_categories.abstract_categories.hom_categories import is_isomorphism
from sage_categories.abstract_categories.product_images import (
    ProductObject,
    is_products_of_category,
)
from sage_categories.abstract_categories.product_presentations import (
    ProductLift,
    ProductPresentation,
    is_product_presentations,
)
from sage_categories.values import Arrow, MathematicalObject


def lift_product(
    structural_functor: StructuralFunctor,
    diagram: Functor,
    apex: MathematicalObject,
    inherited_product: ProductPresentation | ProductObject,
    lift_morphism: Callable[[MathematicalObject, MathematicalObject, Arrow], Arrow],
) -> ProductPresentation:
    """Lift the product inherited through one structural functor."""
    assert diagram.codomain() is structural_functor.domain()
    image_apex = structural_functor.on_object(apex)
    inherited_category = inherited_product.category()
    if is_product_presentations(inherited_category):
        inherited_apex = inherited_product.apex()
    else:
        inherited_apex = inherited_product
    assert image_apex is inherited_apex
    identity = structural_functor.codomain().identity(image_apex)
    comparison = declare_isomorphism(identity, identity)
    assert is_isomorphism(comparison)
    return ProductLift(
        diagram=diagram,
        structural_functor=structural_functor,
        inherited_product=inherited_product,
        apex=apex,
        comparison=comparison,
        lift_morphism=lift_morphism,
    ).presentation()


def inherited_product(
    structural_functor: StructuralFunctor,
    diagram: Functor,
) -> ProductObject:
    """Return the product after structural transport of its diagram."""
    assert diagram.codomain() is structural_functor.domain()
    inherited_diagram = structural_functor.postcomposition(diagram.domain())(diagram)
    product = structural_functor.codomain().ProductFunctor(diagram.domain())(
        inherited_diagram,
    )
    products = structural_functor.codomain().Products(diagram.domain())
    assert is_products_of_category(products)
    assert products.contains_product(product)
    return product
