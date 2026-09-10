"""Generate static stubs from the compiler's declared category graph.

The generator starts with ``mypy.stubgen``'s source projection, then rewrites only
category-owned provider bases from the compiler's retained declaration relation.  It
never reads a tracked ``.pyi`` file as input (`POL-TYPE-025`, `POL-TYPE-026`).
"""

from __future__ import annotations

import ast
import subprocess
import sys
from collections.abc import Iterator
from importlib import import_module
from pathlib import Path

__all__ = ["generate_stubs"]


def generate_stubs(package: str, output_directory: Path) -> tuple[Path, ...]:
    """Write the compiler-derived stub projection for ``package`` to its package directory."""
    subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys; from pathlib import Path; from sage_categories.kernel.stub_generator import _generate_stubs; _generate_stubs(sys.argv[1], Path(sys.argv[2]))"
            ),
            package,
            str(output_directory.resolve()),
        ],
        check=True,
    )
    return tuple(sorted(output_directory.rglob("*.pyi")))


def _generate_stubs(package: str, output_directory: Path) -> tuple[Path, ...]:
    """Project declarations from a fresh package bootstrap in the current Sage interpreter."""
    from mypy.stubgen import main as stubgen_main

    from sage_categories.kernel.compiler import compiler

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
    runtime_aliases = _source_role_aliases(
        package, output_directory, sources, inheritance
    )
    source_modules = frozenset(
        _module_name(package, output_directory, source) for source in sources
    )
    for stub_path in output_directory.rglob("*.pyi"):
        module = _module_name(package, output_directory, stub_path)
        providers = _providers_in_module(inheritance, module)
        source_path = stub_path.with_suffix(".py")
        source = ast.parse(
            source_path.read_text(encoding="utf-8"), filename=str(source_path)
        )
        tree = ast.parse(stub_path.read_text(encoding="utf-8"), filename=str(stub_path))
        _canonicalize_imports(tree, package, canonical_exports)
        _project_class_aliases(tree, source)
        _project_runtime_class_aliases(
            tree, runtime_aliases.get(module, {}), source_modules
        )
        if providers:
            _project_provider_bases(tree, module, providers, source_modules)
        stub_path.write_text(
            ast.unparse(ast.fix_missing_locations(tree)) + "\n", encoding="utf-8"
        )
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
            case (
                ast.ClassDef(name=name)
                | ast.FunctionDef(name=name)
                | ast.AsyncFunctionDef(name=name)
            ):
                names.add(name)
            case ast.Assign(targets=targets):
                names.update(
                    target.id for target in targets if isinstance(target, ast.Name)
                )
            case ast.AnnAssign(target=ast.Name(id=name)):
                names.add(name)
    return names


def _public_names(tree: ast.Module) -> tuple[str, ...]:
    for statement in tree.body:
        if not isinstance(statement, ast.Assign):
            continue
        if not any(
            isinstance(target, ast.Name) and target.id == "__all__"
            for target in statement.targets
        ):
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
        if statement.module != package and not statement.module.startswith(
            f"{package}."
        ):
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


