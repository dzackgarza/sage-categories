# Kernel plan and leaf-boundary review

Date: 2026-08-28

## Verdict

The active kernel plan is incomplete.
Its step-10 phase also lacks a status field and names two files that no longer exist.

The current leaf methods often state their mathematics clearly.
The surrounding category code still contains kernel refinement, cache, class-compilation, and type-construction work.

Two defects are more serious than that wiring.
The cardinality functor cannot act on every object in its declared domain (V2).
Category-owned methods resolve a structural route to reach state that should already be on
their receiver, which is the cause of the leaf wiring rather than another instance of it
(V10).

## Review boundary

The active workstream is
`PLAN-pr-8-functorial-kernel-completion`.
The parent feature and current plan graph both select it.

This review read the complete active plan and its complete step-10 phase.
It also read the governing README, policy rows, and relevant specification sections.

The leaf scan covered every Python source file under these current subtrees:

- `src/sage_categories/sets`;
- `src/sage_categories/number_sets`;
- `src/sage_categories/posets`;
- `src/sage_categories/ordinals`.

The scan checked imports, declarations, refinement calls, duplicate class metadata, cache decorators, and public type assembly.
Each finding then used the complete local owner or the cited source range.

This report does not certify every mathematical algorithm in those subtrees.
The listed violations already disprove full plan and leaf compliance.

## Violations

### V1. The active plan is incomplete

Severity: Blocking

- Searched: the complete active plan, its complete step-10 phase, and each live source named below.
- Found: the plan remains `in-progress` and leaves two completion conditions open.
- Found: the step-10 phase has unresolved success criteria and no status field.
- Found: the phase names two files that no longer exist.
- Found: five of the nine listed defects are corrected in current source. These are the plan working. A defect register records what the plan set out to remediate, so an entry repaired in the tree is the intended end state, not a disagreement with it. The reviewable question is which entries remain open.
- Conclusion: I conclude that the plan is incomplete: register entries remain open, and the phase carries unresolved criteria, a missing status field, and two dead file references.
- Confidence: High.
- Gaps: this review did not inspect remote pull-request state.

Evidence. The plan's own state is open:

- The plan declares `status: in-progress` at
  `.agents/plans/features/FEATURE-functor-owned-category-framework/plans/PLAN-pr-8-functorial-kernel-completion/PLAN-pr-8-functorial-kernel-completion.md:8`.
- The owner review and public witness matrix remain open at the same file, lines 1248-1249.
- The phase still names absent files at
  `.agents/plans/features/FEATURE-functor-owned-category-framework/plans/PLAN-pr-8-functorial-kernel-completion/PHASE-pr-8-step-10-reconciliation/PHASE-pr-8-step-10-reconciliation.md:42`
  and line 99.

These five register entries are remediated and need only to be marked closed:

- The `denotes_diagram` entry at line 1260. Current code uses category containment at
  `src/sage_categories/cat/functors.py:651`.
- The represented-functor entry at line 1262. Current code defines it at
  `src/sage_categories/cat/category.py:519`.
- The `CategoryPoint` entry at line 1264. Current code declares a static class in
  `src/sage_categories/kernel/`.
- The `Subobjects()` name-collision entry at line 1265. Current code uses an extra-named
  product-subobject family at `src/sage_categories/cat/constructions.py:428`.
- The identity-only witness entry at line 1267. Current code has one at
  `tests/cat/test_two_morphisms.sage:254`. It states no mathematical proposition.

Governing sources:

- `POL-DOC-012` requires normalization from the latest decision.
- `POL-DOC-013` limits an executing plan to active decisions, requirements, order, and acceptance.
- `POL-SCOPE-009` requires review of live owners and public call paths.

Required correction:

- Mark the five remediated register entries closed. Do not rewrite the register on the
  ground that it lists them.
- Convert each entry that is still open into an active requirement with an owner and
  acceptance statement.
- Give the step-10 phase a status field and remove its two dead file references.
- Keep completed work and provenance in the existing provenance phase.

### V2. The cardinality functor is not a functor on its declared domain

Severity: Critical

- Searched: `specs/cardinality.md`, `POL-SET-010`, `POL-SET-025`, and the complete functor implementation.
- Found: the specification declares `#: core(Sets()) -> Cardinal()`.
- Found: a set cardinality can be `Unknown`.
- Found: the object map asserts that every source object has an exact cardinal.
- Conclusion: I conclude that the implementation is partial on its declared domain.
- Confidence: High.
- Gaps: none within the stated object map.

Evidence:

- The functor appears at `specs/cardinality.md:435`.
- Unknown cardinalities are required at `specs/cardinality.md:470` and `CONTRIBUTING.md:703`.
- `cardinality_functor()` asserts exact cardinality at
  `src/sage_categories/sets/cardinals.py:993`.
- It still declares `core(Sets())` as its domain at line 1001.
- `Unknown` is not a cardinal under `POL-SET-025`.

Governing sources:

- `POL-SET-010` permits `Cardinal | UnknownClass` as a set cardinality.
- `POL-SET-025` excludes `Unknown` from `Cardinal()`.
- `specs/functor.md:983` requires every functor to satisfy the functor model.

Required correction:

- Decide the mathematical domain of the cardinality functor.
- Narrow its domain to objects with an exact cardinal, or revise the cardinality model.
- Do not keep the current assertion under the current domain.

### V3. Named number sets bypass the point-category architecture

Severity: High

- Searched: `Cat().Point`, all current number-set sources, and the named-object policies.
- Found: `ZZ`, `NN`, `QQ`, and `RR` construct set objects, then call kernel `refine` directly.
- Found: `Primes` is a subset object with another direct kernel refinement.
- Conclusion: I conclude that named-object placement remains leaf-owned kernel work.
- Confidence: High.
- Gaps: this finding applies to the five inspected named number sets.

Evidence:

- The generic point-category path is at `src/sage_categories/cat/category.py:1100`.
- Direct leaf refinement occurs at:
  - `src/sage_categories/number_sets/integers.py:74`;
  - `src/sage_categories/number_sets/positive_integers.py:71`;
  - `src/sage_categories/number_sets/rationals.py:73`;
  - `src/sage_categories/number_sets/reals.py:70`;
  - `src/sage_categories/number_sets/primes.py:38`.

Governing sources:

- `POL-CAT-083` assigns named-object placement to a parameterized point category.
- `POL-LEAF-035` assigns same-object refinement to the generic property constructor.
- `POL-LEAF-054` excludes refinement machinery from leaf code.
- `POL-LEAF-057` requires named objects to state known properties by strongest placement.
- `POL-KERNEL-002` and `POL-KERNEL-012` assign refinement to the kernel.

Required correction:

- Use the `POL-CAT-083` point-category path for each named object.
- Let its selected point functors establish every known ambient and property placement.
- Remove direct kernel refinement from the number-set modules.

### V4. The property-subcategory API forces duplicate class metadata into leaves

Severity: High

- Searched: the complete `PropertySubcategory` declaration and every current leaf call site.
- Found: its constructor requires a dictionary that classifies implementation classes.
- Found: `Sets()` and finite posets pass explicit object-class dictionaries.
- Conclusion: I conclude that the category API requires the leaf shape that policy forbids.
- Confidence: High.
- Gaps: custom full subcategories outside the current leaf subtrees were not classified here.

Evidence:

- The class-dictionary parameter is at `src/sage_categories/cat/properties.py:103`.
- The same class reads that map at `src/sage_categories/cat/properties.py:125`.
- `Sets()` passes a class dictionary at `src/sage_categories/sets/category.py:121`.
- `Posets().Finite()` passes one at `src/sage_categories/posets/category.py:382`.
- Finite-poset properties pass four more at `src/sage_categories/posets/finite.py:211`.

Governing sources:

- `POL-LEAF-051` forbids a second class table beside mathematical declarations.
- `POL-LEAF-054` excludes compiler metadata from leaves.
- `POL-LEAF-059` requires direct nested implementation classes.
- `specs/leaves.md` requires one declared class for each mathematical kind.

Required correction:

- Make each property subcategory an ordinary category class that declares
  `ObjectType`, `ElementType`, and `MorphismType` directly. Follow Sage's general axiom mechanism: declare the axiom once, define the
  implementing class independently, and wire the two with one declared field, as
  `_base_category_class_and_axiom` does (`POL-LEAF-059`).
- Make the generic property owner read those classes directly.

### V5. `Posets()` owns generic element, cache, and inverse machinery

Severity: High

- Searched: the complete poset category, finite-poset category, and their selected functors.
- Found: a poset object stores a point cache.
- Found: `element()` constructs a morphism, refines it, and updates that cache.
- Found: the category builds points through another private cache.
- Found: `inverse_morphism()` owns an inverse cache and reconstructs the inverse locally.
- Found: a mathematical method uses the kernel `retained_method` decorator.
- Conclusion: I conclude that the poset leaf contains kernel-owned structural work.
- Confidence: High.
- Gaps: this finding does not reject the local order algorithms.

Evidence:

- The object-level element cache is at `src/sage_categories/posets/category.py:71`.
- Manual element construction and refinement are at lines 97-110.
- The kernel cache decorator appears at lines 125-130.
- Category-level element construction is at lines 389-399.
- Local inverse construction and retention are at lines 428-434.
- The finite-poset functor refines its morphism image directly at
  `src/sage_categories/posets/finite.py:231`.

Governing sources:

- `POL-KERNEL-001` assigns generic object, element, and morphism construction to the kernel.
- `POL-KERNEL-017` assigns selected-path composition and constructor data to the kernel.
- `POL-LEAF-023` excludes inherited caches from property refinements.
- `POL-LEAF-025` stops leaf work at compiler-path machinery.
- `POL-LEAF-053` excludes framework decorators from mathematical methods.
- `POL-LEAF-056` assigns isomorphism inversion to its generic morphism category.
- `POL-CAT-079` assigns forced operations to their highest mathematical owner.

Required correction:

- Let the kernel construct points. Keep generalized elements in their morphism categories.
- Let the isomorphism category own inversion and its retained inverse.
- Keep `Posets()` focused on relations, monotone maps, order predicates, and induced orders.

### V6. Set constructions expose kernel cache and type wiring

Severity: High

- Searched: every set-construction module and the complete `SetsCategory` type assembly.
- Found: product, limit, exponential, subset, and finite-subset code imports a kernel cache decorator.
- Found: these mathematical modules apply that decorator to construction maps.
- Found: `SetsCategory` rebinds compiled public types into neighboring modules at runtime.
- Conclusion: I conclude that set theory still exposes cache and generated-type plumbing.
- Confidence: High.
- Gaps: generated stub correctness was not rechecked.

Evidence:

- Kernel cache imports occur at:
  - `src/sage_categories/sets/products.py:56`;
  - `src/sage_categories/sets/limits.py:49`;
  - `src/sage_categories/sets/exponentials.py:26`;
  - `src/sage_categories/sets/subobjects.py:61`;
  - `src/sage_categories/sets/finite_subsets.py:56`.
- A product projection uses that decorator at `src/sage_categories/sets/products.py:207`.
- A limit projection uses it at `src/sage_categories/sets/limits.py:90`.
- Runtime type rebinding occurs at `src/sage_categories/sets/category.py:429`.

Governing sources:

- `POL-LEAF-053` excludes framework decorators from mathematical operations.
- `POL-LEAF-054` excludes cache and generated-type concerns from leaves.
- `POL-LAYOUT-001` requires the subtree to use its category's language.
- `POL-LAYOUT-017` places generic wiring in private infrastructure.
- `specs/leaves.md:1006` permits the category type, kernel inheritance, and Sage computation only.

Required correction:

- Make universal-construction owners retain projection and injection identities.
- Give set modules stable source-level type owners.
- Remove cache decorators and compiled-type rebinding from mathematical modules.

### V7. Function sets lose a known property at construction

Severity: High

- Searched: the complete function-set constructor and both set constructors it calls.
- Found: `function_set()` computes an exact cardinal when both input cardinals are exact.
- Found: it returns a rule-valued set without strongest property placement.
- Conclusion: I conclude that exact cardinal data does not establish the known property category.
- Confidence: High.
- Gaps: this finding concerns function sets; product and coproduct code now has eager placement cases.

Evidence:

- Exact exponential cardinality is computed at `src/sage_categories/sets/exponentials.py:92`.
- The function returns `sets.rule_valued(...)` at line 94.
- `rule_valued()` only constructs the set at `src/sage_categories/sets/category.py:149`.
- Product and coproduct placement now occurs at `src/sage_categories/sets/products.py:160` and line 246.

Governing sources:

- `POL-CAT-081` requires the strongest property placement known at construction.
- `specs/leaves.md:1000` requires every mathematically established placement.
- `specs/cardinality.md:479` fixes the function-set cardinality rule.

Required correction:

- Place each function set in every property category established by its exact cardinal.
- Use the generic property constructor, not a direct kernel refinement.

### V8. Internal kernel records still stand in for public witnesses

Severity: High

- Searched: the complete step-10 witness-debt section and its named current tests.
- Found: current tests still assert on compiler nodes, routes, transport, classes, and class tables.
- Found: the active plan still leaves the public witness matrix incomplete.
- Conclusion: I conclude that these checks cannot discharge the public acceptance rows.
- Confidence: High.
- Gaps: the internal checks can remain as kernel unit checks if they prove a separate invariant.

Evidence:

