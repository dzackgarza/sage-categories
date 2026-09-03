"""Generate an axiom's application and build its property subcategory's inclusion (D175).

An axiom's declaration is ``Cat``'s and the compiler's installer is the kernel's, so
neither layer alone can generate ``is_p()``; the inclusion ``C.P() -> C`` needs the
declaration and the placement graph the same way.  Both live here, and this module hands
them to ``Cat`` (``specs/resolution.md``, "The closed kernel surface"; D148, D150).

Each reader reaches ``Cat`` when it is called rather than when this module is imported,
because ``Cat()``'s own class declares axioms in its body and so asks for the generator
while ``Cat`` is still loading.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sage_categories.kernel.compiler import install_on_declaration
from sage_categories.kernel.predicates import AxiomLayer, install_axiom_layer
from sage_categories.kernel.roles import CategoryPoint, category_of, role_of

if TYPE_CHECKING:
    from sage_categories.cat.category import Category, CategoryOfCategories
    from sage_categories.cat.morphisms import MorphismCategory
    from sage_categories.cat.predicates import Axiom, Proposition
    from sage_categories.cat.properties import PropertySubcategory

__all__ = ["generate_application", "install", "install_base_applications", "subcategory_inclusions"]

# The axioms declared on the base category class, held until the declaration that owns
# their applications exists (``install_base_applications``).
_base_axioms: list[Axiom] = []

# The axiom each generated application came from, by the declaration it landed on.
_derived_applications: dict[tuple[type[CategoryPoint], str], Axiom] = {}


def generate_application(axiom: Axiom) -> None:
    """Generate ``is_p()`` from ``axiom`` onto the declaration that owns it."""
    owner = axiom.application_owner()
    if owner is None:
        _base_axioms.append(axiom)
        return
    _install_application(axiom, owner)


def install_base_applications(owner: type[CategoryPoint]) -> None:
    """Install the applications of the base category class's axioms onto the objects of every category."""
    for axiom in _base_axioms:
        _install_application(axiom, owner)
    _base_axioms.clear()


def _install_application(axiom: Axiom, owner: type[CategoryPoint]) -> None:
    name = axiom.application_name()

    def application(value: CategoryPoint, *parameters: Category) -> Proposition:
        placement = category_of(value, role_of(value)).narrowing_base()
        return axiom._declared_on(placement, *parameters).membership_proposition(value)

    application.__name__ = name
    application.__qualname__ = f"{owner.__name__}.{name}"
    known = _derived_applications.get((owner, name))
    assert known is None or known is axiom
    assert known is not None or name not in vars(owner)
    _derived_applications[(owner, name)] = axiom
    install_on_declaration(owner, name, application)


def subcategory_inclusions(subcategory: PropertySubcategory) -> tuple[MorphismCategory.ObjectType, ...]:
    """The inclusion ``C.P() -> C``, then one per further recorded containment (POL-FUN-024, D83)."""
    from sage_categories.cat.functors import Fun

    return (
        Fun.full_subcategory_monomorphism(subcategory, subcategory._ambient),
        *(Fun.full_subcategory_monomorphism(subcategory, containing) for containing in subcategory._full_subcategory_of),
    )


def install() -> None:
    """Hand down the layer an axiom and a property subcategory are built with."""
    install_axiom_layer(
        AxiomLayer(
            generate_application=generate_application,
            install_base_applications=install_base_applications,
            subcategory_inclusions=subcategory_inclusions,
        )
    )
