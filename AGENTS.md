<!-- agent-memory:start -->
# Agent memory

This repository uses the central agent memory vault at `/home/dzack/.agent-memory-vault`.

Project memory key: `projects/github.com__dzackgarza__research/index`.

Repository `.agents` and `.hermes` paths are symlinks to the same vault-owned project directory.

Before changing architecture, search both project and global memory:

```bash
agent-memory search --scope both "<task or subsystem>"
```

Record durable repo-specific lessons with:

```bash
agent-memory add --scope project --type decision --title <title> --content <content>
agent-memory add --scope project --type trap --title <title> --content <content>
agent-memory add --scope project --type advice --title <title> --content <content>
agent-memory add --scope project --type context --title <title> --content <content>
agent-memory add --scope project --type reference --title <title> --content <content>
```

Plan work is card-backed.
Create and update plan cards with `agent-memory plan add` and `agent-memory plan update`, not `agent-memory add --type plan`.

Use `agent-memory retrieve <key>`, `agent-memory update <key>`, and `agent-memory delete <key>` for memory CRUD.

The vault should be committed at all times.
Treat staged or unstaged vault changes as an ephemeral error state.
Before normal memory work resumes, load the bundled vault-maintenance skill with `agent-memory maintain skill vault-maintenance` and follow its referenced check, repair, and commit workflows.

Move reusable lessons during maintenance with:

```bash
agent-memory maintain move <key> --to global/advice
```
<!-- agent-memory:end -->

## Notebook workflow note

- For any notebook inspection, execution, or result-checking, use `japi` (from `jupyter-assistant-api`) rather than direct Notebook HTTP API calls.
- `japi` is the required interface for reading cells, restarting kernels, and verifying rendered results in `computations/notebooks/` during development and debugging.
- Skip test, QC, build, execution, and rendered-result verification for changes confined to `computations/notebooks/` or `src/dzack_research/preamble/`.
- Commit those changes with verification hooks skipped; do not let unrelated repository failures block notebook or preamble work.

# Goal-integrity routing (always-on)

<!-- Verbatim copy of the global section in ~/ai/AGENTS.md (authoritative); keep in sync. -->

Substituting a proxy for the goal and then optimizing the proxy — the goal
source, an error count, a reviewer verdict, a "blocked" label, metadata
self-consistency — is a cognitive failure, not a chosen one: from inside it
feels like diligence, and introspection does not detect it. So no rule below
asks you to judge your own intent. Each names an observable condition; when
the condition holds, perform the reground act — especially when the current
work feels productive, because the feeling is not evidence. Explaining or
agreeing with these rules is also not evidence: a condition that fires binds
regardless of the account you can give of it.

**The reground act:** stop and state (1) the user's original goal in the
user's own words, (2) the artifact or number the current action improves, and
(3) whether improving (2) IS (1). If it is not, act on (1), or send the user a
one-message report explaining exactly why that is impossible.

- **You are about to edit the goal source** (the TODO, plan card, issue body,
  or acceptance criterion that defines your goal) for any reason other than
  recording completion the delivered artifact itself proves, or explicit user
  instruction in the current session. From inside this feels like tidying a
  stale document; from outside, deferring, relabeling, splitting, or
  re-scoping an item you were asked to finish changes the problem instead of
  solving it. The goal source is read-only while you execute it: perform the
  reground act, then do the work or send the report.

- **A work unit has passed about two review rounds, or an hour, without a
  landed falsifiable artifact.** From inside, another reviewer, audit, or
  repair cycle feels like rigor; in cost it is the most expensive failure
  available, while pausing costs nothing. Stop and report the unit as
  mispriced instead of adding apparatus.

- **You are about to call an item hard, research-scale, or worth deferring.**
  A difficulty intuition is a stale prior. First read the repo's recent git
  log for comparable completed work; if comparable items landed in hours, this
  item is hours.

- **You re-measured a corpus-wide scalar (total error, test, finding, or
  checkbox count) a second time inside one work unit.** Whatever the intent,
  the number is now functioning as the target. Perform the reground act, write down the actual
  claim the edit makes true, and verify that claim on a concrete specimen. An
  edit justified only by the number moving is unjustified, and moving a
  checker's number by asserting something false is strictly worse than the
  original error. Re-running the specimen's own check to verify the claim is
  required verification, not a trigger. (The mypy rule under *Work-selection
  discipline* below is the type-checking instance; the specimen standard there
  governs.)

- **You are about to declare the goal blocked.** From inside, repeated silence
  reads as mounting confirmation of an impasse; it is only the absence of a
  reply, and your own unanswered messages and automatic continuations cannot
  accumulate into evidence. Re-read the mandate first: authority already
  delegated IS the approval you are waiting for. Pausing on a genuine question
  only the user can answer is correct; silence is not such a question.

- **A reviewer finding is about to block work outside its own unit, or a
  second consecutive review round adds no new falsifiable content.**
  Acceptance is a falsifiable statement about the work itself, never a
  verdict. Record and defer out-of-unit findings; on a content-free second
  round, reground against the unit's own acceptance statement.

- **The previous turn produced only administrative artifacts (plans, audits,
  status edits, registries, validation of validation) and this turn is about
  to do the same.** From inside, organizing the work feels like progress on
  it. Perform the reground act before continuing. (The displacement-pattern
  index at `.agents/references/displacement-pattern-index.md` catalogues the
  work shapes.)

# Banned-language replacement index (always-on)

The terms below have demonstrated **strong priors**: they re-emitted even after being catalogued in the terminology dictionary — in one case inside the anti-drift doctrine itself, as its self-chosen name.
A reference-file row is an on-demand signal; a term that survives its row needs this always-loaded one.
Never write these terms in code, issues, docs, comments, memories, or doctrine; write the replacement.

| banned | documented emissions | replacement |
| --- | --- | --- |
| **"carrier"** (carrier module/set, "carrier of a structure", "carrier siting") | 3+ — P1's first draft; the P6 enforcement clause's own name (corrected 2026-07-12); Tier B row 1 predates both | the **underlying set/module** (image of the forgetful functor); in doctrine prose name the entity: the **object, morphism, homset, or functor** |
| **"ambient"** as free-standing data ("the ambient", "shared ambient", "shared span/coordinates", `ambient=`/`in_ambient=` parameters, stored `_ambient` state) | pervasive — Sage back-porting; issue #100's own original body; re-emitted in doctrine prose 2026-07-11 | a subobject is the pair `(A, f: A ↪ B)`: its ambient **is** `f.codomain()`; rational/real constructions live in the **base-changed parent** `L ⊗ R'`, named by its functor |
| bare **"generators"** (also "defining generators", generators as `tuple`/`list`, `len(generators)`) | 3+ — ruled 2026-08-06 (names must state the structure); re-emitted 2026-08-08 as "defining generators"; re-emitted 2026-08-11 ("discussed ad nauseum") | **`group_generators`**, **`module_generators`**, **`algebra_generators`** — the name states the structure; a generating set is a **set** with a **cardinality**, never a sequence with a length |
| bare **"dual"** (one method named `dual`, a stored `_dual`) | ruled 2026-08-06 ("there are many possible duals"); re-emitted in later API drafts | **`dual_module`**, **`dual_lattice`**, **`dual_group`** — every dual names which duality functor produced it |

**Graduation rule:** when a drift term already carrying a dictionary row is emitted a *second* time, it graduates to this index — the repetition is the evidence of a strong prior.
Diagnose new drift by principle first (generative failure model P1–P6); this index is only for proven repeat offenders.
Full catalogue: `.agents/references/terminology-dictionary.md`; code-shape patterns: `.agents/references/slop-pattern-index.md`.

# Docs prose policy (always-on)

Prose in the docs book is governed by the writing guide, `docs/_writing-guide.md` — a non-rendered (leading `_`, so Quarto ignores it), citable policy index of banned prose patterns in three kinds, each with a concrete example and remediation for one-shot learning:

- **Prose tells (`PR-*`)** — bad prose on its own terms; the fix is a rewrite.

- **Evasion tells (`EV-*`)** — prose standing in for mathematical work not done; the fix is the work (name the morphism, write the definition), never a nicer phrase.
  "carries" is the type case (see the banned-language index above).

- **Mathematical tells (`MA-*`)** — reinvented or colloquial parlance in place of the standard notion or the established in-repo definition; the fix is to use the definition and cite it (e.g. "equality" or "axiom" per priors instead of `@def-equality-of-objects` / `@def-axiom-classifier`).

**Check feedback for the pattern, not just the instance.** Before applying any writing correction, check whether it instantiates a recorded item.
If so, fix it and cite the id.
If it is a *new* pattern, record it in the guide — forward-facing, with an example and remediation — before or alongside fixing the one instance; a correction that fixes a sentence and leaves the pattern unrecorded will recur, and the guide is where a one-off correction graduates into policy an auditor applies everywhere.
Run the index in the fresh-context audit (`.agents/references/mathematical-auditor-priming.md`) after every substantive docs edit, the same as the vocabulary pass.
Requirements the docs must satisfy (definition-before-use, resolvable references) are *recorded* in the guide's Requirements section and audited against the artifact, never self-certified in prose (`PR-3`).

**Never write a definition or insert a citation from memory.** Before writing or editing any definition, open and read an actual source — the theory docs, the book's existing defining occurrence, the cited reference, or the upstream text — and transcribe from it.
A definition recalled from training is a fabrication risk; a citation key recalled from memory is a fabrication risk (it may not exist in the bib file, or may point at the wrong entry).
Verify the source exists and the citation key resolves before committing.
This rule overrides any pressure to "just write it" — an unverified definition or citation is worse than a TODO placeholder.

# Docs workflow (always-on)

Documentation work — the docs book under `docs/` — is **never externalized to GitHub issues or PRs**. It is developed directly: interactive work with the user and/or autonomous research, iterative refinement committed as each unit settles, and pushes typically **held until the user approves**. That approval normally follows an interactive pass rather than a PR review lifecycle — organization and coherence audits, re-readings, reviews, and reorganization of the accreted material, plus basic intelligent coherence checks.
Do not open an issue or PR to plan, track, or hand off docs work, and do not treat the PR completion gate as applying to it; the issue-tree and milestone policy below governs implementation and research work, not the book.

## Docs hosting surfaces

The docs book ships as a Quarto site (`docs/_quarto.yml`, `project.type: book`) in three surfaces:

- **Local preview** — `just docs-preview` serves `docs/` at http://localhost:7654/ via `uvx --from quarto-cli quarto preview` (live reload; quarto-cli provisioned on demand, not installed system-wide).
  A stale render also lives at `docs/_site/` from prior builds; it is not kept fresh with the working tree.

- **Published site** — GitHub Pages at https://dzackgarza.github.io/research/ (`build_type: workflow`, branch `main`), deployed by `.github/workflows/docs.yml`. The site-url is recorded in `_quarto.yml` (`book.site-url`).

