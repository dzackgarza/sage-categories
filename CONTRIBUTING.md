# Contributing

This repository implements a categorical foundation for Sage-based mathematics.
Mathematical structure controls the code architecture.

Each coding policy has a permanent identifier of the form `POL-AREA-NNN`. Use these identifiers in code review and design discussion.
Do not reuse a retired identifier.

## Current implementation boundary

| ID | Policy |
| --- | --- |
| `POL-SCOPE-001` | Build the complete tower in the dependency order from `specs/system.md`. Close M0 through M6 before P1 begins. Then follow P1 through P7. |
| `POL-SCOPE-002` | Execute only the active phase and its accepted prerequisites. Keep production leaves blocked until R6 passes. |
| `POL-SCOPE-003` | Implement the complete morphism-category family: `Mor(n, C)`, its fixed-endpoint subcategories `Mor(C)(A, B)`, its endomorphism, monomorphism, epimorphism, isomorphism, and automorphism property subcategories, `Fun([1], C)`, and the slice, coslice, subobject, and superobject categories. |
| `POL-SCOPE-004` | Make object, element, and morphism inheritance work before adding theories that depend on it. |
| `POL-SCOPE-005` | Treat the full owned `Sets()` category as foundational work, not as a finite-set helper library. |
| `POL-SCOPE-006` | Use algebra cardinality and the path from lattice isometries through module homs to set homs only as vertical acceptance examples. Do not implement those higher categories yet. |
| `POL-SCOPE-007` | Judge the project by categorical uniformity, explicit mathematical ownership, functorial reuse, and legibility. Successful computation or compilation alone does not satisfy its purpose. |
| `POL-SCOPE-008` | Make every mathematical declaration auditable by a mathematician. The kernel realizes those declarations. Keep runtime representations private, except the selected public SymPy proposition expression. |
| `POL-SCOPE-009` | Derive architecture from controlling decisions and canonical specifications. Verify an implementation claim against the exact method owners, named functors, constructor obligations, and universal data at one revision. Reports, tests, metadata, and generated projections do not replace either source. |
| `POL-SCOPE-010` | Theory code declares categories and implements their objects, elements, morphisms, functors, constructions, and mathematical operations. |
| `POL-SCOPE-011` | Leaf code is theory code for one category. It states only that category's new data, operations, structure functors, constructors, and lifts. |
| `POL-SCOPE-012` | Kernel code implements category-independent class compilation, private runtime state sharing for selected structure-functor targets, dynamic types, and once-only initialization through Sage's controlled linearization. The owned `Cat()` graph is entirely new; the kernel builds only a private Sage runtime mirror of its implementation edges and never imports Sage's mathematical category graph. Each named functor owns its public images through ordinary actions on completed source values. The kernel contains no category-specific mathematics and reads no second functor description. |
| `POL-SCOPE-013` | Backend-adapter code converts owned mathematical values to and from a computation engine. It does not define the public mathematical interface. |
| `POL-SCOPE-014` | Interpret a primitive ban by its stated purpose and layer. A ban on mathematical classification does not ban implementation-only use inside the kernel. |
| `POL-SCOPE-015` | Apply a bare primitive ban to every layer. Only an explicit layer-specific policy can permit a narrower use. |
| `POL-SCOPE-016` | Keep kernel and backend primitives private. The sole public engine value is an authorized SymPy proposition expression with private nested identity atoms. |

## Shadowed package universe

| ID | Policy |
| --- | --- |
| `POL-SHADOW-001` | Build a package-owned categorical replacement for a significant subset of the standard Sage mathematical surface. Shadow supported Sage names with owned objects rather than re-exporting Sage objects. |
| `POL-SHADOW-002` | Provide `sage_categories.all` as the primary opt-in import surface, analogous to `sage.all`. Its imports expose the supported owned universe under the familiar mathematical names. |
| `POL-SHADOW-003` | Keep the public API closed over package-owned mathematics. Every public operation returns an owned value, typed-query application, universal presentation, or authorized SymPy proposition. |
| `POL-SHADOW-004` | Do not refine, register, or graft arbitrary Sage objects into the owned category hierarchy. Construct the corresponding owned object explicitly when the package supports it. |
| `POL-SHADOW-005` | Give no compatibility guarantee between package-owned objects and ordinary Sage APIs. Treat any duck-typed interoperability as incidental behavior outside the public contract. |
| `POL-SHADOW-006` | Absorb each required Sage construction into the package universe. Use its Sage implementation privately when useful and re-express its public behavior through owned categorical APIs. |
| `POL-SHADOW-007` | Treat importing `sage_categories.all` as a commitment to the package universe. Unsupported ordinary Sage constructions and their downstream code remain outside the guaranteed interface. |

For example, shadowing `ZZ` means that a finite-rank free `ZZ`-module, its elements, its products, and every later supported construction remain package-owned.
If elliptic curves are not yet owned, ordinary Sage elliptic-curve code receives no guarantee merely because it internally uses Sage integers or free modules.
The package must absorb the elliptic-curve construction before claiming that workflow.

## Mathematical model

| ID | Policy |
| --- | --- |
| `POL-MATH-001` | Identify the mathematical objects, elements, morphisms, categories, functors, and universal properties before choosing Python representations. |
| `POL-MATH-002` | Model a named category as a category, not as a class with similarly named methods. |
| `POL-MATH-003` | Model a named functor with an object map and a morphism map. |
| `POL-MATH-004` | Model a natural transformation by its components and naturality data. |
| `POL-MATH-005` | Keep a mathematical object distinct from a presentation, coordinate tuple, matrix, or computation-engine value. |
| `POL-MATH-006` | Keep an element distinct from its image under a morphism. |
| `POL-MATH-007` | Store chosen mathematical structure as mathematical data, usually an object or morphism in an owned category. |
| `POL-MATH-008` | Do not duplicate data that a defining morphism already determines. |
| `POL-MATH-009` | Put each operation at the weakest categorical level whose hypotheses imply it. |
| `POL-MATH-010` | Implement the general mathematical notion and obtain special cases by restriction or specialization. |
| `POL-MATH-011` | Use established mathematical terminology. Name each operation by the structure that owns it. |
| `POL-MATH-012` | Treat a missing general construction as a foundational gap. Do not patch only one existing example. |
| `POL-MATH-013` | Keep axiomatic truths distinct from runtime algorithms. |
| `POL-MATH-014` | Use an inspected theorem to justify the owning implementation. Cite it in source documentation and encode only its mathematical consequence. Never use the citation or theorem prose as runtime validation. |
| `POL-MATH-015` | Treat a form as a callable object of its fixed-endpoint morphism category `Mor(C)(A, B)`. A matrix can represent a form but cannot define the general notion. |
| `POL-MATH-016` | Refine a result into a property subcategory when its defining construction, an exact computation, an explicit hypothesis, or an inspected theorem establishes the property. Runtime derivation is not required for a theorem-backed fact. |
| `POL-MATH-017` | Return an object in the strongest category established by available mathematics. Never represent mathematical evidence with certificate classes, proof records, prose fields, opaque proof tokens, marker objects, or justification wrappers. |
| `POL-MATH-018` | Prefer kernels, cokernels, exact sequences, fibers, cofibers, pullbacks, limits, and colimits over element-wise definitions. |
| `POL-MATH-019` | State each public definition so it remains meaningful in a category without elements. Treat element-wise formulas as implementations or consequences. |
| `POL-MATH-020` | Treat one Python realization in different categories as different mathematical objects when their structure maps differ. |
| `POL-MATH-021` | Preserve the base category and structure morphism in every parent, type, and morphism that depends on them. |
| `POL-MATH-022` | State the weakest algebraic hypotheses that make a definition or algorithm valid. |
| `POL-MATH-023` | Open and inspect a mathematical source before adding a definition or citation. Record the exact theorem, section, table, or page that supports it. |
| `POL-MATH-024` | Treat definitionally known and theorem-established values as exact knowledge. When no runtime algorithm can derive the value, the owning construction supplies the typed mathematical conclusion directly. The inspected theorem justifies that implementation in source documentation; Python does not prove it. |
| `POL-MATH-025` | Let `ask()` return `Unknown` only when defining data, explicit hypotheses, construction theorems, inspected sources, and available exact algorithms do not determine the proposition or typed query. The absence of a Python derivation does not make a theorem-established result unknown. Never convert `Unknown` to a Boolean through an unrelated proxy. |
| `POL-MATH-026` | A runtime API never accepts, stores, inspects, or branches on prose that purports to establish a mathematical proposition. This ban includes arguments or fields named `theorem`, `proof`, `certificate`, `citation`, `justification`, `evidence`, `trusted_reason`, and every renamed equivalent. |
| `POL-MATH-027` | Renaming theorem prose as metadata, an opaque token, a marker type, a record, or a callback that returns the same text does not make it mathematical evidence. Runtime evidence must be typed mathematical data, an exact predicate result, an explicit hypothesis, or a construction rule. |
| `POL-MATH-028` | A theorem-backed method constructs its result directly in the established property category. That category placement is the typed mathematical conclusion. The citation remains documentation. Runtime stores no proof text or parallel result record. |
| `POL-MATH-029` | For a proposition, only the result `True` establishes it. Tests such as `decision is not False`, fallthrough, and absence of rejection never turn `Unknown` into evidence. An explicit hypothesis or construction theorem is a separate source of knowledge. |
| `POL-MATH-030` | Prefer a defining construction or theorem over exhaustive verification, even when verification terminates. Finiteness alone does not justify enumeration when the construction already establishes the property. |
| `POL-MATH-031` | Make a mathematical fact explicit through the semantic value that states it: category placement, an exact type, a defining morphism, a functor, a universal construction, a named mathematical construction, an exact predicate result, or an active-session assumption. Never create runtime metadata merely to repeat that fact. |
| `POL-MATH-032` | Treat construction authority as the category, functor, universal construction, or named method whose definition establishes the result. This authority is static mathematical ownership, not runtime data. Never pass, store, register, or inspect an authority token, authority object, marker, or callback to authorize category refinement. |
| `POL-MATH-033` | Treat ordinary category theory and the stated mathematical definitions as the source model. A missing, unclear, or failing Python representation does not make the mathematics unresolved. Derive the representation from the definition, or report the missing foundational category, functor, morphism, construction, or type. |
| `POL-MATH-034` | Give every mathematical truth question one category-owned predicate meaning and one public SymPy `Predicate` representation. Applying it constructs a SymPy proposition. Represent every partial value question as a category-owned typed query with one exact result category. Typed queries never enter SymPy Boolean algebra. Forming either application performs no evaluation. Only `ask()` returns `True`, `False`, an owned result, or Sage `Unknown`. |
| `POL-MATH-035` | Ask every proposition before an assertion or branch. Write `decision = ask(proposition)`, assert that it is not `Unknown` where a decision is required, and then use the decision. The proposition's Python truth value raises. |
| `POL-MATH-036` | Treat Sage as an implementation and computation system, not as a proof assistant for category theory or homotopy theory. The repository never tries to prove or certify categorical laws, universal properties, coherence, equivalences, or property implications. |
| `POL-MATH-037` | Trust the code writer to choose the correct category or property subcategory from external mathematics. Constructing a value directly in that category is the repository assertion of the stated theorem. The constructor performs no proof, certification, search, or validation of that theorem. |
| `POL-MATH-038` | Express every categorical-core requirement through standard category theory or homotopy theory before choosing a Python mechanism. Use named categories, functors, natural transformations, fibrations, Kan extensions, universal constructions, and their compositions. Do not replace a missing mathematical construction with a verifier or certificate system. |
| `POL-MATH-054` | Reserve "the kernel owns X" for machinery, and write "the kernel implements X" whenever `X` is a mathematical object. `Cat`, `Mor(n, C)`, `Fun(C, D)`, the property subcategories, and the standard functors are defined by this repository and read as mathematics; the kernel realizes them and no leaf redefines them. The word matters because ownership carries two meanings here - who implements a thing, and whether a thing is inside the black box - and using it for both puts mathematical objects outside mathematical audit (`POL-MATH-039`). Category-owned implementation classes keep the word: a category does own its `ObjectType`, `ElementType`, and `MorphismType`. |
| `POL-MATH-055` | Give each mathematical fact and public operation one semantic owner: its category, functor, property subcategory, universal presentation, named construction, or category-owned implementation class. Do not add a second runtime or generated entity that restates the same fact. A repair moves the responsibility to the standard owner and deletes the duplicate entity. Renaming it does not change the architecture (D121). |
| `POL-MATH-039` | Every mathematical declaration is audited by a mathematician, and the kernel is not. The split is between a declaration and the wiring that realizes it, never between general and specific mathematics: `Cat`, `Mor(n, C)`, `Fun(C, D)`, the property subcategories, and `Sets()` are all mathematical objects this repository defines, and all are read as theory. What no mathematician reads is the machinery that turns those declarations into working Python - class building, linearization, private runtime state sharing, caches, descriptors, refinement mechanics. Theory code must expose the standard definition, its defining data, and the construction line that asserts each nontrivial categorical property, and must keep reflection, dispatch, transport, and computation representations outside that reading path. The kernel should adhere to precise mathematics where it can, but it is judged only by whether the declarations above read and write like standard mathematics; do not hold it to the theory layer's standard and do not build machinery to make it meet one (`POL-MATH-036`). |
| `POL-MATH-040` | Support each nontrivial categorical declaration with an inspected external source. Use an exact theorem, definition, section, page, tag, or stable link from a textbook, a relevant item in the local Zotero library, nLab, the Stacks Project, Kerodon, or a primary paper. Put the citation on the construction line or in its immediate source documentation. |
| `POL-MATH-041` | Treat citations, tests, runtime checks, and successful computations as aids to human audit. None certifies the categorical mathematics. The typed construction records what the writer asserts; the source lets a mathematician audit that assertion. |
| `POL-MATH-042` | Register a SymPy handler only for a predicate with an exact algorithm on its declared semantic domain. Never add a route that purports to prove a general category-theoretic property. Return `None` when the handler cannot decide the proposition. |
| `POL-MATH-043` | Treat `Cat` as an abstract universe whose foundation is unspecified. Use only the structure that the repository explicitly declares. A declared ordinary or 2-categorical operation does not select a set-theoretic, simplicial, enriched, or higher-categorical realization. |
| `POL-MATH-044` | A mathematical term imports only its explicit repository definition. Do not infer surrounding theory, laws, properties, or constructions from the term alone. |
| `POL-MATH-045` | Fix each mathematical kind, owner, and relation in a declaration before runtime. Derive runtime classes and constructor paths from those declarations. Do not add a second runtime classification of the same fact. |
| `POL-MATH-046` | A structure functor `F: C -> D` is an ordinary functor returned by `C.structure_functors()` as an edge of the new owned implementation graph. This plays a compiler role analogous to Sage's `super_categories()` relation without reusing or translating Sage's mathematical graph. Its two ordinary actions are its complete declaration and accept source values whose own local state is initialized. The kernel selects `D`'s applicable implementation classes and makes inherited execution work on the source value. This Python inheritance states neither a subcategory relation nor an identification with `F(x)`. Only a declared subcategory monomorphism states containment. The named functor constructs the separate image `F(x)` (`POL-CAT-096`, D123). |
| `POL-MATH-047` | Apply inherited operations to the structured source instance through ordinary Python method resolution. If `f` belongs to `D.ObjectType`, then `x.f()` and `F(x).f()` have the same mathematical value. The public functor call still returns the separate image constructed by `F`. |
| `POL-MATH-048` | A category specifies `C.ObjectType`, `C.ElementType`, and `C.MorphismType` directly. The kernel constructs each class dynamically. For each structure functor `F: C -> D`, `C.ObjectType` inherits `D.ObjectType`. The applicable `C.ElementType` and `C.MorphismType` classes inherit the corresponding target classes as compiler consequences of selection. |
| `POL-MATH-049` | State the current architecture in permanent documentation. Put former implementations and their reasons in Git history. Keep prohibited terms only in the deny-list in [specs/glossary.md](specs/glossary.md). |
| `POL-MATH-050` | Before editing agent-facing documentation, read the required distinctions in [specs/glossary.md](specs/glossary.md). Use the exact mathematical owner and public spelling. |
| `POL-MATH-051` | Record only the current vocabulary. Put superseded names and their reasons in Git history, not in current documentation. |
| `POL-MATH-052` | A source comment, plan, report, policy, or generated file cannot create a second spelling for an owned category, functor, construction, proposition, query, or runtime operation. |
| `POL-MATH-053` | Use the required distinctions in [specs/glossary.md](specs/glossary.md) for points, generalized elements, functors, implementation classes, images, and inherited execution. Do not infer an alternative term from nearby source. |

For example, an owned constructor for `RR` records its cardinality as $2^{\aleph_0}$.
The implementation cites the supporting theorem in source documentation.
Runtime stores the typed cardinality; it does not derive uncountability or carry theorem prose.

### Trust boundary for the categorical core

The categorical core is executable mathematical notation. It is not a formalization in
a proof assistant. Sage cannot certify that an arbitrary functor is full, that a square
is a pullback in every model, or that a declared universal construction satisfies its
universal property.

The code writer determines these facts from external mathematics. The writer then uses
the constructor of the exact category that states the fact. For example, a known full
functor is constructed through `Fun(C, D).Full()`. That call asserts fullness. It does
not run a fullness test or create a proof object.

When the assertion is not immediate from the standard definition, place an exact source
reference on that construction line or in its immediate documentation. Suitable sources
include textbooks and papers in the local Zotero library, nLab, the Stacks Project,
Kerodon, and primary arXiv papers. Inspect the cited statement before using it.

A mathematician audits every mathematical declaration by comparing its categories,
morphisms, functors, natural transformations, universal data, and compositions with those
sources. `Cat` and the functor categories are included: they are objects this repository
defines and they read as mathematics. Keep that code in that order, and do not insert
certification machinery between the mathematical definition and its typed construction.
None of it applies to the wiring that realizes those declarations, which no mathematician
reads.

## Foundational architectural ontology and false priors

| ID | Policy |
| --- | --- |
| `POL-ONT-001` | Treat raw Python values (`Datum`) solely as private carrier representations, never as members or elements of any category. An element exists only as a morphism $x: \mathbf{1} \to X$ owned by a specific parent object $X$. Categories contain only category-owned `CategoryPoint` instances. |
| `POL-ONT-002` | Make every mathematical constructor total on a single exact domain. Keep category refinement ($X \mapsto X$ placed in $\mathcal{P}$) strictly distinct from object construction from carrier data ($\text{data} \mapsto X$). Never create overloaded constructors that perform runtime type sniffing or fallback dispatch. |
| `POL-ONT-003` | Evaluate category membership `X in C` strictly through the three-valued categorical proposition $\operatorname{ask}(C.\operatorname{membership\_proposition}(X))$. Never treat `in` as a container item check or query it on raw carrier data. Use `is_placed(X, C)` to test established category placement. |
| `POL-ONT-004` | Never weaken or strip a categorical classification or subcategory placement (such as `Monomorphisms()`, `Epimorphisms()`, `Isomorphisms()`) to bypass a runtime error or constructor failure. Repair the underlying constructor or handler registration instead. |
| `POL-ONT-005` | Never widen an exact semantic type (e.g. `Poset`, `SetMap`) to a generic ancestor type (e.g. `CategoryOfCategories.ElementType`, `CategoryPoint`) to resolve import cycles or forward-reference errors. Resolve module import ordering or defer handler registration instead. |
| `POL-ONT-006` | Inspect established placement via `is_placed(X, C)` inside property deduction handlers. Never invoke active deduction via `X in C` or `ask()` within complementary property handlers, which triggers infinite mutual deduction cycles. |
| `POL-ONT-007` | Treat raw Python callables (`lambda`, functions) solely as constructor input rules, never as morphisms. Morphisms require explicit category endpoints $A \to B$ and must be constructed through `Mor(C)(A, B)(rule)`. |
| `POL-ONT-008` | Ban catch-all constructors, implicit fallback heuristics, and loose `@overload` sniffing. Provide dedicated explicit constructors of the form `X.from_Y(...)` for distinct input modalities. The main constructor must perform an explicit `match`/`case` on the exact supported input types, route them directly with no fallback paths, and unconditionally raise a hard `TypeError` on the default `case _:`. |
| `POL-ONT-009` | Model mathematical structures using generic categorical constructions (slice, coslice, subobject, quotient, comma, and functor categories) rather than ad-hoc leaf classes or facade parents with ambient pointers. Theory-specific sub-entities (e.g. `Submonoids(M)`, `Subgroups(G)`, `Submodules(V)`) are convenience spellings for the corresponding generic construction `SubobjectCategory(C, X)`. No leaf category may implement bespoke subobject or quotient container classes. |
| `POL-ONT-010` | Perform a mandatory survey of existing generic categorical machinery before implementing any new theory, object, morphism, or construction. Never write greenfield code or bespoke data structures without first verifying whether the requested notion is an instance of an existing categorical construction, structure functor, or universal limit/colimit in `Cat`. |
| `POL-ONT-011` | Ban standalone procedural free functions for mathematical properties, queries, or predicates (e.g. `is_discrete(C)`). Mathematical entities must own their operations as direct methods (e.g. `C.is_discrete()`), inherited on role classes from the most general category whose axioms define them. Standalone functions that accept loose duck-typed arguments are strictly prohibited. |

### `POL-ONT-001`: The False Prior "Sets Are Containers of Python Data"

- **The False Model**:
  - Viewing `Sets()` as a Python wrapper around collections.
  - Treating `(1, 2)` or `((),)` as mathematical objects, assuming mathematical elements are bare Python values.
- **The Internalized Reality**:
  - In `sage-categories`, **there is no global element universe**.
  - A raw Python tuple `(1, 2)` is only private carrier representation (`Datum`). It has no mathematical meaning by itself.
  - A mathematical element exists **only** as a morphism from the terminal object:
    $$x: \mathbf{1} \to X \quad (\text{an owned } \texttt{ElementOfObject})$$
  - Categories contain **only** category-owned `CategoryPoint` instances, never raw Python literals.

### `POL-ONT-002`: The False Prior "Constructors Should Be Convenient Polymorphic Parsers"

- **The False Model**:
  - Designing `__call__` as a flexible Python function that sniffs inputs:
    *"If passed an object, refine it; if passed a tuple, parse it into a set."*
  - When this fails, trying to add `isinstance` checks.
- **The Internalized Reality (`POL-API-021`, `POL-API-028`)**:
  - Mathematical constructors are **total functions with a single exact domain**.
  - **Category Refinement** ($X \mapsto X \text{ with placement in } \mathcal{P}$) is mathematically distinct from **Object Construction from Carrier Data** ($\text{data} \mapsto X$).
  - Merging these two operations into one overloaded `__call__` violates categorical clarity and forces runtime type sniffing.

