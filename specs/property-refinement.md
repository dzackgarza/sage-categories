# Property categories and refinement

This specification owns property subcategories, inverse images, containment, and same-object refinement.
It implements D16, D25, D83, D89, D91, D101, and D125.

It consumes the generic calculus from [functor.md](functor.md).
It provides property categories to [undecidable-properties.md](undecidable-properties.md).
The private class update belongs to [resolution.md](resolution.md).

## Property category

Let `P` be an object property on a category `C`.
The objects that satisfy `P` form a full subcategory `C.P()` whose inclusion is an isofibration, declared in `Fun(C.P(), C).Monomorphisms().Isofibrations()` (D170).
The declaration retains its subcategory monomorphism

\[
j_P:C.P()\hookrightarrow C.
\]

`C` declares the axiom `P` by its name and the proposition that decides membership in `C.P()` ([leaves.md](leaves.md#property-categories); D148).
`C.P()` exists implicitly and owns the mathematical meaning of `P`.
A proposition that no existing method supplies applies a SymPy `Predicate` subclass, whose exact SymPy handlers decide the cases known to that owner.

The registered axiom identifier determines the public `is_P()` spelling.
`cat_kernel` generates that method once on the ambient implementation class (D175).
It returns the declared proposition, the value of the private deciding method (D142).

For a morphism property, the construction starts from `Mor(C)`.
For a functor property, it starts from `Fun(C, D)`.

## Property containment

A relation between property categories is a declared subcategory monomorphism.
If every object with property `P` has property `Q`, retain

\[
C.P()\hookrightarrow C.Q().
\]

Construction, restriction, placement, and compiled inheritance use this monomorphism.
The repository does not store the relation as predicate implication metadata.

Intersections use pullbacks of subcategory monomorphisms.
The pullback retains its projections and its monomorphism into `C`.

## Inverse images

Let `F: D -> C` be a named functor.
Let `j_P: C.P() -> C` be a property subcategory.
Define

\[
F^{-1}(C.P())=D\times_C C.P().
\]

The pullback retains both projections.
Its projection to `D` is the inverse-image subcategory monomorphism.

For a structure functor `F: D -> C` and an axiom `P` declared on `C`, this pullback defines `D.P()` (D148).
When two structure functors of `D` have targets that both declare `P`, their pullbacks define one `D.P()`: the pullbacks are equivalent by composition, Sage's C3 linearization determines their order, and coherence is assumed with the first one chosen (D37, D159).
`Modules(R).Finite()` means one thing, whether `Finite` reaches `Modules(R)` through a direct functor to `Sets()` or through one that passes through `Groups().Commutative()`.
The axiom registration exposes its predicate and implementation classes.

See Mathlib's [`ObjectProperty.inverseImage`](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/ObjectProperty/Basic.html) and [full subcategories](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/ObjectProperty/FullSubcategory.html).

## Same-object refinement

A positive property result refines the same owned value into its property subcategory.
The value keeps its mathematical identity.
Its strongest known category and compiled class become more specific.

The static projection represents this operation with the exact compiler-generated
nominal type for the refined category.  That type has the same associated
`ObjectType`, `ElementType`, and `MorphismType` values as the ambient category and
the generated dynamic class exposes both applicable method surfaces.  It is the
static intersection of the ambient and property declarations, not a new value, a
structural protocol, a Python boolean type guard, or a wrapper
([functor.md](functor.md#static-semantic-projection); `POL-TYPE-018`,
`POL-TYPE-020`, `POL-TYPE-025`, `POL-TYPE-027`).

These routes use one refinement operation:

- direct construction in `C.P()`;
- placement through a subcategory that maps to `C.P()`;
- a positive assumption of the membership proposition;
- an exact `True` result from `ask()`.

A value already constructed enters `C.P()` by the assumption route, `assume(X.is_P())`; a constructor takes construction data, and `C.P()` has exactly the constructors of `C` (D150).

After refinement, placement decides the same proposition as `True`.
The property implementation class supplies its operations directly on the value.

A negative result records no placement.
An `Unknown` result changes nothing.

Refinement preserves:

- object identity;
- parent, domain, and codomain data;
- defining mathematical data;
- private engine values;
- public images owned by named functors.

Several established properties combine through their pullback intersection.
The refined class contains each applicable implementation class once.

## Defining predicate

The axiom declaration on the ambient category supplies the proposition that decides membership in the property category.
That proposition is written in terms of methods that already exist on the ambient category, or applies a SymPy predicate the leaf defines ([leaves.md](leaves.md#property-categories); D148).

Placement supplies an exact positive handler result.
Other exact handlers can use owned data, a cited theorem, or a private engine.

Any Python helper for this declaration remains private.
It does not define another predicate type, proposition type, or property category.

The finite-set declaration template is [finite-set-minimal-template.py](finite-set-minimal-template.py); the poset template [poset-minimal-template.py](poset-minimal-template.py) declares a new predicate with its handlers and implements the axiom subcategory through its identity structure functor (D156); the finite-poset template [finite-poset-minimal-template.py](finite-poset-minimal-template.py) implements an axiom reached by pullback.

## Property construction

Direct construction in `C.P()` establishes the property by construction.
It returns the same mathematical kind with `C.P()` as its strongest placement.

```python
f = Mor(Sets()).Monomorphisms()(A, B)(rule)
```

An interactive assumption reaches the same placement:

```python
f = Mor(Sets())(A, B)(rule)
assume(f.is_injective())
```

Theory code and engines construct the category they establish.
They do not add assumptions for their own results.

## Compiled public surface

The property category declares its local `ObjectType`, `ElementType`, and `MorphismType` additions.
Positive refinement places each applicable property class before its ambient class.
Existing ambient operations remain available.

The generated `is_P()` method reaches structural descendants through selected functors and compiled inheritance.
A leaf writes no duplicate ambient method.

The private runtime uses Sage refinement and dynamic-class facilities.
Those mechanics add no public property record.

## Acceptance conditions

The architecture satisfies this specification when:

- each object property gives a full subcategory and its inclusion, a monomorphism and isofibration;
- the property category owns its predicate meaning;
- its public predicate and applied proposition use SymPy;
- the registered axiom determines the generated public method name;
- the generated method returns the category-owned membership proposition;
- property containment uses exact subcategory monomorphisms;
- intersections and inverse images use retained pullbacks;
- each positive route uses one same-object refinement;
- negative and unknown results add no placement;
- private declaration helpers add no second proposition model;
- descendants receive property methods through compiled inheritance;
- no leaf duplicates the property category, predicate meaning, or refinement operation.
