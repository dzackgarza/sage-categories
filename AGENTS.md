# Agent instructions

## Project purpose

`sage-categories` is a foundational category framework for Sage-based mathematics.
It is not an application repository or a domain-specific research corpus.

Read these files before substantive work:

- `README.md` defines the goal and mathematical philosophy.
- `CONTRIBUTING.md` is the coding-policy index. Its `POL-*` identifiers are stable review references.

The package owns its mathematical category graph and public API.
Sage supplies computation objects, algorithms, coercion, and selected runtime machinery.

## Current implementation scope

Work in mathematical dependency order:

1. `Cat`, functor categories, natural transformations, and natural isomorphisms.
2. The full arrow-category family and its object, element, and arrow surfaces.
3. The method compiler for `ObjectType`, `ElementType`, and `ArrowType` inheritance.
4. The owned category `Sets()` and its universal constructions.

The current implementation surface ends at `Sets()`.
Complete this foundation before extending the theory graph.

Use later structures only as vertical acceptance examples.
An algebra's cardinality must eventually come from its structural path to `Sets()`.
A lattice isometry must eventually pass through module homs to set homs.
These examples test the foundation; they do not authorize implementation of algebras, modules, or lattices now.

The arrow-category foundation includes:

- arrow categories and commuting squares;
- hom and endomorphism categories;
- monomorphism, epimorphism, isomorphism, and automorphism categories;
- cores and wide subcategories;
- slices, coslices, subobjects, superobjects, covering objects, and covered objects.

## Mathematical structure as implementation compression

A short mathematical correction can expose a missing foundation rather than a missing method.
Unfold the structure that makes the correction true before adding a local operation.

For example, a product of sets must receive `cardinality()` because its apex is an object of `Sets()`.
The product construction supplies projections and a structural route to that apex.
The method compiler then exposes the operation owned by the set implementation.

Adding `cardinality()` directly to a product class would preserve the missing relation.
It would also create another local task for coproducts, limits, subobjects, and every later construction.
The categorical foundation makes those operations consequences of one structure.

This is the main form of implementation compression in this repository:

- one category owns a generic operation;
- one functor states each change of structure;
- one universal construction retains its defining arrows;
- the compiler turns those declarations into a direct public surface.

Prefer a foundational correction when it removes an entire family of apparent method tasks.
Do not preserve a mistaken architecture with a cheaper local implementation.

Kernel complexity is justified only when it removes repetition from theory code.
The theory layer must read like the mathematics it implements.
A new category should state its new data and immediate structural functors, then inherit the rest.

Foundational categories remain valuable before later theories use them.
Their value is the mathematical structure they make expressible, not their current number of callers.

## Mathematical judgment

Treat a precise user description as a proposed mathematical model of the code.
When the live implementation lacks the named category, functor, arrow, or universal property, surface that discrepancy.
Do not substitute a nearby class, method, constructor, or data record.

Category theory is not a metaphor in this package.
A functor must map objects and arrows.
A subobject must include its monomorphism.
A universal construction must include its universal arrows.
A computation-engine value must be used to construct an owned mathematical object.

One false foundational assertion invalidates each downstream conclusion that uses it.
When such an assertion appears, rederive the architecture from the mathematical definitions and the live code.
Do not optimize a local patch, diagnostic count, or passing specimen built on the false premise.

Implementation obstacles do not change mathematical ownership.
A recursion, type error, slow path, or failing test is a fact about the implementation.
Fix that implementation fact without moving an operation to the wrong object or weakening its type.

Predicates follow their definitions and their available algorithms.
Return `Unknown` when the implementation cannot determine a result.
Do not replace missing knowledge with a fabricated Boolean answer.

Prefer standard categorical constructions and established algorithms over local encodings.
If the current vocabulary cannot state the general mathematical object, treat that absence as the finding.
Extend the foundation instead of hiding the gap inside a special case.

## Core categorical architecture

A category owns its implementations and constructors.
A functor constructs an implementation in another category.

For each category `C`:

- `C.ObjectType` implements objects of `C`.
- `C.ElementType` implements elements when the theory uses them.
- `C.ArrowType` implements arrows of `C`.
- `C(...)` is the category-owned constructor.

