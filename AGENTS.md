# Agent instructions

`sage-categories` builds a foundational category framework for Sage mathematics.
The repository is initialized. Deliver each specified capability to its complete public consumer.

These instructions constrain work at its existing boundary. Apply each rule when its stated condition occurs.
They do not require a new checklist, report, agent, or gate for each action.
Use the relevant section while working; keep the rest available by reference.
An explanation of a failure does not establish that its remedy works.
Preserve the original operation and acceptance claim until the delivered behavior establishes them.

## Repository role: integration framework and engine delegation

`sage-categories` is a stitching framework.
It does not own computational algorithms.
It does not establish new mathematical knowledge.
It defers to mature external dependencies as computation engines.

The repository owns three responsibilities only:
1. Present a uniform public API on categories, functors, and morphisms.
2. Weave and coordinate backend engines.
3. Supply kernel and `Cat` machinery to organize, structure, and inherit categories ergonomically for mathematicians.

### Leaf categories and hand-rolled mathematics

Leaf categories must not introduce new bespoke code.
Leaf categories register discovered functionality from external packages and expose it in a unified category form.
Leaves manage backend engines; `Cat` threads operations across engines.

Hand-rolling mathematical algorithms outside `Cat` is prohibited.
Hand-rolled implementations inside `Cat` are equally prohibited when external packages handle the required categorical computations.
Write new mathematical implementations only when verified evidence proves that no external dependency satisfies the requirement.

## Sources of truth

Each fact has one authoritative home:

