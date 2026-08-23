"""Project the declared category graph into a static typing manifest.

The compiler builds object, element and arrow inheritance at runtime from the
structural functors each category selects. A static checker cannot follow a
declared functor, so POL-TYPE-025 asks for that structure to be generated from
the same declarations rather than restated by hand.

One repository revision holds a finite declaration graph, so this walks the live
categories, reads the functors they select, and records for each implementation
class the implementation classes its category reaches. The manifest is the
projection; POL-TYPE-026 makes regenerating it part of the workflows.

Run it under the Sage interpreter, which is where the category graph exists:

    $SAGE_BIN scripts/generate_type_manifest.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sage_categories.category import Category

MANIFEST = Path(__file__).resolve().parent.parent / "type-manifest.json"

ROLES = ("object", "element", "arrow")


def _local_type(category: Category, role: str) -> type | None:
    match role:
        case "object":
            return category.local_object_type()
        case "element":
            return category.local_element_type()
        case "arrow":
            return category.local_arrow_type()
        case _:
            raise AssertionError(role)


def _qualified(implementation: type) -> str:
    return f"{implementation.__module__}.{implementation.__qualname__}"


def _takes_no_argument(value: object) -> bool:
    """Return whether ``value`` can be called with no argument at all."""
    import inspect

    if not callable(value):
        return False
    signature = inspect.signature(value)
    return all(
        parameter.default is not inspect.Parameter.empty
        or parameter.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
        for parameter in signature.parameters.values()
    )


def _reachable_categories() -> list[Category]:
    """Return every category the owned universe constructs, without duplicates."""
    import importlib
    import pkgutil

    import sage_categories
    import sage_categories.all
    from sage_categories.category import Category as CategoryType

    seen: dict[int, Category] = {}
    pending: list[Category] = []
    # Every module of the package, not only the opt-in surface: a category such
    # as ProductElements() is declared beside its theory and is never exported.
    modules = [sage_categories.all]
    for found in pkgutil.walk_packages(sage_categories.__path__, "sage_categories."):
        modules.append(importlib.import_module(found.name))
    # A category reaches this walk two ways: as a module-level value, which the
    # element categories are, or from a constructor that needs no argument,
    # which is how the theories publish theirs. Requiring an empty signature
    # keeps the walk from guessing arguments for anything else.
    for module in modules:
        for name in dir(module):
            value = getattr(module, name)
            if isinstance(value, CategoryType):
                pending.append(value)
                continue
            if isinstance(value, type) or not callable(value):
                continue
            # Only the package's own constructors. A re-exported name such as a
            # typing construct also reads as callable without an argument.
            if not getattr(value, "__module__", "").startswith("sage_categories"):
                continue
            if not _takes_no_argument(value):
                continue
            produced = value()
            if isinstance(produced, CategoryType):
                pending.append(produced)
    while pending:
        category = pending.pop()
        if id(category) in seen:
            continue
        seen[id(category)] = category
        for functor in category.super_functors():
            pending.append(functor.codomain())
    return list(seen.values())


def build_manifest() -> dict[str, dict[str, list[str]]]:
    """Return, per role, the declared base implementations of each local type."""
    manifest: dict[str, dict[str, list[str]]] = {role: {} for role in ROLES}
    for category in _reachable_categories():
        for role in ROLES:
            local = _local_type(category, role)
            if local is None:
                continue
            bases: list[str] = []
            for functor in category.super_functors():
                codomain = functor.codomain()
                if codomain is category:
                    continue
                inherited = _local_type(codomain, role)
                if inherited is None or inherited is local:
                    continue
                name = _qualified(inherited)
                if name not in bases:
                    bases.append(name)
            if not bases:
                continue
            recorded = manifest[role].setdefault(_qualified(local), [])
            for name in bases:
                if name not in recorded:
                    recorded.append(name)
    for role in ROLES:
        manifest[role] = dict(sorted(manifest[role].items()))
    return manifest


def main() -> int:
    manifest = build_manifest()
    rendered = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    if "--check" in sys.argv:
        # Compare what the manifest says, not how it is laid out: the formatter
        # owns its whitespace and collapses short lists that this writes long.
        current = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else None
        if current != manifest:
            print(
                f"ERROR: {MANIFEST.name} is stale. Regenerate it with "
                f"'$SAGE_BIN scripts/generate_type_manifest.py'.",
                file=sys.stderr,
            )
            return 1
        print(f"{MANIFEST.name} matches the declared category graph.")
        return 0
    MANIFEST.write_text(rendered)
    counts = ", ".join(f"{role}: {len(manifest[role])}" for role in ROLES)
    print(f"Wrote {MANIFEST.name} ({counts})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
