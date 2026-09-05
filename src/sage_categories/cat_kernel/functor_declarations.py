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

__all__ = ["declares_point", "install", "traces_inheritance", "traces_placement"]


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


def declares_point(functor: Functor) -> bool:
    """Whether ``functor`` is declared a point ``* -> C``: monic, with the terminal category as domain (D154, D162).

    ``C.Point()`` writes that declaration in the call that constructs the arrow, so what
    is read here is a declaration like any other (``POL-CAT-069``, D175).  The arrow
    carries neither placement nor inheritance: those run along the inclusion ``<X> -> C``
    of the replete full subcategory its image generates (D161, D169).  The compiler asks
    because a point arrow is the one selected functor whose domain is not the category
    that selected it.
    """
    from sage_categories.cat.functors import Fun

    return Fun.declares_point(functor)


def install() -> None:
    """Hand the kernel the three readers its placement graph, refinement walk, and compiler ask with."""
    install_functor_declaration_readers(traces_placement, traces_inheritance, declares_point)
