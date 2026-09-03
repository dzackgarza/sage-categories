# Agent instructions

## Authority

`sage-categories` is a foundational category framework for Sage-based mathematics.
It is already initialized.

Read the applicable owners before each substantive edit or review:

| Subject | Owner |
| --- | --- |
| System shape, ownership, dependency order, and task context | [`specs/system.md`](specs/system.md) |
| Decisions and supersession | [`specs/decisions.md`](specs/decisions.md) |
| Compact review policies | [`CONTRIBUTING.md`](CONTRIBUTING.md) |
| `Cat`, `Mor`, `Fun`, actions, and selected functors | [`specs/functor.md`](specs/functor.md) |
| Private Sage compiler and runtime | [`specs/resolution.md`](specs/resolution.md) |
| Leaf and computation-engine boundary | [`specs/leaves.md`](specs/leaves.md) |
| Property categories and refinement | [`specs/property-refinement.md`](specs/property-refinement.md) |
| Propositions, typed queries, and `ask()` | [`specs/undecidable-properties.md`](specs/undecidable-properties.md) |

Cross-reference each material decision and review statement against exact `POL-*` rows and specification sections.
When sources disagree, apply the latest controlling decision in `specs/decisions.md`.
Do not derive architecture from source code, tests, reports, or Git history.

A new policy or substantive specification edit needs transcript grounding under `POL-DOC-018`.
Record its provenance in `specs/decisions.md`.
An inspected external definition uses its exact source under `POL-MATH-040`.
The transcript record has three stores: Claude sessions, Codex sessions, and the ChatGPT recordings (`just -f /home/dzack/gitclones/chat-on-steroids/justfile transcript <id>`).
Check a decision against all three before calling it unsupported, and report a miss as searched, found, inference, confidence, gaps (`POL-DOC-025`, `POL-DOC-026`).
Never write that you understood or learned; write the change into its owning document (`POL-DOC-024`).

## Repository entry

Use the current working tree as the source of truth.
Do not inspect Git history unless the task asks about past work or provenance.

Use the project vault for plans:

```bash
uvx --python 3.14 --from git+https://github.com/dzackgarza/agent-memory agent-memory <command>
```

Retrieve the complete active plan and phase card before work.
Use `card dag` for phase dependencies.
An executing plan contains phase delta and acceptance only (`POL-DOC-013`).

For each work unit, write this task frame before delegation or implementation:

```text
Assigned objective:
Mathematical owner:
Active phase and direct prerequisites:
Complete consumer boundary:
Acceptance at the exact revision:
```

The frame is an input contract.
Do not replace its objective with a review finding, diagnostic count, or local patch.
Reject a work unit when its mathematical owner or consumer boundary is missing.

Start inspection with `tree` at the smallest useful depth.
Then read each complete target and its immediate owners.
Use focused `rg` queries.
Preserve unknown files and concurrent work.

## Current scope

Execute the active vault DAG in dependency order.
The active architecture-convergence DAG is M0 through M6.
It covers the private kernel, generic `Cat`, and minimal executable witnesses.
The active phase is the one core phase whose status is `in-progress`; every other phase is `blocked` until the prerequisite card carries an accepted revision (`POL-DOC-028`, D136).
M0 has an accepted revision (`6566c91`); M1 is the active phase.
Production sets, posets, named sets, rings, modules, algebras, and lattices remain blocked through R6 and owner approval.
The tree holds no production leaf (D137); a leaf enters with its P-phase, rewritten from the templates against the accepted kernel.

After R6, execute the production DAG from [`specs/system.md`](specs/system.md).
It cuts the `Sets()` and `Cardinal()` bootstrap cycle before later leaves begin.

Later structures can serve as acceptance examples only.
A generic defect returns to its owning foundational phase and invalidates dependent acceptance.
Never implement a kernel phase and a production leaf in parallel (`POL-DOC-021`).

## Work discipline

Before an edit, identify the violated invariant and its mathematical owner.
Trace objects, elements, and morphisms through their exact constructors and named functors.
Repair generic structure at its canonical owner.
Do not add a leaf workaround.

Use mature dependencies before repository-owned infrastructure.
Keep every engine value private, except the authorized public SymPy proposition expression.
Owned values inside that expression use private identity atoms.
Return an owned category, object, element, morphism, functor, proposition, typed-query result, or universal presentation.

Continue from canonical specifications, the active DAG, and the current working tree.
Do not use a handoff, report, phase label, or previous agent claim as execution state.

Delegate only a complete work unit from the task frame.
A delegate receives its owner sections, direct prerequisites, full consumer boundary, and unchanged acceptance statement.
A delegate can inspect and edit only that boundary.
Review the result against the original frame and exact revision.
If ownership is wrong, discard the work unit instead of repairing its local patch.

End each substantive work unit in a focused commit.
Stage exact files only.
Do not use destructive Git operations.
Never use `rm`; use system trash.

## Verification

This repository is before 1.0.
Architectural agreement with decisions, specifications, and plans controls acceptance.
Tests and static checks provide diagnostics only.

Do not run repository test, lint, type-check, format, stub, or aggregate-check recipes manually.
Commit and push hooks own those checks.
A targeted Sage-aware test is the only routine manual exception; read `justfile` first.
Do not add automated convention enforcement before 1.0 (`POL-TEST-030`, `POL-TEST-031`).
An architectural invariant check is admitted only under `D132`; it runs in `just architecture` at the push tier.
`just architecture` green on the phase's owned rule set at the exact revision is the precondition of every R-gate; the gate agent runs it first (`POL-DOC-028`).
`just plan-state` at the push tier fails on more than one open phase, a `complete` phase without an accepted revision, an open phase with an incomplete prerequisite, or a leaf package in `src` before R6 (`POL-DOC-029`).
Four gates are red by design until their owning card is accepted: the commit-tier mypy gate on the D131 baseline (owner: the static-projection plan, blocked on R6), the push-tier Sage import contract, the push-tier contract "The kernel imports no module of `Cat`", and the D132 rule `no-mathematics-on-kernel-role` (owner of the last three: M1).
The last two carry D173: the kernel is engineering, `Cat` owns the mathematics every category shares, and the direction is kernel to `Cat` to leaves.
`just architecture` runs `scripts/rule_coverage.py` first, so a rule whose file glob matches nothing is a hard stop rather than a vacuous green (D174).
A kernel commit or push inside that window uses `--no-verify`, and its message names the red gate; `just plan-state` and `just architecture` on the owned set are still run first.

A docs-only edit runs no verification.
Commit it with `git commit --no-verify`.
Use independent adversarial review at each plan gate: the `r-gate` agent (`r6-gate` for R6).
Delegate a work unit only to the executor its phase card names (`mechanical-unit`, `construction-unit`, `kernel-core-unit`; D171).
