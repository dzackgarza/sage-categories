# Agent instructions

## Project purpose

`sage-categories` is a foundational category framework for Sage-based mathematics.
It is not an application repository or a domain-specific research corpus.

These files govern substantive work. Read the relevant sections for the active task:

- `README.md` defines the goal and mathematical philosophy.
- `CONTRIBUTING.md` is the coding-policy index. Its `POL-*` identifiers are stable review references.
- `specs/decisions.md` records the architectural decisions the owner stated in working
  sessions, with dates, above a Philosophy section giving the reasons they follow from.
  It is the source of the architecture. When a specification, a policy row, a plan, or a
  report disagrees with it, that other artifact is the defect. Read the Philosophy first:
  a rule you cannot derive is a rule you will replace with a synonym, which is how every
  previous rebuild drifted. Never re-derive a decision from source code — the source was
  written by the process those decisions correct.

## Policy and specification traceability

Cross-reference every review and every work unit against the governing policies and
specifications. This rule has no exceptions.

Before any edit, implementation decision, diagnosis, or review verdict:

- identify the exact applicable `POL-*` identifiers in `CONTRIBUTING.md`;
- identify the exact applicable specification files and sections;
- read those sources together before interpreting code, plans, reports, or runtime
  behavior.

During work, map every material design choice and implementation boundary to those
references. During review, map every finding, acceptance statement, rejection, and
trajectory judgment to them. An uncited architectural judgment is incomplete.

Do not evaluate code from generic software practice, a commit subject, an agent report,
a local test result, or one TODO item in isolation. These can supply evidence. They do
not replace the governing policy and specification model.

When a TODO, plan, report, or implementation appears to conflict with a policy or
specification, resolve the meaning from the governing sources before acting. Preserve
all stated distinctions, examples, exceptions, construction boundaries, and proof
boundaries. Do not compress a specific rule into a nearby general slogan.

Apply `POL-DOC-010` before adding mathematical vocabulary to an implementation plan.
Apply `POL-DOC-011` before reporting a contradiction. When the task reconciles past
decisions, apply `POL-DOC-012`. Apply `POL-DOC-013` to every executing plan.

If no policy or specification governs a material decision, surface that documentation
gap. Do not invent a local convention and present it as repository architecture.

The package owns its mathematical category graph and public API.
Its category-owned implementation classes can combine Sage, SymPy, GAP, Julia packages,
Singular, Macaulay2, Cython, shell programs, imported research software, and bespoke
algorithms. These private engines supply computations. They do not own the mathematical
API or category graph.

## Repository state and task entry

This repository is already initialized.
The project vault is available through `.agents` and `.hermes`.
Do not check initialization, rerun initialization, rebuild project records, or probe vault availability.
Do not load or run `project-initialization` unless the task changes the repository's initialization state.

Treat the current working tree as the source of truth.
Inspect current files and current runtime behavior.
Do not use Git history to decide what the repository contains or whether current code is correct.

Read Git history only when the user or active plan asks about past work, past decisions, or provenance.
Otherwise, do not inspect logs, blame, ancestry, old branches, commit messages, or prior revisions.

Start repository inspection with `tree` at the smallest useful depth.
Then read the exact target files and focused sections of their immediate owners.
Use focused `rg` queries.
Do not dump broad surveys, whole subtrees, generated sources, or large search results into context.

When chat supplies a clear plan, directive, or task report, execute its first concrete task immediately.
Inspect only the files and dependencies needed for that task.
Do not re-plan, audit the repository, inspect history, or initialize tooling.

For a clear plan, limit Git use to current-state safety and completed work.
Check the target file, create a checkpoint when needed, stage exact files, and commit.
Do not change branches, rebase, stash, cherry-pick, or otherwise manipulate Git unless the task requires it.

## Current implementation scope

Work in mathematical dependency order:

1. `Cat`, functor categories, sequence products and coproducts, natural transformations,
   and natural isomorphisms.
2. The `Mor(n, C)` tower, subobjects of products, and their component functors.
3. The method compiler for `ObjectType`, `ElementType`, and `MorphismType` inheritance.
4. The owned category `Sets()` and its universal constructions.

The current implementation surface ends at `Sets()`.
Complete this foundation before extending the theory graph.

Use later structures only as vertical acceptance examples.
An algebra's cardinality must eventually come from its structural path to `Sets()`.
A lattice isometry must eventually pass through module homs to set homs.
These examples test the foundation; they do not authorize implementation of algebras, modules, or lattices now.

The `Mor(n, C)` foundation includes:

- `Mor(C)` and the commuting-square category `Fun([1], C)`;
- fixed-endpoint categories `Mor(C)(A, B)` and endomorphism categories;
- monomorphism, epimorphism, isomorphism, and automorphism categories;
- cores and wide subcategories;
- slices, coslices, subobjects, superobjects, covering objects, and covered objects.

Build slices and coslices after sequence products, subobjects, `Fun([1], C)`, and its
evaluation functors `ev_0` and `ev_1`. Their selected functors are composites of these
general constructions.

## Mathematical structure as implementation compression

A short mathematical correction can expose a missing foundation rather than a missing method.
Unfold the structure that makes the correction true before adding a local operation.

For example, a product of sets must receive `cardinality()` because it is an object of `Sets()`.
The product construction supplies its projections and its placement in `Sets()`.
The method compiler then exposes the operation owned by the set implementation.

Adding `cardinality()` directly to a product class would preserve the missing relation.
It would also create another local task for coproducts, limits, subobjects, and every later construction.
The categorical foundation makes those operations consequences of one structure.

This is the main form of implementation compression in this repository:

