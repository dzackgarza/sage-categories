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
    """Write the compiler-derived stub projection for ``package`` to its package directory."""
    from mypy.stubgen import main as stubgen_main

    sources = tuple(sorted(output_directory.rglob("*.py")))
    canonical_exports = _canonical_exports(package, output_directory, sources)
    stubgen_main(
        [
            "--no-import",
            "--output",
            str(output_directory.parent),
            *(str(source) for source in sources),
        ]
    )
    inheritance = compiler().declared_inheritance()
    for stub_path in output_directory.rglob("*.pyi"):
        module = _module_name(package, output_directory, stub_path)
        providers = _providers_in_module(inheritance, module)
        if not providers:
            tree = ast.parse(stub_path.read_text(encoding="utf-8"), filename=str(stub_path))
            _canonicalize_imports(tree, canonical_exports)
            stub_path.write_text(ast.unparse(ast.fix_missing_locations(tree)) + "\n", encoding="utf-8")
            continue
        tree = ast.parse(stub_path.read_text(encoding="utf-8"), filename=str(stub_path))
        _canonicalize_imports(tree, canonical_exports)
        _project_provider_bases(tree, module, providers)
        stub_path.write_text(ast.unparse(ast.fix_missing_locations(tree)) + "\n", encoding="utf-8")
    return tuple(sorted(output_directory.rglob("*.pyi")))


def _module_name(package: str, output_directory: Path, stub_path: Path) -> str:
    relative = stub_path.relative_to(output_directory).with_suffix("")
    parts = relative.parts
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join((package, *parts))


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


def _canonical_exports(
    package: str,
    output_directory: Path,
    sources: tuple[Path, ...],
) -> dict[str, str]:
    """Map each uniquely declared public name to its authoritative source module."""
    candidates: dict[str, list[str]] = {}
    for source in sources:
        module = _module_name(package, output_directory, source)
        tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
        declarations = _declared_names(tree)
        for name in _public_names(tree):
            if name in declarations:
                candidates.setdefault(name, []).append(module)
    return {
        name: canonical
        for name, modules in candidates.items()
        if len(modules) == 1
        for canonical in modules
    }


def _declared_names(tree: ast.Module) -> set[str]:
    names: set[str] = set()
    for statement in tree.body:
        match statement:
            case ast.ClassDef(name=name) | ast.FunctionDef(name=name) | ast.AsyncFunctionDef(name=name):
                names.add(name)
            case ast.Assign(targets=targets):
                names.update(target.id for target in targets if isinstance(target, ast.Name))
            case ast.AnnAssign(target=ast.Name(id=name)):
                names.add(name)
    return names


def _public_names(tree: ast.Module) -> tuple[str, ...]:
    for statement in tree.body:
        if not isinstance(statement, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == "__all__" for target in statement.targets):
            continue
        if isinstance(statement.value, ast.List | ast.Tuple):
            return tuple(
                element.value
                for element in statement.value.elts
                if isinstance(element, ast.Constant) and isinstance(element.value, str)
            )
    return ()


def _canonicalize_imports(
    tree: ast.Module,
    canonical_exports: dict[str, str],
) -> None:
    """Replace an imported runtime alias with its uniquely declared public owner."""
    statements: list[ast.stmt] = []
    for statement in tree.body:
        if not isinstance(statement, ast.ImportFrom) or statement.module is None:
            statements.append(statement)
            continue
        grouped: dict[str, list[ast.alias]] = {}
        for alias in statement.names:
            module = canonical_exports.get(alias.name, statement.module)
            grouped.setdefault(module, []).append(alias)
        statements.extend(
            ast.ImportFrom(module=module, names=aliases, level=statement.level)
            for module, aliases in grouped.items()
        )
    tree.body[:] = statements


def _project_provider_bases(
    tree: ast.Module,
    module: str,
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
