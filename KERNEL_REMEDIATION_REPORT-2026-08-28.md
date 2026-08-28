# Kernel remediation report

Date: 2026-08-28

## Scope

This report reconciles the current kernel plan with the user's transcript corrections.
The relevant transcript is `e8ad9875-810f-4b88-b553-902320e67825`.

Kernel defects come first.
Leaf work appears only when a leaf violates its contract with the corrected kernel.

The governing references are:

- `POL-CAT-002`, `POL-CAT-053`, `POL-CAT-061`, and `POL-CAT-096`;
- `POL-KERNEL-001`, `POL-KERNEL-018`, `POL-KERNEL-028`, and `POL-KERNEL-029`;
- `POL-FUN-002`, `POL-FUN-003`, `POL-FUN-033`, and `POL-FUN-035`;
- `POL-LEAF-054`, `POL-LEAF-058`, and `POL-LEAF-059`;
- `POL-DOC-012` and `POL-DOC-013`;
- `specs/functor.md`, `specs/leaves.md`, and `specs/resolution.md`.

## Settled kernel contract

### Category-owned classes

Each category declares these nested classes directly:

```python
class C(Category):
    class ObjectType:
        ...

    class ElementType:
        ...

    class MorphismType:
        ...
```

The kernel fills the bases of those same classes.
The declaration and public implementation use one name for each mathematical kind.

A property subcategory is an independent category class.
It uses Sage's category-with-axiom connection to its ambient category.

### Objects, points, and generalized elements

`Cat().ObjectType` implements categories.
`Cat().MorphismType` implements functors.

`Cat().ElementType` implements points

\[
*\longrightarrow C,
\]

where `*` is the terminal category.
These points are the actual objects of `C`.
Therefore, every `C.ObjectType` inherits `Cat().ElementType`.

For `X in C`, `C.ElementType` implements points

\[
1_C\longrightarrow X.
\]

A generalized element has the form

\[
T\longrightarrow X.
\]

