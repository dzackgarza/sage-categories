"""Generate static stubs from the compiler's declared category graph.

The generator starts with ``mypy.stubgen``'s source projection, then rewrites only
category-owned provider bases from the compiler's retained declaration relation.  It
never reads a tracked ``.pyi`` file as input (`POL-TYPE-025`, `POL-TYPE-026`).
"""

from __future__ import annotations

import ast
import copy
import os
import subprocess
import sys
from collections.abc import Iterator
from importlib import import_module
from pathlib import Path
from tempfile import TemporaryDirectory

__all__ = ["generate_stubs"]


def generate_stubs(package: str, output_directory: Path) -> tuple[Path, ...]:
    """Write the compiler-derived stub projection for ``package`` to its package directory."""
    sage_bin = os.environ.get("SAGE_BIN")
    output = str(output_directory.resolve())
    if sage_bin is not None:
        subprocess.run(
            [
                sage_bin,
                "-c",
                (f"from pathlib import Path; from sage_categories.kernel.stub_generator import _generate_stubs; _generate_stubs({package!r}, Path({output!r}))"),
            ],
            check=True,
        )
        return tuple(sorted(output_directory.rglob("*.pyi")))
    subprocess.run(
        [
            sys.executable,
            "-c",
            ("import sys; from pathlib import Path; from sage_categories.kernel.stub_generator import _generate_stubs; _generate_stubs(sys.argv[1], Path(sys.argv[2]))"),
            package,
            output,
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
        if _bootstrap_source(output_directory, source):
            import_module(_module_name(package, output_directory, source))
    canonical_exports = _canonical_exports(package, output_directory, sources)
    stubgen_main(
        [
            "--no-import",
            "--parse-only",
            "--output",
            str(output_directory.parent),
            *(str(source) for source in sources),
        ]
    )
    for stub_path in output_directory.rglob("*.pyi"):
        module = _module_name(package, output_directory, stub_path)
        source_path = stub_path.with_suffix(".py")
        if not source_path.exists():
            continue
        source_tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
        tree = ast.parse(stub_path.read_text(encoding="utf-8"), filename=str(stub_path))
        _project_source_value_aliases(tree, source_tree)
        _project_public_static_surface(tree, source_tree)
        _project_quoted_type_parameter_references(tree, source_tree, module)
        stub_path.write_text(ast.unparse(ast.fix_missing_locations(tree)) + "\n", encoding="utf-8")
    _refresh_internal_static_definitions(package, output_directory, sources)
    inheritance = compiler().declared_inheritance()
    runtime_aliases = _source_role_aliases(package, output_directory, sources, inheritance)
    source_modules = frozenset(_module_name(package, output_directory, source) for source in sources)
    category_parameter_counts = _source_category_parameter_counts(sources)
    category_modules = _source_category_modules(package, output_directory, sources)
    source_class_parameters = _source_class_type_parameters(package, output_directory, sources)
    hoisted_role_providers = _source_hoisted_role_providers(package, output_directory, sources)
    source_class_parameters = _include_hoisted_role_parameters(
        source_class_parameters,
        hoisted_role_providers,
    )
    generic_category_bases = _source_generic_category_bases(sources, category_parameter_counts)
    for stub_path in output_directory.rglob("*.pyi"):
        module = _module_name(package, output_directory, stub_path)
        providers = _providers_in_module(inheritance, module)
        source_path = stub_path.with_suffix(".py")
        source_tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
        tree = ast.parse(stub_path.read_text(encoding="utf-8"), filename=str(stub_path))
        _project_public_exports(tree, source_tree)
        _canonicalize_imports(tree, package, canonical_exports)
        _project_class_aliases(tree, source_tree)
        _project_runtime_class_aliases(tree, runtime_aliases.get(module, {}), source_modules)
        if providers:
            _project_provider_bases(tree, module, providers, source_modules, hoisted_role_providers)
        _project_exact_morphism_endpoints(tree)
        _hoist_lexically_cyclic_nested_classes(tree, module)
        _project_category_role_parameters(
            tree,
            source_tree,
            module,
            category_parameter_counts,
            category_modules,
            generic_category_bases,
            source_class_parameters,
            source_modules,
        )
        _project_hoisted_role_defaults(tree, module, hoisted_role_providers)
        stub_path.write_text(ast.unparse(ast.fix_missing_locations(tree)) + "\n", encoding="utf-8")
    return tuple(sorted(output_directory.rglob("*.pyi")))


_CATEGORY_ROLES = ("ObjectType", "ElementType", "MorphismType")
_HIDDEN_CATEGORY_ROLES = {
    "ObjectType": "_ObjectRole",
    "ElementType": "_ElementRole",
    "MorphismType": "_MorphismRole",
}


def _source_category_parameter_counts(sources: tuple[Path, ...]) -> dict[str, int]:
    """Return each category declaration's public generic arity.

    Category declaration class names are repository-wide unique.  The runtime source
    writes all three role names in every category class (POL-CAT-057), so that
    declaration is also the source-derived marker that the first base is a category
    base.  Hidden static role parameters are not counted here.
    """
    result = {"CategoryDeclaration": 2, "Category": 2}
    for source in sources:
        tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
        for statement in tree.body:
            if not isinstance(statement, ast.ClassDef):
                continue
            bound = {name for local in statement.body for name in _statement_names(local)}
            if not set(_CATEGORY_ROLES).issubset(bound):
                continue
            previous = result.get(statement.name)
            hidden_roles = frozenset(_HIDDEN_CATEGORY_ROLES.values())
            arity = sum(parameter.name not in hidden_roles for parameter in statement.type_params)
            assert previous is None or previous == arity, f"category class name {statement.name!r} has conflicting public arities"
            result[statement.name] = arity
    return result


def _source_class_type_parameters(package: str, output_directory: Path, sources: tuple[Path, ...]) -> dict[str, tuple[str, ...]]:
    """Return source-declared generic parameters for every class, including roles."""
    result: dict[str, tuple[str, ...]] = {}
    for source in sources:
        module = _module_name(package, output_directory, source)
        tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
        for declaration in _classes(tree.body, module):
            names = tuple(parameter.name for parameter in declaration.node.type_params)
            if names:
                result[declaration.name] = names
    return result


def _source_hoisted_role_providers(
    package: str,
    output_directory: Path,
    sources: tuple[Path, ...],
) -> dict[str, str]:
    """Map written nested role classes to their direct generated helper TypeInfos.

    Category roles are hoisted into ``_StaticRoles_<Owner>`` by the static projector.
    A compiler provider base must name that direct TypeInfo rather than an inherited
    ``Owner.Role`` spelling: mypy can resolve the inherited name as the same nominal
    class, but generic base substitution through that inherited nested alias loses the
    role's type arguments.  The mapping is source-derived and only covers roles written
    as local classes; role aliases remain aliases to their actual declaration owner.
    """
    result: dict[str, str] = {}
    for source in sources:
        module = _module_name(package, output_directory, source)
        tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
        for owner in tree.body:
            if not isinstance(owner, ast.ClassDef):
                continue
            bound = {name for local in owner.body for name in _statement_names(local)}
            if not set(_CATEGORY_ROLES).issubset(bound):
                continue
            for local in owner.body:
                if not isinstance(local, ast.ClassDef) or local.name not in _CATEGORY_ROLES:
                    continue
                public = f"{module}.{owner.name}.{local.name}"
                result[public] = f"{module}._StaticRoles_{owner.name}.{local.name}"
    return result


def _include_hoisted_role_parameters(
    source_class_parameters: dict[str, tuple[str, ...]],
    hoisted_role_providers: dict[str, str],
) -> dict[str, tuple[str, ...]]:
    """Give each generated role helper the generic parameters of its source role.

    ``_project_provider_bases`` emits the helper TypeInfo to avoid generic loss through
    an inherited nested alias.  Generic specialization still comes from source, so the
    helper receives exactly the parameter tuple written on the public role declaration.
    """
    result = dict(source_class_parameters)
    for public, helper in hoisted_role_providers.items():
        parameters = source_class_parameters.get(public)
        if parameters is not None:
            result[helper] = parameters
    return result


def _source_generic_category_bases(sources: tuple[Path, ...], category_parameter_counts: dict[str, int]) -> frozenset[str]:
    """Return category declarations used as bases anywhere in the package.

    A base can be declared in one module and subclassed in another. Generic role
    parameters therefore belong to the package-wide source graph, not to the module
    currently being projected.
    """

    def base_name(expression: ast.expr) -> str | None:
        while isinstance(expression, ast.Subscript):
            expression = expression.value
        if isinstance(expression, ast.Name):
            return expression.id
        if isinstance(expression, ast.Attribute):
            return expression.attr
        return None

    result: set[str] = set()
    for source in sources:
        tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
        for statement in tree.body:
            if not isinstance(statement, ast.ClassDef) or not statement.bases:
                continue
            bound = {name for local in statement.body for name in _statement_names(local)}
            if not set(_CATEGORY_ROLES).issubset(bound):
                continue
            name = base_name(statement.bases[0])
            if name in category_parameter_counts:
                result.add(name)
    return frozenset(result)


def _source_category_modules(package: str, output_directory: Path, sources: tuple[Path, ...]) -> dict[str, str]:
    """Map each uniquely named category declaration class to its source module."""
    result: dict[str, str] = {}
    for source in sources:
        module = _module_name(package, output_directory, source)
        tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
        for statement in tree.body:
            if not isinstance(statement, ast.ClassDef):
                continue
            bound = {name for local in statement.body for name in _statement_names(local)}
            if not set(_CATEGORY_ROLES).issubset(bound):
                continue
            assert statement.name not in result, f"category class name {statement.name!r} is not repository-wide unique"
            result[statement.name] = module
    return result


def _project_category_role_parameters(
    tree: ast.Module,
    source: ast.Module,
    module: str,
    category_parameter_counts: dict[str, int],
    category_modules: dict[str, str],
    generic_category_bases: frozenset[str],
    source_class_parameters: dict[str, tuple[str, ...]],
    source_modules: frozenset[str],
) -> None:
    """Thread each category's exact three roles through its static inheritance.

    The runtime compiler owns one ``ObjectType``, ``ElementType`` and ``MorphismType``
    for every category.  Python's ordinary override checker can model that dependent
    relation when the static category carrier has three hidden, defaulted parameters.
    Existing public parameters stay first, so ``C[P, Q]`` keeps its source syntax; a
    derived category supplies its own hidden roles to the mathematical base.  Bare
    inheritance from a two-ParamSpec category uses ``...`` for those already-unknown
    constructor parameters rather than inventing ``Any`` or claiming nullary data.

    Local role classes are hoisted to the owner's existing ``_StaticRoles_*`` helper
    (or a new one) so they exist when the class header states its defaults.  The owner
    inherits that helper, preserving ``C.ObjectType`` as the same class TypeInfo.
    """

    def source_role_owners() -> dict[str, ast.ClassDef]:
        owners: dict[str, ast.ClassDef] = {}
        for statement in source.body:
            if not isinstance(statement, ast.ClassDef):
                continue
            bound = {name for local in statement.body for name in _statement_names(local)}
            if set(_CATEGORY_ROLES).issubset(bound):
                owners[statement.name] = statement
        return owners

    def base_name(expression: ast.expr) -> str | None:
        while isinstance(expression, ast.Subscript):
            expression = expression.value
        if isinstance(expression, ast.Name):
            return expression.id
        if isinstance(expression, ast.Attribute):
            return expression.attr
        return None

    def expression_fullname(expression: ast.expr) -> str | None:
        while isinstance(expression, ast.Subscript):
            expression = expression.value
        parts: list[str] = []
        while isinstance(expression, ast.Attribute):
            parts.append(expression.attr)
            expression = expression.value
        if not isinstance(expression, ast.Name):
            return None
        parts.append(expression.id)
        return ".".join(reversed(parts))

    def subscript_arguments(expression: ast.Subscript) -> list[ast.expr]:
        return list(expression.slice.elts) if isinstance(expression.slice, ast.Tuple) else [expression.slice]

    source_owners = source_role_owners()

    def role_alias(owner: ast.ClassDef, role: str) -> ast.expr | None:
        for local in owner.body:
            if isinstance(local, ast.Assign) and any(isinstance(target, ast.Name) and target.id == role for target in local.targets):
                if owner.name == "CategoryOfCategories" and role == "ObjectType":
                    return ast.Subscript(
                        value=ast.Name(id="Category", ctx=ast.Load()),
                        slice=ast.Tuple(
                            elts=[ast.Constant(value=Ellipsis), ast.Constant(value=Ellipsis)],
                            ctx=ast.Load(),
                        ),
                        ctx=ast.Load(),
                    )
                return copy.deepcopy(local.value)
            if isinstance(local, ast.TypeAlias) and isinstance(local.name, ast.Name) and local.name.id == role:
                return copy.deepcopy(local.value)
        return None

    def rewrite_local_roles(owner: ast.ClassDef) -> None:
        class RoleReferenceRewriter(ast.NodeTransformer):
            def visit_Attribute(self, node: ast.Attribute) -> ast.expr:
                node = self.generic_visit(node)
                if isinstance(node.value, ast.Name) and node.value.id == owner.name and node.attr in _HIDDEN_CATEGORY_ROLES:
                    return ast.copy_location(
                        ast.Name(id=_HIDDEN_CATEGORY_ROLES[node.attr], ctx=ast.Load()),
                        node,
                    )
                return node

        rewriter = RoleReferenceRewriter()
        for local in owner.body:
            if not isinstance(local, ast.FunctionDef | ast.AsyncFunctionDef):
                continue
            for argument in (
                *local.args.posonlyargs,
                *local.args.args,
                *local.args.kwonlyargs,
            ):
                if argument.annotation is not None:
                    argument.annotation = rewriter.visit(argument.annotation)
            if local.args.vararg is not None and local.args.vararg.annotation is not None:
                local.args.vararg.annotation = rewriter.visit(local.args.vararg.annotation)
            if local.args.kwarg is not None and local.args.kwarg.annotation is not None:
                local.args.kwarg.annotation = rewriter.visit(local.args.kwarg.annotation)
            if local.returns is not None:
                local.returns = rewriter.visit(local.returns)

    top_level = {statement.name: statement for statement in tree.body if isinstance(statement, ast.ClassDef)}
    category_declaration = top_level.get("CategoryDeclaration")
    if category_declaration is not None:
        source_category_declaration = next(
            (statement for statement in source.body if isinstance(statement, ast.ClassDef) and statement.name == "CategoryDeclaration"),
            None,
        )
        assert source_category_declaration is not None, "source has no CategoryDeclaration"
        source_parameters = {parameter.name: parameter for parameter in source_category_declaration.type_params}
        existing = {parameter.name: parameter for parameter in category_declaration.type_params}
        defaults: list[ast.expr] = []
        for hidden in _HIDDEN_CATEGORY_ROLES.values():
            source_parameter = source_parameters.get(hidden)
            assert isinstance(source_parameter, ast.TypeVar), f"source CategoryDeclaration parameter {hidden!r} is not a TypeVar"
            assert source_parameter.default_value is not None, f"source CategoryDeclaration parameter {hidden!r} has no default"
            default = copy.deepcopy(source_parameter.default_value)
            parameter = existing.get(hidden)
            if parameter is None:
                parameter = ast.TypeVar(name=hidden, default_value=copy.deepcopy(default))
                category_declaration.type_params.append(parameter)
                existing[hidden] = parameter
            else:
                assert isinstance(parameter, ast.TypeVar), f"CategoryDeclaration parameter {hidden!r} is not a TypeVar"
                parameter.default_value = copy.deepcopy(default)
            defaults.append(default)

        category_alias = next(
            (
                statement
                for statement in tree.body
                if isinstance(statement, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "Category" for target in statement.targets)
            ),
            None,
        )
        if category_alias is not None and isinstance(category_alias.value, ast.Subscript):
            alias_arguments = subscript_arguments(category_alias.value)
            alias_hidden: list[ast.stmt] = []
            for hidden, default in zip(_HIDDEN_CATEGORY_ROLES.values(), defaults, strict=True):
                name = f"_CategoryDeclaration{hidden}"
                alias_arguments.append(ast.Name(id=name, ctx=ast.Load()))
                if not any(
                    isinstance(statement, ast.Assign) and any(isinstance(target, ast.Name) and target.id == name for target in statement.targets) for statement in tree.body
                ):
                    alias_hidden.append(
                        ast.Assign(
                            targets=[ast.Name(id=name, ctx=ast.Store())],
                            value=ast.Call(
                                func=ast.Attribute(
                                    value=ast.Name(id="_typing", ctx=ast.Load()),
                                    attr="TypeVar",
                                    ctx=ast.Load(),
                                ),
                                args=[ast.Constant(value=name)],
                                keywords=[ast.keyword(arg="default", value=copy.deepcopy(default))],
                            ),
                        )
                    )
            category_alias.value.slice = ast.Tuple(elts=alias_arguments, ctx=ast.Load())
            if alias_hidden:
                index = tree.body.index(category_alias)
                tree.body[index:index] = alias_hidden

    required_helper_modules: set[str] = set()
    new_helpers: list[tuple[ast.ClassDef, ast.ClassDef]] = []
    for owner_name, source_owner in source_owners.items():
        owner = top_level.get(owner_name)
        if owner is None:
            continue
        helper_name = f"_StaticRoles_{owner_name}"
        helper = top_level.get(helper_name)
        if helper is None:
            helper = ast.ClassDef(
                name=helper_name,
                bases=[],
                keywords=[],
                body=[],
                decorator_list=[],
                type_params=[],
            )
            top_level[helper_name] = helper
            new_helpers.append((owner, helper))

        defaults: dict[str, ast.expr] = {}
        for role in _CATEGORY_ROLES:
            nested = next(
                (local for local in owner.body if isinstance(local, ast.ClassDef) and local.name == role),
                None,
            )
            if nested is not None:
                owner.body.remove(nested)
                helper.body.append(nested)
                if not owner.body:
                    owner.body.append(ast.Pass())
            helper_role = next(
                (local for local in helper.body if isinstance(local, ast.ClassDef) and local.name == role),
                None,
            )
            if helper_role is not None:
                role_reference: ast.expr = ast.Attribute(
                    value=ast.Name(id=helper_name, ctx=ast.Load()),
                    attr=role,
                    ctx=ast.Load(),
                )
                role_parameters = tuple(parameter.name for parameter in helper_role.type_params)
                if role_parameters:
                    owner_parameters = {parameter.name for parameter in owner.type_params}
                    role_parameter_set = set(role_parameters)
                    shared_parameters = role_parameter_set & owner_parameters
                    assert not shared_parameters or role_parameter_set <= owner_parameters, (
                        f"{owner_name}.{role} carries only some of its generic parameters on its category owner"
                    )
                    if role_parameter_set <= owner_parameters:
                        role_reference = ast.Subscript(
                            value=role_reference,
                            slice=ast.Tuple(
                                elts=[ast.Name(id=name, ctx=ast.Load()) for name in role_parameters],
                                ctx=ast.Load(),
                            ),
                            ctx=ast.Load(),
                        )
                        for index, base in enumerate(helper_role.bases):
                            fullname = expression_fullname(base)
                            if fullname is None or isinstance(base, ast.Subscript):
                                continue
                            if source_class_parameters.get(fullname) != role_parameters:
                                continue
                            helper_role.bases[index] = ast.Subscript(
                                value=base,
                                slice=ast.Tuple(
                                    elts=[ast.Name(id=name, ctx=ast.Load()) for name in role_parameters],
                                    ctx=ast.Load(),
                                ),
                                ctx=ast.Load(),
                            )
                defaults[role] = role_reference
                continue
            alias = role_alias(owner, role)
            if alias is None:
                alias = role_alias(source_owner, role)
                assert alias is not None, f"{owner_name}.{role} has no static role declaration"
                replacement = ast.Assign(
                    targets=[ast.Name(id=role, ctx=ast.Store())],
                    value=copy.deepcopy(alias),
                )
                for index, local in enumerate(owner.body):
                    if role in _statement_names(local):
                        owner.body[index] = replacement
                        break
                else:
                    owner.body.insert(0, replacement)
            defaults[role] = copy.deepcopy(alias)

        generic_owner = owner_name in generic_category_bases
        role_arguments: list[ast.expr]
        if generic_owner:
            existing = {parameter.name for parameter in owner.type_params}
            for role in _CATEGORY_ROLES:
                hidden = _HIDDEN_CATEGORY_ROLES[role]
                if hidden not in existing:
                    owner.type_params.append(ast.TypeVar(name=hidden, default_value=defaults[role]))
            role_arguments = [ast.Name(id=hidden, ctx=ast.Load()) for hidden in _HIDDEN_CATEGORY_ROLES.values()]
        else:
            role_arguments = [copy.deepcopy(defaults[role]) for role in _CATEGORY_ROLES]

        helper_base: ast.expr | None = None
        category_bases = [base for base in owner.bases if not (isinstance(base, ast.Name) and base.id == helper_name)]
        assert category_bases, f"category declaration {owner_name} has no category base"
        category_base = category_bases[0]
        carrier = category_base.value if isinstance(category_base, ast.Subscript) else category_base
        name = base_name(carrier)
        assert name in category_parameter_counts, f"cannot determine public generic arity of category base {ast.unparse(carrier)}"
        base_module = category_modules.get(name)
        if base_module is not None:
            base_helper_name = f"_StaticRoles_{name}"
            if base_module == module:
                helper_base = ast.Name(id=base_helper_name, ctx=ast.Load())
            else:
                required_helper_modules.add(base_module)
                helper_base = _base_expression(f"{base_module}.{base_helper_name}")
            if not helper.bases:
                helper.bases.append(copy.deepcopy(helper_base))

        public_arity = category_parameter_counts[name]
        if isinstance(category_base, ast.Subscript):
            written_arguments = subscript_arguments(category_base)
            assert len(written_arguments) >= public_arity, (
                f"category base {ast.unparse(category_base)} supplies fewer than its {public_arity} public parameters"
            )
            arguments = written_arguments[:public_arity]
        else:
            arguments = [ast.Constant(value=Ellipsis) for _ in range(public_arity)]
        arguments.extend(role_arguments)
        projected_base = ast.Subscript(
            value=copy.deepcopy(carrier),
            slice=ast.Tuple(elts=arguments, ctx=ast.Load()),
            ctx=ast.Load(),
        )
        owner.bases[:] = [ast.Name(id=helper_name, ctx=ast.Load()), projected_base, *category_bases[1:]]
        if generic_owner:
            rewrite_local_roles(owner)

    for owner, helper in reversed(new_helpers):
        index = tree.body.index(owner)
        tree.body.insert(index, helper)
    required_modules = set(required_helper_modules)
    if category_declaration is not None:
        required_modules.add("sage_categories.kernel.roles")
    _ensure_module_imports(tree, required_modules & source_modules)


def _bootstrap_source(output_directory: Path, source: Path) -> bool:
    """Whether ``source`` participates in the compiler-declaration bootstrap.

    Engine modules own private computation, not category declarations.  Importing
    them while constructing the static category graph is both unnecessary and can
    initialize mutually incompatible native runtimes in the generator process.
    They remain in ``sources`` and are still passed to ``stubgen --no-import``.
    """
    relative = source.relative_to(output_directory)
    return not relative.parts or relative.parts[0] != "engines"


def _module_name(package: str, output_directory: Path, stub_path: Path) -> str:
    relative = stub_path.relative_to(output_directory).with_suffix("")
    parts = relative.parts
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join((package, *parts))


def _internal_static_names(
    package: str,
    output_directory: Path,
    sources: tuple[Path, ...],
) -> dict[str, frozenset[str]]:
    """Return source names used explicitly across package-module boundaries.

    The public projection follows source ``__all__``, so a direct sibling import can
    require a declaration omitted from that public surface although the runtime import
    is valid.  Keep runtime wildcard exports and the static
    package-internal surface distinct: this relation comes from actual source
    imports, not from adding private machinery to ``__all__``.
    """
    modules = {_module_name(package, output_directory, source): source for source in sources}
    declarations: dict[str, frozenset[str]] = {}
    trees: dict[str, ast.Module] = {}
    for module, source in modules.items():
        tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
        trees[module] = tree
        declarations[module] = frozenset(_declared_names(tree))

    references: dict[str, set[str]] = {}
    for module, tree in trees.items():
        module_aliases: dict[str, str] = {}
        for statement in ast.walk(tree):
            if isinstance(statement, ast.ImportFrom) and statement.level == 0:
                imported = statement.module
                if imported in modules:
                    for alias in statement.names:
                        if alias.name in declarations[imported]:
                            references.setdefault(imported, set()).add(alias.name)
                if imported is not None:
                    for alias in statement.names:
                        candidate = f"{imported}.{alias.name}"
                        if candidate in modules:
                            module_aliases[alias.asname or alias.name] = candidate
            elif isinstance(statement, ast.Import):
                for alias in statement.names:
                    if alias.name in modules:
                        module_aliases[alias.asname or alias.name.rsplit(".", 1)[-1]] = alias.name

        for expression in ast.walk(tree):
            if not isinstance(expression, ast.Attribute) or not isinstance(expression.value, ast.Name):
                continue
            imported = module_aliases.get(expression.value.id)
            if imported is None or expression.attr not in declarations[imported]:
                continue
            references.setdefault(imported, set()).add(expression.attr)

    return {module: frozenset(names) for module, names in references.items()}


def _statement_names(statement: ast.stmt) -> frozenset[str]:
    match statement:
        case ast.FunctionDef(name=name) | ast.AsyncFunctionDef(name=name) | ast.ClassDef(name=name):
            return frozenset((name,))
        case ast.AnnAssign(target=ast.Name(id=name)):
            return frozenset((name,))
        case ast.Assign(targets=targets):
            return frozenset(target.id for target in targets if isinstance(target, ast.Name))
        case ast.TypeAlias(name=ast.Name(id=name)):
            return frozenset((name,))
        case _:
            return frozenset()


def _project_internal_definitions(
    tree: ast.Module,
    private_tree: ast.Module,
    names: frozenset[str],
) -> None:
    """Merge explicitly cross-module source declarations omitted by ``__all__``."""
    if not names:
        return
    existing = {name for statement in tree.body for name in _statement_names(statement)}
    declarations: dict[str, list[ast.stmt]] = {}
    for statement in private_tree.body:
        for name in _statement_names(statement):
            declarations.setdefault(name, []).append(statement)

    required = set(names)
    while True:
        selected = {id(statement): statement for name in required for statement in declarations.get(name, ())}
        loaded = {
            expression.id for statement in selected.values() for expression in ast.walk(statement) if isinstance(expression, ast.Name) and isinstance(expression.ctx, ast.Load)
        }
        added = (loaded & declarations.keys()) - required
        if not added:
            break
        required.update(added)

    missing = required - existing
    if not missing:
        return

    additions = [copy.deepcopy(statement) for statement in private_tree.body if _statement_names(statement) & missing]
    projected = {name for statement in additions for name in _statement_names(statement)}
    unresolved = missing - projected
    if unresolved:
        raise ValueError(f"private stub projection omitted package-internal declarations: {sorted(unresolved)!r}")

    required_import_names = {
        expression.id for statement in additions for expression in ast.walk(statement) if isinstance(expression, ast.Name) and isinstance(expression.ctx, ast.Load)
    }

    def bound_name(alias: ast.alias, *, from_import: bool) -> str:
        if alias.asname is not None:
            return alias.asname
        return alias.name if from_import else alias.name.split(".", 1)[0]

    already_imported = {
        bound_name(alias, from_import=isinstance(statement, ast.ImportFrom))
        for statement in tree.body
        if isinstance(statement, ast.Import | ast.ImportFrom)
        for alias in statement.names
    }
    imports: list[ast.stmt] = []
    for statement in private_tree.body:
        if not isinstance(statement, ast.Import | ast.ImportFrom):
            continue
        from_import = isinstance(statement, ast.ImportFrom)
        aliases = [copy.deepcopy(alias) for alias in statement.names if bound_name(alias, from_import=from_import) in required_import_names - already_imported]
        if not aliases:
            continue
        if isinstance(statement, ast.ImportFrom):
            imports.append(
                ast.ImportFrom(
                    module=statement.module,
                    names=aliases,
                    level=statement.level,
                )
            )
        else:
            imports.append(ast.Import(names=aliases))
        already_imported.update(bound_name(alias, from_import=from_import) for alias in aliases)

    insertion = next(
        (index for index, statement in enumerate(tree.body) if not isinstance(statement, ast.Import | ast.ImportFrom)),
        len(tree.body),
    )
    tree.body[insertion:insertion] = imports
    tree.body.extend(additions)


def _refresh_internal_static_definitions(
    package: str,
    output_directory: Path,
    sources: tuple[Path, ...] | None = None,
) -> None:
    """Refresh the package-internal static surface without runtime bootstrap."""
    from mypy.stubgen import main as stubgen_main

    if sources is None:
        sources = tuple(sorted(output_directory.rglob("*.py")))
    internal = _internal_static_names(package, output_directory, sources)
    if not internal:
        return

    with TemporaryDirectory(prefix="sage-categories-private-stubs-") as temporary:
        private_output = Path(temporary)
        stubgen_main(
            [
                "--no-import",
                "--parse-only",
                "--include-private",
                "--output",
                str(private_output),
                *(str(source) for source in sources),
            ]
        )
        private_root = private_output / Path(*package.split("."))
        for module, names in internal.items():
            relative = Path(*module.split(".")[len(package.split(".")) :])
            stub_path = output_directory / relative
            if stub_path.name == output_directory.name:
                stub_path = output_directory / "__init__"
            stub_path = stub_path.with_suffix(".pyi")
            if not stub_path.exists():
                continue
            private_stub = private_root / stub_path.relative_to(output_directory)
            if not private_stub.exists():
                raise FileNotFoundError(private_stub)
            tree = ast.parse(stub_path.read_text(encoding="utf-8"), filename=str(stub_path))
            private_tree = ast.parse(private_stub.read_text(encoding="utf-8"), filename=str(private_stub))
            _project_internal_definitions(tree, private_tree, names)
            stub_path.write_text(ast.unparse(ast.fix_missing_locations(tree)) + "\n", encoding="utf-8")


def _direct_provider_bases(
    bases: tuple[str, ...],
    relations: dict[str, tuple[str, ...]],
) -> tuple[str, ...]:
    """Return the direct nominal bases from one compiler C3 ancestry list.

    ``compiler().declared_inheritance()`` records the complete semantic C3 order so
    the plugin can inspect every inherited declaration.  A Python class declaration,
    however, must name only the maximal branches of that order: listing an ancestor
    before a descendant as a second direct base is an inconsistent MRO.  Remove exactly
    those transitive ancestors while preserving the compiler's order on unrelated
    branches.
    """
    return tuple(base for base in bases if not any(base in relations.get(other, ()) for other in bases if other != base))


def _providers_in_module(
    inheritance: dict[str, dict[str, tuple[str, ...]]],
    module: str,
) -> dict[str, tuple[str, ...]]:
    """Return direct provider bases, pruning ancestry across every role surface.

    One nominal provider has one Python MRO even when an ancestry edge crosses the
    compiler's object/element/arrow reporting surfaces.  In particular a functor is
    an object whose base ``Cat().MorphismType`` is reported on the arrow surface.
    Provider names are therefore global in the projection; reject a duplicate rather
    than silently selecting one surface, then prune against the complete relation.
    """
    all_relations: dict[str, tuple[str, ...]] = {}
    for relations in inheritance.values():
        for provider, bases in relations.items():
            assert provider not in all_relations, f"provider {provider!r} is projected on more than one role surface"
            all_relations[provider] = bases

    prefix = f"{module}."
    return {provider: _direct_provider_bases(bases, all_relations) for provider, bases in all_relations.items() if provider.startswith(prefix)}


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
    return {name: canonical for name, modules in candidates.items() if len(modules) == 1 for canonical in modules}


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
            return tuple(element.value for element in statement.value.elts if isinstance(element, ast.Constant) and isinstance(element.value, str))
    return ()


def _project_source_value_aliases(tree: ast.Module, source: ast.Module) -> None:
    """Restore exact source re-exports that parse-only stubgen cannot infer.

    This covers both value aliases such as ``Cat = _category.Cat`` and imported
    re-exports whose public spelling differs from the imported one, such as
    ``cones as Cones``.  Both are source declarations; neither is a second static
    authority.
    """
    public = frozenset(_public_names(source))
    existing_imports = {alias.asname or alias.name for statement in tree.body if isinstance(statement, ast.Import | ast.ImportFrom) for alias in statement.names}
    imported_aliases: list[ast.ImportFrom] = []
    for statement in source.body:
        if not isinstance(statement, ast.ImportFrom) or statement.module is None or statement.level != 0:
            continue
        for alias in statement.names:
            bound = alias.asname or alias.name
            if bound in public and alias.asname is not None and bound not in existing_imports:
                imported_aliases.append(
                    ast.ImportFrom(
                        module=statement.module,
                        names=[ast.alias(name=alias.name, asname=bound)],
                        level=0,
                    )
                )

    module_aliases: dict[str, str] = {}
    for statement in source.body:
        if isinstance(statement, ast.Import):
            for alias in statement.names:
                module_aliases[alias.asname or alias.name.split(".", 1)[0]] = alias.name
        elif isinstance(statement, ast.ImportFrom) and statement.module is not None and statement.level == 0:
            for alias in statement.names:
                module_aliases[alias.asname or alias.name] = f"{statement.module}.{alias.name}"

    aliases: dict[str, tuple[str, str]] = {}
    for statement in source.body:
        if not isinstance(statement, ast.Assign) or len(statement.targets) != 1:
            continue
        target = statement.targets[0]
        value = statement.value
        if not isinstance(target, ast.Name) or not isinstance(value, ast.Attribute) or not isinstance(value.value, ast.Name):
            continue
        module = module_aliases.get(value.value.id)
        if module is not None:
            aliases[target.id] = (module, value.attr)
    if not aliases and not imported_aliases:
        return

    tree.body[:] = [statement for statement in tree.body if not (_statement_names(statement) & aliases.keys())]
    imports = [
        ast.ImportFrom(
            module=module,
            names=[ast.alias(name=name, asname=target)],
            level=0,
        )
        for target, (module, name) in sorted(aliases.items())
    ]
    imports.extend(imported_aliases)
    insertion = next(
        (index for index, statement in enumerate(tree.body) if not isinstance(statement, ast.Import | ast.ImportFrom)),
        len(tree.body),
    )
    tree.body[insertion:insertion] = imports


def _project_quoted_type_parameter_references(
    tree: ast.Module,
    source: ast.Module,
    module: str,
) -> None:
    """Preserve quoted PEP-695 bounds/defaults exactly as written in source.

    ``stubgen --parse-only`` resolves a quoted forward reference such as
    ``T: "Owner" = "Owner"`` into the eager spelling ``T: Owner = Owner``.
    Under mypy 2.0 that can create placeholder types in a cyclic stub graph and force
    semantic analysis to defer during its final iteration.  The source spelling is
    already valid Python 3.14 typing syntax, so retain those quoted references as part
    of the source-derived static projection rather than asking mypy to reconstruct them.
    """
    source_classes = {declaration.name: declaration.node for declaration in _classes(source.body, module)}
    target_classes = {declaration.name: declaration.node for declaration in _classes(tree.body, module)}
    for name, source_class in source_classes.items():
        target_class = target_classes.get(name)
        if target_class is None:
            continue
        source_parameters = {parameter.name: parameter for parameter in source_class.type_params}
        for parameter in target_class.type_params:
            source_parameter = source_parameters.get(parameter.name)
            if source_parameter is None:
                continue
            if (
                isinstance(parameter, ast.TypeVar)
                and isinstance(source_parameter, ast.TypeVar)
                and isinstance(source_parameter.bound, ast.Constant)
                and isinstance(source_parameter.bound.value, str)
            ):
                parameter.bound = copy.deepcopy(source_parameter.bound)
            source_default = source_parameter.default_value
            if isinstance(source_default, ast.Constant) and isinstance(source_default.value, str):
                parameter.default_value = copy.deepcopy(source_default)


def _project_public_static_surface(tree: ast.Module, source: ast.Module) -> None:
    """Keep the explicit public surface and declarations its signatures require.

    Parse-only stubgen deliberately performs no semantic analysis, so it does not apply
    source ``__all__``.  The source declaration is authoritative.  Starting from those
    names, retain the transitive closure of top-level declarations referenced by their
    generated signatures; package-internal cross-module declarations are added later by
    ``_refresh_internal_static_definitions``.
    """
    public = frozenset(_public_names(source))
    if not public:
        return
    declarations: dict[str, list[ast.stmt]] = {}
    for statement in tree.body:
        for name in _statement_names(statement):
            declarations.setdefault(name, []).append(statement)

    required = set(public)
    while True:
        selected = {id(statement): statement for name in required for statement in declarations.get(name, ())}
        loaded = {
            expression.id for statement in selected.values() for expression in ast.walk(statement) if isinstance(expression, ast.Name) and isinstance(expression.ctx, ast.Load)
        }
        added = (loaded & declarations.keys()) - required
        if not added:
            break
        required.update(added)

    tree.body[:] = [
        statement
        for statement in tree.body
        if isinstance(statement, ast.Import | ast.ImportFrom) or not _statement_names(statement) or bool(_statement_names(statement) & required)
    ]


def _project_public_exports(tree: ast.Module, source: ast.Module) -> None:
    """Keep generated ``__all__`` identical to the source module declaration.

    ``stubgen`` can append function-local class spellings such as ``Local@42`` to
    the generated export list. Those names are not module attributes, so the source
    ``__all__`` remains authoritative. Modules without an explicit export list keep
    ``stubgen``'s ordinary export behavior.
    """
    source_exports = next(
        (
            statement
            for statement in source.body
            if isinstance(statement, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "__all__" for target in statement.targets)
        ),
        None,
    )
    if source_exports is None:
        return
    projected = ast.Assign(
        targets=[ast.Name(id="__all__", ctx=ast.Store())],
        value=ast.List(
            elts=[ast.Constant(value=name) for name in _public_names(source)],
            ctx=ast.Load(),
        ),
    )
    for index, statement in enumerate(tree.body):
        if not isinstance(statement, ast.Assign):
            continue
        if any(isinstance(target, ast.Name) and target.id == "__all__" for target in statement.targets):
            tree.body[index] = projected
            return
    insertion = next(
        (index for index, statement in enumerate(tree.body) if not isinstance(statement, ast.Import | ast.ImportFrom)),
        len(tree.body),
    )
    tree.body.insert(insertion, projected)


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
        statements.extend(ast.ImportFrom(module=module, names=aliases, level=statement.level) for module, aliases in grouped.items())
    tree.body[:] = statements


def _project_class_aliases(
    tree: ast.Module,
    source: ast.Module,
) -> None:
    """Project runtime generic class aliases as legacy generic aliases.

    ``stubgen`` writes ``Category = CategoryDeclaration`` as an inferred alias.
    Mypy cannot parameterize that inferred form. A PEP 695 ``type`` alias binds
    the parameters, but it ceases to be a class and therefore cannot represent
    source declarations such as ``class FullSubcategory(Category[P, Q])``.

    Legacy generic aliases bind free ``ParamSpec`` variables on their right-hand
    side while remaining aliases of the underlying class. This preserves both
    source requirements: ``Category[P, Q]`` remains parameterized and the same
    symbol remains usable as a class base. The projection is idempotent and also
    converts a previously generated PEP 695 alias back to this stronger form.
    """
    declarations = {
        declaration.name: tuple(parameter for parameter in declaration.type_params if isinstance(parameter, ast.ParamSpec))
        for declaration in source.body
        if isinstance(declaration, ast.ClassDef) and any(isinstance(parameter, ast.ParamSpec) for parameter in declaration.type_params)
    }

    def alias_declaration(value: ast.expr) -> str | None:
        carrier = value.value if isinstance(value, ast.Subscript) else value
        if isinstance(carrier, ast.Name) and carrier.id in declarations:
            return carrier.id
        return None

    def projected_value(name: str) -> ast.expr:
        return ast.Subscript(
            value=ast.Name(id=name, ctx=ast.Load()),
            slice=ast.Tuple(
                elts=[ast.Name(id=f"_{name}_{parameter.name}", ctx=ast.Load()) for parameter in declarations[name]],
                ctx=ast.Load(),
            ),
            ctx=ast.Load(),
        )

    used: set[str] = set()

    def project(statements: list[ast.stmt]) -> None:
        rewritten: list[ast.stmt] = []
        for statement in statements:
            if isinstance(statement, ast.ClassDef):
                project(statement.body)
                rewritten.append(statement)
                continue
            if isinstance(statement, ast.Assign):
                declaration = alias_declaration(statement.value)
                if declaration is not None:
                    statement.value = projected_value(declaration)
                    used.add(declaration)
                rewritten.append(statement)
                continue
            if isinstance(statement, ast.TypeAlias):
                declaration = alias_declaration(statement.value)
                if declaration is not None and isinstance(statement.name, ast.Name):
                    used.add(declaration)
                    rewritten.append(
                        ast.Assign(
                            targets=[ast.Name(id=statement.name.id, ctx=ast.Store())],
                            value=projected_value(declaration),
                        )
                    )
                    continue
            rewritten.append(statement)
        statements[:] = rewritten

    project(tree.body)
    if not used:
        return

    has_typing_import = any(
        isinstance(statement, ast.Import) and any(alias.name == "typing" and alias.asname == "_typing" for alias in statement.names) for statement in tree.body
    )
    existing_names = {target.id for statement in tree.body if isinstance(statement, ast.Assign) for target in statement.targets if isinstance(target, ast.Name)}
    rewritten: list[ast.stmt] = []
    if not has_typing_import:
        rewritten.append(ast.Import(names=[ast.alias(name="typing", asname="_typing")]))
    for statement in tree.body:
        rewritten.append(statement)
        if not isinstance(statement, ast.ClassDef) or statement.name not in used:
            continue
        for parameter in declarations[statement.name]:
            name = f"_{statement.name}_{parameter.name}"
            if name in existing_names:
                continue
            keywords = [ast.keyword(arg="default", value=parameter.default_value)] if parameter.default_value is not None else []
            rewritten.append(
                ast.Assign(
                    targets=[ast.Name(id=name, ctx=ast.Store())],
                    value=ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id="_typing", ctx=ast.Load()),
                            attr="ParamSpec",
                            ctx=ast.Load(),
                        ),
                        args=[ast.Constant(value=name)],
                        keywords=keywords,
                    ),
                )
            )
            existing_names.add(name)
    tree.body[:] = rewritten


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
                case ast.ImportFrom(module=imported, names=names, level=0) if imported is not None:
                    for alias in names:
                        local[alias.asname or alias.name] = f"{imported}.{alias.name}"
                case ast.ClassDef(name=name) | ast.FunctionDef(name=name) | ast.AsyncFunctionDef(name=name):
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
            if isinstance(statement, ast.AnnAssign) and isinstance(statement.target, ast.Name):
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
    symbols, function_returns, annotations, trees = _source_symbol_tables(package, output_directory, sources)
    providers = {provider for relations in inheritance.values() for provider in relations}
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
                return None if callable_name is None else function_returns.get(callable_name)
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
    candidates = tuple(module for module in source_modules if name == module or name.startswith(f"{module}."))
    if not candidates:
        raise ValueError(f"{name!r} has no source module in the generated package")
    return max(candidates, key=len)


