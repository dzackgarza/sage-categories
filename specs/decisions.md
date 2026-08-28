# Architectural decisions

This file records the decisions the repository owner stated in working sessions between
2026-08-22 and 2026-08-28, in Claude and Codex transcripts. Those statements are the
source of the architecture. They were not written down anywhere in the repository, so
each rebuild rediscovered them by excavation or, more often, invented a replacement.

Each entry gives the decision and its date. The topic specifications own the resulting
technical statements; this file owns what was decided and when. When a specification, a
policy row, a plan, or a report disagrees with an entry here, this file wins and the
other artifact is the defect.

Read this before proposing an architecture. Do not re-derive a decision from source code:
the source was written by the same process these decisions correct.

## Contents

- [Purpose and scope](#purpose-and-scope)
- [Declared functors and inheritance](#declared-functors-and-inheritance)
- [Elements](#elements)
- [Predicates, containment, and assumption](#predicates-containment-and-assumption)
- [Cardinality](#cardinality)
- [Universal constructions](#universal-constructions)
- [Diamonds and identity](#diamonds-and-identity)
- [Leaf discipline](#leaf-discipline)
- [Types and style](#types-and-style)
- [What the documents are for](#what-the-documents-are-for)

## Purpose and scope

**D01 (08-22). Build the whole foundation before any structured category.** `Cat`, all
arrow categories, working inheritance through `ObjectType` and the other implementation
classes, and then an extensive `Sets()` that completely replaces Sage's `Sets` and uses
none of Sage's categorical constructions. Do not drift into rings, modules, lattices, or
formed modules.

**D02 (08-23). The package shadows a subset of Sage, and its universe is closed.**
`sage_categories.all` works like `sage.all`. Once you touch a package-owned object, every
further computation stays inside the package: every operation is mediated by the package's
categorical API, and every result you can produce is still a package object. There is no
intention to refine Sage objects into this hierarchy or to be compatible with base Sage;
any compatibility is incidental. Base Sage appears only inside hidden implementation
engines. When the package wants a Sage construction, it absorbs it as an internal engine
and re-expresses it through the categorical machinery.

The reason is uniformity of interface. Sage's implementations forget things. Sage's
`IntegralLattice` does not know its underlying set is `ZZ^n`, so `ZZ^n` is not recognised
as a product of sets, rings, or rank-one modules, and Sage cannot say its cardinality or
iterate it — while research code wants to enumerate infinite countable sets in bounded
loops, as Vinberg's algorithm does.

**D03 (08-23). Computation is not the goal.** Sage already computes everything this
package computes. The goals are uniformity, categorically principled code, category theory
as a form of DRY, real functors everywhere, and obviating engineering concerns so that a
leaf developer thinks about mathematics. It is an organisational, more legible layer over
Sage. Sage code needs a programmer to audit it; code here, outside the kernel, should be
auditable by a mathematician with very little coding experience.

**D04 (08-23). The long-term asymptote.** Adding a category such as
`MyVerySpecialAlgebraOverANoetherianDomain(R)` should mean: define a leaf category,
possibly from a shipped template; declare a few functors to nearby categories you already
understand, without reading the rest of the codebase; write your new methods; and receive
the full inherited surface. You think at the level of your own algebra, and `cardinality()`
and suitable limits and colimits arrive because of the functorial wiring.

## Declared functors and inheritance

**D05 (08-23). Never subclass objects of a category explicitly.** Not without discussion
first. `ProductSetObject` must not subclass `SetObject`; that bypasses the functor
framework. If the intended architecture does not work, that is not a licence to subclass.
Even `FiniteSets` inside `Sets`, where the underlying object is "just a set" both times,
must declare its functor — here the inclusion, possibly trivial. Otherwise the category is
free-floating. This is what replaces `super_categories`. The same holds for limits,
colimits, products, coproducts, tensor products, direct sums, subobjects, and covering
objects.

**D06 (08-24). Sage's `super_categories` conflates distinct notions.** It carries
subcategory inclusions, full or not, and structure projections such as `(X, op) |-> X`
where `Monoids` declares `Sets` a supercategory. Replace it with an explicit
`structure_functors: list[Functor]`, and name the distinct kinds separately: subcategory
inclusion, full subcategory inclusion, projection, and so on.

**D07 (08-24). Declared functors are not every functor out of the category.** They are
the ones along which the category inherits. In the poset example, do not declare the second
projection: a poset `(X, R)` *is* a set, so it inherits from `X`. Projecting to `R` would
give posets the methods of a subset of a product, which is not how anyone works with posets.
This mirrors Sage declaring only `Sets` as the supercategory.

**D08 (08-24). What declaring `F: C -> D` obliges you to supply.** How to take the leaf
writer's own implementation class and feed it into *any* available constructor for
`D.ObjectType`, and the same for elements and arrows. A subcategory inclusion claims that
`X |-> D()(X)` works. A product projection claims your objects already carry the target as
defining data, so the kernel can extract it. Those two are boilerplate and the kernel owns
them. Any other functor states its own maps, teaching the target's constructor how to
consume your data.

**D09 (08-25). "Forgetful functor" is ill-defined; do not use it.** Categories such as
magmas are pullbacks whose objects are pairs, so there are two projections and neither is
"the" forgetful one. For lattices `(L, b)`, the colloquial answer is `(L, b) |-> L`, but
`(L, b) |-> b` is equally symmetric. For `Modules(R)`, whose defining datum is a ring
morphism `R -> End(X)`, no kernel can be expected to know that "forget" means
`(X, +, rho, ...) |-> X`, and the implementer may choose any of several equivalent
presentations. Formulate instead in terms of fibrations, cofibrations, natural projections
and inclusions, source and target functors, arrows induced by Kan extensions, and
composites of these. Follow Mathlib's treatment.

**D10 (08-25). The kernel owns the standard functors.** `FullSubcategoryInclusionFunctor`,
`ProductProjectionFunctor(i)`, and their relatives are kernel-owned precisely so that
leaves need no boilerplate. A leaf writing a page of functor code is a kernel defect.

**D11 (08-25). `Fun := Ar(Cat)`, and every leaf constructs its functors explicitly.** Not
`self.inclusion(D)`. A leaf constructs `Fun(self, D).inclusion()`, or
`Fun(self, D).Full().inclusion()`, so that a known theorem appears as part of the
construction of the functor. Nothing is computed; the leaf writer is trusted. The
equivalent spellings `self.Hom(D)`, `Ar(Cat())(self, D)`, and `Cat().Hom(self, D)` all
remain valid — `Fun` is an additional name, not the sole one.

**D12 (08-26). A functor does not know it is structural.** Leaves construct ordinary
functors and *declare* them, by returning them from `structure_functors()`. There is no
kind of functor called structural and no constructor that makes one.

**D13 (08-26). The kernel is Sage's class-building plus one repair.** Sage's MRO technique
works. Its one flaw is that dynamic classes carry methods and leave out fields, so a method
arrives without the private data it needs to compute anything. The intended repair is to
copy Sage's class-building and fix that flaw, so that from the writer's point of view it is
ordinary inheritance. If `Sets().ObjectType` holds private set data and a constructor that
initializes it, and `Posets()` holds its own private poset data, its own constructor, and a
functor that supplies what the `Sets()` constructor requires, then a poset receives
inheritance rather than methods alone. Wiring the constructors is the functor's job, so a
leaf constructor never accumulates a field for every ancestor category.

**D14 (08-26). One chain per kind, propagating from `Cat`.** Every category is a
`Cat().ObjectType`; every object of a category is a `Cat().ElementType`; every `X in C` is
a `C.ObjectType`, and that propagates along the declared functors; elements and morphisms
follow the same rule. The lineage is as straightforward as Sage's `Parent` and `Element`.

## Elements

**D15 (08-23). "Shared elements" is not a concept.** Every category has an `ElementType`,
including a dynamically constructed one such as `C.Products()`. Element classes inherit
exactly as object classes do, and may add methods: the element type of a product is also an
element of a set and may carry `x.factors()`. An element of a finite set is not "just an
element of a set" — it is `FiniteSets().ElementType`, which extends `Sets().ElementType`
when the wiring is correct.

**D16 (08-26). What an element is.** A Sage element is implicitly a pair `(X, x)` with
`X = x.parent()`. An element of an object in a category is the same thing: a generalized
element `t: T -> X`, an object of `C.SliceOver(X)`, with `parent()` its codomain. So
`ElementType` makes sense for every category even when the category implements nothing new.
An element of a scheme `X` is not a priori well defined, but any `R`-point should have
`x.parent()` and a stalk `O_{X,x}`; the background model is a point of the category of
elements of `h_X`, and the consequence is that a category of schemes still receives an
`ElementType`. For a concrete category with a path `U_C: C -> Sets()`, this recovers the
usual notion of an element of the underlying set.

**D17 (08-26). Every functor transports elements through its arrow action.** No functor
carries element data. `x.f() := F(x).f()` in `D`, where the induced functor on elements
comes from the arrow action. The onus is on the leaf writer to construct the functor: to
inherit `__add__` on your elements, supply a functor to `Magmas().Additive()`, which reaches
sets because magmas are concrete. Every category *gets* the implementation classes; new
methods arrive by wiring functors out of it.

## Predicates, containment, and assumption

**D18 (08-22). There is no decidability boundary.** Sage already supports `Unknown`, and
many predicates should be `bool | Unknown`.

**D19 (08-22). Prefer containment to a raw predicate check.** Predicate computation is
localised in `__contains__`. Write `X in Sets().Finite()` rather than `X.is_finite()` or
`X.cardinality() < infinity`.

**D20 (08-24). Every propositional method returns a proposition.** Never a bool, never an
`Unknown` in its place. Anything that would need `Unknown` routes through
`assume`/`ask`/`.assume()`. Containment in a category is always a possibly compound
proposition, declared once as part of the category's definition — the kernel wires
`FiniteSets` to be reachable as `Sets().Finite()` and lets it declare a membership
proposition, and `__contains__` follows from that.

**D21 (08-24). Construct into the strongest subcategory you can.** Or override the
predicate to return `True`. Both are programmer assertions and need no computation.
Individual named objects are one-object categories: `QQ` is `{QQ}` with functors into
countable sets, posets, and fields. `Fields().Countable().PartiallyOrdered()` should be
nearly automatic, with Sage's `with_axiom` as the model: if any category defines a
property subcategory, any subcategory can narrow itself the same way. Defining `FF_p` as a
one-object category parameterized by `p` must never require proving finiteness by
enumeration.

**D22 (08-24). Assumption is a shortcut for construction.** `assume(X in Sets().Finite())`
and `assume(f.is_injective())` refine into the property category — the same rule you would
have used to construct into `Monos(Sets)(A, B)` directly.

**D23 (08-24). Property refinement strengthens the category of the same value.** It is not
transport into a second implementation, and it is not a family of admission constructors.
Each property category owns one constructor that trusts its defining property. These APIs
must not exist: `monos.checked(...)`, `monos.from_hypothesis(...)`,
`monos.from_theorem(...)`, `construct(..., check=True)`. Direct construction, global
assumption, exact computation, and construction-owned mathematics all converge on that one
constructor.

**D24 (08-24). Backend code does not call `assume()`.** The Sage or SymPy session owns the
global assumption context, and a notebook user may write into it. Internal code already
knows the category in which to construct its result, and constructs there.

**D25 (08-24, 08-25). Theorem-backed construction is declaration, not computation.** No
Python code can establish that `RR` is uncountable, and running a monotonicity check on
`n |-> n^2 : NN -> NN`, or a totality check on `{1, ..., 10^10}` with its natural order, is
absurd. A specific named constructor owns its theorem, and its controlled input data is what
makes the theorem applicable: `square_morphism_on_naturals()`,
`componentwise_product_order(diagram)`, `finite_total_order_from_enumeration(enumeration)`.
A generic `from_theorem(value, owner)` remains invalid, because a registered owner is an
opaque token that identifies no construction. A public total-order constructor accepting an
arbitrary relation is likewise invalid; a constructor from an enumeration builds the
guaranteed-total relation itself.

**D26 (08-25). The repository never proves or certifies category theory.** That is hopeless
in Sage and belongs in a language like Lean. The categorical core is meant to be
independently auditable by mathematicians, so it encodes its needs in standard category or
homotopy theory — nLab, the Stacks Project, Kerodon, textbooks, arXiv papers — and stays
mathematically legible. A code writer forms constructions into the correct subcategory as
the way of asserting a theorem, with a citation on the construction line.

## Cardinality

**D27 (08-22). Never enumerate a set to compute a property.** Always consider what happens
for `{2, 4, ...}` or `{1, ..., 10^10}`. Enumeration is a dead-last fallback for when
cardinality is required, the set is known finite, and there is no other way. Usually
cardinality is supplied at construction or derived from a known relationship: `{n in NN | n
<= 100}` is finite without listing anything. Enumeration can be a fine first approximation
in a specific algorithm, but it does not belong on a main path and should warn loudly.

**D28 (08-22, 08-23). Cardinals compare by ordinary syntax.** `==`, `<=`, and the rest,
against ordinary integers. You never extract a cardinal's "value".

**D29 (08-24). `cardinality()` always returns a cardinal.** Possibly an unknown one.
Representing unknown mathematics by `None` is a defect. An image receives the domain's
cardinality only when the map is established injective; a constant function is the
counterexample.

**D30 (08-25). Cardinal arithmetic is the categorical operation.** The coproduct in the
category of cardinals is exactly cardinal addition; the product is exactly cardinal
multiplication.

## Universal constructions

**D31 (08-23). Define each construction at the most general level that supports it.**
`Modules(R).Products()` should exist because any `C in Cat` can form `C.Products()`, the
way `with_axiom` works — not through leaf boilerplate. If the category is not complete the
subcategory may be empty, which is fine and not something the code proves. `Modules(R)` may
be where `TensorProducts()` and `DirectSums()` first appear, and then `Lattices(R)` forms
`Lattices(R).TensorProducts()` by stating only its delta:
`⊗_i (L_i, b_i) := (⊗_i L_i, ⊗_i b_i)`, since module homs are themselves modules and the
tensor product there is already handled at the module level.

**D32 (08-23). A constructed object presents as an ordinary object with more methods.** A
product set truly *is* a set; it carries additional methods for its factors, universal
morphisms, and so on. Redefining `cardinality()` on a product is the red flag. Either the
family knows `(prod X_i).cardinality() = prod X_i.cardinality()`, or the functor knows how
to build the underlying set, which knows its own cardinality like any set.

The same holds for `R`-lattices: `L = (M, b)` projects to `M`, so a lattice truly *is* a
module with new methods. Which functors count for inheritance is decided case by case by
what is standard to mathematicians. One does not think of a lattice *as* a bilinear form, so
`L.bilinear_form()` is public while `b`'s methods are not grafted on; but neither should a
lattice be treated as an ordered pair in public, with `L.underlying_module()` indirection.
Any `underlying_Y()` method deserves scrutiny: a lattice does not "have" an underlying
module, it *is* a module with extra structure, just as a group `G = (X, f)` is not handled
as an ordered pair in daily use. Ordered pairs are fine as private representations.

**D33 (08-24). A poset product just is the set product with an order on it.** It needs to
do nothing to construct its projections or its mediating morphisms.

**D34 (08-25). The `Cat` level owns the construction vocabulary.** `Cat().Subobjects()`,
`Cat().Products()`, `Cat().Coproducts()`, so that `Cat().Products().Subobjects()` can be
stated and its objects answer `product_projection(i)`. Slice and coslice categories and
their fibrations to the underlying object follow from that. General projections exist for
any subcategory of a product category, `proj_i: (X_1, ..., X_n) |-> X_i`; a coslice has
projections to both `X in C` and `f in Ar(C)`, and composing with the source and target
projections of `Ar(C)` gives the rest.

**D35 (08-25). The operators are defined once.** `Y ** X` is `Hom_C(X, Y)`, `X * Y` the
product, `X + Y` the coproduct, `X @ Y` the biproduct.

## Diamonds and identity

**D36 (08-26). Size is not modeled.** Assume `Cat` is bicomplete and biclosed, so
`[C, D] := Hom_Cat(C, D) := Fun(C, D)` is a category under whatever definition is in play.
This is an engineering convenience to be formalized later. The point is that `Monoids *
Rings`, `Fun(Monoids, Sets) * Fun(Rings, Graphs)`, and `X * Y` for two sets all use one
interface and one semantics.

**D37 (08-26). There is one underlying set, and identity is the only sameness.** For
almost every algebraic category there just is one underlying set, and the functorial paths
are different ways of equipping it. `Free_R({1, 2})` and `Free_R({a, b})` are distinct
modules and must never be identified: the second's generators are formal symbols while the
first's inherit structure as ring elements. No case in this repository needs anything
weaker than identity, so route agreement is asserted by `is`, and a failure is a
construction defect in the object's leaf.

**D38 (08-26). Set equality is a proposition, not a procedure.** The underlying set of
`Free_R(S)` is created by fiat, from a membership rule and a cardinality rule; nothing
enumerates it and there is no extensional description to compare. `X == Y` is `True` by
identity and otherwise `Unknown`, unless a cited theorem or an exact route decides it. So
the compiler's route check cannot compare images; identity is the only decidable option.

## Leaf discipline

**D39 (08-22). What a leaf implementer supplies.** Functors to known categories that show
how to feed the new category's objects into an old category's constructor, plus a
constructor for the minimal delta that defines the leaf. `Modules(R)` built from an action
`rho: R -> End(X)` declaring `Sets` as a supercategory needs only the functor that uses
`rho` to extract `X` and feed it to the `Sets` constructor. The red flag is a lattice
category defining `cardinality()` instead of declaring its functor to
`Modules(R).Free()`. Constructors and functors are among the few places where reaching
into private fields may be acceptable, and each such use needs scrutiny.

**D40 (08-22). Mathematical encapsulation, enforced by the file system.** A leaf defining
something that depends on deeply underlying structure in another category is a red flag —
`cardinality` mentioned in a lattice subtree, for instance. Keep the kernel siloed in its
own subtree with its own test subtree, and split into subtrees as they grow: `Cat`, `Sets`,
modules, formed modules, algebras. Consider nesting for hot paths such as free modules over
a PID. The point is that the kernel subtree may use ordinary Python and is the firewall for
non-mathematical code, while every mathematical subtree can be audited for non-mathematical
language and types. Engine boundaries — Sage, SymPy — should be quarantined in their own
subtrees, where repository rules may be violated out of necessity, so that violations are
firewalled by layout.

**D41 (08-22). A subcategory should almost never exist to house an implementation.** A
method belongs at the most general category where it makes sense and where something is at
least declarable, so an object can be constructed by supplying that data, and different
computational implementations can be selected by case. `Sets.PropertyCategory()`, invented
to wrap subsets defined by a predicate, was the red flag: any set can form a subset from a
predicate, and the result is a subobject in `Sets`. There is no mathematical notion of "a
set defined by a property" — every set is. The naming is the tell: `PropertySet` is
engineering-brained. Track construction provenance privately if you need it.

**D42 (08-22). The user should not need to know the category graph.** Nobody should write
`FiniteSet({1, 2, 3})`; `Sets({1, 2, 3})` routes intelligently, dispatching on optional
claims such as a supplied cardinality or `is_projective=True` that would otherwise be hard
to verify. A small number of high-level endpoints are the primary construction interface,
bypassable by specific subcategory constructors as the user learns them. Usability comes
from discoverability through well-known names: `Sets`, `Monoids`, `Groups`, `Rings`,
`Modules(R)`, `Algebras(R)`.

**D43 (08-24). The leaf class is the implementation, and it is the firewall.** There is
never more than one choice of implementation: Sage already lets competing implementations
proliferate, with three different free modules carrying different operations and
inconsistent inherited surfaces. Mathematically there is one notion of a free module. Your
`ObjectType` hides every possible implementation, collected in one class. Internally you may
use anything — Sage, SymPy, NumPy, an imported dependency such as VinAL for hyperbolic
lattices, a bespoke research algorithm, Cython, a shell program, Julia, GAP, Singular,
Macaulay2 — provided the public API never exposes the choice. There is no automatic routing
into engine methods and no `@realized_operation`-style marker. Quarantine substantial
Python complexity into helper modules.

**D44 (08-24). Inherited fundamentals stay inherited.** Composition of arrows is basic
category theory and arrives by inheritance. A leaf may override to add leaf-level
mathematics — a free-module morphism hooking composition to build a private matrix — but a
method that adds no new mathematics does not belong in a leaf at all. Inheritance is
automatic; you write wiring only when you are adding mathematics.

**D45 (08-24). The question to answer at every step.** "What generic categorical mechanism
makes every leaf state only its new mathematics?" Only that determines where code lives,
which objects own theorems, how calls work, and what methods must exist. Trace the whole
implementation path: how the kernel defines products, how they propagate through categories
and presentations and declared functors, so that the leaf supplies only its delta.

## Types and style

**D46 (08-22). Everything is a tensor.** The package departs from Sage's linear-algebra
primitives: not vectors as internal representations of module elements and matrices as
internal representations of module morphisms, but `(p, q)`-tensors throughout, encoded at
the module `ElementType` level. A bilinear form is a Gram tensor, not a Gram matrix.
`vector()` and `matrix()` shadow a `tensor()` constructor taking `(p, q)` shapes, base
rings, and multi-indexable data.

**D47 (08-22). Morphisms never operate on plain Python objects.** Always construct elements
of the appropriate objects. A hom-category `__call__` may assert
`x.ambient_object() in self.base_category()`.

**D48 (08-22). Do not coin a name for a standard notion.** `type MathematicalObject = Any`
and `SetMapRule` are both defects. The standard notion is a morphism of sets, and the type
is `SetMorphism`. Calling it a "map" or a "rule" avoids the standard semantics.

**D49 (08-22). Each category is internally consistent in its types.** A poset method takes
`PosetElement := Posets().ElementType`, never `SetElement`, so that passing an unstructured
set element is a static type error — even when the poset element class adds nothing.

**D50 (08-23). Never write a method that only fails.** No body that is `assert False`,
`return NotImplemented`, or a raise. That hides a missing capability from static checkers
and surprises the user at runtime; the point is a uniform interface. A `cardinality()` that
raises is worse than no `cardinality()` at all. Use abstract methods, expose the method only
where it is decidable, return a decision or `bool | Unknown`, or route by capability.

**D51 (08-23). Do not golf type checkers.** They are a signal; the architecture and
philosophy are the arbiters of correctness. The compiler should be strong enough to teach
mypy about the functorial construction, but a very dynamic process may exceed what mypy can
follow. Type-checker plugins are legitimate, as is static generation — manifests,
statically constructed types, stubs — regenerated on commit, test, push, or version bump,
since the repository does statically encode all its intended relations at any given time.

**D52 (08-24). Never use optional arguments.** Write total methods and separate,
specifically named constructors. A set constructor that can accept a cardinality by fiat
does not make cardinality optional with a default; it is total in cardinality, with
`construct_uncountable_set`, `construct_countable_set`, and `construct_finite_set` split
out.

**D53 (08-23). Prefer the mathematically flavoured construction.** `pairwise` over `zip`,
and generally: look for packages and dependencies that improve the mathematical flavour of
the code, and propose them when the idea surfaces.

## What the documents are for

**D54 (08-22).** `CONTRIBUTING.md` holds general principles and patterns grounded in
examples, and may hold specific observed antipatterns once they recur enough to matter.

Specifications are forward-facing. They catalogue the desired functionality, nail down the
public API, and may hint at internal strategies. A specification must be explicit about the
expected declared functors — whatever stands in for `super_categories`. It separates, and
does not repeat, the methods expected to arrive by inheritance, keeping one source of truth,
though naming a few to ground an example is fine. A lattice specification should say that it
mentions no cardinality, and that cardinality arrives compositionally along a chain of
functors landing in `Sets()` — not from a direct functor to `Sets()`.
