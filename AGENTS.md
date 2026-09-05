# Agent instructions

`sage-categories` builds a foundational category framework for Sage mathematics.
The repository is initialized. Deliver each specified capability to its complete public consumer.

These instructions constrain work at its existing boundary. Apply each rule when its stated condition occurs.
They do not require a new checklist, report, agent, or gate for each action.
Use the relevant section while working; keep the rest available by reference.
An explanation of a failure does not establish that its remedy works.
Preserve the original operation and acceptance claim until the delivered behavior establishes them.

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

### Context and attention

Use a search to find the owning definition, then read the whole relevant definition and its immediate callers.
A matching name, excerpt, summary, or commit title selects evidence to inspect; it does not establish the claim.
When output is truncated, narrow the next read to the missing relevant section. Do not repeat the same oversized dump.
Keep current contracts, the active failure, and its evidence in the working context.
Retrieve old history for a disputed decision or repeated failure, rather than routinely replaying the project history.

Separate the requested deliverable from incidental defects exposed while reaching it.
Repair an incidental defect in this unit only when the deliverable depends on that repair.
Record other concrete defects with their existing owners, then return to the assigned operation.
Do not replace difficult implementation with easier policy, typing, environment, or documentation work.
Documentation is the deliverable when the user requests documentation; that does not certify implementation.

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

### Mathematical meaning before implementation shape

For a categorical operation, identify the input categories, result category, and maps that define the result.
Track the distinction between a category, its objects, its points, and its morphisms through each expression.
For a functor, identify both actions and their endpoints. For a universal construction, include its presentation and mediator.
Resolve these from the topic contract before choosing Python classes, tuples, caches, or dispatch branches.
Use ordinary mathematical notation in the task frame when it makes a level or variance distinction explicit.

A representation does not determine its mathematical role.
A tuple representing an element of a product category does not thereby become its image under a product functor.
A Python callable does not establish a functor's morphism action or laws.
A shared runtime base does not make values belong to the same semantic domain.
When a repair relies on one of these identifications, establish the missing map or placement at its owner first.

Check the direction, hypotheses, and scope of an implication before encoding it as category containment.
A property required for one selected functor does not imply that property for every member of its ambient category.
A consequence in one construction does not establish a global implication, its converse, or uniqueness of a choice.
Preserve parameters, endpoint restrictions, and selected data when applying a theorem.
An external theorem supplies mathematical support; the repository still needs the declared map and executable operation.

When the public contract promises a category, functor, or universal presentation, construct that exact object.
Returning its carrier, apex, engine value, or a record bearing its name leaves the missing structure unresolved.
When a named object or operation is absent, keep that absence visible in the assigned claim.
Do not invent a nearby meaning and report completion under the requested name.

### Ownership and dependency reuse