def _ensure_module_imports(tree: ast.Module, modules: set[str]) -> None:
    """Import modules referenced by generated qualified type expressions."""
    imported = {alias.name for statement in tree.body if isinstance(statement, ast.Import) for alias in statement.names}
    additions = [ast.Import(names=[ast.alias(name=module)]) for module in sorted(modules - imported)]
    tree.body[0:0] = additions


def _project_runtime_class_aliases(tree: ast.Module, aliases: dict[str, str], source_modules: frozenset[str]) -> None:
    """Replace ``Incomplete`` runtime class values by aliases to their declarations."""
    if not aliases:
        return
    rewritten: list[ast.stmt] = []
    used = False
    for statement in tree.body:
        name = None
        if isinstance(statement, ast.AnnAssign) and isinstance(statement.target, ast.Name):
            name = statement.target.id
        elif isinstance(statement, ast.Assign):
            targets = [target.id for target in statement.targets if isinstance(target, ast.Name)]
            if len(targets) == 1:
                name = targets[0]
        target = aliases.get(name) if name is not None else None
        if target is None:
            rewritten.append(statement)
            continue
        assert name is not None
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


def _project_hoisted_role_defaults(
    tree: ast.Module,
    module: str,
    hoisted_role_providers: dict[str, str],
) -> None:
    """Resolve quoted role defaults to the direct generated role TypeInfo.

    Source uses quoted forward references because the role owner may not exist yet at
    runtime class-definition time.  In a completed stub the corresponding role has been
    hoisted to ``_StaticRoles_<Owner>``.  Keeping the quoted public spelling makes mypy
    traverse an inherited nested alias and can erase generic arguments; the direct helper
    TypeInfo is the same nominal class and preserves those arguments.

    Apply the rewrite both to PEP-695 class type parameters and to the legacy ``TypeVar``
    declarations used by the public ``Category`` class alias.
    """

    def direct_role(expression: ast.expr | None) -> ast.expr | None:
        if not isinstance(expression, ast.Constant) or not isinstance(expression.value, str):
            return expression
        spelling = expression.value
        matches = [
            helper
            for public, helper in hoisted_role_providers.items()
            if public.endswith(f".{spelling}") or public == spelling
        ]
        if not matches:
            return expression
        assert len(matches) == 1, f"ambiguous quoted role default {spelling!r}: {matches!r}"
        helper = matches[0]
        local_prefix = f"{module}."
        rendered = helper.removeprefix(local_prefix) if helper.startswith(local_prefix) else helper
        return _base_expression(rendered)

    for declaration in _classes(tree.body, ""):
        for parameter in declaration.node.type_params:
            parameter.default_value = direct_role(parameter.default_value)
            if isinstance(parameter, ast.TypeVar):
                parameter.bound = direct_role(parameter.bound)

    for statement in tree.body:
        if not isinstance(statement, ast.Assign) or not isinstance(statement.value, ast.Call):
            continue
        call = statement.value
        if not (
            isinstance(call.func, ast.Attribute)
            and isinstance(call.func.value, ast.Name)
            and call.func.value.id == "_typing"
            and call.func.attr == "TypeVar"
        ):
            continue
        for keyword in call.keywords:
            if keyword.arg == "default":
                keyword.value = direct_role(keyword.value) or keyword.value