- The phase records the debt at
  `.agents/plans/features/FEATURE-functor-owned-category-framework/plans/PLAN-pr-8-functorial-kernel-completion/PHASE-pr-8-step-10-reconciliation/PHASE-pr-8-step-10-reconciliation.md:112`.
- Compiler routes remain in `tests/cat/test_points.sage:102`.
- Transport and compiler nodes remain in `tests/kernel/test_transport.sage:203`.
- Route helpers remain public witness assertions in `tests/kernel/test_routes.sage:116`.
- Compiled class dictionaries remain in `tests/kernel/test_compiler.sage:435`.

Governing sources:

- `POL-TEST-003` requires intended behavior instead of implementation layout.
- `POL-TEST-006` says routes, class identities, and caches do not prove inherited behavior.
- `POL-TEST-010` limits a passing test to the proposition it executes.

Required correction:

- Keep internal checks only under explicit kernel invariants.
- Prove each acceptance row through a public mathematical call and semantic result.

### V9. Step 10 still contains live specification gaps without active work

Severity: High

- Searched: the complete step-10 phase, all source spellings, the set-object implementation, and the public export list.
- Found: chosen set enumeration still lacks the specified indexing, position, and injection methods.
- Found: the main export list still omits specified cardinal and ordinal public types.
- Conclusion: I conclude that step 10 has not met its divergence-resolution criterion.
- Confidence: High.
- Gaps: this review did not decide the design of these missing public methods.

Evidence:

- The phase lists these gaps at lines 24-39 of its file.
- The set API requirement is at `specs/sets.md:397`.
- The complete set-object implementation surface is at
  `src/sage_categories/sets/objects.py:116`.
- The required export surface is at `specs/cardinality.md:493`.
- The complete `sage_categories.all` export list is at `src/sage_categories/all.py:48`.

Governing sources:

- The phase success criterion requires every divergence to be resolved.
- `POL-DOC-013` requires active work and acceptance in the executing plan.
- `POL-SCOPE-009` requires live owners instead of report status.

Required correction:

- Add each still-required surface to active dependency order and acceptance.
- Remove stale phase entries only after live source satisfies their specifications.

### V10. Category-owned methods resolve a route to reach their own state

Severity: Blocking

- Searched: `cat/category.py`, `cat/functors.py`, and every call site under `src/sage_categories/sets`.
- Found: a category exposes a target-category image accessor, although only a named functor can own an image.
- Found: thirteen `Sets()`-owned methods call it before reading their own state.
- Found: the functor API used by the leaves hands the kernel an already-constructed target object instead of construction data for the target's constructor.
- Conclusion: I conclude that the compiled class hierarchy and the retained data disagree. A poset is a Python subclass of the compiled `Sets()` object class, but its set state was never initialized from its own construction data, so each `Sets()` method bridges the gap by hand.
- Confidence: High.
- Gaps: this review did not enumerate the change set in `cat/` needed to move every functor onto the constructor-conversion path.

Evidence:

- The category-level image accessor is at `src/sage_categories/cat/category.py:140`.
- Ten call sites are in `src/sage_categories/sets/objects.py`; three are in `src/sage_categories/sets/maps.py`.
- `Functor.retain_object_constructor_conversion` at `src/sage_categories/cat/functors.py:253` is the constructor-threading path. One call site uses it, at `src/sage_categories/sets/cardinals.py:759`.
- The alternate functor retention path is at `src/sage_categories/cat/functors.py:293`. Its conversion wraps a value the domain's defining data already names.

Governing sources:

- `POL-KERNEL-018` makes `X.f() == F(X).f()` true by threading construction data through ancestor initializers, so a declaring method reads its own state on the receiver.
- `POL-CAT-096` states that a functor has an image and a category does not.
- `POL-CAT-062` and `POL-LEAF-038` forbid fetching a second value to stand for the receiver.
- `POL-LEAF-052` treats one non-mathematical step repeated across methods as a missing kernel derivation.
- `specs/resolution.md`, decision 6.

Required correction:

- Make each selected functor state its target's construction data, not an already-built target object, and let the kernel thread it through the ancestor initializers.
- Delete the category-level image accessor and its thirteen call sites together.

## Leaf assessment

The local mathematics is often close to the intended form.
The number-set predicates use exact Sage decisions and preserve `Unknown`.
Finite-poset operations use one fixed private Sage helper and reconstruct owned results.

The main defect is architectural.
Leaves must still know how refinement, class selection, cache retention, and compiled types work.
That is the work the kernel exists to remove.

SLOP-REPORT-COMPLIANCE: I hereby assert that the above report is formatted in compliance with all slop report requirements.