### `POL-ONT-003`: The False Prior "`in` Is a Python Container Lookup"

- **The False Model**:
  - Treating `x in C` as checking whether `x` is in an internal Python collection on `C`.
- **The Internalized Reality (`specs/undecidable-properties.md`)**:
  - In this architecture, `X in C` is the categorical membership proposition:
    $$\mathrm{ask}(C.\mathrm{membership\_proposition}(X))$$
  - Evaluating `((),) in Sets()` is a category error because raw Python memory structures have no categorical propositions.
  - Checking whether an owned value already carries category placement uses `is_placed(X, C)`, not `in`.

### `POL-ONT-004`: The False Prior "Weaken the Invariant to Fix the Bug"

- **The False Model**:
  - If placing a morphism into `Monomorphisms()` fails during subset creation, constructing a bare morphism in `Mor(Sets())` instead to make the code run.
- **The Internalized Reality (`specs/sets.md`, `POL-FUN-013`)**:
  - Categorical classifications are fundamental mathematical contracts. A chosen subset **must** retain a monomorphism.
  - Never weaken an invariant to suppress a symptom. Fix the constructor or argument preparation that caused the failure.

### `POL-ONT-005`: The False Prior "Widen the Type to Fix the Import"

- **The False Model**:
  - When a type annotation like `poset: Poset` cannot be resolved at module top-level, widening the type to `CategoryOfCategories.ElementType` so Python doesn't raise a `NameError`.
- **The Internalized Reality (`POL-TYPE-001`, `POL-TYPE-018`, `POL-TYPE-019`)**:
  - Types communicate exact mathematical semantics. Type erasure blinds the static checker and violates policy.
  - Fix the module structure, import at module level, or defer handler registration until semantic types exist.

### `POL-ONT-006`: The False Prior "Call `in` Inside Deduction Handlers"

- **The False Model**:
  - Inside `_finite_by_infinite`, querying `ambient in self._infinite` to check if the ambient set is infinite.
- **The Internalized Reality (`specs/undecidable-properties.md`, `specs/sets.md`)**:
  - `ambient in category` re-enters active three-valued proposition deduction (`ask()`).
  - Complementary property handlers calling each other through active deduction cause unbounded mutual recursion.
  - Handlers must inspect already-placed structural facts using `is_placed(ambient, category)`.

### `POL-ONT-007`: The False Prior "Raw Callables Are Morphisms"

- **The False Model**:
  - Passing a bare Python `lambda x: x` into functions or subcategories expecting a morphism.
- **The Internalized Reality (`specs/functor.md`, `specs/sets.md`)**:
  - A lambda function is only mapping rule data (`Rule` / `Datum`), lacking domain, codomain, and category composition laws.
  - A morphism must always be constructed explicitly with endpoints via `Mor(C)(A, B)(rule)`.

### `POL-ONT-008`: The False Prior "Catch-All Constructors with Fallback Heuristics"

- **The False Model**:
  - Writing catch-all `__call__(*args, **kwargs)` constructors or broad `@overload` suites that try to guess user intent, trial-and-error multiple representations, or fall back across loose `if/elif/else` branches.
- **The Internalized Reality (`POL-API-021`, `POL-API-028`)**:
  - Distinct mathematical source representations require **explicit, dedicated constructor methods** of the form `X.from_Y(...)` (e.g. `Sets.from_enumeration(...)`, `Sets.from_rule(...)`, `Posets.from_relation(...)`).
  - The main constructor does an explicit `match`/`case` on *exactly* what types of inputs come in, and routes them directly to the appropriate dedicated constructor.
  - There are **zero fallback heuristics and zero silent coercions**. The default `case _:` branch unconditionally raises a hard `TypeError` or `ValueError`.

### `POL-ONT-009`: The False Prior "Reinventing Generic Categorical Constructions as Ad-Hoc Leaf Facades"

- **The False Model**:
  - Creating a standalone facade class or custom category (e.g. `class Submonoid`, `class Subgroup`) that holds an `ambient` pointer, a `predicate`, and hand-rolled containment logic.
