"""Static compiler projection keeps categorical level identities normalized."""

from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.kernel.compiler import compiler


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