- one category owns a generic operation;
- one functor states each change of structure;
- one universal construction retains its defining morphisms;
- the compiler turns those declarations into a direct public surface.

At every design, implementation, and review step, answer this question:

> What generic categorical mechanism makes every leaf state only its new mathematics?

Use the answer to determine code ownership, theorem ownership, call paths, and public methods.
Do not derive the architecture from the nearest failing method or current Python layout.

Trace the complete implementation path before editing any part of it.
For a product, trace all of these parts:

- the kernel definition of products and their universal data;
- the construction family and its monomorphism into the ambient category;
- the constructed object, its projections, and its universal maps;
- propagation through selected functors;
- method compilation and inherited public operations;
- the leaf theorem or structure that adds the new mathematical delta.

Perform the same trace for objects, elements, morphisms, arguments, and results.
The trace must explain the final public call without leaf-level engineering wiring.
A missing step is a kernel, construction, functor, or compiler defect.
Repair that owner instead of adding a leaf workaround.
Use `POL-CAT-079` through `POL-CAT-080`, `POL-LEAF-056`, `POL-KERNEL-025`,
`POL-FUN-023`, and `POL-API-023` as the stable review references.

Prefer a foundational correction when it removes an entire family of apparent method tasks.
Do not preserve a mistaken architecture with a cheaper local implementation.

Kernel complexity is justified only when it removes repetition from theory code.
The theory layer must read like the mathematics it implements.
A new category should state its new data and immediate selected functors, then inherit the rest.

A leaf category must state its mathematical data, operations, selected functors, constructors, and lifts.
Stop local work when a leaf contains generic reflection, dispatch, route traversal, transport, cache ownership, wrappers, or public backend selection.
Treat that wiring as a kernel or backend-boundary defect.
Repair the owning foundation instead of polishing, moving, or preserving the wiring in a leaf workaround.

The category-owned implementation class is a polyglot algorithm firewall.
Its ordinary method can use one private engine, several engines, or an imported research
program. It can select an exact algorithm from the semantic construction and combine
engine results. This is leaf implementation, not categorical routing.

Use a mature engine construction whenever it discharges logic that would otherwise be
implemented locally. Do not require one engine to represent the whole object or compute
every operation. Do not expose engine selection, engine objects, or engine method names
through the public API.

Foundational categories remain valuable before later theories use them.
Their value is the mathematical structure they make expressible, not their current number of callers.

## Mathematical judgment

Treat a precise user description as a proposed mathematical model of the code.
When the live implementation lacks the named category, functor, morphism, or universal property, surface that discrepancy.
Do not substitute a nearby class, method, constructor, or data record.

Category theory is not a metaphor in this package.
A functor must map objects and morphisms.
A subobject must include its monomorphism.
A universal construction must include its universal morphisms.
A computation-engine value must be used to construct an owned mathematical object.

Treat `Cat` as the abstract universe specified by the repository's declarations.
Apply `POL-MATH-043` before assigning it a foundation or realization.
Apply `POL-MATH-044` before deriving any property from a borrowed mathematical name.

One false foundational assertion invalidates each downstream conclusion that uses it.
When such an assertion appears, rederive the architecture from the mathematical definitions and the live code.
Do not optimize a local patch, diagnostic count, or passing specimen built on the false premise.

Implementation obstacles do not change mathematical ownership.
A recursion, type error, slow path, or failing test is a fact about the implementation.
Fix that implementation fact without moving an operation to the wrong object or weakening its type.

Predicates follow their definitions and their available algorithms.
Return `Unknown` when the implementation cannot determine a result.
Do not replace missing knowledge with a fabricated Boolean answer.

A predicate strictly generalizes a Boolean, so a Boolean is honest only where the
question is two-valued by construction: a record of what was retained, the presence of a
chosen enumeration. Every other question is a proposition, and `ask()` decides it.

Category containment owns predicate evaluation. `is_finite()` is declared once, on
`Sets()`, and the proposition it applies is membership in `Sets().Finite()`. The class
that implements `Sets().Finite()` supplies the defining predicate of that membership,
`cardinality() < aleph_0`. Every category with a selected functor to `Sets()` receives
`is_finite()` from that one declaration, and a poset is finite exactly when its underlying
set is. Placement in the subcategory is a fast positive route, because a value that entered
through the property constructor already satisfies the predicate. Placement is never the
definition of membership. Ask containment; do not reach for a category's predicate object
and apply it at a use site.

Decide an equality with `ask(a == b)`. On an owned value `==` returns a proposition, so
its result decides nothing when consumed as a truth value, compared by identity against
`True`, `False`, or `Unknown`, or folded through `all`, `any`, `and`, `or`, or `not`. A
site whose operands happen to be engine values today is a latent defect: nothing fixes
the datum type. Treat "this comparison cannot be `Unknown` here" as a claim that needs
evidence.

Refine a result into a property subcategory only when an exact computation or a cited theorem establishes the property.
Otherwise, return it in the strongest category that the available mathematics establishes.
Do not create certificate classes, proof records, or prose fields to simulate this refinement.

Open and inspect a mathematical source before adding a definition or citation.
Record the exact theorem, section, table, or page that supports the statement.
Do not reconstruct a definition, citation, or expected value from memory.

Prefer standard categorical constructions and established algorithms over local encodings.
If the current vocabulary cannot state the general mathematical object, treat that absence as the finding.
Extend the foundation instead of hiding the gap inside a special case.

## Core categorical architecture

A category owns its implementations and constructors.
A functor constructs an implementation in another category.

For each category `C`:

- `C.ObjectType` implements objects of `C`.
- `C.ElementType` implements points of objects of `C`. An element of `X` is a morphism `1_C -> X` from the terminal object of `C`, and `x.parent()` is `X`.
- `C.MorphismType` implements morphisms of `C`.
- `C(...)` is the category-owned constructor.

`Cat` is defined by this repository and is read as mathematics like every other category;
the kernel implements it and no leaf redefines it. Every category in this repository uses
`Cat().ObjectType`.
Every functor uses `Cat().MorphismType` and is an object of `Fun = Mor(Cat())`.
`Cat().ElementType` implements points `* -> C`, where `* = Cat().Terminal()`. These points are the actual objects of `C`, so every `C.ObjectType` inherits it.
A generalized element of `C` has the form `T -> C` and is an object of `Fun(T, C)`. It is not a `Cat().ElementType` unless `T = *`.
`C.MorphismType` is `Mor(C).ObjectType`: a morphism of `C` is an object of the morphism category, not a point of `C`.

Size is outside the model. `Cat()` is an object of `Cat()` by runtime convention. No kernel operation quantifies over, enumerates, or scans the objects of `Cat()`.

The same architecture applies to objects, elements, and morphisms.
Do not solve one surface with a mechanism that cannot support the other two.

Never assume that an arbitrary mathematical entity is a set.
Every represented entity is a category or an object in its stated category.
Establish that `X in Sets()` or apply an explicit functor to `Sets()` before using elements, membership, cardinality, enumeration, subsets, or set equality.
An unjustified reduction to `Sets()` is a foundational error.
Rebuild every dependent definition, type, morphism, and conclusion in the correct category.

A sheaf is an object of a sheaf category.
An internal hom of sheaves is again a sheaf.
A functor is an object of `Fun = Mor(Cat())` and of `Fun(C, D) = Mor(Cat())(C, D)` for its
fixed domain and codomain.
None is a set without a specified set-valued functor.

The following are categories and therefore objects of `Cat`:

- `Mor(n, C)` for every `n >= 0`, with `Mor(0, C) = C` and `Mor(C) = Mor(1, C)`, including `Mor(C).Endomorphisms()` and `Mor(C).Automorphisms()`;
- `Fun = Mor(Cat())` and `Fun(C, D) = Mor(Cat())(C, D)`;
- `Mor(C)(x, y)`.

For `A, B in C`, the one owned hom category is `Mor(C)(A, B)`: the full subcategory of
`Mor(C)` on the morphisms with domain `A` and codomain `B`. It has no other spelling.
A category `K` called with construction data constructs an object of `K`; `Mor(K)(A, B)`
called with construction data constructs a morphism `A -> B`. These are the two call forms
on categories.

Define `Fun = Mor(Cat())`. Thus `Fun(C, D)` owns construction of functors from `C` to
`D`. The endpoints select this hom category. They do not select one of its objects.

```python
Fun(C, D)(on_object, on_morphism)
Fun(S, T).Monomorphisms().Isofibrations().Full()()
Fun(C, C).Equivalences().identity()
```

A mathematical construction creates each named functor through this category. It retains
all defining projections, evaluations, and subcategory monomorphisms. A leaf selects the functors that
supply its inherited public structure.

The kernel does not inspect fields or tuple positions to choose a structure map. Product,
pullback, comma, and `Fun([1], C)` constructions retain their distinct projection and
evaluation functors.

A leaf selects the strongest functor-property category established by its mathematics.
The construction trusts that declaration. It does not compute the property.

The hom object at the `Cat` level is the category `Mor(C)(A, B)`.
For example, `Fun(C, D)` has natural transformations as its morphisms.
Only `Sets()` identifies its hom objects with sets of functions: `Mor(Sets())(A, B)` is the discrete category on the maps `A -> B`, and `B ** A` is the function set.

The `Cat` level supplies the uniform category constructors:

- `Mor(n, C)` for every `n`;
- the property subcategories `Mor(C).Monomorphisms()`, `.Epimorphisms()`, `.Isomorphisms()`, `.Endomorphisms()`, and `.Automorphisms()`, and for `Fun` also `.Full()`, `.Faithful()`, `.FullyFaithful()`, `.EssentiallySurjective()`, and `.Equivalences()`, with endpoint dispatch `P(A, B) = Mor(K)(A, B).P()` for every property subcategory `P` of `Mor(K)`;
- `Products()`, `Coproducts()`, `Limits(I)`, and `Colimits(I)` for a supplied shape `I in Cat()`, and `Subobjects()`.

Apply products and coproducts to `Cat()` itself. For a sequence of categories:

```python
P = Cat().Products()((C_0, ..., C_n))
Q = Cat().Coproducts()((C_0, ..., C_n))
P.product_projection(i)   # P -> C_i
Q.coproduct_injection(i)  # C_i -> Q
```

Here `P` and `Q` are the product and coproduct categories themselves. Each returned
morphism is a functor and therefore a `Cat().MorphismType` value.

The operators are defined once in two contexts. On categories: `C * D = Cat().Products()((C, D))`, `C + D = Cat().Coproducts()((C, D))`, and `D ** C = Fun(C, D)`. On objects `X, Y` of one category `C`: `X * Y = C.Products()((X, Y))`, `X + Y` their coproduct, and `Y ** X` the exponential object where `C` is declared cartesian closed. Each takes its construction in the narrowest category containing both operands. An object refined into `C.P()` and an object of `C` are both objects of `C`. Their product is the product in `C`. Operands with no common category fail the assertion. Construct an external pair explicitly as `(C * D)((X, Y))`.

Let `P` be a product category. If `j: S -> P` presents a subcategory, the
corresponding object of `Cat().Products().Subobjects()` retains `j` and reads `P` as its
codomain. Its `product_projection(i)` is the composite of `j` with the corresponding
projection of `P`.

