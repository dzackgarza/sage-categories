# Ordinals

This document specifies the ordinal model used by the cardinality framework.

Ordinal operations specified as predicates follow the proposition interface in
[Property refinement](property-refinement.md). Applying one returns a proposition.
`ask()` returns its decision.

The governing policies are `POL-MATH-022` through `POL-MATH-025`, `POL-MATH-034`,
`POL-MATH-035`, `POL-GEN-017`, `POL-GEN-020`, `POL-GEN-021`, `POL-CAT-001`, `POL-CAT-054`, `POL-CAT-060`, `POL-CAT-071`,
`POL-CAT-083`, `POL-CAT-085`, `POL-FUN-002`, `POL-FUN-003`, `POL-FUN-035`,
`POL-SET-025`, `POL-SET-026`, and `POL-DOC-010` through `POL-DOC-013`.

## Ordinal model

`Ordinals()` is the skeletal category of ordinals. An ordinal is an object of it,
exactly as a cardinal is an object of `Cardinal()`
([cardinality.md](cardinality.md), "Cardinal model"):

```python
OrdinalObject = Ordinals().ObjectType
```

`Ordinals()` owns ordinal construction, both families of ordinal arithmetic, the order
predicates, and expression normalization. Sage supplies private runtime support only.

Two families of operations act on these objects. The Hessenberg natural sum and natural
product are commutative; they are the semiring operations below. The ordinary ordinal
sum, product, and power are noncommutative and carry explicit names; `Ordinals()` owns
them as local operations.

An expression that no normalization rule evaluates is retained exactly.

### The ordinal semiring

