"""The static projection: ``.pyi`` stubs generated from the compiled ownership graph (POL-TYPE-024, POL-TYPE-025, POL-TYPE-026).

A checker cannot see the role classes the compiler builds: ``compile_category``
assigns them onto the category *value*, and their bases come from a C3 merge over
the selected graph.  This module projects that same compile-time computation into
``.pyi`` files, so a checker reads the compiled inheritance from source it can
parse.  It computes owners per name and constructs no value image, exactly as
method compilation does (POL-KERNEL-001).

The projection of one category ``C`` and one role:

- the node is ``compiler.node(C, role)``; ``Mor(n, C).ObjectType`` normalizes to
  ``Mor(n-1, C).MorphismType``, so it names that node's class and declares none of
  its own (POL-CAT-021);
- the stub class is ``C``'s *local declaration* class with its written bases
  replaced by the role classes of the codomains of ``structure_functors()`` in
  declaration order, or by the kernel role base when there are none.  The name a
  declaration already carries is the name of the compiled role: a declared
  parameter or result naming a role of ``D`` therefore already names ``D``'s
  compiled role, and accepts the compiled role of any ``C`` that reaches ``D``,
  because that role is its subclass;
- a category that declares no class of its own for a role gets a generated class
  ``<C><Role>`` in the stub of the module that declares ``C``;
- ``ObjectType``, ``ElementType``, and ``MorphismType`` are read-only properties
  returning ``type`` of those classes.  Only the compiler writes them.

The level shift is outside the projection, and so is the point category it comes
from.  ``{X}`` is built by ``Cat().Point(X)`` from a value, at any moment in a
session; ``{C}``'s generalized elements are then the objects of ``C`` at stage
``1`` and its morphisms at stage ``[1]``, and ``compiler.install_level_shift``
writes those spellings straight onto the classes ``C``'s roles already are.  That
is a runtime refinement of the compiled graph, not a declaration: a stub that
carried it would describe whichever point categories one session happened to
build, and the same declarations would project differently in the next.  So the
projection follows selected functors only -- which is also why the shift
contributes no base -- and a category with a point category gets a stub stating
its declared surface and nothing of the shift.  Every other construction family
is excluded for the same reason it is not named: a stub is not a dependent type
indexed by runtime category values.

A stub describes exactly the categories declared in the modules of one generation
run.  A codomain declared outside that set fails generation naming its module.  A
downstream package runs the same generator over its own declarations.

The module bodies come from mypy's own ``stubgen``, the mature implementation of
"write a ``.pyi`` for this module"; this module edits only what the compiled graph
determines.
"""

from __future__ import annotations

import importlib
import inspect
import re
import sys
import tempfile
from pathlib import Path
from typing import Any, NamedTuple

from sage.misc.cachefunc import CachedFunction

from sage_categories.cat.category import Category
from sage_categories.kernel import compiler
from sage_categories.kernel.roles import CategoryPoint, Role, kernel_base
from sage_categories.kernel.signatures import declared_signature

__all__ = ["Reference", "RoleProjection", "StubGenerationError", "generate_stubs", "main", "module_name"]


class StubGenerationError(Exception):
    """A declaration the static projection cannot state (POL-TYPE-025, POL-TYPE-029)."""


class Reference(NamedTuple):
    """A name in a stub, together with the module that declares it."""

    module: str
    name: str


class RoleProjection(NamedTuple):
    """One compiled role class as the stub states it."""

    category: Category
    role: Role
    reference: Reference
    bases: tuple[Reference, ...]
    declared: bool


type Projections = dict[tuple[int, Role], RoleProjection]

# One attribute of a category as ``getattr`` returns it: a bound method, a Sage
# cached-method caller, a compiled role class, or retained construction data.
# Python's own introspection admits every value, so the ambiguity is genuine and
# named once here (POL-TYPE-004).
type BoundMember = Any

_ROLE_NAMES = frozenset(role.value for role in Role)

_CLASS_HEADER = re.compile(r"^(?P<indent> *)class (?P<name>\w+)(?P<parameters>\[[^\]]*\])?(?:\((?P<bases>.*)\))?:(?P<body>\s*\.\.\.)?$")
_ROLE_ATTRIBUTE = re.compile(r"^ +(?P<role>ObjectType|ElementType|MorphismType)\s*[:=].*$")
_IMPORT = re.compile(r"^(?:from [\w.]+ import (?P<names>.*)|import (?P<module>[\w.]+)(?: as (?P<alias>\w+))?)$")

