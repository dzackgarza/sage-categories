# Ring objects

This specification defines `Rings(C)` in a supplied ambient category.
The initial executable boundary is [minimal leaf scaffolding](leaf-scaffolding.md).

The governing policies are `POL-MATH-019`, `POL-MATH-022`, `POL-MATH-023`,
`POL-GEN-001`, `POL-GEN-017`, `POL-GEN-020`, `POL-GEN-021`, `POL-CAT-027`,
`POL-CAT-030`, `POL-CAT-031`,
and `POL-DOC-003` through `POL-DOC-009`.

## Ambient categorical data

Let `C` be a category with finite products.
Write `C_x` for the specified cartesian monoidal category `(C, product, 1)`.
The constructor `Rings(C)` uses this structure.
The ambient is a parameter. Fixing it gives an instance, and no instance is the
definition.

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

Each chosen addition or multiplication law is a morphism out of a product in `C`, in the sense stated by
[Magmas, monoids, and semirings](magmas-monoids-semirings.md#magmas).
`(R, +, 0, multiplication, 1)` is then an object of `Semirings(C)`, which owns the
distributivity and absorption diagrams
([Semirings](magmas-monoids-semirings.md#semirings)).
`Rings(C)` adds the additive inversion morphism and its two inverse diagrams, and
nothing else.
Sage records the same relation for the ordinary instance: `Rings()` is
`Semirings().AdditiveInverse()`
([Sage `Rings`](https://doc.sagemath.org/html/en/reference/categories/sage/categories/rings.html)).

This is the traditional internal ring-object definition from the
[nLab ring object](https://ncatlab.org/nlab/show/ring%2Bobject) entry, section
"Definition / Traditional definition": "a ring object consists of an object R in a
cartesian monoidal category C together with morphisms a : R x R -> R (addition),
m : R x R -> R (multiplication), 0 : 1 -> R (zero), e : 1 -> R (multiplicative
identity), - : R -> R (additive inversion), subject to commutative diagrams in C that
express the usual ring axioms".

## Morphisms

A morphism in `Rings(C)` is a morphism `f:R -> S` in `C` that preserves
addition, multiplication, zero, and one.
It then preserves additive inverses by the internal group laws.

`Rings(C).Commutative()` is the full property subcategory defined by symmetry of
the multiplication morphism.

## Instances

At `C = Sets()`, an object is an ordinary unital ring and a morphism is a ring
homomorphism. Sage's
[`Rings`](https://doc.sagemath.org/html/en/reference/categories/sage/categories/rings.html)
names the same objects: "The category of rings. Associative rings with unit, not
necessarily commutative."

At `C = Cat()`, an object is a category `R` with functors

\[
+,\ \mathbin{\cdot}:R\times R\longrightarrow R,
\qquad
\iota:R\longrightarrow R,
\]

two functors `1 -> R` that select the zero object and the one object, and every ring law
an equality of functors
([Laws in the supplied ambient](magmas-monoids-semirings.md#laws-in-the-supplied-ambient)).
Its additive part is a commutative group object in `Cat()`; the general group-object
instance there is the strict 2-group
([Groups](magmas-monoids-semirings.md#groups)).

`Cardinal()` is not an object of `Rings(Cat())` because cardinal addition has no inversion functor.
It remains an object of `Semirings(Cat())`.

## Structure functors

Let

\[
\mathcal A=\operatorname{Monoids}(C_x).\operatorname{Additive}().\operatorname{Commutative}().
\]

The additive-structure functors from `Semirings(C)` and
`Groups(C_x).Additive().Commutative()` both land in \(\mathcal A\).
The defining category is their pullback:

\[
\operatorname{Rings}(C)
=
\operatorname{Semirings}(C)
\times_{\mathcal A}
\operatorname{Groups}(C_x).\operatorname{Additive}().\operatorname{Commutative}().
\]

Thus the two branches have one addition and one zero.
The pullback retains both projections and its comparison data.
The complete immediate structure-functor tuple is

```python
def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
    return (
        self.product_projection(0),
        self.product_projection(1),
    )
```

The semiring projection supplies the additive and multiplicative element interfaces and their unit points.
The additive-group projection supplies inversion and subtraction.
Sage's dynamic-class MRO contains each shared additive-monoid and ambient-object class once.
The compatibility of the two branches is the retained pullback mathematics above; the
kernel does not reconcile the diamond by comparing branchwise constructor data or public
functor images.

Both projections state their laws in the supplied ambient
([Laws in the supplied ambient](magmas-monoids-semirings.md#laws-in-the-supplied-ambient)).

## Owned operations

`Rings(C)` owns the compatibility between the semiring and additive-group structures.
The two projections retain all five structure morphisms.
Unary `-` and subtraction come from `Groups(C_x).Additive().Commutative()`.
Addition, multiplication, zero, and one come from `Semirings(C)`.

At `C = Sets()`, the internal diagrams give the usual element operations.
For a general `C`, the morphisms and diagrams above remain the public definition.

## Acceptance conditions

- `Rings(C)` retains one underlying object in `C`.
- Its structure maps are morphisms in `C`.
- Its axioms are commutative diagrams in `C`.
- Its structure functors target `Semirings(C)` and
  `Groups(C_x).Additive().Commutative()`.
- `Rings(Sets())` gives ordinary rings; `Rings(Cat())` states its laws as equalities of
  functors.
- `Rings(C).Commutative()` is a full property subcategory.
- Every structure map is a morphism out of a product, never a universal construction.
- Inherited operations arrive through the two retained projections.

The complete governing set also includes `POL-MATH-001` through `POL-MATH-013`,
`POL-MATH-034`, `POL-CAT-001` through `POL-CAT-020`, `POL-CAT-033`,
`POL-CAT-043` through `POL-CAT-047`, `POL-CAT-054`, `POL-CAT-061` through
`POL-CAT-087`, `POL-FUN-001` through `POL-FUN-006`, `POL-FUN-023`, and
`POL-DOC-003` through `POL-DOC-009`.
