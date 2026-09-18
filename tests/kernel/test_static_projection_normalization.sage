"""Static compiler projection keeps categorical level identities normalized."""

from sage_categories.algebra.abelian import _AbelianOperations
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.structured_objects import RingCategory, Rings
from sage_categories.kernel.compiler import compiler
from sage_categories.sets.finite import Sets


def test_morphism_category_object_projects_as_base_morphism_role() -> None:
    provider = (
        f"{MorphismCategory.ObjectType.__module__}."
        f"{MorphismCategory.ObjectType.__qualname__}"
    )
    projection = compiler().declared_inheritance()
    assert provider not in projection.get("object", {})
    assert projection["arrow"][provider] == (
        "sage_categories.cat.category.CategoryOfCategories.ElementType",
        "sage_categories.kernel.roles.MorphismOfCategory",
    )


def test_exact_augmentation_does_not_leak_into_generic_provider_projection() -> None:
    Rings(Sets())
    projection = compiler().declared_inheritance()
    for surface, role in (
        ("object", "ObjectType"),
        ("element", "ElementType"),
        ("arrow", "MorphismType"),
    ):
        provider = f"{RingCategory.__module__}.{RingCategory.__qualname__}.{role}"
        exact = f"{_AbelianOperations.__module__}.{_AbelianOperations.__qualname__}.{role}"
        assert exact not in projection[surface][provider]
