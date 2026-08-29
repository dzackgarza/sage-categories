# M0 implementation report

## Status

`DONE_WITH_CONCERNS`

Revision reviewed: `305fa430db5e10a9ee8fcf4d92612bf174d6906a`.
Required base: `de0730fbb0c279b23d93eaf0e14c57b6094de76a`.

M0 implementation is committed. R0 does not pass at this revision. Keep M0 open, and do not start M1.

## Governing authority

The review used these sources together:

- `specs/decisions.md`: D123 and its supersession statement; D03; D109 through D114; D121 and D122.
- `CONTRIBUTING.md`: `POL-DOC-010` through `POL-DOC-023`; `POL-LEAF-058`; `POL-LEAF-061`; `POL-FUN-035`; `POL-SCOPE-013`; `POL-SCOPE-016`; `POL-ENGINE-001` through `POL-ENGINE-015`; `POL-KERNEL-017`; and `POL-KERNEL-028` through `POL-KERNEL-036`.
- `specs/functor.md`: “Functors as morphisms of `Cat`” and “Functor actions are concrete constructors.”
- `specs/resolution.md`: “Fixed private dependencies,” “Inputs,” “Direct inherited execution,” “Declarations and signatures,” and “Acceptance conditions.”
- `specs/leaves.md`: the leaf declaration and computation-engine boundary contracts.
- `specs/property-refinement.md`: property containment, inverse images, same-object refinement, and compiled public surface.
- `specs/undecidable-properties.md`: propositions, typed queries, evaluation, assumptions, exact handlers, and public paths.
- `AGENTS.md`: authority, current scope, work discipline, and verification.
- Vault plan `PLAN-pr-8-kernel-cat-architecture-convergence` and phase `PHASE-pr-8-kernel-cat-m0-authority-normalization`.
- `m0-brief.md`: M0 scope and R0 acceptance.

## Commits

1. `b76e1f58c036207cf1bd1c8ddf9d02c4960374ed` — `chore: checkpoint M0 authority normalization`
   - Empty checkpoint over the required base. Its tree equals the base tree.
2. `77e8286997ae1434a3e0bdbc5a37217d613473d7` — `docs: consolidate architecture authority`
   - Reduced `README.md` and `AGENTS.md` to their local responsibilities and canonical-owner links.
   - Reduced the three templates to examples of the canonical contracts.
3. `f4fe2386b2f0c0491343717752a5448a77463120` — `docs: fix private dependency ownership`
   - Recorded the fixed private dependency assignments in `specs/resolution.md`.
   - Updated the applicable dependency and kernel policy rows.
4. `e87ff37cf18e629ed48c22853a52cba9d44d8454` — `build: install fixed dependency groups`
   - Added the fixed project, development, migration, and platform package groups.
   - Removed excluded dependency provisioning from the task runner.
5. `305fa430db5e10a9ee8fcf4d92612bf174d6906a` — `refactor: use typed query vocabulary`
   - Replaced valued-predicate names with query names on the edited public and kernel surfaces.
   - Used Sage `uncamelcase` for generated property-method spelling.
   - Reduced edited source docstrings to local behavior.

## Changed files

