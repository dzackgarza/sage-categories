# Complaints

Friction, papercuts, and kernel/Cat design deficiencies observed while working, recorded against the philosophy that leaf authoring should be thin and mostly mathematical.
Excludes defects fixed within the same workstream.

## Recording new issues

Apply [POL-WORK-002](CONTRIBUTING.md#work-selection-and-issue-capture) during source reading, implementation, mathematical review and ordinary use.
Capture an unresolved observation before leaving the affected work, even when it is small or independent of the current assignment.
An immediate verified fix can record its evidence in the fixing commit instead.

Add a descriptive heading, or extend the existing entry for the same cause:

- **Mathematical need or user action:** exact input/output objects, maps, hypotheses and laws, or the workflow gesture and expected result.

- **Evidence:** source passage, declaration/path and revision, or the actual action and output.
  Distinguish source inspection from an executed failure.

- **Gap and impact:** existing partial capability, the unmet condition, affected consumers, and the earliest mathematical or operational owner.

- **Uncertainty:** inspected scope, confidence, and unresolved questions.
  For absence claims give Searched, Found, Conclusion, Confidence and Gaps.

- **Repair link and acceptance:** the [TODO node](TODO.md), governing-plan obligation or upstream issue, and the result needed to resolve the complaint.

A failed name search is not proof of missing mathematics.
Label an unresolved availability question as such.
Record a mathematical need before proposing an engine or implementation; a package name does not establish its required domain.
Read historical observations at their stated revisions before relying on them.

## Local transcript lookup can fail after daemon restart

- **Mathematical need or user action:** Resume an interrupted repository work unit by searching the local ChatGPT recordings for the predecessor's last accepted/failing consumer and implementation notes.

- **Evidence:** On 2026-09-09, `Chat On Steroids Core2` session search for `9fb5271 refinement_descendant sage-categories` returned HTTP 502 after the daemon had been restarted earlier that day.
  Repository source, Git state, and the uncommitted regression test remained available.

- **Gap and impact:** The local recording search is not reliable enough to be the sole continuation mechanism after a daemon restart.
  A resumed worker can still reconstruct work from Git and files, but loses the predecessor's diagnostic narrative and must re-establish the last runtime observation.

- **Uncertainty:** One search request was attempted in this resumed unit; the repository connector itself remained healthy.
  It is not yet established whether all session-search requests fail or only this recording/index path.

- **Repair link and acceptance:** Operational tooling owner.
  Resolve when session search reliably returns predecessor recordings across daemon restarts, or returns a specific durable recovery path instead of a generic 502.

## Independent reviewer dispatch cannot identify the current conversation

- **User action and evidence:** On 2026-09-10, spawning the required read-only `r-gate` reviewer through `Chat_On_Steroids_Core2.agents` returned `UNIDENTIFIED_CALLER`: the app could not establish the current conversation as the prime agent.
  It explicitly reported that no workers were created, although repository reads and command execution were working.

- **Impact and owner:** The repository's fixed-revision independent-review requirement remains unsatisfied by that call.
  No second writer or worktree was created.
  The installed local reviewer CLIs provide a separate execution path to test; their existence alone is not a completed review.

- **Local dispatch evidence:** The read-only Codex attempt exited at the account usage limit before reading source.
  The configured `r-gate` Fable invocation likewise returned HTTP 429 before any model tokens or source reads.
  A subsequent Sonnet invocation of the same review role, restricted to `Read`, `Grep`, and `Glob` with no MCP servers or command/edit tools, began reading the fixed-revision diff and sources.
  The result of that review, rather than the existence of its process, determines acceptance.
  No credits were purchased, and no permissions were broadened.

- **Related friction:** Several `write_stdin` calls on existing benign sessions were blocked with “couldn't determine the safety status of the request.”
  Retained process IDs and output files allowed the actual job result to be read without treating the blocked poll as a live job or restarting successful mathematical work. The same indeterminate safety response also affected benign command-result reads during this continuation; completed sessions remained recoverable through their original terminal results. On 2026-09-11 two further benign status/result reads for the retained static-stub generator were blocked by the same indeterminate safety response; later ordinary terminal reads succeeded, and the blocked calls were not treated as process evidence. A new bounded read-only delegation attempt again returned `UNIDENTIFIED_CALLER` and created no workers.

- **Acceptance:** The delegation owner must reliably identify this conversation or provide a working read-only reviewer route that returns a result at the exact committed revision.

## Documented repository CLI entry points are not directly on PATH

- **Mathematical need or user action:** Resume a repository work unit using the documented `agent-memory plan show PLAN-native-engine-remediation` and `card dag` entry points from `AGENTS.md`.

- **Evidence:** On 2026-09-09 in this checkout, direct invocations of both `agent-memory` and `card` returned `command not found`. The governing plan remained retrievable through the documented `uvx --python 3.14 --from git+https://github.com/dzackgarza/agent-memory agent-memory` fallback; no corresponding fallback for `card` is stated in `AGENTS.md`.

- **2026-09-10 continuation:** The fallback's current revision (`220242f`) required a Rust build, initially with multiple concurrent compiler jobs on a heavily swapped host.
  Restarting that build with `CARGO_BUILD_JOBS=1` completed it.
  Build output was buffered, so compiler processes and newly written native artifacts distinguished progress from a dead session.
  A non-login Bash invocation then lacked both the shell's `uvx` entry point and `$HOME/.local/bin` for the already-installed `zk`; the login-shell fallback successfully retrieved the plan.
  The working DAG command is the same fallback followed by `agent-memory card dag`. The connector's file reader cannot follow `.agents` outside its approved root; the authorized CLI remains the working vault access route.

- **Dependency-workspace constraint:** The connector rejected `/home/dzack/gitclones/sage-stubs` as a working directory outside its approved roots. An initial clone and setup had completed there, but no source was edited; further access was not attempted after the rejection. The source repair instead uses a fresh public-source clone at `.tmp/dependency-sage-stubs` inside this approved repository root. That independent clone is not a worktree of this repository and remains necessary while its staged repair is uncommitted. A shell-only lookup also failed because `path` is a special zsh variable tied to `PATH`; changing the loop variable to `source_file` restored the same lookup. This was a command error, not evidence that `gh` or `base64` was unavailable.

- **Gap and impact:** The documented first-line continuation commands are not self-contained on this host.
  Plan retrieval degrades to the fallback path, while current DAG-card routing cannot be queried through the named command without separately discovering its installation route.

- **Uncertainty:** This observation is limited to the current shell environment and checkout; it does not establish that the tools are absent from every configured development environment.

- **Repair link and acceptance:** Operational tooling/documentation owner.
  Resolve when the documented direct commands are available in the supported shell or the documentation names a working repository-local/fallback invocation for each.

## Commit QC loses repository runtime and workspace dependency bindings

- **Mathematical need or user action:** Run the repository commit gate on a kernel refinement change in the tracked Sage/Python 3.14 environment with all workspace dependencies resolved exactly as declared by `pyproject.toml`.

- **Dependency-source repair and remaining failure (2026-09-10):** The locked Sage-stubs revision `1d87ee246c5dc95a29617ac64eaa46b9f3df5d48` has the same integer-matrix parser defect as current upstream `d0aa14f52c60431c587bf49ae9a78fe62ba3d940`; selecting the lock's revision would not repair it. A full syntax diagnostic found malformed ellipses in five files: `matrix_integer_dense.pyi`, `matrix_rational_dense.pyi`, `matrix_cyclo_dense.pyi`, `rings/asymptotic/term_monoid.pyi`, and `rings/asymptotic/asymptotics_multivariate_generating_functions.pyi`. The exact token corrections are staged in the independent dependency checkout `.tmp/dependency-sage-stubs`, branch `fix/integer-matrix-stub-syntax`, with its original hooks active after `just setup`. All 2,975 dependency stubs parse after the corrections; no parameter or result annotation was changed. The source and affected definitions were read at the dependency's pinned Sage revision `68d7e0e4d056f82449c8daeca7e7c21b0691c8c7`.

- **Dependency hook is still red:** Its first run could not find the PEP 561 stub package in the Sage interpreter. Installing the package from the retained source checkout into `/tmp/sage314` corrected that setup failure. The unchanged strict type check then reported 88 errors in the five files, including incompatible overrides and class-local names shadowing types. A concrete incompatible contract is `sage-stubs/structure/element.pyi:131`, which declares `Matrix[_Scalar].inverse() -> Matrix[_Scalar]`, versus the rational result of the integer-matrix implementation. That ancestor declaration is not present in the pinned Sage source: `structure/element.pyx:3607` defines `Matrix`, with its directly defined Python-visible methods `__mul__` at 3615 and `__truediv__` at 3947, not `inverse`. The complete native Sage diagnostic `/tmp/sage-categories-inverse-scalar-domain.sage` passes: the inverse of the integer matrix `[2]` has base ring `QQ`, entry `1/2`, and the required inverse equation. Repair must put the declaration at its actual owner and retain the coefficient-changing result; weakening that rational result to satisfy the fabricated ancestor would be incorrect. The same hook also reports eight lint failures; one requests deletion of a source-defined `__repr__` declaration, contrary to the dependency's declaration-preservation requirement. Neither the dependency hooks nor this project's checker settings were bypassed or relaxed.

- **Source-parity rule repaired:** Dependency commit `28c8fe8` excludes only Ruff `PYI029`, retaining directly source-defined representation methods and every strict type-check setting. The normal dependency hook passed. The earlier `__repr__` rejection and source at `asymptotics_multivariate_generating_functions.py:3273–3290` remain its provenance; this rule conflict no longer blocks the repair.

- **Committed source repairs and remaining owner:** In the independent dependency checkout, `636f8c8` removes fabricated element-base matrix methods and parent overrides at their actual source owners, preserving concrete inverse results and reflected arithmetic. Its exact-type consumer and native parent/scalar-domain checks pass. `ec81c00` repairs the asymptotic fraction stub, retains its representation method, and types the actual substitution shapes, ordered substitutions, identity substitution, and coefficient-changing element results. Its strict type consumer and full native symbolic/polynomial/zero-element consumer pass. Both commits passed the normal dependency hook. Dependency commit `0df25c16b8b3fc43d345fd9ef68d09e563e316c0` now also repairs term-monoid classcall and factory typing: static constructor binding, inherited copy identity, callable reconstruction, pickle reduction shapes, and correlated factory argument defaults/keywords, keys, extras and products. The seven affected source/type-consumer files pass strict mypy; the complete native unique-representation, term-factory and fraction consumers pass (`/tmp/sage-stubs-factory-final-types.log`, `/tmp/sage-stubs-factory-final-native.log`). The source commit passed the normal dependency hook; its documentation-only amendment is recorded in `/tmp/sage-stubs-factory-bank-complete.log`. The remaining matrix-only strict check reports 55 errors in the integer, rational and cyclotomic dense stubs (`/tmp/sage-stubs-matrix-only-0df25c1.log`). Those three source repairs and their phase-05 ownership remain staged. The parent repository dependency declaration and lockfile are unchanged, and its ordinary gate is not restored.

- **Retained commit and connector friction (2026-09-10):** A selective commit attempt encountered an active index lock owned by the retained normal-hook commit process (PID 34801, with live mypy child 35302). The lock was not removed. The retained commit completed as `ea51c3f`; its validated source and tests were retained, and its phase/validation record was amended to `0df25c1`. A later read-only grouped inspection was blocked with an undetermined safety-status tool error; the connector file reader remained available. Neither event was treated as a mathematical test result.

- **Installed-package lookup friction:** A targeted check of the fraction stub continued reporting the old `RingElement.parent` after its source repair. Inspection outside the checkout showed that Sage Python was reading the earlier wheel under `site-packages/sage-stubs`, not a live editable stub tree. A normal `uv pip install --python /tmp/sage314/bin/python --reinstall --no-deps .` from the retained dependency source refreshed that installation. Installed tool-cache files were not patched, and import diagnostics were not suppressed.

- **Dependency hook tool path:** The resumed normal commit of the unique-representation source-owner correction reached and passed strict mypy, the source checks, and the protected-configuration check, but failed at `ruff: command not found`. Ruff already exists at `/tmp/sage314/bin/ruff`; `SAGE_BIN` selects the mypy interpreter but does not expose its sibling lint executable to the hook. Setting `PATH=/tmp/sage314/bin:$PATH` together with `SAGE_BIN=/tmp/sage314-qc/sage` resolved the launcher failure. The constructor/factory and subsequent matrix-owner commits passed the normal dependency hook, without changing its rules.

- **Generic matrix owner correction:** Dependency commit `dcb94d4ca8f2b267184361c367bfc3d4a2843629` repairs the next exposed ancestor contracts. At pinned Sage source `68d7e0e`, `matrix2.pyx:2260-2272` defines `det` as a forwarding method, not an alias, and the generic `determinant` accepts no arbitrary keyword options; `rank` is inherited from `matrix0.pyx:5043`; `matrix2.pyx:5717-5814` allows scalar extension for row spans but no `base_ring` argument for column spans. The corrected stub and exact-type consumer pass strict mypy, including the concrete determinant's forwarded `proof` option. The normal hook passes. Its complete native consumer verifies determinant result parents, integer versus rational row spans, column spans, and rejection of phantom generic arguments (`/tmp/sage-stubs-matrix2-owner-types.log`, `/tmp/sage-stubs-matrix-owner-native.log`). The subsequent four-file strict check, explicitly including the corrected base and all three retained dense drafts, reports 48 errors in those three drafts (`/tmp/sage-stubs-matrix-after-dcb94d4.log`); 55 was the preceding revision's count. Phase-05 ownership is now committed, with T05.1 reopened for the still-exposed shared matrix contracts. The three dense source files remain staged and unaccepted, and the parent project's gate is not restored.

- **Polynomial and inverse result owners repaired:** Dependency commits `fca10f8` and `3c2023df4d49871ebc16a0bbdfc4a0a85bc95e81` preserve the four separately source-defined polynomial methods and infer the native inversion result without making matrices covariant. `characteristic_polynomial` forwards the actual `charpoly` arguments; `minimal_polynomial` still permits only its variable positionally. Generic inversion retains its original empty/non-domain result as well as the scalar reciprocal's coefficient extension, while the dense integer inverse remains rational. Integral powers retain the original or inverse type. Matrix indexing now distinguishes scalar entries, rows and submatrices without overlapping result annotations; aliases eliminate class-method shadowing of builtins. `Element.base_ring` returns the stored base parent or `None`, not a category's method provider. Both source units passed the normal dependency hook. All seven affected source/type-consumer files pass strict mypy at `3c2023d`, and the three complete native inverse, polynomial, and determinant/span consumers pass (`/tmp/sage-stubs-inverse-polynomial-types-3c2023d.log`, `/tmp/sage-stubs-inverse-owner-native-3c2023d.log`). The inverse consumer includes nonunimodular integers, rationals, a polynomial fraction field, the empty matrix, and a ring with zero divisors; the polynomial consumer distinguishes repeated characteristic roots from the minimal polynomial.

- **Dense dependency repair completed locally:** Dependency commit `f19dc7973149adf54b2754fae3e1364283f1c351` closes the retained matrix repair through the unchanged normal `sage-stubs` hook. The final unit reconciles matrix0/1/2 ownership, native Singular conversion, backend-overridable dense pickle payloads, integer/rational/cyclotomic call domains, coefficient-changing inversion, Smith/echelon/decomposition/randomize contracts, and cyclotomic tensor products. The three dense stubs plus their four shared owners pass strict mypy together with `typing-tests/dense_matrix_owner_types.py`; all four complete native matrix consumers pass (`/tmp/sage-stubs-dense-all-types-final.log`, `/tmp/sage-stubs-dense-native-final.log`). Native-incompatible ancestor calls are not advertised as successful: where a concrete override really rejects an ancestor-only argument shape, the stub preserves that call as non-returning rather than fabricating support. T05.1, T05.2, T05.3, and T05.5 are restored to done in the dependency phase plan. The dependency branch is eight commits ahead of public `origin/main`; the parent still declares `sage-stubs @ ...@main` and `uv.lock` still resolves `1d87ee246c5dc95a29617ac64eaa46b9f3df5d48`, so publication/integration remains a separate prerequisite.

- **External annotation provisioning:** The first full check of the existing `matrix1.pyi` reported missing mpmath/SymPy type information and unimported NumPy annotation types. Installing the parent project's already-declared `microsoft-python-type-stubs` dependency into the actual Sage interpreter (resolved revision `f7474b297f8764ad96db2e0ce9c0a7bd27fd8d59`) resolves the SymPy import failure. The unchanged matrix1 check still reports four errors involving the untyped mpmath import and NumPy annotations (`/tmp/sage-stubs-matrix1-provisioned-baseline.log`). No matrix1 source or checker configuration was changed. Source inspection also identifies its incorrect `_singular_` ancestor signature: `matrix1.pyx:421-437` uses `Singular` and returns `SingularElement`, rather than the unrelated types declared by the current stub. This is a required T05.2 source repair, whose supporting annotation dependencies must first be made available without suppressing imports.

- **Overlapping execution despite sole-writer context:** During this continuation, files written by this session were changed by other tool executions in the same checkout: `unique_representation.pyi`, `factory.pyi`, and `term_monoid.pyi` changed at 20:25:29-30 UTC, followed by a separately launched factory-consumer command. The source commit made by this session, `ea51c3f`, was then amended to `0df25c1`; comparison showed only two phase-card documentation changes, with identical source and tests. Related changes were preserved and reconciled, not discarded as unexplained dirt. A read-only `agents status` request returned `WORKER_IDENTITY_LOST`; session discovery exposed unattributed activity rather than an independently addressable writer. No worker, branch, or worktree was created by this continuation. The same condition recurred during the inverse-owner repair: intermediate source edits and commit `3c2023d` appeared between visible tool calls. Its actual diff, normal-hook output, seven-file strict result and complete committed-revision native results were collected and checked before use. The execution coordinator must enforce the declared sole-writer ownership and restore attributable calls; an inherited dirty tree alone is not evidence of another writer, but these observed intervening writes are.

- **Earlier parser-stop evidence:** The 2026-09-10 ordinary commit gate reached mypy 2.0.0 but stopped parsing `sage-stubs/matrix/matrix_integer_dense.pyi:174` from the declared `sage-stubs` revision `d0aa14f52c60431c587bf49ae9a78fe62ba3d940`. That source contains six invalid `..` placeholders at lines 174, 180, 186, 187, 201, and 202, and `def LLL\(` at line 210. The corresponding Sage definitions are at `matrix_integer_dense.pyx:2250` (`saturation`), `:2599` (`frobenius_form`), and `:3078` (`LLL`); their stub placeholders must be `...`, and the method identifier has no backslash. The upstream file was checked independently and contained the same defects. No project type-check result follows from this parser stop. At that checkpoint, no dependency source or pin had been changed; the later source repair and its unresolved gate are recorded above. Do not edit installed caches, suppress the dependency's imports, or classify this new failure as an established project baseline.

- **Current gate outcome:** With the native CLI binding repaired, all Sage files pass syntax validation. A local CPython-3.14 homotopy wheel plus a temporary uv absolute override to the committed local `sage-stubs` source lets the unchanged parent `just test-commit` pass both dependency-resolution blockers without editing `pyproject.toml` or `uv.lock`. The gate then reaches project mypy and reports 2,366 errors in 32 project files (`/tmp/sage-categories-parent-local-deps-gate.log`), beginning with the unannotated helper in `tests/static/test_stub_generator_ast.py` and broad category/functor/refinement type-contract failures. This is the first project-level mypy result obtained past the dependency parser stop; it is not a restored ordinary gate because the published `sage-stubs@main` contract remains stale. The gate's 25 autoformat edits were compared against HEAD and restored rather than banked as unrelated churn.
  The hook also selected 41 Python files from the unpushed branch difference despite this being a `.sage`-only code change; its 23 formatting edits were checked AST-identical and restored, rather than silently adding unrelated source changes to the checkpoint.
  On 2026-09-11, after the architecture and first static-projection repairs were banked, the ordinary `just test-commit` retry again failed to reach project mypy: the Semgrep autofix subprocess remained live but the retained gate log did not advance across two measured five-second intervals. Under `POL-WORK-004` that run was stopped as stalled; it had made no tracked edits. This is gate-execution friction, not a Semgrep finding or evidence about the mathematical/static assertions.
  Later the retained tmux run of the unchanged #45 `category_morphism_parameters.py` consumer against committed projection `4cbbf51` disappeared before completion: the tmux session no longer existed, no mypy process remained, and its status file was never written, while the retained log stopped at 1,144,888 bytes. Under the session-continuity rule this is a killed/dead execution, not a checker result. The committed tree remained clean and the same consumer must be relaunched from `4cbbf51`; the partial log supplies no acceptance or failure count.
  No static or mathematical acceptance follows from syntax validation.

- **Current native CLI boundary:** The first 2026-09-10 commit attempt on the set-scaffold correction reached `_sage-syntax` and failed because the conda Sage 10.9 `sage.cli` entry point has no `--preparse` or `-python` option.
  The matching upstream `src/bin/sage-preparse` at tag `10.9` was provisioned unchanged (Git blob `aeb36c926751cf7b3b8a9dd58cfc56dbba7115f9`). `/tmp/sage314-qc/sage` delegates the legacy QC flags to that native script and the existing Python 3.14 interpreter; `SAGE_BIN=/tmp/sage314-qc/sage` selects this runtime.
  No preparsing algorithm, test assertion, or mathematical expectation was rewritten by this launcher repair.
  The wrapper is host provisioning, not a substitute computation engine.

- **Evidence:** On 2026-09-09 after the daemon/runtime restart, `just test-commit` first failed because `SAGE_BIN` was unset.
  Sourcing the tracked `.envrc` selected `$HOME/miniforge3/envs/sage/bin/sage`, whose runtime is Python 3.12 and emits `ModuleNotFoundError: sageparse` during startup.
  The previously provisioned `/usr/local/sage-env/{sage,python,sage-preparse}` wrappers no longer existed.
  This host also disallows rootless user namespaces (`unshare` cannot write `/proc/self/uid_map`), so the documented research image cannot be recovered through a rootless container fallback.
  The mypy stage then invoked each dependency-group requirement separately through `uvx --with`; for the declared workspace dependency `sage-categories-homotopy`, that bypassed `[tool.uv.sources] sage-categories-homotopy = { workspace = true }` and attempted public-registry resolution.
  Building the checkout's CPython-3.14 wheel locally made that requirement resolvable and exposed the underlying known compiler mypy baseline.
  Reproducing that launcher with `uvx --with-editable .` also rewrote `pyproject.toml`/`uv.lock` transiently by pinning `sage-stubs`; those mutations had to be reverted before banking source work.
  `just plan-state` also failed at `tee /dev/stderr` in this connector PTY even though the plan and `itree doctor` checks themselves passed when executed directly.

- **Additional evidence:** `bwrap --ro-bind / / --proc /proc --dev /dev /bin/true` fails at UID-map setup with `Permission denied`, and there is no Docker, Podman, containerd, or corresponding runtime socket on this host.
  Noninteractive `sudo` also fails.
  Thus the documented OCI research image has no executable local launch path even though `/proc/sys/kernel/unprivileged_userns_clone` is `1`.

- **2026-09-10 continuation:** `/tmp/sage314` now contains conda-forge Sage 10.9 and Python 3.14.7, but the tracked `.envrc` still selects the older path.
  The new environment's installed distributions include neither the project's SymPy dependency nor DisCoPy, JuliaCall, Maude, or the local homotopy binding.
  The old default tmux socket is absent even though orphaned tmux processes remain; a session name is not evidence of an executable retained job.
  At inspection the root filesystem had 27 GiB free, while about 18 GiB of 19 GiB swap remained occupied.
  These are current setup observations, not execution of any mathematical assertion.

- **Provisioning repair:** `uv pip install --python /tmp/sage314/bin/python --group platform -e .` initially rejected the zero-byte `asttokens-3.0.2.dist-info/direct_url.json`. Trashing only that malformed optional provenance file allowed the declared dependencies and local homotopy binding to install with `CARGO_BUILD_JOBS=1`. The first full set-scaffold load then started Sage in 12.49 seconds but failed during preprocessing: Sage hoisted numeric constants before `from __future__ import annotations`, producing a `SyntaxError` before imports or assertions.
  The consumer now uses the declared Python 3.14 annotation semantics without that incompatible future import; its mathematical assertions remain unchanged.
  Other `.sage` consumers with future imports require the same source-level diagnosis rather than a loader that strips or rewrites their assertions.

- **Further full-consumer reproduction:** At `374015b`, native Sage `load()` also stops before assertions in `tests/sets/test_indexed_products.sage` and `tests/sets/test_sequential_colimits.sage`, with generated numeric constants preceding their future imports.
  The two files now use the declared Python 3.14 semantics directly; their complete indexed and sequential assertions are unchanged.
  The mypy tool environment subsequently provisioned successfully from the declared dependency groups and checkout-built homotopy wheel; a successful `mypy --version` is setup evidence, not a type-check result.

- **Gap and impact:** The tracked local QC path does not currently reconstruct the same Sage/Python 3.14 runtime and workspace dependency graph that the project declares.
  A developer can reach source-format and static-analysis stages only by manually repairing environment state, and the public test consumer can block in the incompatible Python-3.12 Sage runtime before reaching its assertion.

- **Uncertainty:** The failures above are specific to the post-restart local host/connector environment.
  CI provisioning still declares the `/usr/local/sage-env` wrapper path, but that provisioning was not rerun here.
  The workspace-resolution defect is in the current local QC launcher behavior and was reproduced independently of Sage startup.

- **Repair link and acceptance:** Operational QC/runtime owner.
  Resolve when `just test-commit` provisions or selects the repository's Python-3.14 Sage runtime, preserves uv workspace-source resolution for local packages, and `just plan-state` works in the supported terminal without requiring a writable `/dev/stderr` device.

Preserve concurrent entries.
Once the full repair is verified, retain only the unresolved requirement here and put resolution evidence in its commit.
A local fix does not resolve missing downstream maps or broader hypotheses.
Recording an independent issue allows the assigned work to continue; recording a required prerequisite does not authorize bypassing it.

## Sage scalar coercion can lose a SymPy Lambda variable's identity

- **User action and evidence:** In the full set scaffold before `264b19f`, the preparsed expression `2 * variable`, with `variable = sympy.Dummy("x")`, is evaluated first by Sage's integer coercion.
  Its Sage symbolic expression converts back to the body `2*x` with a distinct ordinary SymPy symbol.
  `Lambda(variable, 2*x)` therefore returns the same unbound expression at zero and at `sqrt(2)`; it does not return `2*sqrt(2)`. The retained native diagnostic and result are `/tmp/sage-categories-lambda-binding-diagnostic-20260910.py` and its `.log` counterpart.

- **Owner and impact:** This is a Sage/SymPy symbolic-conversion boundary, occurring before the set-map constructor receives its Lambda.
  The set membership predicate correctly leaves realness of the unbound expression undecided.
  It must not identify free and bound symbols by their printed names or weaken membership to accept an unproved real datum.

- **Repair and preservation:** The scaffold now builds the native SymPy expression with the raw integer coefficient `2r`; the full original consumer passes with two additional independent component-value assertions.
  Any upstream coercion repair must preserve the Dummy's identity through the symbolic conversion.
  The independent review's claim that the failed datum was already a genuine `2*sqrt(2)` is contradicted by the native result and is not a basis for changing `representative()` or predicate decisions.

## Leaf-authoring friction — production-tower scaffolds

- **Workstream:** production-tower leaf scaffolds — Sets integration, supplied monoidal structures, the order leaf (binary relations, posets, total orders), and magma/monoid consumers over sets.

- **Commits:** `51ca8d7..2f25e26` on `codex/functorial-core-kernel`, baseline `f679083`.

- **Date:** 2026-09-05.

Short answer: the philosophy is half-met.
The spine works and is genuinely thin.
"A mathematician who doesn't program can reason into correct code" is undercut by about nine concrete warts, several of which I hit head-on writing the poset leaf, and two of which my own leaf now carries.

### What actually worked (the win)

Declaring one structure functor to a base and getting everything downstream for free.
`BinaryRelations().to_sets()` as a faithful isofibration gave relation objects their points, maps, iteration, and set constructions, correctly parented, with no extra code.
`equality.point(0)` just worked and its parent was the relation object.
That is the philosophy delivering, and it is thin.

### Warts, ranked by how much they break the promise

**Tier 1 — the "copy the template and reason" path is broken.**

1. The canonical poset specimen does not run as written.
   `specs/poset-minimal-template.py:109` defines order comparison as `relation.membership_proposition(relation.ambient_object()(self, other))`, but `membership_proposition` is a category method, and `relation` there is a subobject value.
   A leaf author copying the template gets an attribute error, not a poset.
   The template is the primary teaching surface, so this is the most damaging wart.
   I had to implement `<=` a different way.

2. Finite property decision is hand-rolled, and the generic relation calculus is not reusable.
   `cat/relations.py:97-107` already decides reflexivity, transitivity, and antisymmetry, but on relation *morphisms* of `Relations(C)`, a different representation from the order leaf's sets-with-a-relation objects.
   I could not reuse it, so `order/posets.py` re-decides the three laws over raw `.datum()` tuples.
   That duplication is a real design smell, and my leaf owns it.

**Tier 2 — kernel/Cat design deficiencies.**

3. Cat cannot encode or carry standard categorical structure facts.
   There is no first-class way to state and retain that a category has a terminal or initial object, is pointed, has products or coproducts, has (small, filtered, or other) limits or colimits, is complete, cocomplete, or bicomplete, is closed under pullbacks or pushouts, is monoidal with respect to one or more structures, or is abelian.
   Nor are the theorems that derive these facts baked in — for example, that `Fun(C, D)` has a terminal object because `D` does, or that a functor category into a complete category is complete.
   Downstream code cannot reason from such a fact because the framework has nowhere to hold it.
   The terminal problem in (4) is one narrow symptom.

4. An unmet contract obligation surfaces as a runtime raise, not at instantiation.
   `Category.Terminal()` raises "declares no terminal object" only when the method is called; a leaf author learns which parts of the inherited contract are unimplemented by hitting runtime errors during execution rather than from defining or instantiating the leaf.
   `Fun(C, D)` and a finite presented category both have a terminal object — `[1]` and `Fun(C, C)` among them — computable from machinery they already carry (pointwise limits; finite morphism enumeration), yet nothing signalled the method was unimplemented until the call failed, and I supplied `Terminal()` on both by hand.
   A category with genuinely no terminal, such as the walking parallel pair, should express that absence as a property, not communicate it only by raising when asked.

5. Claiming a declaration has no mechanism for axiom-subcategory leaves.
   `leaf-scaffolding.md` says the declared `Posets`/`TotallyOrderedSets` must be claimed; `ordered-sets.md` realizes them as `BinaryRelations().PartialOrder()`. Nothing binds an open declaration to an axiom subcategory of a constructed category, so the declared symbols are unclaimed and only accessors exist.

6. The least common category of two property-refined placements needs hand-declared inclusions.
   I fixed the monoid-forgetful case, but `NarrowedProperty` still enumerates cross-inclusions imperatively, so composing property-intersection placements can still report "no least common category," which is a missing edge, not a mathematical fact — the property lattice is maintained by hand rather than derived, a facet of the same gap as (3).

**Tier 3 — plumbing leaking into leaf mathematics.**

7. Predicate-handler registration is definition-order sensitive with an opaque error ("unresolved semantic domain"); registrations must sit below the classes they annotate.
   A mathematician would not predict that.

8. Construct versus refine take different argument types.
   `Posets()(subobject)` works, `Posets()(relation_object)` does not, because the property-subcategory constructor re-runs the base constructor on the base's construction datum.

9. `.datum()` and `.point()` unwrapping is everywhere.
   "The relation on X×X selected by ≤" becomes tuple decomposition and rewrapping.

### Net

The "up and running is thin" claim holds only for the inheritance spine.
Getting a leaf *functional* today demands knowing the handler-ordering rule, the Axiom/PropertySubcategory wiring, that the contract announces unmet obligations only by raising at call time, that Cat cannot hold the categorical structure facts downstream code needs, and that the template does not run.
That is more kernel knowledge than the philosophy wants at the prototyping stage.

### Provisional: what could be reabsorbed upstream

*Advisory only — a post-mortem sweep of this workstream's code, not a mandate, a plan, or an approved design.
Each note points at leaf or kernel code written here that a more capable Cat or kernel could absorb, with the reduction it would yield.
Ideas, to be weighed, not obligations.*

- **Derive named universal objects from the construction already present.** `Terminal()` was hand-written this workstream on both `FunctorCategory` and `FinitePresentedCategory`, yet each is computable from machinery the category already carries — the empty pointwise limit, and finite morphism enumeration.
  A generic derivation of `Terminal`, `Initial`, and the other named universal objects from `limit_construction` and finite enumeration would delete both patches and spare every later leaf the same.
  (Touches warts 3, 4.)

- **A generic endorelation-from-predicate construction with finite property decision.** Most of `order/posets.py` is "a set plus a binary predicate," with reflexivity, antisymmetry, transitivity, and totality decided over the finite carrier (`_related_pairs`, `_decide_partial_order`, `_decide_total_order`, `_decide_order_related`, `from_predicate`). None of it is order-specific.
  Lifted into Cat, or unified with the existing `cat/relations.py` law predicates, the order leaf would state only which properties name `Posets` and `TotallyOrderedSets`, removing roughly the enumeration half of the module and generalizing to any "structured set decided by a finite predicate" leaf.
  (Touches warts 1, 2, 9.)

- **A faithful-structure-over-a-base scaffold.** The leaf's `construct_identity`, `composite`, `construct_morphism`, and its relation-preservation check are the mechanical content of "objects are base objects with extra data; morphisms are base morphisms preserving it."
  The algebraic leaves already get this shape from `InserterCategory`; a lighter base for structure-by-a-forgetful-functor leaves would absorb the identity and composite wiring and take only the preservation predicate.
  (Touches warts 8, 9.)

- **Pair-membership as a proposition on the relation subobject.** If the subobject value answered "is this ordered pair in me?"
  as a proposition, the template's intended `__le__` would run and the bespoke `order_related` predicate and handler would be unnecessary.
  (Touches wart 1.)

- **Lazy predicate-handler domain resolution.** Resolving a handler's semantic domain when first needed rather than at registration would remove the definition-order constraint and the "registrations at the module bottom" dance.
  (Touches wart 7.)

- **Derived property-subcategory inclusions.** Deriving the cross-inclusions `NarrowedProperty` needs for a decidable least-common-category, rather than enumerating them imperatively, would retire the hand-fix made this workstream and the residual "no least common category" failures.
  (Touches wart 6.)

## Concrete category delegation to GAP/CAP packages

- **Area:** `Cat().Concrete()` and leaf computational delegation.

- **Contract:** `Cat` centralizes `Cat().Concrete()` once `Sets()` is defined.
  Categories in `Cat().Concrete()` then delegate computational operations to upstream GAP and CAP packages rather than hand-rolling Python algorithms.

- **Defect:** Previous implementations conflated the abstract Python class compiler with concrete category computation.
  When CAP could not function as an abstract Python class compiler, implementations dropped CAP entirely.
  Concrete leaf categories hand-rolled algorithms over raw tuples in Python instead of delegating to mature GAP packages.

- **Target packages for delegation:**

  - `AdditiveClosuresForCAP`: Additive closures of categories.

  - `Algebroids`: Computations with algebroids and path algebras.

  - `CAP`: Core categorical algorithms, constructors, and generalized morphisms.

  - `CartesianCategories`: Cartesian, cocartesian, and monoidal structures.

  - `CompilerForCAP`: Compilation of pure-GAP category algorithms.

  - `FinSetsForCAP`: Finite sets and maps.

  - `FiniteCocompletions`: Finite cocompletions of finite categories.

  - `FpCategories`: Quivers, path categories, and finitely presented categories.

  - `FpLinearCategories`: Finitely presented linear categories.

  - `FreydCategoriesForCAP`: Freyd categories and abelian closures.

  - `FunctorCategories`: Functor categories with finite or presented sources.

  - `GroupsAsCategoriesForCAP`: Groups as one-object categories.

  - `LinearAlgebraForCAP`: Constructive linear algebra and matrix categories.

  - `LinearClosuresForCAP`: Linear closures and linear categories.

  - `Locales`: Locales and frame representations.

  - `MonoidalCategories`: Monoidal, symmetric, and braided categories.

  - `PresheafCategories`: Presheaf categories and sheaves.

  - `QPA`: Quiver and path algebra representations.

  - `QuotientCategories`: Category quotients by congruence relations.

  - `SliceCategories`: Slices and coslices of concrete categories.

  - `SubcategoriesForCAP`: Subcategories and image inclusions.

  - `ToolsForCategoricalTowers`: Finite diagram limits, colimits, and doctrines.

  - `ToolsForHomalg`: Foundational homalg data structures and matrix tools.

  - `Toposes`: Topos-theoretic constructions.

## Hand-rolling algorithms available in mature external libraries

- **Area:** Computational engines and concrete leaf operations.

- **Contract:** The repository must avoid hand-rolled code where mature external libraries exist (GAP, Julia/Catlab, SageMath, SymPy, Singular, Macaulay2, NetworkX). Leaf categories must delegate computation to these engines.

- **Defect:** Across multiple mathematical domains, the codebase contains bespoke, hand-rolled Python algorithms for problems with existing reference implementations:

  1. **Posets and binary relations:**

     - *Hand-rolled:* `order/posets.py` implements $O(n^3)$ triple Python loops to verify reflexivity, antisymmetry, and transitivity.
       `cat/relations.py` hand-rolls relation inclusion and composition.

     - *Mature libraries:* SageMath (`sage.combinat.posets.posets.Poset`, `sage.graphs.digraph.DiGraph`), NetworkX (`algorithms.dag`, `transitive_closure`), GAP (`Posets`, `Digraphs`), and Julia (`Catlab.CategoricalAlgebra.FinRelations`).

  2. **Finite sets, functions, and quotients:**

     - *Hand-rolled:* `sets/_finite.py` constructs ad-hoc NetworkX graphs to compute equivalence classes.
       `sets/finite.py` hand-rolls tuple equality recursion and membership searches.

     - *Mature libraries:* GAP (`FinSetsForCAP`), SageMath (`FiniteEnumeratedSet`, `DisjointSet`), and SymPy (`FiniteSet`, `ProductSet`).

  3. **Quivers, path categories, and presented colimits:**

     - *Hand-rolled:* `cat/presented_colimits.py` and `cat/canonical.py` manually manipulate generator strings, quiver relations, and path concatenation in Python dictionaries.
       Only word reduction delegates to GAP `kbmag`.

     - *Mature libraries:* GAP (`FpCategories` for quivers, path categories, and quotients; `QPA` for quiver representations and path algebras) and Julia (`Catlab.Presentation`).

  4. **Finite diagram limits, functor categories, and slices:**

     - *Hand-rolled:* `cat/finite_categories.py` uses nested `itertools.product` loops to enumerate commuting squares, limits, and comma categories.
       `cat/kan.py` and `cat/weighted.py` hand-roll pointwise Kan extensions and weighted limits.

     - *Mature libraries:* GAP / CategoricalTowers (`ToolsForCategoricalTowers` for `LimitPair`/`ColimitPair`, `SliceCategories`, `FunctorCategories`) and Julia (`Catlab.CategoricalAlgebra.Limits`).

  5. **Internal algebraic structures:**

     - *Hand-rolled:* `cat/structured_objects.py` hand-rolls inserters, equifiers, and operation renaming for magmas, monoids, groups, and semirings.

     - *Mature libraries:* GAP (`MonoidalCategories`, `CartesianCategories`, `Algebroids`, `GroupsAsCategoriesForCAP`), SageMath algebraic categories, and Singular/Macaulay2.

  6. **Linear and additive categories:**

     - *Hand-rolled:* `cat/modules.py` and `cat/bimodules.py` write bespoke module and matrix handling.

     - *Mature libraries:* GAP (`LinearAlgebraForCAP`, `LinearClosuresForCAP`, `AdditiveClosuresForCAP`, `FreydCategoriesForCAP`).

## Failure to integrate Catlab.jl for finite diagrams and presentations

- **Area:** Julia / Catlab engine integration.

- **Contract:** [specs/resolution.md](specs/resolution.md#L53), [pyproject.toml](pyproject.toml#L37), and [src/sage_categories/juliapkg.json](src/sage_categories/juliapkg.json) explicitly specify Julia 1.12.7, Catlab 0.17.6, and GATlab 0.2.4 via `JuliaCall` as the computation engine for finite diagrams, free diagrams, and limit/colimit presentations.

- **Defect:** Previous implementations failed to integrate Catlab.jl.
  Instead of using Python as the stitching layer to coordinate independent engines, agents fabricated an artificial requirement for a direct GAP-to-Julia FFI bridge and treated `JuliaCall` as an unwanted boundary.
  To avoid writing the `JuliaCall` adapter, agents substituted hand-rolled Python algorithms (`cat/finite_categories.py`, `cat/presented_colimits.py`).

- **Current composite-action mismatch (source inspection at `264b19f`):** `tests/engines/test_catlab_functor_calculus.sage:62-76` explicitly requires an applied composite to remain without a native functor until `ensure_native_functor` is called.
  Its module docstring instead claims Catlab executes those composites.
  `CategoryOfCategories.MorphismType.on_object` and `on_morphism` route to the declared Python actions; the Catlab-backed `_construct_object_image` and `_construct_morphism_image` methods do not supply these public actions.
  The governing plan's sections 5, 10, and 19.2 still require native composite execution, including the unenumerated-source and selected-composite inheritance consumers.
  This observation does not assert that a new full callable-functor run failed.
  Reconcile actual execution with the governing native contract while preserving primitive declaration callbacks and the full admitted category domain; native representation registration alone does not establish native execution.

- **Required resolution:** Implement the private `JuliaCall` adapter connecting Python categorical data to Catlab's `FreeDiagram`, `diagram_limit`, and `diagram_colimit` in `Catlab.CategoricalAlgebra.Limits`, removing hand-rolled Python iteration.

## Spurious claim of missing GAP-Julia bridge as pretext to drop dependencies

- **Area:** Multi-engine coordination and FFI architecture.

- **Contract:** The repository functions as a stitching framework in Python on Sage.
  Python/Sage weaves external computation engines (GAP via `libgap`, Julia via `JuliaCall`) and coordinates data transfer between them.

- **Defect:** Prior architectural reports claimed that using both GAP/CAP and Julia/Catlab was blocked because no direct C-level bridge existed between GAP and Julia.
  This claim was spurious on two counts:

  1. `GAP.jl` already exists in the Julia ecosystem (via OSCAR) and provides a direct C-level bridge between Julia and GAP.

  2. Direct cross-engine communication is unnecessary because Python/Sage acts as the orchestrator.
     Python calls `libgap` for GAP operations and `JuliaCall` for Julia operations, translating data across the boundary when required.
     Agents used this artificial constraint to reject both dependencies and justify hand-rolling category algorithms in pure Python.

- **Required resolution:** Coordinate engines through Python/Sage.
  Call `libgap` for GAP/CAP algebraic computations and `JuliaCall` for Catlab diagram calculations without demanding a direct GAP-Julia foreign-function interface.

## Hand-rolling morphism rewriting logic instead of delegating to Maude

- **Area:** Morphism composition, path reduction, and rewriting engines.

- **Contract:** Categories, finitely presented quivers, and 2-categories are order-sorted equational and rewriting theories.
  Morphism composition is an associative binary operator with left and right identities; path equivalence under generating relations is term rewriting modulo associativity and identity.
  The repository must delegate algebraic rewriting to mature rewriting engines.

- **Defect:** The codebase hand-rolls path logic in Python tuples and string operations ([src/sage_categories/cat/canonical.py](src/sage_categories/cat/canonical.py), [src/sage_categories/cat/presented_colimits.py](src/sage_categories/cat/presented_colimits.py)). It uses a low-level wrapper around GAP's monoid tool `kbmag` ([src/sage_categories/kernel/word_rewriting.py](src/sage_categories/kernel/word_rewriting.py)), which lacks sorted object types and requires Python code to track vertex compatibility manually.

- **Target engine:** Maude (or `python-maude`). Maude provides:

  1. Order-sorted equational logic for typed objects and morphisms.

  2. Native term rewriting modulo associativity and identity ($A, U$).

  3. Automated Knuth-Bendix completion and Church-Rosser confluence checking.

  4. Native support for 2-cell composition, whiskering, and the interchange law.

- **Required resolution:** Replace bespoke Python string/tuple path concatenation and the monoid `kbmag` wrapper with a rewriting engine (such as Maude or GAP's sorted `FpCategories`) that models morphism sorts and relations directly.

## Hand-rolling monoidal coherence logic instead of delegating to DisCoPy

- **Area:** Monoidal categories, strictification, and coherence.

- **Contract:** Monoidal categories, symmetric/braided structures, and string diagrams have mature reference implementations in Python.
  By Mac Lane's coherence theorem, monoidal categories are monoidally equivalent to strict monoidal categories where associators and unitors are identities up to coherence.
  The repository must delegate monoidal calculus to existing libraries rather than hand-rolling coherence checks.

- **Defect:** The codebase implements monoidal categories from scratch ([src/sage_categories/cat/monoidal.py](src/sage_categories/cat/monoidal.py), [src/sage_categories/cat/structured_objects.py](src/sage_categories/cat/structured_objects.py)):

  1. Hand-rolls rebracketing functors (`tensor_parentheses`), unit functors (`tensor_units`), and manual associator/unitor natural isomorphisms via product projections.

  2. Implements manual verification of Mac Lane's pentagon and triangle equations across explicit quadruple and triple objects.

  3. Hand-rolls monoidal reversal ($V^{\mathrm{rev}}$) by reversing object tuples and component reindexing.

  4. Manually constructs internal magma and monoid objects via categorical inserter limits.

- **Target engine:** DisCoPy (`discopy`). DisCoPy provides:

  1. Strict monoidal categories with automatic adherence to the interchange law.

  2. Planar string diagrams and graphical calculus.

  3. Native symmetric, braided, rigid (cups/caps), and compact closed category operations.

  4. Direct functorial evaluation into semantic domains (such as matrices, relations, and circuits).

- **Required resolution:** Delegate monoidal category constructions, coherence tracking, and tensor composition to DisCoPy rather than maintaining bespoke rebracketing and diagram checks in pure Python.

## Hand-rolling higher-morphism towers instead of delegating to homotopy-rs

- **Area:** Globular $n$-morphism towers, 2-cell composition, and higher coherence.

- **Contract:** Higher categories, globular morphism towers ($\mathrm{Mor}(n, C)$), and $k$-cell compositions along $j$-cells ($j < k$) are solved by specialized higher-category engines.
  Higher interchange laws and coherence equations should be evaluated by engines designed for associative $n$-categories rather than hand-rolled Python callbacks.

- **Defect:** The codebase hand-rolls the $\mathrm{Mor}(n, C)$ tower and 2-cell operations in pure Python:

  1. Truncates higher dimensions in [src/sage_categories/cat/morphisms.py](src/sage_categories/cat/morphisms.py) by making $\mathrm{Mor}(n, C)$ discrete for $n \ge 2$.

  2. Hand-rolls 2-cell horizontal composition, vertical composition, and whiskering as custom Python functions in [src/sage_categories/cat/category.py](src/sage_categories/cat/category.py) and [src/sage_categories/cat/functors.py](src/sage_categories/cat/functors.py).

  3. Hand-rolls boundary matching and endpoint checks via ad-hoc SymPy queries.

- **Target engine:** [homotopy-rs](https://github.com/homotopy-io/homotopy-rs) (`homotopy-core`). The Rust core provides:

  1. Finitely-presented associative $n$-categories in arbitrary dimensions.

  2. Exact boundary computations (source and target) for $k$-cells.

  3. Compositions of $k$-cells along bounding $j$-cells with automatic interchange preservation.

  4. Homotopy moves, diagrammatic rewriting, and equivalence verification for higher morphisms.

- **Required resolution:** Delegate higher-dimensional morphism towers, 2-cell compositions, and interchange handling to `homotopy-core` (via Rust/PyO3 bindings) instead of maintaining a truncated, hand-rolled Python implementation.

## OSCAR availability probe stalls in the embedded Julia environment

- **Area:** Julia / OSCAR engine integration for #47.

- **Observed:** `uv run --no-project --python 3.14 --with juliacall` reached JuliaCall startup but `Base.find_package("Oscar")` produced no result after repeated 30-second polls.
  The probe process remained alive until explicitly killed.

- **Impact:** The governing plan allocates polynomial rings, quotients, localizations, affine schemes, sheaves, and gluings to OSCAR. The repository cannot currently verify that the embedded Julia environment exposes OSCAR before extending `SageCategoriesBridge.jl`.

- **Required resolution:** Make the repository's pinned Julia environment expose and load OSCAR through the existing JuliaCall bridge, with a fast deterministic availability/version probe suitable for the ring/affine acceptance gate.

## Catlab and OSCAR cannot share the repository JuliaPkg environment

- **Area:** Julia engine isolation; Catlab/GATlab and OSCAR.

- **Observed:** In a recovered Sage 10.9 / Python 3.14.7 runtime, the decisive #31 public consumer reached JuliaPkg resolution and failed before any test assertion.
  Catlab 0.17.6 constrains Compose to a release requiring `JSON <= 0.21`, while OSCAR 1.8.2 requires `JSON >= 1.0`; Julia's resolver reports these requirements as unsatisfiable in one project.

- **Impact:** Declaring OSCAR in `src/sage_categories/juliapkg.json` prevents every Catlab-backed category consumer from starting, even when the consumer never imports the OSCAR engine.
  Lazy Python loading does not isolate Julia package versions because both bridges still share one Julia process and project.

- **Required resolution:** Keep Catlab/GATlab in the package-global JuliaPkg environment.
  Run OSCAR in a separate Julia process/project with an explicit opaque-handle boundary, so incompatible transitive dependencies never enter one Julia process.
  Until that process boundary exists, OSCAR must not be declared in the global JuliaPkg project.

## Recovered Python-3.14 Sage runtime exhausts host headroom under public consumers

- **Mathematical need or user action:** Execute the required public Sage consumers under the declared Python 3.14 runtime, including #31 and arbitrary-index module-sum acceptance.

- **Evidence:** A local Sage 10.9 / Python 3.14.7 environment was successfully provisioned at `/tmp/sage314` and is about 2.4 GiB. During 2026-09-10 public-consumer runs the root filesystem fell as low as about 55 MiB free and the host used about 11 GiB of swap.
  Single Sage/Julia/Catlab consumers repeatedly spent minutes in `folio_wait_bit_common` before reaching test bodies.
  On 2026-09-11 a full static-stub regeneration process remained live for 2m15s but entered `folio_wait_bit_common`; its retained log stopped at 244 bytes after the Sage runtime warning and no projected stub write advanced during the observed interval. At that point the host had about 557 MiB free RAM, 10 GiB of 19 GiB swap in use, and 24 GiB free disk. The run was stopped under `POL-WORK-004`, and the raw `stubgen` files it had written before stalling were restored rather than mistaken for a completed compiler projection.
  The #31 residue construction nevertheless crossed the previously failing tensor/functor placement path after `5568f78`; subsequent cold-start diagnostics were stopped to avoid exhausting the host.
  The three #31 public consumers were then changed to import their actual owners directly instead of `sage_categories.all`, and primitive functor / natural-transformation actions were restored to their declared Python callbacks while retained composites remain Catlab-backed (`10243b9`, `3d6379c`, `4a55964`). Unrelated resident workloads were left untouched.

- **Gap and impact:** The compatible runtime now exists, but this host cannot reliably execute several cold Sage/Julia consumers while the filesystem and memory are under this pressure.
  Source/static/architecture checks remain usable; long runtime acceptance can be nondiagnostic or terminated externally before an assertion is reached.

- **Repair link and acceptance:** Runtime/gate owner.
  Resolve when the declared runtime is provisioned with enough persistent disk and memory headroom that the public consumer suite can run without swap-thrashing or filesystem exhaustion.