_GENERIC_ROLE = {role: kernel_base(role) for role in Role}


# -- the generation set ---------------------------------------------------------


def module_name(path: Path) -> str:
    """The dotted name of the module at ``path``, read from the enclosing packages."""
    resolved = path.resolve()
    parts = [resolved.stem]
    parent = resolved.parent
    while (parent / "__init__.py").exists():
        parts.append(parent.name)
        parent = parent.parent
    return ".".join(reversed(parts))


def _module_paths(targets: tuple[Path, ...]) -> tuple[Path, ...]:
    found: list[Path] = []
    for target in targets:
        found.extend(sorted(target.rglob("*.py")) if target.is_dir() else [target])
    return tuple(found)


def _declared_categories(names: tuple[str, ...]) -> tuple[Category, ...]:
    """Every category the generation set declares: one bound at module level whose class one of these modules writes.

    A module also binds the categories it imports -- ``Fun``, ``Sets`` -- and those
    belong to the modules that declare them, not to the one that uses them.
    """
    found: list[Category] = []
    for name in names:
        for value in vars(sys.modules[name]).values():
            if isinstance(value, Category) and _declaring_class(value).__module__ in names and not any(value is known for known in found):
                found.append(value)
    return tuple(found)


def _takes_no_argument(member: BoundMember) -> bool:
    """Whether a bound method of a category takes nothing beyond its receiver.

    A ``cached_method`` is a Cython caller rather than a function and carries the
    declaration as ``f``, receiver included (``sage.misc.cachefunc``).
    """
    if not callable(member):
        return False
    cached = isinstance(member, CachedFunction)
    parameters = list(inspect.signature(member.f if cached else member).parameters.values())[1 if cached else 0 :]
    return not any(
        parameter.default is parameter.empty
        and parameter.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
        for parameter in parameters
    )


def _constructed(category: Category) -> tuple[Category, ...]:
    """The categories a category's own class declares by a capitalized constructor of no arguments.

    ``Sets().Finite()``, ``Sets().PowerObjects()``, ``Posets().TotallyOrdered()``:
    a property subcategory or construction family that a category retains is named
    by a method of its own class, and that method is its declaration (POL-CAT-083,
    POL-CAT-084).  The constructors ``Category`` declares for every category alike
    -- ``Products()``, ``Subobjects()``, ``Core()`` -- are families over supplied
    data and are reached only where a declaration selects a functor into one.
    """
    found: list[Category] = []
    for name in vars(_declaring_class(category)):
        if not name[:1].isupper() or name in _ROLE_NAMES:
            continue
        member = getattr(category, name)
        if not _takes_no_argument(member):
            continue
        value = member()
        if isinstance(value, Category):
            found.append(value)
    return tuple(found)


def _reached(category: Category) -> tuple[Category, ...]:
    """The categories one step of the selected graph reaches from one, at any role.

    ``compiler.controlled_bases`` follows the selected functors and nothing else.
    A level shift is deliberately not among them: it points at a point category
    ``{X}``, which ``Cat().Point(X)`` builds from a runtime value, and it installs
    its spellings on classes the compiler has already built.  A stub states the
    declarations, so neither the point category nor the shift enters it.
    """
    return tuple(current.category for role in Role for current in compiler.controlled_bases(compiler.node(category, role)))


def _closure(seeds: tuple[Category, ...]) -> tuple[Category, ...]:
    """The seeds with every declared constructor and everything the selected graph reaches, transitively."""
    found = list(seeds)
    frontier = list(seeds)
    while frontier:
        current = frontier.pop(0)
        for reached in (*_constructed(current), *_reached(current)):
            if not any(reached is known for known in found):
                found.append(reached)
                frontier.append(reached)
    return tuple(found)


# -- the role algebra -----------------------------------------------------------


def _reference(klass: type) -> Reference:
    return Reference(klass.__module__, klass.__qualname__)


def _generated_name(category: Category, role: Role) -> str:
    """The stub name of a role class the category declares none of its own for.

    A category that declares no role class is reached by one spelling through the
    declarations -- ``Sets().Countable()``, ``Mor(Sets())`` -- and its ``repr`` is
    that spelling.  The name is that spelling with the punctuation of a call
    removed, so it is the same name on every run over the same declarations.
    """
    return f"{re.sub(r'_+', '_', re.sub(r'\W', '_', repr(category))).strip('_')}_{role.value}"


