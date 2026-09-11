"""Bridge Cat's parameter-dependent static declarations into the compiler oracle.

The kernel owns the read-only compiler projection but cannot import Cat.  This layer
installs a lazy reader, just as it installs the functor-declaration readers: the reader
imports Cat only when the external static plugin asks after package bootstrap.
"""

from __future__ import annotations

from typing import get_args, get_type_hints

from sage_categories.kernel.compiler import install_method_result_projection_reader


def _fullname(value: type | object) -> str:
    return f"{value.__module__}.{value.__qualname__}"


def method_result_projections() -> dict[str, tuple[str, tuple[tuple[int, int], ...]]]:
    """Project the fixed-endpoint functor category's retained endpoint identities."""
    from sage_categories.cat.functors import FunctorCategory, FunctorsCategory

    result_annotation = get_type_hints(FunctorsCategory.fixed_endpoint_type)["return"]
    result_arguments = get_args(result_annotation)
    assert result_arguments == (FunctorCategory,), "FunctorsCategory.fixed_endpoint_type must name FunctorCategory exactly"
    method = FunctorsCategory.__call__
    return {
        f"{_fullname(FunctorsCategory)}.{method.__name__}": (
            _fullname(FunctorCategory),
            ((0, 0), (1, 1)),
        )
    }


def install() -> None:
    """Install the lazy Cat-owned result reader on the kernel compiler projection."""
    install_method_result_projection_reader(method_result_projections)
