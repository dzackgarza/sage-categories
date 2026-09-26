"""Valid and violating consumers for the architecture gates."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import tomllib
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from rule_coverage import unclassified_source_modules

CONFIG = Path("pyproject.toml")
SOURCE_ROOT = "sage_categories"
FIXTURE_ROOT = "fixturepkg"


def check_unclassified_source_rejection() -> None:
    """A new source module must enter one of the declared architecture packages."""
    with tempfile.TemporaryDirectory(prefix="sage-categories-architecture-") as directory:
        root = Path(directory) / SOURCE_ROOT
        (root / "kernel").mkdir(parents=True)
        (root / "kernel" / "__init__.py").write_text("")
        assert unclassified_source_modules(root, CONFIG) == []
        (root / "unclassified.py").write_text("value = 1\n")
        assert unclassified_source_modules(root, CONFIG) == ["unclassified.py"]


def lint_imports(directory: Path, config: Path) -> subprocess.CompletedProcess[str]:
    """Run the same pinned Import Linter used by ``just architecture-boundary``."""
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(directory)
    return subprocess.run(
        [
            "uvx",
            "--python",
            "3.14",
            "--from",
            "import-linter==2.15",
            "lint-imports",
            "--config",
            str(config),
        ],
        cwd=directory,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
    )


def translated(module: str) -> str:
    """Move one repository module spelling into the isolated fixture package."""
    if module == SOURCE_ROOT:
        return FIXTURE_ROOT
    prefix = f"{SOURCE_ROOT}."
    if module.startswith(prefix):
        return f"{FIXTURE_ROOT}.{module[len(prefix):]}"
    return module


def module_file(root: Path, module: str) -> Path:
    """Create an importable package module and return its ``__init__.py``."""
    directory = root.joinpath(*module.split("."))
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / "__init__.py"
    target.touch()
    return target


def contract_config(contract: Mapping[str, Any]) -> str:
    """Render one repository forbidden contract for the isolated fixture package."""
    sources = [translated(module) for module in contract["source_modules"]]
    forbidden = [translated(module) for module in contract["forbidden_modules"]]
    lines = [
        "[tool.importlinter]",
        f"root_package = {json.dumps(FIXTURE_ROOT)}",
        "include_external_packages = true",
        "exclude_type_checking_imports = true",
        "",
        "[[tool.importlinter.contracts]]",
        f"name = {json.dumps(contract['name'])}",
        'type = "forbidden"',
        f"source_modules = {json.dumps(sources)}",
        f"forbidden_modules = {json.dumps(forbidden)}",
    ]
    if "allow_indirect_imports" in contract:
        lines.append(f"allow_indirect_imports = {str(contract['allow_indirect_imports']).lower()}")
    ignores = [translated(pattern) for pattern in contract.get("ignore_imports", [])]
    if ignores:
        lines.append(f"ignore_imports = {json.dumps(ignores)}")
        lines.append('unmatched_ignore_imports_alerting = "none"')
    return "\n".join(lines) + "\n"


def forbidden_contracts() -> tuple[Mapping[str, Any], ...]:
    """Read the authoritative forbidden contracts from the repository config."""
    data = tomllib.loads(CONFIG.read_text())
    return tuple(
        contract
        for contract in data["tool"]["importlinter"]["contracts"]
        if contract["type"] == "forbidden"
    )


def fixture_for_contract(root: Path, contract: Mapping[str, Any]) -> tuple[Path, str, str]:
    """Create the package skeleton for one translated contract."""
    module_file(root, FIXTURE_ROOT)
    sources = [translated(module) for module in contract["source_modules"]]
    forbidden = [translated(module) for module in contract["forbidden_modules"]]
    for module in (*sources, *forbidden):
        module_file(root, module)
    config = root / "architecture.toml"
    config.write_text(contract_config(contract))
    return config, sources[0], forbidden[0]


def check_each_forbidden_contract() -> None:
    """Every configured forbidden contract accepts a valid tree and rejects its direct violation."""
    for contract in forbidden_contracts():
        with tempfile.TemporaryDirectory(prefix="sage-categories-import-contract-") as directory:
            root = Path(directory)
            config, source, forbidden = fixture_for_contract(root, contract)
            allowed = f"{FIXTURE_ROOT}.allowed"
            module_file(root, allowed)
            module_file(root, source).write_text(f"import {allowed}\n")
            valid = lint_imports(root, config)
            assert valid.returncode == 0, valid.stdout + valid.stderr

            module_file(root, source).write_text(f"import {forbidden}\n")
            violating = lint_imports(root, config)
            output = violating.stdout + violating.stderr
            assert violating.returncode != 0, output
            assert contract["name"] in output, output


def check_indirect_forbidden_import_rejection() -> None:
    """At least one contract that forbids indirect imports rejects a two-hop dependency."""
    contract = next(
        contract
        for contract in forbidden_contracts()
        if not contract.get("allow_indirect_imports", False)
        and translated(contract["forbidden_modules"][0]).startswith(f"{FIXTURE_ROOT}.")
    )
    with tempfile.TemporaryDirectory(prefix="sage-categories-indirect-contract-") as directory:
        root = Path(directory)
        config, source, forbidden = fixture_for_contract(root, contract)
        bridge = f"{FIXTURE_ROOT}.bridge"
        module_file(root, source).write_text(f"import {bridge}\n")
        module_file(root, bridge).write_text(f"import {forbidden}\n")
        violating = lint_imports(root, config)
        output = violating.stdout + violating.stderr
        assert violating.returncode != 0, output
        assert contract["name"] in output, output
        assert bridge in output, output



def check_allowed_indirect_imports() -> None:
    """Contracts that explicitly allow indirect imports accept a public-owner bridge."""
    for contract in forbidden_contracts():
        if not contract.get("allow_indirect_imports", False):
            continue
        with tempfile.TemporaryDirectory(prefix="sage-categories-allowed-indirect-") as directory:
            root = Path(directory)
            config, source, forbidden = fixture_for_contract(root, contract)
            bridge = f"{FIXTURE_ROOT}.public_owner"
            module_file(root, source).write_text(f"import {bridge}\n")
            module_file(root, bridge).write_text(f"import {forbidden}\n")
            valid = lint_imports(root, config)
            assert valid.returncode == 0, valid.stdout + valid.stderr

def ignore_importer(pattern: str, source: str) -> tuple[str, str]:
    """Instantiate one configured ignore edge as a concrete importer and target."""
    importer_pattern, target = (part.strip() for part in translated(pattern).split("->", 1))
    source_component = source.split(".", 1)[1].split(".", 1)[0]
    importer = importer_pattern.replace("**", "adapter").replace("*", source_component)
    return importer, target


def check_designated_allowed_importers() -> None:
    """Configured ignore edges remain valid exceptions to their forbidden contract."""
    for contract in forbidden_contracts():
        ignores = contract.get("ignore_imports", [])
        for ignore in ignores:
            with tempfile.TemporaryDirectory(prefix="sage-categories-import-exception-") as directory:
                root = Path(directory)
                config, source, _forbidden = fixture_for_contract(root, contract)
                importer, target = ignore_importer(ignore, source)
                module_file(root, target)
                module_file(root, importer).write_text(f"import {target}\n")
                valid = lint_imports(root, config)
                assert valid.returncode == 0, valid.stdout + valid.stderr



def ast_grep_scan(root: Path, rule: str, target: Path) -> subprocess.CompletedProcess[str]:
    """Run one repository architecture rule against an isolated fixture tree."""
    return subprocess.run(
        [
            "uvx",
            "--from",
            "ast-grep-cli==0.45.0",
            "ast-grep",
            "scan",
            "--rule",
            str(Path.cwd() / ".ast-grep" / "architecture" / rule),
            str(target.relative_to(root)),
        ],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
    )


def check_leaf_firewall_boundaries() -> None:
    """Protected engine/native/Sage imports are forbidden outside and allowed inside ``_firewall``."""
    cases = (
        (
            "no-engine-import-outside-leaf-firewall.yml",
            "from sage_categories.engines.gap import GAP\n",
        ),
        (
            "no-native-realization-outside-leaf-firewall.yml",
            "from sage_categories.cat.native import NativeRealizationRegistry\n",
        ),
        (
            "no-direct-sage-import-in-a-leaf.yml",
            "from sage.all import ZZ\n",
        ),
    )
    for rule, source in cases:
        with tempfile.TemporaryDirectory(prefix="sage-categories-ast-boundary-") as directory:
            root = Path(directory)
            leaf = root / "src" / SOURCE_ROOT / "algebra"
            firewall = leaf / "_firewall"
            firewall.mkdir(parents=True)
            outside = leaf / "outside.py"
            inside = firewall / "inside.py"
            outside.write_text(source)
            inside.write_text(source)

            violating = ast_grep_scan(root, rule, leaf)
            output = violating.stdout + violating.stderr
            assert violating.returncode != 0, output
            assert "outside.py" in output, output
            assert "inside.py" not in output, output

            outside.unlink()
            valid = ast_grep_scan(root, rule, leaf)
            assert valid.returncode == 0, valid.stdout + valid.stderr

def main() -> None:
    check_unclassified_source_rejection()
    check_each_forbidden_contract()
    check_indirect_forbidden_import_rejection()
    check_allowed_indirect_imports()
    check_designated_allowed_importers()
    check_leaf_firewall_boundaries()
    print(
        "architecture-regressions: exhaustive source classification and valid/violating "
        "fixtures for every forbidden contract behave as required"
    )


if __name__ == "__main__":
    main()