def _home(category: Category) -> str:
    """The module whose stub carries a generated role class: the one declaring the category it narrows."""
    root = category
    while root.has_ambient():
        root = root.ambient()
    return _declaring_class(root).__module__


def _written(klass: type) -> bool:
    """Whether a class is one a module's source writes, rather than one built at runtime.

    The compiler builds a role class for every node whose category declares none
    (``compiler.empty_local_role``), and ``Mor(C)`` builds its own element role the
    same way.  Such a class is bound nowhere, and a stub must never name one.
    """
    found: object | None = sys.modules.get(klass.__module__)
    for part in klass.__qualname__.split("."):
        found = getattr(found, part, None)
        if found is None:
            return False
    return found is klass


def _declares(category: Category, role: Role) -> bool:
    """Whether the category declares a written class of its own for a role."""
    return _written(category.local_role_class(role))


def _declaring_class(category: Category) -> type:
    """The class a module writes for this category.

    ``type(category)`` is not it: placing a category in a subcategory rebuilds its
    class as a dynamic join (``kernel/refinement.place``), and a category placed in
    its own point category carries a class that no module writes and that a stub
    must never name.  The written class below it is the declaration.
    """
    return next(klass for klass in type(category).__mro__ if _written(klass))


def _role_reference(category: Category, role: Role) -> Reference:
    if _declares(category, role):
        return _reference(category.local_role_class(role))
    return Reference(_home(category), _generated_name(category, role))


def _validate(category: Category, role: Role, local: type[CategoryPoint]) -> None:
    """Every declaration states exact roles, or generation fails at it (POL-TYPE-028, POL-TYPE-029).

    This is the check ``signatures.declared_signature`` makes when a descriptor is
    built: a broad union, ``Any``, ``object``, ``Callable[..., Any]``, or an
    unknown role is rejected at the declaration that carries it.
    """
    declarations: dict[str, compiler.DeclaredMethod] = compiler.local_methods(local)
    for name, function in declarations.items():
        try:
            declared_signature(function, f"{category!r}.{role.value}.{name}", category, role)
        except TypeError as broad:
            raise StubGenerationError(str(broad)) from broad


def _require_in_set(klass: type, modules: frozenset[str], category: Category) -> None:
    if klass.__module__ not in modules:
        raise StubGenerationError(
            f"{category!r} needs {klass.__qualname__}, declared in {klass.__module__}, which is not in the "
            "generation set; run the generator over that module too"
        )


def _bases(category: Category, role: Role, modules: frozenset[str]) -> tuple[Reference, ...]:
    """The role classes of the codomains of ``structure_functors()``, as the compiler orders them.

    ``compiler.controlled_bases`` is the list Python must see: the selected targets
    with the control edges the C3 merge needed.  Declaration order is not it -- a
    category's ambient is both declared and constructed first, so declaration order
    can put a base above a base that derives from it, and no linearization exists.
    A shared class collapses to its last position and a node that reaches none ends
    its chain on the kernel role class of its role, exactly as
    ``compiler._base_classes`` does.
    """
    found: list[Reference] = []
    for target in compiler.controlled_bases(compiler.node(category, role)):
        _require_in_set(_declaring_class(target.category), modules, category)
        reference = _role_reference(target.category, target.role)
        found = [known for known in found if known != reference]
        found.append(reference)
    return tuple(found) if found else (_reference(kernel_base(role)),)


def project(categories: tuple[Category, ...], modules: frozenset[str]) -> Projections:
    """The stub class of each role of each category, keyed by ordinal and role."""
    projections: Projections = {}
    for category in categories:
        _require_in_set(_declaring_class(category), modules, category)
        for role in Role:
            current = compiler.node(category, role)
            if current.category is not category or current.role is not role:
                continue
            if _declares(category, role):
                local = category.local_role_class(role)
                _require_in_set(local, modules, category)
                _validate(category, role, local)
            projections[category.ordinal(), role] = RoleProjection(
                category,
                role,
                _role_reference(category, role),
                _bases(category, role, modules),
                _declares(category, role),
            )
    return projections


def _projection_of(category: Category, role: Role, projections: Projections) -> RoleProjection:
    current = compiler.node(category, role)
    return projections[current.category.ordinal(), current.role]


