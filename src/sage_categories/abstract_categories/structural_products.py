"""Products transported through structural functors."""

from __future__ import annotations

from sage_categories.abstract_categories.diagram_shapes import ConeObject
from sage_categories.abstract_categories.functor_core import Functor, StructuralFunctor
from sage_categories.abstract_categories.product_presentations import (
    Cone,
    Product,
    ProductPresentation,
    is_product_presentations,
)
from sage_categories.abstract_categories.product_images import (
    ProductObject,
    is_products_of_category,
)
from sage_categories.values import Arrow, MathematicalObject


def lift_product(
    structural_functor: StructuralFunctor,
    diagram: Functor,
    apex: MathematicalObject,
    inherited_product: ProductPresentation | ProductObject,
) -> ProductPresentation:
    """Transport an inherited product presentation through canonical images."""
    assert diagram.codomain() is structural_functor.domain()
    assert apex in diagram.codomain()
    inherited_category = inherited_product.category()
    if is_product_presentations(inherited_category):
        inherited_apex = inherited_product.apex()
    else:
        assert is_products_of_category(inherited_category)
        inherited_apex = inherited_product
    assert structural_functor.on_object(apex) is inherited_apex

    def projection(index: MathematicalObject) -> Arrow:
        return structural_functor._lift_morphism(
            apex,
            diagram(index),
            inherited_product.projection(index),
        )

    cone = Cone(diagram, apex, projection)

    def mediate(other: ConeObject) -> Arrow:
        assert other.diagram() is diagram
        source = other.apex()
        inherited_cone = Cone(
            inherited_product.diagram(),
            structural_functor.on_object(source),
            lambda index: structural_functor.on_morphism(
                other.structure_morphism(index),
            ),
        )
        return structural_functor._lift_morphism(
            source,
            apex,
            inherited_product.universal_morphism(inherited_cone),
        )

    return Product(cone, mediate)


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