The category whose objects are the morphisms of `C` and whose morphisms are commuting
squares is the functor category `Fun([1], C)` from the walking arrow `[1]`. Its evaluation
functors `ev_0, ev_1: Fun([1], C) -> C` return the domain and codomain. `C.SliceOver(x)` is
the pullback in `Cat()` of `ev_1` along `x: 1 -> C`; `C.CosliceUnder(x)` is the pullback of
`ev_0` along `x`; a comma category `(F, G)` is the pullback of `(ev_0, ev_1): Fun([1], C) -> C * C`
along `F * G`. Each retains its pullback projections; the varying object is the composite
with `ev_0` or `ev_1`.

The generic `MorphismType` stores its domain and codomain and exposes `domain()` and `codomain()`.
If a morphism predicate names a subcategory, implement it as containment in that subcategory.
For example, test `f in Mor(C).Monomorphisms()` instead of inspecting the Python class of `f`.
Prefer a morphism or functor formulation when the mathematical definition names a relation or transport.

A functor transports constructor data. Declaring a supercategory says nothing about how
to build one of its objects or morphisms from one of yours, and supplying that is the
leaf's work. The leaf knows the target's constructors, provides constructors on its own
objects and morphisms, and states how one of its own constructions produces the data the
target's constructor consumes. A module category whose constructor takes an action
`rho: A bullet X -> X` teaches the repository to produce a set from a module by stating
the data `Sets()` requires. Writing those two rules is leaf work. Naming canonical
images, construction inputs, routes, or transport around them is not.

Selecting a functor is not a property of it. A leaf builds an ordinary functor and
declares it structural by returning it from `structure_functors()`; there is no separate
kind of functor and no constructor that makes one.

For each functor `F: C -> D`:

- `F.domain()` is `C`.
- `F.codomain()` is `D`.
- `F.on_object()` constructs the image of an object.
- `F.on_morphism()` constructs the image of a morphism.

For `F: C -> D`, `F.on_element(t)` derives from `F.on_morphism(t)`.
If `t: 1_C -> X` is a point, a supplied morphism `1_D -> F(1_C)` makes the result a point of `F(X)`.
A generalized element `t: T -> X` maps to `F(t): F(T) -> F(X)` without becoming an `ElementType` value.

Functor properties are ordinary property subcategories:

- `Mor(Cat()).Full()`;
- `Mor(Cat()).Faithful()`;
- `Mor(Cat()).FullyFaithful()`;
- `Mor(Cat()).EssentiallySurjective()`;
- `Mor(Cat()).Equivalences()`.

Their `is_*()` methods return applied predicates. Direct property construction and
`assume()` refine the same owned functor. These properties currently have no
computational handlers. `ask()` returns `Unknown` unless category placement, an active
assumption, a cached exact decision, or a categorical implication decides the predicate.

Every functor is explicit.
Only functors selected in `structure_functors()` contribute compiled classes and methods to the public object surface.
Ordinary mathematical functors remain available without changing public inheritance.

A relation between two categories exists only as an arrow.
Every operation that crosses categories names its functor and both endpoints.
For example, `R^n` reaches sets through its ring structure, and a lattice `(L, b)` has distinct projections to `L` and `b`.
A simplicial set has several different functors to `Sets()`.
The named functor makes each mathematical choice visible.

A functor has an image; a category does not. The image of `x` under the named functor `F`
is `F.on_object(x)`. There is no operation that asks a category for "the image of `x` at
`C`". A leaf can declare several functors into one target, so naming only the target leaves
the functor unstated. You should rarely apply a functor by hand; when you do, you get
exactly what you programmed it to construct.

Two selected structural routes to the same category must return the same object by
identity. At the first structural transport of a value to a reachable category, traverse
every route to that category in declaration order, cache the first image, and assert that
each later image `is` the cached one. A mismatch raises a construction-defect error naming
both routes. This agreement is a fact about those functors. It creates no image operation
on the target category. Method compilation constructs no image and performs no such check.

From the leaf writer's side this is ordinary Python inheritance, and that is the whole
requirement. What a leaf writes:

- `ObjectType`, `ElementType`, and `MorphismType`, as its own nested classes, on a category
  class that inherits from a base category class;
- a constructor taking its own category's data, initializing its own state only;
- for each ancestor category, a functor stating how its own data supplies what that
  ancestor's constructor requires.

What must then hold, whatever the kernel does to achieve it:

- an object of `C` is an instance of the compiled class of every category `C` declares a
  functor to, and carries the data those inherited methods need, not the methods alone;
- a leaf constructor never accumulates a field for an ancestor category;
- an inherited method is found by ordinary attribute lookup, Python special methods
  included, and applies to the object the caller named;
- local declarations win; two selected functors reaching one declaring category share one
  method owner; unrelated declarations sharing a name are an error.

There is one chain per mathematical kind. Every category is a `Cat().ObjectType`.
Every object of a category is a `Cat().ElementType` and a `C.ObjectType`.
Every point `1_C -> X` of `X in C` is a `C.ElementType` with parent `X`.
Every morphism of `C` is a `C.MorphismType` and a `Mor(C).ObjectType`.
Selected functors contribute only the class conversions that their mathematics supplies.

Sage's dynamic classes already carry inherited methods; what they do not carry is the
private data those methods need. Supplying that is the kernel's work, and the declared
functor is where the leaf states it.

A category writes `ObjectType`, `ElementType`, and `MorphismType` as its own nested classes.
One name per kind: the category writes the class and the kernel compiles it. A category class
inherits from a base category class, exactly as in Sage. Never define these classes elsewhere
and pass them into a call.