| File | M0 result | Governing anchors |
| --- | --- | --- |
| `AGENTS.md` | Reduced to authority, current scope, work discipline, and verification. | `POL-DOC-013`, `POL-DOC-021`, `POL-DOC-023`; `m0-brief.md` M0.2. |
| `CONTRIBUTING.md` | Updated fixed dependency and declaration-tool policy rows. | `POL-ENGINE-015`, `POL-KERNEL-033`, `POL-KERNEL-036`; `specs/resolution.md`. |
| `README.md` | Reduced to purpose, public import, and canonical documentation map. | `POL-DOC-023`; `m0-brief.md` M0.2. |
| `justfile` | Removed excluded parser provisioning and installed the declared development group. | `POL-ENGINE-015`, `POL-KERNEL-036`; `specs/resolution.md` “Fixed private dependencies.” |
| `pyproject.toml` | Recorded the fixed Python packages and platform groups. | `POL-ENGINE-001` through `POL-ENGINE-015`; `specs/resolution.md` “Fixed private dependencies.” |
| `specs/finite-set-minimal-template.py` | Kept the one required `FiniteSets` property specimen and linked its owners. | `POL-LEAF-058`, `POL-LEAF-061`; `specs/property-refinement.md`; `specs/undecidable-properties.md`. |
| `specs/leaf-category-template.md` | Reduced to a leaf specimen whose complete functor actions use target constructors. | D123; `POL-FUN-035`; `POL-LEAF-058`; `POL-LEAF-061`; `specs/functor.md`. |
| `specs/poset-minimal-template.py` | Reduced module prose to local specimen behavior and owner links. | D123; `POL-LEAF-058`; `POL-LEAF-061`; `specs/functor.md`; `specs/leaves.md`. |
| `specs/resolution.md` | Added the fixed private dependency table and current declaration-tool assignments. | D109 through D114; D123; `POL-ENGINE-001` through `POL-ENGINE-015`; `POL-KERNEL-017`; `POL-KERNEL-028` through `POL-KERNEL-036`. |
| `src/sage_categories/cat/category.py` | Changed the value-valued public application to `Query` and `AppliedQuery`. | `specs/undecidable-properties.md` “Typed queries”; D123; `POL-DOC-023`. |
| `src/sage_categories/cat/category.pyi` | Matched the typed-query public names. | `specs/undecidable-properties.md` “Public paths”; `POL-KERNEL-036`. |
| `src/sage_categories/kernel/predicates.py` | Renamed query classes and used Sage `uncamelcase`. | `specs/undecidable-properties.md`; `specs/resolution.md` “Properties and constructions”; `POL-KERNEL-033`. |
| `src/sage_categories/sets/cardinals.py` | Replaced local valued-predicate wording with proposition wording. | `specs/undecidable-properties.md` “Propositions.” |
| `src/sage_categories/sets/objects.py` | Reduced the module docstring to local set-object behavior. | `POL-DOC-023`; `m0-brief.md` R0.6. |
| `src/sage_categories/sets/subobjects.py` | Reduced the module docstring to local chosen-subobject behavior. | `POL-DOC-023`; `m0-brief.md` R0.6. |

The complete base-to-HEAD diff contains these 15 files and no other tracked path.

## Verification routes

### Documentation-only commits

Commits `77e8286` and `f4fe238` used the repository-required documentation route: inspect the edited documents and commit with `--no-verify`. No test, build, lint, type, format, stub, or aggregate check ran for these commits.

### Non-document commits

- Dependency metadata was edited through parsed TOML operations. No lock file was hand-edited.
- The ordinary commit hook for `e87ff37` reached existing stub generation and stopped at:

  ```text
  AssertionError: FiniteSets writes no ObjectType or ElementType or MorphismType declaration.
  ```

  This is an existing architectural condition outside the dependency metadata change. The commit was recorded with `--no-verify`.
- The edited Python files passed direct bytecode compilation before commit.
- A host import check could not run because the host interpreter has no Sage installation:

  ```text
  ModuleNotFoundError: No module named 'sage'
  ```

- Repository policy forbids manual repository suites, linters, type checks, formatters, stub generation, and aggregate checks during this pre-1.0 architectural phase.
- Closure review checked the complete `de0730f..305fa43` diff and `git diff --check`. The latter returned no output.
- A residual search found no `ValuedPredicate` or `AppliedValuedPredicate` class or reference in current `src/` and `specs/` Python, stub, or Markdown files.

One-line evidence: the complete 15-file diff has no whitespace error, edited Python compiles, and broader import or hook verification remains unavailable at this incomplete architecture.

## R0 disposition

| R0 criterion | Disposition | Evidence |
| --- | --- | --- |
| 1. D123 controls every current functor clause. | **Unresolved** | D123 is controlling in `specs/decisions.md`. The edited canonical functor contract and templates agree with it. Current kernel code still exposes `retain_object_constructor_conversion`, `retain_morphism_constructor_conversion`, `retain_constructor_data`, `object_constructor_input`, `element_constructor_input`, `morphism_constructor_input`, and `_derive_selected_constructor_conversions` in `src/sage_categories/cat/category.py`. These names and paths still encode a second target-construction account. Complete line-by-line coverage of every current functor clause was not established. |
| 2. Each contract has one canonical document. | **Unmet** | `README.md`, `AGENTS.md`, and the edited templates now link to canonical owners. `CONTRIBUTING.md` still contains full architectural contracts rather than compact review rules only. It therefore duplicates the canonical specifications. |
| 3. Public names match M0.3. | **Unmet** | Typed-query names now match. Current public specifications and source still use `1 -> X` for points. Examples include `specs/functor.md:1115`, `specs/sets.md:21`, `specs/sets.md:25`, `specs/sets.md:75`, `src/sage_categories/cat/slices.py:4`, and several set, integer, and poset docstrings. M0.3 requires `* -> X`. |
| 4. Active plans state only phase delta and acceptance. | **Unmet** | The phase cards are compact. The active parent plan still contains complete architecture and dependency contracts, implementation mechanisms, examples, and phase details beyond delta and acceptance. |
| 5. Templates contain no independent contract. | **Satisfied** | The three edited templates identify their canonical owners and present examples. The required `FiniteSets` specimen remains. |
| 6. Source docstrings describe only local symbols. | **Unmet** | The edited module docstrings are local. Current source still contains architecture-wide explanations. Examples occur in `src/sage_categories/sets/objects.py`, `src/sage_categories/sets/elements.py`, `src/sage_categories/sets/exponentials.py`, `src/sage_categories/sets/category.py`, `src/sage_categories/posets/category.py`, and `src/sage_categories/number_sets/integers.py`. |
| 7. Every kernel/Cat dependency has the fixed disposition. | **Unmet** | `specs/resolution.md`, applicable policies, package groups, and `justfile` record the fixed assignments. Unsuperseded D114 in `specs/decisions.md` still assigns `tree-sitter-sage` and `makefun`, while M0 excludes both. These requirements cannot hold together. |
| 8. The active DAG contains no production-leaf implementation. | **Satisfied** | The inspected M0 through M6 phase cards keep production leaves blocked through R6 and explicit owner approval. M1 through M6 remain unstarted. |

