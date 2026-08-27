# Ring objects

This specification defines `Rings(C)` in a supplied ambient category.
The current implementation milestone remains `Sets()` and its universal constructions.
Ring objects are a later vertical acceptance target for that foundation.

The governing policies are `POL-MATH-019`, `POL-MATH-022`, `POL-MATH-023`,
`POL-GEN-001`, `POL-GEN-017`, `POL-CAT-027`, `POL-CAT-030`, `POL-CAT-031`,
and `POL-DOC-003` through `POL-DOC-009`.

## Ambient categorical data

Let `C` be a category with finite products.
Write `C_x` for the specified cartesian monoidal category `(C, product, 1)`.
The constructor `Rings(C)` uses this structure.

An object of `Rings(C)` is an object `R in C` with morphisms

\[
+:R\times R\longrightarrow R,
\qquad
\mathbin{\cdot}:R\times R\longrightarrow R,
\]

\[
0:1\longrightarrow R,
\qquad
1:1\longrightarrow R,
\qquad
-:R\longrightarrow R.
\]

These morphisms make `(R, +, 0, -)` an object of
`Groups(C_x).Additive().Commutative()`.
They make `(R, multiplication, 1)` an object of `Monoids(C_x).Multiplicative()`.
The left and right distributivity diagrams commute.

This is the traditional internal ring-object definition from the
[nLab ring-object definition](https://ncatlab.org/nlab/show/ring%2Bobject),
in its finite-product form.

## Morphisms

A morphism in `Rings(C)` is a morphism `f:R -> S` in `C` that preserves
addition, multiplication, zero, and one.
It then preserves additive inverses by the internal group laws.

`Rings(Sets())` is the category of ordinary unital rings and ring homomorphisms.
`Rings(C).Commutative()` is the full property subcategory defined by symmetry of
the multiplication morphism.

## Structural functors

`Rings(C)` is the subobject of
`Semirings(C) * Groups(C_x).Additive().Commutative()` whose two additive-monoid
images are one object with one addition and zero. Its defining presentation retains
both projections. The complete immediate structural tuple is

```python
def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
    return (
        self.product_projection(0),
        self.product_projection(1),
    )
```

The semiring projection supplies both operation roles and their unit points.
The additive-group projection supplies inversion and subtraction.
Both paths reach one canonical additive monoid and one canonical object of `C`.

The `Cat()` specialization states its laws as equalities of functors, as
`Semirings(Cat())` does in
[Magmas, monoids, and semirings](magmas-monoids-semirings.md#the-cat-specialization).

## Owned operations

`Rings(C)` owns the compatibility between the semiring and additive-group structures.
The two projections retain all five structure morphisms.
Unary `-` and subtraction come from `Groups(C_x).Additive().Commutative()`.
Addition, multiplication, zero, and one come from `Semirings(C)`.

For `C = Sets()`, the internal diagrams give the usual element operations.
For a general `C`, the morphisms and diagrams above remain the public definition.

## Acceptance conditions

- `Rings(C)` retains one carrier object in `C`.
- Its structure maps are morphisms in `C`.
- Its axioms are commutative diagrams in `C`.
- Its structural functors target `Semirings(C)` and
  `Groups(C_x).Additive().Commutative()`.
- `Rings(Sets())` gives ordinary rings.
- `Rings(C).Commutative()` is a full property subcategory.
- Inherited operations arrive through the two retained projections.

The complete governing set also includes `POL-MATH-001` through `POL-MATH-013`,
`POL-MATH-034`, `POL-CAT-001` through `POL-CAT-020`, `POL-CAT-033`,
`POL-CAT-043` through `POL-CAT-047`, `POL-CAT-054`, `POL-CAT-061` through
`POL-CAT-087`, `POL-FUN-001` through `POL-FUN-006`, `POL-FUN-023`, and
`POL-DOC-003` through `POL-DOC-009`.
