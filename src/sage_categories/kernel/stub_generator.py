"""Generate static stubs from the compiler's declared category graph.

The generator starts with ``mypy.stubgen``'s source projection, then rewrites only
category-owned provider bases from the compiler's retained declaration relation.  It
never reads a tracked ``.pyi`` file as input (`POL-TYPE-025`, `POL-TYPE-026`).
"""

from __future__ import annotations

import ast
from importlib import import_module
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path

from sage_categories.kernel.compiler import compiler

__all__ = ["generate_stubs"]


def generate_stubs(package: str, output_directory: Path) -> tuple[Path, ...]:
    """Write the compiler-derived stub projection for ``package`` to its package directory."""
    subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys; from pathlib import Path; "
            "from sage_categories.kernel.stub_generator import _generate_stubs; "
            "_generate_stubs(sys.argv[1], Path(sys.argv[2]))",
            package,
            str(output_directory.resolve()),
        ],
        check=True,
    )
    return tuple(sorted(output_directory.rglob("*.pyi")))


def _generate_stubs(package: str, output_directory: Path) -> tuple[Path, ...]:
    """Project declarations from a fresh package bootstrap in the current Sage interpreter."""
    from mypy.stubgen import main as stubgen_main

    sources = tuple(sorted(output_directory.rglob("*.py")))
    for source in sources:
        import_module(_module_name(package, output_directory, source))
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
        source_path = stub_path.with_suffix(".py")
        source = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
        tree = ast.parse(stub_path.read_text(encoding="utf-8"), filename=str(stub_path))
        _canonicalize_imports(tree, package, canonical_exports)
        _project_paramspec_class_aliases(tree, source)
        if providers:
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
    package: str,
    canonical_exports: dict[str, str],
) -> None:
    """Replace an imported runtime alias with its uniquely declared public owner.

    A name is canonicalized only where it is this package's to own.  An import from
    outside the package keeps its module, whatever the name: ``sage_runtime`` imports
    Sage's own ``Category`` under an alias, and redirecting that to the module where this
    package declares a ``Category`` states that the private Sage runtime mirror stands on
    the owned declaration, which is D173's direction reversed.
    """
    statements: list[ast.stmt] = []
    for statement in tree.body:
        if not isinstance(statement, ast.ImportFrom) or statement.module is None:
            statements.append(statement)
            continue
        if statement.module != package and not statement.module.startswith(f"{package}."):
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


def _project_paramspec_class_aliases(tree: ast.Module, source: ast.Module) -> None:
    """Bind the source class's parameter lists explicitly in its class aliases.

    Generic legacy aliases bind free variables on their right-hand side and remain
    usable as classes: https://mypy.readthedocs.io/en/stable/generics.html#generic-type-aliases
    """
    declarations = {
        declaration.name: tuple(
            parameter for parameter in declaration.type_params if isinstance(parameter, ast.ParamSpec)
        )
        for declaration in source.body
        if isinstance(declaration, ast.ClassDef)
        and declaration.type_params
        and all(isinstance(parameter, ast.ParamSpec) for parameter in declaration.type_params)
    }
    used: set[str] = set()
    for statement in ast.walk(tree):
        if not isinstance(statement, ast.Assign) or not isinstance(statement.value, ast.Name):
            continue
        name = statement.value.id
        parameters = declarations.get(name)
        if parameters is None:
            continue
        used.add(name)
        statement.value = ast.Subscript(
            value=statement.value,
            slice=ast.Tuple(
                elts=[ast.Name(id=f"_{name}_{parameter.name}", ctx=ast.Load()) for parameter in parameters],
                ctx=ast.Load(),
            ),
            ctx=ast.Load(),
        )
    if not used:
        return
    statements: list[ast.stmt] = [ast.Import(names=[ast.alias(name="typing", asname="_typing")])]
    for statement in tree.body:
        statements.append(statement)
        if not isinstance(statement, ast.ClassDef) or statement.name not in used:
            continue
        for parameter in declarations[statement.name]:
            name = f"_{statement.name}_{parameter.name}"
            keywords = (
                [ast.keyword(arg="default", value=parameter.default_value)]
                if parameter.default_value is not None
                else []
            )
            statements.append(
                ast.Assign(
                    targets=[ast.Name(id=name, ctx=ast.Store())],
                    value=ast.Call(
                        func=ast.Attribute(value=ast.Name(id="_typing", ctx=ast.Load()), attr="ParamSpec", ctx=ast.Load()),
                        args=[ast.Constant(value=name)],
                        keywords=keywords,
                    ),
                )
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