def _project_class_aliases(
    tree: ast.Module,
    source: ast.Module,
) -> None:
    """Project runtime class aliases as explicit PEP 695 type aliases.

    ``stubgen`` writes ``Category = CategoryDeclaration`` as an assignment alias.
    For a generic class whose parameters are ``ParamSpec`` values, mypy cannot
    parameterize that inferred alias.  The source assignment is nevertheless an
    exact class alias, so its static form binds the target class's declared type
    parameters explicitly: ``type Category[**P, **Q] =
    CategoryDeclaration[P, Q]``.  The same transformation applies recursively to
    nested aliases such as ``CategoryOfCategories.ObjectType``.  Provider classes
    themselves remain class declarations and therefore retain their ``TypeInfo``.
    """
    declared_classes = {
        statement.name: statement
        for statement in source.body
        if isinstance(statement, ast.ClassDef)
        and statement.type_params
        and all(
            isinstance(parameter, ast.ParamSpec) for parameter in statement.type_params
        )
    }

    def aliases(statements: list[ast.stmt]) -> dict[str, ast.ClassDef]:
        result: dict[str, ast.ClassDef] = {}
        for statement in statements:
            if not isinstance(statement, ast.Assign) or not isinstance(
                statement.value, ast.Name
            ):
                continue
            declaration = declared_classes.get(statement.value.id)
            if declaration is None:
                continue
            for target in statement.targets:
                if isinstance(target, ast.Name):
                    result[target.id] = declaration
        return result

    def type_alias(alias_name: str, declaration: ast.ClassDef) -> ast.TypeAlias:
        parameters = declaration.type_params
        parameter_names = [
            ast.Name(id=parameter.name, ctx=ast.Load()) for parameter in parameters
        ]
        value: ast.expr = ast.Name(id=declaration.name, ctx=ast.Load())
        if parameter_names:
            value = ast.Subscript(
                value=value,
                slice=ast.Tuple(elts=parameter_names, ctx=ast.Load()),
                ctx=ast.Load(),
            )
        return ast.TypeAlias(
            name=ast.Name(id=alias_name, ctx=ast.Store()),
            type_params=[
                ast.copy_location(parameter, declaration) for parameter in parameters
            ],
            value=value,
        )

    def project(
        stub_statements: list[ast.stmt], source_statements: list[ast.stmt]
    ) -> None:
        scope_aliases = aliases(source_statements)
        source_classes = {
            statement.name: statement
            for statement in source_statements
            if isinstance(statement, ast.ClassDef)
        }
        rewritten: list[ast.stmt] = []
        for statement in stub_statements:
            if isinstance(statement, ast.Assign):
                target_names = [
                    target.id
                    for target in statement.targets
                    if isinstance(target, ast.Name)
                ]
                if len(target_names) == 1 and target_names[0] in scope_aliases:
                    alias_name = target_names[0]
                    rewritten.append(type_alias(alias_name, scope_aliases[alias_name]))
                    continue
            if isinstance(statement, ast.ClassDef) and statement.name in source_classes:
                project(statement.body, source_classes[statement.name].body)
            rewritten.append(statement)
        stub_statements[:] = rewritten

    project(tree.body, source.body)


def _source_symbol_tables(
    package: str,
    output_directory: Path,
    sources: tuple[Path, ...],
) -> tuple[
    dict[str, dict[str, str]],
    dict[str, str],
    dict[str, dict[str, str]],
    dict[str, ast.Module],
]:
    """Return source-declared symbols, function returns and value annotations.

    This is a lexical projection only.  It never reads a constructed category or
    native value: imported names, written classes/functions and annotations are
    enough to resolve role expressions such as ``Cat().MorphismType`` and
    ``Fun.MorphismType``.
    """
    trees: dict[str, ast.Module] = {}
    symbols: dict[str, dict[str, str]] = {}
    annotations: dict[str, dict[str, str]] = {}

    for source in sources:
        module = _module_name(package, output_directory, source)
        tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
        trees[module] = tree
        local: dict[str, str] = {}
        for statement in tree.body:
            match statement:
                case ast.Import(names=names):
                    for alias in names:
                        bound = alias.asname or alias.name.split(".")[0]
                        local[bound] = alias.name if alias.asname else bound
                case ast.ImportFrom(module=imported, names=names, level=0) if (
                    imported is not None
                ):
                    for alias in names:
                        local[alias.asname or alias.name] = f"{imported}.{alias.name}"
                case (
                    ast.ClassDef(name=name)
                    | ast.FunctionDef(name=name)
                    | ast.AsyncFunctionDef(name=name)
                ):
                    local[name] = f"{module}.{name}"
        symbols[module] = local

    def path(module: str, expression: ast.expr | None) -> str | None:
        match expression:
            case ast.Name(id=name):
                return symbols[module].get(name)
            case ast.Attribute(value=value, attr=attr):
                base = path(module, value)
                return None if base is None else f"{base}.{attr}"
            case _:
                return None

    # Resolve simple source aliases such as ``Cat = _category.Cat`` before
    # reading annotations and function returns that refer to them.
    changed = True
    while changed:
        changed = False
        for module, tree in trees.items():
            for statement in tree.body:
                if not isinstance(statement, ast.Assign) or len(statement.targets) != 1:
                    continue
                target = statement.targets[0]
                if not isinstance(target, ast.Name):
                    continue
                resolved = path(module, statement.value)
                if resolved is None or symbols[module].get(target.id) == resolved:
                    continue
                symbols[module][target.id] = resolved
                changed = True

    function_returns: dict[str, str] = {}
    for module, tree in trees.items():
        typed_values: dict[str, str] = {}
        for statement in tree.body:
            if isinstance(statement, ast.AnnAssign) and isinstance(
                statement.target, ast.Name
            ):
                resolved = path(module, statement.annotation)
                if resolved is not None:
                    typed_values[statement.target.id] = resolved
            if isinstance(statement, ast.FunctionDef | ast.AsyncFunctionDef):
                resolved = path(module, statement.returns)
                if resolved is not None:
                    function_returns[f"{module}.{statement.name}"] = resolved
        annotations[module] = typed_values
    return symbols, function_returns, annotations, trees