A property subcategory has its own `ObjectType` — `Sets().Finite()` genuinely has one, the
finite sets — but usually adds no method. It receives a trivial extension of its immediate
ancestor's class and writes no boilerplate for it.

An inherited method means `X.f() := F(X).f()` along the selected functor `F`, and returns
the declaring method's value. That equation states the mathematics. Ordinary Python
inheritance is the mechanism that makes it true:

- for each selected functor `F: C -> D`, the kernel makes `C.ObjectType` a Python subclass
  of `D.ObjectType`, so an object of `C` is an object of `D` at the Python level as well;
- `F` states how the construction data of `C` produces the data that `D`'s constructor
  consumes;
- the kernel uses that statement to thread a leaf constructor's arguments through the
  ancestor initializers, so the object carries `D`'s state itself, methods and data alike;
- `D.f` then runs on the original object, reads that state, and returns its declared value.

The method fetches no second object, because no second object exists: the poset carries
the set state. `self` is the value the operation was applied to, and it is a poset. An
object is not "read at the level of" another category, because no value can be read in two
categories at once.

Stating the conversion once, as the functor, is the point of the mechanism. Without it a
leaf would repeat that same conversion inside a hand-written `__init__` that threads
`super()` arguments itself.

A leaf that wants a source-category result overrides the inherited method or adds its own.
Lifting an ancestor result back is leaf work. `Sets()` can construct the product of the
underlying sets; supplying the module structure on that product is the module category's
mathematical delta. Nothing at `Sets()` knows what a module is.

Derive supercategory information from selected functors.
Do not maintain a second inheritance or propagation registry.

## Universal constructions

A categorical construction acts on objects and morphisms.
A parent-only result does not implement a categorical construction.

Retain the data that states the universal property:

- a product retains its diagram, `product_projection(i)`, and mediating morphism;
- a coproduct retains its diagram, `coproduct_injection(i)`, and mediating morphism;
- a limit retains its cone and universal map;
- a colimit retains its cocone and universal map.

Let each apex inherit methods from the category in which it lives.
Use functor composition and natural transformations to move structure.
Do not create a separate method-propagation system for constructions.

For a construction functor `F: Diag(C) -> C`, the family `C.Products()`, `C.Limits(I)`,
or its dual is the full subcategory of `C` on the constructed objects. Its one selected
functor is the retained identity-on-values monomorphism into `C`, so `F(D)` is an object of
`C` with the whole surface of `C`. The construction returns that one value, placed in the
family. The family retains the universal data of each diagram `D`: `D` itself, the
defining morphisms, and the universal maps. Distinct diagrams keep distinct universal
data, including when they construct one object.
This applies to products, coproducts, limits, and colimits.

A covering object of `Y` is a pair `(X, p: X -> Y)` with `p` an epimorphism.
It is not the morphism `p` alone.

A diagram is indexed by a family, and that index need not be an ordered set. Never reorder
a supplied family: `B * A` does not become `A * B` because `"A" <= "B"` in some order.
Where an operation is commutative and associative and a canonical form does order its
terms, order them by an owned mathematical key. Never order by `repr`, `str`, or another
printed presentation. A printer is a presentation, so ordering by it makes object identity
depend on display text.

Implement constructions for arbitrary small diagrams.
Finite diagrams are specimens, not the general interface.

## The category of sets

`Sets()` must replace Sage's Sets category for this package.
It owns arbitrary sets and arbitrary functions.

A set map requires a domain, codomain, and rule.
It does not require a finite table, linearity, continuity, or an enumeration.
The framework must represent maps such as:

\[
\mathbb{Q} \to \mathbb{N}, \qquad
\mathbb{Q} \to \mathbb{Z}, \qquad
\mathbb{R} \to \mathbb{R}^{2}.
\]

Here \(\mathbb{N}\) excludes zero.

Membership predicates can return `bool | Unknown`.
`Unknown` means that the available data and algorithms do not supply an answer.
It is not `False`.

For a predicate on a set `B`, construct the selected subset `A` together with its monomorphism `A -> B`.
The subset is an object of `Sets()`.
That monomorphism is a morphism in `Sets()`.
This must support infinite subobjects such as the even integers and prime integers inside `ZZ`.

`Sets()` owns:

- membership and iteration when available;
- cardinality, which is a cardinal when it is known and `Unknown` when it is not;
- function sets and exponentials;
- products and coproducts of arbitrary small families;
- general limits and colimits;
- predicate subobjects and their monomorphisms.

In `Sets()`, the function set and the exponential are one object `Y ** X`, and
`Mor(Sets())(X, Y)` is the discrete category on its elements:

\[
\operatorname{Mor}_{\mathbf{Set}}(X,Y)=Y^X.
\]

The power set is the corresponding exponential into the two-element set:

\[
\mathcal{P}(X)=2^X=\operatorname{Mor}_{\mathbf{Set}}(X,2).
\]

Construct set maps from a well-typed callable or explicit mapping data.
Neither representation requires enumeration of the domain.
In particular, a map `QQ -> ZZ` can use a callable rule even though no explicit table exists.

The resulting set objects own their cardinality rules.
They must satisfy, when the cardinal arithmetic is known,

\[
\#(X\times Y)=\#X\,\#Y,\qquad
\#(X\sqcup Y)=\#X+\#Y,\qquad
\#(Y^X)=(\#Y)^{\#X}.
\]

The cardinality functor transports those results; it does not contain construction-specific cases.
Write `X.cardinality() == 3`.
Do not write `X.cardinality().value == 3`.

