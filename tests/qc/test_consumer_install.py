"""The built package resolves its native runtime dependency outside the workspace."""

import shutil
import subprocess
import sys
from email.parser import BytesParser
from pathlib import Path
from zipfile import ZipFile

from packaging.requirements import Requirement

ROOT = Path(__file__).resolve().parents[2]


def test_wheel_resolves_native_dependency_without_workspace(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    shutil.copy2(ROOT / "pyproject.toml", source / "pyproject.toml")
    shutil.copytree(
        ROOT / "src" / "sage_categories", source / "src" / "sage_categories"
    )
    shutil.copytree(
        ROOT / "native" / "homotopy-python",
        source / "native" / "homotopy-python",
        ignore=shutil.ignore_patterns("target", ".venv"),
    )
    dist = tmp_path / "dist"
    subprocess.run(
        ["uv", "build", "--wheel", "--out-dir", str(dist)], cwd=source, check=True
    )
    (wheel,) = dist.glob("*.whl")
    with ZipFile(wheel) as archive:
        (metadata_name,) = (
            name for name in archive.namelist() if name.endswith(".dist-info/METADATA")
        )
        metadata = BytesParser().parsebytes(archive.read(metadata_name))
    assert any(
        Requirement(value).name == "sage-categories-homotopy"
        for value in metadata.get_all("Requires-Dist", [])
    )

    environment = tmp_path / "consumer"
    subprocess.run(
        ["uv", "venv", "--python", sys.executable, str(environment)],
        cwd=tmp_path,
        check=True,
    )
    subprocess.run(
        [
            "uv",
            "pip",
            "install",
            "--no-sources",
            "--dry-run",
            "--python",
            str(environment / "bin" / "python"),
            str(wheel),
        ],
        cwd=tmp_path,
        check=True,
    )