The same architecture applies to objects, elements, and arrows.
Do not solve one surface with a mechanism that cannot support the other two.

The following are categories and therefore objects of `Cat`:

- `Ar(C)`, `EndAr(C)`, and `AutAr(C)`;
- `Fun(C, D)`;
- `Hom_C(x, y)`.

Use `HomCatType`, not `HomSetType`, at the `Cat` level.
For example, a hom category between sheaves can have natural transformations as its objects.
Only `Sets()` identifies its hom objects with sets of functions.

The `Cat` level supplies the uniform category constructors:

- `HomCategory()`, `EndCategory()`, and `AutCategory()`;
- `ArrowCategory()`, `EndArrowCategory()`, and `AutArrowCategory()`.

The generic `ArrowType` stores its domain and codomain and exposes `domain()` and `codomain()`.
If an arrow predicate names a subcategory, implement it as containment in that subcategory.
For example, test `f in C.Monomorphisms()` instead of inspecting the Python class of `f`.
Prefer an arrow or functor formulation when the mathematical definition names a relation or transport.

For each functor `F: C -> D`:

- `F.domain()` is `C`.
- `F.codomain()` is `D`.
- `F.on_object()` constructs the image of an object.
- `F.on_morphism()` constructs the image of an arrow.
- `F.on_element()` exists only when the mathematical functor acts on elements.

Every functor is explicit.
Only selected structural functors contribute methods to the public object surface.
Ordinary mathematical functors remain available without changing public inheritance.

For an object `x`, cache one canonical `F(x)` in each reachable category.
Two structural routes to the same category must produce the same implementation.
Reject route incoherence during method compilation.

Compile the public method surface from category declarations:

- local declarations take precedence;
- routes to the same declaring category share one method owner;
- unrelated declarations with the same name are errors;
- forwarding descriptors expose inherited methods directly on the public object;
- descriptor installation must support Python special methods.

Derive supercategory information from structural functors.
Do not maintain a second inheritance or propagation registry.

## Universal constructions

A categorical construction acts on objects and arrows.
A parent-only result does not implement a categorical construction.

Retain the data that states the universal property:

- a product retains its diagram, projections, and mediating arrow;
- a coproduct retains its diagram, injections, and mediating arrow;
- a limit retains its cone and universal map;
- a colimit retains its cocone and universal map.

Let each apex inherit methods from the category in which it lives.
Use functor composition and natural transformations to move structure.
Do not create a separate method-propagation system for constructions.

For a construction functor `F: Diag(C) -> C`, give `F(D)` the parent `Image(F)`.
The immediate structural supercategory of `Image(F)` is `C`.
Construct the corresponding object of `C` from the diagram `D`.
This applies to products, coproducts, limits, and colimits.

A covering object of `Y` is a pair `(X, p: X -> Y)` with `p` an epimorphism.
It is not the arrow `p` alone.

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

For a predicate on a set `B`, construct the selected subset `A` together with its inclusion `A -> B`.
The subset is an object of `Sets()`.
The inclusion is an arrow in `Sets()`.
This must support infinite subobjects such as the even integers and prime integers inside `ZZ`.

`Sets()` owns:

- membership and iteration when available;
- cardinality, including finite, infinite, symbolic, and unknown results;
- function sets and exponentials;
- products and coproducts of arbitrary small families;
- general limits and colimits;
- predicate subobjects and their inclusion arrows.

In `Sets()`, the hom object, function set, and exponential are one object:

\[
\operatorname{Hom}_{\mathbf{Set}}(X,Y)=Y^X.
\]

The power set is the corresponding exponential into the two-element set:

