# Agent instructions

## Authority

`sage-categories` is a foundational category framework for Sage-based mathematics.
It is already initialized.

Read the applicable owners before each substantive edit or review:

| Subject | Owner |
| --- | --- |
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

Start inspection with `tree` at the smallest useful depth.
Then read each complete target and its immediate owners.
Use focused `rg` queries.
Preserve unknown files and concurrent work.

## Current scope

Execute the active vault DAG in dependency order.
The active architecture-convergence DAG is M0 through M6.
It covers the private kernel, generic `Cat`, and minimal executable witnesses.
Production sets, posets, named sets, rings, modules, algebras, and lattices remain blocked through R6 and owner approval.

Later structures can serve as acceptance examples only.
A generic defect returns to its owning foundational phase and invalidates dependent acceptance.
Never implement a kernel phase and a production leaf in parallel (`POL-DOC-021`).

## Work discipline

Before an edit, identify the violated invariant and its mathematical owner.
Trace objects, elements, and morphisms through their exact constructors and named functors.
Repair generic structure at its canonical owner.
Do not add a leaf workaround.

Use mature dependencies before repository-owned infrastructure.
Keep every engine value private.
Return an owned category, object, element, morphism, functor, proposition, typed-query result, or universal presentation.

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
Do not add automated policy enforcement before 1.0 (`POL-TEST-030`, `POL-TEST-031`).

A docs-only edit runs no verification.
Commit it with `git commit --no-verify`.
Use independent adversarial review at each plan gate.
