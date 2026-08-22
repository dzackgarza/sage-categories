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

The arrow-category foundation includes:

- arrow categories and commuting squares;
- hom and endomorphism categories;
- monomorphism, epimorphism, isomorphism, and automorphism categories;
- cores and wide subcategories;
- slices, coslices, subobjects, superobjects, covering objects, and covered objects.

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

Treat private fields as private to their owner or documented subclass contract.
Ask another object through its public mathematical interface.
Invoke Python protocols through public syntax such as `f(x)`, `iter(x)`, and `len(x)`.

Give every value the type that names its mathematical role.
Distinguish categories, objects, elements, arrows, functors, rings, sets, domains, and codomains.

Never use `object` as a type.
Use `Any` only for a parameter that genuinely accepts an arbitrary membership candidate.
Never return `Any`.

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

Continue while the next in-scope action is clear and safe.
Do not stop at an administrative artifact when implementation remains.

End each substantive work unit in a focused commit.
Do not leave required work only in the working tree.
Preserve unknown files until their ownership is known.

Never use destructive Git operations without an explicit request.
Never use `rm`; use recoverable system trash for disposable files.