\[
\mathcal{P}(X)=2^X=\operatorname{Hom}_{\mathbf{Set}}(X,2).
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

Every object whose parent is `Sets()` receives the complete `Sets.ObjectType` method surface.
This includes ordinary sets, products, coproducts, subsets, `Y^X`, and `Hom_Set(X, Y)`.
Products and subsets must delegate to the categorical constructions that create them.
They must not define parallel set APIs.

Propagate these operations along structural functors and universal constructions.
Do not implement a second copy of a set operation in a higher category.

## Mathematical ownership

Start with the mathematical object, data, laws, hypotheses, and arrows.
Choose a Python representation only after those facts are explicit.

Use these ownership rules:

- categories own generic operations;
- objects own operations on themselves;
- arrows own properties and operations whose definitions name the arrow;
- functors own changes of structure;
- universal constructions own their defining arrows;
- computation engines return data used to construct owned mathematical objects.

Keep these notions distinct:

- an object and a presentation of it;
- an element and its coordinates;
- an arrow and a matrix representing it;
- a subobject and its inclusion;
- a theorem and a runtime algorithm;
- a mathematical result and an implementation-engine value.

Represent a chosen subobject of `B` by a monomorphism `f: A -> B`.
Obtain `B` from `f.codomain()`.
Do not duplicate the codomain or inclusion data in storage fields.

Implement the general mathematical notion.
Recover special cases through restriction, category refinement, or specialized functors.
Do not patch only the example that exposed a missing general construction.

## Sage boundary

The owned framework defines the mathematical categories and their inclusions.
Native Sage categories do not define this package's mathematical supercategory graph.

Use Sage for:

- `Parent` and `Element` runtime support;
- homsets and morphisms;
- coercion;
- dynamic classes and refinement;
- category joins and construction classes;
- established exact algorithms.

Cross into Sage through an explicit realization functor or owned computation boundary.
A Sage realization is not a structural functor.
Its Python methods must not enter the public mathematical API by accident.

Do not modify Sage category classes.
Do not add owned methods to Sage classes.
Do not preserve a Sage method spelling as a second public owner.

Use an established Sage algorithm before writing a local implementation.
When Sage lacks an algorithm, keep the operation at its correct owned interface and return an appropriate unknown result.

## Public API and types

Shape every API from the mathematics.
Do not derive it from current class layouts, storage fields, or available method names.

Use one owner, one public name, and one public export for each operation.
Use established mathematical and Sage terminology.
Name an accessor for the exact object or arrow that it returns.

Use standard hom notation and dispatch.
`X.Hom(Y)` takes `Y` as its codomain and delegates to `X._Hom_(Y)`.
Callers use `X.Hom(Y)`.
Only the owning public dispatch may call the private `_Hom_` method.

Treat private fields as private to their owner or documented subclass contract.
Ask another object through its public mathematical interface.
Invoke Python protocols through public syntax such as `f(x)`, `iter(x)`, and `len(x)`.

Give every value the type that names its mathematical role.
Distinguish categories, objects, elements, arrows, functors, rings, sets, domains, and codomains.

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

Do not use runtime `setattr` to assemble the mathematical API.
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

Every assertion must state a mathematical proposition or an essential type invariant.
Test the real category compiler and public API.

As applicable, assert:

- category and parent;
- domain and codomain;
- images of elements;
- identity and composition;
- functor laws;
- naturality;
- universal arrows;
- mathematical equality.

Use the smallest specimen that distinguishes correct behavior from a plausible failure.
Use a real Sage process for Sage behavior.

Do not test implementation layout, diagnostic totals, source text, caches, or correction history.
Do not add a test whose only purpose is to assert the absence of a previous mistake.
A passing test is evidence only for the proposition that it executes.

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

Before editing, inspect the repository tree and the complete target artifact.
Preserve existing and concurrent work.

Work on the requested mathematical object, not a plan, count, checker result, or reviewer verdict.
The first deliverable of a work unit is a falsifiable specimen.

When a correction invalidates a foundational assumption, stop the local patch.
Reconstruct the requested mathematical object and resume from the corrected model.

If the category graph or method owner is wrong, stop runtime debugging.
Fix `Cat`, the arrow categories, the method compiler, and `Sets()` in dependency order.
During that migration, move each required behavior to its new owner before deleting its old implementation.

Continue while the next in-scope action is clear and safe.
Do not stop at an administrative artifact when implementation remains.

End each substantive work unit in a focused commit.
Do not leave required work only in the working tree.
Preserve unknown files until their ownership is known.

Never use destructive Git operations without an explicit request.
Never use `rm`; use recoverable system trash for disposable files.
