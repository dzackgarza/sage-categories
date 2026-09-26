"""Negative consumers for the architecture gates."""

from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

from rule_coverage import unclassified_source_modules


def check_unclassified_source_rejection() -> None:
    """A new source module must enter one of the declared architecture packages."""
    with tempfile.TemporaryDirectory(prefix="sage-categories-architecture-") as directory:
        root = Path(directory) / "sage_categories"
        (root / "kernel").mkdir(parents=True)
        (root / "kernel" / "__init__.py").write_text("")
        assert unclassified_source_modules(root, Path("pyproject.toml")) == []
        (root / "unclassified.py").write_text("value = 1\n")
        assert unclassified_source_modules(root, Path("pyproject.toml")) == ["unclassified.py"]


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


def check_indirect_forbidden_import_rejection() -> None:
    """A forbidden contract must reject a dependency reached through an intermediate module."""
    with tempfile.TemporaryDirectory(prefix="sage-categories-import-contract-") as directory:
        root = Path(directory)
        package = root / "fixturepkg"
        for name in ("foundation", "bridge", "leaf"):
            target = package / name
            target.mkdir(parents=True)
            (target / "__init__.py").write_text("")
        (package / "__init__.py").write_text("")
        (package / "foundation" / "__init__.py").write_text("import fixturepkg.bridge\n")
        (package / "bridge" / "__init__.py").write_text("import fixturepkg.leaf\n")
        config = root / "architecture.toml"
        config.write_text(
            "[tool.importlinter]\n"
            "root_package = \"fixturepkg\"\n"
            "\n"
            "[[tool.importlinter.contracts]]\n"
            "name = \"Foundation imports no leaf\"\n"
            "type = \"forbidden\"\n"
            "source_modules = [\"fixturepkg.foundation\"]\n"
            "forbidden_modules = [\"fixturepkg.leaf\"]\n"
        )
        violating = lint_imports(root, config)
        assert violating.returncode != 0, violating.stdout + violating.stderr
        assert "Foundation imports no leaf" in violating.stdout + violating.stderr

        (package / "bridge" / "__init__.py").write_text("value = 1\n")
        valid = lint_imports(root, config)
        assert valid.returncode == 0, valid.stdout + valid.stderr


def main() -> None:
    check_unclassified_source_rejection()
    check_indirect_forbidden_import_rejection()
    print("architecture-regressions: valid and violating classification/import fixtures behave as required")


if __name__ == "__main__":
    main()
