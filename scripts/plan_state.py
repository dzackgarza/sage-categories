"""Validate the selected execution owner without reviving historical phases."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from graphlib import CycleError, TopologicalSorter
import os
from pathlib import Path
import re
import sys
from typing import cast


ROOT = Path(__file__).resolve().parents[1]
FEATURE = "[[FEATURE-functor-owned-category-framework]]"


@dataclass(frozen=True)
class Node:
    state: str
    needs: tuple[str, ...]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def mapping(value: object, name: str) -> dict[str, object]:
    require(isinstance(value, dict), f"{name} is not an object")
    return cast(dict[str, object], value)


def validate_dependencies(nodes: dict[str, Node], finished: str, started: set[str]) -> None:
    for name, node in nodes.items():
        for dependency in node.needs:
            require(dependency in nodes, f"{name}: missing prerequisite {dependency}")
            if node.state in started:
                require(nodes[dependency].state == finished, f"{name}: prerequisite {dependency} is not {finished}")
    try:
        tuple(TopologicalSorter({name: node.needs for name, node in nodes.items()}).static_order())
    except CycleError as error:
        raise ValueError(f"cyclic execution prerequisites: {error.args[1]}") from error


def todo_nodes(text: str) -> dict[str, Node]:
    nodes: dict[str, Node] = {}
    for line in text.splitlines():
        match = re.fullmatch(r"\| `([^`]+)` \| (.*) \| ([^|]*) \|", line)
        require(not line.startswith("| `") or match is not None, "malformed TODO execution row")
        if match is None:
            continue
        name, body, dependencies = match.groups()
        state = re.match(r"\*\*(Closed|Open|Waiting|Authorized)\b", body)
        require(state is not None, f"{name}: unknown execution state")
        require(name not in nodes, f"duplicate execution node {name}")
        require(dependencies == "none" or bool(re.fullmatch(r"`[^`]+`(?:, `[^`]+`)*", dependencies)), f"{name}: malformed prerequisites")
        nodes[name] = Node(cast(re.Match[str], state).group(1), tuple(re.findall(r"`([^`]+)`", dependencies)))
    require(bool(nodes), "TODO.md contains no execution nodes")
    validate_dependencies(nodes, "Closed", {"Closed"})
    return nodes


def validate_milestones(text: str, nodes: dict[str, Node]) -> None:
    """Check routing to A, B and delivery; mathematical coverage needs review."""
    groups: dict[str, set[str]] = {"A": set(), "B": set(), "history": set()}
    section = "history"
    milestones: list[str] = []
    for line in text.splitlines():
        if re.match(r"#{1,3} ", line):
            heading = re.match(r"### Milestone ([AB]) — ", line)
            section = heading.group(1) if heading else "history"
            if heading:
                milestones.append(section)
        row = re.match(r"\| `([^`]+)` \|", line)
        if row:
            groups[section].add(row.group(1))
    require(milestones == ["A", "B"], "TODO requires exactly milestone A then milestone B")
    foundation, leaves, delivery = "kernel-cat-complete", "leaves-complete", "framework-complete"
    require(foundation in groups["A"], f"{foundation} must belong to milestone A")
    require(leaves in groups["B"], f"{leaves} must belong to milestone B")
    require(delivery in groups["B"], f"{delivery} must follow the milestones in the active table")
    groups["B"].remove(delivery)
    active = groups["A"] | groups["B"] | {delivery}

    # Prerequisites precede consumers in this order, so each closure is derived
    # once from the already-validated graph rather than enumerating all paths.
    ancestors: dict[str, set[str]] = {}
    for name in TopologicalSorter({name: node.needs for name, node in nodes.items()}).static_order():
        ancestors[name] = set(nodes[name].needs)
        for dependency in nodes[name].needs:
            ancestors[name].update(ancestors[dependency])

    for name in groups["history"]:
        require(nodes[name].state == "Closed", f"{name}: unfinished work outside active milestones")
        require(not ancestors[name] & active, f"{name}: historical evidence depends on active work")
    for name in groups["A"]:
        require(not ancestors[name] & (groups["B"] | {delivery}), f"{name}: milestone A depends on B or delivery")
        require(name == foundation or name in ancestors[foundation], f"{name}: does not feed milestone A")
    for name in groups["B"]:
        require(foundation in ancestors[name], f"{name}: milestone B bypasses milestone A")
        require(name == leaves or name in ancestors[leaves], f"{name}: does not feed milestone B")
    require(active - {delivery} <= ancestors[delivery], "active work does not all feed framework-complete")


def read_card(path: Path) -> tuple[dict[str, object], str]:
    import yaml

    text = path.read_text()
    frontmatter = re.fullmatch(r"---\r?\n(.*?)\r?\n---(?:\r?\n|$)(.*)", text, re.DOTALL)
    require(frontmatter is not None, f"{path}: missing card frontmatter")
    header, body = cast(re.Match[str], frontmatter).groups()
    try:
        return mapping(yaml.safe_load(header), str(path)), body
    except yaml.YAMLError as error:
        raise ValueError(f"{path}: invalid card frontmatter") from error


def validate_phases(phase_root: Path, core_plan: Path, source_root: Path) -> str:
    require(phase_root.is_dir(), f"phase owner not found: {phase_root}")
    core, core_body = read_card(core_plan)
    require(core.get("id") == "PLAN-pr-8-kernel-cat-architecture-convergence", "wrong historical core-plan owner")
    parents = core.get("parents")
    require(isinstance(parents, list) and FEATURE in parents, "wrong historical core-plan feature")
    nodes: dict[str, Node] = {}
    for path in sorted(phase_root.rglob("PHASE-*.md")):
        card, body = read_card(path)
        name, state = card.get("id"), card.get("status", "unstarted")
        require(isinstance(name, str) and name.startswith("PHASE-"), f"{path}: invalid phase ID")
        require(name not in nodes, f"duplicate phase {name}")
        require(state in ("unstarted", "in-progress", "complete"), f"{name}: invalid phase state")
        needs = card.get("dependsOn", [])
        require(isinstance(needs, list) and all(isinstance(dep, str) and re.fullmatch(r"\[\[[^\[\]]+\]\]", dep) for dep in needs), f"{name}: invalid prerequisite links")
        require(not (card.get("archived") is True and state == "in-progress"), f"{name}: archived phase is active")
        if state == "complete":
            require(bool(re.search(r"^- Accepted revision: [0-9a-f]{7,40}$", body, re.MULTILINE)), f"{name}: missing accepted revision")
        nodes[cast(str, name)] = Node(cast(str, state), tuple(dep[2:-2] for dep in cast(list[str], needs)))
    require(bool(nodes), "phase-managed owner has no phases")
    validate_dependencies(nodes, "complete", {"in-progress", "complete"})
    active = tuple(name for name, node in nodes.items() if node.state == "in-progress")
    require(len(active) == 1, f"phase-managed execution requires one active phase; found {len(active)}")
    core_state = core.get("status")
    require(core_state in ("unstarted", "in-progress", "complete"), "invalid core-plan state")
    match core_state:
        case "complete":
            require(bool(re.search(r"^- Accepted revision: [0-9a-f]{7,40}$", core_body, re.MULTILINE)), "core plan lacks accepted revision")
        case _:
            require(source_root.is_dir(), f"source owner not found: {source_root}")
            foundations = {"kernel", "cat", "cat_kernel", "engines", "__pycache__"}
            leaves = sorted(path.name for path in source_root.iterdir() if path.is_dir() and path.name not in foundations)
            require(not leaves, f"production leaves precede core completion: {', '.join(leaves)}")
    return active[0]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=("issue-dag", "phase-managed"), default="issue-dag")
    vault = Path(os.environ.get("AGENT_MEMORY_VAULT", str(Path.home() / ".agent-memory-vault")))
    parser.add_argument("--phase-root", type=Path, default=vault / "projects/github.com__dzackgarza__sage-categories/plans")
    parser.add_argument("--core-plan", type=Path)
    parser.add_argument("--source-root", type=Path, default=ROOT / "src/sage_categories")
    args = parser.parse_args()
    try:
        match args.model:
            case "issue-dag":
                text = (ROOT / "TODO.md").read_text()
                nodes = todo_nodes(text)
                validate_milestones(text, nodes)
                print(f"plan-state: current TODO prerequisite graph valid ({len(nodes)} nodes)")
            case "phase-managed":
                core = args.core_plan or args.phase_root / "features/FEATURE-functor-owned-category-framework/plans/PLAN-pr-8-kernel-cat-architecture-convergence/PLAN-pr-8-kernel-cat-architecture-convergence.md"
                active = validate_phases(args.phase_root, core, args.source_root)
                print(f"plan-state: historical phase-managed prerequisites valid; active phase {active}")
    except (ValueError, OSError) as error:
        print(f"plan-state: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