Cardinals form a semiring with a poset structure, not integer wrappers. The poset
is what records that `2 ** aleph_0` is incomparable to most `aleph_i` in ZFC.
There is no separate symbolic cardinal, and cardinals implement no `Unknown`
handling of their own: `cardinality()` uses the same `ask`/`assume` machinery as
every other operation undecidable in full generality, returning a cardinal when the
answer is known and `Unknown` when it is not. Preserve an unknown comparison as
`Unknown`; do not throw an exception or select a Boolean value.

Build cardinals on Sage's existing semiring and poset support rather than hand-rolling
the algebra: a semiring for the finite part, a semiring for the aleph part, and one
that delegates to both and states the mixed cases and the exponential. Defining a
semiring means defining its operations, so an idempotent `x + x = x` is a definition,
not a defect.

Use `cardinality()` for a mathematical set, including a set of module elements or module generators.
Use `len()` only for a finite ordered Python sequence whose sequence length is the stated concept.
Methods such as `ngens()` and `rank()` return cardinalities when their definitions count mathematical sets.

Every object whose parent is `Sets()` receives the complete `Sets.ObjectType` method surface.
This includes ordinary sets, products, coproducts, subsets, and `Y ** X`.
Products and subsets must delegate to the categorical constructions that create them.
They must not define parallel set APIs.

Propagate these operations along selected functors and universal constructions.
Do not implement a second copy of a set operation in a higher category.

## Mathematical ownership

Start with the mathematical object, data, laws, hypotheses, and morphisms.
Choose a Python representation only after those facts are explicit.

Use these ownership rules:

- categories own generic operations;
- objects own operations on themselves;
- morphisms own properties and operations whose definitions name the morphism;
- functors own changes of structure;
- universal constructions own their defining morphisms;
- computation engines return data used to construct owned mathematical objects.

Keep these notions distinct:

- an object and a presentation of it;
- an element and its coordinates;
- a morphism and a matrix representing it;
- a subobject and its monomorphism;
- a theorem and a runtime algorithm;
- a mathematical result and an implementation-engine value.

A subobject of `B` is an object `A` with a monomorphism `f: A -> B`, and that is the whole
notion. There is no second kind and no separate name for a representative: the
equivalence-class formulation matters only when deciding whether two subobjects are equal,
which is a predicate.
Obtain `B` from `f.codomain()`.
Do not duplicate the codomain or monomorphism data in storage fields.

Implement the general mathematical notion.
Recover special cases through restriction, category refinement, or specialized functors.
Do not patch only the example that exposed a missing general construction.

Prefer categorical and homological definitions over element-wise tests:

- use a kernel instead of testing that every output is zero;
- use a cokernel instead of a quotient presentation;
- use vanishing terms in an exact sequence instead of a presentation-specific isomorphism test;
- use fibers, cofibers, pullbacks, limits, and colimits when they state the general definition.

The public definition must remain meaningful in categories without elements.
Element-wise formulas can implement or prove consequences of that definition.

## Semantic representations and computation boundaries

A matrix is a basis-dependent representation.
A matrix is not a morphism, bilinear form, quadratic form, or tensor.
Public APIs accept and return the semantic mathematical object.

Use these boundaries:

- compare elements through their parent and element interface, not their coordinates;
- compare morphisms as morphisms, not by comparing representing matrices;
- compute `f.kernel()`, `f.image()`, and `f.cokernel()` as semantic objects;
- ask `f.is_surjective()` instead of comparing a presentation of `f.image()` with `f.codomain()`;
- evaluate a form as a callable hom element;
- retain a tensor as a tensor and derive a matrix only after a basis is chosen.

Lower a semantic object to coordinates or a matrix in one private computation boundary.
Use private implementation hooks such as `_kernel_matrix_` for matrix algorithms.
Reconstruct the semantic result before returning through the public API.
Tests and downstream code must not call those hooks or repeat the lowering.

One owned object can retain several private computation representations.
One method can combine algorithms from several engines when each computes part of the
semantic result. Select those algorithms from the mathematical construction and exact
input properties. Never create competing public implementation classes for the engines.

The owning method remains the single source of API meaning. Engine adapters only prepare
inputs, call mature algorithms, and return data for semantic reconstruction. They never
install methods, select mathematical owners, or refine categories by themselves.

A public constructor for a module or algebra element accepts semantic elements.
It must not reinterpret a list, tuple, or numerical vector as such an element.
To form a finite linear combination, obtain the module generators and write `sum(a_i * g_i)`.
Do not add a differently named helper that accepts coefficient vectors.

Implement scalar change and other functors on semantic objects and morphisms.
Apply the functor before choosing bases and deriving a matrix in the new realization.

## Generality and hypotheses

State the weakest algebraic hypotheses that make an operation valid.
Parameterize every algebraic-object category by the complete ambient categorical data in its definition.
Do not hard-code `ZZ` when the definition or algorithm works over a PID, integral domain, or commutative ring.

For a tensor category `V`, `Magmas(V)` contains magma objects. For a monoidal category
`V`, `Monoids(V)` contains monoid objects. For cartesian monoidal `V`, `Groups(V)`
contains group objects. For a category `C` with the required product structure,
`Semirings(C)` and `Rings(C)` contain internal semirings and rings. The specification
for the ambient structure states each strictness or coherence requirement.

Let `M` be monoidal, let `C` have a chosen left `M`-action, and let
`A in Monoids(M)`. An object of `Modules(A, C)` is an object `X in C` with an action

\[
\rho:A\mathbin{\bullet}X\longrightarrow X
\]

that satisfies the unit and action diagrams. Retain `M`, `C`, the action functor, and
`A`. Supply `C` independently from `A`. A monoid morphism
`A -> End_C(X)` represents the same action only when the required closed or enriched
structure supplies that correspondence.

