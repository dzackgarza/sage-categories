"""Products transported through structural functors."""

from __future__ import annotations

from sage_categories.abstract_categories.functor_core import Functor, StructuralFunctor
from sage_categories.abstract_categories.product_images import (
    ProductObject,
    is_products_of_category,
)
from sage_categories.values import MathematicalObject


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