def _project_exact_morphism_endpoints(tree: ast.Module) -> None:
    """Project each concrete ``C.MorphismType`` endpoint as ``C.ObjectType``.

    ``MorphismCategory.ObjectType`` owns ``domain`` and ``codomain`` at runtime.
    The generic owner cannot name the associated object type of every source category
    in an ordinary Python annotation, but the output-only projection can: inside a
    concrete category declaration ``C``, both endpoints of ``C.MorphismType`` have
    exactly ``C.ObjectType`` (POL-CAT-024, POL-TYPE-017).  Add only the static
    specialization; never duplicate the runtime method body or overwrite a method the
    concrete declaration itself owns.
    """

    def endpoint_method(name: str, owner_name: str, morphism_type: ast.ClassDef) -> ast.FunctionDef:
        parameter_names = {parameter.name for parameter in morphism_type.type_params}
        endpoint_parameter = "DomainCategory" if name == "domain" else "CodomainCategory"
        if endpoint_parameter in parameter_names:
            returns: ast.expr = ast.Name(id=endpoint_parameter, ctx=ast.Load())
        else:
            returns = ast.Attribute(
                value=ast.Name(id=owner_name, ctx=ast.Load()),
                attr="ObjectType",
                ctx=ast.Load(),
            )
        return ast.FunctionDef(
            name=name,
            args=ast.arguments(
                posonlyargs=[],
                args=[ast.arg(arg="self")],
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[],
            ),
            body=[ast.Expr(value=ast.Constant(value=Ellipsis))],
            decorator_list=[],
            returns=returns,
            type_comment=None,
            type_params=[],
        )

    for owner in tree.body:
        if not isinstance(owner, ast.ClassDef):
            continue
        morphism_type = next(
            (statement for statement in owner.body if isinstance(statement, ast.ClassDef) and statement.name == "MorphismType"),
            None,
        )
        if morphism_type is None:
            continue
        local_methods = {statement.name for statement in morphism_type.body if isinstance(statement, ast.FunctionDef | ast.AsyncFunctionDef)}
        for name in ("domain", "codomain"):
            if name not in local_methods:
                morphism_type.body.append(endpoint_method(name, owner.name, morphism_type))