It is not an `ElementType` value unless `T = 1_C`.
For a category `C`, generalized elements with domain `T` are objects of `Fun(T, C)`.
This follows the nLab entry [generalized element](https://ncatlab.org/nlab/show/generalized+element),
section "Global elements" and the definition immediately before "Examples".

`C.MorphismType` is `Mor(C).ObjectType`.
A morphism of `C` is an object of the morphism category.

### Functor ownership

Many ordinary functors can have the same endpoints.
The endpoints select `Fun(C, D)`, not an object of that category.

Each named functor owns:

- its object action;
- its morphism action;
- its public images;
- its image cache;
- its pure constructor-data conversions.

`structure_functors()` selects ordinary functors for inheritance.
Selection does not change their mathematical action.

For a point `t: 1_C -> X`, `F.on_morphism(t)` gives

\[
F(1_C)\longrightarrow F(X).
\]

A supplied morphism `1_D -> F(1_C)` gives the point of `F(X)` by composition.
A generalized element `T -> X` maps to `F(T) -> F(X)` and remains generalized.

### Constructor conversion and inherited methods

A selected functor owns one pure conversion from source construction data to target constructor data.
The public functor action uses that conversion.
The kernel uses the same conversion to initialize the target class on the structured source instance.

Public `F(x)` returns the separate image owned by `F`.
An inherited method runs on `x` through ordinary Python MRO.
The target constructor has already initialized the state that the method reads on `x`.

Thus, for a method `f` owned by the target category,

\[
x.f() = F(x).f()
\]

as a mathematical equality.
Method dispatch does not replace `x` with `F(x)`.

All selected paths to one target class must supply the same target constructor datum.
Different named functors can still own different public images.

### Property categories

A property subcategory owns one membership proposition.
For example, `X.is_finite()` returns membership in `Sets().Finite()`.

Direct construction, an exact positive decision, and an active assumption use one property constructor.
Positive admission refines the same owned value.

### Universal constructions

Each universal construction retains its defining diagram and morphisms.
Its family selects the monomorphism into the ambient category.
The apex receives ambient methods through that selected functor and the class compiler.

Products preserve the supplied family order.
No constructor sorts an indexed family.

## Kernel remediation

### K1. Compile the classes that categories declare

Make every category declare `ObjectType`, `ElementType`, and `MorphismType` directly.
Make the compiler fill the bases of those classes.
Use Sage's dynamic-class technique for the final C3 classes.

Acceptance:

- one class name exists for each mathematical kind;
- property subcategories use independent Sage axiom classes;
- no second runtime classification controls class selection.

### K2. Correct the point hierarchy

Compile `Cat().ElementType` as the point class `* -> C`.
Make every `C.ObjectType` inherit it.
Compile `C.ElementType` as points `1_C -> X`.
Treat `C.MorphismType` as `Mor(C).ObjectType`.

Acceptance:

- an object of `C` is a `Cat().ElementType` with parent `C`;
- an element of `X` is a point with parent `X`;
- `T -> X` with nonterminal `T` remains a generalized element;
- a morphism of `C` is not classified as a point of `C`.

### K3. Give each functor one constructor conversion

Make the functor retain the conversion used by both its public action and superclass initialization.
Compose these conversions along selected functors.

Acceptance:

- public `F(x)` returns the image owned by `F`;
- two functors with equal endpoints keep independent image caches;
- selected paths to one target class agree on target constructor data;
- no conversion reads a partly initialized source value.

### K4. Use direct inherited execution

Build the selected target classes into the source class MRO.
Initialize every reachable class once through C3.
Run inherited methods on the structured source instance.

Acceptance:

- ordinary and special methods use ordinary Python lookup;
- an inherited method reads initialized target state on the source instance;
- `x.f()` and `F(x).f()` have the same mathematical result;
- the public functor image remains separately inspectable.

### K5. Normalize property containment and refinement

Give each property category one membership proposition and one trusted constructor.
Route `ask()` and assumptions through that owner.
Use category containment for established placement.

Acceptance:

- `is_P()` returns the owned proposition;
- exact positive decisions refine through the property constructor;
- refinement keeps Python and mathematical identity;
- leaves contain no property-dispatch machinery.

### K6. Put generic constructions at their mathematical owners

Make product, coproduct, limit, colimit, subobject, and morphism-property families retain their defining data.
Let descendants inherit their public methods through selected functors.

Acceptance:

- each construction acts on objects and morphisms;
- each result retains its universal morphisms;
- morphism-property categories own inversion and related operations;
- leaves add only the structure required to lift the generic result.

### K7. Keep the public constructor surface exact

Use one named constructor for each mathematical construction.
Accept the strongest minimal semantic input.

Acceptance:

- a poset constructor accepts a plain Python set and an order callable;
- it constructs the pair `(X, R)`;
- the named projection `(X, R) |-> X` supplies set inheritance;
- no public constructor mutates another module's public types;
- templates remain design pseudocode.

## Leaf remediation after the kernel

### `Sets()`

Keep membership, point construction, set maps, cardinality, and exact set algorithms in `Sets()`.
Make `Sets.ElementType` implement points `1 -> X` only.
Use inherited state directly on structured descendants.
Let universal families retain their own defining data.

### `PartiallyOrderedSets()`

Keep only the set `X`, relation `R`, order predicates, monotone maps, and order-specific lifts.
Use the named projection `(X, R) |-> X` as the selected functor.
Let its one conversion supply the `Sets()` constructor data.

### Property leaves

Declare each property category as an independent category class.
Give it direct nested implementation classes and one membership proposition.
Keep exact decision procedures in private computation modules.

### Named number sets

Place each named set through its one-object category and selected monomorphisms.
Use the generic property constructor for established properties.

### Algebraic leaves

Keep each structure map and law at its standard category.
Use named projections to the immediate ambient category.
Let composite selected paths supply inherited set operations.

## Acceptance sequence

1. Construct two different functors with the same endpoints and obtain their separate images.

2. Select one functor and verify direct inherited method execution on the source instance.

3. Construct a point `* -> C` as a `Cat().ElementType` and a `C.ObjectType`.

4. Construct a generalized element `T -> C` in `Fun(T, C)` and verify that it is not a `Cat().ElementType` for nonterminal `T`.

5. Construct a morphism of `C` as an object of `Mor(C)`.

6. Construct a finite-set property proposition and refine the same set after an exact positive decision.

7. Construct a poset from a Python set and order callable, then use inherited set methods on that poset.

8. Construct two selected paths to one target class and verify agreement of their constructor data while preserving separate functor images.

9. Construct two diagrams with one apex and recover distinct universal data for each diagram.

10. Construct product data in supplied order and recover projections with the same indices.
