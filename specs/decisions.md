# Architectural decisions

This file records the decisions the repository owner stated in working sessions between 2026-08-22 and 2026-08-29, in Claude and Codex transcripts.
Those statements are the source of the architecture.
They were not written down anywhere in the repository, so each rebuild rediscovered them by excavation or, more often, invented a replacement.

Each entry gives the decision and its date.
The topic specifications own the resulting technical statements; this file owns what was decided and when.
When a specification, a policy row, a plan, or a report disagrees with an entry here, this file wins and the other artifact is the defect.

Read this before proposing an architecture.
Do not re-derive a decision from source code: the source was written by the same process these decisions correct.

Cite the session identifier and the message timestamp when adding an entry, as
`4544eba5 2026-08-28T12:00Z`, so a reader can retrieve the statement (`POL-DOC-018`).
Entries below carry dates; the sessions they were read from are listed under
[Sources](#sources).

## Sources

This record was built by reading the user's messages in the Claude and Codex sessions for
this repository between 2026-08-22 and 2026-08-28: 208 messages across 99 session files,
under `~/.claude/projects/-home-dzack-gitclones-sage-categories/` and
`~/.codex/sessions/`. The sessions carrying the most decisions were, in order:

| Session | Messages |
| --- | --- |
| `rollout-2026-08-24T18-54-56-01a03368` | 49 |
| `rollout-2026-08-23T00-58-03-01a02a68` | 24 |
| `b55dc6aa` | 23 |
| `rollout-2026-08-25T13-22-02-01a0375e` | 13 |
| `5df9424f` | 12 |
| `rollout-2026-08-24T03-46-01-01a03028` | 10 |
| `rollout-2026-08-25T00-27-59-01a03499` | 9 |
| `rollout-2026-08-26T12-53-54-01a03c6a` | 8 |
| `1c1a3599` | 8 |
| `ee78124f` | 7 |
| `rollout-2026-08-22T22-55-29-01a029f8` | 7 |

Entries added later should name their own session and timestamp inline rather than
relying on this table.

## Contents

- [Philosophy](#philosophy)

- [System synthesis and work control](#system-synthesis-and-work-control)

- [Purpose and scope](#purpose-and-scope)

- [Structure functors and inheritance](#structure-functors-and-inheritance)

- [Elements](#elements)

- [Predicates, containment, and assumption](#predicates-containment-and-assumption)

- [Cardinality](#cardinality)

- [Universal constructions](#universal-constructions)

- [Diamonds and identity](#diamonds-and-identity)

- [Leaf discipline](#leaf-discipline)

- [Types and style](#types-and-style)

- [What the documents are for](#what-the-documents-are-for)

## Philosophy

The decisions below are consequences.
These are the reasons, and they were the part that never got written down: each rebuild received the rules, could not derive them, and substituted something that looked equivalent.
A rule you cannot derive is a rule you will replace with a synonym.

**Category theory is the DRY mechanism, not decoration.** Sage already computes everything this package computes, so computation is not what is being bought.
What is being bought is that a structure is stated once and reaches everywhere it applies.
Products are defined once and apply to categories, sets, rings, modules, sheaves, and schemes alike.
Inheritance, dispatch, and code reuse are engineering answers to a question mathematics answered better, and a functor is not a pleasant way to describe a relationship — it is the reuse mechanism itself.
So writing engineering wiring is the signal that a mathematical statement was missed, not a sign that mathematics ran out.

**Categorical placement is the index into a catalogue of algorithms.** The product is an easily discoverable and transportable catalogue of algorithms, reached by slotting an object into the correct category.
That is why placement has to be principled: a wrong placement is not a taxonomy error, it is a wrong answer about which algorithms apply to your object.
It is also why a value is constructed into the strongest category its mathematics supports — that is how the right algorithms become reachable.

**A definition determines a complete interface, and an implementation cannot forget part of it.** This is the defect being repaired.
Sage's `IntegralLattice` does not know its underlying set is `ZZ^n`, so `ZZ^n` is not recognised as a product, and Sage can neither count nor iterate it, even though `ZZ` enumerates.
Sage has three free modules with different operations and inconsistent inherited cardinality.
If `X` is a set it has a cardinality — not because an author remembered to write one, but because that is what being a set means.
Inheritance is therefore total and automatic, never opt-in.

**Rigour is a floor, not a mandate to build.** The obligation is to be mathematically principled and never to do anything ill-defined.
It is not to satisfy a self-imposed mathematical programme with new machinery.
Proving things belongs in a language like Lean.
When a design question turns out to be about formalization rather than about a decision the code must make, the answer is to drop the question, not to build the apparatus.
Three successive coherence subsystems were built for a mandate that did not exist.

**Construction is assertion.** Placing a value in a category is how a theorem is stated; the writer is trusted, and a citation on the construction line is what an auditing mathematician reads.
There is no separate certificate, authority token, or proof record, because they would duplicate what the placement already says, and duplicating it invites the two to disagree.

**Information flows from the kernel downstream, never upstream.** A kernel that knows what a poset is — that ensures subsets of a poset are posets, with no mechanism that generalizes — is defective even when it works.
The test is not whether the mechanism produces the right answer for the category in front of you; it is whether the mechanism could have been written without knowing that category exists.

**A justification must survive weakening its hypotheses.** Checking a kernel by testing that a matrix rank is zero is wrong the moment `R` stops being a field, because torsion makes a nonzero module have rank zero.
Hard-tying an implementation to `ZZ` is wrong when the algorithm only needed a PID. An implementation that happens to be correct in its current category is still wrong if its *reason* is specific to that category.
Ask what the argument rests on, not whether the answer comes out right here.

**Never encode a non-finitary concept in a finitary structure.** The components of a natural transformation are an indexed family, not a tuple, because almost every category in use is infinite.
Cardinality is not obtained by enumeration, because the set may be `{2, 4, ...}` or `{1, ..., 10^10}`. The underlying set of `Free_R(S)` exists by a membership rule and a cardinality rule, with nothing to enumerate and nothing to compare.

**Complexity has a direction.** It may accumulate in the kernel, and only in exchange for removing it from every leaf.
A kernel feature that does not shrink a leaf is a net loss, and a leaf carrying wiring is evidence the kernel has not paid for itself.

**Dependency order is part of the architecture.** A production leaf consumes an accepted kernel contract; it does not help design that contract while both are changing.
Parallel kernel and leaf work lets the leaf's immediate needs choose generic mechanisms and hides missing kernel ownership inside leaf code.
Complete and independently accept the kernel first, then implement and independently review one leaf phase at a time.
A generic defect found later invalidates every dependent acceptance and returns work to the kernel owner.

**An execution plan contains decisions.** It cannot assign implementation work whose first task is to decide its mathematical owner, public spelling, result category, constructor contract, or acceptance criterion.
Resolve each such question in the governing decision and specification before the phase starts.
When the transcripts do not determine the answer, ask the user before implementation begins.

**The mathematics is the interface; the presentation must not leak.** A group is technically `(X, f)` and a lattice is technically `(L, b)`, but nobody works with them as ordered pairs.
Publicly a lattice *is* a module with more structure.
An ordered pair is a fine private representation and an unacceptable public one, which is why every `underlying_Y()` deserves suspicion: it is a presentation escaping into the API.

**Depth in the graph bounds vocabulary.** A leaf mentioning cardinality in a lattice subtree is a red flag, not because of layering discipline but because cardinality is not part of what a lattice is.
Vocabulary that leaks across the graph is a mathematical error before it is a structural one.

**The kernel is a black box, and no mathematician ever audits it.** The split is between a mathematical declaration and the wiring that realizes it, never between general and specific mathematics.
`Cat`, `Mor(n, C)`, `Fun(C, D)`, the property subcategories, and `Sets()` are all objects this repository defines, and all of them are read as mathematics.
The kernel is what takes those plain declarations and performs the Python wiring behind them: class building, linearization, private runtime state sharing, caches, descriptors, and refinement mechanics.
That is what nobody reads.

So the kernel exists to give a leaf writer an interface that reads and writes like standard mathematics.
It should adhere to precise mathematics where it can, but that is an aid and never its acceptance criterion.
Holding it to the theory layer's standard is what produced universes, straightening machinery, and three coherence subsystems, each built to exhibit category theory to a reader who was never going to look.
Ordinary Python lives there, engine boundaries are quarantined in their own subtrees, and the layout tells a reader where mathematics stops.

**The user should not need to know the framework.** Nobody writes `FiniteSet({1, 2, 3})`; `Sets({1, 2, 3})` routes.
A small number of high-level endpoints are the interface, and discoverability comes from names mathematicians already know.
The code exists to reduce cognitive load, so requiring knowledge of the category graph in order to use it defeats the purpose.

**Prior art before invention, and mathematical structure is itself prior art.** Sage already supports semirings and posets, so cardinals are built on them rather than hand-rolled.
Any Python, Sage, SymPy, GAP, Singular, Macaulay2, Julia, or published package is available inside an implementation.
Before encoding something, look for the structure that already encodes it and for other systems that have solved it.

**A finding is an instance of a principle.** When a violation is identified, the violation is not the finding — the principle it instantiates is, and that principle is the reason the instance is wrong.
Fixing the instance alone leaves every sibling in place and teaches nothing.

**A local repair on a wrong architecture is negative progress.** Polishing the wrong structure removes the pressure that would have forced the real fix while leaving the structure in place, so the result is worse than having done nothing.
The same holds for deleting a test that senses a defect: repair what it senses, and the test becomes unformulable on its own.

## System synthesis and work control

**D124 (08-31, corrected 08-31, `01a05682-23ba-7171-bee9-5755d4c313a4` 2026-08-31T12:04:57Z). The project is one mathematical tower over one runtime substrate.** The active tower runs from `Cat`, morphisms, and functors through foundational properties, universal constructions, pullback-defined property closure, sets, order, algebraic families, modules, and algebras. The runtime substrate compiles and evaluates that mathematics. It is not a second mathematical layer. Every fact has one mathematical owner. Every runtime mechanism serves that owner. [`system.md`](system.md) owns the complete composition, dependency directions, standard execution traces, and smallest task-specific context packets.

**D125 (08-31, `01a05682-23ba-7171-bee9-5755d4c313a4` 2026-08-31T12:04:57Z). Public propositions use SymPy's proposition system.** A category, property category, or equality operation owns the mathematical predicate. Its public representation is a SymPy `Predicate` subclass. Application returns a SymPy applied predicate or Boolean expression. SymPy owns Boolean composition, `global_assumptions`, exact proposition handlers, and evaluation through `sympy.ask()`. The public `ask()` maps an undecided SymPy result to Sage `Unknown`. A positive exact property result refines the same owned value. Private identity atoms can represent owned values inside the public expression. Typed value queries remain repository-owned and never enter SymPy Boolean algebra.

**D126 (08-31, corrected 08-31, `01a05682-23ba-7171-bee9-5755d4c313a4` 2026-08-31T12:04:57Z). The foundation uses a staged bootstrap.** The categorical core completes first. Minimal `Sets()` then exists without cardinality integration. The generic internal algebraic-object schema enters with `Cardinal()` as its first executable consumer in `Semirings(Cat())`. `Ordinals()`, `Cardinal()`, and their order categories complete in that phase. Cardinality and cardinal property categories then attach to `Sets()`. The specified set constructions, ordered sets, general algebraic families, modules, and algebras follow in that order. This sequence cuts the implementation cycle without changing the mathematical dependencies.

**D127 (08-31, `01a05682-23ba-7171-bee9-5755d4c313a4` 2026-08-31T12:04:57Z). Agent work is an exact contract over canonical state.** A work unit states its assigned objective, mathematical owner, active phase and direct prerequisites, complete consumer boundary, and acceptance at an exact revision. Delegation passes that complete contract without substitution. Review compares the result with the same contract. A local patch with the wrong owner is discarded. Agents continue from canonical specifications, the active plan DAG, and the current working tree. Reports, handoffs, diagnostic counts, and prior verdicts are not execution state.

**D128 (08-31, `01a05682-23ba-7171-bee9-5755d4c313a4` 2026-08-31T12:04:57Z). Object placement is direct.** For `X` to carry the object surface of `D`, construct or refine `X` as an object of `D`. `Cat().Point(X)` remains the one-object category on `X`. A functor `Cat().Point(X) -> D` records that one-object diagram. It does not perform object placement or supply implementation inheritance. It is an isofibration only when its literal image is replete and every isomorphism at `X` lifts.

**D129 (08-31, `01a05682-23ba-7171-bee9-5755d4c313a4` 2026-08-31T12:04:57Z). A public mechanism enters with its first mathematical consumer.** A specification can fix a contract before execution. Runtime classes, dispatch, adapters, and fixtures enter only when a real category, functor, property, query, or universal construction consumes them. An acceptance witness uses an existing mathematical object from the active layer. It does not create a placeholder leaf or an artificial property solely to exercise infrastructure.

**D130 (09-01, `637ffa35-b7cb-4c5b-ba49-5453caf84f19` 2026-09-01T13:12:12.391+08:00). Static projection preserves category-owned associated types without a structural bridge.** A category's `ObjectType`, `ElementType`, and `MorphismType` are its exact static associated types. A functor preserves its domain and codomain object and morphism types in both ordinary actions. `Mor(C)(A, B)` preserves `C`'s morphism type and the exact endpoints. A positive property result refines the same owned value to the compiler-generated nominal intersection of its ambient and property surfaces. `typing.Protocol`, `TypeIs`, wrappers, casts, and false explicit runtime inheritance are not static substitutes for these declarations. The compiler projector is the only mechanism that emits `.pyi` artifacts from this model; no hand-maintained type graph is authoritative. This records the user's phase-3 correction and controls `POL-TYPE-018`, `POL-TYPE-020`, `POL-TYPE-025`, and `POL-TYPE-027`.

## Purpose and scope

**D01 (08-22, clarified 08-30, `2026-08-30-cce86657` 2026-08-30T18:13Z). Build the whole foundation before any structured category.** `Cat`, all arrow categories, working inheritance through `ObjectType` and the other implementation classes, and then an extensive owned `Sets()` implemented as a leaf when that migration reaches it. The repository's `Cat()` defines an entirely new category graph; it is not a refinement, fork, or partial reuse of Sage's mathematical category graph. The two systems meet only in the private Python runtime substrate ultimately rooted in Sage `Parent` machinery and in the Sage class-building facilities selected under D109 through D114. No Sage category or categorical construction enters the owned mathematical graph or public API. Categories are migrated as needed by defining new owned categories and their owned functors.
Do not drift into rings, modules, lattices, or formed modules.

**D02 (08-23). The package shadows a subset of Sage, and its universe is closed.** `sage_categories.all` works like `sage.all`. Once you touch a package-owned object, every further computation stays inside the package: every operation is mediated by the package's categorical API, and every result you can produce is still a package object.
There is no intention to refine Sage objects into this hierarchy or to be compatible with base Sage; any compatibility is incidental.
Base Sage appears only inside hidden implementation engines.
When the package wants a Sage construction, it absorbs it as an internal engine and re-expresses it through the categorical machinery.

The reason is uniformity of interface.
Sage's implementations forget things.
Sage's `IntegralLattice` does not know its underlying set is `ZZ^n`, so `ZZ^n` is not recognised as a product of sets, rings, or rank-one modules, and Sage cannot say its cardinality or iterate it — while research code wants to enumerate infinite countable sets in bounded loops, as Vinberg's algorithm does.

**D03 (08-23, clarified 08-29, `01a04c1c-b22b-7f70-8351-6e12ca028470` 2026-08-29T08:08Z, 2026-08-29T08:42Z). Computation is not the goal.** Sage already computes everything this package computes.
The goals are uniformity, categorically principled code, category theory as a form of DRY, real functors everywhere, and obviating engineering concerns so that a leaf developer thinks about mathematics.
It is an organisational, more legible layer over Sage.
Sage code needs a programmer to audit it; code here, outside the kernel, should be auditable by a mathematician with very little coding experience.
For `M = ZZ^3`, the public result is one free module with the complete interface forced by its mathematics.
Its structural route to `Sets()` supplies cardinality and countability.
Its retained finite-product presentation and the chosen enumerations of its factors supply product enumeration.
These consequences do not depend on which private Sage free-module class performs a computation.

**D04 (08-23). The long-term asymptote.** Adding a category such as `MyVerySpecialAlgebraOverANoetherianDomain(R)` should mean: define a leaf category, possibly from a shipped template; declare a few functors to nearby categories you already understand, without reading the rest of the codebase; write your new methods; and receive the full inherited surface.
You think at the level of your own algebra, and `cardinality()` and suitable limits and colimits arrive because of the functorial wiring.

## Structure functors and inheritance

**D05 (08-23, corrected 08-29). A leaf never writes subclass relations between category-owned classes.** The category specifies `C.ObjectType`, `C.ElementType`, and `C.MorphismType` and returns its immediate structure functors.
The kernel constructs those exact classes dynamically with the corresponding target classes as bases.
Thus a product-set leaf does not write `class ProductSetObject(SetObject)`, but its compiled `C.ObjectType` does inherit the target `Sets().ObjectType` through the declared structure functor.
This Python inheritance is the intended mechanism. It does not assert categorical containment.
The same rule applies to limits, colimits, products, coproducts, tensor products, direct sums, subobjects, and covering objects (`01a048f6-e3f5-7e42-be2a-1f60f70ac23e` 2026-08-28T21:03Z; 2026-08-28T21:06Z).

**D06 (08-24, clarified 08-30, `2026-08-30-cce86657` 2026-08-30T18:13Z). Sage's `super_categories` conflates distinct notions.** It carries subcategory inclusions, full or not, and structure projections such as `(X, op) |-> X` where Sage declares `Sets` a supercategory. The new owned graph instead declares explicit `structure_functors: list[Functor]` and names the distinct mathematics separately: subcategory inclusion, full subcategory inclusion, projection, and so on. This is a new graph using a more explicit declaration model, not a replacement of live edges in Sage's category graph. A migrated Sage concept is reconstructed as an owned category with the functors required by its mathematics.

**D07 (08-24, corrected 08-29). Selection does not include every functor out of the category.** The structure functors are the ordinary functors whose target classes supply inherited implementation.
For a poset `(X, R)`, the projection to `X` supplies the set interface. The projection to `R` does not supply the public poset interface.
The Python inheritance from `Sets().ObjectType` does not make the poset an object of `Sets()` and does not identify it with the separate public set image of the projection (`01a048f6-e3f5-7e42-be2a-1f60f70ac23e` 2026-08-28T21:20Z).

**D08 (08-24, corrected 08-29, `01a04c1c-b22b-7f70-8351-6e12ca028470` 2026-08-29T09:15Z). A functor's two actions are complete executable constructions.** Every `F: C -> D` defines `on_object` and `on_morphism`. For `X in C`, `F.on_object(X)` is ordinary Python code that calls a public constructor of `D` and returns the resulting object of `D`. For `f: X -> Y`, `F.on_morphism(f)` calls a public constructor of `Mor(D)(F(X), F(Y))` and returns the resulting morphism of `D`. These two actions are the complete functor definition and the complete writer input. Returning `F` from `C.structure_functors()` only selects this already-complete ordinary functor for compiled inheritance.

**D09 (08-25, corrected 08-30). Name the exact functor.** Categories such as magmas are pullbacks whose objects are pairs, so their distinct projections carry distinct mathematics.
For lattices `(L, b)`, the projections to `L` and to `b` have equal standing.
For `Modules(R)`, the defining datum `R -> End(X)` does not select one unnamed map to another category.
Use the exact projection, inclusion, source, target, adjoint, or composite and state both endpoints.

**D10 (08-25). The kernel implements the standard functors.** `FullSubcategoryInclusionFunctor`, `ProductProjectionFunctor(i)`, and their relatives are kernel-owned precisely so that leaves need no boilerplate.
A leaf writing a page of functor code is a kernel defect.

**D11 (08-25, superseded in spelling by D55). Every leaf constructs its functors explicitly.** Not `self.inclusion(D)`. A leaf constructs `Fun(self, D).inclusion()`, or `Fun(self, D).Full().inclusion()`, so that a known theorem appears as part of the construction of the functor.
Nothing is computed; the leaf writer is trusted.
Several equivalent spellings of the functor category remain valid; `Fun` is an additional name, not the sole one.
The `Ar` and `Hom` spellings used on 08-25 were dropped on 08-26; see D55.

**D12 (08-26, corrected 08-29). A structure functor is an ordinary functor selected for compiler use.** Leaves construct ordinary functors and return the applicable ones from `structure_functors()`. This contextual name does not define another functor class or constructor, and selection does not assert a subcategory relation.

**D13 (08-26, corrected 08-31, `01a04c1c-b22b-7f70-8351-6e12ca028470` 2026-08-29T08:08Z, 2026-08-29T08:42Z, 2026-08-29T09:15Z; `2026-08-30-cce86657` 2026-08-30T18:13Z; `01a05682-23ba-7171-bee9-5755d4c313a4` 2026-08-31T12:04:57Z). The kernel is Sage class-building over a private mirror of the owned implementation graph, plus private runtime state sharing.** Sage's dynamic-class and controlled-C3 machinery works for building the implementation classes. The private Sage runtime categories are generated from the owned `structure_functors()` declarations and are unrelated to Sage's mathematical category graph except for their shared low-level `Parent`/Python ancestry. The compiler makes each applicable target implementation state available on the source instance, initializes each reached implementation class once, and exposes inherited methods as ordinary Python inheritance. A leaf constructor never accumulates a field for every ancestor category. An inherited method runs on the structured source object and reads the initialized target state there; it does not forward through a separate public underlying object. The kernel treats functor bodies as opaque executable actions. In particular, the public `F.on_object(X)` and `F.on_morphism(f)` contracts apply to already-constructed source values and are not constructor-time callbacks on partially initialized sources. The compiler must satisfy the state-sharing obligation without weakening that ordinary functor contract or adding a second leaf-authored transport declaration. Diamonds follow D37.

**D123 (08-30, corrected 08-30, `01a04e73-53f5-7280-8e1f-48e3a96c204f` 2026-08-30T00:56Z; `2026-08-30-cce86657` 2026-08-30T17:52Z). The two ordinary functor actions are the sole functor declaration.** `F.on_object(X)` constructs and returns the public image in `F.codomain()`. `F.on_morphism(f)` constructs and returns the public image in the exact target hom category. Their inputs are completed values of the stated source category; selecting `F` does not broaden either action to partially initialized construction state. A leaf supplies only these two actions. Selecting `F` in `structure_functors()` selects the applicable target implementation classes. The kernel treats both actions as opaque and can keep private ephemeral records for Python execution only, but no such record can turn a public functor action into a second constructor-time transport program. Such records carry no mathematical meaning, require no leaf-authored counterpart, and decide neither functor semantics nor category placement. This decision controls D08, D13, D17, D95, D110, D118, and every policy, specification, template, plan, or docstring that can be read as requiring another leaf-authored account of either action.

**D14 (08-26, corrected 08-29). One chain per mathematical kind.** Every category is a `Cat().ObjectType`. Every object of a category is a point `* -> C`, hence a `Cat().ElementType` and a `C.ObjectType`. `C.ElementType` is the category-owned implementation and public interface shared by the elements of objects of `C`. When an object `X` is regarded as a category, its elements are the points `* -> X`, with `*` the terminal category. A morphism of `C` is a `Mor(C).ObjectType` (`01a04c1c-b22b-7f70-8351-6e12ca028470` 2026-08-29T06:11Z).

**D55 (08-26, corrected 08-29). Use one public morphism-category spelling.** Define `Mor(n, C)` as the repository's recursive total category of `n`-morphisms of `C`. Almost every category here is a 1-category, so `Mor(0, C) = C` with `C.ObjectType`, and `Mor(1, C) = Mor(C)` with `C.MorphismType`. Hence categories are `Mor(0, Cat)`, functors are `Mor(1, Cat)`, and natural transformations are `Mor(2, Cat) = Mor(1, Fun)`. `Mor(C)` is always a category: its objects are the 1-morphisms of `C` and its morphisms are the 2-morphisms. The public API uses `Mor(C)(A, B)` for the fixed-endpoint hom category. Mathematical prose can use standard `Hom_C(A, B)` notation (`01a04c1c-b22b-7f70-8351-6e12ca028470` 2026-08-29T06:02Z, 2026-08-29T08:20Z).
This supersedes the `Ar`/`Hom` spellings of D11.

**D56 (08-26). Eager, and fail fast and loudly.** Declaration order in `structure_functors()` controls preference.

**D58 (08-27, corrected 08-29). What a functor is for.** In Sage you declare your supercategories but never say *how* to construct an object or morphism of a supercategory from one of yours.
An ordinary functor supplies that missing mathematics through its complete executable actions.
The writer knows the source API and the exact target category.
`on_object(X)` calls an ordinary public target constructor and returns the resulting target object.
`on_morphism(f)` does the same in the target hom category.
The kernel does not inspect either function or request a second account of the construction.
For a module built from `rho: R -> End_Set(X)`, the selected functor to `Sets()` literally constructs the associated set from the module API (`01a04c1c-b22b-7f70-8351-6e12ca028470` 2026-08-29T09:15Z).

**D59 (08-26, corrected 08-30). Morphism properties, not arrow properties.** `Mor(C).Monomorphisms()` and its relatives.
For `C = Cat`, use property subcategories such as `Mor(Cat()).Full()` and `Mor(Cat()).Faithful()` on the exact named functor.

**D60 (08-26). A natural transformation's components are an indexed family.** Almost every category in use is infinite, so a tuple of components is absurd.
Model it as an assignment `X |-> eta_X`.

**D61 (08-27). Name the functor property that licenses common-ancestor tracing, and cite it.** There is a property `P` of functors along which tracing a common ancestor is allowed, and it must be the well-known citable one, not a heuristic recorded after the fact.
"Embedding" is colloquial with no formalized definition.
"Subcategory" is colloquial too: if the intended notion is a monomorphism, say so.
"Inclusion functor" is not a term.
Record the precise citable definitions and the decisions that follow from them.

## Elements

**D15 (08-23). "Shared elements" is not a concept.** Every category has an `ElementType`, including a dynamically constructed one such as `C.Products()`. Element classes inherit exactly as object classes do, and may add methods: the element type of a product is also an element of a set and may carry `x.factors()`. An element of a finite set is not "just an element of a set" — it is `FiniteSets().ElementType`, which extends `Sets().ElementType` when the wiring is correct.

**D16 (08-26, corrected 08-29). What `ElementType` implements.** A Sage element is implicitly a pair `(X, x)` with `X = x.parent()`. `C.ElementType` is the shared implementation and API for the elements of objects of `C`, as Sage category element methods are shared across the elements of their parents. The categorical point of a category `X` is a functor `* -> X` from the terminal category. A morphism `T -> X` with general domain is a generalized element and stays in its functor or slice category. For `C in Cat()`, points `* -> C` are the actual objects of `C`, so `C.ObjectType` inherits `Cat().ElementType`. Sets are read as discrete, hence 0-truncated, categories when this point model is applied (`01a04c1c-b22b-7f70-8351-6e12ca028470` 2026-08-29T06:11Z).

**D17 (08-26, corrected 08-29). Point transport uses composition at the point's categorical level.** For `x: * -> X` and a functor `G: X -> Y`, the image point is the composite `G after x: * -> Y`. A functor `F: C -> D` between ambient categories has a different domain and supplies no such composite (`01a04c1c-b22b-7f70-8351-6e12ca028470` 2026-08-29T06:11Z). Compiled `ElementType` inheritance is a compiler consequence of selecting `F`. It adds no third functor action and requires no additional declaration from the functor writer.

**D62 (08-27, corrected 08-29). Points and generalized elements are distinct.** A point of a category `X` is `p: * -> X`. A generalized element is `p: T -> X`. For `X = C in Cat()`, a point `* -> C` is an actual object of `C`, while a functor `T -> C` is a generalized element.

## Predicates, containment, and assumption

**D18 (08-22, corrected 08-29). There is no decidability boundary.** Every mathematical truth question returns an applied proposition. Every other mathematical query that is not total and exact on its full declared domain returns an applied query with an exact result category. Only `ask()` returns `True`, `False`, an owned result, or Sage `Unknown`. Predicates are proposition-valued; cardinality and cofinality are invariants, not predicates (`01a048f6-e3f5-7e42-be2a-1f60f70ac23e` 2026-08-28T17:24Z, 2026-08-28T17:25Z; `01a04c1c-b22b-7f70-8351-6e12ca028470` 2026-08-29T06:02Z).

**D19 (08-22, corrected 08-29). Category containment and the public predicate application ask one proposition.** The kernel derives `X.is_finite()` from the property declaration owned by `Sets().Finite()`. It returns that category's containment proposition. `ask(X.is_finite())` evaluates it. Python containment asks the same proposition and is only a forced two-valued admission boundary (`4544eba5` 2026-08-28T12:00Z; `01a048f6-e3f5-7e42-be2a-1f60f70ac23e` 2026-08-28T19:51Z).

**D20 (08-24). Every propositional method returns a proposition.** Never a bool, never an `Unknown` in its place.
Anything that would need `Unknown` routes through `assume`/`ask`/`.assume()`. Containment in a category is always a possibly compound proposition, declared once as part of the category's definition — the kernel wires `FiniteSets` to be reachable as `Sets().Finite()` and lets it declare a membership proposition, and `__contains__` follows from that.

**D21 (08-24, corrected 08-31, `01a05682-23ba-7171-bee9-5755d4c313a4` 2026-08-31T12:04:57Z). Construct into the strongest subcategory you can.** A named construction can return its result through the strongest property-subcategory constructor that its mathematics establishes.
The public predicate remains proposition-valued and keeps its one category-owned definition (`4544eba5 2026-08-28T12:00Z`).
Place an individual named object directly in every category its construction establishes. `QQ` is an object of the applicable countable-set, poset, and field categories. `Cat().Point(QQ)` is a separate one-object diagram category.
`Fields().Countable().PartiallyOrdered()` should be nearly automatic, with Sage's `with_axiom` as the model: if any category defines a property subcategory, any subcategory can narrow itself the same way.
Defining `FF_p` and its category placements must never require proving finiteness by enumeration.

**D22 (08-24, corrected 08-28). Assumption is a shortcut for construction.** `assume(X.is_finite())` and `assume(f.is_injective())` refine into the corresponding property category.
Python containment asks the same proposition and returns its Boolean decision, so it is not the proposition passed to `assume()` (`4544eba5 2026-08-28T12:00Z`).

**D23 (08-24, corrected 08-29). Property refinement strengthens the category of the same value.** It is not transport into a second implementation, and it is not a family of admission APIs.
Direct property construction, global assumption, exact computation, and construction-owned mathematics use the kernel's same-object refinement mechanism.
These APIs must not exist: `monos.checked(...)`, `monos.from_hypothesis(...)`, `monos.from_theorem(...)`, `construct(..., check=True)`. A property category can still provide every constructor required by its supported mathematical and engine representations (`01a048f6-e3f5-7e42-be2a-1f60f70ac23e` 2026-08-28T20:21Z).

**D24 (08-24, corrected 08-31, `01a05682-23ba-7171-bee9-5755d4c313a4` 2026-08-31T12:04:57Z). Backend code does not call `assume()`.** SymPy `global_assumptions` owns the proposition context, and a notebook user can write into it.
Internal code already knows the category in which to construct its result, and constructs there.

**D25 (08-24, 08-25). Theorem-backed construction is declaration, not computation.** No Python code can establish that `RR` is uncountable, and running a monotonicity check on `n |-> n^2 : NN -> NN`, or a totality check on `{1, ..., 10^10}` with its natural order, is absurd.
A specific named constructor owns its theorem, and its controlled input data is what makes the theorem applicable: `square_morphism_on_naturals()`, `componentwise_product_order(diagram)`, `finite_total_order_from_enumeration(enumeration)`. A generic `from_theorem(value, owner)` remains invalid, because a registered owner is an opaque token that identifies no construction.
A public total-order constructor accepting an arbitrary relation is likewise invalid; a constructor from an enumeration builds the guaranteed-total relation itself.

**D26 (08-25). The repository never proves or certifies category theory.** That is hopeless in Sage and belongs in a language like Lean.
The categorical core is meant to be independently auditable by mathematicians, so it encodes its needs in standard category or homotopy theory — nLab, the Stacks Project, Kerodon, textbooks, arXiv papers — and stays mathematically legible.
A code writer forms constructions into the correct subcategory as the way of asserting a theorem, with a citation on the construction line.

**D63 (08-26). `__eq__` returns a predicate.** So `a == b` can evaluate to `Unknown`, and that is fine.
Where a Boolean is forced, repository code writes `decision = ask(x == y); assert decision is not Unknown`. Points are chosen data `x: * -> X`.

## Cardinality

**D27 (08-22). Never enumerate a set to compute a property.** Always consider what happens for `{2, 4, ...}` or `{1, ..., 10^10}`. Enumeration is a dead-last fallback for when cardinality is required, the set is known finite, and there is no other way.
Usually cardinality is supplied at construction or derived from a known relationship: `{n in NN | n <= 100}` is finite without listing anything.
Enumeration can be a fine first approximation in a specific algorithm, but it does not belong on a main path and should warn loudly.

**D28 (08-22, 08-23). Cardinals compare by ordinary syntax.** `==`, `<=`, and the rest, against ordinary integers.
You never extract a cardinal's "value".

**D29 (08-24, amended by D62). `cardinality()` never uses absence for unknown mathematics.** Representing an undecided cardinality by `None` is a defect.
An image receives the domain's cardinality only when the map is established injective; a constant function is the counterexample.

**D30 (08-25). Cardinal arithmetic is the categorical operation.** The coproduct in the category of cardinals is exactly cardinal addition; the product is exactly cardinal multiplication.

**D64 (08-26, corrected 08-29). There is no unresolved cardinal object.** `X.cardinality()` returns an applied query with result category `Cardinal()`. `ask(X.cardinality())` returns an owned cardinal when an exact route applies and Sage `Unknown` otherwise. The same architecture applies to every mathematical query that is not total and exact on its full declared domain. Cardinals contain no separate unresolved value (`01a048f6-e3f5-7e42-be2a-1f60f70ac23e` 2026-08-28T17:24Z, 2026-08-28T17:25Z; `01a04c1c-b22b-7f70-8351-6e12ca028470` 2026-08-29T06:02Z).
This amends D29.

**D65 (08-27). Cardinals are a semiring with a poset structure.** The poset records that `2 ** aleph_0`, and most cardinal exponentials, are incomparable to `aleph_i` in ZFC. There are two totally ordered infinite sets of formal symbols, `{0, 1, ...}` and `{aleph_0, aleph_1, ...}`, and the algebra must take arbitrary sums, products, and formal exponentials of them.

Do not hand-roll that algebra.
Build on Sage, which already supports semirings and posets: one semiring for the finite part, one for the aleph part, and a new one that delegates to both for the pure cases, states the mixed cases, and defines the exponential — extending Sage's semiring and poset classes, or at minimum composing them and declaring itself into Sage's categories.
When you define a semiring you *define* its operations, so an idempotent `x + x = x` is a definition and not a defect.
Look for prior art before inventing an encoding.

**D66 (08-27). Sets of the same cardinality are never identified; cardinals of the same value always are.** `[2] * [3]` is not `[6]` in `Sets()`: the left side is a set of ordered pairs.
Identifying `{1, 2, 3}` with `{a, b, c}` would render a computer algebra system useless.
In `Cardinal()`, by contrast, `c_2 * c_3` *is* `c_6`, because a skeletal category that is a semiring object has a multiplication `C * C -> C` along which products collapse.
A cardinal may still be *represented* as a product, as `aleph_0 ** 2` may be represented by the pair, but finite with finite, finite with infinite, and infinite with infinite all collapse.

## Universal constructions

**D31 (08-23). Define each construction at the most general level that supports it.** `Modules(R).Products()` should exist because any `C in Cat` can form `C.Products()`, the way `with_axiom` works — not through leaf boilerplate.
If the category is not complete the subcategory may be empty, which is fine and not something the code proves.
`Modules(R)` may be where `TensorProducts()` and `DirectSums()` first appear, and then `Lattices(R)` forms `Lattices(R).TensorProducts()` by stating only its delta: `⊗_i (L_i, b_i) := (⊗_i L_i, ⊗_i b_i)`, since module homs are themselves modules and the tensor product there is already handled at the module level.

**D32 (08-23). A constructed object presents as an ordinary object with more methods.** A product set truly *is* a set; it carries additional methods for its factors, universal morphisms, and so on.
Redefining `cardinality()` on a product is the red flag.
Either the family knows `(prod X_i).cardinality() = prod X_i.cardinality()`, or the functor knows how to build the underlying set, which knows its own cardinality like any set.

The same holds for `R`-lattices: `L = (M, b)` projects to `M`, so a lattice truly *is* a module with new methods.
Which functors count for inheritance is decided case by case by what is standard to mathematicians.
One does not think of a lattice *as* a bilinear form, so `L.bilinear_form()` is public while `b`'s methods are not grafted on; but neither should a lattice be treated as an ordered pair in public, with `L.underlying_module()` indirection.
Any `underlying_Y()` method deserves scrutiny: a lattice does not "have" an underlying module, it *is* a module with extra structure, just as a group `G = (X, f)` is not handled as an ordered pair in daily use.
Ordered pairs are fine as private representations.

**D33 (08-24). A poset product just is the set product with an order on it.** It needs to do nothing to construct its projections or its mediating morphisms.

**D34 (08-25, corrected 08-30, `01a048f6-e3f5-7e42-be2a-1f60f70ac23e` 2026-08-28T18:48Z; `01a04c1c-b22b-7f70-8351-6e12ca028470` 2026-08-29T06:02Z, 2026-08-29T06:11Z, 2026-08-29T08:20Z; `01a04e73-53f5-7280-8e1f-48e3a96c204f` 2026-08-30T00:56Z). The `Cat` level owns the construction vocabulary.** It supplies `C.Subobjects(X)`, `C.Superobjects(X)`, `C.CoveringObjects(X)`, and `C.CoveredObjects(X)` for every `X in C`, together with `C.Products()`, `C.Coproducts()`, `C.Limits(I)`, and `C.Colimits(I)`. The fixed-object categories are the applicable monomorphism and epimorphism subcategories of slices and coslices. `C.Products()` is the interface subcategory on objects in the full images of the chosen nontrivial product functors `Prod_J: C^J -> C`; `C.Coproducts()` is dual. The construction retains the diagram and the selected universal presentation. For a product category `P`, an object of `Cat().Subobjects(P)` answers `product_projection(i)`. Slice and coslice categories and their fibrations to the varying object supply the fixed-object constructions.
General projections exist for any subcategory of a product category, `proj_i: (X_1, ..., X_n) |-> X_i`; a coslice has projections to both `X in C` and its defining morphism in `Mor(C)`, and composing with the source and target projections gives the rest.

**D101 (08-29, `01a04c1c-b22b-7f70-8351-6e12ca028470` 2026-08-29T06:39Z). Base change of a subcategory is a first-class categorical construction.** For `F: D -> C` and a subcategory monomorphism `i: P -> C`, the inverse-image subcategory is the pullback `F.inverse_image(P) = D ×_C P`. It retains the pullback projections, including its monomorphism into `D`. A property category on `D` obtained from a property category on `C` is this inverse image along the named functor that defines the inherited property. The axiom and class compiler expose the resulting category and its implementation classes.

**D102 (08-29, `01a04c1c-b22b-7f70-8351-6e12ca028470` 2026-08-29T06:39Z). Opposite categories and dualization are foundational.** The dualizing functor `Op: Cat() -> Cat()` acts on categories and functors, and dualization sends natural transformations to natural transformations with reversed direction. It retains the natural isomorphism `Op compose Op ≅ Id`. The public operations are `C.op()`, `F.op()`, and `eta.op()`. Dual constructions are obtained through this functorial operation. The limit-side owners are terminal objects, products, limits, slices, monomorphisms, fibrations, and right Kan extensions. Initial objects, coproducts, colimits, coslices, epimorphisms, opfibrations, and left Kan extensions are their duals. Each pair has one foundation.

**D103 (08-29, corrected 08-31, `01a04c1c-b22b-7f70-8351-6e12ca028470` 2026-08-29T07:02Z; `01a05682-23ba-7171-bee9-5755d4c313a4` 2026-08-31T12:04:57Z). The generic core supplies a thin functorial calculus in mathematical dependency order.** Its four strata are functor-category calculus, category constructions, universal and functorial structure, and indexed and representational structure. The strata add standard categories, functors, natural transformations, and properties. They do not form a second framework beside `Cat`, `Fun`, pullbacks, and the method compiler.

**D104 (08-29, `01a04c1c-b22b-7f70-8351-6e12ca028470` 2026-08-29T07:02Z). Composition, evaluation, and base change are first-class functorial constructions.** Composition and evaluation are functors between functor and product categories. Their morphism actions supply whiskering and horizontal composition. Pullbacks supply intersections of subcategories, restriction of a functor to subcategories, induced functors between pullbacks, fibers of functors, and change of base. A leaf states the theorem that its functor lands in a named subcategory. The generic restriction or pullback construction then owns the resulting functor.

**D105 (08-29, `01a04c1c-b22b-7f70-8351-6e12ca028470` 2026-08-29T07:02Z). Comma categories and the three image constructions are public mathematical language.** A comma category retains its two projections and defining natural transformation; slices and coslices are its fixed-object cases. For `F: C -> D`, distinguish the strict image, the full subcategory spanned by the literal object image, and the essential image. The essential image is the replete closure and retains the standard essentially-surjective/fully-faithful factorization.

**D106 (08-29, `01a04c1c-b22b-7f70-8351-6e12ca028470` 2026-08-29T07:02Z). Existence properties and selected universal data have different owners.** `Adjunctions(F, G)`, `Equivalences(C, D)`, `Cones(D)`, `LimitCones(D)`, and `Representations(F)` are categories of selected mathematical data. Their inhabitation states existence; selecting an object supplies data needed for computation. A universal presentation is separate from its diagram and its apex. The total category of limiting cones has a diagram projection and an apex functor. The fiber of the apex functor over `X` is the category of limiting presentations with apex `X`.

**D107 (08-29, `01a04c1c-b22b-7f70-8351-6e12ca028470` 2026-08-29T07:02Z). Functor properties state preservation and creation of universal constructions.** `PreservesLimits(I)` and `CreatesLimits(I)` are shape-indexed property subcategories of functors; their colimit forms are derived by duality. Chosen limits give `Lim_I` right adjoint to the diagonal functor, and chosen colimits give its dual left adjoint. A leaf that creates a limit states that theorem on its named structure functor. The generic construction then supplies the lifted limit and its universal data.

**D108 (08-29, corrected 08-31, `01a04c1c-b22b-7f70-8351-6e12ca028470` 2026-08-29T07:02Z; `01a05682-23ba-7171-bee9-5755d4c313a4` 2026-08-31T12:04:57Z). Fibers, Grothendieck constructions, Yoneda, and representability complete the generic calculus.** A functor has a category-valued fiber over each object. Base change of a fibration is the ordinary pullback of its projection. The Grothendieck construction owns the passage from an indexed category to its total category. Yoneda, co-Yoneda, restricted Yoneda, and the category of representations are generic constructions. Density and separation are properties of the restricted Yoneda functor. Mates, monads, comonads, Eilenberg--Moore categories, and reflective or coreflective subcategories are later extensions.

**D109 (08-29, clarified 08-30, `01a04c1c-b22b-7f70-8351-6e12ca028470` 2026-08-29T07:34Z; `2026-08-30-cce86657` 2026-08-30T18:13Z). Sage is the private runtime and compiler substrate.** The owned `Cat` layer determines every mathematical category, functor, property, construction, and public type in an entirely new graph. A private Sage runtime graph mirrors the three owned implementation-class graphs only so Sage can supply controlled C3, dynamic classes, refinement, and ordinary `Parent` machinery. It neither imports nor extends Sage's mathematical category graph. The owned and Sage runtime implementation classes meet only through the low-level Python/Sage ancestry propagated from the `Cat().ObjectType` root. No relation in the private runtime graph states a public subcategory relation or changes the owned mathematical graph.

**D110 (08-29, corrected 08-29, `01a04c1c-b22b-7f70-8351-6e12ca028470` 2026-08-29T07:34Z, 2026-08-29T09:15Z). Sage compiles each implementation class.** For each owned category `C` and implementation-class kind `R`, a private runtime category `_RuntimeImplementationCategory(C, R)` has as immediate Sage supercategories the private implementation categories selected by the applicable immediate structure-functor edges. Its one method provider is `C`'s local `ObjectType`, `ElementType`, or `MorphismType`. Sage's `_all_super_categories`, `_super_categories_for_classes`, `_make_named_class`, controlled C3, and `dynamic_class` build the resulting `parent_class`. The repository keeps only the adaptations Sage cannot supply: rebinding a copied zero-argument `super()`, semantic collision rejection, categorical level identities, private runtime state sharing, and once-only initialization. It has no second graph linearizer or dynamic-class identity system.

**D111 (08-29, `01a04c1c-b22b-7f70-8351-6e12ca028470` 2026-08-29T07:34Z). Sage owns ordinary runtime refinement and caching.** An owned value that is a Sage `Parent` uses `Parent._refine_category_`. Other owned values use the same small pattern with the private runtime category join and `dynamic_class`. `CachedRepresentation`, `UniqueRepresentation`, and `cached_method` own caches whose keys have ordinary exact equality. `MonoDict` and `TripleDict` remain for keys containing owned values whose equality is proposition-valued.

**D112 (08-29, `01a04c1c-b22b-7f70-8351-6e12ca028470` 2026-08-29T07:34Z). Sage axiom and construction categories are private implementation sources.** Sage's `CategoryWithAxiom`, `_base_category_class_and_axiom`, and construction-category factories supply runtime binding, caching, and method-provider assembly. The owned category `C.P()` remains the full replete subcategory and its functorial base changes remain pullbacks in `Cat`. Owned product and other construction interfaces retain their defining functors and universal presentations. Sage's deduction from `super_categories()` never determines this mathematics.

**D113 (08-29, `01a04c1c-b22b-7f70-8351-6e12ca028470` 2026-08-29T07:34Z). Generic `Mor` and `Fun` stay in the owned `Cat` layer.** Concrete leaves can use Sage `Hom`, `Homset`, `Map`, `Morphism`, and identity morphisms when their endpoints are Sage parents. The generic kernel follows their small domain, codomain, parent, and composition protocol without forcing every abstract category object to become a Sage `Parent`. It follows Sage's functor action protocol without inheriting `sage.categories.functor.Functor`, whose endpoints are Sage categories. A selected structure functor remains an owned object of `Fun(C, D)`.

**D114 (08-29, `01a04c1c-b22b-7f70-8351-6e12ca028470` 2026-08-29T07:34Z). Generated Python structure uses Python syntax tools.** The stub projector uses Python 3.14 `ast` for ordinary Python declarations and generated stubs. It uses `tree-sitter-sage` only for Sage syntax. Fixed constructor wrappers keep ordinary declared functions. A later wrapper that needs a generated runtime signature uses `makefun` instead of a local signature generator.

**D115 (08-29, `01a04c1c-b22b-7f70-8351-6e12ca028470` 2026-08-29T08:01Z). Forming a mathematical question is separate from evaluating it.** Calling a truth-valued method constructs an applied proposition. Calling a partial value-valued method constructs an applied query with an exact result category. Neither call evaluates the application. `ask()` is the common evaluation boundary and can return `Unknown`. Category placement or an active assumption changes what `ask()` can establish without changing the proposition or query that the public method constructs.

**D116 (08-29, `01a04c1c-b22b-7f70-8351-6e12ca028470` 2026-08-29T06:02Z, 2026-08-29T08:20Z). Ordinal operators keep their standard meaning.** For ordinals `alpha` and `beta`, `alpha + beta` is ordinary ordinal sum and `alpha * beta` is ordinary ordinal product. The Hessenberg operations use `alpha.natural_sum(beta)` and `alpha.natural_product(beta)`. Ordinal exponentiation remains `alpha.ordinal_power(beta)` because `**` denotes the categorical exponential. The ordinary ordinal category is not presented as a commutative semiring through the Hessenberg operations.

**D117 (08-29, `01a04c1c-b22b-7f70-8351-6e12ca028470` 2026-08-29T06:02Z, 2026-08-29T08:20Z). Aleph and initial ordinal are order functors.** Let `OrdinalOrder()` and `CardinalOrder()` be the thin categories on ordinal and cardinal objects, with one morphism `a -> b` exactly when `a <= b`. `Aleph: OrdinalOrder() -> CardinalOrder()` and `InitialOrdinal: CardinalOrder() -> OrdinalOrder()` act on the unique order morphisms by monotonicity. They are not functors on arbitrary functions between cardinal representatives. Their object actions return the same owned ordinal and cardinal values used by the arithmetic categories.

**D118 (08-29, corrected 08-29, `01a04c1c-b22b-7f70-8351-6e12ca028470` 2026-08-29T08:47Z, 2026-08-29T08:49Z, 2026-08-29T09:15Z). A typical leaf is an executable mathematical definition.** It states its objects, elements, morphisms, default and named semantic constructors, immediate selected structure functors, and only the operations, predicates, algorithms, and theorems first owned there. The main transport work is the explicit object and morphism action of each selected functor. Each action directly constructs its result through the target category's public constructors. A leaf reuses projections, inclusions, restrictions, lifts, fibers, and universal maps retained by the categorical construction that defines it. A property implementation gives its defining proposition and optional exact handlers. A chosen-datum category uses the applicable fiber or Grothendieck construction. The kernel compiles classes and makes inherited implementation state available. Several semantic or engine-ingestion constructors still construct one category-owned implementation type.

**D119 (08-29, corrected 08-29, `01a04c1c-b22b-7f70-8351-6e12ca028470` 2026-08-29T09:01Z, 2026-08-29T09:15Z). Every mathematical value is constructed by its owning category.** `Cat()` supplies the generic categorical calculus and constructs categories. It does not choose a leaf-specific functor or infer how one leaf construction becomes an object of another category. A leaf either reuses the exact functor retained by its defining categorical construction or constructs its new action as an object of `Fun(self, Target)`. Thus `C` constructs its objects, `Mor(C)(X, Y)` constructs morphisms, `Fun(C, D)` constructs functors, and the applicable property or construction subcategory constructs its objects. Convenience constructors belong to that owning category. No parallel `Cat`, kernel, or helper namespace constructs functors for leaves.

**D120 (08-29, `01a04c1c-b22b-7f70-8351-6e12ca028470` 2026-08-29T09:15Z). A functor writer implements one concrete map between two known constructor surfaces.** Each category has a finite, discoverable public set of object and morphism constructors. The writer of `F: C -> D` knows `C`, the immediate target `D`, and the standard categorical calculus. The writer uses arbitrary ordinary Python in `on_object` and `on_morphism`, including private helpers owned by `C`, and ends by returning values constructed through `D` and `Mor(D)`. A helper used only inside these actions is private or local to the action; it is not part of `C`'s public method surface. The kernel derives nothing from the function bodies and requires no duplicate description of them. Selecting `F` in `structure_functors()` only selects the target implementation surface for compilation.

**D121 (08-29, `01a04c1c-b22b-7f70-8351-6e12ca028470` 2026-08-29T15:42Z). One mathematical fact has one semantic owner.** A category, functor, property subcategory, universal presentation, named construction, or category-owned implementation class owns each mathematical fact and public operation. No second runtime or generated entity can represent the same fact. A repair identifies the standard mathematical owner, moves the responsibility there, and deletes the duplicate entity. Renaming the duplicate is not a repair.

**D122 (08-29, `01a04c1c-b22b-7f70-8351-6e12ca028470` 2026-08-29T15:42Z). Layer dependencies preserve mathematical ownership.** Kernel and `Cat` theory modules do not import production leaves. Leaves do not import kernel internals and depend only on their own mathematics, exact immediate targets, generic categorical constructions, and private computation helpers. Private backends do not register categories, refine objects, or control assumptions. Generated stubs and manifests are output projections of accepted declarations; runtime and mathematical declarations never consume them as authority.

**D35 (08-25, corrected 08-29). Category operators and object operators have different owners.** For categories, `D ** C = Fun(C, D)`, `C * D` is the product category, and `C + D` is the coproduct category. Objects receive categorical product, coproduct, biproduct, and exponential operators as inherited defaults. A category-owned implementation overrides a default when standard notation for its objects names another declared algebraic operation. The explicit universal-construction methods remain available (`01a04c1c-b22b-7f70-8351-6e12ca028470` 2026-08-29T06:02Z, 2026-08-29T08:20Z).

**D67 (08-26, corrected 08-28). Scope of the current foundation.** Complete `Cat`, functor categories, the `Mor(n, C)` tower, universal constructions, the method compiler, and the owned `Sets()` category before adding later theories.
Tests can use small vertical examples to establish this foundation.
Those examples do not add their theories to the implementation surface (`01a029f8 2026-08-22T16:48Z`).

**D68 (08-26). Diagram categories are the workhorse.** Provide machinery for finite diagram categories, specializing to filtered ones such as explicit sequences, since ninety percent of downstream code writes `X * Y` or a product over a list.
Do not over-specialize: finite sequence-indexed products alone hit a wall at the adeles.
Do not over-generalize either: ten times the code for the ten percent needing arbitrary diagrams is the opposite error.

**D69 (08-26, corrected 08-29). The categorical binary operators live at the `Cat` level.** Categories receive product, coproduct, and functor-category operators through `ObjectType`. Objects receive defaults through `Cat().ElementType`. A local object implementation can replace a default with its standard algebraic notation. Local declarations win through the compiled MRO (`01a04c1c-b22b-7f70-8351-6e12ca028470` 2026-08-29T06:02Z, 2026-08-29T08:20Z).
That is where the assertion that both operands lie in the same category belongs.
`X * Y` is never silently cast into a product category: when you want that, call the product's own constructor, `(C * D)(X, Y)`.

**D70 (08-27, corrected 08-29). `**` is category-owned.** The inherited default is the exponential object where the category declares one. `Sets()` identifies this exponential with its function set. `Cardinal()` declares cardinal exponentiation. `Ordinals()` uses `ordinal_power()` for ordinal exponentiation. No spelling identifies an exponential object with the fixed-endpoint category `Mor(C)(Y, X)` (`01a04c1c-b22b-7f70-8351-6e12ca028470` 2026-08-29T06:02Z, 2026-08-29T08:20Z).

**D71 (08-26). Canonical objects are included.** `1 = *`, the empty object, simple horns with their boundaries, simplices, and walking structures in `Cat`; the empty set and `[n]` in `Sets()`. Any canonical representing object the constructions need.

## Diamonds and identity

**D36 (08-26). Size is not modeled.** Assume `Cat` is bicomplete and biclosed, so `[C, D] := Hom_Cat(C, D) := Fun(C, D)` is a category under whatever definition is in play.
This is an engineering convenience to be formalized later.
The point is that `Monoids * Rings`, `Fun(Monoids, Sets) * Fun(Rings, Graphs)`, and `X * Y` for two sets all use one interface and one semantics.

**D37 (08-26, corrected 08-30, `2026-08-30-cce86657` 2026-08-30T18:01Z, 2026-08-30T18:11Z, 2026-08-30T18:12Z, 2026-08-30T18:13Z). Controlled C3 owns implementation diamonds in the entirely new owned category graph.** The kernel constructs `C.ObjectType`, `C.ElementType`, and `C.MorphismType` from the immediate targets of the owned functors in `C.structure_functors()`. It realizes that implementation graph through private Sage runtime categories; it does not reuse Sage's mathematical category graph. Sage's controlled linearization places a shared target implementation class once in the resulting MRO, and that implementation class initializes once. When several owned structural paths reach the same implementation owner, there is still only that one private implementation occurrence; the kernel does not construct, compare, merge, or reconcile competing public functor images along the other paths. D56 remains the declaration-order preference rule wherever a route preference is needed; controlled C3 supplies the class occurrence rather than a second preference rule.

Every structural diamond in the owned graph is valid input to compilation. A diamond whose coherence has not been explicitly represented in the owned mathematics is **unresolved** only for diagnostics: compilation proceeds, while an opt-in `DEBUG` log records the outstanding diamond. If that diagnostic identifies a preferred path, it follows D56's declaration order. It is never a normal warning, failure, proof obligation, or runtime coherence check. This diagnostic applies equally to diamonds that arise while familiar Sage categories are later reconstructed as new owned leaves; no Sage provenance marks them resolved.

Future kernel work may let theory code supply actual owned coherence data between the relevant composite functors, using the existing 2-morphism/natural-transformation machinery rather than a certificate, proof record, or compiler metadata object. Such supplied coherence silences the debug diagnostic for that diamond. The exact public spelling and the exact required property of the 2-cell are deferred until that mechanism is implemented; absence of coherence data never blocks ordinary compilation. The controlled-C3 implementation mechanism is Sage's `Category._all_super_categories` and `C3_sorted_merge` machinery (`sage/categories/category.py`, `sage/misc/c3_controlled.py`, inspected 2026-08-29).

**D38 (08-26, corrected 08-28). Set equality is a proposition, not a procedure.** The image in `Sets()` of `Free_R(S)` can be created by fiat, from a membership rule and a cardinality rule; nothing enumerates it and there is no extensional description to compare.
`X == Y` is `True` by identity and otherwise `Unknown`, unless a cited theorem or an exact computation decides it.
The compiler never uses set equality to merge public functor images.
Each named functor constructs its own public image, and two functors with the same endpoints can return different objects (`4544eba5 2026-08-28T12:00Z`; `4544eba5 2026-08-28T12:18Z`).

## Leaf discipline

**D80 (08-28, corrected 08-29). A category class defines the category and its implementation classes together.** A category is defined by a class in the Sage model.
That class contains its nested `ObjectType`, `ElementType`, and `MorphismType`, its constructors, and its immediate structure functors.
The kernel constructs the three exact nested classes dynamically from that declaration.
Parameterized category families use ordinary mathematical constructors or functors into `Cat()` as their definitions require (`b55dc6aa` 2026-08-27T18:57Z; `01a048f6-e3f5-7e42-be2a-1f60f70ac23e` 2026-08-28T21:03Z, 2026-08-28T21:06Z).

**D81 (08-28, `77631b59` 2026-08-28T17:35:47Z). Imports flow from the kernel into the leaves, never backwards.** No kernel module imports a leaf module.
This is the executable form of the Philosophy's information-flow rule: a generic construction is parameterized by its ambient category and never imports a leaf category to obtain one. A kernel module that imports a leaf has taken that leaf's mathematics into the kernel, which is the defect the rule names whether or not the result works.

**D86 (08-28, `77631b59` 2026-08-28T19:03:51Z, corrected 2026-08-28T19:12Z). An identity is named by the operation it is an identity for, and the identity morphism is one of them.** `identity()` unqualified says nothing: `ZZ.identity()` could be `0` or `1`. An identity comes from the magmatic structure, which splits into the additive and multiplicative axiomatic subcategories, so the names are `additive_identity()` and `multiplicative_identity()`.
Sage draws the same split with the same mechanism: `AdditiveMagmas.AdditiveUnital` supplies `zero()` and `Magmas.Unital` supplies `one()` (`sage/categories/additive_magmas.py:599,696`, `sage/categories/magmas.py:461,482`, inspected 2026-08-29).
Composition induces a multiplicative monoid structure on `End_C(X) = Mor(C)(X, X)`. Its unit is `End_C(X).one()`.

**D83 (08-28, corrected 08-30, `77631b59` 2026-08-28T18:10:28Z; `01a04e73-53f5-7280-8e1f-48e3a96c204f` 2026-08-30T00:56Z). Property containment is a subcategory monomorphism.** `Mor(C).Isomorphisms()` is a full subcategory of `Mor(C).Monomorphisms()` and of `Mor(C).Epimorphisms()` simultaneously, the same way `Sets().Finite()` is a full subcategory of `Sets().Countable()`. The declaration retains each exact subcategory monomorphism. An inherited property on `D` along `F: D -> C` is the inverse-image pullback `F.inverse_image(C.P())`. Propositional implication remains an operation on propositions.

**D82 (08-28, corrected 08-29). Category-valued families are ordinary mathematical constructions.** A family such as `Discrete: Sets() -> Cat()` or `MonoidObjects: Cat() -> Cat()` is a functor because its mathematics is functorial.
A constant category such as `Sets()` is constructed by its category class.
The kernel supplies category-independent class compilation and construction machinery; it does not list future leaf categories or use their absence as runtime state (`b55dc6aa` 2026-08-27T18:57Z; `01a048f6-e3f5-7e42-be2a-1f60f70ac23e` 2026-08-28T16:05Z).

**D84 (08-29, corrected 08-30, `01a048f6-e3f5-7e42-be2a-1f60f70ac23e` 2026-08-28T18:36Z, 2026-08-28T18:48Z, 2026-08-28T19:09Z; `01a04c1c-b22b-7f70-8351-6e12ca028470` 2026-08-29T08:20Z; `01a04e73-53f5-7280-8e1f-48e3a96c204f` 2026-08-30T00:56Z). Identity morphisms and object-dependent constructions keep their mathematical owners.** For `X in C`, the identity morphism is `End_C(X).one()`, the unit of the endomorphism monoid on `Mor(C)(X, X)` under composition. The inherited fixed-object construction methods are `C.Subobjects(X)`, `C.Superobjects(X)`, `C.CoveringObjects(X)`, and `C.CoveredObjects(X)`. The ambient category in the call fixes the role of `X`; the same value can occur in more than one category. `Sets().Subobjects(X).from_predicate(predicate)` constructs the set subobject selected by a predicate.

**D85 (08-29, corrected 08-29, `01a048f6-e3f5-7e42-be2a-1f60f70ac23e` 2026-08-28T18:48Z, 2026-08-28T18:49Z, 2026-08-28T19:05Z, 2026-08-28T19:09Z). Uniform category operations are inherited methods.** `Cat().ObjectType` defines each method once, and every category inherits it through the implementation-class hierarchy. In particular, its fixed-object methods return the monomorphism or epimorphism property subcategories of slices and coslices. A leaf supplies only its specialization, realization, and new mathematical constructors. Type-specific and leaf-specific convenience aliases begin after version 1.

**D87 (08-29, `01a048f6-e3f5-7e42-be2a-1f60f70ac23e` 2026-08-28T19:25Z). A construction specification follows the category graph.** `Cat` owns the shape, index, diagram, cone or cocone, defining morphisms, universal morphism, and every operation determined by that categorical construction. A leaf specification links to that contract and states its mathematical delta: the added leaf structure, its membership and equality predicates, its cardinality or other leaf operations, its exact algorithms, and its private engine realizations. A public name identifies the exact mathematical object or morphism it returns. One generic construction has one inherited public surface.

**D88 (08-29, corrected 08-29, `01a048f6-e3f5-7e42-be2a-1f60f70ac23e` 2026-08-28T19:38Z; `01a04c1c-b22b-7f70-8351-6e12ca028470` 2026-08-29T07:02Z). Version 1 exposes defining data and composes public operations.** A universal presentation supplies its diagram, apex, legs, and universal map. A derived query uses ordinary composition on that data. For a selected product cone `p`, apply `p.diagram().on_object(i).cardinality()` to its factors. This rule applies to the complete specification surface, not only to construction queries. An operation expressible as one or two lines of public compositional code receives no additional method in version 1.

**D89 (08-29, corrected 08-29). The kernel generates property applications from axioms.** Declaring the axiom `P` on `C` makes the functorial construction `C |-> C.P()` available and gives each `C.P()` its monomorphism into `C`. A concrete implementation identifies that same axiom through Sage's `_base_category_class_and_axiom = (CClass, "P")` registration. The registered axiom identifier supplies the substitution in `is_P`: the kernel converts its CamelCase spelling to snake case and prefixes `is_`. Thus `"Finite"` gives `is_finite()`, `"FullyFaithful"` gives `is_fully_faithful()`, and `"OfCardinalityExactlyFour"` gives `is_of_cardinality_exactly_four()`. The kernel generates that method on `C.ObjectType`. It returns the containment proposition for `C.P()`. Descendants receive it through compiled inheritance. No leaf writes or separately names the method. `Sets().ObjectType.is_finite()` therefore returns the proposition that the supplied set lies in `Sets().Finite()`. Only `ask()` decides that proposition (`4544eba5` 2026-08-28T12:00Z; `01a048f6-e3f5-7e42-be2a-1f60f70ac23e` 2026-08-28T19:51Z, 2026-08-28T22:51Z, 2026-08-28T23:00Z, 2026-08-28T23:05Z).

**D97 (08-28, corrected 08-31, `01a05682-23ba-7171-bee9-5755d4c313a4` 2026-08-31T12:04:57Z). An axiom makes a subcategory available; an exact SymPy handler can compute refinement into it.** These mechanisms are independent. A Sage axiom registration makes `Sets().Finite()` available for trusted construction and refinement. The category owns its finite predicate meaning and defines its public SymPy predicate. Exact handlers can decide that predicate. The registered implementation class is still the one `Sets().Finite()` category. Positive placement, assumption, or handler results use the same refinement.

**D95 (08-29, corrected 08-29, `01a048f6-e3f5-7e42-be2a-1f60f70ac23e` 2026-08-28T21:06Z; `01a04c1c-b22b-7f70-8351-6e12ca028470` 2026-08-29T09:15Z). `C.ObjectType` is the exact class name.** A category specifies `C.ObjectType`, and the kernel constructs `C.ObjectType` dynamically. For each structure functor `F: C -> D`, `C.ObjectType` inherits `D.ObjectType`. The kernel supplies the corresponding applicable `ElementType` and `MorphismType` inheritance without another functor-writer declaration. A leaf never constructs this inheritance. Policies, specifications, and plans name the exact class they mean.

**D96 (08-29, corrected 08-30, `01a048f6-e3f5-7e42-be2a-1f60f70ac23e` 2026-08-28T21:20Z; `2026-08-30-cce86657` 2026-08-30T18:13Z). A structure functor is an edge of the new owned implementation graph; it does not assert a subcategory relation.** A functor returned by `C.structure_functors()` can be forgetful, a projection, a fibration, a subcategory monomorphism, or another functor whose target classes supply inherited implementation. Its compiler role is analogous to the role Sage's `super_categories()` relation plays for Sage's own mixin graph, but it is not a reused or translated Sage edge.
Its use in dynamic class construction does not assert that `C` is a subcategory of its codomain or that an object of `C` is its public image under the functor.
The public image `F(x)` remains a separate object owned by `F`.
A subcategory relation exists only through its declared monomorphism.

**D90 (08-29, corrected 08-29, `01a048f6-e3f5-7e42-be2a-1f60f70ac23e` 2026-08-28T20:21Z). Algebraic structures expose their standard mathematical syntax.** A magma constructor receives or defines its multiplication morphism. The additive and multiplicative subcategories expose the corresponding binary operation through `+` and `*`. The public API has no generic `operation()` or `combine()` alias. The specification does not prescribe private storage. Accessors for other chosen structures require their own mathematical contract.

**D91 (08-29, corrected 08-29, `01a048f6-e3f5-7e42-be2a-1f60f70ac23e` 2026-08-28T20:21Z). Property refinement and representation construction are distinct.** Positive property evidence uses the kernel's same-object refinement mechanism. This does not limit the property's constructors. A finite-set category can accept lists, tuples, Python sets, SymPy sets, Julia sets, GAP sets, and other supported representations through as many exact constructor routes as its mathematics requires.

**D92 (08-29, `01a048f6-e3f5-7e42-be2a-1f60f70ac23e` 2026-08-28T20:21Z). Active prohibitions remain explicit.** A specification keeps prohibitions that exclude known architectural failure patterns. Such a prohibition is a current contract, not a record of removed implementation history.

**D93 (08-29, `01a048f6-e3f5-7e42-be2a-1f60f70ac23e` 2026-08-28T16:05Z). Kernel and leaf implementation proceeds in strict dependency order.** First specify the complete kernel contract and its detailed acceptance criteria. Then implement and independently accept the kernel while production leaves remain unchanged. After that, implement and independently review one leaf phase. A leaf defect returns to that leaf phase. A generic defect returns to the kernel phase and invalidates every dependent acceptance. Kernel and production leaf implementation never proceed in parallel.

**D77 (08-28). The leaf writer's contract is a closed list.** The kernel exists to make this list short, so anything a leaf must supply beyond it is a kernel defect, not a leaf obligation.

1. `ObjectType`, `ElementType`, and `MorphismType`, as nested classes.

2. Constructors: how another mathematician builds objects of your category, in the terms your mathematics uses.

3. Functors: how ordinary executable actions construct objects and morphisms through another category's public constructors.
   Returning the applicable ones from `structure_functors()` is where the owned category states which target implementation supplies inherited structure.

4. Which axiomatic subcategories are available.
   Finiteness is declared once as `C.Finite()`, and any category `D` with a functor into `C` can then declare `D.Finite()`, exactly as Sage's `with_axiom` propagates an axiom down the graph.

5. For a property-based subcategory, its containment predicate.
   That predicate is the whole declaration; membership, refinement, and `ask()` follow from it.

6. The wiring that makes a category the concrete implementation of such a subcategory.
   `FiniteSets` declares itself the implementation of `Sets().Finite()` and adds the methods that finiteness makes available; that is Sage's `_base_category_class_and_axiom` shape (D55, `POL-LEAF-059`).

The list is what a mathematician writes.
Everything else - inheritance, dispatch, construction threading, caches, class building - is the kernel's, and it is the kernel's precisely so that this list stays this short (D04).

**D39 (08-22). What a leaf implementer supplies.** Functors to known owned categories that show how to feed the new category's objects into another owned category's constructor, plus a constructor for the minimal delta that defines the leaf.
`Modules(R)` built from an action `rho: R -> End(X)` and selecting the owned functor to `Sets()` needs only the functor that uses `rho` to extract `X` and feed it to the `Sets()` constructor.
The red flag is a lattice category defining `cardinality()` instead of declaring its functor to `Modules(R).Free()`. Constructors and functors are among the few places where reaching into private fields may be acceptable, and each such use needs scrutiny.

**D40 (08-22). Mathematical encapsulation, enforced by the file system.** A leaf defining something that depends on deeply underlying structure in another category is a red flag — `cardinality` mentioned in a lattice subtree, for instance.
Keep the kernel siloed in its own subtree with its own test subtree, and split into subtrees as they grow: `Cat`, `Sets`, modules, formed modules, algebras.
Consider nesting for hot paths such as free modules over a PID. The point is that the kernel subtree may use ordinary Python and is the firewall for non-mathematical code, while every mathematical subtree can be audited for non-mathematical language and types.
Engine boundaries — Sage, SymPy — should be quarantined in their own subtrees, where repository rules may be violated out of necessity, so that violations are firewalled by layout.

**D41 (08-22). A subcategory should almost never exist to house an implementation.** A method belongs at the most general category where it makes sense and where something is at least declarable, so an object can be constructed by supplying that data, and different computational implementations can be selected by case.
`Sets.PropertyCategory()`, invented to wrap subsets defined by a predicate, was the red flag: any set can form a subset from a predicate, and the result is a subobject in `Sets`. There is no mathematical notion of "a set defined by a property" — every set is.
The naming is the tell: `PropertySet` is engineering-brained.
Track construction provenance privately if you need it.

**D42 (08-22, corrected 08-28). The user should not need to know the category graph.** Nobody should write `FiniteSet({1, 2, 3})`; `Sets({1, 2, 3})` uses the total constructor selected by that datum.
Additional construction data or established properties select separate, specifically named total constructors.
A small number of high-level endpoints are the primary construction interface.
Specific named constructors state any stronger construction (`4544eba5 2026-08-28T11:34Z`; `4544eba5 2026-08-28T12:00Z`).
Usability comes from discoverability through well-known names: `Sets`, `Monoids`, `Groups`, `Rings`, `Modules(R)`, `Algebras(R)`.

**D43 (08-24). The leaf class is the implementation, and it is the firewall.** There is never more than one choice of implementation: Sage already lets competing implementations proliferate, with three different free modules carrying different operations and inconsistent inherited surfaces.
Mathematically there is one notion of a free module.
Your `ObjectType` hides every possible implementation, collected in one class.
Internally you may use anything — Sage, SymPy, NumPy, an imported dependency such as VinAL for hyperbolic lattices, a bespoke research algorithm, Cython, a shell program, Julia, GAP, Singular, Macaulay2 — provided the public API never exposes the choice.
There is no automatic routing into engine methods and no `@realized_operation`-style marker.
Quarantine substantial Python complexity into helper modules.

**D44 (08-24). Inherited fundamentals stay inherited.** Composition of arrows is basic category theory and arrives by inheritance.
A leaf may override to add leaf-level mathematics — a free-module morphism hooking composition to build a private matrix — but a method that adds no new mathematics does not belong in a leaf at all.
Inheritance is automatic; you write wiring only when you are adding mathematics.

**D45 (08-24). The question to answer at every step.** "What generic categorical mechanism makes every leaf state only its new mathematics?"
Only that determines where code lives, which objects own theorems, how calls work, and what methods must exist.
Trace the whole implementation path: how the kernel defines products, how they propagate through categories and presentations and structure functors, so that the leaf supplies only its delta.

**D73 (08-28). Every method makes its choices explicit.** A method that returns the image of a value in another category names the functor and both its endpoints.
A name that does not determine the codomain chooses silently, whatever noun it uses: a module's object could be asked for as an object of `C`, as an abelian group, or as a ring when it happens to be one.
So there is no accessor standing in for a functor.
If you want to project to sets, you construct that functor and apply it.

The rule is a consequence, and the reason it keeps having to be restated is that only the rule was ever written down.

*A relation between two categories exists only as an arrow.* An object does not carry its underlying set the way a record carries a field.
There is nothing inside a module that is the set; there is a functor whose image at that module is a set.
A generic accessor asserts that the relation is a property of `X` alone, and it is not — it is a property of a map somebody chose.
A category-level image accessor has the same defect: it names a target and hides the functor.
The mistake recurs because the surrounding programming model always offers "get the part", and mathematics offers only "apply the map you named".

*The choice is real, so hiding it asserts mathematics.* `R^n` does not project directly to sets: it is an `R`-algebra because it is a product of rings, so it reaches sets through rings, and its object there is `U(R) * ... * U(R)`. A lattice `(L, b)` projects to `L` and to `b` with equal right.
A simplicial set has `X_0`, the disjoint union of its `X_n`, and `pi_0`, three functors to `Sets()` carrying different mathematics.
An implicit choice is not merely underspecified: it silently claims that one of several genuinely different constructions is the canonical one, and it makes that claim in a place where no reader can see it.

*The arrow is where the leaf writer's work lives.* Everything the framework supplies is a consequence of stating the map: the inheritance, private runtime state sharing, and the construction lifts.
An accessor that hands back an ancestor value is a way to obtain that value without stating the map — so the mechanism never runs, and the leaf ends up reimplementing what it should have received.
That is a bypass around the structure-functor mechanism.

*And it is what makes the code auditable.* A mathematician can read `U_A(M)` and check it against the definition.
Reading an accessor that omits the functor endpoints requires opening the implementation to find out which category was meant, which is programming rather than mathematics, and it forfeits the reason the layer exists at all (D03).

The same philosophy governs every other implicit choice, not just this accessor.
A coercion, a default ambient category, or a walk to a "common ancestor" is the same defect wherever it silently selects a category — which is why common-ancestor tracing has to run along a named, citable property of functors and never a heuristic (D61).

**D76 (08-28, corrected 08-28). Distinguish preservation from equality on the nose.** A functor `U` preserves a product when the canonical comparison morphism `U(prod X_i) -> prod U(X_i)`, induced by the cone `(U(pi_i))`, is an isomorphism.
A lifted construction can require more: its chosen apex and defining morphisms can map to the chosen ambient construction on the nose.
State that stronger equality where the construction needs it.

This construction-level equality does not identify the public images of arbitrary named functors (`01a03c6a 2026-08-26T07:36Z`; `4544eba5 2026-08-28T12:18Z`).
Inheritance follows the Sage dynamic-class MRO from the immediate structure-functor targets (D37, D95, D96). A leaf that lifts an ambient construction builds on the ambient apex and retains its defining morphisms; the compiler has no preservation registry.

**D75 (08-28). Objects carrying a choice form the total category of a fibration over the base, and the choice is usually a morphism.** Sage names the phenomenon — `Modules(R).WithBasis()` is "the category of modules with a distinguished basis" (`sage/categories/modules_with_basis.py:179`), with `AlgebrasWithBasis`, `WithRealizations`, and the `FinitelyGenerated` family beside it, all on the same axiom machinery as `Finite`. Taking the name is not taking the construction, and the construction is what has to be stated.

`Modules(R)` and the category of pairs `(M, S)` with `S` a chosen generating set are completely different categories.
The relation between them is a fibration `p: E -> Modules(R)` whose fibre over `M` is the category of choices for `M`, with `p` the functor that forgets the datum; the pairs are the objects of the total category, obtained by the Grothendieck construction from the assignment `M |-> {choices for M}`. Straightening and unstraightening are the two directions of that correspondence.

The citations, inspected: the Grothendieck construction `∫F` of a pseudofunctor `F: C^op -> Cat` has as objects the pairs `(c, a)` and as morphisms the pairs `(f, phi)` with `f: c -> c'` in `C` and `phi: a -> F(f)(a')` in `F(c)`, with `p: ∫F -> C` the first projection, and `∫` is an equivalence of 2-categories onto the fibrations over `C` ([nLab, "Grothendieck construction"](https://ncatlab.org/nlab/show/Grothendieck+construction)). A fibred category is one where every morphism of the base lifts to a strongly cartesian morphism ([Stacks Project, Categories, Definition 4.33.5, tag 02XJ](https://stacks.math.columbia.edu/tag/02XJ), with Lemma 4.33.7 giving the pseudofunctor once pullbacks are chosen).

The datum is itself a morphism, which is why one construction covers the whole family.
A generating set `S` for `M` is an epimorphism `Free_R(S) ->> M`. A finite presentation is a length-two resolution `Free_R(X_1) -> Free_R(X_0) -> M`. A resolution of any length is the general case.
So these are categories of diagrams over `M`, expressible with machinery this repository already owns: `C.SliceOver(M)`, `Fun([1], C)` and its evaluations, and `Fun(I, C)` for a shape `I` (D34, D68). `WithBasis`, `WithGeneratingSet`, and `FinitelyPresented` are one construction at different shapes, not a family of separate axioms — which is the whole point, since one mechanism stated once is what the framework buys (see the Philosophy).

The name also hides a real choice about morphisms, which the construction has to make explicit: whether a morphism of the total category is required to respect the datum, and whether it is cartesian over the base.
Sage's own case shows the subtlety — its `ModulesWithBasis` morphisms are ordinary module morphisms, while the homset uses the distinguished bases to read a matrix as a morphism (`sage/categories/modules_with_basis.py:47`). That is a decision, not a detail, and `With<Datum>` states none of it.

Two places the pattern does not reach.
There is no bare object to equip when the object is already the pair. An object of `Subobjects(X)` is an object together with a monomorphism into `X` (D74). A construction family that already retains its construction is the equipped form, so it needs no adjective. A product has many isomorphic siblings, and the repository keeps the one it built.

**D74 (08-26, corrected 08-30, `01a048f6-e3f5-7e42-be2a-1f60f70ac23e` 2026-08-28T18:48Z, 2026-08-28T19:25Z; `01a04c1c-b22b-7f70-8351-6e12ca028470` 2026-08-29T06:02Z, 2026-08-29T08:20Z; `01a04e73-53f5-7280-8e1f-48e3a96c204f` 2026-08-30T00:56Z). `Subobjects(X)` retains a monomorphism representative, and restricting structure to one is leaf work.** An object is a pair `(A, i)` with `i: A -> X` monic. A subobject in the quotient sense is an isomorphism class of such representatives. Equality of represented subobjects is a proposition.

For a poset `P` presented by `(X, R)`, `Sets().Subobjects(X).from_predicate(predicate)` constructs only a set subobject. `Posets().Subobjects(P)` specializes the inherited construction by retaining the restricted order and monomorphism in `Posets()`. The ordering subtree decides the strongest established order category of the result.

The theorem that transports a monomorphism between the set and poset categories belongs to the leaf that states it. The compiler supplies only the generic construction and inherited category structure.

**D72 (08-27). Categories of structured objects are parameterized by another category.** `Semirings`, `Magmas`, `Monoids`, `Rings`, `Modules`, and `Algebras` all take an ambient category.
The point is only to endow objects with the corresponding methods.
Sage's monoids are monoid objects in sets; taking the ambient category as a parameter is the generalization, not a specialization to `Cat`.

## Types and style

**D78 (08-28, session `353b942d`). Automated checks are not the arbiter of correctness before 1.0.** Never run a test suite, type checker, linter, formatter, or diagnostic sweep against an incomplete or incorrect architecture, and never chase test or lint correctness mid-refactor. The reason is the gradient it sets, not the timing: it polishes intermediate code the refactor will delete or obviate; it rewards golfing that code until the checks pass, which optimizes the checker rather than the architecture; it implicitly protects the old code the refactor exists to replace, because breaking it registers as a failure; and it can derail the refactor outright, turning a structural change into a sequence of local repairs that keep the checks green.

Regression prevention is not a goal before 1.0, and pursuing it is gradient-misaligned with correctness. The architecture is still being designed, so a regression test locks in behaviour that the design work exists to replace, and each one becomes a reason not to make the change that is needed. After 1.0, when edits are incremental against a working codebase, regression prevention is the point and the craft of writing a good test applies to it. Rules about honesty never lapse in either phase: an assertion states a mathematical proposition or an essential type invariant, every expected fact needs an independent inspected oracle, no mock or skip is evidence, and arithmetic is exact.

Tests are for regressions and end-to-end behaviour. They are not for internal consistency, they are not unit tests, and they are not a way to lock in current behaviour. A one-off test is fine, and so is adding a test and running it on its own while working - as a feedback signal, never as a correctness signal. Lean on red commits until a 1.0 milestone.

Until then the arbiter is agreement with the plans, the specifications, and the transcripts. Establishing that agreement takes intelligent, dynamic, adversarial review, for which subagents are appropriate: alignment with the stated architecture, contradictions between documents, abstraction leaking across the kernel and leaf boundary, and drift from what was actually decided. A green suite is evidence of none of it.

**D79 (08-28, session `be8d8a9e` 2026-08-28T15:50Z). Do not build automated enforcement before 1.0.** Adding a lint rule, an `ast-grep` rule, a CI gate, a hook, or a checker to police a convention is the same gradient error as `D78`, one step earlier. It turns a judgement that belongs to review into a check that can be satisfied, and it fixes a convention's current wording into machinery while the architecture that gave the convention its meaning is still moving. The wording then cannot change without changing the machinery, so the machinery starts deciding the architecture.

Observing that nothing enforces a rule is not a finding, and it is not a reason to write the enforcement. The absence is the design. A rule is carried by the documents an agent reads before working and by review that reads them. Where a rule is being broken, the finding is the breach and its repair.

This does not retract `D51`. Static projection of the declared architecture - stub generation, the category type-checker plugin - states what the code already declares, enforces no convention, and stays.

**D46 (08-22). Everything is a tensor.** The package departs from Sage's linear-algebra primitives: not vectors as internal representations of module elements and matrices as internal representations of module morphisms, but `(p, q)`-tensors throughout, encoded at the module `ElementType` level.
A bilinear form is a Gram tensor, not a Gram matrix.
`vector()` and `matrix()` shadow a `tensor()` constructor taking `(p, q)` shapes, base rings, and multi-indexable data.

**D47 (08-22). Morphisms never operate on plain Python objects.** Always construct elements of the appropriate objects.
A hom-category `__call__` may assert `x.ambient_object() in self.base_category()`.

**D48 (08-22). Do not coin a name for a standard notion.** `type MathematicalObject = Any` and `SetMapRule` are both defects.
The standard notion is a morphism of sets, and the type is `SetMorphism`. Calling it a "map" or a "rule" avoids the standard semantics.

**D49 (08-22). Each category is internally consistent in its types.** A poset method takes `PosetElement := Posets().ElementType`, never `SetElement`, so that passing an unstructured set element is a static type error — even when the poset element class adds nothing.

**D50 (08-23, corrected 08-30). Never write a method that only fails.** No body that is `assert False`, `return NotImplemented`, or a raise.
That hides a missing capability from static checkers and surprises the user at runtime; the point is a uniform interface.
A `cardinality()` that raises is worse than no `cardinality()` at all.
Use abstract methods or expose the method only on the category that owns the capability.
When a mathematical truth question is not total and exact on its full declared domain, return an applied proposition. For any other partial mathematical query, return an applied query with its exact result category. Evaluate either application with `ask()`.

**D51 (08-23). Do not golf type checkers.** They are a signal; the architecture and philosophy are the arbiters of correctness.
The compiler should be strong enough to teach mypy about the functorial construction, but a very dynamic process may exceed what mypy can follow.
Type-checker plugins are legitimate, as is static generation — manifests, statically constructed types, stubs — regenerated on commit, test, push, or version bump, since the repository does statically encode all its intended relations at any given time.

**D52 (08-24). Never use optional arguments.** Write total methods and separate, specifically named constructors.
A set constructor that can accept a cardinality by fiat does not make cardinality optional with a default; it is total in cardinality, with `construct_uncountable_set`, `construct_countable_set`, and `construct_finite_set` split out.

**D53 (08-23). Prefer the mathematically flavoured construction.** `pairwise` over `zip`, and generally: look for packages and dependencies that improve the mathematical flavour of the code, and propose them when the idea surfaces.

## What the documents are for

**D94 (08-29, `01a048f6-e3f5-7e42-be2a-1f60f70ac23e` 2026-08-28T17:36Z, 2026-08-28T18:18Z, 2026-08-28T18:20Z, 2026-08-28T18:30Z). An executing plan records resolved contracts.** Before a phase starts, its governing decisions and specifications fix every mathematical owner, public spelling, input and result category, constructor contract, dependency, exclusion, and acceptance statement needed to implement it. The plan states those decisions and the work that makes them true. It does not defer them with tasks to determine, choose, clarify, or correct a contract or policy during implementation. If the transcripts do not determine a required decision, ask the user before implementation starts and then update the governing specification and plan.

**D100 (08-29, `77631b59` 2026-08-29T02:43:39Z). A separating family declares nothing this repository uses.** `separating_family()` returns a tuple whose unstated meaning is that its objects jointly separate morphisms, and downstream code reads it as authorization. That is theorem metadata: `POL-MATH-031` forbids runtime metadata repeating a fact, `POL-MATH-032` makes construction authority static ownership rather than runtime data, `POL-MATH-037` makes constructing in the category the assertion, and `POL-MATH-045` forbids a second runtime classification of one fact.

Every claimed use has a more direct owner:

- constructing `Hom(G, -)` needs only the object `G`, and does not need `G` to be a generator;
- that `Hom(G, -)` is faithful belongs on that named functor, through `.Faithful()`;
- morphism equality belongs to the category's equality predicate and its exact leaf algorithms;
- a functor `X -> Y` transports points `* -> X` by composition;
- structural inheritance uses the selected structure functor, not faithfulness;
- set equality already uses identity, symbolic comparison, finite extensional comparison, or `Unknown`.

So the tuple-based declaration leaves the kernel. Named restricted Yoneda functors and their properties own every supported use.

Corrected 08-29: this entry originally added that generators buy the repository nothing. That is stale. [Separating families and categorical generators](separating-families-and-categorical-generators.md) records concrete uses — presentations, restricted Yoneda functors, density, and evaluation epimorphisms. What is banned is the tuple as theorem metadata and as construction authority, not the notion. Generators and separating families stay, through named mathematical constructions: faithfulness on the restricted Yoneda functor, canonical evaluation maps in the established epimorphism category, and finite presentations for finitary morphism constructors.

`Sets()` hid the conflation, because its terminal object `1` is also a generator; the two notions differ in general.
**D99 (08-29, corrected 08-29, `77631b59` 2026-08-29T00:44:44Z; `01a04ab2-d713-74b3-8a24-eeef392b0869` 2026-08-29T00:48Z). `Core` is a functor `Cat -> Groupoids`, and category relations belong to their named structure functors.** Three objects are distinct: a multiplicative property `P` of the morphisms of `C`; the category `W_P(C)` with the objects of `C` and only its `P`-morphisms; and the inclusion functor `i_P: W_P(C) -> C`. A construction produces a category and its defining functor. The category and its inclusion are never two spellings of one object.

`Core(C)` is not `Mor(C).Isomorphisms()`. `Core(C)` has the objects of `C`, and its morphisms are the isomorphisms of `C`. `Mor(C).Isomorphisms()` has the isomorphisms of `C` as its *objects* and lives one categorical level higher; it can say which arrows enter the core and it is not the core.

The functorial formulation is `U: Groupoids -> Cat` and `Core: Cat -> Groupoids`, with the inclusion the component `eps_C: U(Core(C)) -> C`. `C.Core()` returns `Core.on_object(C)`, and the cardinality functor has domain `Core(Sets())`.

`Groupoids()` is a declared point of `Cat`; the current foundation requires no further groupoid implementation. `Core` is required. The generic public `WideSubcategory(P)` has no independent production use. Do not reintroduce it unless a later user decision requires that general construction.

Use standard functor properties on the named object of `Fun(C, D)`. `Faithful` means injective on each fixed-endpoint morphism collection. `Full` means surjective. `FullyFaithful` means bijective. `EssentiallySurjective` means that every target object is isomorphic to an image. These replace presentation-dependent object counts and ambiguous global claims about bijectivity on morphisms. Most structural relations have this form: they are properties of the structure functor, not properties of its source category.
**D98 (08-29, `01a048f6-e3f5-7e42-be2a-1f60f70ac23e` 2026-08-28T22:17Z, 2026-08-28T22:27Z, 2026-08-28T22:37Z). Transcript-grounded decisions control documentation repair.** A review of the architecture starts from the user's cited transcript decisions in this file.
The topic specifications and policies state their normalized consequences.
Plans cite those fixed requirements and contain only forward obligations, dependency order, acceptance criteria, and return conditions.
Current code, prior reports, phase status, and an uncited document cannot override a cited decision.

**D54 (08-22).** `CONTRIBUTING.md` holds general principles and patterns grounded in examples, and may hold specific observed antipatterns once they recur enough to matter.

Specifications are forward-facing.
They catalogue the desired functionality, nail down the public API, and may hint at internal strategies.
A specification must be explicit about the expected structure functors. It separates, and does not repeat, the methods expected to arrive by inheritance, keeping one source of truth, though naming a few to ground an example is fine.
A lattice specification should say that it mentions no cardinality, and that cardinality arrives compositionally along a chain of functors landing in `Sets()` — not from a direct functor to `Sets()`.

**D131 (09-01, `6660e9c` 2026-09-01). CategoryPoint.__eq__ returns AppliedPredicate, not bool.** Under POL-API-015 and `specs/undecidable-properties.md`, mathematical equality on `CategoryPoint` (objects, elements, morphisms) returns `AppliedPredicate` — a SymPy proposition evaluated by `ask()`. This intentionally diverges from Python's `object.__eq__ -> bool` protocol. Mypy's `[override]` diagnostic on `CategoryPoint.__eq__` against `builtins.object` is an acknowledged static consequence of this architectural choice and is not a defect. `candidate: Any` on `__eq__` and `__contains__` is permitted per POL-TYPE-004. `__bool__` on `AppliedPredicate` raises to prevent silent boolean coercion; three-valued evaluation requires `ask()` (`specs/undecidable-properties.md`).