def _project_provider_bases(
    tree: ast.Module,
    module: str,
    providers: dict[str, tuple[str, ...]],
    source_modules: frozenset[str],
    hoisted_role_providers: dict[str, str],
) -> None:
    required_modules: set[str] = set()
    for statement in _classes(tree.body, module):
        bases = providers.get(statement.name)
        if bases is None:
            continue
        projected_bases = tuple(hoisted_role_providers.get(base, base) for base in bases)
        statement.node.bases = [_base_expression(base) for base in projected_bases]
        required_modules.update(_qualified_module(base, source_modules) for base in projected_bases)
    _ensure_module_imports(tree, required_modules)


def _hoist_lexically_cyclic_nested_classes(tree: ast.Module, module: str) -> None:
    """Hoist nested classes whose provider ancestry is lexically cyclic.

    A nested class does not exist until Python has executed the body of its owner.
    Thus a generated base relation such as ``Declaration -> Owner.Element`` and
    ``Owner -> Declaration`` is cyclic even though the nominal class graph itself
    contains no edge from ``Owner.Element`` back to ``Owner``.  Model that lexical
    availability edge explicitly.  For every nested class in such a cycle, move its
    class body to a private owner base and make the public owner inherit that base.
    ``Owner.Element`` then resolves to the *same* inherited class object; no assignment
    alias or second declaration is introduced (PLAN-native-engine-remediation 18.1).
    """
    classes = {entry.name: entry.node for entry in _classes(tree.body, module)}
    if not classes:
        return

    top_level = {f"{module}.{statement.name}": statement for statement in tree.body if isinstance(statement, ast.ClassDef)}

    def base_name(expression: ast.expr) -> str | None:
        while isinstance(expression, ast.Subscript):
            expression = expression.value
        parts: list[str] = []
        while isinstance(expression, ast.Attribute):
            parts.append(expression.attr)
            expression = expression.value
        if not isinstance(expression, ast.Name):
            return None
        parts.append(expression.id)
        name = ".".join(reversed(parts))
        if name in classes:
            return name
        local = f"{module}.{name}"
        return local if local in classes else None

    dependencies: dict[str, set[str]] = {name: set() for name in classes}
    for name, node in classes.items():
        for base in node.bases:
            dependency = base_name(base)
            if dependency is not None:
                dependencies[name].add(dependency)
        relative = name.removeprefix(f"{module}.")
        if "." in relative:
            lexical_owner_name = f"{module}.{relative.split('.', 1)[0]}"
            if lexical_owner_name in top_level:
                dependencies[name].add(lexical_owner_name)

    def reaches(start: str, target: str) -> bool:
        frontier = list(dependencies[start])
        seen: set[str] = set()
        while frontier:
            current = frontier.pop()
            if current == target:
                return True
            if current in seen:
                continue
            seen.add(current)
            frontier.extend(dependencies[current] - seen)
        return False

    cyclic = {name for name in classes if reaches(name, name)}
    owners: dict[str, list[ast.ClassDef]] = {}
    for name in cyclic:
        relative = name.removeprefix(f"{module}.")
        if relative.count(".") != 1:
            continue
        owner_name, nested_name = relative.split(".")
        owner_class = top_level.get(f"{module}.{owner_name}")
        if owner_class is None:
            continue
        nested = next(
            (statement for statement in owner_class.body if isinstance(statement, ast.ClassDef) and statement.name == nested_name),
            None,
        )
        if nested is not None:
            owners.setdefault(owner_name, []).append(nested)

    if not owners:
        return

    replacements: dict[str, ast.expr] = {}
    helpers: list[ast.ClassDef] = []
    for owner_name, nested_classes in sorted(owners.items()):
        owner_class = top_level[f"{module}.{owner_name}"]
        nested_names = {nested.name for nested in nested_classes}
        owner_class.body[:] = [statement for statement in owner_class.body if not (isinstance(statement, ast.ClassDef) and statement.name in nested_names)]
        helper_name = f"_StaticRoles_{owner_name}"
        helper_body: list[ast.stmt] = []
        helper_body.extend(nested_classes)
        helper = ast.ClassDef(
            name=helper_name,
            bases=[],
            keywords=[],
            body=helper_body,
            decorator_list=[],
            type_params=[],
        )
        helpers.append(helper)
        owner_class.bases.append(ast.Name(id=helper_name, ctx=ast.Load()))
        for nested in nested_classes:
            replacements[f"{module}.{owner_name}.{nested.name}"] = ast.Attribute(
                value=ast.Name(id=helper_name, ctx=ast.Load()),
                attr=nested.name,
                ctx=ast.Load(),
            )

    for entry in _classes(tree.body, module):
        rewritten: list[ast.expr] = []
        for base in entry.node.bases:
            qualified_base_name = base_name(base)
            replacement = replacements.get(qualified_base_name) if qualified_base_name is not None else None
            if replacement is None:
                rewritten.append(base)
                continue
            if isinstance(base, ast.Subscript):
                rewritten.append(
                    ast.Subscript(
                        value=replacement,
                        slice=base.slice,
                        ctx=ast.Load(),
                    )
                )
            else:
                rewritten.append(replacement)
        entry.node.bases = rewritten

    insertion = next(
        (index for index, statement in enumerate(tree.body) if isinstance(statement, ast.ClassDef)),
        len(tree.body),
    )
    tree.body[insertion:insertion] = helpers


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