# -- emission -------------------------------------------------------------------


def _stubgen(paths: tuple[Path, ...], destination: Path) -> None:
    """The module bodies, written by mypy's own stub generator."""
    from mypy.stubgen import generate_stubs as write_stubs, parse_options

    write_stubs(parse_options([*(str(path) for path in paths), "--no-analysis", "-o", str(destination)]))


def _bound_names(lines: list[str]) -> dict[str, str]:
    """Each name the stub already binds, with the module it comes from."""
    found: dict[str, str] = {}
    for line in lines:
        match = _IMPORT.match(line)
        if match is None:
            continue
        if match["module"] is not None:
            found[match["alias"] or match["module"].split(".")[0]] = match["module"]
            continue
        source = line.split(" import ", 1)[0].removeprefix("from ")
        for entry in match["names"].split(","):
            found[entry.strip().split(" as ")[-1].strip()] = source
    return found


def _role_references(category: Category | None, projections: Projections) -> tuple[Reference, ...]:
    """The three role classes of a category class; the kernel bases when the class stands for a family."""
    if category is None:
        return tuple(_reference(_GENERIC_ROLE[role]) for role in Role)
    return tuple(_projection_of(category, role, projections).reference for role in Role)


def _category_classes(module: str, categories: tuple[Category, ...]) -> dict[str, Category | None]:
    """The category classes whose role attributes the projection states.

    A class standing for one live category states that category's role classes.
    ``Category`` states the kernel bases, so every category has the three
    attributes and each narrowing of them is a subtype.  A class standing for a
    family -- a property subcategory, a presented shape -- states nothing and
    keeps whatever its body writes: its instances have different role classes,
    and a stub is not indexed by a runtime category value.
    """
    found: dict[str, Category | None] = {}
    for name, value in vars(sys.modules[module]).items():
        if not isinstance(value, type) or not issubclass(value, Category) or value.__module__ != module:
            continue
        single = [category for category in categories if _declaring_class(category) is value]
        if len(single) == 1:
            found[name] = single[0]
        elif value is Category:
            found[name] = None
    return found


def _resolved(references: set[Reference], module: str, lines: list[str]) -> tuple[dict[Reference, str], list[str]]:
    """The spelling of each reference in this stub, with the imports it needs.

    A name the stub already binds to another module is imported under an alias
    naming its own module: ``Cat().ElementType`` is ``cat.elements.CategoryPoint``
    and every stub also binds ``kernel.roles.CategoryPoint``.
    """
    bound = _bound_names(lines)
    spelling: dict[Reference, str] = {}
    imports: list[str] = []
    for reference in sorted(references):
        if reference.module == module or bound.get(reference.name) == reference.module:
            spelling[reference] = reference.name
            continue
        name = reference.name if reference.name not in bound else f"{reference.name}_{reference.module.rsplit('.', 1)[-1]}"
        spelling[reference] = name
        imports.append(f"from {reference.module} import {reference.name} as {name}")
    return spelling, imports