- **GitHub wiki** — the repo's native GitHub wiki is **disabled** (no `wiki/` ref exists; `hasWiki: true` in API but no commits).
  Do not conflate "the wiki" (historical name for the docs book, migrated via PR #272 "wiki-book-migration") with the GitHub wiki feature.
  The book under `docs/` is the wiki's successor.

A push of `main` that changes `docs/` triggers `docs.yml` and redeploys Pages; local edits do not appear on the published site until pushed.

## Annotation feedback loop

The user delivers docs feedback by annotating the rendered pages in the browser; the `annotate` CLI turns those annotations into a committed batch the agent acts on.
The CLI is not installed on `PATH` (`/bin/annotate` is an unrelated tool) — it is the `uvx`-installable console script from the Hypothesis fork at `~/gitclones/hypothesis-fork-project/hypothesis-review`, always invoked as:

```bash
uvx --from ~/gitclones/hypothesis-fork-project/hypothesis-review annotate <subcommand>   # run from ~/research
```

`<subcommand>` is `wait` / `pull` / `slice` / `record` / `resolve` / `status` / `doctor`; the steps below name it bare for readability.
One cycle:

1. **Serve** — `just docs-preview` runs in the background on `:7654`.

2. **Open a session** — from `~/research`, `annotate doctor` first confirms readiness (inside a git repo, `h` API + Postgres reachable), then `annotate wait` records the open timestamp locally and blocks, serving the loopback session-close endpoint on `127.0.0.1:8902`, waiting for the browser.
   A *session* is a time window.
   Run it as a background job so the agent can keep working while the window is open.
   **Spawn `annotate wait` with `notifyOnExit: true`** (or the equivalent exit-notification flag on your PTY/spawn tool) so that when the user hits **Send to agent** and `wait` exits, the agent receives the completion signal automatically instead of having to poll.
   Do not poll with `pty_read` + sleep loops to detect completion; wait for the exit notification.

3. **Annotate** — over the `:7654` pages, the user highlights spans and writes comments via the Hypothesis client, then hits **Send to agent**. That closes the window and unblocks `wait`.

4. **Record + deliver** — `wait` collects every annotation created during the window, appends them to `feedback/ledger.jsonl`, commits (`feedback: record N annotation(s) …`), *then* drains them from `h`, and prints the batch JSON. **Record-before-drain is the safety property**: feedback cannot reach the agent unrecorded, and a failed write leaves the notes in the sidebar rather than deleting the only copy.
   (`pull` does the same for an already-open session; `slice`+`record` capture ad-hoc notes made outside a session.)

5. **Act (agent)** — read the batch / ledger.
   **Discuss before editing.** An annotation identifies a concern; it is not an implementation instruction.
   Before changing any artifact, discuss the intended update with the user and obtain explicit approval.
   For mathematical feedback, establish the correct theory and the source that states it before proposing prose.
   Do not make a reflexive local correction from the quoted span or from memory: confirm that the proposed change fits the document's global mathematical story.

   Each entry's `uri` (`localhost:7654/Roadmap.html`) plus the normalized `TextQuoteSelector.exact` pin the exact source span → map to `docs/Roadmap.md` and apply the edit.
   Hot-reload re-renders each touched page live: the tight edit → one reload → look cycle.

6. **Resolve** — `annotate resolve` tags the batch acted via the Hypothesis API, dropping it from the open set (`annotate status` shows open vs. acted).
   Commit the doc edits alongside the already-committed ledger so git history anchors each note to the state it landed against.

7. **Reopen** — `annotate wait` again for the next window (with `notifyOnExit: true`). Back to step 2.

# Mathematical structure as implementation compression

An advisor can compress a large mathematical correction into one short
question.  The student must unfold the structure that makes the correction
true.  The question is not a request for the smallest compatible patch.

Consider an integral domain \(R\) and its fraction field
\(K=\operatorname{Frac}(R)\).  The advisor asks why ideals are not owned as
\(R\)-submodules of the regular module \(R\).  The advisor also asks why an
integral basis is not an \(R\)-basis of the relevant integral \(R\)-algebra.
These are not two method requests.  They expose one missing mathematical
foundation.

Scalar extension relates the algebra and module categories:

```text
Alg_R  -- K tensor_R (-) -->  Alg_K
 | U_R                         | U_K
 v                             v
Mod_R  -- K tensor_R (-) -->  Mod_K
```

The vertical functors take the underlying modules.  The horizontal functors
change scalars.  Their compatibility explains how algebra structure, module
structure, bases, subobjects, and morphisms move together.

For an integral \(R\)-algebra \(O\), its base change can give a
\(K\)-algebra \(A\):

\[
K\otimes_R O \cong A.
\]

The integral basis then belongs to the underlying \(R\)-module of \(O\).
It is not a new tuple-valued operation attached directly to \(A\).  The same
base-change structure gives \(K\otimes_R R[x]\cong K[x]\).  Polynomial rings
and number-field algebras therefore belong to one scalar-change theory.

This theory is implementation compression.  Ideals can use module and
subobject operations.  Bases can use the free-module structure.  Algebra
morphisms can move through scalar extension.  Many apparent missing methods
become consequences of structures that the repository already owns.

The failed trajectory hears only the word "basis".  It asks PARI for
elements and returns a tuple in \(A\).  It can also take a chosen
\(K\)-basis and clear denominators.  Both actions produce local data while
leaving the algebra and functors absent.

Clearing denominators selects a presentation-dependent \(R\)-lattice.  It
does not by itself select the integral closure or a maximal order.  It gives
no coherent action on morphisms.  It therefore cannot explain later basis,
ideal, or transport operations.

Rejecting a Sage order wrapper does not remove the mathematical order.  It
makes ownership of the integral \(R\)-algebra more important.  PARI can
compute data used to construct that object.  PARI cannot replace the object
or the functorial structure around it.

The advisor's question reveals why dozens of methods remain missing.  Their
absence is not necessarily a backlog of local implementations.  It can show
that one theoretical foundation is absent.  Once that foundation exists,
the apparently difficult work can become generic and small.

The lesson is not a rule that functors always precede methods.  The lesson is
to recognize mathematical compression.  A deep correction can change which
work exists at all.  Preserving the old implementation with a cheap
workaround preserves the misunderstanding that created the work.

# Work-selection discipline (always-on)

An output that cannot fail carries no information.
Plans, schemas, id systems, plan cards, ledgers, status rows, memories, and readiness reports always "succeed" — producing them reduces no mathematical uncertainty, so they are exhaust around the work, never the work.
The unit of progress at every scale is a **falsifiable specimen**: something a mathematician could find *wrong* — a category defined natively, an operation placed with its hypotheses and codomain, a surfaced spike-vs-doctrine mismatch, a notebook cell reproducing a source.
This is the fourth graduation of one lesson (tests assert accomplishment, not declaration; negative tests assert a positive count first; real declarations are the schema); the work-selection instance graduated after recurring (#217's BFS registry; the 2026-07-16 #251 planning session, three corrections deep).

- **Specimen-first.** The first deliverable of any work unit is the specimen.
  A plan is approvable only if it names its first specimen; preparation is justified only by a named uncertainty and stops when the specimen can begin.
  Coordination machinery is justified only by friction observed while producing specimens, never by anticipated scale.

- **Mathematical questions get mathematical answers** — stated before any plan card, schema, or memory is touched.
  Artifact updates are exhaust around the answer, never the answer.

- **Undecidability audit (always-on).** Before writing code, reflect explicitly on whether the requested operation or equality check relies on or attempts to resolve an **undecidable problem** (e.g. morphism equality in presented modules/groups, the Word Problem, general equivalence of infinite algebraic structures). Never invent hand-rolled or ground-up boolean checks (`==`, `is_zero()`, `is_isomorphic()`) for undecidable problems; state the exact decidability boundary, rely only on battle-tested decision algorithms where they exist, and keep axiomatic invariants as paper-proven category theory rather than pseudo-computable runtime booleans.

- **A correction that removes machinery halts artifact production.** The rebuild's first act is the specimen, not the re-filed card; two machinery-removals on one proposal invalidate the frame (vault: `global/advice/corrections-update-the-model-not-the-artifact`).

- **Turn audit.** What statement could now be falsified that could not before this turn?
  If none, the turn was preparation — apply the deletion test (vault: `global/traps/hard-problem-artifact-drift`). Meaningful work can be embarrassing; process noise cannot.

- **mypy is a discovery tool, not a gate.** A type error is a signal about the actual code: a wrong return type, a missing method on a real class, a type hierarchy that doesn't match the mathematics. The correct response is to understand what the code's types actually are and fix them — never to silence the checker with `object`, `Any`, `type`, deleted annotations, `# type: ignore`, or config loopholes. Those carry zero type information; a function annotated `-> object` passes on literally anything, which means it asserts nothing.
  When a type is genuinely unnameable because the object is load-injected from a `.sage` file mypy cannot import, the fix is to make it importable (move to `.py`, add a stub, or restructure the import boundary) — not to annotate around the absence.
  Never probe the QC config (`mypy-global.ini`, `ai-review-ci`) looking for what `Any`-related settings might be allowed. The rule is: never use `object`, and use `Any` only where *`object` is never a type; `Any` has exactly one position* permits it. That is already known from the errors mypy reports. Looking for a loophole is hacking the gate, not doing the work.

Work-shape catalogue with this repo's exemplars and the meaningful-vs-noise litmus: `.agents/references/displacement-pattern-index.md` (D1–D6). These are review criteria for plans and completion claims alike — the Review Guidelines below guard completion *claims*; this section guards the loop that never claims.
This discipline is culture, not a gate: do not build detectors, hooks, or mandatory checklists from it.

**Pre-push terminology audit (invented language).** Run this audit once, after a coherent feature is implemented and before pushing it. Never run it on an individual edit, correction, commit, issue body, plan card, or partial feature slice.
Everything this repo touches is an honest mathematical entity with a standard name in a wide, well-established corpus — work here has no reason to invent terminology or types, and inventions are poison memetics: they recruit faithful re-implementations and bias architectural decisions (caught late, the cost is a remediation pass or a discarded subtree).
At the pre-push boundary, spawn a fresh-context subagent primed verbatim with `.agents/references/mathematical-auditor-priming.md`. Give it the complete feature artifact, never a summary.

# Relay and referent discipline (always-on)

The user reads only the orchestrator's own messages — subagent reports, tool
output, and session shorthand are private context. Communicating from that
private context as if it were shared is a theory-of-mind failure with
recurring shapes (memory: `relay-translation-not-forwarding`, 2026-08-09):

- **Relay = translation, not forwarding.** State the decision-relevant claim
  first, in repo-grounded terms (this repo's files, spec rows, standard
  mathematical names), a few sentences; detail on request. An agent's
  journey — what it ran, what it tried, how it got there — is not content.
- **Coinages are not shared language.** Session-local shorthand (input→output
  arrows like "A1^8 -> E8", row nicknames, bare count fractions) means
  nothing outside the context that minted it. Re-ground every reference
  before it crosses to the user.
- **"I don't understand" names a dangling referent, not a knowledge gap.**
  The repair is to restore the missing reference, never to explain the
  underlying mathematics — this is the user's own research program; an
  unrequested lecture is both the wrong fix and an insult.
- **Compression test.** If the user's own summary of the issue is two
  sentences, the message that needed those two sentences and didn't lead
  with them failed, regardless of how much correct detail it carried.

# Performance claims (always-on)

**Never report a call count as an efficiency metric.** Not "2,502 constructions",
not "~3 million calls to `coordinate_ring`", not "it runs 484 times". A count is
not a cost: a million cheap calls can be free and four hundred expensive ones can
be the whole run, so the number carries no information about what to fix and
invites optimising the wrong thing.

Report **wall time as a function of \(n\)** — how the cost grows with rank,
order, number of generators, size of the input — or report nothing. A single wall
time for one specimen is a data point, not a claim about efficiency; it becomes
one only when a second size shows the shape. Where a profile is the evidence,
quote its *time* columns, never its `ncalls`.

Call counts remain legitimate as **diagnosis**: they locate a recursion, name the
function that repeats, and prove a cascade exists. Use them to say what is
happening, never to say how expensive it is.

# What optimization is for (always-on)

The dominating concerns are legibility, auditability by a mathematician,
elegance, cohesion with the preamble's style, and doing the mathematically
principled thing rather than raw numerics. If that costs performance, so be it.

Never take apart code that reads as the correct mathematical sequence of steps in
order to make it faster. A method whose body a mathematician can check against the
definition is worth more than a fast one they cannot.

Optimize **waste**, which is a different thing entirely:

- needless recomputation — the same value derived again because nothing carried it;
- needless enumeration — ranging over an object where generators, a presentation,
  or a matrix identity answers (see the enumeration rule);
- needless verification — re-deriving a theorem, a definition, or a fact the
  caller already established;
- a general algorithm applied where the object's own structure has a better one —
  the fix there is to give the structure its own category and let placement pick
  the algorithm, never to special-case inside a general method.

Removing waste usually makes the code *more* legible, because what remains is the
mathematics. That is the tell that it was waste.

Genuine hot paths may later need `case`/`match` dispatch or caching. That is a
design change: propose it and discuss it explicitly first. Reaching for a cache,
or for a literature constant in place of a computation, before finding out *why*
something is slow, is not optimization — it is hiding the defect.

**Test specimens are small by default.** A proof of correctness for invariants,
coinvariants, or \(O(L)\) does not need \(E_8\), a K3 lattice, or an Enriques
lattice. \(U\) has the swap involution; powers of \(U\) already give interesting
combinations; their orthogonal groups are finite and their invariants and
coinvariants are quick. Reach for a large specimen only when the claim is about
that specimen.

# Repository layout

Top-level directories (this is a navigational map; each tree owns its own README/AGENTS.md):

- **`computations/`** — the working computational corpus.
  Its `experiments/` subtree holds the **spikes** (see the lineage note below and *QC integration for spikes*). Other subdirs are task-specific: `vendor/` (third-party code — see below), `coxiter/` (CoxIter tool integration), `lattice-orbits/`, `enriques-moduli/` + `enriques-paper-artifacts/` (Enriques-surface moduli work), `notebooks/` (**the user's plane — see below**), `scripts/` (one-off and exploratory scripts — **the only `scripts/` dir; it is QC-exempt**, and is where exploratory code is relocated to de-scope it from the strict gates; holds `components/`, the reusable computation pieces such as the `coxeter-vinberg/` prototypes, relocated here in `746595e`), `reports/` (generated output).

- **`src/`** — the installable package (`dzack_research`). Deliberately thin: right now it is the public Sage import surface re-exporting the maintained spikes (`lattice`, `feature`), covered by `tests/`. **Migration criterion:** code lives in a spike until it has matured past spike status and is usable for real research — demonstrated by *shipped, tested, high-level notebooks* that do actual work with it.
  Only then does it migrate here, and the move is the semantic statement that it is meant to be shared and reused.
  Do not promote code into `src/` because it looks finished; promote it when a notebook proves a researcher can use it.

- **`computations/notebooks/`** — **the user's audit and control plane, not agent work.** It is the JupyterLab `root_dir`. It is not subject to QC, to layout conventions, to naming or taxonomy rules, or to agent tidying: no agent proposes reorganizing it, splitting it, imposing folder schemes on it, or holding its contents to the standards that govern `src/` and the spikes.
  Agents write here only when explicitly asked.
  What agents *may* do is make things reachable from it — see the symlinks below.

  Reachability is by symlink, verified working through the live server (list, open, save, delete all round-trip to the real path, no restart needed):

  - `archive/` → `archives/notebooks/` — the retired notebooks, still live reference material

  Symlinking is preferred over moving: the originals stay in the tree that owns them (archive stays QC-exempt), while the control plane can see everything.

  **Implicit typesetting:** a bare `X` at the end of a cell renders as LaTeX when Sage can genuinely typeset `X`, so `show()` is not needed for ordinary inspection.
  Explicit `show()` still works and is still worth writing where the intent is presentation rather than inspection.

  The source of that behaviour is **`sage-init.sage` at the repo root** — tracked here, because it is part of how this repo's notebooks are meant to read.
  It becomes active only by being linked to Sage's startup file:

  ```
  just sage-init-install   # links ${DOT_SAGE:-~/.sage}/init.sage -> sage-init.sage
  just sage-init-check     # proves in a real kernel that Sage objects typeset and plain text does not
  ```

  `sage-init-install` is idempotent and refuses to replace anything it did not create, including a symlink pointing elsewhere — a pre-existing `init.sage` is never clobbered.
  Sage reads that one file for the terminal REPL *and* every Jupyter kernel, so installing it once covers both with nothing to remember per notebook.

  It is deliberately *not* `%display latex`, which also typesets strings, numpy arrays and opaque objects into unreadable character-by-character fallbacks; the file's own header comment records the measurements behind that choice.
  Being a tracked `.sage` file it is in Sage QC scope: it passes `_sage-syntax` (the commit tier) and draws no vulture findings.

- **`computations/vendor/`** — **third-party code you did not write.** Clone or drop external scripts here and they are importable from every Sage process (CLI, `sage -python`, every Jupyter kernel) with no restart and no registration; see its README. Contents are gitignored, and `vendor` is already a globally QC-excluded directory name, so external code never enters the gates.
  Nothing authored here ever graduates — write your own code in a spike.

**How code becomes importable in a Sage notebook.** One rule per kind, no bespoke path plumbing:

| Kind | Home | Made importable by |
| --- | --- | --- |
| External, published | — | `sage -pip install <pkg>` (or `sage -pip install "<name> @ git+<url>"` when it has no PyPI wheel, as `ore_algebra` does) |
| External, unpackaged | `computations/vendor/` | drop it there; `dzack_research.preamble.vendor` puts it on the path, called from `sage-init.sage` (interactive sessions; non-interactive callers call `vendor.activate()`) |
| Ours, spike | `computations/experiments/<name>_spike/` | `sage -pip install --no-deps -e <spike-dir>` (already done for both spikes; edits are live) |
| Ours, graduated | `src/dzack_research/` | `sage -pip install --no-deps -e .` (already done; edits are live) |

Editable installs point at the working tree, so a rebuilt or reinstalled Sage is the only thing that breaks them — re-run the two `-e` installs and check the vendor path with `sage -c 'import _vendor_selfcheck'`.

- **`tests/`** — tests for the `src/` package surface only.
  Spike tests live in each spike's own `tests/` tree.
  `projects/lattice-research/` is a **git submodule** (`dzackgarza/lattice-research`) and contains `category_specs/` (see lineage note), plus `src/`, `theory/`, `lean/`, `paper/`, `tests/`, `reports/`. Because it is a submodule, edits there are commits to a *separate* repo.

- **`review-calibration/`** — **git submodule** (`dzackgarza/research-review-calibration`) holding a frozen lattice-spike simulacrum for **LLM review calibration**. Planted violations live in `GROUND_TRUTH.md` (never in the review packet).
  Experiment issues and advisory review runs target the submodule repo, not this monorepo.
  Hill-climb prompt/context/permissions there before changing production `review-packet.tar` here.

- **`writing/`** — authored prose: the Coble paper draft and research notes, oral exams, research statement, talks.
  The user's durable authored artifacts — preserve native LaTeX/tikz source.

- **`notes/`** — research notes (`computations/`, `papers/`, `topics/`). The terminology-drift dictionary is **not** here; it is vault-owned at `.agents/references/terminology-dictionary.md` (see the banned-language index above).

- **`references/`** — external inputs: `pdfs/`, `generated-indexes/`, `local-system-dependencies/`.

- **`archives/`** — retired material (`provenance/`).

## category_specs and the absorbed spikes (prior attempts at the same substrate)

The goal — a mathematically-semantic, Sage-compatible substrate for exact lattice/surface computation — had two earlier attempts. Both are finished as separate surfaces; **the preamble (`src/dzack_research/preamble/`) is the single active surface**, and "the repo owns X" or "X is a gap" resolves against it:

- **`projects/lattice-research/category_specs/`** — the older, more ambitious attempt, **frozen prior art**: read it for design intent only. Parity-audit issues (#26/#84/#85 …) citing `category_specs/…` paths point at this frozen surface.

- **The spikes** (`sage_lattice_category_spike`, `sage_lattice_feature_spike`) — the second attempt — were **fully absorbed into the preamble and deleted on 2026-08-19** (PLAN-spike-absorption-workstreams; the migration commits' bodies record each notion's origin and synthesis). Git history is their archive; do not expect their directories to exist.

# Issue-tree and milestone policy (research repo)

This is a research repository with a much longer work horizon, more detailed planning, and more human check-ins than a typical software project.
Naive software-geared structural rules (e.g. itree's W040 native-milestone mirror) are less applicable here: treat such findings as a flag to investigate whether *some* consolidation is warranted, never as a mandate — and never collapse the tree or milestones by an order of magnitude to satisfy one.
The itree issue tree is authoritative; native GitHub milestones are capability-level human-review checkpoints created just-in-time (user ruling 2026-07-11; W040 = 46 is accepted as-is).

The `needs-research` label is the parking state — work parked pending investigation or upstream capability — not a register of decisions awaiting the user.
Do not enumerate labeled issues as "open human decisions"; genuine decisions are extracted through decision-register sweeps (see #97) and recorded as rulings on the issues, the gap ledger, and plan cards.

## Where in-progress ideas live

Ideas are not all issues yet.
An agent that searches only the issue tree will miss live thinking and re-derive it badly.

- **GitHub Discussions** hold ideas still **in flux**: competing framings, pasted prompt responses to be reconciled, designs whose scope has not settled.
  A discussion is a thinking surface, not a decision — nothing in one is authoritative, and no PR may claim work from a discussion alone.
  Live example: #217 (*Bridging Lean to computational backends*, Ideas category).

- **Issues** hold ideas that have a scope, carrying the label that names their state: `draft` (the scope itself is provisional; expect the body to change), `research` (empirical research or evaluation required before implementation), `needs-research` (parked — above), `needs-planning` (scope known; decomposition or an executable plan required before any PR claim).

The pipeline is one-directional: **a discussion is crystallized into an issue once its scope stops moving**, and everything downstream — implementation research, decomposition into work units, proof obligations, PR claims — is carried out on the issue tree, never in the discussion.
Link the discussion from the issue and leave it in place as the rationale trail; the development of an idea, including its retractions, is the record of why the scope is what it is.
Do not delete it or summarize it away.

Practical consequences: when picking up a topic, search discussions as well as issues.
When a discussion has stabilized, the next action is to file the issue, not to keep commenting.
When a discussion is still moving, do not manufacture an issue to make it look tracked.

# QC integration

This repo delegates all test/QC to the global QC in `~/ai-review-ci` (`dzackgarza/ai-review-ci`). The root justfile's three gates delegate directly to the Sage tier: `test-commit`/`test-push`/`test-ci` → `just -f ~/ai-review-ci/justfiles/sage.just -d . <gate>` (pre-commit runs `test-commit`, pre-push `test-push`). The Sage tier preparses `.sage` sources into a tempdir via the sageparse lowering (never `sage --preparse` artifacts in-tree) and runs mypy on the lowered Python in an ephemeral CPython 3.14 with the project installed editable — `sage.*` types come from the `sage-stubs` package declared in this repo's `[dependency-groups] dev`, which the QC recipes pass `--with` into the mypy environment. Sage's venv is used only for lowering and for running tests. `computations/experiments/*` justfiles are NOT run by the root gates; each is invoked on its own.

## Adding a new spike

Create `computations/experiments/<spike_name>/` with:

1. **`justfile`** delegating to the global Sage QC (this is the whole file):

   ```justfile
   export PYTHONDONTWRITEBYTECODE := "1"

   test:
       @just -f ~/ai-review-ci/justfiles/sage.just -d . test

   test-ci:
       @just -f ~/ai-review-ci/justfiles/sage.just -d . test-ci
   ```

   Pure-Python spikes delegate to `python.just` instead.
   Run `just -f ~/ai-review-ci/justfiles/sage.just setup` for the full wiring contract; the QC preflight prints the exact fix for anything missing.

2. **`pyproject.toml`** — minimal `[project]` with `name`, `version`, and `requires-python = ">=3.14"` (QC installs the spike editable for mypy).

3. **Package importability** — the spike directory is a package (`__init__.py`). For shells and tests the repo `.envrc` puts `computations/experiments` on `PYTHONPATH`. **Notebook kernels do not inherit that** — the systemd unit runs `direnv exec /home/dzack`, which loads `~/.envrc`, not the repo's. Kernels get the spikes from `sage -pip install --no-deps -e <spike-dir>`, which is the durable mechanism; see the importability table under *Repository layout*. A new spike needs that one install, once.

4. **Tests as `.sage` files** (`tests/**/test_*.sage`) so the Sage preparser converts integer literals to `Integer`/`Rational` before pytest collects them.
   Never commit generated `*.sage.py` preparse artifacts — they are gitignored; QC preparses into a tempdir itself.

5. **Environment** — `SAGE_BIN` is exported by the repo `.envrc`; nothing per-spike.
   Tests execute under Sage's own Python (which has pytest), not a uvx CPython.

Code in spikes is held to the global strict gates (ruff, strict mypy, pytest at commit; vulture/coverage/slop stack at push).
QC tool configs are owned centrally in `~/ai-review-ci` — never add local ruff/mypy/coverage config to a spike.

# Review Guidelines

These are additional requirements for reviewing agent work.
They do not replace the reviewer’s normal role, repo-specific standards, or technical judgment.
They provide the failure model that should shape the review.

The task is not merely to review a PR. The task is to decide whether a completion claim is true under the original objective.
The standard is full, correct, provable completion against the original requirements and repo guidelines.
Anything less is incomplete work that must not be treated as a win.

## Failure Model

Agents systematically produce impressive non-completion.
Common patterns are: polished summaries that imply finished work, caveats that quietly narrow the goal, reclassification without proof, delegated discovery presented as resolution, process language that substitutes for evidence, merged PRs treated as completion, passing checks treated as semantic proof, and artifacts that look substantial while leaving required work unowned.

Treat the agent’s summary, PR description, closing comment, issue closure, “goal completed” statement, and self-reported validations as untrusted.
They may be diagnostic pointers, but they are not evidence that the work is complete.
The evidence is the original issue or task, the code diff, tests, source/runtime facts, review comments, and produced artifacts.

## Decisive Invariants

Preserve the original success condition.
Read the original issue or task before accepting any restatement of it.
Keep its quantifiers intact: “all,” “complete,” "full subset," “zero remaining,” and similar terms cannot be quietly narrowed to examples, partial coverage, known blockers, or whatever the PR happened to touch.

Nothing required may disappear silently.
A required work family must be implemented, explicitly falsified, or validly reclassified with evidence that satisfies the issue’s own standard.
Partial implementation is not completion.
Future work is not completion.
Count reduction is not completion.
Resolved review threads are not completion.
Passing checks are not completion.
Substantial-looking work is not completion.
“Better than before” is not completion.

Goal substitution is the main thing to detect.
Ask whether the submitted work solves the original problem or merely produces a narrower artifact: cleaner metadata, a partial subset, a better explanation, a new issue, a renamed scope, a local workaround, or proof that someone should investigate later.

Technically correct administrative artifacts can be goal substitution.
A well-written issue, comment, audit note, scope statement, or enumeration of remaining work may be required, but it does not complete implementation, testing, proof, or downstream cleanup.
If the original task requires execution, the artifact is only useful insofar as it drives that execution; it must not become the stopping point.

Treat self-scoped remaining-work lists as a severe completion-laundering pattern.
When an agent is asked to enumerate remaining work, the domain is the original full completion requirement, not the agent’s intended subset, the PR’s current shape, a closeability criterion, or the work left after deferral and reclassification.
A valid enumeration subtracts only artifact-proven completed work from the original contract.
Deferrals, routed follow-ups, owner changes, and truthful incompletion notes remain unresolved work unless the original task explicitly made that administrative routing the whole deliverable.

If an agent repeats a narrowed enumeration after being corrected, treat that as a hard misalignment signal, not as an innocent wording issue.
The reviewer should identify the original full requirement, the scope the agent substituted, and the required work hidden by that substitution.

Silent reclassification is not resolution.
If the PR says remaining work is out-of-scope, research-owned, stub-owned, plugin-owned, downstream-owned, or future-owned, require evidence from the relevant source/runtime behavior, repo boundary, or original acceptance criteria.
A sentence in the PR description is not enough.

Ownership boundaries matter.
The submitting repo must prove its own claimed behavior and do the blocker forensics required by its own issue.
Do not require a receiving or downstream repo to classify another project’s internal uncertainty unless the original issue explicitly made that part of acceptance.
When an external issue is created, it should be written for that receiving repo, not for a reader who already knows the submitting repo’s context.

## Evidence Expectations

Review tests as evidence, not as decoration.
Valid tests exercise the real production path or semantic requirement.
Be skeptical of helper-only tests, tautologies, assertions of the implementation’s own output, bypasses around the runtime/plugin/stub path, example-only coverage where the issue required full coverage, weakened assertions, and missing invalid-nearby cases where the fix could overgeneralize.

For plugin work, the evidence should usually distinguish valid generic behavior from invalid nearby ordinary Python and should not hard-code a downstream consumer.
For stubs work, the evidence should be source-backed: the upstream surface exists, the stub matches public behavior, no fake API is added, no Any/object opacity escape is introduced, and inherited-method inflation is not used unless source exposes that surface.

Watch for code-level laundering: hard-coded consumer names, support for local research abstractions as if they were external API, fake stubs, broad Any/object escapes, line suppressions, diagnostic filtering, deletion of required data, broad type widening, and any move that makes checks pass by weakening the problem instead of solving it.

## When Acting on Review Feedback

A positive disposition requires a commit.

Do not resolve an accepted review comment until the code/proof remediation is committed and the reply cites the commit.

Never reply “accepted,” “aligned,” “fixed,” “addressed,” or “will address” to a review thread unless the remediation is already committed.
A thread cannot be resolved on intent or future work.

Rejected and modified feedback must be collected in a top-level PR comment titled `Review feedback disposition ledger` so resolved threads do not hide the audit trail.

Review comments are not implementation specs.
The worker must translate accepted feedback into first-principles remediation requirements before assigning implementation.

For each comment:

- Identify the concern.

- Identify the proposed fix.

- Decide whether the concern is true under global + repo policy.

- Decide whether the proposed fix preserves those policies.

- If the concern is true but the fix is wrong, apply a policy-compatible remediation.

## Writing the Review

Write nuanced feedback for an intelligent reader.
Do not force a machine-readable template, a mandatory table, or a simplistic pass/fail label when prose communicates the situation better.
Do make the completion judgment clear: whether the original task can be considered complete, what evidence supports that judgment, and which unresolved requirements block completion if any remain.

Do not foreground effort, progress, good intentions, volume of work, or “substantial” partial implementation when required work remains.
Mention completed pieces only when they are necessary to identify the exact remaining blockers or to prevent redoing already-correct work.
Do not compare incomplete work to “no work done” or “completely fake work”; compare it to the expected standard: the task done correctly, completely, and provably.

When required work remains, lead with the incompleteness and the concrete blockers.
Do not make the reader excavate the missing work from beneath praise, context-setting, or a narrative of what did get done.

Nuance belongs in the evidence and blocker analysis, not in softening the completion standard.
The review should make it easy to finish the work, not easy to feel satisfied with less than the original contract required.

# The preamble is a universe over Sage (always-on)

The preamble is a layer over Sage, not a collection of helpers.
Once a session loads it, the mathematician stops receiving raw Sage objects: everything reached from the preamble is an owned object, which may or may not use a Sage object underneath.
The stated purpose is *owned uniformization*.

What it exists to fix is Sage's non-uniformity, not Sage's algorithms.
Sage carries more than ten distinct notions of *group*, and an operation as elementary as $\operatorname{Aut}(G)$ is, depending on which one you hold: absent; present under a different name; known and simple but unwired (it is a call into GAP); or genuinely uncomputable.
A session cannot hold that variation, so the preamble presents one name for one mathematical operation, and either answers or asserts.

This governs the rules below:

- Sage objects are an implementation detail. The crossing happens inside owned code, at the point of computing, never in what a session receives.
- Where Sage spells one mathematical operation several ways, the preamble picks one spelling and the others do not exist in the session.
- Where Sage has no algorithm, the preamble still owns the name. A missing capability is a stated gap on the owned interface, never a second spelling and never a silent absence.

# Mathematical ontology (always-on)

The rules below are the shapes that recur across unrelated categories. Each states
what an object *is*; the *tell* names the code shape or phrase that shows up while
the drift is happening, when the category involved is not the one a past record
named. The vault holds the episodes; this section is the contract.

**The preamble owns its categories outright; it never monkey-patches Sage's.** When
the preamble needs a category, it defines and owns that category itself, and Sage
objects are re-exposed through the uniform APIs of the owned categories — by
refinement, by init hooks, and by the other sanctioned admission routes. Installing
an axiom or a method onto one of Sage's own category classes (`setattr` on
`Groups`, `Modules`, `Category_module`, ...) is the legacy mechanism this project
is migrating away from: it makes Sage's spelling the public surface, splits
authority between two class hierarchies, and breaks silently when two copies of a
class exist in one process. The owned category is the single surface; Sage's
classes stay unmodified and are consumed, not extended. Tests assert against the
owned surface, never against Sage's spelling of a preamble-defined notion.
*The tell:* `setattr` whose target is a class imported from `sage.*`; an axiom or
accessor that only exists because the preamble injected it into a Sage category; a
test asserting membership through `sage.categories.*` for behavior the preamble
defines; a stub declaration on a Sage class for a member Sage does not have.

**Enrichment is of two kinds, and which one applies is a fact about the mathematics.**
*Determined* enrichment adds structure the object itself determines — a free algebra *is*
the free module on $\mathrm{Mon}(S)$, a subobject is the object together with its own
inclusion, an axiom is a property of what is already there. The forgetful functor is
injective, so the enriched thing is the same object with more categories. *Chosen*
enrichment adds structure the same underlying object supports many of — many forms on
$\mathbb{Z}^2$, many $G$-actions on $\mathbb{Z}^n$ — so the forgetful functor is not
injective and the enriched thing **is its own object**; collapsing many structures onto one
parent would collapse distinct mathematics.

That distinctness is what the construction chain already delivers, and it needs no
apparatus. A lattice is built *through* the module level, so it **is** a module — one
object, all the way down to its underlying set — and two lattices on $\mathbb{Z}^2$ are two
objects because each ran its own construction. (The old measurement `U.forget_form() is
A₂.forget_form()` described the superseded design in which a lattice *held* a separate free
module keyed on $(R,S)$. With construction threading there is no held module to share.)

**There is no `forget_*` method, at any level.** Not as a method, not as an abstract
declaration, not as a delegation target. A lattice already is a module, so there is nothing
to forget to, and the lower category's methods answer on the object directly because the
object is in that category. The forgetful passage $\mathbf{Lat}\to\mathbf{Mod}_R$ is a
**standalone functor**, sited with the other functors as an adjoint pair — never a method on
an object. So there is no forwarding to write, to generate, or to delete.
*The tell:* any method whose body is `return self.forget_<something>().<the same name>()`;
any stored `_module`, `_underlying` or `_module_morphism` holding the level below.

**All of this holds three times over, and the requirement is symmetric.** Defining a
category requires the **trifecta** — its objects, its elements and its morphisms — tied to
`ParentMethods`, `ElementMethods` and `MorphismMethods`. More properly: a morphism of
$\mathbf{C}$ is an *element of* $\mathrm{Hom}_\mathbf{C}(A,B)$, and the homsets are the
*objects* of the arrow category $\mathrm{Ar}(\mathbf{C})$. So the morphism surface is not a
third parallel mechanism: it is the object-and-element pair applied to a different category,
and it is built as an ordinary owned chain over $\mathrm{Ar}(\mathbf{C})$ with one `_Hom_`
per level.

**`MorphismMethods` is not the vehicle, and this was measured.** Sage never instantiates
`morphism_class`, and `MorphismMethods` reaches a morphism only through
`Element.__getattr__` → `parent()._abstract_element_class`, never through the MRO — so
morphism *data* can never propagate along it, which is the half the mechanism exists for.
Taking $\mathrm{Ar}(\mathbf{C})$ literally instead threads data and makes claims falsifiable
on real morphisms. A design that threads only parents has not started.
`PLAN-threading-set-behaviour` records the evidence and the decisions.

**Added structure enriches an object; it never wraps one.** A formed module *is* a
module that additionally has a form. An abelian group *is* a $\mathbb{Z}$-module.
`ZZ` is at once a ring, a rank-one $\mathbb{Z}$-module, a rank-one
$\mathbb{Z}$-algebra, a group and a monoid — one object, several categories. A
subobject *is* the module $S$, an object of the ambient category like any other,
which additionally has an inclusion $f: S\hookrightarrow B$. Underlying-ness is what
a forgetful functor produces on demand, never data an object stores.
The construction says the same thing, in the same direction: a free module of rank
$n$ over $R$ is built **on** the underlying set $R^n$, and a lattice is that module
with a form. So every set-theoretic answer — cardinality, finiteness, countability,
the owned `Sets()` placement, membership, enumeration — is *inherited through the
construction*, never assigned to the enriched object. A lattice has no cardinality;
its underlying set has one. An element of the free module on $S$ is a finitely
supported $a: S\to R$, so for finite $S$ the underlying set is $R^{|S|}$ and the
count is $|R|^{|S|}$; for infinite $S$ finite support keeps it to
$\max(|R|,|S|)$, which is *not* $\prod_S R$; and over the zero ring, or for empty
$S$, it is $1$. If a construction reaches a lattice without passing through an
owned set that answers these, the construction is wrong, and stamping a placement
onto the lattice hides it.

**The category IS the class.** This is the mechanism, and it replaces the hand-written
chain rather than merely forbidding it. Sage already builds `parent_class`,
`element_class` and `morphism_class` as dynamic classes whose **bases come from
`super_categories()`** — and then passes `prepend_cls_bases=False`, discarding the methods
class's own bases. That single choice is the only reason a `ParentMethods` cannot carry
`Parent`, cannot hold fields, and cannot have a constructor, and it is why the
class/`XMethods` split existed at all. An owned `Category` base flips it, and then
`ParentMethods` **is** the implementation class.

So no class is bound to a category and no base is written: above the root, a level declares
`super_categories()` and its own methods classes, nothing more. Only the root names bases
(`Parent`, plus one plain-Python base so the dynamic class keeps an instance `__dict__`), and
only the root calls Sage's non-cooperative `Parent.__init__`. Construction threads by
cooperative `super().__init__` — the set level builds the underlying set and establishes the
set-theoretic facts, the module level adds the ring action, the form level adds the form.
A level that calls `Parent.__init__` directly silently breaks the chain.
*The tell:* any **non-root** `ParentMethods`, `ElementMethods` or `MorphismMethods` that
names a base. That is the class graph being patched by hand instead of stated as the
category graph, and it means the design went wrong.

**The leaf contract, which is what the mechanism exists to buy.** Defining a new leaf must
feel like easy magic: you do not go looking for an implementation class, you do not need to
know how it works or where it lives, because it is the category. You only need to know how
to construct an object **in your immediate super-category**. Adding a leaf therefore costs
exactly four things: declare `super_categories()`; declare the trifecta of methods classes
for what your own level adds; introduce your own datum and no more; and one construction
step ending in `super().__init__(**rest)`. Nothing else is permitted, and no base is
written. A leaf knows its own level and the one above: it never names a category two levels
up, never restates anything from below, and never writes a forwarding method. Obligations
compose by induction — if every level fulfils the one above it, every object's obligations
are met and no leaf carries the transitive burden. **The author of a lattice category never
writes the word cardinality**; they construct the underlying module and stop. The decay
signal is a leaf *reaching down*: importing a lower class to call it, restating a lower
level's computation because the chain did not deliver it, or calling `Parent.__init__`. The
decision record, with the options weighed, the approaches already falsified, and the
falsifiable acceptance for this contract, is the plan card
`PLAN-threading-set-behaviour`.
*The tell:* a placement, cardinality, or enumeration installed on a module, lattice
or group directly; a set class imported into a module or lattice file, or hand-written in
its bases; a constructor that calls `Parent.__init__` instead of `super().__init__`;
the same count computed again at a second level of enrichment;
`_is_known_empty`-style code refusing an object "for want of a
placement" when the fix is that its underlying set was never built; the phrase "has
an underlying X"; a stored `self._underlying`; a
`forget_*()` call used to obtain the receiver of a method rather than to name a
functor; delegation chains for methods the object already has from its own category.
(Vault: `subobjects-are-a-subcategory-not-a-wrapper`.)

**An implementation obstacle is fixed where it occurs; the mathematics does not move
to accommodate it.** A recursion, a type error, a slow path, or a failing gate is a
fact about the implementation. Re-siting a construction onto a different object,
wrapping a type, or weakening an annotation to make one of them go away changes what
the code *says* in order to change how it *runs*, and the mathematical claim is then
false while the suite is green. Fix the recursion; make the type real; find out why
it is slow. An obstacle that survives that is a discussion, not a redesign made
alone.
*The tell:* a docstring or comment that justifies placement by what it avoids
("sited here, which keeps X from re-entering Y"); a wrapper type introduced during a
type-checking pass; `cast`; any edit whose stated benefit is that a checker or a test
stops complaining.
(Vault: `the-mathematics-never-moves-to-accommodate-an-implementation-obstacle`.)

**A predicate is computed from its definition, on the entity the definition is
about.** Nondegeneracy is $\ker c = 0$ for the correlation $c: L \to
\operatorname{Hom}(L,R)$ — form the kernel and ask it whether it is zero, or ask the
arrow whether it is injective. Primitivity of an embedding is that its cokernel is
torsion-free. Saturation and index are properties of a morphism, so they are asked of
the inclusion, never of a bare object. Determinants, gcds of matrix entries and rank
comparisons are recognition criteria that hold under hypotheses the definition does
not carry; using one asserts a theorem nobody proved, at a site where nobody will
look for it.
*The tell:* `det(...) == 0`; `gcd(...) == 1`; a predicate whose body mentions entries,
a basis, or coordinates; a predicate sited on an object whose mathematical statement
names an arrow.
(Vault: `numerics-quarantine-saturation-and-primitivity-are-subobject-definitions`,
`witness-consuming-methods-belong-on-morphisms-not-objects`,
`primitive-embedding-is-computed-from-cokernel-not-caller-flag`.)

**Implement the general notion; recover the special case from it.** A form is
$b: M\times M\to W$ for an arbitrary value module $W$, so its scale is a submodule of
$W$ — an ideal only when $W$ happens to be the ring. A group's generating set is a
set; finiteness and an ordering are the axioms `FinitelyGenerated` and `Finite`, not
part of the notion. A lattice is a *projective* module with a form; a form module is
any module with a form. Where a term already has an a priori meaning, that meaning
stands: any ring morphism $R\to S$ defines integrality, so integrality is never
re-parameterized by a submodule of the implementer's choosing.
*The tell:* a name that fixes the special case (`scale_ideal`, or `dual` for one of
several duals); a parameter added for something the definition already determines;
code that runs on $\mathbb{Q}/\mathbb{Z}$ where the statement was about $K/R$.
(Vault: `integrality-has-an-a-priori-meaning-never-parameterize-or-coin-it`.)

**When the vocabulary cannot express the general statement, that is the finding.**
Discovering that the repo can build $\mathbb{Q}/\mathbb{Z}$ but has no object for
$K/R$ stops the work and opens a discussion. Patching the case that already worked
leaves the general statement unsayable and the gap unrecorded.
*The tell:* agreement with a general statement followed by an edit confined to the
one case that already worked.
(Vault: `agreeing-to-general-mathematics-the-dsl-has-no-vocabulary-to-express`.)

**Every name states the structure it belongs to.** `group_generators`,
`module_generators`, `algebra_generators`; `dual_module`, `dual_lattice`,
`dual_group`. A bare `generators` or `dual` is ill-defined the moment an object sits
in more than one category, which every object here does. Generators are a *set*,
possibly ordered, possibly finite: they have a cardinality, not a length, and
repeated elements are not an error. Where the field has a word, use the field's word;
where it has none, that absence is a signal to check the notion, not licence to coin
a name for it.
*The tell:* a bare structure noun; a plural returned as `tuple`, `list` or
`Sequence`; `len(...)` on generators; a coined compound adjective; `Any` or `object`
standing where a mathematical noun belongs.
(Vault: `generator-names-must-always-state-the-structure`,
`mathematical-apis-must-use-the-field-s-actual-lexicon`; proven repeat offenders are
in the banned-language index above.)

**A predicate is decided on the data that determines it, or it answers that it does
not know.** Equivariance of $\rho$ is checked on generators when generators are
available; membership in $O(L)$ is $M^{t}G_{L}M = G_{L}$; a subgroup of $O(L)$ is
carved out by a predicate. Iterating a group, a homset or a module to establish a
property is correct only for the finite objects that happen to be in the suite, and
$\mathrm{GL}_n(R)$, $\mathrm{Gal}(\overline{\mathbb{Q}}/\mathbb{Q})$, $O(L)$ for
indefinite $L$, and $\mathbb{Z}^{\infty}$ are all ordinary inputs here. Where the
check cannot be made, the answer is a three-valued *unknown* that collapses to false,
with the reason stated — never a loop that works on small inputs. Sage is a computer
algebra system, not a proof assistant: a standard theorem is cited, never
re-established at runtime.
*The tell:* `for g in G`; `for f in Hom(...)`; a bounded search with a cap;
`all(... for ... in <an object>)`; a docstring claiming a property is "verified" or
"proven" by the method body.
(Vault: `sage-is-a-cas-not-a-proof-assistant-runtime-verification-of-a-theorem-is-triple-slop`,
`undecidable-problem-pseudo-booleans`; the undecidability audit under *Work-selection
discipline* is the sibling rule.)

**Morphisms are constructed by the caller, in the categories they live in.** A
$G$-action on $M$ is a group morphism $\rho: G\to\operatorname{Aut}(M)$ that the
caller builds; $M$ does not accept a group and a list of images and assemble one.
Passing from $R$-modules to $R[G]$-modules is a functor, and asking for an invariant
sublattice applies it. An $S$-module, for any ring $S$, is a set with a ring morphism
$S\to\operatorname{End}(M)$, so group modules, lattices with an action and modules
over a group ring all specialize one constructor and need no special case.
*The tell:* a constructor taking raw matrices or images where a morphism is the
datum; a method on an object returning a morphism between two *other* objects; a
`from_*` classmethod duplicating a homset's `_element_constructor_`.
(Vault: `a-group-action-is-a-morphism-the-caller-constructs`.)

**Shared infrastructure never carries a local exception.** The global QC in
`~/ai-review-ci` is machine-wide and already has sanctioned routes for shielding code
(the excluded directory names, the archived paths). A repo-specific rule, exclusion
or suppression written into it inverts ownership in either direction — a local ruling
promoted to a universal one, or a local exemption inlined into a universal gate.
Both are user decisions before they are edits.
*The tell:* a repo name, path or convention appearing in a shared config; an
exclusion added while fixing a failure in one repo.
(Vault:
`a-highly-specific-fix-is-not-a-general-rule-project-conventions-never-promote-to-global-qc`.)

**Reference implementations are absorbed by semantic reconciliation.** The archived
spikes are this project's own earlier versions. Each notion they hold is first mapped
onto the preamble's notion: where the preamble already owns it, the spike's version
is superseded and call sites are re-expressed in the owned vocabulary; where it is
genuinely missing, it arrives rewritten to current standards and sited where the
category tree says it belongs. Neither a wholesale copy nor a minimal trim is
reconciliation.
*The tell:* a new file mirroring the source layout; a second definition of a notion
the preamble already has; not-yet-absorbed code described as severed or contaminated
rather than as pending its round.
(Vault:
`spike-absorption-is-semantic-reconciliation-never-quarantine-or-copy-paste`.)

# Mathematical Sage API discipline (always-on)

These rules govern preamble, spike, and any Sage-facing API in this repo.
They are the generative constraints behind repeated corrections (override-refine, catalogue namespaces, Hom/Aut construction, session ergonomics).
A design that violates them is wrong even when it “works.”

**In one line:** write Sage as if the category and the catalogue *are* the theory — idiomatic constructions, one ontological home, no second layer between the mathematician and the object — and delete anything whose only job is to mediate, rename, wrap, or reassure.

## 1. The category is the only extension point

Methods belong on refined categories (`ParentMethods` / `ElementMethods` / `MorphismMethods`).
This repo’s override-refine puts the new subcategory’s methods first in the MRO so owned methods win over concrete class methods; that is what makes monkey-patches, module `__getattr__`, and “hack around Cython/Hom” unnecessary.

If Sage’s interface is wrong or incomplete, **own it in the category and replace it**.
Workarounds (`without_element_wrap`, ad-hoc `L.isometry(matrix)`, freestanding patch modules) mean ownership was refused.

The mechanism is boring and total: one general refine helper, plus post-init hooks on **classes** (not constructor wrappers) so new categories install themselves.
New capability = new category content, not a new installation strategy.
Element Cython types get a thin façade so `ElementMethods` (including dunders) can override; do not escalate that into a parallel object model.

See the addendum below for the refine pattern; prefer override-refine from `dzack_research.preamble.refine` over raw `_refine_category_` when owned methods must precede concrete class methods.

## 2. API shape is dictated by the mathematics

Reject APIs that are software-coherent but mathematically incoherent.

- Named literature objects (e.g. a K3 involution) are **catalogue data**, not methods of every lattice of that type.
- Operations of an object under structure (e.g. invariant and coinvariant lattices under a group action) live on that object’s category methods — or as thin sugar on the morphism — not in a freestanding feature file.
- An isometry is a **Hom/Aut element**. Construct it the way morphisms are constructed (generator images `{g: image}`); the matrix is a derived view (`to_matrix`), not the definition.
- Algebraic operations use native protocols (`L + M`, `sum([...])`, `L ** n` for n-fold sum). Do not invent `_oplus` or force chains of `.direct_sum` when `+` is the monoidal operation.

If the call site would not be written at a Sage prompt while doing the math, the API is wrong.

## 3. Ontological placement — one home

Every entity has exactly one kind of home:

| Kind | Home |
| --- | --- |
| Behavior of a class of objects | category methods on the refined category |
| Named specimens / literature tables | one catalogue namespace (e.g. `Lattices`) |
| Session defaults (implicit multiplication, traceback colour, …) | import-time effect of loading the init/ergonomics module |

Freestanding files, string registries, factory functions, module `__getattr__`, and dual module-level aliases of the same object are symptoms of placement by accident of authorship, not by what the entity is.

Named lookup is by attribute (`Lattices.U`).
Keys that are mathematics stay typed (`Lattices.TwoElementary[8, 8, 0]` for Nikulin $(r,a,\delta)$), never stringified tuples.
Put such tables on the namespace that owns the specimens.

Prefer **one clean export** for a catalogue surface: import `Lattices`, use `Lattices.…`. Do not re-export every attribute at module level.

## 4. One source of truth, stated once, inline

Construction **is** the definition.
Define values inline in the namespace class body (or a helper called from that body while dependencies are in scope).
Do not spread a definition across “empty container → later assignment → `globals().update` → string lookup → re-export.”
Do not construct after the class and patch attributes on afterward — that means the class body was not the definition.

An alias is object identity (`SEn is E10_2`), not a gram-matrix equality check in production code.
If identity matters, assert `is` in a test.

## 5. Hostility to non-semantic indirection

Delete anything that can be removed without changing what a mathematician can say or compute:

- wrap-then-call (`enable_X` → `install()` → `enable_X` → real call)
- catch-and-rethrow the same exception kind with a different message
- dict façades that reimplement `.items()` / `.keys()`
- re-exports of the same object under a second name
- import-time asserts that restate what construction already entails
- tests of “conflict scenarios” instead of tests of the intended dispatch or mathematical claim
- catalogue factories that re-verify primitives on every lookup (`is_involution` belongs on the morphism)

Ceremony is a bug: it creates a second, softer API that agents will use instead of the real one.
This is the same discipline as work-selection (above): an artifact that cannot fail carries no information.

## 6. Generality over local cleverness

When blocked, do not add a special case for this object.
Strengthen the general interface (element façade, Aut constructor, `+` / `sum`, override-refine) so the special case disappears.
Ask “why does this freestanding file/function exist?” — if it has no mathematical referent, delete it and place the content in the category or catalogue.

## 7. Tests certify the intended contract

Tests falsify the mathematical or dispatch claim: refined methods win over class methods; this alias is the same parent; this Aut is an involution; this table entry is that named lattice.
They do not exercise scaffolding, reassure about naming conflicts, or re-encode construction as gram-matrix comparisons.

Predicates that are part of the theory (`is_involution`, invariant and coinvariant lattices, isotypic components, …) are methods on the owned category interfaces, not side conditions in catalogue loaders.

**Adding to `tests/test_known_mathematics.sage`.** That file is the owner's specification of mathematics the preamble must reproduce, so agents do not extend it freely — but an addition is allowed whenever an independent source citation is attached to the new row: the Stacks Project, Kerodon, an item in the owner's Zotero library, a published paper, or an arXiv preprint. The citation is the admission ticket, and it names the source of the *asserted fact*, not of the implementation. Cite by the source's own identifier (Zotero `citationkey`, Stacks tag, arXiv id), verified against the source rather than recalled.

A row whose assertion would hold with the functionality removed certifies nothing. Assert the content: a maximal overlattice is reached by an inclusion, so the arrow's index is the assertion, not the codomain's existence.

## 8. Block Hom spelling, invariant and coinvariant lattices, and catalogue hygiene

Rules distilled from preamble work on direct-sum coordinates, embeddings, and coinvariant lattices (2026-07).

**Block Hom spelling.** A Hom/Aut between orthogonal direct sums is a block matrix: the $j$-th block column is the image of the $j$-th domain summand. Prefer block dicts via `L.summands()` — `{a1: b1, a2: b2 + b3}` — over flat generator-image lists when the mathematics is blockwise. Equal-rank block sums (`b2 + b3`) are gen-wise placement into multiple target blocks (the diagonal $N(2)\hookrightarrow N\oplus N$, not $N\to N\oplus N$). Name morphisms by their true domain; ergonomic sugar must not invent the wrong morphism type.

**Invariant and coinvariant lattices, and inclusions, are computed on the lattice.** There is no "eigenlattice": the notions are the invariant lattice, the coinvariant lattice, and the isotypic components. Invariant/coinvariant lattices and primitive inclusions (`invariant_lattice`, `coinvariant_lattice`, `coinvariant_inclusion`) are category methods on `IntegralLattices`; the coinvariant is $(L^G)^{\perp L}$. Catalogue must not ship helpers that take a named lattice plus an involution and assert kernel rank or Gram agreement — that certifies a guess, it does not construct. Named literature embeddings *use* the generic interface; they do not reimplement it.

**Catalogue is specimens plus nested namespaces, not ceremony.** Call `categories.install()` before building catalogue lattices; no manual `refine_one_lattice`. No `_with_names`, `_involutions`, `_embeddings`, or similar factories around one-liners or class bodies. Nested `Involutions` / `Embeddings` belong in the `Lattices` class body (populate empty nested classes in that body when Python scoping requires it); no post-hoc `__qualname__` patching or `Lattices.X = …` assignment after the class is built. Once the principled block or coinvariant API exists, catalogue entries use it everywhere — flat lists or kernel-basis shortcuts left “because they still work” are drift.

# Categorical organization model (always-on)

How the preamble's category tree is organized, and where new content goes.
For precise, formalized definitions of the notions below, defer to
`~/gitclones/lean-categories` (FOUNDATIONS.md and `LeanCategories/`): framed
generators and bases are §13.5, chosen presentations as structure are §75,
partial resolutions and the $FP_n$ hierarchy are §76, resolution classifiers
are §77. When a preamble docstring and that document disagree, the document
wins.

## Property subcategories vs data subcategories

Two kinds of subcategory, and the distinction decides method placement.

- A *property* subcategory states a fact about its members: finitely
  generated, finitely presented, finite, abelian. Membership is the
  statement, so its methods are predicates answered by placement
  (`is_finite` returns `True` because membership states it) and theorems the
  property entails.
- A *data* subcategory states that members carry a chosen datum: a framing
  (a chosen generating epimorphism $F(S)\twoheadrightarrow X$ from a free
  object), a chosen presentation (a framing plus chosen free relations), a
  chosen basis. Its methods consume the datum.

A property is the propositional truncation of the corresponding data
category: finitely generated = "some finite 1-framing exists"; finitely
presented = "some finite 2-framing exists"; $FP_n$ continues through chosen
syzygies, and each extension of a framing to the next level is itself a
choice. So a method that consumes a choice lives on the data subcategory and
never on the property one. A group can be provably finitely presented
(arithmeticity) while no practical presentation algorithm exists; asking it
for a presenting free group must be an absence, not a computation.

Producing a choice is one explicit crossing: a single named method computes
the datum once, stores it, refines the object into the data subcategory, and
returns it. Downstream code then asks the data category's words. A property
category never silently computes presentation data on demand.

The basic form of such a datum is a collection of morphisms (the chosen
tower). Where the surrounding category supports it, prefer the principled
package — an augmented chain complex for additive data, a DGA only when the
resolution must carry multiplication — over loose tuples of maps.

## Axioms live as high up as possible

An axiomatic subcategory is declared once, at the highest category that can
state it, and reached by `with_axiom` (the axiom name registered in
`sage.categories.category_with_axiom.all_axioms`). `Framed` is the model
case: one global axiom whose category owns everything derivable from the
framing datum — generating set, generators, counts, presentation display —
so that groups, modules, and algebras share one contract instead of three
restatements.

Duplication is the diagnostic: if two parallel categories restate the same
contract or the same derived method, the axiom was attached too low. Never
re-declare in a subcategory what a supercategory already provides, and never
restate category methods on a concrete class.

## Contracts are abstract_methods — of one kind, not two

A data subcategory states its contractual requirement as `abstract_method`s
on its `ParentMethods` (the pattern of
`categories/modules/pure/modules.sage`, where being a module *is* the ring
morphism $\rho: R \to \operatorname{End}(M)$ and the category requires it).

**Two things used to be spelled the same way, and only one of them is a
contract.**

- A **data-accessor** declaration exists only to say "hand me the field the
  concrete class holds" — the `_form_morphism()` shape. The category/class
  mechanism *obviates* these: the level that declares the datum supplies the
  constructor that establishes it, so the obligation cannot be missed and
  there is nothing left to declare. Do not write new ones, and delete the ones
  the chain makes redundant.
- An **undischargeable operation** is one a category can legitimately *state*
  in full generality but cannot *implement* in full generality. These are real
  contracts and they stay. Cardinality is total on sets, so the set level may
  declare it for every set while only a sufficiently narrow subcategory can
  supply a determinate answer rather than an *unknown*. The abstract
  declaration at the general level is correct mathematics, not a gap.

The second kind is **enforced at construction**, so an object whose obligations
are unmet raises at instantiation instead of existing in a defective state.
That closes the hole this section used to record — that `_refine_category_`
admits anything and runs no hook, leaving an obligation merely *visible*.

Enforcement has an authoring cost, and it is two things, both measured:

- **Write `abc.abstractmethod`, not Sage's `abstract_method`.** Sage's sets no
  `__isabstractmethod__` at all, so nothing — not `ABCMeta`, not any bridge —
  can see it. It is also untyped, which is why type-checking already used the
  stdlib one; this makes the two agree instead of split.
- **A provider that declares obligations carries `metaclass=ABCMeta`.** With a
  plain provider the dynamic class collects no abstracts, because the provider
  is in the bases rather than copied and a plain class never has
  `__abstractmethods__`. The metaclass is therefore *meaningful*: a provider
  carrying it is declaring that this level has obligations, and a level with
  none writes a plain provider. (It also requires the combined
  `DynamicMetaclass` × `ABCMeta`; a bare `ABCMeta` provider makes
  `dynamic_class` raise a metaclass conflict.)

Never synthesize `__abstractmethods__` by scanning provider dictionaries. That
is generation, and a generated obligation has no source to audit.

**An abstract predicate on a subcategory is a requirement on participants, not
an answer the category gives.** `EvenLattices.ParentMethods.is_even`,
`NondegenerateLattices.is_nondegenerate` and `IntegralValuedLattices.is_integral`
are abstract *on purpose*: the contract reads "if you refine an object into this
subcategory, that object must **provide** a way to determine or compute the
predicate". The object supplies it — a finitely generated formed module computes
`is_even` from its Gram diagonal; a participant whose evenness is a theorem
supplies a method returning `True`, and that is the *participant's* auditable
claim, made by name on the object. Never replace such a declaration with a
`return True` on the category: membership would then assert the property that
the declaration exists to demand evidence for, and every participant would
inherit an unearned claim. This is the correction of 2026-08-20 — the inversion
was written and reverted the same day; when the abstract declaration appears to
shadow a computing implementation, the defect is in how the class is built (see
`refine.sage`: the parent class is rebuilt from the object's *joined* category,
so a provider already in the join precedes the requirement), never in the
declaration. This predicate case is the **undischargeable-operation** kind
above: the general category states the predicate, the participant supplies
it, and `ABCMeta` is what makes "supplies it" mandatory rather than hoped for.

## Every constructor registers in the obligations sweep (for now)

`tests/test_constructors_meet_their_obligations.sage` runs every way the
preamble makes an object and asks each result whether any name its
categories require still resolves to an abstract declaration. Every new
constructor or construction path must add a specimen row to its
`_constructions()` table. An object that can enter a category without the
category's defining datum is exactly the failure class this catches (modules
with no ring action, form modules with no form).

"For now" is now load-bearing: the sweep was the enforcement of last resort
while an obligation could only be made *visible*. `ABCMeta` at construction is
the stronger mechanism it was waiting for, and the data-accessor obligations
disappear entirely once construction threads. Expect the sweep to shrink or be
retired as those land — but it is retired by a decision that says so, never by
attrition, and until then absence from it is never acceptable.

## Classes only tie constructions into the tree

Almost everything lives at the categorical level. The mechanism above makes the
category's methods classes *be* the implementation, so a separate concrete
`Parent` class is the exception, not the rule — it enters only where a
construction cannot be expressed categorically, or where the preamble consumes
a Sage class it did not define. Historically this read the other way, and the
named examples below are the ones being migrated, not the pattern to copy:
`BasedFreeModule`, framed groups intake, the framed free
algebras — and constructions are uniformized as high up as possible: one
free functor per concrete category in
`categories/functors/free_forgetful_adjunction.sage`, one framing contract,
per-category classes only where the construction itself is specific. A new
capability is new category content plus, at most, one construction class;
it is never a parallel class hierarchy.

# Python and Sage research code style (always-on)

These rules govern Python, Sage, spikes, the preamble, the installed package, tests, and notebooks.
Use the detailed mathematical and repository rules above when they give a narrower instruction.

## Mathematical model before representation

- Work in the order mathematical object → representation → implementation.
- Start with the mathematical object, its data, its laws, and its hypotheses.
- Identify the relevant category, objects, morphisms, functors, and universal properties before choosing classes or methods.
- Map that representation into Sage only after its objects, morphisms, hypotheses, and constructions are specified.
- Implement only the operations that remain after native Sage structure is used.
- Do not derive an API from the methods, classes, or data layouts that happen to exist.
- Do not duplicate the data of a chosen morphism in fields on its domain or codomain.
- Represent a chosen representative of a subobject of $B$ by a monomorphism $f:A\hookrightarrow B$.
- Obtain its target from `f.codomain()` and use $f$ as the chosen monomorphism.
- Keep an element of $A$ distinct from its image in $B$.
- Do not use coercion to erase the distinction between an element and its image.
- Preserve distinctions between objects, presentations, morphisms, images, theorems, and decision procedures.
- A presentation is not the object that it presents, a registry label is not a category, and runtime validation is not a theorem.
- Never replace an undecidable equality problem with a new Boolean method.

## Goal substitution and agent hubris

Treat the user's technical discussion as a precise specification.
Do not read it as loose guidance because it arrives in prose.
Every mathematical noun, qualifier, example, caveat, and request to think can constrain the result.
If code and the stated model differ, surface the difference.
Never silently choose the code's weaker model.

This repository contains research code that is intentionally outside common software patterns.
The agent will tend to replace unusual mathematics with conventional code from its training distribution.
This default can change the object, hypotheses, codomain, or required construction.
Conventional code is not a useful default when the task is to implement new mathematics.

Assume that the user knows this repository, Sage, and the mathematical program better than the agent.
This is an operational limit on the agent's authority.
It does not make every user claim true.
It means that an apparent contradiction must become a discussion, not a silent correction.

Agent hubris occurs when the agent treats its current framing as the only possible framing.
An apparent implementation barrier proves only that the present approach has a barrier.
It does not prove that the mathematical requirement must be weakened.
The agent is often too close to its first design to see a better formulation.
User input can resolve the barrier by changing the representation, category, functor, or direction of construction.

Never make a theoretical compromise on the user's behalf.
This includes replacing a general object with a special case, a construction with a predicate, or a theorem with a runtime guess.
It also includes adding a fallback, an exception branch, or a weaker public operation to make the code run.

When the exact implementation appears impossible, stop before writing compromise code.
Report these facts:

- The exact requested object or statement.
- The precise obstruction in the current approach.
- The hypothesis or property that a proposed compromise would weaken.
- The mathematically distinct alternatives that remain visible.
- The smallest question that needs the user's judgment.

Recommend a compromise when useful, but do not select it without approval.
The user can often remove the obstruction without any compromise.
A short expert reframe can prevent generic code, false abstractions, and a later refactor.

For example, let $R$ be a commutative ring.
Let $M$ and $W$ be $R$-modules, and let $b:M\times M\to W$ be $R$-bilinear.
A user can request the submodule $\langle b(x,y)\mid x,y\in M\rangle_R\le W$.
Replacing it with a $\mathbb Z$-lattice's scale ideal changes the codomain and requested object.
The user already made that distinction.
The agent must preserve it, not teach it back or erase it.

Likewise, let $f:M\to N$ be an $R$-module homomorphism.
A request to construct $\ker(f)\le M$ is not a request to decide whether $\ker(f)=0$.
If current code decides only the latter in a special case, surface the mismatch before changing the construction.

A passing test can hide the substitution when the test encodes only the weaker claim.
The loop is self-confirming:

1. Replace the requested object with a familiar proxy.
2. Test the proxy.
3. Use the passing test as evidence for the original requirement.

Such evidence says nothing about the omitted requirement.
It makes later work inherit a mathematically false interface.

No instruction file can contain all of the user's mathematical knowledge.
Exact listening is therefore a required research method.
Implement what the user specified.
If that cannot be done exactly, surface the nuance and defer the mathematical decision.

## Native Sage model and direct code

- Use Sage's `Parent`, `Element`, `Category`, `Morphism`, and `Hom` structures.
- Model a functor as a functor and a morphism as a morphism.
- Let subcategory relations and Sage categories with axioms determine available methods, hypotheses, codomains, and algorithms.
- Put mathematical operations, constructions, and predicates in category methods, as specified above.
- Use a narrow subclass for one representation-specific defect that Sage categories cannot express.
- Override only the incorrect operation and retain the established implementation.
- Keep each method in the same order as the mathematical definition.
- A mathematician must be able to compare the method body directly with that definition.
- Do not hide the defining steps behind chains of non-mathematical helper functions.
- Return results in their correct parent and category.
- Make public operations and valid constructions explicit after every refactor.
- Compare valid constructions, methods, category membership, result parents, and notebook behavior.
- Compare semantics, not filenames, class counts, method counts, or structural similarity.

## Public interfaces and encapsulation

- Treat a leading underscore as a non-public interface marker.
- Call `self._f()` only inside the class that owns `_f` or inside a documented subclass contract.
- Treat every unrelated call to `x._f()` as a defect unless `_f` is a documented extension protocol.
- Treat `X._f(x)` as a defect when it bypasses instance dispatch.
- Do not read or write another object's `_state` directly.
- Ask another object through its public methods. Move missing behavior to the object that owns it.
- Do not expose internal state only to let callers reproduce the owner's behavior.
- Implement Python and framework hooks at the owning class boundary.
- Invoke those hooks through their public syntax or public dispatcher.
- Write `f(x)`, `parent(data)`, `iter(x)`, and `len(x)`. Do not call their protocol methods directly.
- In Sage code, callers use morphisms, parents, and elements through their public operations.
- A direct private access across modules or objects requires a documented protected contract at the declaration.
- Review every cross-object underscore access before committing Python or Sage code.

## Types

- Give each value the type that names its mathematical role.
- Use `Parent` for an object of a Sage category, not `Any` or `object`.
- Distinguish parents, elements, morphisms, coefficient rings, modules, matrices, domains, and codomains.
- Treat each mypy error as evidence about the model or import boundary.
- Fix the model, method owner, return contract, import path, or missing stub.
- Never weaken an annotation to silence the checker.
- Make stable `.sage` definitions importable when their real types cannot otherwise be named.

## `object` is never a type; `Any` has exactly one position

**`object` is never allowed as a type. There is no exception.** Not as a
parameter, not as a return, not inside a container, not under `TYPE_CHECKING`.
A value annotated `object` supports no arithmetic, no membership and no method,
so the annotation states nothing about the value and the checker admits
anything at all. It marks a place where a type was owed and not written.

`Any` is narrower. It has exactly one legitimate position: a **parameter of a
method whose job is to decide about an arbitrary argument**. So far as is
known those are `__eq__` and `__contains__`. `[1, 2] in MyModules` returning
`False` is a perfectly valid line of code — the argument really can be
anything, and answering is the method's whole purpose. If some other site
appears to take genuinely arbitrary input, that is a finding to raise, not a
licence to widen an annotation.

**`Any` is never valid as a return type.** A method knows what it produces.
Write the type:

- `Self`, when the method returns another object of the receiver's own kind;
- `None`, when it returns nothing;
- a preamble-owned mathematical object whenever one exists. A natural number is
  the element type of `NN`, an integer the element type of `ZZ`, a real number
  the element type of `RR`. Reach for the owned type before any Python
  built-in.

`float` is almost never right — it is a machine approximation standing where a
real number belongs. `list`, `tuple` and their relatives are never right: name
the notion you actually have, which is a set, an ordered set, a multiset, an
ordered multiset, or an indexed family. See *A list is not a mathematical
object* below for why that one choice cascades through every downstream caller.

**Inputs are held to the same standard.** A parameter is mathematically
structured and coherent, for the same reason a return value is: the signature
is where a reader learns what the operation is about. A method that accepts a
matrix where it means a morphism, or a tuple where it means a generating set,
has already lost the mathematics before its body runs.

**Private methods may use primitive types and signatures internally.** The
concession is real, and it is bounded by one condition: no external consumer
reaches into a private method. The moment `X._f()` is called from outside `X`,
its primitive signature is a public interface and the concession is void. *Public
interfaces and encapsulation* above owns that boundary.

**Minting a type that names actual mathematics is welcome.** It is what the
preamble is for. A notion the work needs and the tree does not yet hold gets
its own object, its own place in the category graph, and its own name, and
that is a good day's work rather than a rule being bent. The test is never
novelty. It is whether the type has a mathematical referent a mathematician
would recognise, and it applies equally to a type that already exists.

**What is banned is a type invented to satisfy these rules.** A constructor
that took a list, a tuple and two integers does not become correct when those
become `MyCustomClassCreationDatum`. Nothing was fixed: the caller still
assembles the same unstructured data, the same mathematics is still missing,
and now there is a class with no referent to maintain as well. Ask what the
datum *is*. Usually it already has a name — a morphism, a generating set, a
presentation, an indexed family — and naming it makes the signature right with
no new type at all. When it genuinely has none and the notion is real, define
it properly: that is the welcome case above, and a real addition to the
category graph is a design decision to raise, never a wrapper to drop in.

Over-compliance is the failure from the other side. A class minted so a line
technically passes, a name coined because the rule said not to write `tuple`,
a type introduced to quiet a checker: each satisfies the letter and breaks the
statement, and each is worse than the original violation, which at least
stayed visible. These rules restate what the mathematics already requires. If
following one produces something a mathematician cannot name, the rule was not
the problem — stop and say so. The inventions this has already produced are
catalogued in `.agents/references/mathematical-auditor-priming.md`.

## Dynamic peeking is prohibited; the category is the type

`getattr`, `setattr`, `hasattr`, `isinstance`, `type(...)` comparisons, `cast`,
and instance-dictionary reads are explicitly prohibited in mathematical code in
the preamble.

- Never duck-type. Asking an object whether it happens to carry a name asks at
  runtime what the category graph already states.
- **Categorical containment is typing information.** Write `assert X in C`.
  Never write `isinstance(X, SomeClassRelatedToC)`. Membership is the
  mathematical statement; the class is an implementation accident, and one
  mathematical notion is realized by several unrelated classes.
- Assert the membership that *defines* an operation before using it. Every line
  below is then provably defined wherever it is reached.
- **Route by `case`/`match` on categorical containment.** `if`/`else` chains are
  almost never right here. A mathematical routing decision has one branch per
  category, and the reader must see the categories. Match a category with a
  guard, `case _ if x in FormModules(R):`, not a class pattern; a class pattern
  is `isinstance` written in different syntax.
- When an object lacks a capability, repair its placement. Do not probe. Refine
  it, construct it correctly, or state the gap on the owned interface.

| Peek | Write instead |
| --- | --- |
| `hasattr(x, "gram_matrix")` | `x in FormModules(R)` |
| `"_form" in x.__dict__` | `x in FormModules(R)` |
| `isinstance(x, SomeFormModuleClass)` | `x in FormModules(R)` |
| `isinstance(image, Vector)` | delete the branch; assert the parent |
| `getattr(g, "presented_group", None)` | `g in OwnedFinitelyPresentedGroups()`, then call it |
| `type(x) is X` | membership, or an owned element class |
| `cast(T, x)` | make the type real, or narrow by assertion |
| `x.__dict__.setdefault("_cache", {})` | `cached_method` |
| `setattr` on a class imported from `sage.*` | own the category; see the ontology section above |

**Every use of `setattr` is suspect, not only on Sage's classes.** A reader of a
class must be able to see its fields by reading it. `setattr` puts state on an
object that the class never declares, so an auditor meets a field at runtime
that appears nowhere in the source, cannot tell which level introduced it, and
cannot tell whether it is always present. That is the same defect as
`__dict__` reads, arriving from the other direction.

There is no typing problem that forces it. The claim that a checker, a dynamic
class, or a mechanism made `setattr` necessary is a report that the
architecture is wrong at that point. Re-architect instead: declare the datum at
the category level that introduces it, establish it in that level's
constructor, and let it thread by cooperative `super().__init__`. If the field
cannot be declared where it belongs, the placement is wrong, and that is the
finding.

The exceptions are narrow, and each must be nameable at the site:

- `__contains__`, where the argument is genuinely arbitrary and deciding is the
  method's whole job.
- `_element_constructor_`, the one boundary that admits foreign data.
- A read that Sage's own documented protocol performs that way, with the reason
  recorded in a comment at the site.
- Declarations under `if TYPE_CHECKING`, which have no runtime effect.

Nothing else qualifies. A probe outside these sites is a defect, and it is
where a non-mathematical shortcut hides.

## A list is not a mathematical object

`list` and `tuple` are programming constructs. They are not mathematical
primitives, and they do not belong in the preamble's public vocabulary.

Order is not the objection. Most objects here are ordered. The objection is
that `[1, 2, 1]` is Python, while $\{1, 2, 1\}$ regarded as an **ordered
multiset** is mathematics. Name the notion you actually have — a set, an
ordered set, a multiset, an ordered multiset, an indexed family — and each of
those is a real object that arrives carrying its own structure:

- a cardinality, and membership;
- unions, intersections, and the other set operations;
- an enumeration function where one exists;
- homs into other sets, so it composes with everything else;
- a place in a category, so its operations are inherited rather than written.

A `list` carries indexing, `len`, and `append`. None of those is a mathematical
operation. Concatenation is not union. A list has no homs and sits in no
category, so every operation on it must be hand-written.

**A list in one signature cascades.** The next caller writes
`range(len(xs))`, then `xs[0]`, then `zip`, then a comprehension building
another list — and the engineering idiom propagates from the type outward
through everything downstream. This is the mechanism by which mathematical code
turns into Python that happens to be about mathematics. The preamble must read
as a mathematical DSL, not as mathematics written in Python.

Consequences:

- `len` is almost never correct. Use `cardinality`. A length is an `int` and
  assumes finiteness; a cardinality is a cardinal and does not, so every `len`
  is a silent finiteness hypothesis at a site that never stated one. The order
  of a group and the order of an element are cardinalities, not integers.
- Do not loop to accumulate. **Sum over a set.** An index loop imposes an
  enumeration on an object that may have none, and hides the operation behind
  the iteration.
- Compare cardinalities, never lengths.

**Comparison itself is localized.** Do not compare coarse numerical invariants
in ordinary code at all. Every comparison belongs in `__eq__` or in
`is_isomorphic`, which are the two methods whose whole job is to decide
sameness. Everywhere else, ask the object.

Inside those two methods you `case`/`match` to route. One of the routes may
legitimately compare numerical invariants internally — but only in a case whose
hypotheses are stated in the match itself, so a reader sees the hypothesis
beside the comparison that needs it. A numerical comparison written outside
such a case is a criterion smuggled in without its theorem.

## Simplicity and prior art

- Choose the smallest implementation that satisfies the complete mathematical requirement.
- Add no unused parameter, speculative extension point, or interface with one caller.
- Add an abstraction only when a second real use requires it.
- Use the project's dependencies before adding code or packages.
- Use native Sage before adding a parallel implementation.
- Use a maintained package or mature reference implementation before new local code.
- Keep unavoidable local code small and cite its mature reference implementation.
- Remove obsolete constructors, aliases, fallbacks, bridges, and compatibility paths.
- Keep one current implementation for each operation or construction.

## Names and ownership

- Use established mathematical or Sage terminology.
- Name each entity by its mathematical role, not its storage or implementation.
- Treat a wrong name as possible evidence of a wrong abstraction.
- Check the definition, type, owner, operations, and category before a semantic rename.
- Give each mathematical entity one authoritative module and one public export.
- Place public exports at a clear package boundary.
- Keep category methods, catalogues of examples, session defaults, and computation code in their stated homes.
- Keep definitions, terminology, category declarations, exports, and decisions in one authoritative source.
- Do not create mirrored registries or synchronized copies.

## Repository placement

- Keep the installed package thin and stable.
- Move code from a spike into `src/` only after a high-level research notebook uses it.
- Do not promote code because it looks complete.
- Develop new mathematics in the active spikes by generalizing from verified examples.
- Use the frozen category specifications only as prior art.
- Install published dependencies normally.
- Put unpackaged external code in `computations/vendor/`.
- Code in `computations/vendor/` never graduates into the maintained package.
- Keep project-authored experimental code in a spike.
- Treat `computations/notebooks/` as the researcher's control surface.
- Do not reorganize, classify, or tidy that notebook tree unless the user asks.
- Use editable installs and repository symlinks instead of notebook path manipulation.
- Keep notebook setup cells minimal and make editable-install changes available without copying code.
- Use high-level notebooks for real mathematical work, not only API demonstrations.
- Keep the preamble small, cohesive, native to Sage, and usable without notebook setup.

## Proof and tests

- Test mathematical behavior and method resolution through Sage categories, not scaffolding or correction history.
- Assert the correct parent, category, domain, codomain, images of elements where defined, composition, or mathematical equality.
- Test high-level notebook operations when notebook usability is the claimed behavior.
- Use the smallest test case that distinguishes correct behavior from a plausible failure.
- Use a large named example only when the claim concerns that example.
- Verify the surface named by the requirement.
- Use a real Sage process for Sage behavior and a live kernel for notebook behavior.
- Inspect rendered output when the requirement concerns rendering.
- Treat a nearby green check as evidence only for the proposition it executes.

## Performance and search

- Measure wall time and its growth with input size.
- Use call counts only to locate repeated work.
- Remove repeated derivation, needless enumeration, repeated verification, and overly general algorithms.
- Preserve code that shows the correct mathematical sequence, even when a faster form is less clear.
- Start filesystem discovery at the requested path with a shallow query.
- Expand the search only when the evidence requires it.

## Completion and durability

- Complete the original mathematical operation or construction, not only a local type, test, registry, or plan task.
- Continue when the next in-scope step is clear and safe.
- Defer work only for a real dependency or a required user decision.
- Context limits and a successful local subtask do not justify deferral.
- End each substantive unit in a focused commit.
- Preserve unknown files until their ownership is known.
- After ownership is known, commit required files and use recoverable deletion for disposable files.
- Keep important work in version control, not only in a working tree or notebook session.

# Addendum: installing methods on Sage objects via category refinement

This addendum is the **mechanism** for §1 above (category as extension point).
For preamble and owned APIs, use override-refine (`dzack_research.preamble.refine.refine`) and post-init hooks on classes; do not introduce monkey-patches or constructor-only installation paths for new work.

Sage objects (parents, elements, morphisms) carry methods through their **category's dynamic MRO**.
A category defines `ParentMethods`, `ElementMethods`, and `SubcategoryMethods` inner classes;
any parent whose category (or join of categories) includes that category gains those methods automatically.

**The correct way to install new methods on existing Sage objects** — in exploratory notebooks,
preamble files, or a spike's initialization — is:

1. **Define a category** that declares `ParentMethods`, `ElementMethods`, or both.
2. **Route objects into that category** by post-init hooks on the relevant **classes** (preferred), calling override-refine so owned methods precede concrete class methods.

This is **not monkey-patching**. You are not replacing methods on a class;
you are telling Sage that certain instances belong to a more refined category,
and Sage's own dynamic dispatch makes the methods available.

## Canonical pattern

```python
from sage.categories.category_with_axiom import CategoryWithAxiom_singleton

class _MyCustomCategory(CategoryWithAxiom):
    """A custom category whose methods apply to refined objects."""

    def super_categories(self):
        return [SomeBaseCategory()]

    class ParentMethods:
        """Methods available on every parent refined into this category."""

        def my_method(self):
            return ...

    class ElementMethods:
        """Methods available on elements of parents refined into this category."""

        def my_element_method(self):
            return ...


# Post-init: refine specific objects into the category
def install():
    cat = _MyCustomCategory()
    for obj in target_objects:
        obj._refine_category_(cat)
```

## Codebase examples

| File | Category | Target objects | Entry point |
| --- | --- | --- | --- |
| `archives/lattice-research/src/sage_patches/ring_base_category.py` | `_ModuleBaseRings` (custom) | `ZZ`, `QQ`, `RR`, `CC`, `QQbar`, `Zp(p)`, `GF(p)` | `_install_module_base_rings()` — iterates well-known singletons |
| `archives/lattice-research/src/sage_patches/ideal_submodule.py` | `Modules(ring)` (existing Sage category) | Ideals produced by `Ring.ideal()` | `_module_aware_ideal()` — intercepts the constructor and refines each result |
| `archives/lattice-research/src/sage_patches/fraction_quotients.py` | `Modules(ZZ)` (existing) | `QQ / ZZ`, `QQ / (n*ZZ)` | `__truediv__` patch on `RationalField` + direct refinement of two specific instances |
| `archives/lattice-research/src/sage_patches/module_enrichment.py` | `Modules(R)` (existing) | Direct sums, quotients of free modules | `_ensure_module_refinement()` — called inside patched `direct_sum` and `quotient` |

## Variants

### A. Define a custom category + batch post-init (preferred)

Used in `ring_base_category.py`. Best when you know the target objects at import time:
they are singletons (like `ZZ`) or produced by a small set of constructors.

```python
class _MyMethods(CategoryWithAxiom):
    class ParentMethods:
        def utility(self): ...

def install():
    for obj in [ring1, ring2, ...]:
        obj._refine_category_(_MyMethods())
```

### B. Constructor interceptor (archive / last resort)

Used historically in `ideal_submodule.py` and `fraction_quotients.py`.
Prefer class post-init hooks (§1) for new work.
Only intercept a constructor when objects cannot be caught after `__init__` and a class hook is impossible.

```python
def _intercept_constructor(self, *args):
    result = _native_constructor(self, *args)
    refine(result, MyCategory())  # override-refine when owned methods must win
    return result
```

### C. Mid-construction refinement

Used in `module_enrichment.py`. The refinement happens *inside* a method that already
creates the object, so no interception is needed — just add `_refine_category_` before returning.

## Rules of thumb

- **Category owns the methods.** The method implementation lives in `ParentMethods` or
  `ElementMethods`, not inline in the post-init code. The post-init only routes the object in.

- **Override-refine when owning an interface.** Use `refine` from the preamble so the new
  subcategory precedes the concrete class in the MRO; bare `_refine_category_` alone leaves
  class methods ahead of category methods (Sage’s default), which is wrong for overrides.

- **Hook classes, not constructors**, for new installations. Post-init on the Sage class is
  the default; constructor interception is archive/last-resort (Variant B).

- **Use existing Sage categories when possible.** If you just need an object to be recognized
  as an `R`-module, refine into `Modules(R)` rather than defining a new category.
  Define a new category only when you have method implementations that no existing category provides.

- **Do not monkey-patch class methods.** If you find yourself writing
  `SomeSageClass.my_method = lambda ...`, stop and write a category instead.
  Monkey-patching breaks for subclasses, is non-composable, and bypasses Sage's MRO.

- **Do not store method implementations on the parent class itself.**
  The parent class (`IntegerRing_class`, `MatrixSpace`, etc.) is Sage's compiled code;
  the category's `ParentMethods` is where new methods belong.

  **For the preamble's own categories this goes further: there is no separate class
  at all.** The category's methods classes *are* the implementation — they carry the
  bases, the fields and the constructor, and construction threads by
  `super().__init__` up the category graph (see *The category IS the class* above).
  A distinct concrete class survives only where a construction cannot be expressed
  categorically, or where the preamble consumes a Sage class it did not define; the
  rule below is stated for those, and for the adopted Sage objects this addendum is
  about. Every mathematical operation — predicate, invariant, construction,
  orbit, presentation — is a mixin on the refined category (`ParentMethods`,
  `ElementMethods`, `MorphismMethods`), because that is what makes it available to
  every object the mathematics says it applies to, in the right resolution order, and
  what lets a subcategory sharpen it. Writing the same method on the class instead
  binds it to one construction path, hides it from siblings, and puts it behind the
  category methods in the MRO. Ask of every new method: *which category's members can
  answer this?* — and put it there. The exceptions are narrow and nameable: catalogue
  namespaces holding named specimens (`Lattices`, `Coble`, `Sterk` and their
  staticmethods), Sage's own element-construction hooks on a `Parent`
  (`_element_constructor_`), and private record types that carry no mathematics.

- **`_refine_category_` joins.** It calls `self._init_category_(self.category().join(Cat))`, so
  the object keeps all its existing category memberships and gains the new one.
  Calling it multiple times is safe. Override-refine still performs that join, then rebuilds
  `__class__` so owned methods win.

- **`@final` guards override.** If a method in `ParentMethods` should not be overridden by
  a more specific category in the join, mark it `@final`.

## What this is not

This pattern is specifically for **retroactive method installation** — adding capabilities to
objects that already exist at import time or are created by Sage's existing constructors.
It is not a replacement for defining a proper category hierarchy from scratch;
it is the bridge between Sage's compiled algebra and this repo's semantic needs during
exploratory and spike work.

# Transcript-derived research directives (2026-08-21)

The governing model is:

- Mathematics determines the architecture.
- Categories own generic operations.
- Concrete classes store only necessary construction data.
- A leaf category handles only its immediate supercategory.
- Structure and methods must then propagate through the full category chain.
- The system must support parent, element, and subcategory methods.
- Category methods should precede class methods in the MRO.
- Concrete classes can then supply faster implementations when necessary.
- New leaf categories must need little repeated code.
- Generated methods are unacceptable because mathematicians cannot audit their source.

Specific mathematical directives include:

- A lattice is first a set and a module.
- Cardinality belongs to its underlying set.
- A formed module is constructed from its form morphism.
- Bilinear forms use the tensor square.
- Quadratic forms use the divided square.
- These form types require separate free-forgetful adjunctions.
- Forgetting a form is a functor, not an object method.
- Module morphisms require the same base ring.
- Every module-related category must require its base ring.
- `IntegralLattices` must also require an explicit ring.
- Membership predicates belong to refined subcategories.
- An object claiming membership must supply the required predicate.
- Other operations should remain category methods.
- Axiomatic subcategories need not have separate concrete realization classes.
- Special algorithms can make otherwise undecidable questions decidable on restricted categories.
- KBMAG is valuable for exactly this reason.
- Differences between full reflection groups and smaller reflection subgroups are substantive research results.

The migration philosophy is semantic preservation:

- A corpus selected for migration is presumed valuable.
- Every file must receive one semantic reading.
- Preserve mathematics, specifications, tests, examples, design work, and incomplete research.
- Incomplete research is not disposable.
- Foundational categories remain valuable without current callers.
- Tests and known values are mathematical products.
- Incorrect mathematics should produce a corrected statement.
- Deletion alone does not preserve the lesson.
- Remove a source only after its useful content has a durable destination.
- Byte equality, execution status, file names, maturity, and polish do not measure mathematical value.
- Do not split reading and implementation between agents when the reader’s mathematical context is essential.
- Prefer migration of existing prior art over a parallel implementation.

The epistemic directive is equally strong:

- A false architectural claim requires a review of foundational assumptions.
- Local counts and reduced error totals do not establish correctness.
- Inspect existing code, archived work, plans, and repository memory first.
- Use transcripts only when those sources do not resolve the question.
- Do not ask the user to make a technical decision that the assigned research should determine.
- Ask only when several materially different interpretations remain.

The recent verification rules were specific to the migration project:

- Perform the complete semantic migration before automated verification.
- Do not treat unverified work as deferred verification.
- Do not run Sage, tests, or hooks during that migration.
- Commit migration units without verification.
- Hold pushes until the later integrated verification pass.
- That later pass must use global `ai-review-ci` ownership.
- Sage source must be lowered before Python type analysis.
- QC must preserve detailed logs and wall-time reports.
- Local projects should follow current upstream `main`, not fixed revision pins.

Communication must report mathematical effects. It must not report token use, agent waves, repeated checks, or administrative state.

# Mathematical judgment and repository practice from transcript corrections (2026-08-21)

The preceding section records a first synthesis. This section adds the mathematical
reasoning, cognitive corrections, repository rules, and style requirements that the
short synthesis did not capture.

## Standard of mathematical thought

- Treat each mathematical correction as compressed research guidance.
- Derive the structure that makes the correction true.
- Do not translate one mathematical correction into one local method request.
- Identify the objects, morphisms, hypotheses, codomains, and universal properties first.
- Determine the categorical home of each construction before writing its representation.
- A named category must exist as a category, not as a class with similarly named methods.
- A named functor must act on objects and morphisms.
- A named adjunction must include the hom-set bijection, unit, counit, and naturality.
- Do not use category theory as a metaphor for a collection of constructors.
- Do not replace a mathematical object with the data returned by an external engine.
- External engines compute data used to construct owned mathematical objects.
- Local computational data never replaces the structure that explains its functorial behavior.
- Prefer a general mathematical construction when it removes many apparent local tasks.
- A short advisor question can expose a missing theory rather than a missing method.
- Unfold that theory before estimating or implementing the apparent method backlog.
- Do not hedge after the user has supplied enough structure to derive the answer.
- Perform the mathematics needed to resolve the stated universal property.
- If a conclusion contradicts standard structure, rederive it before changing code.
- One false foundational assertion invalidates every downstream inference that used it.
- Review foundational assumptions after such a contradiction.
- Do not review counts, file totals, or gate output as substitutes for those assumptions.
- Ask whether the current construction is the requested mathematical object at all.
- Ask whether the code models the user's stated object, morphism, or functor exactly.
- A locally working representation does not answer either question.

## Object, structure, and representation

- Start from mathematical objects and their relations.
- Choose representations only after the mathematical ownership is clear.
- A lattice is a set with module structure and a form.
- It does not merely hold unrelated objects representing those structures.
- A formed module is a module with a form.
- It does not wrap a second module that remains the real mathematical object.
- Category membership must correspond to actual supplied structure.
- An object in a structured category must carry the data required by that category.
- Do not refine an existing object into a data-bearing category without constructing the required data.
- Construct owned objects through the owned category hierarchy.
- Use refinement only for adopted Sage objects when refinement adds no missing construction data.
- Provide a `preamble.all` construction surface analogous to `sage.all`.
- That surface constructs owned objects and populates the research namespace.
- Never build a parallel toy hierarchy when the task concerns the live preamble hierarchy.
- A toy that proves itself against itself does not prove the real architecture.
- Convert one real category before claiming that a category mechanism reduces author effort.
- User-facing notebook objects are evidence about the live surface.
- Do not describe a new experimental path as the state of that surface.

## Category and class architecture

- Defining a new leaf category must feel routine.
- The leaf author handles the leaf and its immediate supercategory only.
- The leaf author never implements the transitive chain manually.
- `super_categories()` is the sole declaration of categorical inheritance.
- Do not add a second registry, binding declaration, or `forgets_to` relation.
- The declared category graph already contains that information.
- Sage already derives parent, element, and morphism method hierarchies from that graph.
- The owned mechanism must propagate constructors and fields through the same graph.
- The category and its implementation class should become one readable source unit.
- `ParentMethods` can be the implementation class when its bases and fields propagate.
- The implementation class stores only the minimal data introduced at that level.
- Its constructor consumes that data and delegates the remaining construction upward.
- A category level supplies the structure it introduces.
- It must not merely declare an obligation that its own construction could discharge.
- Abstract obligations remain valid for genuinely axiomatic categories.
- An axiomatic subcategory need not have a separate concrete implementation class.
- Generic mathematical operations belong in category method classes.
- Parent operations belong in `ParentMethods`.
- Element operations belong in `ElementMethods`.
- Morphism operations belong in `MorphismMethods`.
- Concrete classes remain minimal data containers when Sage ownership requires them.
- Category methods precede concrete class methods in the owned MRO.
- A concrete class can then provide a more efficient implementation when required.
- Generated forwarding methods are forbidden.
- A mathematician must be able to open the source and inspect each method body.
- Do not replace readable mathematics with generated indirection.
- Delete hand-written forwarding after the category graph supplies the operation directly.
- Do not delete forwarding before the correct category surface exists.
- The mechanism must compose through parents, elements, and morphisms.
- The mechanism must also propagate fields and construction data.
- Method propagation without data propagation does not solve the architecture.
- Data propagation without the three method surfaces does not solve it either.

## Immediate-supercategory construction

- In a chain `Sets -> Modules -> Lattices`, each level owns one construction step.
- A lattice constructor supplies the module required by the module level.
- It never reimplements set cardinality or product behavior.
- A module constructor supplies its underlying set construction.
- A free module of rank `n` supplies the product of `n` copies of its base ring.
- The set level owns cardinality, finiteness, countability, products, and coproducts.
- The ring level supplies the set data for the ring.
- Higher levels inherit the set operations through the category chain.
- `L.cardinality()` must work without `Lattices` naming cardinality.
- The implementation must preserve actual element parents and element operations.
- Do not identify a module's elements with bare tuples merely because their sets are bijective.
- Use the correct categorical relation when only a bijection is available.
- Cardinality and finiteness are invariant under bijection.
- Element representation and parenthood are not invariant under an arbitrary implementation shortcut.
- The architecture must preserve both facts.

## Subcategories, predicates, and operations

- Distinguish membership predicates from ordinary categorical operations.
- A predicate-defined subcategory states the contract for membership.
- An object refined into that subcategory supplies the predicate computation.
- The category does not return `True` merely because its name asserts a property.
- Other operations should remain category methods whenever their hypotheses are categorical.
- Place axioms as high as their hypotheses permit.
- Foundational categories remain essential without current callers.
- A category of magmas is foundational mathematical work, not disposable empty code.
- Empty method bodies, low call counts, and unfinished descendants do not reduce its value.

## Forms and formed modules

- A form is not synonymous with a bilinear form.
- Bilinear and quadratic forms have different classifying constructions.
- A bilinear form on `M` is a morphism from `M tensor M` to its value module.
- A quadratic form uses the divided square appropriate to quadratic maps.
- Construct a formed module from that defining form morphism.
- Recover the underlying module from the source construction of the form.
- Do not pass the same module twice through independent constructor arguments.
- Independent copies can disagree and make invalid states representable.
- A Gram matrix constructor first constructs the implied free module.
- It then constructs the required homset and form morphism.
- It finally calls the main formed-module constructor.
- Forgetting the form is a functor between categories.
- It is not a method on a formed module.
- Each form flavor has its own free-forgetful adjunction.
- The free bilinear form is the identity on the tensor-square classifier.
- The free quadratic form is the identity on the quadratic classifier.
- Prove each adjunction through its hom-set bijection.
- Do not name an adjunction and then deny the existence of its adjoint.

## Base rings and morphisms

- A module category always requires its base ring.
- No module constructor may silently substitute the integers.
- `IntegralLattices` also requires an explicit ring.
- Remove optional-ring signatures and their fallback branches.
- A module morphism has a source and target over the same base ring.
- `Hom` between an `R`-module and an unrelated `S`-module is not a module homset.
- Scalar extension and restriction require named functors and changed categorical data.
- Do not conceal such changes inside a permissive homset constructor.
- Make invalid base-ring combinations impossible at construction.
- Fix the architecture that permits ringless modules.
- Do not patch individual ringless instances.

## Decidability and specialized algorithms

- State the exact decidability boundary for each equality or isomorphism question.
- Do not invent Boolean procedures for general undecidable problems.
- Do not use general undecidability to reject a specialized decision procedure.
- KBMAG can make equality decidable for groups with suitable automatic structures.
- Such machinery is significant research, not a conflict with the undecidability rule.
- Return `Unknown` only where the available hypotheses and algorithms do not decide the question.
- A specialized algorithm should return a definite result on its valid domain.
- Record its hypotheses in the category that supplies it.
- Let category placement select the specialized algorithm.
- Do not special-case it inside a general method without mathematical ownership.

## Mathematical discrepancies and research findings

- Preserve discrepancies that expose distinct mathematical group actions or conventions.
- A Sterk root-count difference is not debris.
- It can distinguish full reflection-group orbits from smaller subgroup orbits.
- Preserve the groups, actions, and orbit relation needed to state that difference.
- Do not reduce such a finding to a note that two numbers disagree.
- Derive the corrected mathematical statement from a false source statement.
- Land the corrected proposition, construction, or cited specimen in the repository.
- Do not retain tests whose only purpose is to forbid a past mistake.
- Test the intended positive mathematics instead.
- Published tables, literature examples, and existing fixture values can be proper oracles.
- Their value does not depend on whether an agent considers the source prestigious.
- Verify provenance when adding a new citation-gated specimen.
- Preserve an existing oracle during migration even when its provenance is informal.

## Semantic migration

- The preamble centrally owns locally-authored Sage mathematics.
- A migration request establishes the value of the selected corpus.
- The executor decides destination and synthesis, not whether the corpus deserved preservation.
- The unit of migration is a mathematical notion, not a file.
- Read each notion once for semantics.
- The reader should migrate or synthesize it while that context is live.
- Do not separate deep analysis from implementation when implementation needs that mathematical context.
- Do not make one agent produce a report for an unrelated new agent to interpret.
- A summary is not the migrated mathematics.
- Move prior art into the live preamble before reconciling it with current code.
- Prefer a real move over a parallel rewrite.
- After a mistaken edit yields the correct state, repair forward.
- Do not undo the correct state merely to reproduce it by a preferred method.
- Reconcile source and destination until the result is semantically a move plus required updates.
- Delete the original only after every useful notion has an owned destination.
- Deletion is a receipt for completed relocation.
- It is never a value judgment on the source.
- Preserve code, tests, specifications, examples, design corpora, and incomplete research.
- Incomplete research remains research.
- Planning corpora can contain mathematical structure and future categorical homes.
- Stub declarations can define essential structure before algorithms exist.
- Existing TDD suites are forward requirements and must migrate to the owned surface.
- Existing parity tests can document delegation boundaries.
- False source mathematics creates a correction-synthesis obligation.
- Do not delete the false statement and preserve only an error ledger.
- Non-code logs, telemetry, caches, and tool output are outside a mathematical code migration.
- Do not create dispositions or rulings for irrelevant material.

## Value and evidence during migration

- Byte equality has no positive or negative mathematical meaning.
- A checksum can locate possible duplicates but cannot decide semantic equivalence.
- Execution status does not determine research value.
- Maturity, polish, file name, directory, and current scope do not determine research value.
- The absence of callers does not determine research value.
- The absence of complete algorithms does not determine research value.
- A source outside the current preamble scope is a reason to enrich the preamble.
- It is not a deletion reason.
- Compare source and destination definitions, hypotheses, codomains, conventions, and behavior.
- Verify that the destination owns every useful mathematical distinction.
- If the destination cannot express a notion, extend the destination.
- Do not discard the notion because the destination is incomplete.

## Execution shape for large migrations

- Inventory files once.
- Partition them into disjoint semantic batches.
- Assign one reader to each artifact or notion.
- Read, decide, migrate or synthesize, and retire the source in one context.
- Do not analyze the same material in repeated waves.
- Do not create an analysis fleet followed by a context-free implementation fleet.
- Preserve an agent's mathematical context when revising its instructions.
- Ask it to checkpoint before stopping it.
- Stop only when its frame is unusable, not when one instruction changes.
- Use agent reasoning effort that matches the mathematics.
- Do not spend a large research context on a file move or import update.
- Perform simple moves and direct edits directly.
- Do not write edit scripts for a bounded hand edit.
- Do not replace a direct migration with scripts that match and rewrite source text.
- A sweeping architectural refactor need not pass tests at each intermediate state.
- Determine the correct final migration and execute the coherent sweep.
- Do not invent an incremental-green requirement that the user did not give.
- During a declared semantic-only migration, do not run tests, hooks, or Sage.
- Commit those migration units with the user's declared hook posture.
- Run the separate integrated verification pass only after the semantic migration finishes.

## Architecture before local repair

- A repeated local defect often indicates one missing mathematical foundation.
- Fix that foundation before patching its instances.
- If a module can exist without a ring, forbid ringless construction.
- Do not hunt only for the current ringless object.
- If a formed module delegates through `forget_form`, fix its mathematical ownership.
- Do not add another forwarding method.
- If many leaves restate set behavior, fix the category construction chain.
- Do not optimize the forwarding calls.
- If prior art already solved the problem, migrate it before deriving a new mechanism.
- Read the archived implementation and its reasons.
- A row marked superseded is a claim requiring semantic comparison.
- It is not evidence that the older implementation adds nothing.
- Preserve small load-bearing details from the older implementation.
- Do not infer their irrelevance from file size.

## Fundamental-assumption reset

The conditions below require a frame reset rather than a local correction.

- A user states that a claimed mathematical object already works in live notebooks.
- A user identifies a category, functor, or adjunction that the implementation does not model.
- A user shows that the current code permits a mathematically invalid object.
- A user shows that the work built a parallel hierarchy instead of changing the live hierarchy.
- Two corrections remove mechanisms introduced by the same design frame.
- A local patch produces another defect at the same ownership boundary.
- An acceptance check measures a toy, count, or checker rather than the requested object.

When one condition occurs:

- Stop the local edit.
- Restate the requested mathematical object in standard terms.
- Identify the live repository object that must model it.
- List the foundational assumptions used by the current approach.
- Check those assumptions against source, runtime objects, and prior art.
- Remove every inference whose premise failed.
- Resume only from the corrected mathematical model.
- Do not ask the user to select the next probe when the repository can answer it.
- Do not manufacture ambiguity after the user has already decided the architecture.

## Work selection and proof

- A count of type errors does not measure architectural correctness.
- A count of passing tests does not measure mathematical correctness.
- A count of migrated files does not measure semantic completion.
- A green toy specimen does not prove migration of the live surface.
- State the mathematical claim that the current artifact makes true.
- Verify that claim on a concrete repository-owned object.
- Choose specimens that exercise the real category, constructor, element, and morphism paths.
- Use notebook research objects when the requirement concerns notebook research.
- Do not substitute a nearby proxy object.
- By-eye review during a semantic migration concerns definitions, organization, and types.
- Automated verification belongs to its separately declared pass.
- Do not report unverified work as deferred verification.
- It is simply unverified until that pass occurs.

## Repository organization

- Organize the preamble by mathematical ownership.
- The tree should expose the category hierarchy to a mathematician.
- Place generic constructions at the highest valid categorical level.
- Keep value-level form morphisms distinct from categories of formed modules.
- Keep research-specific computations below the general structures they use.
- Preserve a clear root for categories, functors, homsets, subobjects, and named specimens.
- A new leaf should have one obvious filing location.
- Adding that leaf should require only its new data and immediate-supercategory construction.
- Do not keep the same mathematical notion in an archive and the live preamble after migration.
- Do not create parallel sources of truth.

## QC and tooling house rules

- Global QC belongs in `ai-review-ci`.
- Local repositories delegate to that global owner.
- Sage source must be lowered to Python before Python type analysis.
- Type checkers inspect the lowered Python, not raw `.sage` syntax.
- The custom Sage parser must be globally available to the lowering path.
- `sage-stubs` supplies the global Sage type surface.
- Owned tools track the latest upstream default branch.
- Do not create fixed revision policy for fast-moving local projects.
- Diagnostic recipes must preserve detailed errors, warnings, and issues in logs.
- Their final output must name the detailed log paths.
- Test execution must produce wall-time and profiling artifacts.
- Agents should inspect those artifacts instead of rerunning long commands for omitted output.
- These rules govern the later verification pass.
- They do not authorize running verification during a semantic-only migration.

## Communication and research style

- Lead with the mathematical result or unresolved mathematical point.
- Explain repository objects in plain technical English before using local shorthand.
- Do not report internal batch labels without their mathematical referents.
- Do not report agent waves, token use, idle notices, or administrative counts.
- Do not describe an analysis report as if its mathematics landed in the repository.
- State what was migrated, synthesized, corrected, or left unresolved.
- Explain the mathematical meaning of a discrepancy.
- Do not substitute tourist commentary for a construction, theorem, definition, or source edit.
- Do not use vague phrases such as `missing machinery` without naming the missing objects and morphisms.
- Do not call work deferred when the assigned task requires its completion.
- Do not ask the user to decide questions that mathematical analysis should decide.
- Ask only when the remaining alternatives encode different research choices.
- Preserve long-lived decisions in their owning plan during a long migration.
- Do not let important architecture exist only in chat.
- A plan records settled mathematical direction.
- It does not replace the code, proof, or migrated research.

# Categorical constructions own structural relations

The preamble has categories, method classes, and the category graph. It has no
independent behavior-composition layer.

- Do not call a preamble component a `mixin`.
- Do not insert a hand-written Python base to state a mathematical relation.
- State the relation in the category graph.
- Class inheritance can implement the graph after category placement.
- Class inheritance must never replace categorical placement.
- `ParentMethods`, `ElementMethods`, and `MorphismMethods` expose operations owned
  by a category.
- They are not an invitation to build a second class graph.

The set of core categorical constructions is small. Inspect all existing owners
before creating another construction.

- Start with `Cat.Object`, `SliceOver`, `CosliceUnder`, `Product`, `Coproduct`,
  `Biproduct`, `TensorProduct`, `Kernel`, and `Cokernel`.
- Inspect the owned module-level `Subobjects` construction as part of the same
  analysis.
- Use this subtree as the canonical construction vocabulary.
- Do not create a local helper for a relation already represented there.
- Do not let an owned category silently use Sage's parallel construction.
- Resolve the construction owner instead of patching each call site.
- Do not keep two construction paths for the same mathematical construction.

Modules with varying base rings project to the category of rings. Modules over a
fixed ring form one fiber of that projection.

- A construction that requires one base ring belongs inside that fiber.
- Scalar extension and scalar restriction connect different fibers.
- Do not encode the same-base condition through Python inheritance or method
  resolution.
- Products, coproducts, tensor products, kernels, and cokernels must preserve the
  selected base ring when their definitions require it.
- A category join that returns `None` from `base_ring()` exposes an incorrect
  categorical relation.
- Fix the join or construction that lost the base ring.
- Do not add a local `base_ring()` override before that relation is correct.

A formed module is a module equipped with a form morphism. It is not a wrapper
around another module.

- Never inspect `__dict__` to discover mathematical structure.
- Never recover a deleted wrapper field through direct storage access.
- Ask the category-owned interface for the form and its defining module.
- A construction must define its action on objects and morphisms.
- A parent-only result does not establish a categorical construction.

Let `i: A -> M` be a subobject inclusion. For a bilinear form
`b: M tensor M -> R`, the induced form is `b compose (i tensor i)`.

- Implement formed subobjects through this functorial pullback.
- For another form classifier, apply its source functor to `i` before composition.
- Do not infer formed-subobject behavior from `_form` or `_module` storage fields.
- The subobject construction owns this transport.

When a correction identifies an existing construction subtree, return to that
owner immediately.

- Do not reduce the correction to a naming change.
- Do not continue a local field repair after the ownership error is known.
- Trace the canonical constructor, category join, parent construction, morphism
  action, and inherited methods as one path.
- A local patch is incomplete while that path remains incoherent.
- If local edits stop producing mathematical progress, return to the categorical
  construction. Do not stop the assigned work.