| Fact | Owner |
| --- | --- |
| System layers, imports, and bootstrap order | [specs/system.md](specs/system.md) |
| Mathematics and public contracts | Topic specifications linked from [specs/system.md](specs/system.md#ownership-map) |
| Decision provenance and supersession | [specs/decisions.md](specs/decisions.md) |
| Stable policy identifiers and technical constraints | [CONTRIBUTING.md](CONTRIBUTING.md) |
| Execution, review, delegation, and documentation procedure | This file |
| Remediation scope, implementation allocation, and work order | Project vault `PLAN-native-engine-remediation` |
| Current execution and acceptance evidence | The governing plan's retained issue dependencies and exact-revision public consumers; retired planning records are historical evidence only |
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

For implementation, retrieve the governing plan through agent-memory:

```bash
agent-memory plan show PLAN-native-engine-remediation
```

When the installed command is unavailable, use the same command through
`uvx --python 3.14 --from git+https://github.com/dzackgarza/agent-memory agent-memory`.

`PLAN-native-engine-remediation` contains the approved detailed plan with its current
amendments. It supersedes every earlier project plan, including their core, production, scaffold,
static-projection, and remediation execution orders. Sections 19 and 20 own the
integration order and complete consumer requirements. Retain the issue dependencies
and mathematical contracts incorporated there, not an independent older plan.

Use `card dag` for current routing. Superseded plans and phases have been removed
from the execution graph. Their historical records remain retrievable through
[the continuation locator](docs/remediation-handoff.md).
Their statuses and acceptance records do not certify the replacement or impose an
additional active-phase prerequisite. Static projection accompanies the same
native-backed operations under section 18.

Start inspection with `tree` at the smallest useful depth.
Read the complete target and immediate owners. Use focused `rg` queries.
Expand inspection when a constructor, import, or call exposes another required owner.
A status request needs native state evidence; it does not authorize whole-system certification.

Write this short frame once before implementation or delegation:

```text
Assigned objective:
Mathematical owner:
Governing plan section, issue owner, and direct prerequisites:
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

Retrieve a governing plan once per work unit and retain its path, relevant sections,
and revision in the existing task context. After an interruption, compare the source
revision and the plan's revision before refreshing either. Read changed sections and
the pending result first. Rebinding an already-bound repository is not a retrieval
step: use `plan show` or `retrieve`. Project initialization and vault-wide indexing
belong to their own setup or maintenance operation, not a routine TODO update.

Before launching another command after an interruption, collect the retained terminal
session's result. A delivery error says nothing about whether its process finished.
For work that must survive the calling turn, use the existing host `tmux` session
with `remain-on-exit` enabled on that pane. Retain its name in the current work unit;
recover output with `tmux capture-pane -p -S - -t SESSION` and inspect
`tmux display-message -p -t SESSION '#{pane_dead} #{pane_dead_status}'`.
Keep full stdout and stderr in the job's existing output artifact when scrollback
would truncate the failure. Resume the same operation from its observed result.
Terminal persistence preserves the job; it does not promise that the agent or
connector will automatically start another turn.

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

If an integration requires unfinished prerequisite work, complete it at its prerequisite owner before proceeding.
Follow the governing plan's section 19 and the retained issue dependencies; preserve the required behavior.
The archived core-closure and scaffold sequences are not additional execution prerequisites.
Respect the dependency directions in `specs/system.md` and keep shared-interface edits serialized.
A generic repair stays at its generic owner and includes the complete public consumer required by the governing plan.

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

Do not hand-roll algorithms that external engines already provide.
Leaf categories delegate computation to backend engines (such as GAP, Julia/Catlab, SageMath, SymPy, Singular, or Macaulay2).
`Cat` coordinates these engines through category structure.
Every mathematical algorithm must cite its external engine owner unless proven that no dependency supplies it.

### Replacing an engine or representation

Before replacing a shared operation, compare its full declared input domain with
the proposed engine's domain. Read the existing consumers of the displaced paths,
including nonfinite and symbolic cases. Use
[computational generality](specs/computational-generality.md) to distinguish carrier
size, presentation size, index size, chosen enumeration, and decidability.
An engine restriction belongs to that computation; it cannot silently narrow the
shared constructor, its annotations, its functor images, or inherited operations.

Trace the complete responsibility being replaced: input representation, identities,
composition, relations, any promised inverses or decision procedures, and public
reconstruction. A native reduction call inside a local path algorithm replaces only
reduction. A native apex calculation replaces neither the retained cone nor its
mediator. Keep the rest of the originally assigned responsibility open until its
replacement works through the same public consumer.

Remove a displaced implementation only after its required behavior has transferred
to the conforming owner. If the old implementation violates policy but supplies a
valid operation, preserve the operation's assertions and repair its ownership.
Neither keeping an obsolete fallback nor deleting the operation satisfies the
replacement. When a complete transfer is blocked, retain the explicit incomplete
claim under its existing owner; do not mark the unit accepted or change its domain.

When a new consumer fails on a constructed category, follow the same operation
through its defining functors and generic owner. Do not restrict acceptance to raw
engine categories merely because composites, slices, or functor images expose the
missing interoperation. A broader private adapter test cannot replace this path.

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
Use a small complete example of the stated domain. Substituting a finite domain,
identity action, strict coherence, or fixed finite stage makes a different claim.
The infinite and nonenumerable obligations are at their
[specification owner](specs/computational-generality.md#acceptance-across-domains).

## Review and acceptance

A complete implementation unit receives independent review at a fixed committed revision.
Use `r-gate` for the owned acceptance boundary. Archived R0–R6 and P1–P7 phase
procedures preserve historical evidence; they do not reinstate the superseded
execution order or require recreating those phases for the governing plan.
Supply the unchanged acceptance contract, owner sections, revision, and complete consumer boundary.
The reviewer reads that packet and relevant implementation. Expand it only for a concrete dependency.

1. Confirm the revision and the implementation unit's owned architecture rules.
2. Run `just architecture` under **Verification** before grading owned criteria.
3. Exercise every acceptance claim through the real public consumer at that revision.
4. Examine relevant leaf rules, ownership, functorial reuse, and mathematical legibility within the boundary.
5. Report each unmet claim with its owner, location, concrete failure, and required behavior.
6. Accept only when every required claim holds. Record the accepted revision with the unit's existing execution owner.

One public exercise can establish several related criteria. Reuse it and state those claims.
Tests establish only what they execute and assert.
A fixture that implements the generic operation under review cannot establish its availability to a leaf.
A source citation establishes a contract; execution establishes behavior.

After repair, review changed behavior and affected consumers. Reuse still-valid findings and prerequisite evidence.
Reopen a passed claim only for a changed dependency, new counterexample, or corrected controlling contract.
Name the affected claim and dependency before invalidating downstream acceptance.
A documentation location error alone does not invalidate executable behavior.
Record out-of-unit findings with their issue or mathematical owner. They do not block an unrelated unit.
Keep one current acceptance record and one unresolved-work section on each card.
Archive detailed reviews once; do not paste them into subsequent cards or prompts.
The governing plan's complete integration consumers determine closure; historical R6 status does not substitute for them.

### Checkpoints and progress over time

A committed adapter or targeted reproducer is a useful intermediate artifact.
Keep its claim at that boundary until the assigned public consumer and affected
preservation obligations hold. Do not turn a successful inner call into acceptance
of its operation family or advance a dependent unit on that premise. Independent
authorized work can continue while the incomplete prerequisite stays visible.

For a temporal assessment, reconstruct what the public consumer could do at the
start, what became possible, what stopped working, and what was subsequently
restored. Follow each correction across commits and handoffs as the same operation.
Restoring a regression restores lost capability; it does not establish another new
capability. Distinguish productive diagnosis that yields a new counterexample or
repairs the consumer from repeated changes leaving the same failure intact.

Use timestamps and observed active work to order that evidence. Commit counts,
changed-line totals, diagnostic totals, review counts, and the fraction of commits
devoted to administration are not measures of substantive progress. A missing
activity record does not establish idle time. Report gains and losses by capability
and dependency, without cancelling an unresolved required regression against an
unrelated gain or declaring all work unproductive because one claim remains open.

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
| An assertion of a true fact the language can express is about to be deleted, weakened, or made conditional because it fails | Keep the assertion. Record the defect with its owner and commit the test red under that issue. |
| Two consecutive implementation turns produce only plans, audits, or status records | Resume the required implementation, or state the exact decision preventing it. |
| A task grows through unrelated review findings | Keep the original unit fixed. Route findings to their owners. |
| A diagnostic total is measured again as the reason for an edit | State the mathematical claim and verify it on a concrete specimen. |
| A task is called difficult because it contains many similar items | Examine one operation and its dependencies; execute independent items as a batch. |
| A known command fails again without new evidence | Read the owned command and first failure. Change the hypothesis before another run. |
| A reviewer requests already-located provenance again | Open the retained locator. Search further only if it is incomplete or contradicted. |
| The same public operation loses an already repaired domain or law | Recover the earlier failing and passing consumer, locate the changed premise, and repair that boundary before claiming restoration. A new filename or engine does not reset the correction sequence. |
| A finite backend introduces enumeration into a shared constructor | Compare the declared domain with the adapter preconditions and exercise an affected nonfinite consumer before accepting the replacement. |

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
The suite states every fact the repository's language can express and the mathematics makes true, not the subset the current implementation satisfies.
Execution never edits an expectation. A contract-derived assertion that fails is a defect in the implementation, and that assertion is the regression test for it.
Deleting or weakening such an assertion leaves the suite asserting what the code already does, which is the one thing it cannot check, and it removes the facts nearest the implementation's edge, where its errors are.
Keep the assertion, record the defect with its owner, and commit the test red under that issue.
Read each assertion as a proposition: its inputs, quantifiers, expected result, and the wrong behavior it excludes.
Changing the specimen to an easier case changes what it proves, even if its test name stays the same.

Selecting which assertions execute is part of the proof boundary. A test file left
unchanged on disk supplies no evidence when a command cuts its source before the
nonfinite cases, filters them out, or invokes only an easier function. Targeted
selection is useful while diagnosing a case; label its result by that case. Before
accepting a shared replacement, exercise the affected consumer obligations that
selection omitted, through the declared verification route.

Inspect removed implementation branches alongside the assertions and invocations
that used them. Preserve their mathematical obligations even when the implementation
was nonconforming. Adapter-level exercises establish adapter behavior; the public
constructor, functor action, inherited operation, and reconstruction remain separate
obligations until the ordinary consumer reaches them.

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
Compare concrete failures, not just their number: removing one old failure while
introducing another does not preserve the baseline. A run that stops during import
does not test the later mathematical assertions. Keep that distinction in its claim.
Read the first concrete failure and the relevant output once. Re-run after a change or new diagnostic question.
Inspect the actual rule scope when a green check is used for acceptance; an empty or wrong scope proves nothing.
Prefer a decisive public exercise to another aggregate diagnostic total.

Commit and push hooks own test, lint, type-check, format, stub, and aggregate recipes. Do not run these suites manually.
A targeted Sage-aware exercise is the routine manual exception.
Execute a complete `.sage` consumer with the configured Sage file-loading path.
For related consumers in one Sage process, use Sage's `load()` with one complete
Sage globals dictionary per file, including the Sage numeric constructors; use
`load_attach_mode(load_debug=True)` to retain source-backed tracebacks.
Keep declaration-order and fresh-process claims in separate processes. Never strip
assertions, inject future-annotation semantics, or supply test classes through a
different locals dictionary to make a consumer executable. The runner must preserve
the file's Python and Sage semantics.

Measure native runtime startup separately from the public operation before changing
process reuse. Preserve Julia's resolved project and compiled cache between ordinary
runs. Batch compatible consumers at the same source revision; after a binding error,
collect its full native exception and exercise the failing binding before repeating
the complete public consumer. A passing native probe does not replace that consumer.
Check the configured Sage interpreter against the project's declared Python version
before loading a consumer. An older installed Sage is not an interchangeable runtime.
An R-gate also runs `just architecture` on its declared owned rule set.
D132 admits exact architectural invariant checks with file-and-line failures at the architecture push tier.
`scripts/rule_coverage.py` rejects a rule whose file glob matches nothing.
Retain static projection. Add no automated convention enforcement before 1.0.

`just plan-state` validates the governing plan and its retained native issue DAG.
Its successful result establishes execution-state consistency, not implementation
acceptance. Exact public consumers and prerequisite evidence remain required by
the governing plan. Preserve archived phase evidence without reactivating it.
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
