"""Execution-gate behavior at the shell entry point and historical card owner."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def gate_repo(tmp_path: Path) -> tuple[Path, dict[str, str]]:
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    for name in ("plan_state.sh", "plan_state.py"):
        shutil.copyfile(ROOT / "scripts" / name, scripts / name)
    (tmp_path / "TODO.md").write_text(
        "| `core` | **Closed.** Accepted. | none |\n"
        "| `leaf` | **Open.** Pending. | `core` |\n"
    )
    plan = {
        "id": "PLAN-native-engine-remediation",
        "type": "plan",
        "metadata": {
            "status": "complete",
            "archived": True,
            "parents": ["[[FEATURE-functor-owned-category-framework]]"],
        },
    }
    report = {
        "repo": "dzackgarza/sage-categories",
        "status": "ok",
        "root": {
            "kind": "present",
            "ref": {"number": 36, "repo_ref": {"owner": "dzackgarza", "repo": "sage-categories"}},
        },
        "metrics": {"errors": 0, "open_work_units": 23},
    }
    (tmp_path / "plan.json").write_text(json.dumps(plan))
    (tmp_path / "report.json").write_text(json.dumps(report))
    binaries = tmp_path / "bin"
    binaries.mkdir()
    # Substitute only the external command responses. The real shell gate and
    # local prerequisite validator execute unchanged, including failure exits.
    uvx = binaries / "uvx"
    uvx.write_text(
        f"#!{sys.executable}\n"
        "import pathlib, sys\n"
        "match sys.argv[-4:]:\n"
        "    case ['agent-memory', 'plan', 'show', 'PLAN-native-engine-remediation']:\n"
        "        name = 'plan.json'\n"
        "    case ['itree', 'doctor', 'dzackgarza/sage-categories', '--json']:\n"
        "        name = 'report.json'\n"
        "    case _: raise SystemExit('unexpected native validator command')\n"
        "print(pathlib.Path(name).read_text())\n"
    )
    uv = binaries / "uv"
    uv.write_text(
        f"#!{sys.executable}\n"
        "import os, sys\n"
        "arguments = sys.argv[sys.argv.index('python') + 1:]\n"
        "os.execv(sys.executable, [sys.executable, *arguments])\n"
    )
    uvx.chmod(0o755)
    uv.chmod(0o755)
    return tmp_path, {**os.environ, "PATH": str(binaries) + os.pathsep + os.environ["PATH"]}


def run_gate(repo: Path, environment: dict[str, str], *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", "scripts/plan_state.sh", *arguments],
        cwd=repo, env=environment, capture_output=True, text=True, timeout=20,
    )


def test_issue_dag_does_not_reactivate_archived_phases(gate_repo: tuple[Path, dict[str, str]]) -> None:
    repo, env = gate_repo
    phase = repo / "PHASE-archived.md"
    phase.write_text("---\nid: PHASE-archived\nstatus: complete\narchived: true\n---\n")
    original = phase.read_bytes()
    result = run_gate(repo, env)
    assert result.returncode == 0, result.stderr
    assert "current TODO prerequisite graph valid" in result.stdout
    assert phase.read_bytes() == original


@pytest.mark.parametrize(
    ("filename", "path", "value"),
    [
        ("plan.json", ("id",), "PLAN-wrong-owner"),
        ("plan.json", ("metadata", "parents"), ["[[FEATURE-other]]"]),
        ("report.json", ("status",), "error"),
        ("report.json", ("metrics", "errors"), 1),
        ("report.json", ("root", "ref", "number"), 99),
        ("report.json", ("root", "ref", "repo_ref", "repo"), "other"),
    ],
)
def test_wrong_or_invalid_native_owner_fails(
    gate_repo: tuple[Path, dict[str, str]], filename: str, path: tuple[str, ...], value: object,
) -> None:
    repo, env = gate_repo
    data = json.loads((repo / filename).read_text())
    current = data
    for key in path[:-1]:
        current = current[key]
    current[path[-1]] = value
    (repo / filename).write_text(json.dumps(data))
    assert run_gate(repo, env).returncode != 0


@pytest.mark.parametrize(
    "todo",
    [
        "| `leaf` | **Closed.** | `missing` |\n",
        "| `core` | **Open.** | none |\n| `leaf` | **Closed.** | `core` |\n",
        "| `a` | **Open.** | `b` |\n| `b` | **Open.** | `a` |\n",
        "| `a` | **Closed.** | none |\n| `a` | **Closed.** | none |\n",
        "| `a` | **Closed.** | none |\n| `malformed` | **Open.** |\n",
    ],
)
def test_invalid_current_prerequisites_fail(gate_repo: tuple[Path, dict[str, str]], todo: str) -> None:
    repo, env = gate_repo
    (repo / "TODO.md").write_text(todo)
    assert run_gate(repo, env).returncode != 0


def write_card(path: Path, card: dict[str, object], accepted: bool = True) -> None:
    body = "- Accepted revision: abc1234\n" if accepted else ""
    path.write_text("---\n" + yaml.safe_dump(card) + "---\n" + body)


@pytest.mark.parametrize("fault", [None, "prerequisite", "missing", "revision", "core-order", "archived", "two-active", "no-active"])
def test_historical_phase_model(gate_repo: tuple[Path, dict[str, str]], fault: str | None) -> None:
    repo, env = gate_repo
    phases = repo / "phases"
    phases.mkdir()
    source = repo / "src/sage_categories"
    (source / "algebra").mkdir(parents=True)
    core = {
        "id": "PLAN-pr-8-kernel-cat-architecture-convergence",
        "status": "complete",
        "parents": ["[[FEATURE-functor-owned-category-framework]]"],
    }
    first: dict[str, object] = {"id": "PHASE-A", "status": "complete"}
    second: dict[str, object] = {"id": "PHASE-B", "status": "in-progress", "dependsOn": ["[[PHASE-A]]"]}
    match fault:
        case "prerequisite": first["status"] = "unstarted"
        case "missing": second["dependsOn"] = ["[[PHASE-missing]]"]
        case "core-order": core["status"] = "in-progress"
        case "archived": second["archived"] = True
        case "two-active": write_card(phases / "PHASE-C.md", {"id": "PHASE-C", "status": "in-progress"})
        case "no-active": second["status"] = "complete"
        case None | "revision": pass
    write_card(phases / "core.md", core)
    write_card(phases / "PHASE-A.md", first, accepted=fault != "revision")
    write_card(phases / "PHASE-B.md", second)
    before = {p: p.read_bytes() for p in phases.iterdir()}
    result = run_gate(
        repo, env, "phase-managed", "--phase-root", str(phases),
        "--core-plan", str(phases / "core.md"), "--source-root", str(source),
    )
    assert (result.returncode == 0) == (fault is None), result.stdout + result.stderr
    assert {p: p.read_bytes() for p in phases.iterdir()} == before
