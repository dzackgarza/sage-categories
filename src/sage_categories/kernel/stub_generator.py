"""Generate static stubs from the compiler's declared category graph.

The generator starts with ``mypy.stubgen``'s source projection, then rewrites only
category-owned provider bases from the compiler's retained declaration relation.  It
never reads a tracked ``.pyi`` file as input (`POL-TYPE-025`, `POL-TYPE-026`).
"""

from __future__ import annotations

import ast
from collections.abc import Iterator
from pathlib import Path

from sage_categories.kernel.compiler import compiler

__all__ = ["generate_stubs"]


def generate_stubs(package: str, output_directory: Path) -> tuple[Path, ...]:
    """Write the compiler-derived stub projection for ``package`` to ``output_directory``."""
    from mypy.stubgen import main as stubgen_main

    stubgen_main(["--package", package, "--output", str(output_directory)])
    inheritance = compiler().declared_inheritance()
    written: list[Path] = []
    for stub_path in output_directory.rglob("*.pyi"):
        module = _module_name(package, output_directory, stub_path)
        if module is None:
            continue
        providers = _providers_in_module(inheritance, module)
        if not providers:
            continue
        tree = ast.parse(stub_path.read_text(encoding="utf-8"), filename=str(stub_path))
        _project_provider_bases(tree, providers)
        stub_path.write_text(ast.unparse(ast.fix_missing_locations(tree)) + "\n", encoding="utf-8")
        written.append(stub_path)
    return tuple(written)


def _module_name(package: str, output_directory: Path, stub_path: Path) -> str | None:
    relative = stub_path.relative_to(output_directory).with_suffix("")
    parts = relative.parts
    if not parts or parts[0] != package:
        return None
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def _providers_in_module(
    inheritance: dict[str, dict[str, tuple[str, ...]]],
    module: str,
) -> dict[str, tuple[str, ...]]:
    providers: dict[str, tuple[str, ...]] = {}
    prefix = f"{module}."
    for relations in inheritance.values():
        for provider, bases in relations.items():
            if provider.startswith(prefix):
                providers[provider] = bases
    return providers


def _project_provider_bases(
    tree: ast.Module,
    providers: dict[str, tuple[str, ...]],
) -> None:
    requires_package_import = False
    for statement in _classes(tree.body, module):
        bases = providers.get(statement.name)
        if bases is None:
            continue
        statement.node.bases = [_base_expression(base) for base in bases]
        requires_package_import = requires_package_import or bool(bases)
    if requires_package_import:
        tree.body[0:0] = [ast.Import(names=[ast.alias(name="sage_categories")])]


class _QualifiedClass:
    """One class declaration and its source-qualified name."""

    def __init__(self, node: ast.ClassDef, name: str) -> None:
        self.node = node
        self.name = name


def _classes(statements: list[ast.stmt], prefix: str) -> Iterator[_QualifiedClass]:
    for statement in statements:
        if not isinstance(statement, ast.ClassDef):
            continue
        name = f"{prefix}.{statement.name}"
        yield _QualifiedClass(statement, name)
        yield from _classes(statement.body, name)


def _base_expression(base: str) -> ast.expr:
    return ast.parse(base, mode="eval").body
