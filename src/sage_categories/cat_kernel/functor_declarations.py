"""Read a functor's declared properties to decide placement and inheritance (D175).

``Fun`` reads both off the functor's own placement, and the kernel's placement graph and
refinement walk ask for the answer while ``Fun`` is still building its own property
categories.  So each reader reaches ``Fun`` when it is called rather than when this
module is imported, and this layer installs itself before ``Cat`` is loaded.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sage_categories.kernel.refinement import install_functor_declaration_readers

if TYPE_CHECKING:
    from sage_categories.cat.functors import Functor

__all__ = ["install", "traces_inheritance", "traces_placement"]


def traces_placement(functor: Functor) -> bool:
    """Whether placement follows ``functor``: it is declared a monomorphism of ``Cat()`` and an isofibration (POL-FUN-036).

    Read both conditions from the functor's property-category placement.
    Monicity and repleteness together present the exact subcategory relation.
    """
    from sage_categories.cat.functors import Fun

    return Fun.declares_subcategory(functor)


def traces_inheritance(functor: Functor) -> bool:
    """Whether inheritance follows ``functor``: it is declared an isofibration (D164 to D167).

    A selected structure functor without that declaration gives access to the structure
    it selects and supplies no implementation (``specs/functor.md``, "Structure functors
    and inherited classes").  Placement asks for a monomorphism as well
    (``traces_placement``, D169).
    """
    from sage_categories.cat.functors import Fun

    return Fun.declares_inheritance(functor)


def install() -> None:
    """Hand the kernel the two readers its placement graph and refinement walk ask with."""
    install_functor_declaration_readers(traces_placement, traces_inheritance)
