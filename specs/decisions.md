# Architectural decisions

This file records the decisions the repository owner stated in working sessions between 2026-08-22 and 2026-08-28, in Claude and Codex transcripts.
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

- [Purpose and scope](#purpose-and-scope)

- [Selected functors and inheritance](#selected-functors-and-inheritance)

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

**The mathematics is the interface; the presentation must not leak.** A group is technically `(X, f)` and a lattice is technically `(L, b)`, but nobody works with them as ordered pairs.
Publicly a lattice *is* a module with more structure.
An ordered pair is a fine private representation and an unacceptable public one, which is why every `underlying_Y()` deserves suspicion: it is a presentation escaping into the API.

**Depth in the graph bounds vocabulary.** A leaf mentioning cardinality in a lattice subtree is a red flag, not because of layering discipline but because cardinality is not part of what a lattice is.
Vocabulary that leaks across the graph is a mathematical error before it is a structural one.

**The kernel is a black box, and no mathematician ever audits it.** The split is between a mathematical declaration and the wiring that realizes it, never between general and specific mathematics.
`Cat`, `Mor(n, C)`, `Fun(C, D)`, the property subcategories, and `Sets()` are all objects this repository defines, and all of them are read as mathematics.
The kernel is what takes those plain declarations and performs the Python wiring behind them: class building, linearization, constructor threading, caches, descriptors, refinement mechanics.
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

## Purpose and scope

**D01 (08-22). Build the whole foundation before any structured category.** `Cat`, all arrow categories, working inheritance through `ObjectType` and the other implementation classes, and then an extensive `Sets()` that completely replaces Sage's `Sets` and uses none of Sage's categorical constructions.
Do not drift into rings, modules, lattices, or formed modules.

**D02 (08-23). The package shadows a subset of Sage, and its universe is closed.** `sage_categories.all` works like `sage.all`. Once you touch a package-owned object, every further computation stays inside the package: every operation is mediated by the package's categorical API, and every result you can produce is still a package object.
There is no intention to refine Sage objects into this hierarchy or to be compatible with base Sage; any compatibility is incidental.
Base Sage appears only inside hidden implementation engines.
When the package wants a Sage construction, it absorbs it as an internal engine and re-expresses it through the categorical machinery.

The reason is uniformity of interface.
Sage's implementations forget things.
Sage's `IntegralLattice` does not know its underlying set is `ZZ^n`, so `ZZ^n` is not recognised as a product of sets, rings, or rank-one modules, and Sage cannot say its cardinality or iterate it — while research code wants to enumerate infinite countable sets in bounded loops, as Vinberg's algorithm does.

**D03 (08-23). Computation is not the goal.** Sage already computes everything this package computes.
The goals are uniformity, categorically principled code, category theory as a form of DRY, real functors everywhere, and obviating engineering concerns so that a leaf developer thinks about mathematics.
It is an organisational, more legible layer over Sage.
Sage code needs a programmer to audit it; code here, outside the kernel, should be auditable by a mathematician with very little coding experience.

**D04 (08-23). The long-term asymptote.** Adding a category such as `MyVerySpecialAlgebraOverANoetherianDomain(R)` should mean: define a leaf category, possibly from a shipped template; declare a few functors to nearby categories you already understand, without reading the rest of the codebase; write your new methods; and receive the full inherited surface.
You think at the level of your own algebra, and `cardinality()` and suitable limits and colimits arrive because of the functorial wiring.

## Selected functors and inheritance

**D05 (08-23). Never subclass objects of a category explicitly.** Not without discussion first.
`ProductSetObject` must not subclass `SetObject`; that bypasses the functor framework.
If the intended architecture does not work, that is not a licence to subclass.
Even `FiniteSets` inside `Sets`, where the underlying object is "just a set" both times, must declare its functor — here the inclusion, possibly trivial.
Otherwise the category is free-floating.
This is what replaces `super_categories`. The same holds for limits, colimits, products, coproducts, tensor products, direct sums, subobjects, and covering objects.

**D06 (08-24). Sage's `super_categories` conflates distinct notions.** It carries subcategory inclusions, full or not, and structure projections such as `(X, op) |-> X` where `Monoids` declares `Sets` a supercategory.
Replace it with an explicit `structure_functors: list[Functor]`, and name the distinct kinds separately: subcategory inclusion, full subcategory inclusion, projection, and so on.

**D07 (08-24). Selection does not include every functor out of the category.** The selected functors are the ones along which the category inherits.
In the poset example, do not select the second projection: a poset `(X, R)` *is* a set, so it inherits from `X`. Projecting to `R` would give posets the methods of a subset of a product, which is not how anyone works with posets.
This mirrors Sage declaring only `Sets` as the supercategory.

**D08 (08-24). What declaring `F: C -> D` obliges you to supply.** How to take the leaf writer's own implementation class and feed it into *any* available constructor for `D.ObjectType`, and the same for elements and arrows.
A subcategory inclusion claims that `X |-> D()(X)` works.
A product projection claims your objects already carry the target as defining data, so the kernel can extract it.
Those two are boilerplate and the kernel implements them.
Any other functor states its own maps, teaching the target's constructor how to consume your data.

**D09 (08-25). "Forgetful functor" is ill-defined; do not use it.** Categories such as magmas are pullbacks whose objects are pairs, so there are two projections and neither is "the" forgetful one.
For lattices `(L, b)`, the colloquial answer is `(L, b) |-> L`, but `(L, b) |-> b` is equally symmetric.
For `Modules(R)`, whose defining datum is a ring morphism `R -> End(X)`, no kernel can be expected to know that "forget" means `(X, +, rho, ...) |-> X`, and the implementer may choose any of several equivalent presentations.
Formulate instead in terms of fibrations, cofibrations, natural projections and inclusions, source and target functors, arrows induced by Kan extensions, and composites of these.
Follow Mathlib's treatment.

**D10 (08-25). The kernel implements the standard functors.** `FullSubcategoryInclusionFunctor`, `ProductProjectionFunctor(i)`, and their relatives are kernel-owned precisely so that leaves need no boilerplate.
A leaf writing a page of functor code is a kernel defect.

**D11 (08-25, superseded in spelling by D55). Every leaf constructs its functors explicitly.** Not `self.inclusion(D)`. A leaf constructs `Fun(self, D).inclusion()`, or `Fun(self, D).Full().inclusion()`, so that a known theorem appears as part of the construction of the functor.
Nothing is computed; the leaf writer is trusted.
Several equivalent spellings of the functor category remain valid; `Fun` is an additional name, not the sole one.
The `Ar` and `Hom` spellings used on 08-25 were dropped on 08-26; see D55.

**D12 (08-26). A functor does not know it is structural.** Leaves construct ordinary functors and *declare* them, by returning them from `structure_functors()`. There is no kind of functor called structural and no constructor that makes one.

**D13 (08-26). The kernel is Sage's class-building plus one repair.** Sage's MRO technique works.
Its one flaw is that dynamic classes carry methods and leave out fields, so a method arrives without the private data it needs to compute anything.
The intended repair is to copy Sage's class-building and fix that flaw, so that from the writer's point of view it is ordinary inheritance.
If `Sets().ObjectType` holds private set data and a constructor that initializes it, and `Posets()` holds its own private poset data, its own constructor, and a functor that supplies what the `Sets()` constructor requires, then a poset receives inheritance rather than methods alone.
Wiring the constructors is the functor's job, so a leaf constructor never accumulates a field for every ancestor category.

**D14 (08-26, corrected 08-28). One chain per mathematical kind.** Every category is a `Cat().ObjectType`. Every object of a category is a point `* -> C`, hence a `Cat().ElementType` and a `C.ObjectType`. An element of `X in C` is a point `1_C -> X` and uses `C.ElementType`. A morphism of `C` is a `Mor(C).ObjectType`.

**D55 (08-26). Drop `Ar(C)` and every arrow and hom spelling.** Define `Mor(n, C)` as the category of `n`-morphisms of `C`. Almost every category here is a 1-category, so `Mor(0, C) = C` with `C.ObjectType`, and `Mor(1, C) = Mor(C)` with `C.MorphismType`. Hence categories are `Mor(0, Cat)`, functors are `Mor(1, Cat)`, and natural transformations are `Mor(2, Cat) = Mor(1, Fun)`. `Mor(C)` is always a category: its objects are the 1-morphisms of `C` and its morphisms are the 2-morphisms.
Drop hom and arrow notation everywhere.
This supersedes the `Ar`/`Hom` spellings of D11.

**D56 (08-26). Eager, and fail fast and loudly.** Declaration order in `structure_functors()` controls preference.

**D57 (08-26, corrected 08-28). The point functor regards a category as an object.** It is the inclusion of the one-object category `{C}` into `D`. `D`'s object methods propagate to the category `C` itself.
`D`'s element methods become `C`'s object methods because the points `* -> C` are exactly the objects of `C`. Morphisms of `C` do not receive that element surface.
This is how `Ordinals()` receives semiring operations.

**D58 (08-27). What a functor is for.** In Sage you declare your supercategories but never say *how* to construct an object or morphism of a supercategory from one of yours.
That is the entire purpose of a functor: it transports literal constructor data.
You choose the categories you map into, you understand exactly their constructors, you supply constructors on your own objects and morphisms, and then it is your job as the leaf writer to take one of your constructions and produce the data one of the target's constructors consumes.
If your modules are built from `rho: R -> End_Set(X)` and you want set operations, you write the functor that takes your `M` and produces the data the `Sets()` constructor accepts.
The leaf teaches the repository how to produce a set from a module.

**D59 (08-26). Morphism properties, not arrow properties.** `Mor(C).Monomorphisms()` and its relatives.
For `C = Cat` you need at least `Mor(Cat).Full()` and `Mor(Cat).Faithful()`, so that a downstream category can declare minimal wiring — `FiniteSets` defines one standard inclusion into `Sets()` for its `structure_functors()`, doing what Sage's `super_categories` would do.

**D60 (08-26). A natural transformation's components are an indexed family.** Almost every category in use is infinite, so a tuple of components is absurd.
Model it as an assignment `X |-> eta_X`.

**D61 (08-27). Name the functor property that licenses common-ancestor tracing, and cite it.** There is a property `P` of functors along which tracing a common ancestor is allowed, and it must be the well-known citable one, not a heuristic recorded after the fact.
"Embedding" is colloquial with no formalized definition.
"Subcategory" is colloquial too: if the intended notion is a monomorphism, say so.
"Inclusion functor" is not a term.
Record the precise citable definitions and the decisions that follow from them.

## Elements

**D15 (08-23). "Shared elements" is not a concept.** Every category has an `ElementType`, including a dynamically constructed one such as `C.Products()`. Element classes inherit exactly as object classes do, and may add methods: the element type of a product is also an element of a set and may carry `x.factors()`. An element of a finite set is not "just an element of a set" — it is `FiniteSets().ElementType`, which extends `Sets().ElementType` when the wiring is correct.

**D16 (08-26, corrected 08-28). What an element is.** A Sage element is implicitly a pair `(X, x)` with `X = x.parent()`. Categorically, an element of `X in C` is a point `1_C -> X` from the terminal object.
This is what `C.ElementType` implements.
A morphism `T -> X` with general domain is a generalized element and stays in its morphism or slice category.
For `C in Cat()`, points `* -> C` are the actual objects of `C`, so `C.ObjectType` inherits `Cat().ElementType`. An `R`-point of a scheme is generalized unless its domain is terminal.

**D17 (08-26, corrected 08-28). Every functor transports points through its morphism action.** For `F: C -> D` and `t: 1_C -> X`, the morphism action gives `F(1_C) -> F(X)`. A declared comparison `1_D -> F(1_C)` gives the point of `F(X)`. A generalized element `T -> X` maps to `F(T) -> F(X)` and remains generalized.
The functor carries no independent element callback.

**D62 (08-27, corrected 08-28). Points and generalized elements are distinct.** A point of `X` is `p: 1_C -> X`. A generalized element is `p: T -> X`. For `X = C in Cat()`, a point `* -> C` is an actual object of `C`, while a functor `T -> C` is a generalized element.

## Predicates, containment, and assumption

**D18 (08-22, corrected 08-28). There is no decidability boundary.** Every mathematical truth question returns an applied proposition. Every other mathematical query that is not total and exact on its full declared domain returns an applied predicate with an exact result category. Only `ask()` returns `True`, `False`, an owned result, or Sage `Unknown` (`01a048f6-e3f5-7e42-be2a-1f60f70ac23e` 2026-08-28T17:24Z, 2026-08-28T17:25Z).

**D19 (08-22, corrected 08-29). Category containment and the public predicate application ask one proposition.** The kernel derives `X.is_finite()` from the property declaration owned by `Sets().Finite()`. It returns that category's containment proposition. `ask(X.is_finite())` evaluates it. Python containment asks the same proposition and is only a forced two-valued admission boundary (`4544eba5` 2026-08-28T12:00Z; `01a048f6-e3f5-7e42-be2a-1f60f70ac23e` 2026-08-28T19:51Z).

**D20 (08-24). Every propositional method returns a proposition.** Never a bool, never an `Unknown` in its place.
Anything that would need `Unknown` routes through `assume`/`ask`/`.assume()`. Containment in a category is always a possibly compound proposition, declared once as part of the category's definition — the kernel wires `FiniteSets` to be reachable as `Sets().Finite()` and lets it declare a membership proposition, and `__contains__` follows from that.

**D21 (08-24, corrected 08-28). Construct into the strongest subcategory you can.** A named construction can return its result through the strongest property-subcategory constructor that its mathematics establishes.
The public predicate remains proposition-valued and keeps its one category-owned definition (`4544eba5 2026-08-28T12:00Z`).
Individual named objects are one-object categories: `QQ` is `{QQ}` with functors into countable sets, posets, and fields.
`Fields().Countable().PartiallyOrdered()` should be nearly automatic, with Sage's `with_axiom` as the model: if any category defines a property subcategory, any subcategory can narrow itself the same way.
Defining `FF_p` as a one-object category parameterized by `p` must never require proving finiteness by enumeration.

**D22 (08-24, corrected 08-28). Assumption is a shortcut for construction.** `assume(X.is_finite())` and `assume(f.is_injective())` refine into the corresponding property category.
Python containment asks the same proposition and returns its Boolean decision, so it is not the proposition passed to `assume()` (`4544eba5 2026-08-28T12:00Z`).

**D23 (08-24). Property refinement strengthens the category of the same value.** It is not transport into a second implementation, and it is not a family of admission constructors.
Each property category owns one constructor that trusts its defining property.
These APIs must not exist: `monos.checked(...)`, `monos.from_hypothesis(...)`, `monos.from_theorem(...)`, `construct(..., check=True)`. Direct construction, global assumption, exact computation, and construction-owned mathematics all converge on that one constructor.

**D24 (08-24). Backend code does not call `assume()`.** The Sage or SymPy session owns the global assumption context, and a notebook user may write into it.
Internal code already knows the category in which to construct its result, and constructs there.

**D25 (08-24, 08-25). Theorem-backed construction is declaration, not computation.** No Python code can establish that `RR` is uncountable, and running a monotonicity check on `n |-> n^2 : NN -> NN`, or a totality check on `{1, ..., 10^10}` with its natural order, is absurd.
A specific named constructor owns its theorem, and its controlled input data is what makes the theorem applicable: `square_morphism_on_naturals()`, `componentwise_product_order(diagram)`, `finite_total_order_from_enumeration(enumeration)`. A generic `from_theorem(value, owner)` remains invalid, because a registered owner is an opaque token that identifies no construction.
A public total-order constructor accepting an arbitrary relation is likewise invalid; a constructor from an enumeration builds the guaranteed-total relation itself.

**D26 (08-25). The repository never proves or certifies category theory.** That is hopeless in Sage and belongs in a language like Lean.
The categorical core is meant to be independently auditable by mathematicians, so it encodes its needs in standard category or homotopy theory — nLab, the Stacks Project, Kerodon, textbooks, arXiv papers — and stays mathematically legible.
A code writer forms constructions into the correct subcategory as the way of asserting a theorem, with a citation on the construction line.

**D63 (08-26). `__eq__` returns a predicate.** So `a == b` can evaluate to `Unknown`, and that is fine.
Where a Boolean is forced, repository code writes `decision = ask(x == y); assert decision is not Unknown`. Points are chosen data `x: 1 -> X`.

## Cardinality

**D27 (08-22). Never enumerate a set to compute a property.** Always consider what happens for `{2, 4, ...}` or `{1, ..., 10^10}`. Enumeration is a dead-last fallback for when cardinality is required, the set is known finite, and there is no other way.
Usually cardinality is supplied at construction or derived from a known relationship: `{n in NN | n <= 100}` is finite without listing anything.
Enumeration can be a fine first approximation in a specific algorithm, but it does not belong on a main path and should warn loudly.

**D28 (08-22, 08-23). Cardinals compare by ordinary syntax.** `==`, `<=`, and the rest, against ordinary integers.
You never extract a cardinal's "value".

**D29 (08-24, amended by D62). `cardinality()` never uses absence for unknown mathematics.** Representing an undecided cardinality by `None` is a defect.
An image receives the domain's cardinality only when the map is established injective; a constant function is the counterexample.

**D30 (08-25). Cardinal arithmetic is the categorical operation.** The coproduct in the category of cardinals is exactly cardinal addition; the product is exactly cardinal multiplication.

**D64 (08-26, corrected 08-28). There is no unresolved cardinal object.** `X.cardinality()` returns an applied predicate with result category `Cardinal()`. `ask(X.cardinality())` returns an owned cardinal when an exact route applies and Sage `Unknown` otherwise. The same architecture applies to every mathematical query that is not total and exact on its full declared domain. Cardinals contain no separate unresolved value (`01a048f6-e3f5-7e42-be2a-1f60f70ac23e` 2026-08-28T17:24Z, 2026-08-28T17:25Z).
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

**D34 (08-25, corrected 08-29, `01a048f6-e3f5-7e42-be2a-1f60f70ac23e` 2026-08-28T18:48Z). The `Cat` level owns the construction vocabulary.** It supplies `C.Subobjects(X)`, `C.Superobjects(X)`, `C.CoveringObjects(X)`, and `C.CoveredObjects(X)` for every `X in C`, together with `C.Products()`, `C.Coproducts()`, `C.Limits(I)`, and `C.Colimits(I)`. For a product category `P`, an object of `Cat().Subobjects(P)` answers `product_projection(i)`. Slice and coslice categories and their fibrations to the varying object supply the fixed-object constructions.
General projections exist for any subcategory of a product category, `proj_i: (X_1, ..., X_n) |-> X_i`; a coslice has projections to both `X in C` and `f in Ar(C)`, and composing with the source and target projections of `Ar(C)` gives the rest.

**D35 (08-25). The operators are defined once.** `Y ** X` is `Hom_C(X, Y)`, `X * Y` the product, `X + Y` the coproduct, `X @ Y` the biproduct.

**D67 (08-26, corrected 08-28). Scope of the current foundation.** Complete `Cat`, functor categories, the `Mor(n, C)` tower, universal constructions, the method compiler, and the owned `Sets()` category before adding later theories.
Tests can use small vertical examples to establish this foundation.
Those examples do not add their theories to the implementation surface (`01a029f8 2026-08-22T16:48Z`).

**D68 (08-26). Diagram categories are the workhorse.** Provide machinery for finite diagram categories, specializing to filtered ones such as explicit sequences, since ninety percent of downstream code writes `X * Y` or a product over a list.
Do not over-specialize: finite sequence-indexed products alone hit a wall at the adeles.
Do not over-generalize either: ten times the code for the ten percent needing arbitrary diagrams is the opposite error.

**D69 (08-26). The binary operators live at the `Cat` level.** For categories they do the obvious thing through `ObjectType`; objects of categories receive defaults through `Cat().ElementType`, deferring to their own category for its products and coproducts.
That is where the assertion that both operands lie in the same category belongs.
`X * Y` is never silently cast into a product category: when you want that, call the product's own constructor, `(C * D)(X, Y)`.

**D70 (08-27). `X ** Y := Hom_C(Y, X)`, always, and `Cat` owns it.** Not `Sets()`. The same way `X * Y` is always a product in `C`. Common-ancestor tracing has to be resolved by a named mechanism: `{1, 2}` is in `Sets().Finite()` and `ZZ` is in `Sets().Countable().TotallyOrdered()`, so a result may trace as far back as `Sets()` and may refine again.

**D71 (08-26). Canonical objects are included.** `1 = *`, the empty object, simple horns with their boundaries, simplices, and walking structures in `Cat`; the empty set and `[n]` in `Sets()`. Any canonical representing object the constructions need.

## Diamonds and identity

**D36 (08-26). Size is not modeled.** Assume `Cat` is bicomplete and biclosed, so `[C, D] := Hom_Cat(C, D) := Fun(C, D)` is a category under whatever definition is in play.
This is an engineering convenience to be formalized later.
The point is that `Monoids * Rings`, `Fun(Monoids, Sets) * Fun(Rings, Graphs)`, and `X * Y` for two sets all use one interface and one semantics.

**D37 (08-26, corrected 08-28). A structured source instance carries one initialized state for each inherited target class.** For almost every algebraic category there is one set from which the structured object is built.
Every selected path to `Sets()` must supply that same set as constructor data for the inherited `Sets().ObjectType` state.
`Free_R({1, 2})` and `Free_R({a, b})` are distinct modules and must never be identified: the second's generators are formal symbols while the first's inherit structure as ring elements.
This constructor agreement does not identify functor images.
Each named functor constructs and caches its own public image, and two functors with the same endpoints can return different objects (`4544eba5 2026-08-28T12:00Z`; `4544eba5 2026-08-28T12:18Z`).

**D38 (08-26, corrected 08-28). Set equality is a proposition, not a procedure.** The image in `Sets()` of `Free_R(S)` can be created by fiat, from a membership rule and a cardinality rule; nothing enumerates it and there is no extensional description to compare.
`X == Y` is `True` by identity and otherwise `Unknown`, unless a cited theorem or an exact computation decides it.
The compiler never uses set equality to merge public functor images.
Its construction obligation is only that every selected path to one target class supplies the same constructor datum (`4544eba5 2026-08-28T12:18Z`).

## Leaf discipline

**D80 (08-28, `77631b59` 2026-08-28T17:35:47Z). `Cat` declares; a downstream category implements.** `Cat` declares points. It declares `Sets`. It declares constructions such as magma objects in a category. A downstream category then *is* the implementation of a category the kernel declared.
This is D77.6 generalized. `FiniteSets` already declares itself the implementation of `Sets().Finite()`; the same connection carries a leaf declaring itself the implementation of a kernel-declared base category. Declaring a category and implementing it are two acts, and only the second is a leaf's.

**D81 (08-28, `77631b59` 2026-08-28T17:35:47Z). Imports flow from the kernel into the leaves, never backwards.** No kernel module imports a leaf module.
This is the executable form of the Philosophy's information-flow rule, and it is what D80 is for: a generic construction stated over `Sets` uses the declaration the kernel holds, and never reaches into the set implementation to obtain it. A kernel module that imports a leaf has taken that leaf's mathematics into the kernel, which is the defect the rule names whether or not the result works.

**D86 (08-28, `77631b59` 2026-08-28T19:03:51Z, corrected 2026-08-28T19:12Z). An identity is named by the operation it is an identity for, and the identity morphism is one of them.** `identity()` unqualified says nothing: `ZZ.identity()` could be `0` or `1`. An identity comes from the magmatic structure, which splits into the additive and multiplicative axiomatic subcategories, so the names are `additive_identity()` and `multiplicative_identity()`.
Sage draws the same split with the same mechanism: `AdditiveMagmas.AdditiveUnital` supplies `zero()` and `Magmas.Unital` supplies `one()` (`sage/categories/additive_magmas.py:599,696`, `sage/categories/magmas.py:461,482`, inspected 2026-08-29).
The identity morphism is not a second notion beside these. Composition induces a multiplicative monoid structure on `End_C(X) = Mor(C)(X, X)`, and `1_X` is that monoid's multiplicative identity: `End_C(X).multiplicative_identity()`, which is what D84 spells `End_C(X).one()`. `identity_morphism()` is therefore an alias, and D85 keeps aliases out until after version 1, so it should not exist yet.

**D83 (08-28, `77631b59` 2026-08-28T18:10:28Z). A property subcategory contained in another is a subcategory, not an implication.** `Mor(C).Isomorphisms()` is a full subcategory of `Mor(C).Monomorphisms()` and of `Mor(C).Epimorphisms()` simultaneously, the same way `Sets().Finite()` is a full subcategory of `Sets().Countable()`. "Finite implies countable" is set-theoretic logic and has no category-theoretic formulation.
The containment is the statement, and the monomorphism presenting it is what the declaration records. Nothing induces it from a relation between predicates.
This corrects the existing vocabulary rather than adding to it. `specs/functor.md` currently makes the implication primary — "These implications induce the corresponding monomorphisms between property subcategories" — and `POL-CAT-090`, `POL-CAT-091`, and `specs/undecidable-properties.md` carry the same wording where they mean containment. Propositional implication remains what it is for ordinary propositions, which compose through SymPy; it is not what relates two property subcategories.

**D82 (08-28, `77631b59` 2026-08-28T18:00:33Z). `Cat` holds a mathematical planning surface.** It declares the categories the repository expects: points such as `Sets`, `Posets`, `NN`, and `ZZ`; construction functors such as `MagmaObjects(C)`, `MonoidObjects(C)`, and `RingObjects(C)`; and the specializations those give, `Monoids := MonoidObjects(Sets())`.
Every declaration is a functor into `Cat()`, and the parameter it takes is that functor's domain; a category with no parameter is the terminal-domain case. A declaration no leaf implements is a work queue for leaf writers, auditable against, and never a check that fails a build (`AGENTS.md`, "Tests"). [Declared categories and their implementations](functor.md#declared-categories-and-their-implementations) states the mechanism.

**D84 (08-29, corrected 08-29, `01a048f6-e3f5-7e42-be2a-1f60f70ac23e` 2026-08-28T18:36Z, 2026-08-28T18:48Z, 2026-08-28T19:09Z). Identity morphisms and object-dependent constructions keep their mathematical owners.** For `X in C`, the identity morphism is `End_C(X).one()`, the unit of the endomorphism monoid on `Mor(C)(X, X)` under composition. The inherited fixed-object construction methods are `C.Subobjects(X)`, `C.Superobjects(X)`, `C.CoveringObjects(X)`, and `C.CoveredObjects(X)`. The ambient category in the call fixes the role of `X`; the same value can occur in more than one category. `Sets().Subobjects(X).from_predicate(predicate)` constructs the set subobject selected by a predicate.

**D85 (08-29, corrected 08-29, `01a048f6-e3f5-7e42-be2a-1f60f70ac23e` 2026-08-28T18:48Z, 2026-08-28T18:49Z, 2026-08-28T19:05Z, 2026-08-28T19:09Z). Uniform category operations are inherited methods.** `Cat().ObjectType` defines each method once, and every category inherits it through the implementation-class hierarchy. In particular, its fixed-object methods return the monomorphism or epimorphism property subcategories of slices and coslices. A leaf supplies only its specialization, realization, and new mathematical constructors. Receiver-specific and leaf-specific convenience aliases begin after version 1.

**D87 (08-29, `01a048f6-e3f5-7e42-be2a-1f60f70ac23e` 2026-08-28T19:25Z). A construction specification follows the category graph.** `Cat` owns the shape, index, diagram, cone or cocone, defining morphisms, universal morphism, and every operation determined by that categorical construction. A leaf specification links to that contract and states its mathematical delta: the added leaf structure, its membership and equality predicates, its cardinality or other leaf operations, its exact algorithms, and its private engine realizations. A public name identifies the exact mathematical object or morphism it returns. One generic construction has one inherited public surface.

**D88 (08-29, corrected 08-29, `01a048f6-e3f5-7e42-be2a-1f60f70ac23e` 2026-08-28T19:38Z). Version 1 exposes defining data and composes public operations.** A construction supplies its retained mathematical data, such as the indexed family returned by `P.product_factors()`. A derived query uses ordinary composition: apply `X_i.cardinality()` to those factors. This rule applies to the complete specification surface, not only to construction queries. An operation expressible as one or two lines of public compositional code receives no additional method in version 1.

**D89 (08-29, `01a048f6-e3f5-7e42-be2a-1f60f70ac23e` 2026-08-28T19:51Z). Property applications come from property subcategories.** When `is_X()` asks whether a value has property `X`, the property subcategory owns the containment predicate. Its `predicate_name` gives the exact public spelling, and its `predicate_owner` gives the largest meaningful ambient implementation class. The kernel derives the public application from that declaration. A leaf or operation specification does not define a second method contract for the same question.

**D90 (08-29, `01a048f6-e3f5-7e42-be2a-1f60f70ac23e` 2026-08-28T20:21Z). Algebraic structures expose their standard mathematical syntax.** A magma constructor receives its chosen binary law. The public element surface applies that law through `+` in the additive subcategory or `*` in the multiplicative subcategory. The specification does not require an object-level accessor for the stored law or prescribe its private representation. A module action is different: the action morphism is mathematical data that applications can construct and inspect.

**D91 (08-29, `01a048f6-e3f5-7e42-be2a-1f60f70ac23e` 2026-08-28T20:21Z). Property refinement and representation construction are distinct.** One property subcategory has one trusted same-object refinement route. This does not limit its ordinary constructors. A finite-set category can accept lists, tuples, Python sets, SymPy sets, Julia sets, GAP sets, and other supported representations through as many exact constructor routes as its mathematics requires.

**D92 (08-29, `01a048f6-e3f5-7e42-be2a-1f60f70ac23e` 2026-08-28T20:21Z). Active prohibitions remain explicit.** A specification keeps prohibitions that exclude known architectural failure patterns. Such a prohibition is a current contract, not a record of removed implementation history.

**D77 (08-28). The leaf writer's contract is a closed list.** The kernel exists to make this list short, so anything a leaf must supply beyond it is a kernel defect, not a leaf obligation.

1. `ObjectType`, `ElementType`, and `MorphismType`, as nested classes.

2. Constructors: how another mathematician builds objects of your category, in the terms your mathematics uses.

3. Functors: how one of your constructions produces the data another category's constructor consumes.
   This is what replaces `super_categories`, and it is where you say which structure you inherit.

4. Which axiomatic subcategories are available.
   Finiteness is declared once as `C.Finite()`, and any category `D` with a functor into `C` can then declare `D.Finite()`, exactly as Sage's `with_axiom` propagates an axiom down the graph.

5. For a property-based subcategory, its containment predicate.
   That predicate is the whole declaration; membership, refinement, and `ask()` follow from it.

6. The wiring that makes a category the concrete implementation of such a subcategory.
   `FiniteSets` declares itself the implementation of `Sets().Finite()` and adds the methods that finiteness makes available; that is Sage's `_base_category_class_and_axiom` shape (D55, `POL-LEAF-059`).

The list is what a mathematician writes.
Everything else - inheritance, dispatch, construction threading, caches, class building - is the kernel's, and it is the kernel's precisely so that this list stays this short (D04).

**D39 (08-22). What a leaf implementer supplies.** Functors to known categories that show how to feed the new category's objects into an old category's constructor, plus a constructor for the minimal delta that defines the leaf.
`Modules(R)` built from an action `rho: R -> End(X)` declaring `Sets` as a supercategory needs only the functor that uses `rho` to extract `X` and feed it to the `Sets` constructor.
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
Trace the whole implementation path: how the kernel defines products, how they propagate through categories and presentations and selected functors, so that the leaf supplies only its delta.

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

*The arrow is where the leaf writer's work lives.* Everything the framework supplies is a consequence of stating the map: the inheritance, the constructor threading, the construction lifts.
An accessor that hands back an ancestor value is a way to obtain that value without stating the map — so the mechanism never runs, and the leaf ends up reimplementing what it should have received.
That is a bypass around the selected-functor mechanism.

*And it is what makes the code auditable.* A mathematician can read `U_A(M)` and check it against the definition.
Reading an accessor that omits the functor endpoints requires opening the implementation to find out which category was meant, which is programming rather than mathematics, and it forfeits the reason the layer exists at all (D03).

The same philosophy governs every other implicit choice, not just this accessor.
A coercion, a default ambient category, or a walk to a "common ancestor" is the same defect wherever it silently selects a category — which is why common-ancestor tracing has to run along a named, citable property of functors and never a heuristic (D61).

**D76 (08-28, corrected 08-28). Distinguish preservation from equality on the nose.** A functor `U` preserves a product when the canonical comparison morphism `U(prod X_i) -> prod U(X_i)`, induced by the cone `(U(pi_i))`, is an isomorphism.
A lifted construction can require more: its chosen apex and defining morphisms can map to the chosen ambient construction on the nose.
State that stronger equality where the construction needs it.

This construction-level equality does not identify the public images of arbitrary named functors (`01a03c6a 2026-08-26T07:36Z`; `4544eba5 2026-08-28T12:18Z`).
Inheritance requires only that selected paths to one target class supply the same constructor datum (D37, D38). A leaf that lifts an ambient construction builds on the ambient apex and retains its defining morphisms; the compiler has no preservation registry.

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
There is no bare object to equip when the object is already the pair: a subobject is an object together with a monomorphism, so `Subobjects(X)` is the name (D74). And a construction family that already retains its construction is the equipped form, so it needs no adjective — that, and not an absence of alternatives, is why an extra product-family adjective was redundant, since a product has many isomorphic siblings and the repository simply keeps the one it built.

**D74 (08-26, corrected 08-29, `01a048f6-e3f5-7e42-be2a-1f60f70ac23e` 2026-08-28T18:48Z, 2026-08-28T19:25Z). A subobject is an object with a monomorphism, and restricting structure to one is leaf work.** There is no second notion and no separate name for a representative; the equivalence class matters only when deciding whether two subobjects are equal, which is a predicate. For `X in C`, the one fixed-object category is `C.Subobjects(X)`.

For a poset `P` presented by `(X, R)`, `Sets().Subobjects(X).from_predicate(predicate)` constructs only a set subobject. `PartiallyOrderedSets().Subobjects(P)` specializes the inherited subobject construction by retaining the restricted order and monomorphism in `PartiallyOrderedSets()`. The ordering subtree decides the strongest established order category of the result.

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

**D50 (08-23). Never write a method that only fails.** No body that is `assert False`, `return NotImplemented`, or a raise.
That hides a missing capability from static checkers and surprises the user at runtime; the point is a uniform interface.
A `cardinality()` that raises is worse than no `cardinality()` at all.
Use abstract methods or expose the method only on the category that owns the capability.
When a mathematical query is not total and exact on its full declared domain, return an applied predicate and evaluate it with `ask()`.

**D51 (08-23). Do not golf type checkers.** They are a signal; the architecture and philosophy are the arbiters of correctness.
The compiler should be strong enough to teach mypy about the functorial construction, but a very dynamic process may exceed what mypy can follow.
Type-checker plugins are legitimate, as is static generation — manifests, statically constructed types, stubs — regenerated on commit, test, push, or version bump, since the repository does statically encode all its intended relations at any given time.

**D52 (08-24). Never use optional arguments.** Write total methods and separate, specifically named constructors.
A set constructor that can accept a cardinality by fiat does not make cardinality optional with a default; it is total in cardinality, with `construct_uncountable_set`, `construct_countable_set`, and `construct_finite_set` split out.

**D53 (08-23). Prefer the mathematically flavoured construction.** `pairwise` over `zip`, and generally: look for packages and dependencies that improve the mathematical flavour of the code, and propose them when the idea surfaces.

## What the documents are for

**D54 (08-22).** `CONTRIBUTING.md` holds general principles and patterns grounded in examples, and may hold specific observed antipatterns once they recur enough to matter.

Specifications are forward-facing.
They catalogue the desired functionality, nail down the public API, and may hint at internal strategies.
A specification must be explicit about the expected selected functors — whatever stands in for `super_categories`. It separates, and does not repeat, the methods expected to arrive by inheritance, keeping one source of truth, though naming a few to ground an example is fine.
A lattice specification should say that it mentions no cardinality, and that cardinality arrives compositionally along a chain of functors landing in `Sets()` — not from a direct functor to `Sets()`.
