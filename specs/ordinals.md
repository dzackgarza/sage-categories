# Ordinals

This document specifies the ordinal model used by the cardinality framework.

Ordinal operations specified as predicates follow the proposition interface in
[Property refinement](property-refinement.md). Applying one returns a proposition.
`ask()` returns its decision.

The governing policies are `POL-MATH-022` through `POL-MATH-025`, `POL-MATH-034`,
`POL-MATH-035`, `POL-CAT-054`, `POL-CAT-060`, `POL-CAT-085`, `POL-CAT-087`,
`POL-SET-025`, and `POL-SET-026`.

## Ordinal model

`Ordinals()` is one parent representing the commutative semiring of ordinals under Hessenberg operations.

Ordinals are elements of that parent:

```python
Ordinal = OrdinalSemirings().ElementType
```

This differs from the cardinal model:

- A cardinal is an object of `Cardinal()`.

- An ordinal is an element of `Ordinals()`.

An ordinal semiring is a semiring whose carrier consists of ordinals, whose addition is
Hessenberg natural sum, and whose multiplication is Hessenberg natural product.
Its multiplication is commutative.

Let `P(S)` be this property of objects `S in Semirings()`. Then
`OrdinalSemirings()` is the full subcategory defined by `P`. Its objects are the
semiring objects satisfying `P`. Property refinement retains each same owned semiring.
Its fixed-endpoint morphism categories are definitionally those of `Semirings()`:

\[
\operatorname{Mor}(\mathbf{OrdinalSemirings})(A,B)
=
\operatorname{Mor}(\mathbf{Semirings})(A,B).
\]

Thus the inclusion is fully faithful by construction. No fullness predicate or runtime
check exists. This follows mathlib's
[`CategoryTheory.ObjectProperty.FullSubcategory`](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/ObjectProperty/FullSubcategory.html)
definition: objects carry an object property, while morphisms ignore that property.

The ambient predicate application is:

```python
S.is_ordinal_semiring()
```

It returns `P(S)`. `ask()` uses its computational routes.

The complete immediate structural tuple is:

```python
def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
    return (Fun(self, Semirings()).FullyFaithful().inclusion(),)
```

The selected semiring functors supply both monoid structures and the set image fixed by
the semiring presentation. Sage supplies private runtime support only.

### Public ordinal constructors

```python
OrdinalSemirings()
Ordinals()

Ordinals()(value)
Ordinals().omega(index)

omega0
```

`Ordinals()(value)` accepts:

- An existing `Ordinal`.

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

The parent supplies:

```python
O = Ordinals()

O.zero()
O.one()

O.natural_sum(*ordinals)
O.natural_product(*ordinals)
```

`Ordinals()` is cached.

### Natural arithmetic

Python `+` and `*` mean Hessenberg natural operations:

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

The implementation does not define `**` as natural ordinal exponentiation.

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
