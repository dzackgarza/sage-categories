"""Read a functor's declared properties to decide placement and inheritance (D175).

``Fun`` reads both off the functor's own placement, and the kernel's placement graph and
refinement walk ask for the answer while ``Fun`` is still building its own property
categories.  So each reader reaches ``Fun`` when it is called rather than when this
module is imported, and this layer installs itself before ``Cat`` is loaded.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from sage_categories.kernel.compiler import install_structural_comparison_readers
from sage_categories.kernel.construction import retained_values
from sage_categories.kernel.refinement import install_functor_declaration_readers
from sage_categories.kernel.roles import CategoryPoint, MorphismOfCategory

if TYPE_CHECKING:
    from sage_categories.cat.functors import Functor, NaturalTransformation

__all__ = ["declares_point", "install", "retained_invertible_comparisons", "traces_inheritance", "traces_placement"]


def _functors():
    """Load the functor category after the kernel declaration readers are importable."""
    from sage_categories.cat.functors import Fun

    return Fun


def traces_placement(functor: Functor) -> bool:
    """Whether placement follows ``functor``: it is declared a monomorphism of ``Cat()`` and an isofibration (POL-FUN-036).

    Read both conditions from the functor's property-category placement.
    Monicity and repleteness together present the exact subcategory relation.
    """
    return _functors().declares_subcategory(functor)


def traces_inheritance(functor: Functor) -> bool:
    """Whether inheritance follows ``functor``: it is declared an isofibration (D164 to D167).

    A selected structure functor without that declaration gives access to the structure
    it selects and supplies no implementation (``specs/functor.md``, "Structure functors
    and inherited classes").  Placement asks for a monomorphism as well
    (``traces_placement``, D169).
    """
    return _functors().declares_inheritance(functor)


def declares_point(functor: Functor) -> bool:
    """Whether ``functor`` is declared a point ``* -> C``: monic, with the terminal category as domain (D154, D162).

    ``C.Point()`` writes that declaration in the call that constructs the arrow, so what
    is read here is a declaration like any other (``POL-CAT-069``, D175).  The arrow
    carries neither placement nor inheritance: those run along the inclusion ``<X> -> C``
    of the replete full subcategory its image generates (D161, D169).  The compiler asks
    because a point arrow is the one selected functor whose domain is not the category
    that selected it.
    """
    return _functors().declares_point(functor)


def retained_invertible_comparisons(
    first: Functor,
    second: Functor,
) -> tuple[MorphismOfCategory, ...]:
    """Retained invertible 2-cells from first to second in the ordinary owned Mor tower."""
    return tuple(
        value
        for value in retained_values()
        if isinstance(value, MorphismOfCategory) and value.domain() is first and value.codomain() is second and value.base_category().retained_inverse(value) is not None
    )


def _comparison_is_executable(comparison: MorphismOfCategory) -> bool:
    """Whether a retained comparison has an executable natural-transformation component rule."""
    return cast("NaturalTransformation", comparison)._has_component_rule()


def _comparison_component(
    comparison: MorphismOfCategory,
    value: CategoryPoint,
) -> MorphismOfCategory:
    """The executable component transporting one structural object image to the other."""
    return cast("NaturalTransformation", comparison).component(value)


def install() -> None:
    """Hand the kernel the Cat-owned readers used by refinement and structural coherence."""
    install_functor_declaration_readers(traces_placement, traces_inheritance, declares_point)
    install_structural_comparison_readers(
        retained_invertible_comparisons,
        _comparison_is_executable,
        _comparison_component,
    )
