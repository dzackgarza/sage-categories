# Agent instructions

`sage-categories` builds a foundational category framework for Sage mathematics.
The repository is initialized. Deliver each specified capability to its complete public consumer.

## Sources of truth

Each fact has one authoritative home:

| Fact | Owner |
| --- | --- |
| System layers, imports, and bootstrap order | [specs/system.md](specs/system.md) |
| Mathematics and public contracts | Topic specifications linked from [specs/system.md](specs/system.md#ownership-map) |
| Decision provenance and supersession | [specs/decisions.md](specs/decisions.md) |
| Stable policy identifiers and technical constraints | [CONTRIBUTING.md](CONTRIBUTING.md) |
| Execution, review, delegation, and documentation procedure | This file |
| Work order and phase acceptance | Project vault plan and phase cards |
| Current phase status and accepted revision | Phase metadata and its single `Accepted revision` entry |
| Implemented behavior | Source and public execution at the stated Git revision |
| Previous implementation and review history | Git history and archived vault records |

Specifications define intended behavior. Source and execution establish whether it exists.
A passing check, phase label, handoff, or reviewer verdict cannot establish architecture.
The decision index records why a contract changed; the topic specification states the current contract.
Apply a later controlling decision to a stale specification and correct that specification in the same work unit.
Ask about a genuine unresolved choice before implementing dependent behavior. Continue independent authorized work.
Keep current phase names, revisions, failure counts, and review histories out of this file and topic specifications.
Read [specs/glossary.md](specs/glossary.md) when writing project terminology. Use standard mathematical language and exact public names.

## Starting a work unit

For implementation, retrieve the active plan, active phase, and direct prerequisite acceptances through the project vault:

```bash
uvx --python 3.14 --from git+https://github.com/dzackgarza/agent-memory agent-memory <command>
```

Use `plan show`, `phase show`, and `card dag` for their respective owners.
The core plan is `PLAN-pr-8-kernel-cat-architecture-convergence`.
The production plan is `PLAN-foundation-production-tower`.
The static projection plan is `PLAN-mypy-static-projection-remediation`.
Read phase bodies for contracts, not old review records.

Start inspection with `tree` at the smallest useful depth.
Read the complete target and immediate owners. Use focused `rg` queries.
Expand inspection when a constructor, import, or call exposes another required owner.
A status request needs native state evidence; it does not authorize whole-system certification.

Write this short frame once before implementation or delegation:

```text
Assigned objective:
Mathematical owner:
Active phase and direct prerequisites:
Complete consumer boundary:
Acceptance at the exact revision:
```

The consumer boundary names inputs, owning categories, constructors, functors, and public results.
Resolve required public spellings, constructors, result categories, dependencies, fixed exclusions, and acceptance before implementation.
Reuse the frame through retries. Change it only for an authorized change of objective.
An ordinary read, small correction, or status answer needs no separate frame document.
Load skills for the requested operation and observed problems only. A skill reference does not create another task.
Do not reload unchanged contracts within a session. Retain paths and section names for targeted reads.

## Implementation and dependencies

Follow [specs/system.md](specs/system.md#dependency-directions).
Trace each object, point, and morphism through its constructor, named functors, inherited operations, and public result.
Inherited methods must operate on correctly initialized source state.
Acceptance examples must obtain generic operations from their real owner.

Before adding a mechanism, inspect existing generic constructions and their first consumers.
Check retained projections, selected functors, universal data, and predicate machinery before creating local infrastructure.
Use current dependencies and maintained prior art first. Cite a reference for unavoidable local infrastructure.
Propose a dependency when it gives the code clearer mathematical vocabulary.
A new abstraction needs a second real consumer.

Implement each capability with its smallest complete public consumer in the same work unit.
Include all roles needed by the claim: objects, points, morphisms, and functor images.
Exercise actual multiple-target declarations when multiple inheritance is introduced.
Later integration phases compose accepted capabilities; they cannot own an earlier capability's first working example.

If a phase requires unfinished prerequisite work, place that work with its prerequisite owner before proceeding.
Record the corrected dependency once in the cards. Preserve the required behavior.
Production starts after core acceptance and owner approval, in the bootstrap order from `specs/system.md`.
Never implement a core phase and a production leaf in parallel.
An executing leaf unit edits neither kernel source nor kernel-test subtrees; a generic repair is a separate owning unit.

A generic defect belongs to its generic owner. A leaf defect belongs to that leaf.
Repair the complete duplicated responsibility and affected sibling constructions within the authorized boundary.
Preserve required behavior before deleting its former implementation.
Never weaken a type, category declaration, or acceptance claim to pass a check.
Keep engine values private under [specs/leaves.md](specs/leaves.md#computation-engine-boundary).

## Review and acceptance

A phase receives one independent review at a fixed committed revision.
Use `r-gate`; use `r6-gate` for final core closure.
Supply the unchanged acceptance contract, owner sections, revision, and complete consumer boundary.
The reviewer reads that packet and relevant implementation. Expand it only for a concrete dependency.

1. Confirm the revision and the phase's owned architecture rules.
2. Run `just architecture` under **Verification** before grading owned criteria.
3. Exercise every acceptance claim through the real public consumer at that revision.
4. Examine relevant leaf rules, ownership, functorial reuse, and mathematical legibility within the boundary.
5. Report each unmet claim with its owner, location, concrete failure, and required behavior.
6. Accept only when every required claim holds. Record one accepted revision on the phase card.

One public exercise can establish several related criteria. Reuse it and state those claims.
Tests establish only what they execute and assert.
A fixture that implements the generic operation under review cannot establish its availability to a leaf.
A source citation establishes a contract; execution establishes behavior.

After repair, review changed behavior and affected consumers. Reuse still-valid findings and prerequisite evidence.
Reopen a passed claim only for a changed dependency, new counterexample, or corrected controlling contract.
Name the affected claim and dependency before invalidating downstream acceptance.
A documentation location error alone does not invalidate executable behavior.
Record out-of-unit findings with their phase owner. They do not block an unrelated unit.
Keep one current acceptance record and one unresolved-work section on each card.
Archive detailed reviews once; do not paste them into subsequent cards or prompts.
R6 checks integration and remaining required claims. It reuses valid prerequisite acceptance.

## Repeated failures

Apply these actions to observed conditions, regardless of how productive the current work feels:

| Condition | Required action |
| --- | --- |
| Two review rounds, or about an hour, without a landed falsifiable artifact | Stop adding review machinery. Report the mispriced unit, failed capability, and smallest complete repair boundary. |
| A second review adds no new falsifiable finding | Return to the original acceptance claim instead of seeking another verdict. |
| A correction changes only terminology, labels, or file placement | Trace the same public consumer. Correct the owning operation if its failure remains. |
| An acceptance specimen supplies infrastructure a normal consumer must inherit | Remove that substitution from the proof; implement the capability at its owner. |
| Two consecutive implementation turns produce only plans, audits, or status records | Resume the required implementation, or state the exact decision preventing it. |
| A task grows through unrelated review findings | Keep the original unit fixed. Route findings to their owners. |
| A diagnostic total is measured again as the reason for an edit | State the mathematical claim and verify it on a concrete specimen. |
| A task is called difficult because it contains many similar items | Examine one operation and its dependencies; execute independent items as a batch. |
| A known command fails again without new evidence | Read the owned command and first failure. Change the hypothesis before another run. |
| A reviewer requests already-located provenance again | Open the retained locator. Search further only if it is incomplete or contradicted. |

Distinguish recording proven completion from changing a requirement before editing a goal source.
Change a requirement only with user authorization or a controlling decision that already supplies it.
An unanswered question does not create blocker evidence or revoke existing authority.

## Delegation

Delegate only when a bounded independent unit saves work after context and review costs.
Use the existing task classes: `mechanical-unit`, `construction-unit`, and `kernel-core-unit`.
Their files are role adapters; this file owns procedure.
Select available capacity appropriate to the unit. Model names and quotas are not acceptance criteria.

Give each writer disjoint files or an isolated worktree. State ownership before work starts.
Shared dependencies, public exports, and witness files have one writer at a time.
Do not review a boundary while another agent edits it. Review the committed revision after integration.
A delegate receives the frame, owner sections, allowed files, and exact acceptance claims.
It reports delivered behavior, revision or diff, and unresolved claims.
The integrating agent checks the actual diff and consumer against the original frame, then commits the integrated unit.
Delegates do not edit shared phase state. Avoid nested delegation and repeated reviewers for an unchanged question.

## Verification

This repository is before 1.0. Architectural agreement controls acceptance.
Read test guidance before touching a test, and `justfile` before a targeted Sage run.
Use real Sage for Sage behavior and exact arithmetic for exact mathematical claims.
Choose the smallest source-defined specimen or an independent canonical oracle.
Inspect its exact theorem, section, table, or page; independently check ambiguous expected facts.
Sage parity is secondary evidence. Never change expected mathematics to match output.

Exercise relevant public categories, parents, endpoints, images, composition, inheritance, and universal maps.
Each assertion must distinguish a plausible mathematically wrong implementation.
Private layout, class names, caches, call counts, and fixture correctness cannot prove a stronger public claim.
Failures state the failed proposition and expected behavior. Use unique test basenames.
Assertions establish repository behavior rather than re-proving a dependency or theorem alone.
Do not use mocks, simulations, skips, xfails, or assertions about the absence of a former implementation.
Keep explicit enumeration approximations outside foundational paths; warn before large enumeration where explicitly offered.
Measure performance by wall time and input size. Call counts can locate repeated work.
Preserve the legible mathematical sequence over a faster opaque form.

Commit and push hooks own test, lint, type-check, format, stub, and aggregate recipes. Do not run these suites manually.
A targeted Sage-aware exercise is the routine manual exception.
An R-gate also runs `just architecture` on its declared owned rule set.
D132 admits exact architectural invariant checks with file-and-line failures at the architecture push tier.
`scripts/rule_coverage.py` rejects a rule whose file glob matches nothing.
Retain static projection. Add no automated convention enforcement before 1.0.

`just plan-state` enforces one active phase, accepted revisions for complete phases, accepted prerequisites, and core-before-production order.
Keep known red checks, owners, reasons, and permitted checkpoint commands in the active plan.
For a documented red baseline, run required owned architecture and plan-state checks before a kernel checkpoint.
Use `--no-verify` only under that recorded exception, naming the red gate in the commit message.
A new failure needs diagnosis at its owner; it is not a baseline exception.

A docs-only edit runs no repository verification. Commit it with `git commit --no-verify`.
Compare transferred semantics and inspect the diff; do not invent tests for prose consolidation.

## Documentation changes

Edit the one owner. Replace duplicates with a link and the local consequence needed by their reader.
Topic specifications state the full mathematical obligation and leaf input.
Private initialization, caches, and compiler calls belong in resolution.md.
Keep stable policy and decision identifiers while shortening explanations.
Before retiring a source, compare each unique requirement, command, exception, and source locator with its destination.
Preserve uncertainty and supersession. Never promote an inference to a user decision.

Distinguish contradiction, specialization, override, and an undecided choice.
Apply a controlling correction to the whole affected statement and its examples, including constructors and result categories.
A new substantive choice needs user grounding in `specs/decisions.md`, with session and timestamp.
Current explicit instructions establish provenance for the change they authorize.

For an old disputed decision, inspect its existing locator first.
Search Claude sessions, Codex sessions, and ChatGPT recordings before claiming that no source exists.
Use the `reading-transcripts` parser for CLI sessions, including queued user answers.
Read ChatGPT recordings with `just -f /home/dzack/gitclones/chat-on-steroids/justfile transcript <id>`; that justfile also provides `sessions` and `search`.
Report a miss as searched, found, inference, confidence, and gaps. A miss alone cannot strike a decision or invalidate acceptance.
Check the cited content and its consequence for the leaf writer; a locator alone does not establish support.
Inspect external definitions before citing them; retain exact definition or theorem locators.

Write current contracts and remaining work. Keep incident narratives in history.
When removing a requirement, remove its wording instead of adding a prohibition that repeats it.
Update an existing rule before adding another. Each procedural rule needs an observable trigger and an action advancing the capability.

## Session continuity

Phase cards hold contracts, dependencies, remaining delta, acceptance, and the current accepted revision.
Edit them through `agent-memory`. Keep detailed past runs in archived references outside the normal context packet.
Update status once the delivered revision proves the transition.
Historical accepted revisions remain evidence; a documentation edit does not certify new code.

Inspect repository and vault state before edits. Preserve unknown files and concurrent work.
Stage exact files and commit each substantive unit. Push authorized work so it can be recovered.
Use system trash for deletions. Do not use destructive Git operations.
Keep user messages private; public documents contain neutral technical decisions and source locators.

On resume, read the current card and actual tree. Reuse valid prerequisite evidence.
Report remaining capability gaps and necessary user decisions. Keep routine checks and administration brief.
Continue safe authorized work until the requested result exists.
