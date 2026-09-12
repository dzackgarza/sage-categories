# Mathematical execution DAG

This is the repository entry point to the approved [native-engine remediation plan][plan], especially its sections 19 and 20. The plan owns full mathematical obligations, engine allocations, acceptance, and retained issue dependencies.
This file names their work nodes and immediate dependency edges; it does not assert that an implementation is absent or that an earlier checkpoint must be repeated.
Start from delivered source and valid consumer evidence.
Preserve work already in flight.

Read [AGENTS.md](AGENTS.md), the named [contribution policies](CONTRIBUTING.md), and [COMPLAINTS.md](COMPLAINTS.md) before selecting affected work.
The [continuation locator](docs/remediation-handoff.md) supplies plan retrieval when the local vault link is unavailable.

## Nodes and prerequisites

`A` in `B`'s Needs column means `A -> B`: B consumes the stated output of A. `none` means no prerequisite node in this table; existing mathematical inputs and the plan's retained issue contracts still apply.
Acceptance belongs to the linked contract, not the short node name.
Multiple prerequisites are conjunctive.

| ID | Work and full obligation in the governing plan | Needs |
| --- | --- | --- |
| `runtime` | Section 19.1: runtime bindings, owned reconstruction, exact installation, earlier objects and selected maps | none |
| `sets` | Section 19.2: restore general Sets products, including rule-defined integers, represented reals and mixed inputs, while retaining finite native operations | `sets-mixed`, `sets-finite-native` |
| `functors` | Section 19.2: native categories, both functor actions, transformations, compositions, whiskerings and nonenumerated sources | none |
| `paths` | Section 19.2: complete typed presented paths and native finite universal-construction operation families | none |
| `universal` | Section 19.2: retained diagrams, chosen apex/legs/mediators, nonstandard indexing, opposites and predicate subobjects (#30/#24/#41; intrinsic #32) | `sets`, `functors`, `paths` |
| `indexed` | Section 19.2: full infinite/nonenumerable indexed constructions and sequential colimits with maps and their specified equality | `sets`, `functors` |
| `diagrams` | Section 19.3: symbolic, supplied monoidal and cell interpretation, including nonstrict comparisons and noninvertible ordinary arrows | `functors` |
| `refinement` | Section 19.4: same-object refinement (#31), with existing inherited operations | none |
| `inverses` | Section 19.4: retained inverses (#33) | none |
| `isofibrations` | Section 19.4: composite isofibrations and generic state transport (#35) | none |
| `named` | Section 19.4: named projections and composites (#39), consuming the required structure and transport | `refinement`, `inverses`, `isofibrations` |
| `additive` | Section 19.4: native additive owner (#40 and additive #32), exact Ab Homs, both selected presentations and forgetful maps | `named`, `paths` |
| `tensor` | Section 19.4: ordinary tensor (#42), induced maps, universal factors and comparisons | `additive` |
| `relative` | Section 19.4: relative tensor (#43), distinct outer rings, noncommutative middle ring, both actions and balanced factors | `tensor`, `inverses` |
| `actions` | Section 19.4: supplied actions and module transport (#44), retaining distinct acting and acted-on categories and generic structured objects | `relative`, `named`, `diagrams` |
| `kan` | Sections 14 and 19.4: Kan, weighted, profunctor and relation consumers with actual diagrams and universal maps | `universal`, `functors` |
| `orders` | Section 19.4: #41, #9/#10 order branch; selected squares, supplied inverse transport, indexed comparisons and undecided predicates | `universal`, `inverses` |
| `groups` | Section 19.5: group presentations (#21), relation arrows and universal factors | `named`, `paths` |
| `modules` | Section 19.5: module presentations and constructors (#22), scalar conventions, cokernel and supplied actions | `tensor` |
| `module-sums` | Section 19.5: arbitrary indexed module sums, finite support per element, injections and universal maps | `indexed`, `actions` |
| `algebras` | Section 19.5: #46 then #23; full algebra presentations and infinite underlying-module consumer R<x,y>, retaining genuine forgetful maps | `relative`, `module-sums` |
| `rings` | Section 19.5: rings/localization (#47), owned maps and native algebra integration | `named`, `additive` |
| `spaces-sheaves` | Section 19.5 and #48: spaces, topology/maps, sheaf values and restrictions on their proper domains | `rings` |
| `affine` | Sections 17 and 19.5: affine branch (#49), contravariant Spec, native pullbacks and induced maps | `spaces-sheaves` |
| `gluing` | Sections 17 and 19.5: gluing (#50), projective-line charts, structure sheaf and chart-swap action | `affine` |
| `topological-colimit` | Section 19.5: full CP^infty diagram, CW topology, inclusions and induced continuous maps | `indexed`, `spaces-sheaves` |
| `adeles` | Section 19.5: full restricted product, topology, ring operations, component maps and diagonal QQ map | `indexed`, `rings`, `spaces-sheaves` |
| `mypy-runtime` | Type checking actually executes and understands this project: mypy starts under the QC harness, and the category plugin is loaded by the effective config rather than merely installed. **Blocker owners:** `dzackgarza/ai-review-ci#409` and `#410`. **Reproducer:** `just test-commit`; the failing mypy stage currently stops before mypy starts with `sage-categories-homotopy was not found in the package registry` because `uvx --with` cannot resolve the workspace source, and the Sage mypy profile is not selected so the effective config does not load `sage-mypy-category-plugin`. **Acceptance:** both upstream repairs are present together, mypy actually starts, and the effective config loads the category plugin. Landing #409 alone is a regression, not progress: mypy would then check a dynamic category compiler against a model that does not hold | none |
| `stub-conformance` | `kernel/stub_generator.py` is reachable as a recipe, and the `.pyi` it emits satisfies this repository's own formatter and linter by construction. 379 of the current 457 ruff findings are in emitted stubs; they are fixed at the projector, never by editing a tracked stub (`POL-TYPE-025`, `POL-TYPE-026`) | none |
| `lint-debt` | The 78 hand-written `.py` ruff findings cleared at their owners — including `B019` cached decorators on methods, which is a retained-reference defect rather than style. Suppressions, per-file ignores and widened excludes do not discharge this | none |
| `gate` | Section 19.6: ordinary execution gate (#51) against the governing plan and retained issue/PR claims. Green on a clean tree, so that `[known red: ...]` ceases to be a valid commit subject here | `mypy-runtime`, `stub-conformance`, `lint-debt` |
| `python-runtime` | Section 19.6: declared Sage/Python runtime available to actual execution processes | none |
| `static` | Sections 18 and 19.6: exact static projection (#45), developed alongside the same runtime consumers. Its exactness cannot be claimed while the projector has no entry point and emits output the repository rejects | `stub-conformance` |
| `host-headroom` | Long Sage/Julia consumer runs on this host are nondiagnostic: the provisioned `/tmp/sage314` runtime is ~2.4 GiB, public-consumer runs have driven the root filesystem to ~55 MiB free and ~11 GiB of swap, and single consumers spend minutes in `folio_wait_bit_common` before reaching a test body or are terminated externally with no retained failure. Until a consumer run can be trusted to reach its assertions, every node whose acceptance is a long runtime check is unmeasurable. Make one such run reproducibly complete — by trimming its resident set, staging the consumers, or bounding what a single run loads — and record the shape that works. See COMPLAINTS.md, "Recovered Python-3.14 Sage runtime exhausts host headroom under public consumers" | none |
| `monodict-autofix` | Ruff's unsafe dict autofixes are invalid for Sage `MonoDict` and silently introduce retained-reference defects; a worker has already had to reverse them by hand once. Encode the exclusion at the linter config so the autofix cannot be applied again, rather than relying on each worker to notice. See COMPLAINTS.md, "Ruff unsafe dict autofixes are invalid for Sage MonoDict" | none |
| `sets-integers` | Section 19.2 decomposition: rule-defined integer objects inside general Sets products. **Acceptance:** `tests/sets/test_set_scaffold.sage::test_rule_defined_infinite_set` passes | `sets-core` |
| `sets-reals` | Section 19.2 decomposition: represented reals inside general Sets products. **Acceptance:** a test function named for represented reals exists in `tests/sets/` and passes. As of 2026-09-12 `test_set_scaffold.sage` defines only `test_finite_set_universal_maps`, `test_selected_set_functor_supplies_point_and_map_behavior` and `test_rule_defined_infinite_set`, so this node is not discharged by that file passing | `sets-core` |
| `sets-mixed` | Section 19.2 decomposition: mixed-input products combining enumerated, rule-defined and represented factors. **Acceptance:** a test function named for mixed-input products exists in `tests/sets/` and passes; see the note on `sets-reals` about what the current scaffold does and does not define | `sets-integers`, `sets-reals` |
| `sets-finite-native` | Section 19.2 decomposition: finite native operations retained unchanged across the restored general product. **Acceptance:** `tests/sets/test_set_scaffold.sage::test_finite_set_universal_maps` passes against the restored general product, not only the finite path | `sets-core` |
| `sets-core` | **Closed.** Section 19.2 decomposition: the general Sets product construction itself, before its factor kinds. **Acceptance:** `tests/sets/test_general_set_product.sage::test_general_set_product` passes under the declared runtime | none |
| `acceptance` | Section 20 in full, including displaced-code removal under 20.1 and native integration extensions under 20.2 | `host-headroom`, `monodict-autofix`, `runtime`, `sets`, `functors`, `paths`, `universal`, `indexed`, `diagrams`, `refinement`, `inverses`, `isofibrations`, `named`, `additive`, `tensor`, `relative`, `actions`, `kan`, `orders`, `groups`, `modules`, `module-sums`, `algebras`, `rings`, `spaces-sheaves`, `affine`, `gluing`, `topological-colimit`, `adeles`, `gate`, `python-runtime`, `static` |

## Use the graph at the consumer boundary

The plan's named next boundary is the general Sets product; reuse its accepted repair if already delivered.
Continue independent authorized mathematics while runtime or gate repairs proceed.
A runtime binding defect blocks acceptance of the affected consumer, not all source work.
Static projection accompanies each affected operation; the `static` node is not permission to defer its first types.

**`gate`, `static` and `python-runtime` come before more mathematics, and the reason is measured.** Over 2026-09-10 to 2026-09-11 this repository took 41 commits.
Twenty-five of them declare a known-red gate in their own subject line.
Twelve are `docs: record ...` write-ups into COMPLAINTS, which grew by 250 lines in that day; eight more are `fix(static)` or `fix(architecture)` repairs against the gate.
Eight are feature work.
The tree gained 3,628 lines and 71 methods, five new classes — roughly one node's worth of surface for a day of a worker's whole attention.

**Correction to the paragraph below, which was wrong for this repository.** It said to move the static projection to push tier. That reasoning was imported from `lean-categories`, where a commit gate cost twenty-four minutes and the work is transcription. Neither holds here. This gate is **cheap** — measured at 62 seconds end to end on 2026-09-11 — and this repository is code that other agents read and imitate, so an ill-typed or dynamically-shaped construction does not stay where it was written: the next worker copies the pattern, and the cost compounds instead of staying local. A cheap gate against a propagating failure belongs exactly where it is, on commit. Keep it there. The paragraph below is retained for the tier description of `architecture` and `plan-state`, which are correctly on push; disregard its instruction to relocate the static projection.

**The real defect is that the gate has been red long enough to stop being a gate.** `ruff check src tests` reports **457 errors**, and a check that always fails informs nobody: it cannot distinguish the commit in front of it from the hundred before, so every worker learns to read `[known red: ...]` as the normal ending of a commit subject rather than as a fault to repair. Twenty-five of forty-one commits in one day ended that way. That is not a papercut being tolerated; it is the repository's one defence against pattern propagation being switched off, in a repository whose whole risk is pattern propagation.

The inventory, so nobody has to re-derive it:

- **379 of the 457 are in `.pyi` files, and those are generated by this repository's own projector.** The rules are all stub shape — `I001` import order (118), `RUF022` `__all__` order (87), `PYI013` and `PIE790` stray `...` (132), `UP049` deprecated generic syntax (45). The generator is `src/sage_categories/kernel/stub_generator.py`, it wraps `mypy.stubgen`'s source projection and rewrites category-owned provider bases from the compiler's retained declaration relation, and it already encodes the right invariant: it "never reads a tracked `.pyi` file as input" (`POL-TYPE-025`, `POL-TYPE-026`). What it lacks is an **entry point** — no `justfile` recipe, no console script, nothing outside `tests/static/test_stub_generator_ast.py` that invokes it — so regeneration happens by hand-assembled invocation and its output has never been required to satisfy the repository's own lint. That is the whole mechanism behind the recurring `fix(static): regenerate ...` commits.

  **Correcting an earlier version of this entry**, which claimed no generator existed here. It does; the gap is an entry point and a conformance obligation on its output, not a missing tool. Nothing about the stubs is hand-authored, and nothing should be: a `.pyi` finding is a defect in the projector or in the source it projects, and it is fixed there. Hand-editing a tracked stub splits the source of truth and is erased by the next regeneration.
- **78 are in hand-written `.py`** and are straightforwardly owned: 28 `I001`, 15 `RUF022`, 10 `F401` unused imports, 6 `SIM401`, 6 `B019` (cached decorator on a method, a real leak risk), 5 `PERF102`, 2 `F841`, and a handful of others.
- **417 of the 457 are auto-fixable** by `ruff check --fix`.
- **All 99 tracked `.pyi` shadow a `.py` of the same module, and that needs a deliberate decision.** A stub adjacent to a module takes precedence for a type checker, which is correct and intended for the compiler-built categories — they have no static form to read, which is the whole reason the projection exists. But precedence applies to the *entire module*, so every ordinary, statically-analysable function body in those 99 files also stops being checked. That may be acceptable if those bodies are thin compiler plumbing and the mathematics lives in the projected surface; it is not acceptable if real logic is hiding behind a stub that describes it only approximately. Settle it by measuring rather than assuming: once mypy actually runs (item 0), check a shadowed module with and without its stub and see whether the body yields findings. Record the answer in `specs/`; if bodies do need checking, the projection needs to be scoped to the declarations that require it rather than emitted per module.

The work, in order:

0. **`mypy` is not running, and the gate misreports why.** On 2026-09-11 the commit tier printed `ERROR: mypy found type errors in project code.` The actual output above it is a dependency resolution failure — `Because sage-categories-homotopy was not found in the package registry and you require sage-categories-homotopy, we can conclude that your requirements are unsatisfiable` — so mypy never started and reported nothing. Every worker reading that line has been sent to hunt type errors that were never emitted. Fix the missing distribution or the requirement naming it, confirm mypy actually runs, and only then judge what it says. Until this is settled the type-checking half of the gate is not red, it is absent, and no conclusion about this repository's typing is supported by it. Filed upstream as `ai-review-ci#409`.

  **Do not fix that alone — it would leave mypy running blind, which is worse than not running.** `sage-mypy-category-plugin` is declared in this repository's dependencies and is installed into the checking environment on every run, but nothing loads it: a mypy plugin is activated by a `plugins =` line in the effective config, and the config the gate uses (`mypy-global.ini`) has none, while the one that does load it (`mypy-sage.ini`) is referenced by nothing and is never selected. This repository has no `[tool.mypy]` section of its own either. The plugin is what teaches mypy this project's category paradigm; without it, mypy checks a dynamic category compiler against a model that does not hold, and produces a large volume of confident findings that are simply about the wrong thing. Filed upstream as `ai-review-ci#410`. Both must land before any mypy output from this repository means anything — and if #409 lands first, treat the resulting findings as unverified until #410 does.

1. **Give the existing projector an entry point, and put a conformance obligation on its output.** `stub_generator.py` exists and its invariants are already correct; what is missing is a recipe that runs it and a rule that its emitted `.pyi` must satisfy the repository's own formatter and linter before it is committed. Make the generator's output green by construction — the projector is the place a stub finding gets fixed, because it is the only writer of those files.
2. **Clear the 78 hand-written findings.** These are owned code and several are real: an unused import is noise, but `B019` on a method is a retained-reference bug waiting to happen.
3. **Regenerate the stubs through the new recipe and commit the result green.**
4. **Then the commit gate is a gate again**, and `[known red: ...]` stops being a valid commit subject in this repository.

**Acceptance:** `just test-commit` passes on a clean tree; regenerating the static projection leaves the tree green with no hand-editing; and no commit subject carries `[known red: ...]` for ruff or mypy thereafter. A suppression, a per-file ignore, or a widened `pyproject` exclusion does not satisfy this — the point is that the code conforms, not that the checker stops asking.

**Why this is ahead of the mathematics.** A day of this repository's work produced 71 methods and 5 classes against 3,628 changed lines, with half its commits spent on the gate or on writing up why the gate could not pass. Paying the 457 down is bounded — most of one working session, the majority of it mechanical — and it converts every subsequent commit from an argument with a broken checker into a real check. The velocity problem here is not that the gate is slow; it is that it has been red so long that nobody treats it as information.

**Before repairing the gate, move it to the tier it belongs on.** The three tiers already exist here and one of them is already right: `architecture` and `plan-state` run on `test-push`, described in the justfile as "a hard stop before push", which is exactly where a hard stop belongs. `test-commit` is the problem — it delegates to the shared Sage QC commit tier, which runs the static and type projection over the project, and that is a quality gate standing where a sanity check should be. That is why twenty-five commit subjects in a day end in `[known red: ...]`: the gate is being asked a question it cannot answer yet, on every single commit, while the mathematics it is guarding has not been written.

What belongs on each tier here:

- **Commit** — does the module import, does it parse, does it satisfy the repository's own cheap invariants, is the node it claims real. The things a worker forgot, caught while the fix is seconds. Not mypy over the project, and not a static projection that depends on stubs which do not yet exist.
- **Push** — the static projection, the architecture invariants, the import contracts, the Sage suite. `test-push` already carries two of those; the static projection joins them.
- **Contribution** — the promise to anyone outside: coherent, installable, defensible. That one does not move.

Choose this in *this* repository's justfile, which is what selects the tier each check runs on. If the shared `ai-review-ci` Sage tier cannot express the split, that is a defect to file against that repository with the exact recipe and diagnostic — not something to route around with a local reimplementation of the checks.

The point is not a lighter standard. It is that the standard is currently applied where it can only be failed, so it produces a red subject line instead of a repair, and the worker spends its day answering the gate rather than writing the mathematics the gate exists to protect.

Those three nodes each carry `Needs: none` and all three are prerequisites of `acceptance`, so nothing downstream can be accepted while they are open.
That is the ordinary consequence of the graph; what makes them urgent rather than merely required is that every other node is currently being delivered *through* them, at the cost above.
A repository where the majority of commits announce a red gate is not deferring verification by policy — it is paying for verification it does not get.
Take them in this order:

1. **`gate`.** Make the commit-tier check either pass or say precisely which obligation is outstanding, so `[known red: ...]` stops being the normal ending of a commit subject.
   A gate that is red for everyone all the time reports nothing about the commit in front of it, and the next real regression lands inside that noise.

2. **`static`.** The `fix(static)` sequence of 2026-09-11 03:30–04:34 repaired seven distinct projection defects in one hour and still ended known-red.
   Settle what exact projection the node requires and close it, rather than continuing to chase it one consumer at a time.

3. **`python-runtime`, in part only.** The Julia side is repo work and is already specified in COMPLAINTS: Catlab 0.17.6 constrains Compose to `JSON <= 0.21` while OSCAR 1.8.2 requires `JSON >= 1.0`, so declaring OSCAR in `src/sage_categories/juliapkg.json` breaks every Catlab-backed consumer, and the recorded resolution is an explicit process/project boundary with an opaque handle rather than one shared Julia process.
   Do that.

**The host headroom half of `python-runtime` is not repo work — stop spending commits on it.** COMPLAINTS records the Sage 10.9 / Python 3.14.7 runtime being provisioned successfully and then failing under load: the root filesystem down to about 55 MiB free, roughly 11 GiB of swap in use, consumers sitting in `folio_wait_bit_common`, a stub regeneration alive for 2m15s without advancing a write.
That observation is complete and correct, and no further reproduction of it changes anything, because the repair is more memory and disk on the machine.
It is recorded, it is the owner's decision, and it is not a reason to keep re-running the consumers to watch them die.
Continue authorized source work that does not need the runtime, and leave that complaint closed to further evidence until the hardware answer arrives.

Edges apply to the required output, not blanket closure of a work family.
In particular, additive #32 does not require the independent opposite-diagram #24 consumer; group presentations need #32's intrinsic coequalizer, not additive completion.
The topology and adelic extensions do not block projective-line gluing.
Ordinary finite module/tensor consumers do not await all infinite-rank extensions.
Read the retained issue prerequisites before selecting a subtask.

When a node's independently deliverable output needs its own scheduling, name that output at the existing task and redirect the affected edges without losing any obligation.
Preserve the plan's full hypotheses and section-20 consumers.
Do not infer readiness from a phase label or a package installation.
Record new observed issues in COMPLAINTS and link the affected node; logging is not repair.

Before committing graph changes, check unique IDs, resolved prerequisite IDs, absence of cycles, and a path from each required node to `acceptance`. Keep completion evidence in the existing plan/issue records and implementation commits, not a second checkbox ledger in this routing table.

[plan]: .agents/plans/features/FEATURE-functor-owned-category-framework/plans/PLAN-native-engine-remediation/PLAN-native-engine-remediation.md