Separate mathematical meaning, runtime execution, and interpretation that needs both layers before moving code.
Use the responsibilities in [specs/system.md](specs/system.md#system-shape), not the convenience of the current import graph.
If a proposed move needs a forbidden dependency, split the responsibilities at the actual boundary.
An import hidden inside a function or a renamed forwarding module does not change dependency direction.
After an ownership repair, follow the original consumer through the new owner and inspect the affected sibling path.
A file move or changed docstring establishes only location until that path works.

Before implementing runtime infrastructure, identify the exact operation the existing dependency already owns.
Exercise its required interlock through the smallest current consumer before building surrounding machinery.
Use the dependency's class construction, ordering, identity, caching, or proposition operation directly where specified.
Importing a library while keeping a second implementation of its job does not delegate that job.
A reference comment does not justify maintaining a duplicate class graph, method graph, or state-transport system.
Add repository code only for the semantic difference that the dependency does not supply.

When two representations of the same relation need synchronization, identify which one derives from the other.
Keep the defining declaration authoritative and derive the runtime or static view through its existing owner.
Do not add another registry to reconcile registries introduced by the same unfinished implementation.
Check whether a proposed cache retains an already-retained value before adding it.
Caching, interning, mathematical equality, and category membership have distinct obligations; do not exchange their checks.

### Construction, scope, and generality

Follow initialization in dependency order: written source data, required functor images, then the inherited operation using that state.
At an initialization failure, identify the exact value, state owner, and first read that occurs too early.
Repair that ordering or ownership. Do not fill the field with a default, replay unrelated constructors, or copy target state in a leaf.
Distinguish the constructing-time contract from the completed public action contract in `resolution.md`.

When independent declarations interfere, inspect the scope of ranks, caches, retained identities, and mutable state first.
Check whether the supposedly conflicting data belongs to the same category, declaration, or interned value.
Do not introduce global precedence, a rejection rule, or a new mathematical constraint to accommodate accidental shared state.
For a fix that depends on construction order, exercise the relevant declarations in both orders in fresh state.
For retained values, check the promised repeated construction and a distinct parameter or owner that must remain distinct.
Use these cases when the claim concerns scope or identity; do not impose a fresh-process matrix on unrelated work.

Distinguish an implementation of a construction from an implementation of one evaluable case.
An identity diagram, terminal apex, equal-leg span, or singleton domain proves only the case it exercises.
Before claiming generality, use an admissible case where the shortcut cannot produce the answer.
For transport, use an action that changes the datum; for composition, use the nonidentity maps required by the claim.
Check a universal mediator with a competing cone or cocone, rather than only reading the stored apex.

If successive examples require branches in the generic operation, re-read its defining construction before adding the next branch.
Use the existing generic calculus or the specified engine domain to cover the required family.
Keep legitimate finite or presented evaluation restrictions explicit at their owner.
Do not expand those restrictions to excuse missing generic representation, retained maps, or declared categorical structure.
A later integration phase composes working capabilities; it cannot retroactively justify accepting an unexercised primitive.

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

### Review the claim independently

Give the reviewer the original contract, observed failure, and relevant diff before the implementer's causal explanation.
The reviewer must derive the disputed behavior from those sources before assessing the proposed remedy.
Another agent repeating the same supplied explanation does not add independent evidence.

Separate a finding from its proposed repair. A true finding can come with a wrong repair.
Rejecting that repair leaves the original failed claim to solve.
Accept a finding because its counterexample or contract argument holds, not because of the reviewer's model or confidence.
Reject a finding with the exact defeating fact; a green scanner or another approving review is insufficient.

Read changed assertions and constructors during review, including lines removed by a claimed strengthening or cleanup.
A test rewrite that removes one target, action, parameter, or public call can reduce the claim while improving presentation.
If evidence is weakened, retain the affected acceptance obligation until an equally strong public exercise replaces it.
A larger unrelated test or a more elaborate report cannot replace that lost evidence.

When an accepted claim fails at its public boundary, reopen that claim and conclusions using the same failed evidence.
Identify the shared premise or mechanism. Recheck those consumers within the assigned boundary.
Do not declare the latest symptom to be the whole defect before following its callers and sibling use.
Retain unrelated acceptance; the scope of invalidation follows evidence, not a blanket restart or automatic exoneration.

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

Keep a correction sequence anchored to the same public operation and expected result.
Renaming the issue, changing files, switching agents, or proposing a new cause does not start a new sequence.
Before another repair of that operation, compare the earlier predicted result with what actually happened.
Identify the premise the observation disproved and the next observation that can distinguish the remaining causes.
Use the existing task frame and unresolved-work entry for this reasoning; do not create another tracking system.

An ordinary failing test during implementation needs diagnosis and repair, not an additional review ceremony.
A failure of a previously claimed public result also invalidates the evidence used for that claim.
An admission, confident new explanation, small diff, or passing private check does not restore that evidence.
Re-establish it through the same public boundary under the unchanged requirement.

When replacing a rejected technique, preserve the obligation that technique tried to meet.
Replacing attribute inspection with exception catching still uses implementation accidents to choose the operation.
Replacing a broad type with another broad alias still loses the mathematical domain.
Replacing explicit leaf wiring with a helper that performs the same wiring leaves its owner unchanged.
Trace the missing declaration, state, or generic operation and repair it there.
Do not add fallback branches, defaults, successful no-ops, or broader exception catches to make execution continue.
Use the specified typed outcome for a legitimately undecided computation; implementation failure must remain visible.

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

A parallel split must have a stable shared interface before writers start.
If both units require changing that interface, complete the prerequisite first or give the coherent change one writer.
Do not split intertwined compiler and consumer changes merely to occupy available agents.
When a delegate violates ownership, return the unchanged claim and concrete failure instead of composing another patch over it.
Reassign an unresolved unit with its correction sequence intact when repeated results fail the same contract.
Adding workers cannot resolve a missing mathematical definition or a contradictory input contract.

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

### Preserve the strength of the example

Write expected results from the contract before using execution to determine whether they hold.
Read each assertion as a proposition: its inputs, quantifiers, expected result, and the wrong behavior it excludes.
Changing the specimen to an easier case changes what it proves, even if its test name stays the same.

For framework acceptance, a small local category may supply its mathematical data, operations, and permitted declarations.
It must receive the framework capability under review exactly as an ordinary leaf receives it.
If setup installs generic methods, registers retained projections, copies inherited state, or directly supplies Python inheritance, inspect its role.
Setup cannot supply the very inheritance, placement, retention, or property propagation the test claims to establish.
Use the closed declaration template and the genuine generic owner for that behavior.

Preserve every material dimension when replacing a nonconforming specimen.
A two-target inheritance claim still needs two actual selected targets and behavior from both after the rewrite.
Repeated refinement of one property cannot substitute for propagation from two targets.
An identity action cannot substitute for a claim about changed target data.
A private helper call cannot substitute for the public constructor or inherited method that failed.
If a lawful replacement exposes a missing capability, repair that capability in the assigned unit.
Removing the unlawful setup does not discharge its intended proof burden.

For a typed query, exercise a registered handler returning a known owned answer through public `ask()`.
Check its semantic value and result category, plus a legitimately undecided case when the contract permits one.
An always-Unknown implementation passes an Unknown-only test; that test cannot establish query dispatch.
For dispatch over generated classes, distinguish semantic domains even when their values share a runtime role or Python base.
Check the affected domain after refinement when refinement is part of the claimed behavior.

Choose the relation the contract requires: Python identity for retained identity, `ask(a == b)` for decided equality.
Constructing a proposition is not deciding it. Python truth conversion cannot replace `ask()`.
Membership alone does not establish the strongest placement, inherited operation, or retained comparison promised by a claim.
Read the result through that promised public operation, including its state and endpoints where relevant.
Do not replace a semantic assertion with a class name, representation string, permissive Boolean, or alternative expected output.

### Diagnostics and generated projections

Treat a type error as evidence about an exact input, output, domain, or projection boundary.
Determine which boundary is wrong before changing its annotation or constructor.
An unavailable annotation during registration can be an initialization problem; widening the domain does not solve it.
Do not move construction from a required property category to its ambient category to bypass a failure.
Correct registration, dispatch, or construction while retaining the specified mathematical type and placement.

Compare generated stubs against the changed declarations and the compiler's semantic projection.
A generator completing successfully does not establish that its output retained inherited methods, bases, and exact domains.
If generation changes unrelated interfaces or depends on prior construction history, identify the generator defect at its owner.
Do not accept those changes as harmless churn, weaken the runtime contract, or maintain an unrecorded second API by hand.
Use only the active plan's explicit checkpoint exception while that defect remains unresolved.

A diagnostic baseline classifies already-established failures; it is not evidence that a new failure is pre-existing.
Attribute a claimed baseline failure to its recorded owner and cause before using the exception.
Read the first concrete failure and the relevant output once. Re-run after a change or new diagnostic question.
Inspect the actual rule scope when a green check is used for acceptance; an empty or wrong scope proves nothing.
Prefer a decisive public exercise to another aggregate diagnostic total.

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

### Corrections, inference, and policy scope

Translate a correction into the changed mathematical or behavioral claim before editing its wording.
Check the entire affected definition, its examples, and its immediate consumers for the same assumption.
A search-and-replace over verbs cannot resolve a responsibility split or a change of result category.
Rewrite the complete owning statement once, then link to it from dependent guidance.

Distinguish a source statement from the inference that applies it to this implementation.
Record derived consequences as derivations, with the assumptions that make them valid.
An agent-authored decision number, repeated citation, or newer timestamp does not turn an inference into a user instruction.
When a source contradicts an inference, correct that inference and its dependent statements together.
Keep unaffected decisions and their provenance intact.

Before presenting an architectural conflict to the user, establish that both claims concern the same mathematical object and scope.
Distinguish declaration-local from global state, mathematical equality from identity, and a construction from its presentation.
Check whether one statement describes intended behavior and the other describes a current implementation defect.
Those two statements do not create a product choice. Repair the defect within the existing contract.
Ask only when the remaining alternatives change required mathematics or observable behavior and the sources do not decide them.

Interpret a policy through its stated invariant and boundary.
Do not extend a rule about leaf engineering to move generic mathematics into the private kernel.
Do not extend a convention check into mathematical certification, or a missing citation into evidence that a contract is false.
A rule violation requires repairing its substantive cause; renaming the construct to evade the rule leaves that cause intact.
If literal wording conflicts with its controlling contract, correct the owning wording instead of building around the contradiction.

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
Put incident details and the evidence behind a rule in its commit and decision locator, not in every future task packet.
After a repeated failure, first check whether an existing rule was bypassed, mis-scoped, or incapable of distinguishing the bad result.
Repair that rule at its owner. Do not append stronger adjectives or add a gate that checks only compliance with another gate.
New automated architectural checks still require the D132 boundary; prose guidance does not authorize additional enforcement machinery.
Judge this guidance by later action on the original capability, not by an agent restating or agreeing with it.

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
