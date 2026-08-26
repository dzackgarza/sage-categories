# Magmas, monoids, and semirings

This specification fixes the first algebraic categories after `Sets()`. Standard
universal algebra and category theory are assumed.

The governing policies are `POL-MATH-034`, `POL-CAT-001`, `POL-CAT-033`,
`POL-CAT-054`, `POL-CAT-060`, `POL-CAT-085`, and `POL-CAT-087`.

## Contents

- [Magmas](#magmas)
- [Additive and multiplicative operation roles](#additive-and-multiplicative-operation-roles)
- [Monoids](#monoids)
- [Semirings](#semirings)
- [Structural functors](#structural-functors)
- [Owned operations](#owned-operations)
- [Definition sources](#definition-sources)
- [Acceptance conditions](#acceptance-conditions)

## Magmas

An object of `Magmas()` is a set `X` with a binary operation

\[
\mu:X\times X\longrightarrow X.
\]

A morphism `f : (X, mu_X) -> (Y, mu_Y)` is a set map satisfying

\[
f(\mu_X(x,y))=\mu_Y(f(x),f(y)).
\]

The magma category is a subcategory of the product category with factors `Sets()` and
`Mor(Sets())`. The defining equations identify the source and target of the second
component with the required powers of the first component. Thus `Magmas()` is an object
of `Cat().Products().Subobjects()`.

`Magmas()` owns the operation-neutral structure:

```python
M.operation()
M.combine(x, y)
f.is_magma_homomorphism()
```

`operation()` returns the owned set morphism `mu`. `combine(x, y)` evaluates that morphism.
The homomorphism method returns the owned preservation predicate.

The complete immediate structural tuple is:

```python
def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
    return (self.product_projection(0),)
```

The second product projection maps `(X, mu)` to `mu` in `Mor(Sets())`. It remains an
ordinary functor. Only the first projection supplies inherited operations.

## Additive and multiplicative operation roles

`Magmas()` does not select a notation for its operation. The two axiomatic subcategories
are:

```python
Magmas().Additive()
Magmas().Multiplicative()
```

They retain the same carrier, operation morphism, elements, and homomorphisms. Each selects
one algebraic role and its standard syntax:

```python
x + y  # Magmas().Additive()
x * y  # Magmas().Multiplicative()
```

Each is the full subcategory defined by its operation-role property. For its objects
`A, B`, `Mor(Magmas().Additive())(A, B)` is definitionally `Mor(Magmas())(A, B)`, and
likewise for the multiplicative role.

Their complete immediate structural tuples are:

```python
# Magmas().Additive()
def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
    return (Fun(self, Magmas()).FullyFaithful().inclusion(),)
```

```python
# Magmas().Multiplicative()
def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
    return (Fun(self, Magmas()).FullyFaithful().inclusion(),)
```

The selected operation role is the only new mathematics in each refinement. A bare
magma exposes neither `+` nor `*`.

The generic property `Magmas().Commutative()` is defined by

\[
\forall x,y,\qquad \mu(x,y)=\mu(y,x).
\]

It propagates to the additive and multiplicative refinements through the property
inverse-image construction.

## Monoids

An object of `Monoids()` is a magma with an associative operation and a neutral element
`e`. Its defining equations are

\[
\mu(\mu(x,y),z)=\mu(x,\mu(y,z)),
\]

and

\[
\mu(e,x)=x=\mu(x,e).
\]

A monoid morphism preserves the operation and the neutral element. Thus `Monoids()` is a
subcategory of `Magmas()`, but this inclusion is not full.

The complete immediate structural tuple is:

```python
def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
    return (Fun(self, Magmas()).Faithful().inclusion(),)
```

A bare monoid remains notation-neutral. It owns:

```python
M.operation()
M.identity_element()
M.combine(x, y)
```

It does not determine whether the operation is written additively or multiplicatively.
The corresponding axiomatic subcategories are:

```python
Monoids().Additive()
Monoids().Multiplicative()
```

They are the inverse images of `Magmas().Additive()` and
`Magmas().Multiplicative()` along the monoid inclusion. Their complete immediate tuples
preserve both category branches:

```python
# Monoids().Additive()
def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
    return (
        Fun(self, Monoids()).FullyFaithful().inclusion(),
        Fun(self, Magmas().Additive()).Faithful().inclusion(),
    )
```

```python
# Monoids().Multiplicative()
def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
    return (
        Fun(self, Monoids()).FullyFaithful().inclusion(),
        Fun(self, Magmas().Multiplicative()).Faithful().inclusion(),
    )
```

Each refinement is full in `Monoids()`: for its objects `A, B`, its `Mor(-)(A, B)` is
definitionally `Mor(Monoids())(A, B)`. Its inclusion in the matching magma role is
not full because a monoid morphism must preserve the neutral element.

The additive refinement exposes `+` and `zero()`. The multiplicative refinement exposes
`*` and `one()`. Each named unit is the monoid's neutral element in the selected
notation.

`Monoids().Additive().Commutative()` denotes commutative additive monoids. The matching
multiplicative expression denotes commutative multiplicative monoids.

## Semirings

An object of `Semirings()` consists of one carrier set with:

- a commutative additive monoid `(X, +, 0)`;
- a multiplicative monoid `(X, *, 1)`;
- left and right distributivity;
- absorption of multiplication by zero.

The laws are

\[
x(y+z)=xy+xz,
\qquad
(x+y)z=xz+yz,
\]

and

\[
0x=0=x0.
\]

A semiring morphism preserves both monoid structures. It therefore preserves `0`, `1`,
addition, and multiplication.

The semiring category is a subcategory of the product of
`Monoids().Additive().Commutative()` and `Monoids().Multiplicative()`. Its defining
conditions identify their set images and impose distributivity and zero absorption.

The complete immediate structural tuple is:

```python
def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
    return (
        self.product_projection(0),
        self.product_projection(1),
    )
```

Both functors reach the same set image. The structural diamond must retain both operation
catalogues and that canonical image.

`Semirings()` fixes the roles of its two monoid structures. Its public object surface
includes `zero()` and `one()`. Its public element surface includes `+` and `*`.

## Structural functors

Each listed functor acts on objects and morphisms. It acts on elements when the corresponding
change of structure has an element map.

The additive and multiplicative refinements use inclusions because they retain the magma
operation. The two semiring component functors come from the generic subobject-of-product
construction. They are not category-only inheritance edges.

Longer routes to `Sets()` arise only by composition. No algebraic category adds a direct
set functor for convenience.

## Owned operations

Ownership follows this table:

| Category | New public mathematics |
| --- | --- |
| `Magmas()` | Binary operation morphism and operation-preserving predicate. |
| `Magmas().Additive()` | Additive notation. |
| `Magmas().Multiplicative()` | Multiplicative notation. |
| `Monoids()` | Associativity, neutral element, and unit-preserving morphisms. |
| `Monoids().Additive()` | `zero()` in additive notation. |
| `Monoids().Multiplicative()` | `one()` in multiplicative notation. |
| `Semirings()` | Distributivity, zero absorption, and the two selected monoid structures. |

Predicates return applied propositions. Their exact handlers can use finite checks,
construction theorems, or private computation engines. `ask()` returns their decisions.

## Definition sources

The algebraic laws use the Sage reference sections for
[magmas](https://doc.sagemath.org/html/en/reference/categories/sage/categories/magmas.html),
[additive monoids](https://doc.sagemath.org/html/en/reference/categories/sage/categories/additive_monoids.html),
[monoids](https://doc.sagemath.org/html/en/reference/categories/sage/categories/monoids.html),
and [semirings](https://doc.sagemath.org/html/en/reference/categories/sage/categories/semirings.html).
These sections distinguish additive and multiplicative operation roles. This package
puts their common structure in the notation-neutral `Magmas()` and `Monoids()` owners.

## Acceptance conditions

- A bare magma or monoid exposes no additive or multiplicative operator.
- `Magmas().Additive()` and `Magmas().Multiplicative()` retain one operation-neutral
  magma image.
- `Monoids()` preserves the neutral element in every morphism.
- Additive monoids expose `+` and `zero()`.
- Multiplicative monoids expose `*` and `one()`.
- A semiring has one carrier and two distinct monoid structures.
- Semiring morphisms preserve both structures.
- The two semiring routes reach one canonical set image.
- Every immediate structural edge is an owned functor.
- Deeper inherited operations arrive through functor composition.

The governing policies are `POL-MATH-001` through `POL-MATH-013`, `POL-MATH-022`,
`POL-MATH-034`, `POL-MATH-035`, `POL-CAT-001` through `POL-CAT-020`, `POL-CAT-033`,
`POL-CAT-043` through `POL-CAT-047`, `POL-CAT-054`, `POL-CAT-061` through
`POL-CAT-086`, `POL-FUN-001` through `POL-FUN-006`, `POL-FUN-023`, and `POL-DOC-003`
through `POL-DOC-009`.