Define `Algebras(R, C)` only when `Modules(R, C)` has a supplied monoidal structure.
It is the base-relative presentation category for the monoid objects in that module
category. Its selected functor to the general monoid-object category supplies the
multiplication, unit, and monoid laws. A noncommutative base instead requires a
supplied monoidal category of `R`-bimodule objects.

A lattice over `R` starts from a finitely generated projective `R`-module with the specified form.
Free `ZZ`-modules are specimens of that notion, not its definition.
Select algorithms by proved ring properties, not by identity checks against `ZZ` or `QQ`.

A `W`-valued bilinear form is a morphism from `M tensor_R M` to `W`.
Its Gram matrix is its representation in a chosen basis.
Use “inner product” only for a positive-definite symmetric bilinear form.
Do not assume that a lattice is positive definite, free, based, embedded, or unimodular.
Distinguish left and right radicals when the form is not symmetric.
State the symmetry and nondegeneracy hypotheses needed for orthogonal complements, norms, and reflections.
Use exact coefficient rings and exact arithmetic for form and lattice predicates.
Do not define definiteness through floating eigenvalues or numerical spectra.

Do not import vector-space equivalences into modules over a general ring.
A nonzero torsion module can have rank zero.
A nonzero torsion kernel can have rank zero.
Therefore, neither `M.rank() == 0` nor `matrix(f).right_kernel().rank() == 0` proves that a module or kernel is zero.
Use the semantic zero-object or kernel predicate supported by the relevant category.

The same Python realization can define different mathematical objects in different categories.
For example, `QQ` over two base objects or in two ambient module categories has different structure morphisms.
A scalar-change functor relates them.
Do not erase the base category from the type, parent, or morphism data.

## Sage and external computation engines

The owned framework defines the mathematical categories and their subcategory monomorphisms.
Native Sage categories do not define this package's mathematical supercategory graph.

Sage is one private computation engine and runtime substrate. It is not the required
representation for every object and is not an intermediate through which every other
engine must pass.

A category-owned implementation can use any suitable combination of Sage, SymPy, GAP,
Julia packages, Singular, Macaulay2, external programs, or local research algorithms.
Choose each engine because its native mathematical construction supplies the needed
exact computation. Different methods on the same object can use different engines.

Use Sage for:

- `Parent` and `Element` runtime support;
- homsets and morphisms;
- coercion;
- dynamic classes and refinement;
- category joins and construction classes;
- established exact algorithms.

Cross into Sage through an explicit realization functor or owned computation boundary.
A Sage realization is not selected for inheritance.
Its Python methods must not enter the public mathematical API by accident.

Apply the same boundary to every external engine. Keep each engine value private.
Reconstruct the owned mathematical object, element, morphism, cardinal, or decision before
return. A method can combine several engine values before this reconstruction.

Do not add a public backend selector, engine registry, competing `ObjectType`, automatic
engine-method routing, or implementation-specific public operation. The sole
category-owned implementation class hides the full polyglot computation catalogue.

Do not modify Sage category classes.
Do not add owned methods to Sage classes.
Do not preserve a Sage method spelling as a second public owner.

Use an established exact algorithm from a suitable engine before writing a local
implementation. If no applicable theorem or mature exact algorithm determines the
result, keep the operation at its owned interface and return the appropriate unknown
value.

## Public API and types

Shape every API from the mathematics.
Do not derive it from current class layouts, storage fields, or available method names.

Use one owner, one public name, and one public export for each operation.
Use established mathematical and Sage terminology.
Name an accessor for the exact object or morphism that it returns.

Use the two call forms on categories.
`K(data)` constructs an object of `K`.
`Mor(K)(A, B)(data)` constructs a morphism `A -> B`.

Treat private fields and private methods as private to their owner or documented subclass contract.
Ask another object through its public mathematical interface.
Invoke Python protocols through public syntax such as `f(x)` and `iter(x)`.

Give every value the type that names its exact mathematical type.
Distinguish categories, objects, elements, morphisms, functors, rings, sets, domains, and codomains.

Never use `object` as a type.
Use `Any` only for a parameter that genuinely accepts every input.
The normal examples are the candidate parameters of `__eq__` and `__contains__`.
Never return `Any`.

Use `Self`, `None`, or a type for the returned mathematical object.
For example, return the element type of `NN`, `ZZ`, or `RR` for a natural number, integer, or real number.
Do not replace an exact mathematical result with `float` or a built-in container type.
Use the mathematical collection type: set, ordered set, multiset, or another named structure.

Primitive types can occur inside a private implementation boundary.
No external consumer may depend on that private signature.

Create a new type when it names a genuine mathematical object.
Do not wrap a union of invalid constructor inputs in a new engineering type.
Replace the invalid inputs with the mathematical object that the constructor requires.

Treat a type error as evidence about the mathematical model or import boundary.
Fix the owner, type hierarchy, return contract, import path, or missing declaration.
Do not silence it with a cast, ignored diagnostic, deleted annotation, or wider type.

Use category membership as type information.
Do not inspect fields, `__dict__`, or method names to discover mathematical capabilities.

## Implementation style

Write each method in the order of the mathematical definition.
A mathematician must be able to compare the method body with that definition.

Keep code direct:

- use short functions and early returns;
- avoid helper chains that hide the mathematical steps;
- add an abstraction only when a second real use requires it;
- use existing dependencies and Sage capabilities before adding code;
- prefer a maintained library or mature reference implementation;
- cite the mature source of unavoidable local implementation code.

Do not add compatibility layers, fallbacks, migrations, obsolete aliases, or parallel implementations.
Fail loudly when required mathematical structure or a dependency is absent.

