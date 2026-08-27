# Magmas, monoids, and semirings

This specification defines algebraic objects in a supplied ambient category.
The current implementation milestone remains `Sets()` and its universal constructions.
These algebraic categories are vertical acceptance targets for that foundation.

The governing policies are `POL-MATH-019`, `POL-MATH-022`, `POL-MATH-023`,
`POL-GEN-001`, `POL-GEN-016`, `POL-GEN-017`, `POL-CAT-027`, `POL-CAT-030`,
`POL-CAT-031`, and `POL-DOC-003` through `POL-DOC-009`.

## Contents

- [Ambient categorical data](#ambient-categorical-data)
- [Magmas](#magmas)
- [Additive and multiplicative operation roles](#additive-and-multiplicative-operation-roles)
- [Monoids](#monoids)
- [Groups](#groups)
- [Semirings](#semirings)
- [Structural functors](#structural-functors)
- [Owned operations](#owned-operations)
- [The `Cat()` specialization](#the-cat-specialization)
- [Definition sources](#definition-sources)
- [Acceptance conditions](#acceptance-conditions)

## Ambient categorical data

Let `V` be a category `C` with a selected tensor bifunctor

\[
\mathbin{\otimes}:C\times C\longrightarrow C.
\]

`Magmas(V)` requires this bifunctor.
`Monoids(V)` requires a selected monoidal extension

\[
(C,\mathbin{\otimes},I,a,\lambda,\rho).
\]

The structured argument `V` retains `C` and all selected ambient structure.
Two tensor or monoidal structures on one underlying category give different values of
`V` and therefore different magma and monoid categories.

The internal semiring construction uses finite products.
Write `C_x` for the specified cartesian monoidal category `(C, product, 1)`.
Then `Semirings(C)` uses `Monoids(C_x)` for both of its monoid structures.
It does not select another monoidal structure carried by the same underlying category.
`Semirings(Sets())` gives ordinary semirings.

The definitions use morphisms and commutative diagrams in `C`.
They remain meaningful when `C` has no element-based description.

## Magmas

An object of `Magmas(V)` is an object `X in C` with a multiplication morphism

\[
\mu_X:X\otimes X\longrightarrow X.
\]

A morphism from `(X, mu_X)` to `(Y, mu_Y)` is a morphism `f:X -> Y` in `C`
such that

\[
f\circ\mu_X=\mu_Y\circ(f\otimes f).
\]

`Magmas(V)` is the category of these objects and morphisms.
Its defining presentation retains `X`, `mu_X`, and their endpoint equation.
The carrier projection is the selected structural functor to `C`:

```python
def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
    return (self.product_projection(0),)
```

The operation projection to `Mor(C)` remains an ordinary retained functor.
It does not contribute the morphism category's public method surface.

`Magmas(V)` owns the operation-neutral interface:

```python
M.operation()
M.combine(x, y)
f.is_magma_homomorphism()
```

`operation()` returns the morphism `mu_X:X tensor X -> X` in `C`.
`combine(x, y)` applies that morphism through the selected point-stage map.
The homomorphism method returns the owned preservation predicate.

## Additive and multiplicative operation roles

The two operation-role subcategories are

```python
Magmas(V).Additive()
Magmas(V).Multiplicative()
```

They retain the same carrier, multiplication morphism, and morphisms.
Each selects one standard operation role.
Their complete immediate structural tuples are

```python
# Magmas(V).Additive()
def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
    return (Fun(self, Magmas(V)).FullyFaithful().inclusion(),)
```

```python
# Magmas(V).Multiplicative()
def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
    return (Fun(self, Magmas(V)).FullyFaithful().inclusion(),)
```

When `V` is monoidal, the selected roles expose `+`
and `*` on unit-stage points.
For cartesian `V`, two generalized points `x,y:T -> X` combine through

\[
T\xrightarrow{\Delta_T}T\times T
 \xrightarrow{x\times y}X\times X
 \xrightarrow{\mu_X}X.
\]

This diagram is the generalized-point meaning of the element syntax.
For `C = Sets()`, it is the usual binary operation on elements.

When `V` is braided monoidal, `Magmas(V).Commutative()` is defined by equality of
`mu_X` and its composite with the braiding on `X tensor X`.
It propagates to both operation roles through property inverse image.

## Monoids

An object of `Monoids(V)` is an object `X in C` with morphisms

\[
\mu_X:X\otimes X\longrightarrow X,
\qquad
\eta_X:I\longrightarrow X.
\]

The associativity diagram uses the associator `a` of `V`.
The unit diagrams use `lambda` and `rho`.
A monoid morphism preserves both `mu` and `eta`.

This is the standard monoid-object construction in a monoidal category.
Its immediate structural functor forgets associativity and the unit:

```python
def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
    return (Fun(self, Magmas(V)).Faithful().inclusion(),)
```

A notation-neutral monoid owns

```python
M.operation()
M.identity_element()
M.combine(x, y)
```

Here `identity_element()` returns the generalized point `eta_X:I -> X`.

The operation-role subcategories are

```python
Monoids(V).Additive()
Monoids(V).Multiplicative()
```

They are inverse images of the matching `Magmas(V)` roles.
Their complete immediate structural tuples preserve both category branches:

```python
# Monoids(V).Additive()
def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
    return (
        Fun(self, Monoids(V)).FullyFaithful().inclusion(),
        Fun(self, Magmas(V).Additive()).Faithful().inclusion(),
    )
```

```python
# Monoids(V).Multiplicative()
def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
    return (
        Fun(self, Monoids(V)).FullyFaithful().inclusion(),
        Fun(self, Magmas(V).Multiplicative()).Faithful().inclusion(),
    )
```

The additive role names the unit `zero()`.
The multiplicative role names it `one()`.
The identity point is one owned morphism with the selected role name.

`Monoids(V).Additive().Commutative()` denotes commutative additive monoid objects.
The matching multiplicative expression denotes commutative multiplicative monoid objects.

## Groups

When `V` is cartesian monoidal, `Groups(V)` is the full property subcategory of
`Monoids(V)` on objects with an inversion morphism

\[
\iota_X:X\longrightarrow X
\]

that satisfies the left and right inverse diagrams. A monoid morphism between group
objects preserves inversion. The additive role
`Groups(V).Additive()` exposes unary `-` and subtraction. The commutative additive
group category is `Groups(V).Additive().Commutative()`.

Its complete immediate structural tuple is

```python
def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
    return (Fun(self, Monoids(V)).FullyFaithful().inclusion(),)
```

The selected functor supplies the monoid operation and unit. `Groups(V)` adds only
the inversion morphism and its laws.

## Semirings

Let `C` have finite products.
A strict internal semiring object in `C` consists of one object `X in C` with:

- a commutative additive monoid structure on `X`;
- a multiplicative monoid structure on `X`;
- left and right distributivity diagrams;
- left and right zero-absorption diagrams.

Both monoid structures use the cartesian product of `C`.
A semiring morphism is a morphism in `C` that preserves both structures.

The strict internal category is the subcategory of
`Monoids(C_x).Additive().Commutative() * Monoids(C_x).Multiplicative()` whose two
carrier images agree and whose distributivity and absorption diagrams commute.
Its defining presentation retains both component projections.

The complete immediate structural tuple is

```python
def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
    return (
        self.product_projection(0),
        self.product_projection(1),
    )
```

Both routes reach one canonical object of `C`.
The structural diamond supplies both operation roles to that object.

`Semirings(C)` owns the compatibility laws and the combined role surface.
Its object interface exposes both unit points.
Its point interface exposes `+` and `*` through the two retained monoid structures.

```python
X.zero()
X.one()
x + y
x * y
```

Here `X in Semirings(C)`. The points `x` and `y` have a stage on which the two
operation morphisms can act. For `C = Cat()`, `X` is a category, `zero()` and `one()`
return objects of `X`, and the two operators apply its addition and multiplication
functors.

For `C = Sets()`, the diagrams give the familiar formulas

\[
x(y+z)=xy+xz,
\qquad
(x+y)z=xz+yz,
\qquad
0x=0=x0.
\]

These formulas are consequences of the internal diagrams.

## Structural functors

Each selected functor acts on objects and morphisms.
Its point action comes from its morphism action.

The additive and multiplicative refinements use inclusions.
The semiring component functors come from the generic subobject-of-product construction.
Longer routes to `C` arise through the carrier projections of `C_x`.

## Owned operations

| Category | New public mathematics |
| --- | --- |
| `Magmas(V)` | Multiplication morphism and operation-preservation predicate. |
| `Magmas(V).Additive()` | Additive operation role. |
| `Magmas(V).Multiplicative()` | Multiplicative operation role. |
| `Monoids(V)` | Associativity, unit point, and unit-preserving morphisms. |
| `Monoids(V).Additive()` | `zero()` in the additive role. |
| `Monoids(V).Multiplicative()` | `one()` in the multiplicative role. |
| `Groups(V)` | Inversion and the inverse laws. |
| `Groups(V).Additive()` | Unary `-` and subtraction. |
| `Semirings(C)` | Distributivity, absorption, and both selected monoid structures. |

Inherited capabilities come from the listed structural functors.
Each defining predicate returns its owned proposition.

## The `Cat()` specialization

The family parameter supports algebraic objects whose carrier is a category.
Thus the intended placement for category-valued ordinal and cardinal arithmetic is
`Semirings(Cat())`.

An object of `Semirings(Cat())` is a strict internal semiring object in the ordinary
category `Cat()`.
Its algebraic laws are equalities of functors, as the laws of `Semirings(Sets())` are
equalities of maps.
The two operation functors are formed over the finite products of `Cat()`.

`Cardinal()` and `Ordinals()` satisfy that strictness because both are skeletal.
Each operation selects one representative, so `(a + b) + c` and `a + (b + c)` name one
object and the law is an equality of functors.

`Rings(Cat())` follows the same convention; see [Ring objects](rings.md).

## Definition sources

The monoid-object definition and its associativity and unit diagrams follow the
[nLab definition of a monoid in a monoidal category](https://ncatlab.org/nlab/show/monoid%2Bin%2Ba%2Bmonoidal%2Bcategory).

The strict internal ring and semiring pattern uses the finite-product interpretation
described by the
[nLab ring-object definition](https://ncatlab.org/nlab/show/ring%2Bobject).

The notation-role catalogues use the Sage reference sections for
[magmas](https://doc.sagemath.org/html/en/reference/categories/sage/categories/magmas.html),
[additive monoids](https://doc.sagemath.org/html/en/reference/categories/sage/categories/additive_monoids.html),
[monoids](https://doc.sagemath.org/html/en/reference/categories/sage/categories/monoids.html),
and [semirings](https://doc.sagemath.org/html/en/reference/categories/sage/categories/semirings.html).

## Acceptance conditions

- `Magmas(V)` retains the selected tensor bifunctor of `V`.
- `Monoids(V)` retains the selected monoidal structure of `V`.
- `Groups(V)` uses the selected cartesian monoidal structure of `V`.
- Their objects and morphisms live in the underlying category `C`.
- Every algebraic law is a diagram in `C`.
- `Semirings(C)` uses `C_x`, the specified cartesian monoidal structure on `C`.
- `Semirings(Sets())` gives ordinary semirings.
- Both semiring component routes reach one canonical object of `C`.
- Every immediate structural edge is an owned functor.
- Deeper inherited operations arrive through functor composition.
- `Semirings(Cat())` states its laws as equalities of functors.

The complete governing set also includes `POL-MATH-001` through `POL-MATH-013`,
`POL-MATH-034`, `POL-MATH-035`, `POL-CAT-001` through `POL-CAT-020`,
`POL-CAT-033`, `POL-CAT-043` through `POL-CAT-047`, `POL-CAT-054`,
`POL-CAT-061` through `POL-CAT-087`, `POL-FUN-001` through `POL-FUN-006`,
`POL-FUN-023`, and `POL-DOC-003` through `POL-DOC-009`.