def _rewrite(text: str, module: str, categories: tuple[Category, ...], projections: Projections) -> str:
    """One module's stub, carrying the compiled bases and the role attributes."""
    owned: dict[str, RoleProjection] = {}
    for projection in projections.values():
        if projection.reference.module != module or not projection.declared:
            continue
        held = owned.setdefault(projection.reference.name, projection)
        # One declaration serves every category of a presented family, and each of
        # them compiles it against its own selected graph.  The stub has one class
        # for the name, so the graphs must agree on its bases.
        if held.bases != projection.bases:
            raise StubGenerationError(
                f"{projection.reference.name} is the {projection.role.value} of both {held.category!r} and "
                f"{projection.category!r}, which reach different categories; a stub has one class for the name"
            )
    generated = sorted(
        (projection for projection in projections.values() if projection.reference.module == module and not projection.declared),
        key=lambda projection: (projection.category.ordinal(), projection.role.value),
    )
    classes = _category_classes(module, categories)
    lines = text.splitlines()
    references = {base for projection in [*owned.values(), *generated] for base in projection.bases}
    references.update(
        reference for name, category in classes.items() for reference in _role_references(category, projections)
    )
    spelling, imports = _resolved(references, module, lines)

    result: list[str] = []
    enclosing: list[tuple[int, str]] = []
    # The role attributes the projection restates, and therefore replaces, in the
    # class body currently open.  A family class keeps the ones its body writes.
    replaced: set[str] = set()
    for line in lines:
        match = _CLASS_HEADER.match(line)
        if match is None:
            attribute = _ROLE_ATTRIBUTE.match(line)
            if attribute is None or attribute["role"] not in replaced:
                result.append(line)
            continue
        indent = len(match["indent"])
        while enclosing and enclosing[-1][0] >= indent:
            enclosing.pop()
        name, parameters = match["name"], match["parameters"] or ""
        qualified = ".".join([*(held for _, held in enclosing), name])
        enclosing.append((indent, name))
        if indent == 0:
            replaced = set()
        if qualified not in owned and qualified not in classes:
            result.append(line)
            continue
        body: list[str] = []
        if qualified in owned:
            bases = ", ".join(spelling[base] for base in owned[qualified].bases)
            result.append(f"{match['indent']}class {name}{parameters}({bases}):")
        else:
            result.append(f"{match['indent']}class {name}{parameters}({match['bases']}):" if match["bases"] else f"{match['indent']}class {name}{parameters}:")
        # A category whose role is a nested class of its own body already names that
        # role: the nested class is the stub type, and a property of the same
        # spelling would shadow it.
        if qualified in classes:
            for role, reference in zip(Role, _role_references(classes[qualified], projections)):
                if reference.name == f"{qualified}.{role.value}":
                    continue
                replaced.add(role.value)
                body.append(f"{match['indent']}    @property")
                body.append(f"{match['indent']}    def {role.value}(self) -> type[{spelling[reference]}]: ...")
        result.extend(body)
        if match["body"] and not body:
            result.append(f"{match['indent']}    ...")
    for projection in generated:
        bases = ", ".join(spelling[base] for base in projection.bases)
        result.append("")
        result.append(f"class {projection.reference.name}({bases}):")
        result.append("    ...")
    return "\n".join([*imports, *result]) + "\n"


# -- the entry point ------------------------------------------------------------


def generate_stubs(targets: tuple[Path, ...], destination: Path | None = None) -> tuple[Path, ...]:
    """Write one ``.pyi`` for each processed module whose declarations the compiled graph projects.

    ``targets`` are Python files or package directories.  Every module is imported,
    every category declared in one of them is compiled through the ownership
    computation of ``kernel/compiler.py``, and the role classes are projected into
    the stubs.  Without ``destination`` each stub is written beside its module, and
    a stub the projection no longer states is removed: the ``.pyi`` files under the
    targets *are* the projection, and a stale one would go on shadowing its module
    for good.  With a ``destination`` the package layout is reproduced under it,
    which is how a downstream package or a test generates stubs for its own
    declarations.
    """
    paths = _module_paths(targets)
    names = tuple(module_name(path) for path in paths)
    for name in names:
        importlib.import_module(name)
    modules = frozenset(names)
    categories = _closure(_declared_categories(names))
    projections = project(categories, modules)
    carried = {projection.reference.module for projection in projections.values()}
    carried.update(_declaring_class(category).__module__ for category in categories)
    selected = tuple((path, name) for path, name in zip(paths, names) if name in carried)
    written: list[Path] = []
    if selected:
        with tempfile.TemporaryDirectory() as scratch:
            _stubgen(tuple(path for path, _ in selected), Path(scratch))
            for path, name in selected:
                produced = Path(scratch).joinpath(*name.split(".")).with_suffix(".pyi")
                stub = path.with_suffix(".pyi") if destination is None else destination.joinpath(*name.split(".")).with_suffix(".pyi")
                stub.parent.mkdir(parents=True, exist_ok=True)
                stub.write_text(_rewrite(produced.read_text(), name, categories, projections))
                written.append(stub)
    if destination is None:
        for stale in (path.with_suffix(".pyi") for path in paths):
            if stale.exists() and not any(stale == stub for stub in written):
                stale.unlink()
    return tuple(written)


def main(arguments: list[str] | None = None) -> None:
    """``python -m sage_categories.kernel.stubs <path> ...``: regenerate the projection in place."""
    supplied = sys.argv[1:] if arguments is None else arguments
    if not supplied:
        raise SystemExit("usage: python -m sage_categories.kernel.stubs <module or package path> ...")
    for stub in generate_stubs(tuple(Path(entry) for entry in supplied)):
        print(stub)


if __name__ == "__main__":
    main()