Do not use `setattr` to assemble or modify the mathematical API.
Do not use `hasattr` to guess which mathematical interface an object supports.
Do not recover mathematical structure from storage fields.
Fix a repeated defect at its category, functor, or construction owner.

Do not use `getattr` for mathematical dispatch.
Do not use `isinstance` for mathematical classification.
Use the owned public interface and categorical containment.

Use assertions for mathematical preconditions, functionality gates, and type narrowing.
Write `assert x in C` when membership in `C` is the required fact.
Do not replace it with `assert isinstance(x, C.ObjectType)`.
The assertion must remain true when the Python implementation class changes.
Do not add `try`/`except`, fallback values, or recovery branches for a violated mathematical precondition.

Preserve exact arithmetic until an explicit numerical boundary.
Keep precision parameters at that boundary.

## Tests

Read the test guidelines before editing a test file.

Never run repository test, lint, type-check, format, or aggregate-check recipes manually.
Commit and push hooks own these checks and run them automatically.
Do the work, commit it, and repair a hook failure from its exact output.
Retry the commit or push after that repair.
Do not duplicate a hook check before the commit.

A targeted Python test needed during implementation is the only routine manual exception.
Read `justfile` before running it.
Use the Sage-aware route defined there instead of guessing a plain Python command.

Do not test or type-check an incomplete or known-broken architecture.
This restriction includes targeted tests, lints, formatters, and diagnostic sweeps.
These checks measure a transient local state and give false confidence in small patches.
They encourage greedy local repairs that move the code away from the required architecture.
Compare each issue directly with the governing specifications and inspect the code itself.
First make ownership, category paths, dependency direction, and public semantics converge to those specifications.
Run real tests and type checks only after the architecture is coherent and complete.
Until then, checkpoint necessary intermediate states through the red-commit pathway.

Every assertion must state a mathematical proposition or an essential type invariant.
Test the real category compiler and public API.

Every expected mathematical fact needs an independent oracle.
Use a source that you inspected, with a theorem, section, table, or page citation when available.
Sage behavior can guide a realization, but Sage parity is not an oracle for repository-owned mathematics.
Never change an expected mathematical fact because the implementation returned another value.

Use canonical mathematical objects when they exist.
An explicit matrix is suitable only when the cited mathematical datum is that matrix or the test concerns its semantic realization.

As applicable, assert:

- category and parent;
- domain and codomain;
- images of elements;
- identity and composition;
- functor laws;
- naturality;
- universal morphisms;
- mathematical equality;
- isomorphisms and classification results;
- semantic kernels, images, cokernels, and induced maps.

Rank, determinant, signature, parity, dimension, and nonemptiness can be setup guards.
They do not by themselves prove a richer claim about isomorphism, genus, a discriminant form, a universal construction, or a morphism.
State and test the stronger semantic claim.

Tests must use semantic objects and public operations.
Do not assert coordinate arrays, matrix ranks, Python classes, private fields, helper output, or source layout when those are not the public contract.
Do not use `isinstance`, `hasattr`, `getattr`, or `setattr` in a mathematical test.

Use exact arithmetic and exact equality.
Do not replace a mathematical equality with a numerical tolerance.
For an ambiguous computation, combine a cited fixture with an independent formula, construction, or representation.

Use the smallest specimen that distinguishes correct behavior from a plausible failure.
Use a real Sage process for Sage behavior.

Do not test implementation layout, diagnostic totals, source text, caches, or correction history.
Do not add a test whose only purpose is to assert the absence of a previous mistake.
A passing test is evidence only for the proposition that it executes.
Do not use mocks, simulations, skipped cases, or expected-failure markers as mathematical evidence.

## Performance

Measure wall time as a function of input size.
Do not report call counts as efficiency evidence.
Use call counts only to locate repeated work.

Remove waste:

- repeated derivation;
- needless enumeration;
- repeated verification;
- a general algorithm where category placement provides a more specific one.

Preserve code that displays the mathematical sequence when a faster form hides it.
Use small mathematical specimens unless the claim concerns a large named object.

## Work discipline

Before editing, inspect a focused repository tree and the complete target artifact.
Preserve existing and concurrent work.

Work on the requested mathematical object, not a plan, count, checker result, or reviewer verdict.
The first deliverable of a work unit is a falsifiable specimen.

When a correction invalidates a foundational assumption, stop the local patch.
Reconstruct the requested mathematical object and resume from the corrected model.

If the category graph or method owner is wrong, stop runtime debugging.
Fix `Cat`, the `Mor(n, C)` tower, the method compiler, and `Sets()` in dependency order.
During that migration, move each required behavior to its new owner before deleting its old implementation.

For a sweeping architectural refactor, make the final ownership graph and dependency direction correct first.
Do not chase type errors that exist only because the refactor is incomplete.
Complete the category, functor, compiler, and constructor transition before resolving remaining diagnostics.

If the incomplete architecture needs a checkpoint, use the sanctioned red-commit pathway:

```bash
ai-review-ci red-commit --issue <owning-issue> -m "<message>"
```

The red commit skips verification for the incomplete state.
Never weaken the architecture or add temporary repairs merely to make an intermediate state pass.

Continue while the next in-scope action is clear and safe.
Do not stop at an administrative artifact when implementation remains.

End each substantive work unit in a focused commit.
Do not leave required work only in the working tree.
Preserve unknown files until their ownership is known.

For every docs-only edit, bypass all verification.
Commit it with `git commit --no-verify`.
Do not run tests, linters, formatters, or other checks for that edit.

Never use destructive Git operations without an explicit request.
Never use `rm`; use recoverable system trash for disposable files.