## Negative-finding evidence boundaries

### Criterion 1

- **Searched:** the complete `de0730f..305fa43` diff; D123; canonical functor and runtime specifications; focused current-source searches for retained constructor conversions and constructor-input paths.
- **Found:** edited contracts follow D123, but current kernel paths still describe separate construction conversion and input machinery.
- **Conclusion:** based on these sources, R0.1 lacks the required whole-repository proof and has concrete conflicting implementation vocabulary.
- **Confidence:** High.
- **Gaps:** every current functor clause outside the complete diff was not read line by line.

### Criterion 2

- **Searched:** the complete changed documents and current `CONTRIBUTING.md` policy surface against the canonical-owner map.
- **Found:** `CONTRIBUTING.md` retains detailed architecture clauses that restate canonical specifications.
- **Conclusion:** R0.2 is unmet.
- **Confidence:** High.
- **Gaps:** none that could make the retained duplicate contracts compact review rules.

### Criterion 3

- **Searched:** current `specs/` and `src/` Markdown, Python, and stub files for point spellings; current query vocabulary for the retired valued-predicate names.
- **Found:** query names are normalized; many current point clauses still use `1 -> X`.
- **Conclusion:** R0.3 is unmet.
- **Confidence:** High.
- **Gaps:** no claim is made about file types outside the searched Markdown, Python, and stub surfaces.

### Criterion 4

- **Searched:** the complete active parent plan and the M0 through M6 phase cards.
- **Found:** phase cards are compact; the parent plan carries complete cross-phase contracts and implementation detail.
- **Conclusion:** R0.4 is unmet.
- **Confidence:** High.
- **Gaps:** none within the active plan and phase cards supplied by the vault.

### Criterion 6

- **Searched:** the complete changed source files and focused current-source searches for architecture-wide point and category explanations.
- **Found:** unedited source modules retain cross-owner contract prose.
- **Conclusion:** R0.6 is unmet.
- **Confidence:** High.
- **Gaps:** this is not a complete classification of every source docstring; the concrete surviving examples already defeat the criterion.

### Criterion 7

- **Searched:** D109 through D114, `specs/resolution.md`, applicable policy rows, `pyproject.toml`, and `justfile`.
- **Found:** D114 names two dependencies that the fixed M0 boundary excludes.
- **Conclusion:** R0.7 is unmet at this revision.
- **Confidence:** High.
- **Gaps:** no later supersession statement for D114 was found in the inspected controlling decision source.

## Required closure

Resolve R0.1, R0.2, R0.3, R0.4, R0.6, and R0.7 at one revision. Then perform the required independent R0 review. M1 remains blocked until that review accepts the exact revision.

## R0 fix round 1

Status: `DONE_WITH_CONCERNS`.

Revision repaired: `e3bb1b3421b1f971fb1fac8871aaf6264ba15cf6`.

### Commits

- `e3bb1b3421b1f971fb1fac8871aaf6264ba15cf6` - bounded M0 authority repair in current worktree.

### Files

- `CONTRIBUTING.md`
- `specs/decisions.md`
- `specs/functor.md`
- `specs/resolution.md`
- `specs/sets.md`
- `src/sage_categories/cat/category.py`
- `src/sage_categories/cat/kan.py`
- `src/sage_categories/cat/slices.py`
- `src/sage_categories/number_sets/integers.py`
- `src/sage_categories/posets/category.py`
- `src/sage_categories/sets/category.py`
- `src/sage_categories/sets/elements.py`
- `src/sage_categories/sets/exponentials.py`
- `src/sage_categories/sets/objects.py`
- `src/sage_categories/sets/power_objects.py`
- primary plan-workspace copy `authoritative-plan.md`