- **The Internalized Reality (`specs/functor.md`, `specs/leaves.md`)**:
  - Subobjects, quotients, pointed objects, and comma objects are **generic categorical constructions** that exist uniformly across any category $\mathcal{C}$.
  - In any category $\mathcal{C}$, for an object $X \in \operatorname{Ob}(\mathcal{C})$, the subobjects form the **Subobject Category** $\mathbf{Sub}_{\mathcal{C}}(X)$—the full subcategory of the slice $\mathcal{C}/X$ spanned by monomorphisms $m: S \hookrightarrow X$. Morphisms between subobjects are commuting triangles in the slice ($m' \circ h = m$).
  - Theory-specific constructors (`Submonoids(M)`, `Subgroups(G)`, `Subsets(X)`, `Submodules(V)`) are convenience spellings for `SubobjectCategory(C, X)`.
  - Generic operations (subobject poset ordering, intersection via pullbacks, image factorization) are implemented once generically, not duplicated across leaf theories.

### `POL-ONT-010`: The False Prior "Greenfield First, Search Later"

- **The False Model**:
  - Receiving an implementation task (e.g. "implement submonoids", "implement products of sets", "implement pullback diagrams"), immediately creating a new file or class, and writing bespoke ad-hoc code from scratch without surveying the existing codebase.
- **The Internalized Reality (`specs/system.md`, `specs/functor.md`)**:
  - Category theory is deeply unified: almost all structural concepts are instances of generic constructions (`Cat`, `Mor`, `Fun`, `SliceCategory`, `SubobjectCategory`, `QuotientCategory`, `Pullbacks`, `Limits`, `Colimits`, `diagrams`).
  - Before writing any implementation code, a mandatory survey of existing generic machinery is strictly required. Hand-rolling code that duplicates or bypasses existing foundational machinery causes architectural drift and code bloat.

### `POL-ONT-011`: The False Prior "Standalone Procedural Helper Functions"

- **The False Model**:
  - Writing module-level standalone functions like `is_discrete(diagram_category)` that accept arbitrary inputs and inspect attributes via loose duck-typing.
- **The Internalized Reality (`POL-MATH-009`, `POL-TYPE-018`, `POL-TYPE-019`)**:
  - Standalone procedural functions allow foreign, duck-typed, or unvetted objects to pass through loosely, creating subtle bugs and bypassing category role compilation.
  - Objects must own their operations directly as methods (e.g. `C.is_discrete()`, `X.cardinality()`).
  - Methods must be defined on the role classes in the **most general category where the concept makes mathematical sense** (e.g. any category $\mathcal{C}$ can ask `C.is_discrete()`), so that all subcategories inherit the operation with full type safety and MRO compilation.

### Core Project Philosophy Summary

| Concept | Python / SWE Prior (The Mistake) | `sage-categories` Architecture (The Truth) | Policy |
| :--- | :--- | :--- | :--- |
| **Elements** | Raw Python values (`1`, `(1, 2)`) | Arrows $x: \mathbf{1} \to X$ owned by a specific parent set $X$ | `POL-ONT-001` |
| **Carrier Data** | The mathematical object itself | Private implementation representation (`Datum`), not in any category | `POL-ONT-001` |
| **Categories** | Collections / registries of objects | Mathematical category structures with role-compiled classes | `POL-ONT-001` |
| **Constructors** | Polymorphic helper functions (`*args`) | Total, single-purpose mathematical operations (`POL-API-021`) | `POL-ONT-002` |
| **Refinement** | Dynamic mutation / wrapper allocation | Same-object placement in subcategory without wrapper classes | `POL-ONT-002` |
| **Membership `in`** | Container item containment | Three-valued proposition evaluation via SymPy / `ask()` | `POL-ONT-003` |
| **Categorical Invariants** | Omit or weaken when failing | Strict mathematical contract; fix root cause | `POL-ONT-004` |
| **Semantic Types** | Widen to avoid import issues | Exact mathematical types; defer handler registration | `POL-ONT-005` |
| **Deduction Handlers** | Call `in` / `ask()` on complements | Inspect established structure via `is_placed` | `POL-ONT-006` |
| **Morphisms** | Bare Python callables / lambdas | Explicit arrows with domain and codomain endpoints | `POL-ONT-007` |
| **Constructor Architecture** | Catch-all `*args` with heuristic fallbacks | Dedicated `from_Y` methods; explicit `match`/`case` with hard error on default `case _:` | `POL-ONT-008` |
| **Subobjects & Quotients** | Bespoke leaf facade classes with ambient pointers | Generic slice/subobject/quotient categories (`SubobjectCategory(C, X)`) | `POL-ONT-009` |
| **Implementation Process** | Immediate greenfield coding without surveying | Mandatory prior survey of existing generic categorical machinery | `POL-ONT-010` |
| **Method & Property Ownership** | Standalone free functions (`is_discrete(C)`) | Direct category-owned methods (`C.is_discrete()`) inherited from the most general category | `POL-ONT-011` |

### The Core Categorical Philosophy

#### 1. Categorical Primacy: Arrows and Objects as Foundational Primitives
Mathematics in `sage-categories` is not constructed on top of a global universe of material sets or raw Python data structures. Category theory is the primitive ontology:
- **No Free-Floating Elements**: There is no such thing as an element existing outside of an object, or an object existing outside of a category. An "element" $x$ of an object $X$ is a **generalized element**—an arrow $x: \mathbf{1} \to X$ from the terminal object in the slice category over $\mathbf{1}$.
- **Morphisms as the Universal Medium of Interaction**: Mathematical actions, evaluations, points, and relationships are modeled as morphism compositions $g \circ f$ and functor applications $F(f)$, never as container mutations, dictionary lookups, or ad-hoc method calls.
- **Private Carrier Data vs. Public Mathematical Identity**: A raw Python tuple, integer, or lambda is solely private carrier data (`Datum` / `Rule`) used by runtime engines. It has no category membership, no domain, and no mathematical standing until an owned category constructor produces an owned `CategoryPoint`.

#### 2. Functorial Transport: Structure Arrives via Functor Chains
In traditional object-oriented systems, capabilities are added to classes via inheritance, mixins, or duplicated utility methods. In `sage-categories`, capabilities are **transported along canonical chains of structure functors**:
- **Single Source of Mathematical Ownership**: Every mathematical concept is owned by the weakest category whose axioms imply it. Cardinality is owned exclusively by $\mathbf{Sets}$. Linearity is owned exclusively by $\mathbf{Modules}$. Order is owned exclusively by $\mathbf{Posets}$.
- **Compositional Access**: Higher mathematical structures receive capabilities compositionally. For example, a lattice does not implement an ad-hoc cardinality method; cardinality arrives through the functor path:
  $$\mathbf{Lattices} \xrightarrow{U_{\mathrm{form}}} \mathbf{FormedModules} \xrightarrow{U_{\mathrm{mod}}} \mathbf{Modules} \xrightarrow{U_{\mathrm{grp}}} \mathbf{AbelianGroups} \xrightarrow{U_{\mathrm{set}}} \mathbf{Sets}$$
- **Zero Redundancy**: Leaf categories declare only their genuine mathematical delta (new objects, generating arrows, structure functors, and canonical lifts). They never re-implement or shadow downstream theory.

#### 3. Universal Properties: Defining Data Determined up to Unique Isomorphism
Categorical constructions are defined strictly by their **universal mapping properties**:
- **Limits and Colimits**: A product $A \times B$ is not a Python tuple container; it is the universal limit cone equipped with canonical projection morphisms $\pi_A: A \times B \to A$ and $\pi_B: A \times B \to B$. Any candidate cone factors uniquely through these projections.
- **Subobjects and Quotients**: A subobject of $X$ is an equivalence class of monomorphisms $m: S \hookrightarrow X$ (an object of the slice category $\mathbf{Sub}(X)$). A quotient of $X$ is an epimorphism $q: X \twoheadrightarrow Q$.
- **Universal Data Preservation**: Structural constructions retain their defining universal morphisms and presentations as first-class mathematical objects.

#### 4. Categorical Refinement: Subcategories as Same-Object Classification
A subcategory $\mathcal{P} \subseteq \mathcal{C}$ (whether a property subcategory, full subcategory, or wide subcategory) is a mathematical filter on the ambient category:
- **Same-Object Identity**: An object in a property subcategory $\mathcal{P}$ is the exact same runtime instance in memory as in the ambient category $\mathcal{C}$. Refinement is functorial placement, not subclass instantiation or wrapper allocation.
- **Multi-Property Intersection**: An object can simultaneously belong to multiple property subcategories (e.g., $X \in \operatorname{Ob}(\mathbf{FiniteSets}) \cap \operatorname{Ob}(\mathbf{TotallyOrderedSets})$) without generating combinatorial wrapper classes.
- **Placement vs. Active Deduction**: An established placement means the object is already known to belong to $\mathcal{P}$ (`is_placed(X, P)`). Category containment `X in P` evaluates active proposition deduction.

#### 5. Constructive Categorical Logic: Three-Valued Propositions via SymPy
Mathematical truths, relations, and capabilities are modeled through constructive categorical logic:
- **Propositions as First-Class Expressions**: Membership queries, property assertions, and equalities return unevaluated SymPy propositions (`AppliedPredicate`).
- **Three-Valued Decidability**: Questions evaluate via `ask()` to `True` (provably true), `False` (provably false), or `Unknown` (undecidable from available axioms and algorithms).
- **Exact Justification**: Truth is established by definition, by inspected construction theorem (canonical lifts along structure functors), or by exact computational deduction handlers. Algorithms realize natural transformations rather than ad-hoc heuristics.

#### 6. Explicit Construction and Total Pattern Matching
A robust categorical framework requires unambiguous mathematical construction:
- **Explicit Named Constructors `X.from_Y(...)`**: When an object or morphism can be presented from different data modalities (e.g. from an explicit enumeration, a characteristic predicate, a generator list, a relation matrix), each representation receives its own dedicated, explicitly named constructor (`from_enumeration`, `from_rule`, `from_matrix`). Never rely on polymorphic overloads to guess the representation.
- **Exhaustive Matching on Canonical Constructors**: The main constructor (`__call__` or primary factory) performs an explicit `match`/`case` on *exactly* what types or structural signatures of inputs arrive, routing each matched case directly to the appropriate dedicated constructor.
- **Zero Fallback Heuristics and Hard Error on Default**: There are zero fallback branches and zero heuristic coercions. The default `case _:` branch must unconditionally raise an immediate, informative hard error (`TypeError` or `ValueError`), ensuring that unrecognized input forms fail fast and noisily.

#### 7. Generic Categorical Constructions vs. Ad-Hoc Leaf Facades
Whenever a mathematical structure is an instance of a standard categorical construction, it must be realized through that generic construction rather than by inventing bespoke leaf classes:

| Mathematical Concept | Anti-Pattern (Ad-Hoc Leaf Facade) | Correct Generic Categorical Construction |
| :--- | :--- | :--- |
| **Subobjects** (Submonoids, Subgroups, Subrings) | Custom `SubX` class with `ambient` pointer | `SubobjectCategory(C, X)` (full subcategory of slice $\mathcal{C}/X$ on monics) |
| **Quotients** (Quotient groups, Quotient rings) | Custom `QuotientX` equivalence-class wrapper | `QuotientCategory(C, X)` (full subcategory of coslice $X/\mathcal{C}$ on epics) |
| **Pointed Objects** (Pointed sets, Pointed spaces) | Custom `PointedX` pair `(space, basepoint)` | Coslice under the terminal/initial object $\mathbf{1}/\mathcal{C}$ |
| **Hom-Sets / Morphisms** | Custom mapping lookup classes | Morphism Category $\mathbf{Mor}(\mathcal{C})(A, B)$ |
| **Diagrams / Systems** | Custom graph/network data structures | Functor Category $[\mathcal{J}, \mathcal{C}]$ |
| **Extensions / Bundles** | Ad-hoc fiber classes | Slice Category $\mathcal{C}/B$ |

#### 8. Mandatory Construction Survey: Reuse Before Greenfield
Writing new code before understanding existing machinery causes severe architectural fragmentation:
- **The Mandatory Pre-Implementation Survey**: Before writing any implementation code for a requested structure or operation, the engineer must explicitly survey:
  1. Generic categorical constructions in `src/sage_categories/cat/` (`SliceCategory`, `SubobjectCategory`, `QuotientCategory`, `MorphismCategory`, `FunctorCategory`, `Cones`, `Cocones`, `Pullbacks`).
  2. Structure functor transport paths and canonical lifts across existing categories.
  3. Universal data and predicate registration mechanisms in `src/sage_categories/kernel/`.
- **Specialization Over Duplication**: If the required mathematical concept is an instance of an existing generic construction (e.g. subobjects of $X$ in $\mathcal{C}$), specialize the generic construction (`SubobjectCategory(C, X)`) rather than hand-rolling new classes. Only write greenfield theory code when the concept is genuinely primitive to that specific category.

#### 9. Method Ownership over Standalone Procedural Functions
In a typed categorical architecture, operations belong to mathematical objects, not loose module functions:
- **The Danger of Standalone Functions**: Standalone functions like `is_discrete(diagram_category)` or `is_finite(set_obj)` allow arbitrary duck-typed or unverified objects to slip through, bypassing category role compilation and producing subtle runtime errors.
- **Direct Object Methods**: Properties, queries, and predicates must be owned directly as methods on the object itself (e.g. `C.is_discrete()`, `X.cardinality()`, `V.dimension()`).
- **Inheritance at the Most General Categorical Level**: Every method must be defined on the role class (`CategoryDeclaration`, `ObjectOfCategory`, `ElementOfObject`, `MorphismOfCategory`) in the most general category whose mathematical hypotheses imply it (e.g. `C.is_discrete()` on generic `Cat`). The kernel compiles role MROs so that all specialized subcategories inherit the operation uniformly and with complete type safety.

## Predicates, hypotheses, and assumptions

A predicate application is a public SymPy proposition with typed mathematical arguments.
SymPy `global_assumptions` is the active mathematical assumption context.
The category, property category, or equality operation owns the predicate meaning.

| ID | Policy |
| --- | --- |
| `POL-ASSUME-001` | Give every assumable proposition one mathematical owner. Represent its public predicate with a SymPy `Predicate` subclass. |
| `POL-ASSUME-002` | Store proposition assumptions only in SymPy `global_assumptions`. Do not implement another assumption store or context object. |
| `POL-ASSUME-003` | Register exact typed handlers on the owning SymPy predicate. Use private identity atoms only to recover owned values inside those handlers. |
| `POL-ASSUME-004` | Let `sympy.ask()` read `global_assumptions`. Translate only its `None` result to Sage's `sage.misc.unknown.Unknown` singleton. Never define or export another `Unknown` value. |
| `POL-ASSUME-005` | Return a `bool` only for an implementation fact that is two-valued by construction. Every mathematical truth question returns a SymPy proposition. Every partial value question returns a typed query with one exact result category. Only `ask()` evaluates either kind. |
| `POL-ASSUME-006` | Decide equality with `ask(a == b)`. Equality on an owned value returns its exact category-owned SymPy proposition. Do not consume it through Python truth protocols. |
| `POL-ASSUME-007` | `assume(P(x))` adds the proposition to `global_assumptions`. A positive property assumption also refines the same value into its property subcategory. It performs no separate evaluation. |
| `POL-ASSUME-008` | A predicate handler returns `True` or `False` only when its exact rule establishes that result. Otherwise, return `None`. Category placement and active assumptions use the same SymPy evaluation path. |
| `POL-ASSUME-009` | Public APIs use category-owned predicate meanings and public SymPy proposition expressions. The identity atoms nested in those expressions remain private. |
| `POL-ASSUME-010` | A construction-owned theorem does not enter the assumption state. Its implementation constructs directly in the property subcategory under `POL-MATH-028`. |
| `POL-ASSUME-011` | Engine and theory code never call `assume()` to justify a result. They construct directly in the category established by computation, definition, or theorem. |
| `POL-ASSUME-012` | Do not compare a proposition or decision by identity with `True` or `False`. Call `ask()`. An undecided result stops a Boolean protocol at its exact boundary. |
| `POL-ASSUME-013` | Compose propositions with SymPy `And`, `Or`, `Not`, and `Implies`, then call `ask()` once. Do not fold unasked propositions through Python Boolean operators. |
| `POL-ASSUME-014` | Where code requires a decided answer, call `ask()` and reject Sage `Unknown` at that exact boundary. State which proposition remained undecided. |
| `POL-ASSUME-015` | Use no Boolean for a mathematical question. A Boolean is valid only for an implementation fact that is two-valued by construction. |
| `POL-ASSUME-016` | Distinguish exact falsity from an unsupported handler argument. Exact falsity returns `False`. An unsupported or undecided case returns `None`. |
| `POL-ASSUME-017` | Validate a constructor argument before normalization. Do not turn an invalid input into a different valid value before its predicate handlers see it. |
| `POL-ASSUME-018` | An ambient hypothesis is a zero-argument SymPy predicate application. It refines no value. A theory module can declare it in `global_assumptions`, and `retract()` can remove it. |

For a semantic morphism $f:P\to Q$, `Q.order_preserving(f)` is an applied SymPy predicate.
Adding it to `global_assumptions` records the session hypothesis.
Public `assume(Q.order_preserving(f))` also refines the owned morphism into its property category.
An exact handler can establish the same result for supported semantic morphisms.

See the official [SymPy predicates and assumptions](https://docs.sympy.org/latest/modules/assumptions/index.html) documentation.

## Semantic representations

| ID | Policy |
| --- | --- |
| `POL-REP-001` | Treat Sage vectors and matrices only as private computation representations. The owned linear-algebra object is always a tensor. |
| `POL-REP-002` | Accept and return the semantic mathematical object at every public API. |
| `POL-REP-003` | Compare tensor elements through their parent and element interface, not by unwrapping coordinate data. |
| `POL-REP-004` | Compare and compose morphisms as morphisms, not by unwrapping their representing matrices. |
| `POL-REP-005` | Expose `f.kernel()`, `f.image()`, and `f.cokernel()` as semantic objects with their defining morphisms. |
| `POL-REP-006` | Ask `f.is_surjective()` instead of testing whether a presentation of `f.image()` is isomorphic to `f.codomain()`. |
| `POL-REP-007` | Treat a bilinear form as a callable hom element encoded by its Gram tensor. |
| `POL-REP-008` | Encode every linear-algebra element as a tensor. A vector or matrix notation does not create another semantic type. |
| `POL-REP-009` | Lower a tensor to a Sage computation representation once, inside one private computation boundary. |
| `POL-REP-010` | Keep matrix algorithms behind private hooks such as `_kernel_matrix_`. Do not expose those hooks to callers or tests. |
| `POL-REP-011` | Reconstruct the tensor, semantic object, or morphism before returning from a private computation. |
| `POL-REP-012` | Do not reinterpret a list, tuple, or numerical vector as a module, algebra, lattice, or tensor element. |
| `POL-REP-013` | Form `sum(a_i * g_i)` from semantic module generators when a finite linear combination is required. |
| `POL-REP-014` | Do not provide a coefficient-vector helper that bypasses construction from semantic module generators. |
| `POL-REP-015` | Type a module morphism by its semantic morphism and tensor element. Keep any Sage matrix realization private and unexported. |
| `POL-REP-016` | Implement scalar change and other functors on tensors, semantic objects, and morphisms. Choose a private computation representation only after the functor acts. |
| `POL-REP-017` | Define the tensor model at the module `ElementType` layer. Every module element has tensor valence `(p, q)`. |
| `POL-REP-018` | Make `tensor()` the fundamental linear-algebra constructor. It accepts valence `(p, q)`, a base ring, and multi-indexable coefficient data. |
| `POL-REP-019` | Shadow Sage's `vector()` and `matrix()` constructors. Make both delegate to `tensor()` with the corresponding valence. |
| `POL-REP-020` | Return tensor elements from `vector()` and `matrix()`. Do not expose Sage vector or matrix elements through the owned API. |
| `POL-REP-021` | Require tensor coefficient data to support one index per tensor slot. Keep storage order private to the tensor implementation. |

## Computation-engine encapsulation

| ID | Policy |
| --- | --- |
| `POL-ENGINE-001` | Define the public API entirely from the owned categorical mathematics. A computation engine supplies private realizations and algorithms only. |
| `POL-ENGINE-002` | Keep every engine value behind a private computation boundary, except public SymPy proposition expressions. Their nested identity atoms remain private. |
| `POL-ENGINE-003` | Return owned categories, objects, elements, morphisms, functors, typed-query results, or authorized SymPy propositions from public operations. Reconstruct every other semantic result before it crosses the computation boundary. |
| `POL-ENGINE-004` | Expose a set-theoretic image as `f.image()` and construct a predicate subobject through `Sets().Subobjects(X).from_predicate(predicate)`. Keep constructors such as Sage or SymPy `ImageSet` and `ConditionSet` private. |
| `POL-ENGINE-005` | Let categorical construction data select refinements and additional methods. An image subobject can retain its defining morphism and inherit operations owned by the corresponding image-subobject category. |
| `POL-ENGINE-006` | Expose no engine selection or dispatch. The category-owned method chooses its private computation. Public signatures use owned mathematical notions, except the authorized SymPy proposition types. |
| `POL-ENGINE-007` | Keep public semantics independent of computation technology. Never add an engine interface, registry, selectable backend, replaceability layer, or competing implementation class. |
| `POL-ENGINE-008` | Write tests, notebooks, and downstream packages against the owned semantic API and the authorized SymPy proposition contract. Do not inspect other engine types or constructors. |
| `POL-ENGINE-009` | Do not re-export an engine API or let its operations determine the public method surface. Export only the selected SymPy proposition types used by the canonical question contract. |
| `POL-ENGINE-010` | Translate engine-specific partial results into the owned result type. Translate undecided SymPy proposition results from `None` to Sage `Unknown` only at public `ask()`. |
| `POL-ENGINE-011` | Treat a timeout, crash, incomplete computation, or indeterminate engine verdict as establishing no mathematical result. It cannot justify category refinement or a Boolean answer. |
| `POL-ENGINE-012` | Treat an engine as a private source of representations and algorithms. It never owns a parallel `ObjectType`, `ElementType`, `MorphismType`, public method catalogue, or semantic implementation surface. |
| `POL-ENGINE-013` | Distinguish a modeled mathematical realization functor from a private computation representation. A private Sage value, cache, or algorithm call requires no functor, category, compiler binding, or natural transformation. |
| `POL-ENGINE-014` | A category-owned method can call a fixed engine through its private computation boundary. This is dependency use, not runtime backend selection or public engine dispatch. |
| `POL-ENGINE-015` | Use the fixed private dependency assignments in [specs/resolution.md](specs/resolution.md). An implementation can combine those technologies inside one category-owned method. Each adapter reconstructs the exact owned result before it returns. |
| `POL-ENGINE-016` | Select private algorithms inside the owning method from established mathematical hypotheses and available representations. Algorithm selection does not create multiple implementations of the mathematical object. |

See [Leaf category implementations](specs/leaves.md) for the complete engine boundary.
See [Private Sage runtime](specs/resolution.md) for the fixed dependency assignments.

## Algebraic generality

| ID | Policy |
| --- | --- |
| `POL-GEN-001` | Parameterize each algebraic-object category by all ambient categorical data in its definition. A typed base object supplies its owning category. It does not determine an independent actegory, action, tensor product, or coherence data. |
| `POL-GEN-002` | Do not hard-code `ZZ` when the definition or algorithm works over a PID, integral domain, or commutative ring. |
| `POL-GEN-003` | Select algorithms by proved ring properties, not by identity checks against `ZZ`, `QQ`, or another named ring. |
| `POL-GEN-004` | Do not import vector-space equivalences into modules over a general ring. |
| `POL-GEN-005` | Do not infer that a module is zero from `M.rank() == 0`; a nonzero torsion module can have rank zero. |
| `POL-GEN-006` | Do not infer that `ker(f) = 0` from a zero matrix-nullspace rank; a nonzero torsion kernel can have rank zero. |
| `POL-GEN-007` | Use matrix-rank criteria for injectivity, surjectivity, or exactness only when the required field hypotheses are established. |
| `POL-GEN-008` | Use the semantic zero-object, kernel, cokernel, and exactness predicates supplied by the relevant category. |
| `POL-GEN-009` | Treat one Python realization with different base objects, ambient categories, actions, or structure morphisms as different mathematical objects. Relate them through the applicable scalar-change functor. |
| `POL-GEN-010` | Preserve infinite algebra-generation data. Do not force a finitely generated presentation onto an algebra such as `QQ` over `ZZ`. |
| `POL-GEN-011` | Keep rank, dimension, cardinality, and minimum number of module generators distinct. Use each invariant only under its defining hypotheses. |
| `POL-GEN-012` | Assume finiteness only when the mathematical definition or a selected property subcategory requires it. Define the arbitrary small indexed construction first and obtain its finite form by restriction. |
| `POL-GEN-013` | Place a coefficient family with potentially infinite support in the appropriate formal power-series ring. Do not declare its sum to be a polynomial without established finite support. |
| `POL-GEN-014` | Recover polynomials as the finitely supported elements of a formal power-series ring. Make polynomial-valued methods restrictions of the general power-series-valued construction. |
| `POL-GEN-015` | Return a lazy iterator when a method enumerates a result family and materialization is not part of the mathematics. Do not encode an unproved finiteness assumption by returning a list or tuple. |
| `POL-GEN-016` | For a supplied tensor category `V`, let `Magmas(V)` own magma objects. For a supplied monoidal category `V`, let `Monoids(V)` own monoid objects. When `V` is cartesian monoidal, let `Groups(V)` own group objects. The applicable tensor product, unit object, associator, unitors, and cartesian structure are part of `V`'s retained structure. |
| `POL-GEN-017` | Let `Semirings(C)` and `Rings(C)` own the corresponding internal algebraic models in a supplied category `C`. The owning specification states the products or monoidal structures and every strictness or coherence requirement. `Semirings(Sets())` and `Semirings(Cat())` are different categories. |
| `POL-GEN-018` | Given a monoidal category `M`, a chosen left `M`-actegory `C`, and `A in Monoids(M)`, let `Modules(A, C)` own pairs `(X, rho)` with `X in C` and `rho: A bullet X -> X` satisfying the unit and action diagrams. Retain `M`, `C`, the action functor, and `A`; never infer `C` from `A`. |
| `POL-GEN-019` | Define `Algebras(R, C)` only when `Modules(R, C)` has a supplied monoidal structure `V_R`. Present it through a retained equivalence to `Monoids(V_R)`. The general monoid category owns multiplication, unit, and monoid laws. Reach the underlying module through the named monoid and magma projections. A noncommutative base requires a supplied monoidal category of bimodule objects. |
| `POL-GEN-020` | State each algebraic family's definition once, at the family, over its ambient parameter. Fixing the ambient gives an instance of that definition, never a specialization of it, and no ambient is the definition. Name each instance with its own source. A downstream specification cites the family definition and states only its own new mathematics. |
| `POL-GEN-021` | Keep every algebraic law an equation between morphisms of the supplied ambient. Do not weaken a law to an isomorphism or a coherence datum. A structure map is a morphism out of a tensor or cartesian product; it presents no diagram, retains no injection or projection, and carries no cone. At `C = Cat()` the laws are equalities of functors. |

For a family \((X_i)_{i\in I}\), the product \(\prod_{i\in I}X_i\) is the limit of the corresponding discrete diagram.
The foundational product constructor therefore accepts an arbitrary small index set \(I\).
A finite product is its restriction to `I in Sets().Finite()`.
A constructor based on a finite tuple of factors cannot express the integral adeles \(\prod_p\mathbb Z_p\).

Likewise, \(\sum_{n\in\mathbb N}a_nt^n\) belongs to \(R[[t]]\) for a general coefficient family.
It belongs to \(R[t]\) after the support of \((a_n)\) is known to be finite.
Thus the public operation is `poincare_series()`, not `poincare_polynomial()`.
The series remains defined when every grading has nonzero cohomology and becomes a polynomial when its support is finite.

## Forms and lattices

| ID | Policy |
| --- | --- |
| `POL-FORM-001` | Model an `R`-lattice as a finitely generated projective `R`-module `M` with the specified form, not as a free `ZZ`-module. |
| `POL-FORM-002` | Model a `W`-valued bilinear form as a morphism `M tensor_R M -> W`, encoded by its Gram tensor. |
| `POL-FORM-003` | Use “inner product” only for a positive-definite symmetric bilinear form. |
| `POL-FORM-004` | Do not assume that a lattice is positive definite, embedded in a vector space, free, based, or unimodular. |
| `POL-FORM-005` | Distinguish left and right radicals for a nonsymmetric bilinear form. |
| `POL-FORM-006` | Define orthogonal complements, norms, and reflections only under the symmetry and nondegeneracy hypotheses they require. |
| `POL-FORM-007` | Determine definiteness from the exact behavior of the form on elements, not from floating eigenvalues or numerical spectra. |
| `POL-FORM-008` | Use exact coefficient rings and exact arithmetic for form and lattice predicates. |
| `POL-FORM-009` | Choose the minimal exact coefficient extension required by the mathematical object. Do not approximate algebraic coefficients by floats. |
| `POL-FORM-010` | Use “Gram tensor” for the tensor that encodes a bilinear form. Keep its chosen-basis coefficient data inside that tensor. |

## Category ownership and inheritance

| ID | Policy |
| --- | --- |
| `POL-CAT-001` | A category owns its constructors, local operations, `C.ObjectType`, `C.ElementType`, and `C.MorphismType`. `C(...)` is the public construction dispatcher for objects of `C`; it delegates to exact private constructor routes selected from the supplied semantic data. |
| `POL-CAT-002` | Use `ObjectType`, `ElementType`, and `MorphismType` for category-owned implementations. This repository defines `Cat` and the kernel implements it; every category uses `Cat().ObjectType`, every functor uses `Cat().MorphismType`, and every natural transformation uses `Fun.MorphismType`. `Cat().ElementType` implements points `* -> C`, with terminal category `*`. These points are the actual objects of `C`, so every `C.ObjectType` inherits it. `C.ElementType` is the shared implementation and API for the elements of objects of `C`. When an object `X` is regarded as a category, its elements are the points `* -> X`; sets use their discrete, 0-truncated category. A generalized element of a category `X` has the form `T -> X` and is an object of `Fun(T, X)`. `C.MorphismType` is `Mor(C).ObjectType`. |
| `POL-CAT-003` | Construct `C.ObjectType`, `C.ElementType`, and `C.MorphismType` from their exact mathematical owners. The kernel adds the corresponding immediate target class of each structure functor as a dynamic base. That Python base relation supplies inherited implementation and does not assert categorical containment. |
| `POL-CAT-004` | A category level defines only the structure and operations introduced at that level. |
| `POL-CAT-005` | A leaf category knows only itself and its immediate structure functors. |
| `POL-CAT-006` | Do not copy or forward methods already owned by another category. |
| `POL-CAT-007` | Do not build a second Python class graph to duplicate the category graph. |
| `POL-CAT-008` | Preserve methods specified on `C.ObjectType`, `C.ElementType`, and `C.MorphismType` in the public method surface. Do not generate opaque method bodies. |
| `POL-CAT-009` | Give a method specified directly on `C.ObjectType`, `C.ElementType`, or `C.MorphismType` precedence over inherited methods. |
| `POL-CAT-010` | Deduplicate routes that reach the same declaring category and the same `ObjectType`, `ElementType`, or `MorphismType`. |
| `POL-CAT-011` | Reject unrelated method-name collisions during method compilation. |
| `POL-CAT-012` | Construct `C.ObjectType`, `C.ElementType`, and `C.MorphismType` as the `parent_class` values of private Sage runtime implementation categories generated from the owned structure-functor graph. Sage's controlled C3 and dynamic classes place a shared ancestor class once in the MRO. The private runtime graph is not Sage's mathematical category graph. The repository threads each initializer once. Each named functor keeps its own public images. |
| `POL-CAT-013` | Include each reached `D.ObjectType`, `D.ElementType`, or `D.MorphismType` once in the source value's MRO. |
| `POL-CAT-014` | Expose inherited operations directly on the public mathematical object. |
| `POL-CAT-015` | Keep functor images inspectable when their exact mathematical type matters. |
| `POL-CAT-016` | Derive inherited category information from the functors selected in `structure_functors()`. Do not maintain a second inheritance registry. |
| `POL-CAT-017` | Put an axiom at the highest category that can state it. |
| `POL-CAT-018` | Distinguish a property subcategory from a category whose objects contain chosen data. Membership in a property subcategory records a proposition, not a selected witness. |
| `POL-CAT-019` | Require chosen data only when it is part of the mathematical structure. Do not require or store a witness merely because an object belongs to a property subcategory. |
| `POL-CAT-020` | Make every construction path account for the defining obligations of its result category. Declare the typed conclusion of its construction theorem, compute the obligation exactly, or accept it as an explicit hypothesis. Runtime proof is not required. Never infer an obligation from an unrelated property. |
| `POL-CAT-021` | Make `Mor(n, C)` for every `n >= 0`, its fixed-endpoint subcategories `Mor(C)(A, B)`, and its property subcategories categories and therefore objects of `Cat`. `Mor(0, C) = C`, `Mor(C) = Mor(1, C)`, and `Mor(n + 1, C) = Mor(Mor(n, C))`. Make every functor an object of `Fun = Mor(Cat())`, and identify `Fun(C, D)` with `Mor(Cat())(C, D)`. |
| `POL-CAT-022` | Keep the hom object category-valued at the `Cat` level: `Mor(C)(A, B)` is the full subcategory of `Mor(C)` on the morphisms `A -> B`. `Fun(C, D) = Mor(Cat())(C, D)` has functors as objects and natural transformations as morphisms. For a 1-category `C`, `Mor(C)` is discrete. A hom object becomes a function set only through the exact structure supplied by `Sets()`. |
| `POL-CAT-023` | Supply `Mor(n, C)`, `Mor(C)(A, B)`, `Mor(C).Endomorphisms()`, `Mor(C).Automorphisms()`, and `Fun([1], C)` at the `Cat` level. A category has two call forms: `K(data)` constructs an object of `K`, and `Mor(K)(A, B)(data)` constructs a morphism `A -> B`. `Mor(K)(A, B)` is the sole fixed-endpoint spelling, and every property subcategory `P` of `Mor(K)` applies endpoints by the same dispatch, `P(A, B) = Mor(K)(A, B).P()`. For `X in C`, the identity morphism is `End_C(X).one()`, the unit of the endomorphism monoid on `Mor(C)(X, X)` under composition. `Y ** X` denotes only the exponential object. |
| `POL-CAT-024` | Make the generic `MorphismType` store its endpoints and expose them through `domain()` and `codomain()`. |
| `POL-CAT-025` | Implement a general morphism predicate as containment in its property subcategory of `Mor(C)`, such as `f in Mor(C).Monomorphisms()`. |
| `POL-CAT-026` | Represent a covering object of `Y` as `(X, p: X -> Y)` with `p` an epimorphism. The morphism `p` alone is not the object. |
| `POL-CAT-027` | Never assume that an arbitrary mathematical entity is a set. Treat it as a category or as an object in its stated category. |
| `POL-CAT-028` | Keep `Mor(C)(X, Y)` category-valued at the general level. Obtain a set of morphisms only through an explicit set-valued construction with the required hypotheses. |
| `POL-CAT-029` | Distinguish an internal Hom object from its global morphisms. Apply the relevant global-sections, object-set, or underlying-set functor explicitly. |
| `POL-CAT-030` | Establish `X in Sets()` or apply an explicit functor to `Sets()` before using elements, membership, cardinality, enumeration, subsets, or set equality. |
| `POL-CAT-031` | Treat an unjustified reduction to `Sets()` as a foundational error. Rebuild every dependent definition, type, morphism, and conclusion in the correct category. |
| `POL-CAT-032` | Put an operation at the most general category where its mathematical result can be declared. Partial knowledge or the absence of one general algorithm does not justify moving the operation to a narrower category. |
| `POL-CAT-033` | Define a subcategory only for a genuine mathematical property or structure. Additive and multiplicative refinements expose their binary operation through `+` or `*`. Do not add public `operation()` or `combine()` aliases. Never define a subcategory only to select, store, or expose an implementation. |
| `POL-CAT-034` | Retired. Use `POL-API-021`. |
| `POL-CAT-035` | Treat an implementation-shaped category or object name as evidence that an established mathematical owner or construction has been missed. Resolve the object, morphisms, and construction before adding terminology. |
| `POL-CAT-036` | Use mathematically standard, total category constructors. Give genuinely different mathematical input forms their own explicit constructors and required inputs. Do not create constructor families merely to distinguish checked, assumed, or theorem-established evidence for one property. |
| `POL-CAT-037` | Place each constructed result in every property subcategory established by that named route and its required inputs. |
| `POL-CAT-038` | Make the category call `C.P()(...)` the standard public trust boundary for a property subcategory. It dispatches to the exact constructor for the supplied semantic representation. Construction in `C.P()` asserts the defining property. Supplying an existing owned value self-refines that value into the subcategory. |
| `POL-CAT-039` | Make each named construction route discoverable through its parameterized category, such as `Sets()`, `Monoids(V)`, `Semirings(C)`, `Rings(C)`, `Modules(A, C)`, and `Algebras(R, C)`. Keep every ambient category and route selection explicit at the call site. |
| `POL-CAT-040` | For \(f:X\to Y\), evaluate `f` only on elements of `X` and return elements of `Y`. A morphism never accepts or returns an unowned Python value. |
| `POL-CAT-041` | Construct or coerce raw representations into elements of the appropriate category objects before morphism evaluation. Keep this conversion outside the morphism. |
| `POL-CAT-042` | Make the operations of `Mor(C)(X, Y)` verify that each element's owning object lies in the base category and that evaluation respects the declared domain and codomain. |
| `POL-CAT-043` | Let a named property subcategory and its category-owned predicate meaning state one mathematical condition. Represent the public predicate with SymPy. The generated `is_P()` method returns its applied proposition without evaluation. `ask()` requests a result and performs exact positive self-refinement. Containment asks the same proposition and forces a Boolean. |
| `POL-CAT-044` | Register each exact decision rule on the SymPy predicate owned by the property subcategory. The axiom declaration `P` gives the kernel `C |-> C.P()` and its ambient category. The kernel generates `is_P()` on `C.ObjectType`. Descendants receive it through compiled inheritance. `ask()` evaluates the proposition. Exact `True` invokes same-object refinement. A leaf does not write another ambient method or proposition model. |
| `POL-CAT-045` | Present every derived object through the complete public interface of the category in which it lives. Its construction can add methods but never replace or duplicate the inherited interface. |
| `POL-CAT-046` | Make a universal-construction category the full subcategory of its ambient category on the constructed objects, with the retained identity-on-values monomorphism selected for inheritance. For each input diagram `D`, the constructor returns one value: the constructed object itself, placed in the family and ambient category. The family retains each diagram, its defining morphisms, and its universal maps. Distinct diagrams retain distinct universal data, including when they construct one object. |
| `POL-CAT-047` | Decide structure functors case by case. A structure functor can be a named projection, fibration, subcategory monomorphism, a right adjoint to a named free functor, or another mathematically specified functor. Returning it from `structure_functors()` selects it for inherited class construction; selection does not assert a subcategory relation or any unnamed functor property. |
| `POL-CAT-048` | Treat structure that an object has, rather than structure that it is, as attached mathematical data. Expose that object by its exact mathematical name without grafting its full method surface. |
| `POL-CAT-049` | Scrutinize every public `underlying_*()` accessor. When the source is canonically a target-category object with additional structure, expose the target interface directly through inheritance instead of requiring accessor indirection. |
| `POL-CAT-050` | Define every axiomatic or functorial category constructor at the highest categorical level where its mathematical meaning exists. Define it once and inherit it throughout the category graph. `C.Products()`, `C.Coproducts()`, `C.Limits(I)`, `C.Colimits(I)`, and the other universal-construction interfaces are defined once on `Cat().ObjectType` and apply when `C` is `Cat()`, `Sets()`, `Fun(C, D)`, or any other category. |
| `POL-CAT-051` | Let a construction subcategory exist without asserting that it is nonempty or that its parent category is complete or cocomplete. Do not require a decision procedure for those properties. |
| `POL-CAT-052` | Make generic category constructors propagate through structure functors. A descendant category supplies no boilerplate merely to form the inherited construction subcategory. |
| `POL-CAT-053` | A leaf never writes Python subclass relations between category-owned classes. The kernel makes `C.ObjectType` inherit `Cat().ElementType` and the immediate target object classes of its structure functors. It makes `C.MorphismType = Mor(C).ObjectType` and supplies the applicable target element and morphism classes as compiler consequences of selection. No additional functor-writer declaration controls this inheritance. |
| `POL-CAT-054` | Declare every relation between categories by a named functor, including a subcategory monomorphism or identity. Select it in `structure_functors()` only when it supplies inheritance. |
| `POL-CAT-055` | Treat a failed structure functor or method compiler as a foundational defect. Its failure does not permit explicit subclassing or another inheritance path. |
| `POL-CAT-056` | Apply structure-functor inheritance to every functorial, universal, and morphism-based construction. Each construction creates and retains its distinct monomorphism, projection, or evaluation functors through `Fun(Source, Target)`. The endpoint pair never selects one functor. |
| `POL-CAT-057` | Every explicitly defined category class writes its own nested `ObjectType`, `ElementType`, and `MorphismType` declarations. An inherited declaration does not satisfy this requirement. Generated axiom categories repeat no leaf declaration. A full property subcategory self-refines the same owned value and places its category-owned class first in the Sage dynamic MRO. |
| `POL-CAT-058` | Compile `ElementType` inheritance from the applicable immediate structure-functor targets. A subcategory declares its own `ElementType`; the kernel fills its target bases. The public functor contract remains its object and morphism actions. |
| `POL-CAT-059` | Let each category add local methods to its `ElementType`. The compiler supplies an applicable target element interface when its functor is selected. Preserve the category-specific element type even when it adds no local methods. Do not add an element-conversion action to the public functor contract. |
| `POL-CAT-060` | Model `P` as an axiom that declares `C |-> C.P()` and its monomorphism into `C`. Sage axiom registration binds the private implementation class to that same category. The axiom identifier supplies the generated `is_P()` name. `C.P()` owns the mathematical predicate. SymPy owns its public class and applied proposition. The kernel generates the ambient method. |
| `POL-CAT-061` | Compile an inherited declaration into the source class MRO and execute it on the original source instance. Construct the dynamic bases from the immediate structure-functor targets. Let Sage's controlled linearization place each shared class once and initialize it once. Initialize `Cat().ElementType` on each `C.ObjectType` with parent `C`. A morphism receives this object rule through `Mor(C).ObjectType`. |
| `POL-CAT-062` | Make inherited calls use ordinary Python inheritance. A declaring category's method applies to the value it was called on and reads its initialized state there. The kernel makes that state available when the functor is selected (`POL-KERNEL-018`). A leaf that changes the mathematics overrides the method or adds its own. |
| `POL-CAT-063` | Preserve exact object, element, morphism, iterator, and mathematical collection types in compiled method signatures. Derive them from the owning implementation class and declared annotations. Do not infer them from runtime registries, `isinstance`, method names, descriptors, or duplicate per-method metadata. |
| `POL-CAT-064` | Compile special methods and ordinary methods through the same dynamic MRO. Do not add per-method wrappers. Generated constructor wrappers are part of class construction, not method dispatch. |
| `POL-CAT-065` | Return a lazy result and an owned collection exactly as the inherited method returns them, one value at a time. Do not wrap or relabel the collection or its items. |
| `POL-CAT-066` | Each named functor owns its object and morphism actions. Two functors with the same endpoints can construct different images. A functor `G: X -> Y` maps a point `* -> X` by composition. |
| `POL-CAT-067` | Apply the same property-refinement rule to the morphism categories `Mor(C)`. Direct property construction, an active-session assumption, exact computation, and construction-owned mathematics all use the kernel's same-object refinement mechanism. |
| `POL-CAT-068` | Let `ask()` return `True` from category placement only when construction or same-object refinement established placement under `POL-CAT-020` or `POL-CAT-067`. The public predicate continues to return its applied proposition. |
| `POL-CAT-069` | Use the kernel's same-object refinement mechanism for every established positive property. The property category owns the predicate meaning and its exact SymPy handlers. `assume(P(x))`, exact `True`, and named mathematical constructions establish the same category placement. |
| `POL-CAT-070` | Treat direct implementation construction, private constructors, subcategory monomorphisms, lifts, and internal helpers as category-entry paths. Each path selects the exact established property category through direct construction, an active assumption, exact computation, or construction-owned mathematics. Internal access is not an exemption. Reach `ObjectType` or another raw allocator only inside the owning category constructor, after that target category has been established for the exact supplied value. A private entry point that a sibling module calls is a public constructor with a misleading name: give each one a name and typed parameters that state the construction data it accepts, as a classmethod or an ordinary named constructor. A method named `_construct` states nothing about its input and skips the preconditions the named constructor asserts. |
| `POL-CAT-071` | Require `F.on_object(X)` to return an actual object of `F.codomain()` and `F.on_morphism(f)` to return an actual morphism in the exact target hom category. Each action calls the target category's public constructors itself. These two actions are the sole writer contract. Runtime state sharing for inherited execution is a private kernel problem (D123). |
| `POL-CAT-072` | Preserve a collection's declared mathematical type and item type through ordinary inherited calls. Do not infer collection semantics from `Iterable` checks or assume that every lazy result contains elements. |
| `POL-CAT-073` | Treat `X in C` as the mathematical admissibility fact. Exact identity such as `X.category() is C` is an implementation fact and never triggers structural normalization. |
| `POL-CAT-074` | Preserve the strongest established category of every object. Do not replace it with an ancestor implementation merely to call an inherited operation. |
| `POL-CAT-075` | Treat the ordinary typed signature and executable body on the owning implementation class as the sole authoritative declaration of a method. Copy that declaration into its compiled class and derive every generated typing artifact from it. Never maintain a second description of the value it applies to, its parameters, call shape, result, or exact mathematical types. |
| `POL-CAT-076` | Keep mathematical type, Python call shape, and categorical construction owner distinct. Exact types state exact mathematical types. Python signatures state positional, keyword, and variadic shape. Named functors and retained presentations state construction provenance. No one of these facts can replace another. |
| `POL-CAT-077` | Determine method ownership from its definition on the category-owned implementation class and the structure functors. No decorator, marker, annotation payload, registry entry, or descriptor argument can create mathematical ownership or repair a missing category declaration. |
| `POL-CAT-078` | The owner of a mathematical fact is the category, object, morphism, functor, or universal construction whose definition states it. A metadata holder, descriptor, registry, adapter, backend, compiler component, or generated type is never its mathematical owner. |
| `POL-CAT-079` | Place every operation forced by category placement at the highest category that first guarantees it. A universal presentation owns its shape, index, diagram, cone or cocone, defining morphisms, universal morphism, and presentation operations. The isomorphism category owns inversion; a selected product cone owns `leg(i)` and its universal map. The apex interface can expose an unambiguous convenience operation. Descendants receive applicable operations through inheritance and state only their added mathematical structure and algorithms. |
| `POL-CAT-080` | Before placing code in a leaf, trace the complete public call from its mathematical owner through construction families, the executable functor action, the target category's public constructor, compiled class inheritance, direct inherited execution, and the declared result. Perform this trace for objects, points, and morphisms. A missing step is a foundational defect. |
| `POL-CAT-081` | Construct every owned value in the strongest property-based subcategory established by its defining construction, exact computation, or trusted programmer assertion. Never construct it weakly and recompute a property already known at construction time. |
| `POL-CAT-082` | Permit an exact SymPy handler at the predicate owner to return `True` when the construction or definition establishes the property. The public predicate still returns an applied proposition. The exact result invokes same-object refinement. |
| `POL-CAT-083` | Represent a distinguished named object by its one-object category `Cat().Point(X)`. Declare its placements as point functors in `{X}.structure_functors()`; each selected point functor places `X` in its codomain and supplies the codomain's surfaces through the categorical level shift, `D.ObjectType` to `X` itself and `D.ElementType` to `X.ObjectType` when `X` is a category (D128, corrected 09-02). |
| `POL-CAT-084` | If a named functor `F: D -> C` defines an inherited property `P` on `D`, construct `D.P()` as the inverse-image subcategory `F.inverse_image(C.P()) = D ×_C C.P()`. Retain its pullback square and monomorphism into `D`. A category with more than one functor to `C` names the functor used. A descendant can add constructors for its own supported representations. |
| `POL-CAT-085` | Define the new owned implementation graph through explicit structure functors returned by `structure_functors()`. Return the complete tuple of immediate ordinary objects of `Fun = Mor(Cat())` used for inheritance. Each entry is constructed by the category's defining presentation or through `Fun(self, Target)`. Migrating a Sage category reconstructs the required owned node and functors; it does not import a Sage category node or edge. A structure functor need not be a subcategory monomorphism. Endpoints and object fields never determine it. See `specs/functor.md`. |
| `POL-CAT-086` | Make `Mor(C)(A, B)` a category for every `A, B in C`. Define inhabitation and emptiness through the axioms that construct `Cat().Inhabited()` and `Cat().Empty()`. The kernel generates `is_inhabited()` and `is_empty()` on `Cat().ObjectType` from those declarations. Each returns the corresponding containment proposition. An unresolved decision leaves the morphism category symbolic; it never replaces that category with an empty category. |
| `POL-CAT-087` | Define a full subcategory from an object predicate `P` on `C`. Its objects are the objects of `C` satisfying `P`; its morphism categories `Mor(C.P())(A, B)`, identities, and composition are inherited definitionally from `C`. Construct its monomorphism as `Fun(C.P(), C).Monomorphisms().Isofibrations().Full()()`. Follow [mathlib's `CategoryTheory.ObjectProperty.FullSubcategory` definition](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/ObjectProperty/FullSubcategory.html). |
| `POL-CAT-088` | On `Cat().ObjectType`, define `C * D` as the product category `Cat().Products()((C, D))`, `C + D` as the coproduct category, and `D ** C` as `Fun(C, D)`. On `Cat().ElementType`, supply categorical product, coproduct, biproduct, and exponential operators as defaults. A category-owned implementation can override a default when standard notation for its objects names a different declared algebraic operation. The explicit categorical constructions remain `C.Products()`, `C.Coproducts()`, `C.Biproducts()`, and the named exponential construction. Local declarations win through the ordinary compiled MRO. An external pair is constructed explicitly as `(C * D)((X, Y))`. Each universal construction retains its defining morphisms. |
| `POL-CAT-089` | Define `Mor(C)` once in the kernel for every `C in Cat()`. Its objects are the morphisms of `C`, and its morphisms are the 2-morphisms of `C`; for a 1-category it is discrete. Endpoint application `Mor(C)(A, B)` is the full subcategory on the morphisms `A -> B`, one cached object per pair. Obtain `Fun = Mor(Cat())` from the same construction: its objects are functors, and `Fun(C, D) = Mor(Cat())(C, D)` has natural transformations as morphisms. The category whose objects are the morphisms of `C` and whose morphisms are commuting squares is the functor category `Fun([1], C)` from the walking arrow, with evaluation functors `ev_0, ev_1: Fun([1], C) -> C`; it is not a primitive. |
| `POL-CAT-090` | Define `Mor(Cat()).Full()`, `.Faithful()`, `.FullyFaithful()`, `.EssentiallySurjective()`, and `.Equivalences()` through the axiom property-subcategory mechanism. The kernel generates their specified `is_*()` applications on `Cat().MorphismType` from those axiom declarations. Each returns the owned containment proposition. Direct construction, assumptions, category placement, and declared subcategory containments use the standard same-object refinement path. |
| `POL-CAT-091` | Register no computational handlers for functor fullness, faithfulness, full faithfulness, essential surjectivity, or equivalence. `ask()` uses property-category placement, active assumptions, and declared subcategory containments (D83). It returns `Unknown` when those sources do not decide the predicate. |
| `POL-CAT-092` | Define the uniform construction methods once on `Cat().ObjectType`; every category inherits them. For `X in C`, `C.Subobjects(X)` is `C.SliceOver(X).Monomorphisms()`, `C.Superobjects(X)` is `C.CosliceUnder(X).Monomorphisms()`, `C.CoveringObjects(X)` is `C.SliceOver(X).Epimorphisms()`, and `C.CoveredObjects(X)` is `C.CosliceUnder(X).Epimorphisms()`. The property subcategory applies to the defining arrow in `C`, through the retained functor from the slice or coslice to `Mor(C)`. The ambient category in the call fixes the role of `X` when the same value belongs to more than one category. Define products, coproducts, pullbacks, pushouts, equalizers, coequalizers, and the other standard universal-construction methods once on `Cat().ObjectType` from `Limits(I)` and `Colimits(I)` at their standard shapes. A leaf supplies only its realization and any constructor specific to its mathematics. `Sets().Subobjects(X).from_predicate(predicate)` is such a set-specific constructor. Restricting a leaf's structure to a subobject is leaf work (`POL-LEAF-060`). Each limit or colimit family is indexed by one supplied shape `I in Cat()`; `C.Limits(Cat())` never denotes limits over all small shapes. A discrete diagram is a rule `i |-> X_i` on an index set; a Python sequence denotes the diagram over `Discrete([n])`. Bicompleteness and cartesian closure of `Cat()` are trusted declarations attached to the constructors the kernel supplies; they assert nothing about a shape or category not supplied to a constructor. |
| `POL-CAT-093` | Give each selected product cone `p` the method `leg(i) -> C.MorphismType`, indexed by its diagram. Give each selected coproduct cocone the dual method. An apex in `C.Products()` or `C.Coproducts()` can expose a direct convenience method only when the call selects one retained presentation without ambiguity. For `C = Cat()`, these morphisms are functors. |
| `POL-CAT-094` | An object of `C.Subobjects(P)` is an object `S` with a monomorphism `j: S -> P`. The equivalence-class formulation of a subobject matters only when deciding whether two such representatives define the same subobject. Let `p` be a selected product presentation with apex `P`, and let `j: S -> P` be such a monomorphism. Make the corresponding object of `Cat().Subobjects(P)` retain `j`. Its component functor at `i` is `p.leg(i) after j`. Do not ask a leaf to repeat these composites. |
| `POL-CAT-095` | Present `C.SliceOver(x)` as the pullback in `Cat()` of `ev_1: Fun([1], C) -> C` along `x: * -> C`, and `C.CosliceUnder(x)` as the pullback of `ev_0` along `x`. More generally, `Comma(F, G)` is the pullback of `(ev_0, ev_1): Fun([1], C) -> C * C` along `F * G`. Each retains its pullback projections; the varying object is the composite with `ev_0` or `ev_1`. Two distinct functors carry distinct lift data: `ev_1` is a fibration when `C` has pullbacks, with the cartesian lift of `f: y -> x` at `p: z -> x` given by pullback; the fixed slice projection `C.SliceOver(x) -> C` is a discrete fibration for every `C`, with the cartesian lift of `f: y -> z` at `(z, p)` given by precomposition, `(y, p compose f) -> (z, p)`. Retain each lift at its construction owner. |
| `POL-CAT-096` | A functor has an image; a category does not. The image of `x` is `F.on_object(x)` for a named functor `F`, and the image of `f` is `F.on_morphism(f)`. Two functors into one target can have different images. Making `F` a structure functor changes none of this. Python inheritance exposes the target method surface on the source value; it does not identify that value with `F(x)`. |
| `POL-CAT-098` | Objects carrying a choice of extra data form the total category of a fibration over the base, not a subcategory of it. `Modules(R)` and the category of pairs `(M, S)` with `S` a generating set are different categories, related by the functor `p: E -> Modules(R)` whose fiber over `M` is the category of choices for `M`. State that functor. The datum is normally a morphism: a generating set is an epimorphism `Free_R(S) ->> M`, a finite presentation is a length-two resolution `Free_R(X_1) -> Free_R(X_0) -> M`, and a resolution of any length is the general case. Thus the family is one construction at different shapes, built from `C.SliceOver(M)`, `Fun([1], C)`, and `Fun(I, C)` (`POL-CAT-092`, `POL-CAT-095`), never a separate axiom per datum. The Grothendieck construction relates indexed categories to their total fibrations; base change along `F: D -> C` is the pullback `D ×_C E -> D`. State also which morphisms the total category has and which are cartesian. Follow [Mathlib, `CategoryTheory.Pseudofunctor.Grothendieck`](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Bicategory/Grothendieck.html), [Mathlib, fibered categories](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/FiberedCategory/Fibered.html), and [Stacks, Definition 4.33.5, tag 02XJ](https://stacks.math.columbia.edu/tag/02XJ). Sage's `WithBasis` names the phenomenon and settles none of this; its morphisms are ordinary module morphisms while its homset reads a matrix in the distinguished bases (`sage/categories/modules_with_basis.py:47`, `:179`). |
| `POL-CAT-099` | Define the dualizing functor `Op: Cat() -> Cat()` with `Op.on_object(C) = C.op()` and `Op.on_morphism(F) = F.op()`. Dualization sends `eta: F => G` to `eta.op(): G.op() => F.op()` and retains the natural isomorphism `Op compose Op ≅ Id`. Use the limit-side construction as the owner for each dual pair: terminal, product, limit, slice, monomorphism, fibration, and right Kan extension. Derive the initial, coproduct, colimit, coslice, epimorphism, opfibration, and left Kan extension through `Op`. Follow [Mathlib, `CategoryTheory.Cat.opFunctor`](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Category/Cat/Op.html) and [Mathlib, `CategoryTheory.Opposites`](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Opposites.html). |
| `POL-CAT-100` | For `F: D -> C` and a subcategory monomorphism `i: P -> C`, define `F.inverse_image(P)` as the pullback `D ×_C P` in `Cat()`. Retain both pullback projections. The projection to `D` is the subcategory monomorphism. If `P` is full or replete, its inverse image has the same property. Use this construction for property categories and every other inverse-image subcategory. Follow [Mathlib, `ObjectProperty.inverseImage`](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/ObjectProperty/Basic.html) and its [full-subcategory construction](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/ObjectProperty/FullSubcategory.html). |
| `POL-CAT-101` | Make composition `Fun(B, C) * Fun(A, B) -> Fun(A, C)` and evaluation `Fun(C, D) * C -> D` functors. Obtain precomposition, postcomposition, whiskering, and horizontal composition from their object and morphism actions. Retain associator and unitor natural isomorphisms. Follow [Mathlib, whiskering](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Whiskering.html). |
| `POL-CAT-102` | Use pullbacks as one category-construction calculus. Compute `P.intersection(Q)` as `P ×_C Q`. For `F: C -> D` and subcategories `P -> C`, `Q -> D`, let `F.restrict(P, Q)` be the functor supplied by a stated factorization of `F` through `Q`. Build induced functors between pullbacks from the universal property. Define `p.Fiber(b)` as the pullback of `p: E -> B` along the point `b: * -> B`, and define `F.base_change(p)` as `D ×_C E -> D`. Retain every pullback projection and comparison square. |
| `POL-CAT-103` | Treat `(F ↓ G)` as a public comma category for `F: A -> C` and `G: B -> C`. Retain its projections to `A` and `B` and its natural transformation from the first composite to the second. Define slices and coslices as its fixed-object forms. Follow [Mathlib, comma categories](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Comma/Basic.html). |
| `POL-CAT-104` | Represent selected adjunctions, equivalences, limiting cones, and functor representations as objects of `Adjunctions(F, G)`, `Equivalences(C, D)`, `LimitCones(D)`, and `Representations(F)`. Inhabitation of the applicable category states existence. Selecting an object supplies the unit and counit, inverse and natural isomorphisms, limiting cone, or representing object and natural isomorphism. Give each category its standard structure-preserving morphisms. |
| `POL-CAT-105` | Separate a diagram, its universal presentation, and the presentation's apex. `Cones(D)` is the cone category and `LimitCones(D)` is its full subcategory of terminal objects. For a fixed shape, the total category of limiting cones retains its projection to `Fun(I, C)` and its apex functor to `C`. The fiber of the apex functor over `X` is the category of presentations with apex `X`. Define `C.Products()` and `C.Limits(I)` from the full images of the applicable chosen product and limit functors. Follow [Mathlib, cone categories](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Limits/ConeCategory.html). |
| `POL-CAT-106` | Supply Yoneda, co-Yoneda, restricted Yoneda, and the category of representations as generic constructions. For `j: A -> C`, the restricted Yoneda functor is `N_j: C -> Fun(A.op(), Sets())`, with `N_j(X)(a) = Mor(C)(j(a), X)`. State separation by placing `N_j` in `.Faithful()` and density by placing it in `.FullyFaithful()`. Follow [Mathlib, Yoneda](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Yoneda.html) and [Mathlib, represented functors](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/RepresentedBy.html). |
| `POL-CAT-097` | A diagram is indexed by a family, and that index need not be an ordered set. Never reorder a supplied family: `B * A` does not become `A * B` because `"A" <= "B"` in some order. Where an operation is commutative and associative and a canonical form does order its terms, order them by an owned mathematical key. Never order by `repr`, `str`, or another printed presentation; a printer is a presentation, so ordering by it makes object identity depend on display text. |

Grounding examples:

- Limits, colimits, products, coproducts, tensor products, and direct sums return their retained functors from `structure_functors()` when those functors supply inherited implementation.
  The kernel then places the immediate target classes in their dynamic MRO.

- Subobjects, superobjects, covering objects, and covered objects retain the functors that select each stated component of their defining morphisms.
  A retained functor contributes a dynamic target base only when the category returns it from `structure_functors()`.

- `Sets().Finite()` declares its monomorphism into `Sets()` even when both categories use the same realization.
  The monomorphism states the owned categorical relation and, when selected in `structure_functors()`, supplies the corresponding owned implementation edge.

- An element of a finite set has type `Sets().Finite().ElementType`, not `Sets().ElementType`.
  The monomorphism supplies the set-element interface to the finite-set element type.

- An element of a product has type `C.Products().ElementType`.
  It inherits the applicable `C.ElementType` interface and can add `factors()` to return its indexed component family.

- Cardinality belongs on every object of `Sets()` because every set has a cardinality.
  A constructor can supply the cardinal directly.
  Pattern matching on available data can select a computation without defining a subcategory for its implementation.

- Every set can construct `Sets().Subobjects(X).from_predicate(predicate)`.
  The result is a subobject \(A\hookrightarrow X\), including infinite examples such as the even or prime integers inside \(\mathbb Z\).
  A private representation can retain the predicate or other construction provenance for computation.
  `PropertySet` or `Sets.PropertyCategory()` does not name a mathematical class: every set can be characterized by a property.
  Such a name mistakes the construction of an ordinary subset for a new kind of set.

- `Sets().Finite()(members, cardinality)` requires the semantic data needed for a finite
  set and constructs directly in the finite-set subcategory.
  The countable and uncountable property subcategories own their corresponding constructors.

- Use `ask(X.is_finite())` when asking the category-owned SymPy predicate to decide finiteness and refine
  `X`. Use `X in Sets().Finite()` when asking whether that placement is already established.
  After refinement, category placement makes `ask(X.is_finite())` return `True`.

- Every `C in Cat` can form `C.Products()`.
  This subcategory can be empty, and its existence does not assert that `C` has all products.
  Thus `Modules(A, C).Products()` requires no module-specific reconstruction of the generic product category.

## Leaf-category encapsulation

| ID | Policy |
| --- | --- |
| `POL-LEAF-058` | Review a leaf functor against [specs/functor.md](specs/functor.md) and [specs/leaves.md](specs/leaves.md): its complete leaf declaration is `on_object` and `on_morphism`, and each action returns an owned value through the exact target constructor surface. |
| `POL-LEAF-060` | Review leaf restriction claims against [specs/functor.md](specs/functor.md) and [specs/leaves.md](specs/leaves.md): a leaf states only its own theorem, and the generic `F.restrict(P, Q)` construction owns the restricted functor and its actions. |
| `POL-LEAF-061` | Review each selected functor against [specs/functor.md](specs/functor.md): a leaf either reuses the retained functor of its defining construction or constructs `Fun(self, Target)` with complete actions, and `Cat` and the kernel add no second functor account. |
| `POL-LEAF-062` | Review helper visibility against [specs/leaves.md](specs/leaves.md): keep a helper private when only leaf-internal code or a functor action uses it, and keep genuinely public mathematical data public. |
| `POL-LEAF-059` | Review leaf runtime declarations against [specs/leaves.md](specs/leaves.md) and [specs/resolution.md](specs/resolution.md): a leaf declares `ObjectType`, `ElementType`, and `MorphismType`, and Sage's axiom mechanism owns abstract property-class generation. |
| `POL-LEAF-001` | Integrate a new leaf category by selecting its named functors to known categories. These selections are the complete inheritance declaration. |
| `POL-LEAF-002` | Make a leaf constructor accept only its strongest minimal semantic datum. Recover every weaker component through the datum's domains, codomains, ambient products, defining morphisms, and named functors. Never require an underlying set, module, ring, or other ancestor object as a second argument when the supplied relation, morphism, form, or structure map already determines it. |
| `POL-LEAF-003` | Explicitly select each subcategory monomorphism, projection, restriction, lift, or evaluation functor. Obtain generic projections, restrictions, lifts, evaluations, and base-change functors from their defining category constructions. Construct a functor through `Fun(self, Target)` only when the leaf introduces its mathematical action. |
| `POL-LEAF-004` | Make a realization constructor idempotent on an object already owned by its target category. In particular, `Sets(X)` returns `X` when `X in Sets()`. |
| `POL-LEAF-005` | Let the category compiler inherit the target categories' object, element, and morphism methods along structure functors. A leaf category defines no forwarding methods. |
| `POL-LEAF-006` | Treat a leaf implementation of an inherited operation as evidence of a missing structure functor, an incorrect functor image, or an operation placed at the wrong owner. |
| `POL-LEAF-007` | Permit a structure functor to land in a morphism category `Mor(C)` when the defining morphism determines the required inherited object data through its domain or codomain. |
| `POL-LEAF-008` | Confine private-field access to constructors and genuinely new functor maps that cannot recover their required defining data through owned semantic interfaces. A standard kernel functor never requires leaf access code. |
| `POL-LEAF-009` | Keep private representations out of inherited methods, public signatures, callers, tests, and downstream packages. A leaf-owned executable method can access a private representation inside its computation boundary. |
| `POL-LEAF-010` | Validate a leaf integration by calling inherited mathematical operations directly on its objects, elements, and morphisms through the compiled public surface. |
| `POL-LEAF-011` | When a named leaf functor creates limits of shape `I`, place it in `.CreatesLimits(I)` and state only the leaf mathematics that establishes this property. The generic creates-limits construction supplies the lifted cone and universal morphisms. If the functor does not create those limits, a different leaf construction must name its actual mathematical source. |
| `POL-LEAF-012` | Do not redefine the inherited construction's objects, elements, universal property, or general methods in a leaf subtree. Those remain owned by the category where the construction was introduced. |
| `POL-LEAF-013` | Design the kernel so leaf authors can treat inheritance and method compilation as established infrastructure. Adding a mathematical leaf must not require reading or modifying kernel code or kernel tests. |
| `POL-LEAF-014` | Ship and maintain design-pseudocode templates for an ordinary structured leaf, a property implementation, a pullback-defined category, a chosen-datum fibration, and a universal-construction realization. Each template contains only the category declaration, minimal default and named constructors, complete executable functor actions, immediate selected structure functors, and sites for new methods or exact handlers. It reuses every functor retained by its defining categorical construction. A template is never imported, executed, type-checked, or held to a spelling criterion. It shows one valid presentation without making other mathematical presentations stale. A template is defective when it teaches a shape the kernel cannot compile, adds a second semantic owner, or crosses the layer dependency boundary (D118 through D122). |
| `POL-LEAF-015` | Let a leaf author work from the new mathematics and the contracts of nearby categories. Do not require knowledge of distant subtrees or the complete category graph. |
| `POL-LEAF-016` | After the functors are selected, automatically supply the complete applicable object, element, morphism, and construction interfaces from their target categories. |
| `POL-LEAF-017` | Give a full replete subcategory the inherited categorical interface without extra wiring. When its inclusion creates a stated class of limits, place that inclusion in the applicable `.CreatesLimits(I)` property categories. The generic construction supplies the lifted limits. The subcategory leaf states only the closure theorem and its own constructors. |
| `POL-LEAF-018` | Do not implement an inherited category-owned mathematical operation in a leaf object. A local `__iter__`, `__contains__`, or `cardinality()` on a poset object duplicates the set interface instead of receiving it through the structure functor to `Sets()`. |
| `POL-LEAF-019` | Do not create a free-standing category to hold the elements of another category. Poset elements belong to `Posets().ElementType`; a separate `PosetElements()` category disconnects their type and inheritance from `Posets()`. |
| `POL-LEAF-020` | Give every refinement and construction its own category-owned `ObjectType`, `ElementType`, and `MorphismType` declarations. Property refinement keeps the same owned value and updates its Sage dynamic class so the refined class precedes inherited classes. |
| `POL-LEAF-021` | Lift a construction through functors, natural transformations, and the new mathematical structure only. A poset product supplies the componentwise order and its action on morphisms; its implementation types do not subclass generic product types or reconstruct the underlying set product interface. |
| `POL-LEAF-022` | Do not require data that defines a stronger structure than the named leaf category. A total order requires a partial order with total comparison; indexing, ranking, unranking, and enumeration belong to separate enumerable or well-ordered refinements. |
| `POL-LEAF-023` | Do not copy inherited storage or constructor arguments into a property refinement. A finite poset adds finite-poset operations and declares its subcategory monomorphisms. Same-object refinement preserves the source value, its relation, its elements, and its private realizations. The refined dynamic MRO supplies inherited operations; the leaf never traverses a monomorphism to recover its own state. |
| `POL-LEAF-024` | A finished leaf contains its category, minimal defining data, new operations, immediate structure functors, named constructors, and properties established for those functors. |
| `POL-LEAF-025` | Stop leaf work when it must resolve inherited structure, category placement, compiler metadata, types, or computation-engine choice at run time. A fixed private computation dependency is not backend selection. |
| `POL-LEAF-026` | Use the first leaf that exposes missing generic infrastructure as an acceptance specimen. Repair the foundation, then delete the leaf workaround. |
| `POL-LEAF-027` | Identity morphisms and morphism composition are fundamental categorical operations. Every leaf morphism receives its domain, codomain, and composition surface automatically from the owning categories through compiled structural inheritance. |
| `POL-LEAF-028` | Never define `compose()` in a leaf merely to expose, forward, route, coerce, inspect generic caches, or reconstruct the inherited operation. A missing inherited composition method is a kernel defect. |
| `POL-LEAF-029` | Refine an inherited method in a leaf only when the leaf's additional mathematical structure or owned realization requires a new step. Form the inherited semantic result first. |
| `POL-LEAF-030` | A leaf refinement adds only its leaf-specific structure or private realization. It preserves the inherited method's name, laws, domain, codomain, and mathematical owner. |
| `POL-LEAF-031` | Delete any leaf method that adds no leaf-specific mathematical or realization step. Generic algorithms, structural transport, wrappers, and public-surface installation belong to their existing owners. |
| `POL-LEAF-032` | Treat structure functors as the complete inheritance program. A finished leaf contains no forwarding, descriptor, route, cache, wrapper, or type-repair boilerplate. |
| `POL-LEAF-033` | A concrete category that implements `C.P()` uses Sage's private axiom registration. It defines the property meaning and registers exact SymPy handlers. It can declare its nested implementation classes and supported constructors. `Cat` owns the monomorphism and inverse-image categories. The kernel generates `is_P()` and performs same-object refinement. |
| `POL-LEAF-034` | Never give a leaf an ambient-to-refined cache, an identity-keyed refinement table, an ambient wrapper field, or a local refinement mechanism. |
| `POL-LEAF-035` | Direct construction, `assume(P(x))`, exact `True`, and construction-owned mathematics all use the kernel's generic same-object refinement. The leaf performs no refinement allocation, cache mutation, narrowing, or repeated membership assertion. |
| `POL-LEAF-036` | Treat a type error in leaf refinement machinery as evidence that the kernel lacks a typed refinement contract. Repair that contract and delete the leaf machinery. |
| `POL-LEAF-037` | A leaf returns its immediate structure functors and uses the resulting inherited surface. It never discovers, inspects, composes, or traverses the compiled class graph. |
| `POL-LEAF-038` | Never apply a structure functor to fetch an object, element, or morphism image for an inherited method. The method already applies to a value that carries the declaring category's state (`POL-KERNEL-018`). |
| `POL-LEAF-039` | Call an inherited operation directly on the original structured value. If that call fails, stop the leaf edit and repair structural compilation. |
| `POL-LEAF-040` | Never normalize a leaf input to an ancestor implementation, add an exact-category branch, or repeat membership after transport. Store and pass the established mathematical object. |
| `POL-LEAF-041` | Make `C.ObjectType`, `C.ElementType`, and `C.MorphismType` the sole executable implementation classes for operations owned by `C`. Each class is the public firewall that hides every supported representation, dependency, and algorithm for that exact mathematical type. |
| `POL-LEAF-042` | Let the category declaration define or link exactly one implementation class for each exact mathematical type. Never offer competing implementation classes, backend choices, realization variants, or parallel public surfaces for one mathematical notion. |
| `POL-LEAF-043` | Implement every leaf-local public operation as an ordinary executable method on its owning implementation class. Never replace its body with `assert False`, `@realized_method`, `@realized_operation`, another computation-routing decorator, a descriptor marker, or a backend-name mapping. |
| `POL-LEAF-044` | Let a leaf-owned method lower semantic inputs to a fixed private engine, invoke a mature exact algorithm, and reconstruct the owned mathematical result. This computation is part of the leaf implementation, not structural wiring. |
| `POL-LEAF-045` | Treat a short category-owned method that invokes a dependency as a valid implementation when it owns the public contract and semantic reconstruction. Repetition of private realization access alone does not justify a dispatcher or parallel hierarchy. |
| `POL-LEAF-046` | Permit a private neighboring engine helper only for a substantial shared computation boundary. It exposes no public method surface, category classes, runtime registry, compiler binding, or mirror of the leaf operations. |
| `POL-LEAF-047` | Give each local implementation constructor one exact typed datum containing only the new state required by its category. A functor action constructs its target image through an ordinary public target constructor. Each local initializer calls `super().__init__()` once. An object initializer reaches `Cat().ElementType` with its parent category. The leaf writes no separate initializer input for compiled inheritance. |
| `POL-LEAF-048` | Make the public operation surface depend only on categorical placement. Every object of the category receives the same owned operations, regardless of which private dependency or representation computes them. |
| `POL-LEAF-049` | Select each immediate named functor in the category layer. Reuse the exact functor retained by the defining category construction. Otherwise, define its complete object and morphism actions once through `Fun(self, Target)`. Select the strongest established functor-property subcategory before construction. Selection requires no additional object, element, morphism, or constructor description. |
| `POL-LEAF-050` | Quarantine substantial Python, foreign-function, process, conversion, caching, and engine-adaptation code in private helpers. Keep mathematical ownership, public methods, semantic inputs, and semantic reconstruction on the sole category implementation class. |
| `POL-LEAF-051` | Write a leaf method as one ordinary typed Python method. Its signature and owning class are the complete declaration. Do not place a second compiler record beside it. |
| `POL-LEAF-052` | Stop a change that repeats the same non-mathematical declaration across leaf methods or categories. Such repetition identifies missing kernel derivation. Repair the kernel once, or reject the unsupported semantic signature during compilation. |
| `POL-LEAF-053` | Require no framework-specific decorator on a mathematical leaf method. Never use a decorator to establish ownership, compilation, inheritance, transport, dispatch, engine selection, result reconstruction, or type repair. An ordinary typed method on the owning implementation class is complete. |
| `POL-LEAF-054` | Keep kernel concerns out of every leaf import, decorator, annotation, signature, class attribute, and method body. Leaves state mathematical data, operations, named functors, constructors, and theorems about those functors. |
| `POL-LEAF-055` | Use only ordinary Python call syntax and exact mathematical types in a leaf method signature. Derive call shape and compiler data from that signature. |
| `POL-LEAF-056` | Never implement an operation supplied by an inherited morphism category, morphism-property category, or universal construction. This includes inversion of isomorphisms and every other operation implied by established categorical placement. If the operation is absent from a descendant morphism, repair the generic owner, structure functor, or compiler. |
| `POL-LEAF-057` | A named-object leaf states its known properties by its strongest category placement or by ordinary defining predicates that return `True`. Never enumerate the object, query an engine, or run a general decision procedure to rediscover a property supplied by its definition. |
| `POL-LEAF-063` | Red flag: an initializer in a theory declaration that calls a base initializer or installs an inherited owner's state by hand. The kernel runs every reached initializer and threads inherited state through the selected structure functors (D13, D133). |
| `POL-LEAF-064` | Red flag: a category that constructs a property or construction subcategory by hand, names it with a string, or patches an accessor onto it. An axiom is declared once at its owner, and the kernel routes `C.P()`, `C.Products()`, and `is_p()` from that declaration (D89, D133). |
| `POL-LEAF-065` | Red flag: identity, composition, morphism construction, element construction, or element retention written in a leaf for structure it inherits. These arrive through the structure functor; a leaf writes only the mathematical delta it adds (D44, D133). |
| `POL-LEAF-066` | Red flag: a leaf that branches on kernel roles, placement, or refinement machinery, refines a value after constructing it, keeps its own cache of its values, or passes kernel state such as the constructing category into a constructor. Construct into the strongest category directly; retention and placement are the kernel's (D21, D111, D133). |
| `POL-LEAF-067` | Red flag: a Sage parent, element, or Sage category used as an owned category's own runtime. Sage machinery runs behind a private engine boundary; the owned category expresses the operations (D01, D65, D133). |

See [Leaf category implementations](specs/leaves.md) for the complete ownership model,
the allowed private computation sequence, and the rejected decorator and mirrored-class
designs.

For example, a free-module morphism inherits categorical composition.
A leaf refinement can attach a private matrix realization to the inherited composite when bases are chosen.
It does not reimplement composition, structural transport, domain checks, codomain checks, or public method installation.

## Leaf and kernel boundary

| ID | Policy |
| --- | --- |
| `POL-KERNEL-001` | The kernel translates the applicable immediate edges of the new owned structure-functor graph into private Sage runtime implementation categories for objects, elements, and morphisms. Sage compiles their dynamic classes. The kernel makes the target implementation state available on the source instance and initializes each class once. It imports no leaf-specific mathematics and no Sage mathematical category node. This private mechanism requires no second leaf-authored functor description. Each named functor owns its public images. |
| `POL-KERNEL-002` | The kernel owns generic same-object property refinement. It strengthens the owned value's category, joins the applicable private runtime categories, applies Sage's dynamic refinement pattern, and preserves identity, construction data, and private realizations. A Sage `Parent` uses `Parent._refine_category_`. Named functor images remain separate values. |
| `POL-KERNEL-003` | A leaf functor states its complete mathematical action on objects and morphisms. A functor between categories maps their points and generalized elements by composition. Compiled `ElementType` inheritance is a private compiler consequence of selecting the functor and adds no action or writer input. The leaf never implements path composition or cache management. |
| `POL-KERNEL-004` | The generic categorical foundation owns the lift supplied by a functor in `.CreatesLimits(I)` and retains its universal data. It never asserts that a leaf functor has this property. The leaf states the theorem and the construction data that make the property true. For posets, the projection to sets creates limits and the leaf states the componentwise-order theorem once. |
| `POL-KERNEL-005` | Add a kernel abstraction only when one mathematical declaration replaces the same infrastructure in every applicable leaf. Keep category-specific branches out of the kernel. |
| `POL-KERNEL-006` | Kernel complexity is valid only when it removes that complexity from theory code. Expose each kernel capability through a mathematical declaration. |
| `POL-KERNEL-007` | Kernel code can use `isinstance`, `issubclass`, `getattr`, `setattr`, `inspect`, descriptor protocols, and Python collection protocols to implement declared runtime mechanics. |
| `POL-KERNEL-008` | Each kernel primitive must inspect a Python implementation class. It must not establish category membership, a mathematical property, method ownership, or functorial structure. |
| `POL-KERNEL-009` | Derive exact mathematical types from typed category and functor declarations. Use Python inspection only to realize those declarations in the runtime. |
| `POL-KERNEL-010` | Keep the private Sage implementation-class graph, dynamic-class construction, method rebinding, and initializer threading inside the kernel. Expose the resulting typed mathematical surface through ordinary Python inheritance. |
| `POL-KERNEL-011` | Kernel permissions do not permit `Any`, `object`, casts, ignored diagnostics, fallbacks, or fabricated mathematical evidence. |
| `POL-KERNEL-012` | Provide one typed same-object self-refinement operation for objects, elements, and morphisms of every full property subcategory. Every positive evidence source converges on that kernel operation. |
| `POL-KERNEL-013` | Generic property refinement preserves the same Python and mathematical identity. It joins the current category with the property subcategory and updates the Sage dynamic class and MRO in place. The refined value remains the one owned value. |
| `POL-KERNEL-014` | Compile each property subcategory's `ObjectType`, `ElementType`, and `MorphismType` declarations into the refined value's dynamic MRO. The property class contributes its new mathematics before inherited classes. |
| `POL-KERNEL-015` | A kernel `try`/`except` can only add exact context, translate to a more precise kernel exception while preserving the cause, or perform mandatory cleanup before re-raising. |
| `POL-KERNEL-016` | Every kernel catch terminates the current operation. It never selects another implementation, retries, suppresses a diagnostic, continues computation, or returns an ordinary value. |
| `POL-KERNEL-017` | Review kernel compilation against [specs/resolution.md](specs/resolution.md): Sage receives the applicable immediate structure-functor targets and the local declaration as `ParentMethods`, and named functors alone construct public images. |
| `POL-KERNEL-018` | Make each inherited method callable directly on every structural descendant through its compiled class MRO, applying to the descendant with its arguments unchanged. For a selected `F: C -> D`, the ordinary action constructs the separate public image `F(X)`, and the kernel runs that same action during construction to initialize the applicable `D` implementation on `X` from the datum it feeds to `D`'s constructor (D13). Thus `X.f() == F(X).f()` holds and the declaring method reads its own state where it is applied. This private runtime obligation creates no second theory-layer transport declaration (`POL-MATH-046`, D123). |
| `POL-KERNEL-019` | Let a constructor requiring an object of `C` accept every `X` with `X in C`. Resolve its owned implementation inside the generic kernel boundary. |
| `POL-KERNEL-020` | Give the local `ObjectType`, `ElementType`, or `MorphismType` to Sage as the runtime category's method provider. Rebind copied methods whose zero-argument `super()` still names that provider class. Never route a locally owned operation into Sage or another engine, replace its executable method, match it to an engine method by name, or interpret a decorator, annotation, registry entry, or marker as a computation route. |
| `POL-KERNEL-021` | Derive the exact type a method applies to from its owning `ObjectType`, `ElementType`, or `MorphismType`. Derive parameter and result types from their exact mathematical types. Derive call shape from the Python signature. Fail compilation when a required type is not exact. Never require a leaf to restate these facts. |
| `POL-KERNEL-022` | Use exact mathematical types for construction inputs and functor images. Never relabel a category, object, element, morphism, or mathematical collection as a plain value to avoid its exact type. |
| `POL-KERNEL-023` | Compile every supported ordinary typed leaf method without any kernel import or framework annotation in the leaf. A required decorator, marker, or signature mirror is a kernel API defect. |
| `POL-KERNEL-024` | Inspect standard Python signatures and exact mathematical type annotations inside the kernel. Never require a theory module to use a signature DSL, encode standard call mechanics, describe absent parameters, or state compiler mechanics. |
| `POL-KERNEL-025` | Compile operations from inherited categories, morphism-property categories, and construction categories onto every descendant `ObjectType`, `ElementType`, and `MorphismType`. A missing inherited inverse, universal morphism, or other placement-forced operation is a kernel defect. It never licenses leaf wiring. |
| `POL-KERNEL-026` | Compile each inverse-image property subcategory produced under `POL-CAT-084` and `POL-CAT-100`. Build its class MRO, construction dispatcher, containment proposition, refinement, and inherited predicate behavior directly from the retained pullback category and its functors. |
| `POL-KERNEL-027` | Let `Fun(Source, Target)` construct functors from complete object and morphism actions. Implement the composition and evaluation functors and their natural-transformation actions there. Let each product, pullback, comma, fiber, image, `Fun([1], C)`, or other category construction create and retain its own named functors. Use universal properties to construct restrictions, induced pullback functors, and base changes. The kernel never interprets a leaf presentation to select one. |
| `POL-KERNEL-028` | Review `ObjectType`, `ElementType`, and `MorphismType` compilation against [specs/resolution.md](specs/resolution.md): Sage builds the applicable `parent_class`, and the same rule applies to objects, elements, and morphisms. |
| `POL-KERNEL-029` | Review selected inherited execution against [specs/resolution.md](specs/resolution.md): a leaf initializes only its own local state, each functor action constructs the separate public image, and the kernel supplies each inherited target implementation state once by running the object action during construction; no declaration calls a base-class initializer. |
| `POL-KERNEL-030` | Review runtime-category caching against [specs/resolution.md](specs/resolution.md): cache `_RuntimeImplementationCategory(C, kind)` by owned-category identity and exact kind, after normalizing categorical level identities. |
| `POL-KERNEL-031` | Review class compilation against [specs/resolution.md](specs/resolution.md): Sage owns category traversal, controlled C3, and dynamic-class construction, while the repository keeps the semantic collision check and unresolved-diamond diagnostic. Every owned structural diamond compiles with one shared implementation occurrence; absent explicit owned coherence, it produces only opt-in `DEBUG` output, never a warning, failure, public-image comparison, or coherence proof. Future suppression uses ordinary owned 2-morphism data rather than a certificate, proof record, route registry, or second functor declaration. |
| `POL-KERNEL-032` | Review private cache choice against [specs/resolution.md](specs/resolution.md): use Sage exact-key caches for ordinary equality, `MonoDict` or `TripleDict` only for proposition-valued equality, and `dynamic_class(..., cache=True)` for kernel-built classes. |
| `POL-KERNEL-033` | Review property-class binding against [specs/resolution.md](specs/resolution.md) and [specs/property-refinement.md](specs/property-refinement.md): Sage binds implementation classes, while `Cat` owns the property category, predicate, inverse images, and monomorphism. |
| `POL-KERNEL-034` | Review private construction-family binding against [specs/resolution.md](specs/resolution.md): Sage factories supply binding and caching, while owned functors determine the implementation edges and the owned cone or cocone retains the universal data. |
| `POL-KERNEL-035` | Review hom and functor boundaries against [specs/resolution.md](specs/resolution.md) and [specs/functor.md](specs/functor.md): Sage `Hom`-level types stay leaf-local, and generic `Mor` and `Fun` stay owned by `Cat`. |
| `POL-KERNEL-036` | Review declaration and wrapper tooling against [specs/resolution.md](specs/resolution.md): use Python 3.14 `ast` for ordinary declarations and generated stubs, LibCST only for syntax-preserving codemods, and Sage introspection with wrapt for residual runtime behavior. |
| `POL-KERNEL-037` | Every red-flag shape in `POL-LEAF-063` through `POL-LEAF-067` names a missing kernel capability. The repair adds that capability to the kernel generically and deletes the leaf wiring; a leaf-local patch that keeps the shape is rejected (D133). |
See [Leaf category implementations](specs/leaves.md) for the exact boundary between
kernel-owned inheritance and leaf-owned computation.

Structure functors are executable inheritance declarations.
A leaf states its immediate mathematics and then uses inherited operations as native methods.
If a leaf must inspect a route or recover an ancestor implementation, the kernel abstraction has failed.

For example, `__pow__(self, exponent: ObjectType) -> ObjectType` (the exponential object) already states
the type it applies to, its argument, call shape, and result type.
The leaf does not repeat those facts in a transport decorator.
The result remains an `ObjectType`; it is not a plain value used to evade transport.
The signature supplies the complete compiler input. Theory modules add no parallel call metadata.

Given `A in Monoids(M)` and a chosen left `M`-actegory `C`, a presentation of
`Modules(A, C)` retains an object `X in C` and an action morphism
\(\rho:A\mathbin{\bullet}X\to X\). It also retains the unit and action equations.
Its projection to `X` supplies the inherited `C` interface. When `C` has the required
closed or enriched structure, the same action can correspond to a monoid morphism
\(A\to\operatorname{End}_{C}(X)\).

Present an \(R\)-lattice \(L=(N,b)\) as a subobject of a product category whose first factor is the applicable `Modules(R, C)`. The corresponding product projection supplies the module interface.
The lattice exposes `L.bilinear_form()` to return \(b\); it does not inherit the full interface of a bilinear-form morphism.
An internal pair representation remains valid, but callers do not need `L.underlying_module()` to use \(L\) as a module.
Cardinality then arrives through the selected named functor from `C` to `Sets()`.
A lattice-specific cardinality implementation signals a missing or incorrect structure functor.

If `Modules(R, C)` has a supplied monoidal structure, every structural descendant can form its tensor-product subcategory.
For lattices, the leaf-specific lift is

\[
\bigotimes_i(L_i,b_i)=\left(\bigotimes_iL_i,\ \bigotimes_i b_i\right).
\]

The module subtree owns the tensor-product objects, elements, morphisms, and universal property.
The lattice subtree supplies only the induced bilinear form and its compatibility with `product_projection(0)` to `Modules(R, C)`.

A new specialized algebra category should start from the leaf template, select its named functors to nearby algebra and module categories, and add only its new algebraic methods.
It receives distant operations such as cardinality through the resulting functor chain without importing or reimplementing them.

For a toy leaf, `FiniteSubsetsOfNN()` declares its research-specific constructors, its monomorphism into `Sets()`, and methods such as `minimal_element()` or `gcd_of_elements()`.
Its elements automatically receive the `Sets().ElementType` interface through `FiniteSubsetsOfNN().ElementType`, even when the leaf adds no element methods.
Products, coproducts, filtered limits, and other set constructions require no leaf implementations.
Their results use the category that owns each construction and return to the leaf when closure is declared or derived.

For `Posets()`, the minimal new object data is an object of `Sets()` together with a partial-order relation.
Its product-subobject construction supplies `product_projection(0)` to `Sets()`. This functor supplies membership, iteration, cardinality, elements, and set maps through the compiled interface.
`FinitePosets()` declares its monomorphism into `Posets()` and its compatible route to `FiniteSets()`.
It does not copy the poset representation or reuse the poset element type.

`Posets().Products()` is the formal product-construction subcategory obtained from the product functor.
Its lift equips the inherited product apex with componentwise order and maps product morphisms accordingly.
It does not subclass the generic product implementation or construct a second set product API.

`TotallyOrderedSets()` refines partial orders by the totality property alone.
An enumeration is additional mathematical structure and therefore belongs to a separate category with its own structure functor to `TotallyOrderedSets()`.

## Mathematical encapsulation and repository layout

| ID | Policy |
| --- | --- |
| `POL-LAYOUT-001` | Keep a leaf subtree expressed in the language of its own category, its defining structure, and its immediate structure functors. Deeply underlying operations belong to the category that owns them. |
| `POL-LAYOUT-002` | Treat a reference to cardinality inside a lattice subtree as an ownership defect. Cardinality reaches lattice objects through their structure functors to modules and sets. |
| `POL-LAYOUT-003` | Make filesystem subtrees follow mathematical ownership boundaries. A reader must be able to audit one category without reading implementations owned by unrelated categories. |
| `POL-LAYOUT-004` | Quarantine the non-mathematical implementation kernel in its own subtree. Category compilation, descriptors, dispatch, and other standard Python machinery belong behind this boundary and never mix with mathematical theory code. |
| `POL-LAYOUT-005` | Mirror each source subtree in the test layout. Quarantine all implementation-kernel tests in a dedicated kernel testing subtree and keep each category's tests with that category's proof obligations. |
| `POL-LAYOUT-006` | Split `Cat`, `Sets()`, modules, formed modules, algebras, and other substantial mathematical owners into separate subtrees when one-file or shared-subtree organization impedes a complete local audit. |
| `POL-LAYOUT-007` | Give a frequently used property subcategory its own nested subtree when its constructors, morphisms, algorithms, and tests form a substantial unit. Examples include finite or countable sets and free modules or algebras under stated ring hypotheses. |
| `POL-LAYOUT-008` | Keep public mathematical signatures and results free of engine types, storage vocabulary, generic container types, and non-mathematical dispatch. Permit private engine use inside an executable category-owned computation boundary. |
| `POL-LAYOUT-009` | Put category-independent Sage, SymPy, and other engine adapters in dedicated backend subtrees. A category-specific private engine helper can remain beside its mathematical owner under `POL-LAYOUT-020`. |
| `POL-LAYOUT-010` | Confine engine imports, engine classes, conversion code, and engine-specific exceptions to private computation boundaries. Translate inputs before the engine call and reconstruct owned results before return. |
| `POL-LAYOUT-011` | Define and implement the public mathematical operation on its category-owned implementation class. A backend module supplies private representations, conversions, or raw computations rather than another implementation of that interface. |
| `POL-LAYOUT-012` | Keep a mathematical leaf change outside the kernel code and kernel-test subtrees. If the kernel boundary cannot support the leaf, treat that fact as a separate foundational defect instead of modifying the kernel as part of the leaf. |
| `POL-LAYOUT-013` | Make dependency direction visible in the layout: category implementations depend on the kernel, immediate mathematical owners, and any fixed private computation helper. Engine helpers never depend on compiler dispatch or define public category classes. |
| `POL-LAYOUT-014` | Audit mathematical purity by public semantic surface. Engine types in signatures or results, primitive collection semantics, coordinate representations, and unrelated invariants indicate misplaced responsibility. A private exact engine call does not. |
| `POL-LAYOUT-015` | Permit a private engine boundary to use engine-specific types and required Python representations. Keep those values private and return them only to the category-owned method that reconstructs the semantic result. |
| `POL-LAYOUT-016` | Split a large mathematical module by coherent mathematical owners, properties, or constructions, not by line count, implementation technique, or an arbitrary group of helpers. Keep the owning category visible in each module name. For `Sets()`, suitable modules include `setsubsets.py`, `setproducts.py`, `setcoproducts.py`, and `setlimitscolimits.py` when each forms a substantive mathematical unit. |
| `POL-LAYOUT-017` | Move generic non-mathematical wiring into relatively private infrastructure modules whenever it can be separated from the definitions. Keep registration, compiler hooks, structural dispatch, and route caches out of mathematical modules. A local private computation call is not generic wiring. |
| `POL-LAYOUT-018` | Preserve separate audit surfaces for mathematics and engineering. A mathematical module must be reviewable against definitions and theorems without following private runtime wiring; an infrastructure module must be reviewable for implementation correctness without deciding new mathematics. |
| `POL-LAYOUT-019` | When one implementation class becomes a substantial audit unit, place that sole class in a neighboring module named for its exact mathematical type and link it from the category declaration. Do not duplicate declarations in the category module. |
| `POL-LAYOUT-020` | Create a neighboring engine-specific module only for substantial shared lowering, conversion, caching, foreign-function or process integration, or raw computation. Use the concrete engine name, keep the module private, and do not create one by default for every category. |
| `POL-LAYOUT-021` | Enforce the layer dependency direction. Kernel and `Cat` theory modules never import production leaves. A leaf imports no kernel internals and depends only on its own owner, exact immediate mathematical targets, generic categorical constructions, and private computation helpers. A backend never registers categories, refines owned values, controls assumptions, or defines generated public surfaces (D122). |

See [Leaf category implementations](specs/leaves.md) for the permitted file layouts and
the single-source-of-truth rule.

Grounding examples: a sheaf is an object of a sheaf category, and an internal Hom of sheaves is again a sheaf.
A functor is an object of `Fun = Mor(Cat())` and of `Fun(C, D) = Mor(Cat())(C, D)` for its fixed endpoints. None enters `Sets()` without a specified functor.

Do not split `sets.py` into `sets_part_1.py`, `sets_helpers.py`, or files chosen only to satisfy a length limit.
Split it into category-qualified mathematical units such as `setsubsets.py`, `setproducts.py`, `setcoproducts.py`, and `setlimitscolimits.py` when those units have distinct objects, morphisms, universal properties, or algorithms.
Place class compilation, generated constructor setup, caches, registration, and backend conversion in private infrastructure modules outside those mathematical units.

## Functors and universal constructions

| ID | Policy |
| --- | --- |
| `POL-FUN-001` | Every functor is a morphism in `Cat` and uses `Cat().MorphismType`. It owns its domain, codomain, object map, and morphism map through that uniform morphism implementation. |
| `POL-FUN-002` | A functor owns its complete object and morphism actions. For a point `x: * -> X` and a functor `G: X -> Y`, its point image is the composite `G after x: * -> Y`. Selecting a structure functor contributes the applicable target implementation classes while leaving those two actions unchanged. |
| `POL-FUN-003` | Only structure functors contribute inherited public methods. Returning an ordinary functor from `structure_functors()` changes compiler behavior only; it does not change that functor's mathematical type in `Fun` or assert a subcategory relation. |
| `POL-FUN-004` | Use ordinary functors for mathematical transport that does not define public inheritance. |
| `POL-FUN-005` | Represent each projection, scalar change, and modeled mathematical realization as an explicit functor. Do not treat a private engine representation, cache, or algorithm call as a realization functor. |
| `POL-FUN-006` | Use functor composition to propagate structure. Do not add a separate propagation registry. |
| `POL-FUN-007` | A categorical construction must define its action on objects and morphisms. |
| `POL-FUN-008` | A limit or colimit constructor selects a universal presentation and returns its apex. The cone or cocone retains its diagram, legs, apex, and universal morphisms. Keep this selected presentation separate from property-subcategory membership. |
| `POL-FUN-009` | A selected product cone retains its diagram, apex, `leg(i)` morphisms, and mediating morphism. |
| `POL-FUN-010` | A selected coproduct cocone retains its diagram, apex, legs, and mediating morphism. |
| `POL-FUN-011` | Let the apex of a universal construction inherit operations from the category in which it lives. |
| `POL-FUN-012` | Implement arbitrary small diagrams. Do not encode finiteness into the general construction. |
| `POL-FUN-013` | Represent a subobject by an object together with its monomorphism. |
| `POL-FUN-014` | Obtain the containing object of a subobject from the monomorphism's codomain. |
| `POL-FUN-015` | For `F: D -> C`, distinguish `C.StrictImage(F)`, whose objects are literal values `F(X)` and whose morphisms are the morphisms of `C` equal to some `F(f)`; `C.FullImage(F)`, the full subcategory on the literal object image; and `C.EssentialImage(F)`, the replete full subcategory on objects isomorphic to some `F(X)`. Retain their inclusions and the applicable factorizations of `F`. Follow [Mathlib, essential image](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/EssentialImage). |
| `POL-FUN-016` | Implement products, coproducts, limits, and colimits as functors on diagrams, including their action on diagram morphisms. |
| `POL-FUN-017` | Define `Fun = Mor(Cat())`. Represent a functor `F: C -> D` as an object of `Fun(C, D) = Mor(Cat())(C, D)`. Its object and morphism actions come from `Cat().MorphismType`. Do not reduce it to a callable or set of assignments. |
| `POL-FUN-018` | Treat membership in `C.EssentialImage(F)` as the existential image property. A preimage can be selected when an operation needs one, but no selected preimage belongs to the membership data. The standard factorization through the essential image retains an essentially surjective functor followed by a fully faithful inclusion. |
| `POL-FUN-019` | Define `C.Products()` as the union of the full images of the chosen product functors `Prod_J: Fun(J, C) -> C` for nontrivial discrete shapes `J`; define `C.Coproducts()` dually. Define `C.TensorProducts()` and analogous named interfaces from their selected construction functors. Reach each interface through its retained full subcategory monomorphism. A selected product presentation is an object of the applicable `LimitCones(D)`, with `apex()` and `leg(i)`. Distinct diagrams and distinct limiting cones remain distinct presentations, including when their apex objects are identical. Their common apex has a fiber of presentations. Keep the apex interface distinct from `C.EssentialImage(Prod_J)`, which records the replete existential property. |
| `POL-FUN-020` | Lift an inherited universal construction through the structure functor. Retain its chosen diagram, constructed object, universal morphisms, and comparison map instead of reconstructing a parallel result. |
| `POL-FUN-021` | Establish properties of lifted objects and morphisms from the theorem of the construction. Record those facts at the construction owner instead of replacing that theorem with a presentation-specific check. |
| `POL-FUN-022` | Discharge closure and morphism-property obligations through the construction-owned lift. The lift can declare the typed conclusion of its construction theorem without runtime proof. Do not rely on a permissive general constructor that would admit the same property for arbitrary inputs. |
| `POL-FUN-023` | Implement the functor laws for every functor. Preserve identities and composition, and map an isomorphism inverse to the inverse of its image: `F(f.inverse()) == F(f).inverse()`. Structural descendants use this generic action and never add leaf-specific inverse transport. |
| `POL-FUN-024` | Define fullness, faithfulness, full faithfulness, essential surjectivity, and equivalence as properties of named objects in `Fun(C, D)`. Give each one a property subcategory, category-owned predicate meaning, and public SymPy predicate. State these properties on the named functor. |
| `POL-FUN-025` | Define `FullyFaithful(F)` as `Full(F) and Faithful(F)`. Treat it as a property without selected preimage morphisms. A construction that needs a chosen preimage morphism owns that separate choice. |
| `POL-FUN-026` | Use external mathematics to select the strongest applicable functor-property subcategory. The code writer constructs the functor directly there, and the constructor trusts that assertion. Use `assume(F.is_P())` for an interactive hypothesis. Neither route proves or certifies the property. |
| `POL-FUN-027` | Let `Fun(C, D)` own construction of every functor `C -> D`. The endpoints determine only this morphism category `Mor(Cat())(C, D)`. A specialized constructor needs mathematical data that selects one functor. Category constructions create their projection and evaluation functors through `Fun(C, D)` and retain them as defining data. |
| `POL-FUN-036` | Propagate established placement from `S` to `T` along a functor that is both a monomorphism of `Cat()` and an isofibration, and along no other functor. A leaf declares the relation by constructing in `Fun(S, T).Monomorphisms().Isofibrations()`, and a full subcategory adds `.Full()`. Monicity is faithfulness with injectivity on objects, so one value is shared rather than copied. The isofibration condition is repleteness of the subcategory, which is what makes strict membership respect the principle of equivalence; without it a skeleton would qualify, and a cardinal would be a set. A subcategory is a subobject of `T` in `Cat()`, and no intrinsic choice of representative exists, so the leaf declares which monomorphism placement follows through the owning property category and the kernel trusts that declaration. Never infer the relation from Python inheritance, shared storage, or a table of previously constructed functors. See `specs/functor.md`, "Monomorphisms of `Cat()` and placement". |
| `POL-FUN-028` | Name every functor by the construction that supplies it. Fixed endpoints, a source object presentation, or a collection of Python fields do not select an object of `Fun(C, D)`. Use the exact projection, inclusion, evaluation, composite, or right adjoint to a named free functor. For `Posets() -> Sets()`, use the fibration projection `(X, R) |-> X`. |
| `POL-FUN-037` | Every method makes its choices explicit. A method that returns the image of a value in another category names the exact functor and both endpoints. Construct that functor, retain it, return it from `structure_functors()` when it supplies inheritance, and apply it by name. Wanting a set means constructing and applying the named functor into `Sets()` (`POL-CAT-096`). |
| `POL-FUN-038` | Make `Adjunctions(F, G)` retain a unit `Id => G compose F`, a counit `F compose G => Id`, and the triangle identities. A morphism is a pair of endotransformations of `F` and `G` compatible with these data. Make `Equivalences(C, D)` retain a functor, an inverse functor, and unit and counit natural isomorphisms. Its morphisms are natural transformations between the forward functors, as in Mathlib's category of equivalences. Keep these selected data distinct from membership in `Fun(C, D).Equivalences()`. Follow [Mathlib, adjunctions](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Adjunction/Basic.html) and [Mathlib, equivalences](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Equivalence.html). |
| `POL-FUN-039` | For each shape `I`, define `.PreservesLimits(I)` and `.CreatesLimits(I)` as property subcategories of `Fun(C, D)`. Derive the colimit properties through `Op`. A right adjoint lies in each applicable limit-preservation subcategory; a left adjoint lies in each applicable colimit-preservation subcategory. An equivalence creates and reflects both. Follow [Mathlib, adjunctions and limits](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Adjunction/Limits.html) and [Mathlib, creates limits](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Limits/Creates.html). |
| `POL-FUN-040` | When chosen `I`-limits exist, retain the diagonal functor `Delta_I: C -> Fun(I, C)`, the limit functor `Lim_I: Fun(I, C) -> C`, and an object of `Adjunctions(Delta_I, Lim_I)`. Obtain products from discrete shapes. Derive colimits and coproducts through `Op`. |
| `POL-FUN-041` | Define `p.Fiber(b)` for every functor `p: E -> B`. A fibration adds cartesian lifts and reindexing functors between these fibers. For `F: D -> B`, `F.base_change(p)` is the pullback projection `D ×_B E -> D`; if `p` is a fibration, the result inherits the pulled-back cartesian lifts. |
| `POL-FUN-042` | For `F: C.op() -> Sets()`, make `Representations(F)` contain pairs `(X, eta)` with `X in C` and a natural isomorphism `eta: yoneda(X) -> F`. A morphism `(X, eta) -> (Y, theta)` is a morphism `u: X -> Y` for which `theta compose yoneda(u) = eta`; Yoneda makes every such morphism an isomorphism. `F` is representable exactly when this category is inhabited. A computation that needs a representing object selects one object of `Representations(F)`. |
| `POL-FUN-029` | Name and construct each functor by its mathematical source: a product projection, coproduct injection, subcategory monomorphism, evaluation at an object of the shape, base change, fibration projection, opfibration projection, Kan extension, or explicit composition. Retain the data that defines it. |
| `POL-FUN-030` | Treat a Grothendieck fibration as a functor with specified cartesian lifts. Treat its dual as an opfibration, also called a cofibered category, with specified cocartesian lifts. Use “cofibration” only when a cited source uses it for this dual notion. Do not confuse it with a class of morphisms in topology or a model category. |
| `POL-FUN-031` | Form slice and coslice projections from the pullback projections of `C.SliceOver(x)` and `C.CosliceUnder(x)` as pullbacks of `Fun([1], C)`, composed with the evaluation functors `ev_0` and `ev_1`. `ev_1: Fun([1], C) -> C` is a fibration when `C` has pullbacks; the fixed slice projection `C.SliceOver(x) -> C` is a discrete fibration by precomposition for every `C`. State each lift at its construction owner; do not infer it from object fields. |
| `POL-FUN-032` | Let left and right Kan extension constructions own their resulting functors, units, counits, and universally induced natural transformations. These natural transformations are morphisms of the applicable fixed-endpoint functor categories. Build later routes by ordinary composition. |
| `POL-FUN-033` | Make `structure_functors()` select exact construction-named functors or composites. Selection does not create a preferred projection, an unnamed structure map, or another kind of functor. |
| `POL-FUN-034` | Never try to prove, certify, or check fullness, faithfulness, full faithfulness, essential surjectivity, equivalence, or another general functor property. Use external mathematics to choose the property subcategory, construct the functor there, and cite any nontrivial theorem beside that construction. |
| `POL-FUN-035` | Review functor actions against [specs/functor.md](specs/functor.md): `F.on_object(X)` and `F.on_morphism(f)` are the complete public declaration, selection changes compiler behavior only, and the kernel treats both bodies as opaque. |

### Why endpoints do not select a functor

Fixed endpoints do not determine an object of `Fun(C, D)`.
A presentation can also have several projections with different codomains.

For example, a presentation of a lattice as `(M, b)` has a projection to `M` and a
projection to `b`. Neither projection follows from the endpoints. A presentation of
a module by `rho: A bullet X -> X` has projections and evaluations determined by that
presentation. An equivalent presentation can expose different immediate projections.
The kernel must not inspect tuple positions or fields to choose one.

Use the construction that supplies the map:

- a subcategory supplies its monomorphism;
- a product supplies its component projections;
- a coproduct supplies its component injections;
- `Fun([1], C)` supplies its evaluation functors `ev_0` and `ev_1`;
- a slice or coslice supplies projections to its varying object and defining morphism;
- a fibration or opfibration supplies its projection and cartesian or cocartesian lifts;
- a base-change construction supplies its pullback or pushforward functor;
- a Kan extension supplies its extended functor and universal natural transformation;
- ordinary composition combines these maps into named composite functors.

A category can select one such functor in `structure_functors()`. This selection states
the exact immediate target used for dynamic class inheritance. It does not make that functor a
canonical map determined by the category alone.

Mathlib's `ConcreteCategory.forget` and `HasForget₂.forget₂` are chosen functors carried
as extra structure. They are not derived from their endpoint categories. This repository
models the underlying construction directly and does not add a generic constructor for
that convention. See [the Mathlib concrete-category definition](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/ConcreteCategory/Forget.html).

For the product functor `Products: Diag(C) -> C`, an object `Y` lies in
`C.EssentialImage(Products)` when some `Products(D)` is isomorphic to `Y`. This full
replete subcategory records no selected diagram or projections.

For each diagram `D`, `C.Products()(D)` selects `p in LimitCones(D)` and returns
`p.apex()` in `C.Products()`. The cone `p` owns its diagram, legs, and universal maps.
`C.Products()` is the full subcategory of `C` on the literal object images of the chosen
product functors. The chosen product also lies in the applicable essential image.

For `C = Sets()`, cardinality is the inherited set operation applied to the product object and satisfies \(\#(\prod_i X_i)=\prod_i\#X_i\).
The products category does not define a second set interface or an independent cardinality operation.

## The category of sets

| ID | Policy |
| --- | --- |
| `POL-SET-001` | `Sets()` owns arbitrary sets and arbitrary functions between them. |
| `POL-SET-002` | A set map requires a domain, codomain, and rule. It does not require a finite table. |
| `POL-SET-003` | Permit maps whose rules have no linearity, continuity, or finiteness hypothesis. |
| `POL-SET-004` | Support maps such as `QQ -> NN`, `QQ -> ZZ`, and `RR -> RR^2` as ordinary morphisms in `Sets()`. |
| `POL-SET-005` | Let set-membership predicates return applied propositions. Use `ask()` to obtain `True`, `False`, or `Unknown`. Python containment is the Boolean admission boundary. |
| `POL-SET-006` | Treat `Unknown` as unavailable knowledge, not as `False`. |
| `POL-SET-007` | Construct a predicate-defined subset as an object with its monomorphism into the ambient set. |
| `POL-SET-008` | Support infinite predicate subobjects such as the even integers and prime integers inside `ZZ`. |
| `POL-SET-009` | Put cardinality on the set implementation. |
| `POL-SET-010` | Support finite, infinite, and symbolic cardinal values. `X.cardinality()` returns an applied query whose result category is `Cardinal()`. `ask(X.cardinality())` returns an owned cardinal or Sage `Unknown`. A cardinal is always exact and contains no unresolved value. |
| `POL-SET-011` | Use cardinality for sets. Use length only for an ordered finite sequence. |
| `POL-SET-012` | Support function sets and exponentials. |
| `POL-SET-013` | Support products and coproducts indexed by arbitrary small diagrams. |
| `POL-SET-014` | Support general limits and colimits in `Sets()`. |
| `POL-SET-015` | Propagate set operations, including cardinality, to objects produced by functors and universal constructions. |
| `POL-SET-016` | Derive structural properties from construction data, defining predicates, functors, injections, bijections, and universal constructions before considering enumeration. |
| `POL-SET-017` | Use one parent and implementation for the set of functions `X -> Y` and the exponential `Y ** X`. `Mor(Sets())(X, Y)` is the discrete category on the elements of `Y ** X`. |
| `POL-SET-018` | Use one parent and implementation for `P(X)`, `2^X`, and `2 ** X`, where `2 = [1] = {0, 1}`. |
| `POL-SET-019` | Construct a set morphism from a well-typed callable or explicit mapping data. A callable must represent maps such as `QQ -> ZZ` without enumerating `QQ`. |
| `POL-SET-020` | Register the exact evaluation cases `#(X × Y) = #X #Y`, `#(X ⊔ Y) = #X + #Y`, and `#(Y^X) = (#Y)^(#X)` on the corresponding `Sets()` constructions. Each case applies only when `ask()` has exact operand cardinalities. |
| `POL-SET-021` | Let the category-owned implementation of each set construction register its exact cardinality-query cases from retained construction data. Keep this evaluation behind `X.cardinality()` and `ask()`. |
| `POL-SET-022` | Let `ask(X.cardinality())` return an owned cardinal. Compare that cardinal through the ordinary cardinal equality predicate. Never expose a cardinal's engine value. |
| `POL-SET-023` | Give every object of `Sets()` the complete `Sets().ObjectType` method surface, including products, coproducts, subsets, exponentials, and the morphism categories `Mor(Sets())(X, Y)`. |
| `POL-SET-024` | Make set products and subsets delegate to the categorical product and subobject constructions instead of defining parallel APIs. |
| `POL-SET-025` | Make `Cardinal()` the set-enriched skeletal category of cardinal representatives. Its morphism categories are discrete on the function sets between selected representatives. Cardinal order is the existence of an injective map. Construct `Cardinal()` directly as an internal semiring object in `Cat()`. Cardinal objects form an ordered semiring of finite, infinite, and symbolic values. `Unknown` is not a cardinal. |
| `POL-SET-026` | Let cardinal arithmetic return cardinal values. Let cardinal equality and order return applied propositions. `ask()` returns `Unknown` when available mathematics does not decide one of those propositions. |
| `POL-SET-027` | Use `len()` only for a finite sequence whose order is part of its meaning. Use `cardinality()` for every mathematical set. |
| `POL-SET-028` | When `rank()` or `ngens()` counts a mathematical set, return its cardinality rather than a sequence length. |
| `POL-SET-029` | Before enumerating a set, determine how the operation behaves for an infinite set and for a very large finite set. Keep unbounded enumeration out of the normal path. |
| `POL-SET-030` | Enumerate to compute cardinality only when a concrete cardinality is required, finiteness is established, and no construction formula or structural relation supplies it. |
| `POL-SET-031` | A constructor that knows a set's cardinality or structural property records it. Functors and related objects derive and transport that information. |
| `POL-SET-032` | Use `NN` for the positive integers. Zero is not an element of `NN`; use `ZZ_{>=0}` for the nonnegative integers. |
| `POL-SET-033` | Apply `POL-API-015` to cardinalities and standard integers. Write `k == 3`, `k <= 3`, or `3 < k`; do not expose named cardinal comparison methods or require integer coercion. |
| `POL-SET-034` | Never require a caller to extract a stored value from a cardinality. A cardinal is the mathematical value, not a wrapper around one; public code does not use `.value`, `.finite_value()`, or an equivalent accessor to compare, calculate with, display, or return it. |
| `POL-SET-035` | Define modulus with domain a finite cardinal `k` and a positive natural cardinal `n`. The value `k % n` is the finite cardinal represented by the natural-number remainder. |
| `POL-SET-036` | Make `Mor(Sets())(X, Y)` the morphism category in `Sets()`: the discrete category whose objects are the total maps from `X` to `Y`. The exponential `Y ** X` is the owned set of those maps, and `Mor(Sets())(X, Y)(rule)` constructs one of them. |
| `POL-SET-037` | Give standard ordinal notation its standard meaning: `alpha + beta` is ordinary ordinal sum and `alpha * beta` is ordinary ordinal product. Expose the Hessenberg operations as `alpha.natural_sum(beta)` and `alpha.natural_product(beta)`. Keep ordinal exponentiation as `alpha.ordinal_power(beta)` because `**` denotes the categorical exponential. |
| `POL-SET-038` | Define `OrdinalOrder()` and `CardinalOrder()` as thin categories with the same owned objects as `Ordinals()` and `Cardinal()`, and a unique morphism exactly when the source is at most the target. Define `Aleph: OrdinalOrder() -> CardinalOrder()` and `InitialOrdinal: CardinalOrder() -> OrdinalOrder()`. Their morphism actions use monotonicity on the unique order arrows; neither is a functor on arbitrary cardinal-representative functions. |

Grounding examples: the even positive integers are infinite, and \(\{1,2,\ldots,10^{10}\}\) is finite but unsuitable for materialization.
The set \(\{n\in\mathbb N\mid n\leq100\}\) is finite from its defining bound.
None requires enumeration to establish finiteness.

If `k` is a cardinal, write `k == 3`, `k <= 3`, or `3 < k`.
Do not write `k.equals(3)`, `k.le(3)`, `k.value == 3`, or `k.finite_value() <= 3`.
When an established finite algorithm requires a primitive loop bound, lower the cardinal once inside that private computation boundary.

## Sage boundary

| ID | Policy |
| --- | --- |
| `POL-SAGE-001` | The owned framework defines the mathematical category graph and public API. |
| `POL-SAGE-002` | Sage supplies computation objects, algorithms, coercion, and runtime machinery. |
| `POL-SAGE-003` | Cross into Sage only through an explicit realization functor or owned computation boundary. |
| `POL-SAGE-004` | Do not make a Sage category a mathematical supercategory of an owned category. |
| `POL-SAGE-005` | Do not modify Sage category classes or install owned methods on them. |
| `POL-SAGE-006` | Do not expose the Python method catalogue of a Sage implementation as the mathematical API. |
| `POL-SAGE-007` | Keep one owned public spelling for each mathematical operation. |
| `POL-SAGE-008` | Keep Sage's category runtime only for dynamic classes, refinement, joins, and construction support. |
| `POL-SAGE-009` | Preserve Sage `Parent`, `Element`, homsets, morphisms, and coercion where they implement the owned model. |
| `POL-SAGE-010` | Use Sage's exact algorithms before writing a parallel local implementation. |
| `POL-SAGE-011` | Use Sage's exact linear-algebra algorithms only behind the tensor realization boundary. Do not expose Sage vectors or matrices as owned objects. |
| `POL-SAGE-012` | Treat agreement with Sage or a Sage doctest as secondary evidence. It is not an independent mathematical oracle for owned behavior. |
| `POL-SAGE-013` | Do not memoize an owned mathematical value with a hash-and-equality cache, `sage.misc.cachefunc.cached_method` included. `==` on an owned value returns a proposition and `bool()` on it raises, so such a cache degenerates to hashing alone and fails on the first collision. Retain owned values by identity. |
| `POL-SAGE-014` | When one comparison operator is defined through another, state each from its own definition. Python tries the reflected operator first when the right operand's class is a proper subclass of the left's, and same-object refinement makes exactly that true, so `__ge__` written as `other <= self` calls itself without bound as soon as one operand is refined. |
| `POL-SAGE-015` | Bind every public name in the module whose source declares it. Assigning into another module's namespace at import time produces a name no source writes, which the static projection cannot state and a reader cannot find. A provisional binding that a later import overwrites is the same defect. |

## Public API and types

| ID | Policy |
| --- | --- |
| `POL-API-001` | Shape the API from the mathematics, not from current storage fields or Python classes. |
| `POL-API-024` | Give two distinct notions two names. Never let one spelling carry a general meaning on one class and a narrower meaning on a subclass. The compiler rejects unrelated declarations with the same name. |
| `POL-API-025` | Use only the exact names `C.ObjectType`, `C.ElementType`, and `C.MorphismType`. A category specifies these classes, and the kernel constructs them dynamically from the structure functors. For each structure functor `F: C -> D`, `C.ObjectType` inherits `D.ObjectType`. The applicable `C.ElementType` and `C.MorphismType` surfaces inherit the corresponding target classes. A leaf never constructs this inheritance. |
| `POL-API-026` | Let a method's return annotation state what the body returns. Use `Self` only when the method returns the same value. Use the exact owned result type for every other method. |
| `POL-API-027` | During version 1, add no method for an operation expressible as one or two lines of public compositional code. Apply this rule to every specification and category level. Expose the defining mathematical data at its owner, then compose existing operations at the call site. For a unary property, define the property subcategory and its containment predicate once; the standard `is_P()` application comes from that declaration and is not a second operation contract. |
| `POL-API-002` | During version 1, give each operation one mathematical owner and one canonical public spelling. Define a category operation once on `Cat().ObjectType` when every category must have it; ordinary inheritance supplies that method to each category. A public method declared on another owned implementation type follows the same rule. A standard mathematical operator invokes the same owned implementation. Type-specific and leaf-specific convenience aliases begin after version 1. |
| `POL-API-003` | Use standard mathematical and Sage syntax at call sites. |
| `POL-API-004` | Use `as_*` only for an explicit conversion to another mathematical representation. |
| `POL-API-005` | Keep private fields private to their owner or documented subclass contract. |
| `POL-API-006` | Ask another object through its public mathematical interface. |
| `POL-API-007` | Invoke Python special methods through public syntax such as `f(x)`, `iter(x)`, and `len(x)`. |
| `POL-API-008` | Name an accessor for the exact mathematical object or morphism it returns. |
| `POL-API-009` | Use positional standard notation: `Mor(C)(X, Y)` is the morphism category from `X` to codomain `Y`, and `Mor(C)(X, Y)(data)` constructs a morphism `X -> Y`. |
| `POL-API-010` | Let callers construct morphisms only through `Mor(C)(X, Y)(data)` and objects only through `C(data)`. The category-owned constructor is the sole dispatch. |
| `POL-API-011` | Treat every public method-name collision as mathematical ambiguity. Resolve it by naming the exact mathematical operation, not by inheritance precedence, overload selection, or context. |
| `POL-API-012` | Let a structured object expose every applicable operation under its unambiguous name. Its discoverable method surface must preserve distinctions between its structures. |
| `POL-API-013` | Name categorical morphisms as morphisms. Do not replace the standard mathematical object with implementation names such as `Map` or `Rule`. |
| `POL-API-014` | Ban nondescript identifiers that do not state what they contain or denote. Never name a type, method, parameter, field, or local value `data`, `container`, `rule`, `value`, `values`, or a similarly contentless term. |
| `POL-API-015` | Make every mathematical object and element use standard Python or Sage syntax for comparison, equality, containment, indexing, iteration, and calls. Do not expose a named method that forwards to an operator or special method. Write `x <= y`, `x == y`, and `x in X`; never write `x.le(y)`, `x.equals(y)`, or `X.contains(x)`. On every owned object, element, and morphism, `__eq__` returns the applied equality predicate and `__ne__` its negation; `ask(a == b)` decides it; the predicate's `__bool__` raises. Containment `in` remains the one Python Boolean boundary and fails loudly when `ask()` returns `Unknown`. `__hash__` is explicit: objects and morphisms hash by identity, and a point hashes by its chosen datum. |
| `POL-API-016` | Prefer a method or constructor on the mathematical owner over a standalone public function. Add a standalone public function only when the operation has no natural category, object, morphism, or functor owner. |
| `POL-API-017` | Never expose a method whose complete implementation only asserts `False`, returns `NotImplemented`, or raises an error. Such a method advertises a capability that the object does not have. |
| `POL-API-018` | Use an abstract method when every concrete object must supply an implementation. Prevent construction of an incomplete concrete object instead of deferring the failure to a method call. |
| `POL-API-019` | When an operation requires a capability, place it on the category that supplies that capability and let the method compiler expose it there. Do not install a failing placeholder on objects outside that category. |
| `POL-API-020` | When a mathematical operation is not total and exact on its full declared domain, return an applied query with the exact category of its evaluated result. Let `ask()` return an owned result or Sage `Unknown`. A truth-valued operation returns an applied proposition, and `ask()` returns `True`, `False`, or `Unknown`. Never put `Unknown` inside an owned mathematical result type. |
| `POL-API-021` | Make every method and constructor total on its declared domain. Require every argument. Never use optional parameters, default values, `None` sentinels, or fallback behavior. Give genuinely different mathematical input forms or computations separate explicit names. An evidence source for one property is not another constructor form. |
| `POL-API-022` | Use the kernel's same-object refinement mechanism for every established positive property. The owning SymPy predicate supplies exact handlers. `assume(P(x))` uses `global_assumptions`. Named constructions establish the property directly. Never select evidence with a default, proof object, or prose. |
| `POL-API-023` | Never require a caller to supply a value uniquely determined by an established mathematical object or its category placement. Obtain that value from its owner. In particular, an isomorphism supplies its inverse; no leaf helper accepts a second candidate inverse. |
| `POL-API-028` | Construct every mathematical value through its owning category. Use `C(...)` for objects of `C`, `Mor(C)(X, Y)(...)` for morphisms, `Fun(C, D)(...)` for functors, and the applicable property or construction subcategory for refined or constructed objects. Put every convenience constructor on that owning category. Do not add a parallel `Cat`, kernel, factory, or helper namespace for values already owned by one of these categories (D119). |
| `POL-TYPE-001` | Give every value the type that names its exact mathematical type. |
| `POL-TYPE-002` | Distinguish categories, objects, elements, morphisms, functors, rings, sets, domains, and codomains in types. |
| `POL-TYPE-003` | Never use `object` in a type annotation. There are no exceptions. |
| `POL-TYPE-004` | Annotate the candidate parameter of every `__eq__` and `__contains__` method as raw `Any`. These two parameter positions are the only permitted uses of `Any`. |
| `POL-TYPE-005` | Never use `Any` as a return type. |
| `POL-TYPE-006` | Do not silence a type error with a cast, ignored diagnostic, deleted annotation, or wider type. |
| `POL-TYPE-007` | Fix the mathematical model, method owner, import boundary, or missing type declaration exposed by a type error. |
| `POL-TYPE-008` | Use category membership as type information. Do not inspect fields or method names for capabilities. |
| `POL-TYPE-009` | Do not invent wrapper types whose only purpose is to satisfy the type checker. |
| `POL-TYPE-010` | Return `Self`, `None`, or the exact mathematical result type. Use the element type of `NN`, `ZZ`, or `RR` for natural numbers, integers, or real numbers. |
| `POL-TYPE-011` | Use a set, ordered set, multiset, indexed family, or another named mathematical collection in every theory-layer mathematical signature. The compiler-owned `structure_functors()` declaration returns the complete tuple required by `POL-CAT-085`. Never use `Iterable`, `Sequence`, `Collection`, `list`, or `tuple` for a mathematical collection. Use `float` only at an explicit numerical boundary. |
| `POL-TYPE-012` | Primitive signatures can occur inside a private method only when every consumer remains inside that private boundary. |
| `POL-TYPE-013` | Create a type for a genuine mathematical object. Do not wrap invalid constructor inputs in an engineering type to satisfy the checker. |
| `POL-TYPE-014` | Never alias `Any`, directly or as part of a wider alias. Such an alias erases type information while giving the erasure a misleading semantic name. |
| `POL-TYPE-015` | Do not create types with an `Input` suffix to model forms accepted by an implementation. Type each parameter as the mathematical object it denotes. |
| `POL-TYPE-016` | Use types to express the mathematics. Keep parsing, coercion, normalization, and representation conversion behind the typed mathematical boundary. |
| `POL-TYPE-017` | Type every morphism by the element types of its domain and codomain categories. Do not widen either endpoint to a generic mathematical-object type. |
| `POL-TYPE-018` | Give every category its own semantic object, element, and morphism types through `ObjectType`, `ElementType`, and `MorphismType`. Use those types throughout that category's API. |
| `POL-TYPE-019` | Type each method parameter and result by the most specific category that supplies the required structure. Do not widen it to an element or object type from a supercategory. |
| `POL-TYPE-020` | Preserve category-specific implementation classes even when a category adds no new runtime fields or methods. Same-object property refinement updates the Sage dynamic class to include the refined class. It does not erase the refinement or allocate a second semantic value. |
| `POL-TYPE-021` | Admit raw Python container types only inside the implementation kernel, a backend adapter, or a dedicated interoperation module. Convert them immediately into the required mathematical collection before theory code receives them. A theory constructor or helper is not such a boundary. |
| `POL-TYPE-022` | Use `Iterator[T]` only for the Python traversal protocol or a private lazy-enumeration result. It never replaces a named mathematical collection in a theory-layer input or result. |
| `POL-TYPE-023` | Treat type-checker and import output as diagnostic signals. An error can falsify the current implementation, but it cannot establish a new architecture or mathematical owner. The mathematical definitions, category ownership, and functor declarations determine correctness. |
| `POL-TYPE-024` | Make the category compiler expose functorial construction and dynamic object, element, and morphism inheritance to static type checkers. A checker's default inability to infer that structure does not justify weakening it. |
| `POL-TYPE-025` | When a checker cannot infer the declared dynamic structure, generate `.pyi` stubs from the authoritative category and functor declarations: one kernel generator projects the same compile-time ownership computation that installs methods, and the commit hook regenerates the stubs whenever a declaration changes. Stub generation is the sole projection mechanism. Do not maintain a second type graph by hand. |
| `POL-TYPE-026` | Treat generated static typing artifacts as output-only projections of repository-owned declarations. Runtime code, mathematical declarations, and compiler inputs never consume them as semantic authority. Regenerate them through the applicable commit, test, push, and release workflows whenever their source declarations change (D122). |
| `POL-TYPE-027` | Do not define or use `typing.Protocol` or another structural duck type. Type mathematical values through the exact category-owned `ObjectType`, `ElementType`, or `MorphismType`, and express capabilities through category membership and named functors. |
| `POL-TYPE-028` | Preserve the exact type a declaration applies to, and its positional-parameter, keyword-parameter, and result types, in its copied compiled method and generated typing artifact. `Callable[..., Any]` and `Callable[..., object]` are forbidden. |
| `POL-TYPE-029` | A broad union of unrelated exact mathematical types is type erasure. Do not combine it with `Callable[...]` or variadic parameters as a substitute for each method's exact signature. |

The runtime compiler constructs category relations dynamically, but one repository revision contains a finite declaration graph.
A generator can project that graph into static typing artifacts without changing its mathematical owner.

For example, `gens()` is ambiguous on an object that can be a group, module, and algebra.
Expose `group_generators()`, `module_generators()`, and `algebra_generators()` side by side.
Each name identifies the structure whose generating set it returns.

For example, `SomeMathematicalObjectInput` names constructor data rather than a mathematical object.
If the parameter denotes an element of a set, its type is `SetElement`.

The special-method signatures are `__eq__(self, candidate: Any)` and `__contains__(self, candidate: Any)`.
Use raw `Any` at those two special-method boundaries.

Likewise, do not define `MathematicalObject = Any` and then type `SetMapRule` as a callable on that alias.
A `SetMorphism` acts from `SetElement` to `SetElement`, with its specific domain and codomain stored on the morphism.
Its evaluation in `Mor(Sets())(X, Y)` can assert `x.parent() in self.base_category()` before verifying that `x` belongs to the declared domain `X`.

For a poset, define `PosetElement = Posets.ElementType` and type `is_sup(x: PosetElement)` accordingly.
Typing `x` as `SetElement` would admit an element without the required poset structure and conceal that error from static checking.

Likewise, use `OrderedSet[MyCatElement]`, not `Iterable[MyCatElement]`, when order and uniqueness are the mathematical input.
The latter type also admits raw lists, tuples, and Python iterators, which discards the required collection semantics.

Use `x <= y`, `x in X`, `X[i]`, and `x == y` instead of public methods such as `x.le(y)`, `X.contains(x)`, `X.index(i)`, or `x.equals(y)` that shadow that standard syntax.

Every object of `Sets()` has `cardinality()`.
It returns an applied query with result category `Cardinal()`.
`ask(X.cardinality())` returns an owned cardinal or Sage `Unknown`.
A method available only under an additional mathematical hypothesis belongs to the corresponding property category.

For example, a total set constructor requires a typed cardinality.
The finite, countably infinite, and uncountable property subcategories each own the
constructor that requires and supplies the semantic cardinal data for that property.

Likewise, a natural interval constructor constructs its result directly in the total-order category.
The identity constructor constructs its result directly in the poset morphism category `Mor(Posets())(P, P)`.
A named squaring builder on `NN` constructs its result directly in the same morphism category.
These methods rely on their defining theorems and do not run exhaustive decision procedures.
An arbitrary relation or map starts in its ambient category. Its category-owned SymPy predicate performs
any available exact check. Exact `True` self-refines it through the same property-category
constructor used by the named constructions.

Replace a nondescript name with the exact entity, such as `tensor_coefficients`, `ordered_set`, or `set_morphism`.

A method that enumerates solutions yields them lazily.
The caller can materialize a finite result when its application requires one.

## Implementation style

| ID | Policy |
| --- | --- |
| `POL-CODE-001` | Write each method in the order of the mathematical definition. |
| `POL-CODE-002` | Keep the implementation direct and readable to a mathematician. |
| `POL-CODE-003` | Do not hide defining steps behind non-mathematical helper chains. |
| `POL-CODE-004` | Add an abstraction only when a second real use requires it. |
| `POL-CODE-005` | Use existing project dependencies before adding code or packages. |
| `POL-CODE-006` | Use a maintained library or mature reference implementation before writing local infrastructure. |
| `POL-CODE-007` | Cite the mature source of unavoidable local implementation code. |
| `POL-CODE-008` | Do not add compatibility layers, fallbacks, migrations, or obsolete aliases. |
| `POL-CODE-009` | Keep one current implementation for each operation or construction. |
| `POL-CODE-010` | Fix a repeated defect at its mathematical owner, not at each call site. |
| `POL-CODE-011` | Fail loudly when required mathematical structure or a dependency is absent. |
| `POL-CODE-012` | Do not inspect `__dict__` or recover mathematical structure from storage fields. |
| `POL-CODE-013` | Do not use `setattr` to assemble or modify a mathematical API. Define the method on its owning category or class. |
| `POL-CODE-014` | Keep a matrix distinct from the morphism it represents. |
| `POL-CODE-015` | Keep coordinates distinct from elements of their parent. |
| `POL-CODE-016` | Lower to a computation representation once and reconstruct the mathematical result once. |
| `POL-CODE-017` | Preserve exact arithmetic until an explicit numerical boundary. |
| `POL-CODE-018` | Keep precision parameters at the numerical boundary. |
| `POL-CODE-019` | Remove needless recomputation, enumeration, and verification without obscuring the mathematics. |
| `POL-CODE-020` | Call the owned public method directly. Do not use `getattr(x, name)` to select a mathematical operation. |
| `POL-CODE-021` | Write `assert x in C` for a categorical precondition. Do not write `assert isinstance(x, C.ObjectType)`. |
| `POL-CODE-022` | Use assertions for mathematical preconditions, functionality gates, and type narrowing. |
| `POL-CODE-023` | Make each assertion state a mathematical fact that remains true when the Python implementation class or field layout changes. |
| `POL-CODE-024` | Use an assertion for a violated mathematical precondition. Do not add `try`/`except`, fallback values, or recovery branches. |
| `POL-CODE-025` | When code assigns mathematical ownership wrongly or cannot express the fixed owner, stop runtime debugging and local mechanism design. Reapply the standard definition, identify the owner it already determines, and repair `Cat`, the morphism categories `Mor(n, C)`, method inheritance, and `Sets()` in dependency order. |
| `POL-CODE-026` | During a foundational migration, move each required behavior to its new owner before deleting its old implementation. |
| `POL-CODE-027` | Do not use `hasattr` to guess mathematical capabilities. Ask category membership or call the required category-owned operation. |
| `POL-CODE-028` | Prefer a named primitive that states the mathematical construction over a generic Python composition that merely reproduces it. |
| `POL-CODE-029` | Actively search the standard library, Sage, current dependencies, and maintained packages for primitives that make theory code read more like mathematics. |
| `POL-CODE-030` | Propose a new dependency when it materially improves mathematical vocabulary, auditability, or categorical uniformity. State the mathematical construction that the dependency supplies. |
| `POL-CODE-031` | Use `sum` and `prod` for established finite algebraic aggregations instead of mutable accumulator loops. Use the categorical indexed construction when the family can be infinite. |
| `POL-CODE-032` | Prefer `map`, `reduce`, comprehensions, and named functional combinators when they state the mathematical transformation more directly than an imperative loop. |
| `POL-CODE-033` | Make method bodies functional and expression-oriented. This style concerns transformations inside mathematically owned methods, not a proliferation of standalone functions. |
| `POL-CODE-034` | Replace long structural `if` and `elif` cascades with exhaustive `match` and `case` routing when the cases form a mathematical decomposition. |
| `POL-CODE-035` | Handle trivial or decisive cases with early returns. Then assert the stronger invariants established by their exclusion before implementing the remaining case. |
| `POL-CODE-036` | Prefer immutable transformations, explicit case analysis, and local equations in the style of Haskell and Lean over C-style mutable state and control flow. |
| `POL-CODE-037` | Do not rewrap a value when the new wrapper does not change its required type or semantics. Calls such as `int(0)`, `Integer(0)`, and `ZZ(0)` require a local comment that proves why the conversion is necessary. |
| `POL-CODE-038` | Do not add a function or method whose body only forwards to another function, method, operator, or special method. A category-owned semantic method that lowers inputs, invokes a mature algorithm, or reconstructs an owned result is an implementation rather than a forwarding wrapper. |
| `POL-CODE-039` | Never write `try`/`except` outside the implementation kernel. Let errors propagate from theory, leaf, functor, construction, backend-adapter, and public API code. |
| `POL-CODE-040` | Never use exceptions to select a route, discover a capability, handle optional data, retry, choose an implementation, substitute a value, or continue computation. |
| `POL-CODE-041` | Never catch an exception to return `False`, `Unknown`, `None`, `NotImplemented`, or a default. An unknown mathematical result is explicit data, not a converted runtime failure. |
| `POL-CODE-042` | Compare mechanisms by their mathematical meaning and information flow, not by syntax or location. Moving the same duplicate classification between a decorator, annotation, wrapper, callback, registry, generated class, or helper module leaves the architecture unchanged. |
| `POL-CODE-043` | Locate the mathematical owner of every proposition, construction obligation, method, and ownership fact before adding runtime data. Derive its software representation from the standard definition. |

For adjacent elements, use `itertools.pairwise(xs)` instead of `zip(xs, xs[1:])`.
The named primitive states adjacency, remains lazy, and does not require slicing.
Use `zip` when the mathematics pairs separate indexed families.

Write a finite linear combination as `sum(c_i * e_i for c_i, e_i in terms)` and a finite multiplicative aggregation as `prod(a_i for a_i in factors)`.
The corresponding indexed categorical sum or product owns the potentially infinite case.

Within an owned method, route disjoint construction forms with `match` and `case`.
Return immediately for identities, zero objects, empty diagrams, or already-normal forms when those cases apply.
Assert the mathematical hypotheses that remain before entering the general branch.

For example, do not define `equals(x, y)` to return `x == y` or define `Y.contains(X)` to return `X in Y`.
Use the standard syntax directly.

## Tests and performance

| ID | Policy |
| --- | --- |
| `POL-TEST-028` | A row that asserts a fabricated answer asserts the defect. Asserting `x not in X` immediately after establishing that the membership is `Unknown` records the flattening rather than the mathematics; state the proposition and its decision instead. |
| `POL-TEST-029` | Give every test file a basename unique across the whole test tree. Under pytest's default import mode two files sharing a basename collide and the second is never collected, so it reports nothing while appearing to pass. |
| `POL-TEST-030` | Never run a test suite, type checker, linter, formatter, or diagnostic sweep against an incomplete or incorrect architecture, and never chase test, lint, or type-check correctness mid-refactor. It polishes code the refactor will delete, rewards golfing that code until the checks pass, implicitly protects the old code the refactor exists to replace, and can derail the refactor into a sequence of local repairs that keep the checks green. Tests are for regressions and end-to-end behaviour, not internal consistency, unit testing, or locking in current behaviour. A one-off test is fine, and so is adding a test and running it alone while you work, as a feedback signal and never as a correctness signal. Until a 1.0 milestone, checkpoint through `ai-review-ci red-commit`. Until then the arbiter of correctness is agreement with the plans, specifications, and transcripts, established by intelligent adversarial review - dispatch subagents - looking for alignment, contradictions between documents, abstraction leaking across the kernel and leaf boundary, and drift from what was decided. A green suite is evidence of none of those. Grounded in session `353b942d`, 2026-08-28. |
| `POL-TEST-031` | Do not build new automated enforcement before 1.0: no lint rule, `ast-grep` rule, CI gate, hook, or checker added to police a convention. It is `POL-TEST-030`'s gradient error one step earlier - it turns a judgement that belongs to review into a check that can be satisfied, and fixes a convention's current wording into machinery while the architecture that gives the convention its meaning is still moving, after which the machinery decides the architecture. That nothing enforces a rule is not a finding and not a reason to write the enforcement; the absence is the design, and the finding is the breach and its repair. Static projection of the declared architecture - stub generation, the category type-checker plugin - enforces no convention and stays (`D51`). `D132` admits one further kind: a check that names one acceptance line of `specs/system.md` or `specs/resolution.md`, or one R-gate criterion, and fails on a file and line; the admitted set is listed there and runs in `just architecture` at the push tier. Grounded in session `be8d8a9e`, 2026-08-28T15:50Z. |
| `POL-TEST-001` | Read the repository test rules before editing a test file. |
| `POL-TEST-002` | Make every assertion state a mathematical proposition or an essential type invariant. |
| `POL-TEST-003` | Test the intended end-to-end behavior, not implementation layout or past defects. |
| `POL-TEST-004` | Assert the correct category, parent, domain, codomain, images, composition, and mathematical equality as applicable. |
| `POL-TEST-005` | Use the smallest specimen that distinguishes correct behavior from a plausible failure. |
| `POL-TEST-006` | Test object, element, and morphism inheritance by calling inherited public operations through the real category compiler. Route records, compiled-class identities, and caches do not prove that public surface. |
| `POL-TEST-007` | Test universal constructions through their universal morphisms, not only their apex objects. |
| `POL-TEST-008` | Use a real Sage process for Sage behavior. |
| `POL-TEST-009` | Do not add a test that only asserts the absence of a previous mistake. |
| `POL-TEST-010` | Treat a passing test as evidence only for the proposition it executes. |
| `POL-TEST-011` | Give every mathematical expected value an independent oracle: an inspected source, a theorem-derived formula, or an independently verified canonical fixture. |
| `POL-TEST-012` | Cite the exact theorem, section, table, or page that fixes a literature-based test value. |
| `POL-TEST-013` | Inspect the cited source before writing the fixture. Do not reconstruct a citation or expected value from memory. |
| `POL-TEST-014` | Use Sage parity only as a secondary check. Do not make the implementation under test or Sage's matching output its own oracle. |
| `POL-TEST-015` | Never change an expected mathematical fact to match the implementation output. Repair the implementation or establish a better oracle. |
| `POL-TEST-016` | Use a canonical object or a source-defined fixture. Use a matrix fixture only when the source datum is that matrix or the test constructs its semantic realization. |
| `POL-TEST-017` | Use rank, determinant, signature, parity, dimension, and nonemptiness only as guards when the claim under test is stronger. |
| `POL-TEST-018` | Assert isomorphism, classification data, action, semantic kernel, semantic cokernel, or a universal morphism when that is the mathematical claim. |
| `POL-TEST-019` | Test through the public semantic API. Do not assert coordinate arrays, matrix ranks, private hooks, concrete classes, helper calls, or field layout. |
| `POL-TEST-020` | Do not use `is not None`, `len(x) > 0`, `isinstance`, `hasattr`, `getattr`, or `setattr` as the main evidence for a mathematical claim. |
| `POL-TEST-021` | Use exact arithmetic and exact equality for exact mathematical claims. |
| `POL-TEST-022` | Cross-check an ambiguous expected fact through an independent theorem, implementation, or representation. |
| `POL-TEST-023` | Do not use mocks, simulations, skipped tests, or expected failures as evidence for mathematical behavior. |
| `POL-TEST-024` | Test repository-owned behavior. Do not spend assertions re-proving Sage, Python, or a cited theorem in isolation. |
| `POL-TEST-025` | Keep an assertion only if a plausible mathematically wrong implementation can fail it. |
| `POL-TEST-026` | Let a citation establish the oracle. Assert the resulting mathematical fact rather than the citation text or source layout. |
| `POL-TEST-027` | Make each mathematical test failure state the failed proposition and the expected mathematical behavior. A user must not need implementation context to understand the failure. |
| `POL-PERF-001` | Measure performance with wall time as a function of input size. |
| `POL-PERF-002` | Use call counts only to locate repeated work. Do not use them as efficiency evidence. |
| `POL-PERF-003` | Preserve code that displays the mathematical sequence when a faster form hides it. |
| `POL-PERF-004` | Use small mathematical specimens unless the claim concerns a large named object. |
| `POL-PERF-005` | Keep an enumeration-based approximation explicit and outside foundational paths. Log a clear warning before a potentially large enumeration begins. |

Enumerating isotropic subgroups of a torsion bilinear module can be an explicit first approximation.
It remains a replaceable algorithm, not the representation or default structural method.

## Documentation ownership

| ID | Policy |
| --- | --- |
| `POL-DOC-001` | Use `CONTRIBUTING.md` for general contribution principles and recurring patterns. State the general rule first and use concrete cases only as grounding examples. |
| `POL-DOC-002` | Add a specific observed antipattern to `CONTRIBUTING.md` only when its recurrence or severity makes a dedicated indexed warning useful. Keep its governing general principle explicit. |
| `POL-DOC-003` | Make each specification a forward-facing inventory of the desired mathematical capabilities and public API. |
| `POL-DOC-004` | Keep private compiler design in `specs/resolution.md`. Other specifications state the public mathematical consequence and link to that private design only when needed. Keep private computation types and names outside public contracts. Public SymPy proposition types follow `POL-SCOPE-016`. |
| `POL-DOC-005` | Make each category specification declare its complete `structure_functors()` tuple. Use the exact functor retained by its defining construction, or construct it through `Fun(self, Target)`. Each entry is an ordinary functor. The tuple is the compiler input for the immediate edges of the new owned implementation graph and determines inherited structure; it does not describe or modify Sage's `super_categories()` graph. |
| `POL-DOC-006` | State which capabilities the specified category owns. State inherited capabilities by naming their owning category and the functor path that supplies them. |
| `POL-DOC-007` | Keep one authoritative catalogue for each public method surface. Reference that catalogue from dependent specifications instead of copying it. |
| `POL-DOC-008` | Mention a small number of inherited methods only when they clarify a category-specific example. Do not reproduce the inherited API inventory. |
| `POL-DOC-009` | Name only mathematically meaningful immediate functors. Select only the functors that supply inheritance. Obtain deeper inherited capabilities by functor composition, not by adding direct functors for convenience. |
| `POL-DOC-010` | Put a mathematical distinction or formal term in an implementation plan only when it changes a required construction, public API, admissible result, or failure condition. Vocabulary alone creates no implementation decision. |
| `POL-DOC-011` | Classify two statements as contradictory only when they impose requirements that cannot both hold in the same scope and context. An override replaces an earlier rule. A specialization narrows it. An unresolved choice records alternatives. A different presentation is not a contradiction unless it imposes incompatible requirements. |
| `POL-DOC-012` | When reconciling project history, let the latest explicit user decision and its stated context control earlier drafts. Then normalize every current durable owner. Do not use the current documents' conflict as evidence for either side. |
| `POL-DOC-014` | State every mathematical notion in terminology a reader can look up. A colloquial word may not stand as a definition, and a word this repository coins has no prior meaning at all. Give each notion its citable name with an inspected locator, or remove the word. Where a short spelling survives in the API, the specification states the conditions it abbreviates and the short spelling abbreviates nothing else. |
| `POL-DOC-015` | Remove a retired term rather than annotating it. A sentence saying that a notion does not exist, a docstring recording what a name used to mean, or a shorthand kept with a note attached all leave the term in the file for the next reader to find. Git history owns what a thing was called; the artifact owns what it is called. |
| `POL-DOC-016` | Let cited mathematics settle a mathematical question. A definition, a formula, or the correctness of a construction is decided by an inspected source, not by a reviewer's preference, a coordinator's ruling, or the behaviour of the current implementation. Where the sources leave a genuine choice, record the alternatives and the choice; where they do not, follow them. |
| `POL-DOC-017` | A specification states what must hold of the result and what the writer of a leaf supplies. It does not state how the kernel achieves it. A sentence that names a library call and its arguments, an allocation or initialization order, a class-tail composition, a cache location, or a closure fixup is implementation: remove it, and state the obligation it was serving. The test is on the sentence, not on intent. Where an implementation choice is worth recording, record it as prior art to use rather than as a required mechanism. |
| `POL-DOC-018` | Ground every new policy row and every substantive specification edit in the transcripts, and specifically in the user's own words. Agent reasoning, a review finding, a plan, and the existing source are not grounds. Cite the session identifier and the message timestamp, as `4544eba5 2026-08-28T12:00Z`, so a reader can retrieve the statement; sessions live under `~/.claude/projects/-home-dzack-gitclones-sage-categories/` and `~/.codex/sessions/`. Record the decision in `specs/decisions.md`, which holds the provenance, and let the row or specification state the consequence. When no user statement grounds a rule you believe is needed, that absence is the finding: surface it and ask, because writing it anyway is how the coinages and the wrong models entered every previous time. A rule that only records an inspected external definition cites that source's locator instead (`POL-MATH-040`). |
| `POL-DOC-013` | Keep an executing plan limited to active decisions, fixed requirements and exclusions, dependency order, and acceptance conditions. Put completed work, archaeology, revision history, and provenance in a separate record. |
| `POL-DOC-019` | In a leaf specification, link each inherited categorical construction to its generic owner and state only the leaf's mathematical delta. Put the shape, index, diagram, cone or cocone, defining morphisms, universal morphism, and inherited presentation operations in the generic specification once. |
| `POL-DOC-020` | Resolve every mathematical owner, public spelling, input and result category, constructor contract, dependency, exclusion, and acceptance statement before its implementation phase starts. An executing plan states those decisions and the work that makes them true. It never assigns a task to determine, choose, clarify, or correct its own contract or governing policy. If the transcripts do not determine a required decision, ask the user before implementation starts, then update the governing decision, specification, and plan. |
| `POL-DOC-021` | Execute foundational work in strict dependency order. Fully specify, implement, and independently accept the kernel while production leaves remain unchanged. Then implement and independently review one leaf phase. A leaf defect returns to that leaf phase. A generic defect returns to its kernel phase, invalidates every dependent acceptance, and requires those phases to pass again in order. Never implement the kernel and a production leaf in parallel. |
| `POL-DOC-022` | Every architectural repair names the violated invariant, the standard mathematical owner, and the positive replacement. Correct the governing decision and specification first when they are stale. Delete the complete duplicate entity, inspect sibling constructions for the same responsibility, and reject any new metadata source of truth. A rename-only repair is incomplete (D121). |
| `POL-DOC-023` | Keep one canonical document for each contract. Use the ownership table below. Every dependent document links to that owner and states only its local delta (D123). |

| Contract | Canonical document |
| --- | --- |
| Complete system shape, cross-layer ownership, and dependency order | `specs/system.md` |
| `Cat`, `Mor`, `Fun`, functor actions, and structure-functor selection | `specs/functor.md` |
| Leaf, kernel, and computation-engine boundary | `specs/leaves.md` |
| Property categories, inverse images, and same-object refinement | `specs/property-refinement.md` |
| Propositions, typed queries, `ask()`, assumptions, and exact handlers | `specs/undecidable-properties.md` |
| Private Sage compiler and runtime | `specs/resolution.md` |
| Controlling decisions and supersession | `specs/decisions.md` |
| Compact contribution rules | `CONTRIBUTING.md` |
| Agent workflow, authority order, and current scope | `AGENTS.md` |
| Phase delta and acceptance conditions | Agent-memory plan cards |
| Local symbol behavior | Source docstrings |

For example, a lattice specification names and selects its functor to the appropriate formed-module category.
When its ambient category has a selected named functor to `Sets()`, cardinality arrives through the composite path from formed modules through modules and that functor.
It does not list cardinality as a lattice-owned method or add a direct lattice-to-`Sets()` functor.

## Policy maintenance

| ID | Policy |
| --- | --- |
| `POL-INDEX-001` | Give every coding policy exactly one unique identifier. |
| `POL-INDEX-002` | Add an identifier only for a new coding rule, not for an example or restatement. |
| `POL-INDEX-003` | Keep identifiers stable when policy wording improves. |
| `POL-INDEX-004` | Retire an obsolete identifier without assigning it to another policy. |
