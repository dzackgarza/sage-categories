# Property categories and refinement

This specification owns property subcategories, inverse images, containment, and same-object refinement.
It implements D16, D25, D83, D89, D91, and D101.

The governing policies are `POL-MATH-016`, `POL-MATH-025`, `POL-MATH-029`, `POL-MATH-034`, `POL-MATH-035`, `POL-CAT-018` through `POL-CAT-020`, `POL-CAT-043`, `POL-CAT-044`, `POL-CAT-060`, `POL-CAT-067` through `POL-CAT-069`, `POL-CAT-082` through `POL-CAT-091`, and `POL-FUN-024` through `POL-FUN-027`.

See [undecidable-properties.md](undecidable-properties.md) for propositions, typed queries, `ask()`, assumptions, and exact handlers.
See [resolution.md](resolution.md) for the private Sage class update.

## Property axiom

Let `P` be a registered property axiom on a category `C`.
The axiom declares the functorial category construction

\[
C\longmapsto C.P()
\]

and the subcategory monomorphism

\[
j_P:C.P()\hookrightarrow C.
\]

The objects of `C.P()` are exactly the objects of `C` that satisfy `P`.
The property category owns this membership proposition.
Its implementation classes own the operations that require `P`.

The registered axiom identifier determines the public `is_P()` spelling.
The kernel generates that method once on the applicable ambient implementation class.
The method returns the containment proposition for `C.P()`.

For a property of morphisms, the same construction starts from `Mor(C)`.
For a property of functors, it starts from `Fun` or `Fun(C, D)`.

## Property containment

A relation between two property categories is a declared subcategory monomorphism.
For example, if every object with property `P` has property `Q`, retain

\[
C.P()\hookrightarrow C.Q().
\]

Category placement and composition with this monomorphism decide the corresponding positive containment proposition.
The monomorphism is the operational object used by construction, restriction, and compiled inheritance.

Intersections use pullbacks of subcategory monomorphisms.
The pullback retains its projections and presents the combined property as a subcategory of `C`.

## Inverse images

Let `F: D -> C` be a named functor and let `j_P: C.P() -> C` be a property subcategory.
Define

\[
F^{-1}(C.P())
=
D\times_C C.P().
\]

The pullback retains both projections.
Its projection to `D` is the subcategory monomorphism of the inverse image.

When `F` defines the inherited property `P` on `D`, this inverse image is `D.P()`.
The axiom registration and compiler expose its containment proposition and implementation classes.

This construction is the standard inverse image of an object property.
See Mathlib's [`ObjectProperty.inverseImage`](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/ObjectProperty/Basic.html) and [full subcategories](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/ObjectProperty/FullSubcategory.html).

## Same-object refinement

A positive property result refines the same owned value into its property subcategory.
The value keeps its mathematical identity.
Its strongest known category and compiled implementation class become more specific.

These routes use one refinement operation:

- direct construction in `C.P()`;
- placement in a property subcategory that maps to `C.P()`;
- an active positive assumption of the containment proposition;
- an exact `True` result from `ask()`.

After refinement, category placement decides the same containment proposition as `True`.
The property implementation class supplies its new operations directly on the value.

A negative result records no property placement.
An `Unknown` result changes nothing.
Later exact knowledge can still refine the value.

Refinement preserves:

- object identity;
- parent, domain, and codomain data;
- defining mathematical data;
- private engine values;
- images owned by named functors.

If several established properties apply, their pullback intersection gives the combined property category.
The refined class contains each applicable property implementation once.

## Predicate-backed property categories

A concrete property category can choose predicate-backed containment.
It inherits `PredicateSubcategory` and implements its private abstract `_predicate()` method.

```python
class ConcreteProperty(PredicateSubcategory):
    def _predicate(self, X: Ambient.ObjectType) -> Proposition:
        return exact_relation_about(X)
```

The method states the defining proposition.
It does not return a Python decision.
`ask()` owns evaluation.

Placement is a fast positive route because construction or refinement already established the predicate.
Placement is not a separate definition of membership.

The complete finite-set example exists only in [finite-set-minimal-template.py](finite-set-minimal-template.py).

## Property construction

Direct construction in `C.P()` establishes the property by construction.
It returns the same owned mathematical kind with the property category as its strongest placement.

```python
f = Mor(Sets()).Monomorphisms()(A, B)(rule)
```

An interactive assumption of the generated proposition reaches the same placement:

```python
f = Mor(Sets())(A, B)(rule)
assume(f.is_injective())
```

Theory code and computation engines construct the category they establish.
They do not create assumptions for their own results.

## Compiled public surface

The property category declares `ObjectType`, `ElementType`, and `MorphismType` additions under the same rules as every category.
Positive refinement places the applicable property class before the ambient class.
Existing ambient operations remain available.

The generated `is_P()` method reaches structural descendants through selected functors and compiled inheritance.
For example, a property pulled back along a named functor is available on the source implementation class.
The leaf writes no duplicate ambient method.

The private runtime uses Sage's refinement and dynamic-class facilities.
Those mechanics add no public property record.

## Acceptance conditions

The property architecture satisfies this specification when:

- each property axiom constructs `C.P()` and its monomorphism into `C`;
- the registered axiom identifier determines the generated public method name;
- each generated property method returns the owned containment proposition;
- every property containment relation is its exact subcategory monomorphism;
- intersections and inherited properties use retained pullbacks;
- direct construction, positive assumption, positive placement, and exact positive decision use one same-object refinement;
- negative and unknown decisions add no property placement;
- a predicate-backed category supplies only its defining `_predicate()` method;
- property implementation classes add only operations valid under the property;
- descendants receive property methods through selected functors and compiled inheritance;
- no leaf duplicates the property category, containment proposition, or refinement operation.