### Provenance

- `m0-r0-repair.md` R0.1 controls this repair: normalize normative and source prose, and do not remove or implement the M1 runtime path.
- D63 and D109 through D114 remain the governing decision sources for point language, dependency language, and the private runtime boundary.
- `research-cap.md` supplies the checked CAP facts used here: MonoidalCategories is a required transitive dependency; SliceCategories is the checked slice source; FpCategories does not by itself supply generic `Fun([1], C)` or evaluation functors; CompilerForCAP is a CAP_project component; and no checked source supplies a generic Python--GAP--Julia bridge.
- The parsed Codex transcript cited by D109 through D114 supplied no user-grounded supersession for D114-based exclusions of `inflection`, `multimethod`, `tree-sitter-sage`, or `makefun`.

### Verification

- Before the edit, `git rev-parse HEAD` matched the authorized base `21cf52e49662e8e20ee3bcb84f68ce7366ad4d50`.
- The immediate repair diff was inspected before commit.
- A focused residual search on the repaired M0 surfaces left only genuine terminal-object formulas such as `Mor(Sets())(1, X)` and `Fun([1], C)`.
- `uvx --python 3.14 --from git+https://github.com/dzackgarza/agent-memory agent-memory plan update PLAN-pr-8-kernel-cat-architecture-convergence --body-file /home/dzack/gitclones/sage-categories/.superpowers/sdd/PLAN-pr-8-kernel-cat-architecture-convergence-v3/authoritative-plan.md` succeeded, and `plan show PLAN-pr-8-kernel-cat-architecture-convergence` returned the compact body.
- No test, build, lint, type, format, stub, or aggregate command ran. This was the documentation-only route.

### R0.1 ruling

The repaired prose now treats `F.on_object` and `F.on_morphism` as the complete leaf functor contract on the inspected M0 surfaces.
The retained constructor-conversion path remains private compiler vocabulary.
This round did not remove it and did not implement it.

### R0 criteria after round 1

| R0 criterion | Round 1 disposition | Evidence |
| --- | --- | --- |
| 1. D123 controls every current functor clause. | **Satisfied for the bounded M0 prose boundary.** | The repaired specifications, policy rows, and source docstrings treat the two ordinary actions as the complete public contract. The retained constructor-conversion path remains private compiler machinery under the R0.1 ruling. |
| 2. Each contract has one canonical document. | **Satisfied on the inspected authority surfaces.** | `CONTRIBUTING.md` now points to canonical owners instead of restating the full leaf, kernel, and functor contracts. |
| 3. Public names match M0.3. | **Satisfied on the repaired M0 surfaces.** | Current M0-governed specs and source now use point notation `* -> X`. Genuine terminal-object formulas remain where they are the mathematical object, such as `Mor(Sets())(1, X)` and `Fun([1], C)`. |
| 4. Active plans state only phase delta and acceptance. | **Satisfied.** | The active parent plan body now stores authority, scope, phase delta, acceptance, and the explicit D114 authority gap only. |
| 5. Templates contain no independent contract. | **Unchanged and still satisfied.** | This round needed no template edit. The prior M0 repair already reduced the active templates to examples. |
| 6. Source docstrings describe only their local symbols. | **Satisfied on the repaired M0 source surfaces.** | The cited slice, set, integer, and poset files now describe only their local objects, maps, points, and retained data. No broader whole-repository claim is made here. |
| 7. Every kernel/Cat dependency has the fixed disposition above. | **Improved, with one remaining authority gap.** | `specs/resolution.md` now records MonoidalCategories, SliceCategories, CompilerForCAP as a CAP_project component, the limits of CAP and FpCategories, and the separate Python--GAP--Julia bridge requirement. No user-grounded supersession was found for any D114-based exclusion list, so this round removes the unsupported fixed exclusions from the active plan instead of inventing a new decision. |
| 8. The active DAG contains no production-leaf implementation. | **Satisfied.** | The compact active plan keeps the work at M0 through M6 and keeps production leaves blocked. |

### Remaining concerns

- The inspected transcript did not ground a superseding decision for any D114-based exclusion list. A later authority edit needs that user grounding.
- This was a bounded M0 repair on the inspected authority and source surfaces. It is not a new whole-repository R0 certification.
