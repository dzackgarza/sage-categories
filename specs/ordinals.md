# Ordinals

This document specifies the ordinal model used by the cardinality framework.

All ordinal properties and relations follow the proposition interface in
[Property refinement](property-refinement.md). They return propositions. Only `ask()`
returns `True`, `False`, or `Unknown`.

## Ordinal model

`Ordinals()` is one parent representing the commutative semiring of ordinals under Hessenberg operations.

Ordinals are elements of that parent:

```python
Ordinal = OrdinalSemirings().ElementType
```

This differs from the cardinal model:

- A cardinal is an object of `Cardinalities()`.

- An ordinal is an element of `Ordinals()`.

`OrdinalSemirings` declares `Sets()` and Sage’s commutative semirings as supercategories.

### Public ordinal constructors

```python
OrdinalSemirings()
Ordinals()

ordinal(value)
omega(index)

omega0
```

`ordinal(value)` accepts:

- An existing `Ordinal`.

- A nonnegative Python `int`.

- A nonnegative Sage `Integer`.

`omega(index)` constructs the initial ordinal \(\omega_{\text{index}}\).

Examples:

```python
ordinal(0)
ordinal(5)

omega(0)       # omega0
omega(1)
omega(omega(1))
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

O(value)
O.zero()
O.one()
O.initial(index)

O.natural_sum(*ordinals)
O.natural_product(*ordinals)
O.proves_le(alpha, beta)
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
alpha.expression()

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

Ordinary ordinal powers map to cardinal powers:

\[
|\alpha^\beta|=|\alpha|^{|\beta|}.
\]

This bridge is implemented in [Ordinal.cardinality()](/home/dzack/research/src/dzack_research/preamble/categories/sets/ordinals.py:316).
