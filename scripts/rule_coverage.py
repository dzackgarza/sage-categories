"""Fail architecture rules that read nothing or source modules with no layer class."""

from __future__ import annotations

import argparse
import sys
import tomllib
from pathlib import Path

import yaml

DEFAULT_RULES = Path(".ast-grep/architecture")
DEFAULT_SOURCE_ROOT = Path("src/sage_categories")
DEFAULT_CONFIG = Path("pyproject.toml")
ROOT_SOURCE_FILES = frozenset({"__init__.py", "_bootstrap.py", "all.py"})


def dead_rule_globs(rules: Path = DEFAULT_RULES, *, root: Path = Path()) -> list[str]:
    """Return architecture-rule globs that read no file under the supplied root."""
    dead: list[str] = []
    for rule_file in sorted(rules.glob("*.yml")):
        rule = yaml.safe_load(rule_file.read_text())
        for glob in rule.get("files", []):
            if not any(root.glob(glob)):
                dead.append(f"{rule['id']}: no file matches '{glob}'")
    return dead


def classified_top_level_packages(config: Path = DEFAULT_CONFIG) -> frozenset[str]:
    """Read source architecture classes from the Import Linter contracts."""
    data = tomllib.loads(config.read_text())
    contracts = data["tool"]["importlinter"]["contracts"]
    packages: set[str] = set()
    prefix = "sage_categories."
    for contract in contracts:
        for field in ("source_modules", "forbidden_modules"):
            for module in contract.get(field, []):
                if module.startswith(prefix):
                    packages.add(module[len(prefix) :].split(".", 1)[0])
    return frozenset(packages)


def unclassified_source_modules(
    source_root: Path = DEFAULT_SOURCE_ROOT,
    config: Path = DEFAULT_CONFIG,
) -> list[str]:
    """Return Python source modules outside every declared architecture class."""
    classified = classified_top_level_packages(config)
    unclassified: list[str] = []
    for source in sorted(source_root.rglob("*.py")):
        relative = source.relative_to(source_root)
        if len(relative.parts) == 1:
            if relative.name not in ROOT_SOURCE_FILES:
                unclassified.append(relative.as_posix())
            continue
        if relative.parts[0] not in classified:
            unclassified.append(relative.as_posix())
    return unclassified


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rules", type=Path, default=DEFAULT_RULES)
    parser.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE_ROOT)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    arguments = parser.parse_args()

    dead = dead_rule_globs(arguments.rules)
    unclassified = unclassified_source_modules(arguments.source_root, arguments.config)
    for line in dead:
        print(f"rule-coverage: {line}")
    for source in unclassified:
        print(f"rule-coverage: unclassified source module '{source}'")
    if dead or unclassified:
        if dead:
            print(f"rule-coverage: {len(dead)} dead glob(s); a rule that reads nothing is not green")
        if unclassified:
            print(
                "rule-coverage: "
                f"{len(unclassified)} source module(s) are outside every architecture class"
            )
        return 1
    print(
        "rule-coverage: "
        f"every glob of {len(list(arguments.rules.glob('*.yml')))} rules reads at least one file; "
        f"every source module is classified by {len(classified_top_level_packages(arguments.config))} architecture packages"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