The commutative semiring of ordinals under the Hessenberg operations is the point
functor of `Ordinals()` into `Semirings(Cat())`
([functor.md](functor.md#point-categories-and-point-functors)):

```python
# Cat().Point(Ordinals())
def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
    return (Fun(self, Semirings(Cat())).Faithful().inclusion(),)
```

It regards the category `Ordinals()` as one object of `Semirings(Cat())`. That
category's objects, its two operation morphisms, its unit points, and its laws are
defined in [Semirings](magmas-monoids-semirings.md#semirings). `Ordinals()` adds only
which functors those are: its additive operation functor is the natural sum with unit
object `0`, and its multiplicative operation functor is the natural product with unit
object `1`.

Mathlib establishes the semiring laws for these two operations. Its
[`Mathlib/SetTheory/Ordinal/NaturalOps.lean`](https://github.com/leanprover-community/mathlib4/blob/v4.14.0/Mathlib/SetTheory/Ordinal/NaturalOps.lean)
defines "natural addition and multiplication on ordinals, also known as the Hessenberg
sum and product" and states that "they're commutative, associative, preserve order, have
the usual `0` and `1` from ordinals, and distribute over one another". Its
`OrderedCommSemiring NatOrdinal` instance supplies the two distributivity fields
`left_distrib` and `right_distrib`, the two absorption fields `zero_mul` and `mul_zero`,
and `mul_comm`.

The `Cat()`-level law data is the equations between these functors
([functor.md](functor.md#ambient-algebraic-categories)). `Ordinals()` is skeletal, so the
natural sum and the natural product each select one representative and the laws hold as
equalities
([Laws in the supplied ambient](magmas-monoids-semirings.md#laws-in-the-supplied-ambient)).

The point functor supplies complete compiled roles and exact constructor conversions.
Those constructors initialize the semiring state before they expose its methods. The
level shift places `zero()` and `one()` on the category and `+` and `*` on its objects
([Semirings](magmas-monoids-semirings.md#semirings)). One level down, the object
surface belongs to the category `Ordinals()` and the element surface belongs to the
objects of `Ordinals()`:

```python
Ordinals().zero()
Ordinals().one()

alpha + beta
alpha * beta
```

At stage `[1]` the same element surface acts on the morphisms of `Ordinals()`, which is
the functorial action of the two natural operations.

### Public ordinal constructors

```python
Ordinals()

Ordinals()(value)
Ordinals().omega(index)

omega0
```

`Ordinals()(value)` accepts:

- An existing `OrdinalObject`.

- A nonnegative Python `int`.

`Ordinals().omega(index)` constructs the initial ordinal \(\omega_{\text{index}}\).

Examples:

```python
Ordinals()(0)
Ordinals()(5)

Ordinals().omega(0)       # omega0
Ordinals().omega(1)
Ordinals().omega(Ordinals().omega(1))
```

Negative finite ordinals raise `ValueError`.

### Ordinal expression forms

The private expression model supports:

- Finite ordinals.

- Initial ordinals.

- Hessenberg natural sums.

- Hessenberg natural products.

- Ordinary ordinal sums.

- Ordinary ordinal products.

- Ordinary ordinal powers.

### `Ordinals()` API

The category supplies the two variadic natural operations:

```python
O = Ordinals()

O.natural_sum(*ordinals)
O.natural_product(*ordinals)
```

`O.zero()` and `O.one()` arrive on the same surface through the point functor.

`Ordinals()` is one cached category. Construction is cached by expression.
Reconstructing an equal expression returns the same ordinal object.

### Natural arithmetic

Python `+` and `*` are the semiring operations: the Hessenberg natural sum and the
Hessenberg natural product. Each is a morphism out of a product,

\[
\alpha,\mu:\operatorname{Ordinals}()\times\operatorname{Ordinals}()
\longrightarrow\operatorname{Ordinals}(),
\]

so applying one to a pair returns an ordinal. It presents no diagram and carries no cone.

```python
alpha + beta
alpha * beta

n + alpha
n * alpha
```

Natural sum:

- Flattens nested natural sums.

- Combines all finite terms.

- Sorts symbolic terms by representation.

- Removes additive zero.

- Produces a commutative symbolic expression.

Natural product:

- Distributes across represented natural sums.

- Flattens nested natural products.

- Multiplies finite factors.

- Removes multiplicative identity.

- Returns zero if one factor is zero.

- Sorts symbolic factors.

Ordinal exponentiation is `alpha.ordinal_power(beta)`. `**` keeps the categorical
meaning fixed by `POL-CAT-088`.

### Ordinary ordinal arithmetic

Ordinary noncommutative operations have explicit names:

```python
alpha.ordinal_sum(beta)
alpha.ordinal_product(beta)
alpha.ordinal_power(beta)
```

These methods evaluate finite inputs exactly.

They also simplify:

```python
alpha.ordinal_sum(0) == alpha
0.ordinal_sum(alpha) == alpha

alpha.ordinal_product(0) == 0
alpha.ordinal_product(1) == alpha

alpha.ordinal_power(0) == 1
0.ordinal_power(beta) == 0       # positive beta
1.ordinal_power(beta) == 1
```

Other cases remain symbolic.

### Ordinal object API

Every ordinal supplies:

```python
alpha.is_initial()
alpha.initial_index()
alpha.cardinality()
```

It supports structural hashing and proposition-valued comparisons:

```python
alpha == beta
alpha != beta
alpha < beta
alpha <= beta
alpha > beta
alpha >= beta
```

### Ordinal order support

The exact handler for `ask(alpha <= beta)` recognizes:

- Structural equality.

- Exact order between finite ordinals.

- Every finite ordinal below a represented nonfinite ordinal.

- Order between initial ordinals through recursive index comparison.

When no exact handler decides a represented comparison, `ask()` returns `Unknown`.

Thus ordinal comparison operators state order propositions. They do not replace an
unresolved proposition with Boolean `False`.

### Ordinal representations

Representative output is:

```text
5
ω_0
ω_1
ω_0 # ω_1
ω_0 ⊗ ω_1
(ω_0 +o ω_1)
(ω_0 *o ω_1)
(ω_0 ^o ω_1)
```

Here:

- `#` denotes natural sum.

- `⊗` denotes natural product.

- `+o`, `*o`, and `^o` denote ordinary ordinal operations.

## Cardinality of ordinals

`alpha.cardinality()` maps ordinal expressions into cardinal expressions.

The rules are:

\[
|n|=n,
\qquad
|\omega_\alpha|=\aleph_\alpha.
\]

Both natural and ordinary ordinal sums map to cardinal sums:

\[
|\alpha+\beta|=|\alpha|+|\beta|.
\]

Both natural and ordinary ordinal products map to cardinal products:

\[
|\alpha\beta|=|\alpha||\beta|.
\]

Ordinary ordinal powers do not map to cardinal exponentiation in general. For example,

\[
2^\omega=\omega,
\qquad
|2^\omega|=\aleph_0,
\qquad
|2|^{|\omega|}=2^{\aleph_0}.
\]

This follows from the limit-power rule in Enderton,
[Elements of Set Theory, Chapter 8, Theorem 8L](https://docs.ufpr.br/~hoefel/ensino/CM304_CompleMat_PE3/livros/Enderton_Elements%20of%20set%20theory_%281977%29.pdf).

`alpha.ordinal_power(beta).cardinality()` uses exact ordinal normalization rules. If no
rule determines the value, it returns a symbolic cardinal expression for the ordinal
power. It does not replace that expression with cardinal exponentiation.