def _source_role_aliases(
    package: str,
    output_directory: Path,
    sources: tuple[Path, ...],
    inheritance: dict[str, dict[str, tuple[str, ...]]],
) -> dict[str, dict[str, str]]:
    """Resolve public aliases to written role declarations without runtime inspection."""
    symbols, function_returns, annotations, trees = _source_symbol_tables(
        package, output_directory, sources
    )
    providers = {
        provider for relations in inheritance.values() for provider in relations
    }
    result: dict[str, dict[str, str]] = {}

    def symbol_path(module: str, expression: ast.expr) -> str | None:
        match expression:
            case ast.Name(id=name):
                return symbols[module].get(name)
            case ast.Attribute(value=value, attr=attr):
                base = symbol_path(module, value)
                return None if base is None else f"{base}.{attr}"
            case _:
                return None

    def value_type(module: str, expression: ast.expr) -> str | None:
        match expression:
            case ast.Name(id=name):
                return annotations[module].get(name)
            case ast.Call(func=func):
                callable_name = symbol_path(module, func)
                return (
                    None
                    if callable_name is None
                    else function_returns.get(callable_name)
                )
            case _:
                return None

    for module, tree in trees.items():
        public = frozenset(_public_names(tree))
        aliases: dict[str, str] = {}
        for statement in tree.body:
            if not isinstance(statement, ast.Assign) or len(statement.targets) != 1:
                continue
            target = statement.targets[0]
            if not isinstance(target, ast.Name) or target.id not in public:
                continue
            value = statement.value
            if not isinstance(value, ast.Attribute) or value.attr not in {
                "ObjectType",
                "ElementType",
                "MorphismType",
            }:
                continue
            owner = value_type(module, value.value)
            if owner is None:
                continue
            declaration = f"{owner}.{value.attr}"
            if declaration in providers:
                aliases[target.id] = declaration
        if aliases:
            result[module] = aliases
    return result


def _qualified_module(name: str, source_modules: frozenset[str]) -> str:
    """Return the longest source-module prefix of one qualified declaration name."""
    candidates = tuple(
        module
        for module in source_modules
        if name == module or name.startswith(f"{module}.")
    )
    if not candidates:
        raise ValueError(f"{name!r} has no source module in the generated package")
    return max(candidates, key=len)


def _ensure_module_imports(tree: ast.Module, modules: set[str]) -> None:
    """Import modules referenced by generated qualified type expressions."""
    imported = {
        alias.name
        for statement in tree.body
        if isinstance(statement, ast.Import)
        for alias in statement.names
    }
    additions = [
        ast.Import(names=[ast.alias(name=module)])
        for module in sorted(modules - imported)
    ]
    tree.body[0:0] = additions


def _project_runtime_class_aliases(
    tree: ast.Module, aliases: dict[str, str], source_modules: frozenset[str]
) -> None:
    """Replace ``Incomplete`` runtime class values by aliases to their declarations."""
    if not aliases:
        return
    rewritten: list[ast.stmt] = []
    used = False
    for statement in tree.body:
        name = None
        if isinstance(statement, ast.AnnAssign) and isinstance(
            statement.target, ast.Name
        ):
            name = statement.target.id
        elif isinstance(statement, ast.Assign):
            targets = [
                target.id
                for target in statement.targets
                if isinstance(target, ast.Name)
            ]
            if len(targets) == 1:
                name = targets[0]
        target = aliases.get(name) if name is not None else None
        if target is None:
            rewritten.append(statement)
            continue
        rewritten.append(
            ast.TypeAlias(
                name=ast.Name(id=name, ctx=ast.Store()),
                type_params=[],
                value=_base_expression(target),
            )
        )
        used = True
    tree.body[:] = rewritten
    if used:
        _ensure_module_imports(
            tree,
            {_qualified_module(target, source_modules) for target in aliases.values()},
        )


def _project_provider_bases(
    tree: ast.Module,
    module: str,
    providers: dict[str, tuple[str, ...]],
    source_modules: frozenset[str],
) -> None:
    required_modules: set[str] = set()
    for statement in _classes(tree.body, module):
        bases = providers.get(statement.name)
        if bases is None:
            continue
        statement.node.bases = [_base_expression(base) for base in bases]
        required_modules.update(
            _qualified_module(base, source_modules) for base in bases
        )
    _ensure_module_imports(tree, required_modules)


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
