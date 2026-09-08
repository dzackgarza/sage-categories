# Ordinals

This document specifies the ordinal model used by the cardinality framework.

`Ordinals()` owns each ordinal predicate meaning.
Its public representation and evaluation follow [Propositions and `ask()`](undecidable-properties.md).
Applying a predicate returns a SymPy proposition.
Only `ask()` returns `True`, `False`, or Sage `Unknown`.

The governing policies are `POL-MATH-022` through `POL-MATH-025`, `POL-MATH-034`, `POL-MATH-035`, `POL-GEN-017`, `POL-GEN-020`, `POL-GEN-021`, `POL-CAT-001`, `POL-CAT-054`, `POL-CAT-060`, `POL-CAT-071`, `POL-CAT-083`, `POL-CAT-085`, `POL-FUN-002`, `POL-FUN-003`, `POL-FUN-035`, `POL-SET-025`, `POL-SET-026`, `POL-SET-037`, `POL-SET-038`, and `POL-DOC-010` through `POL-DOC-013`.

## Ordinal model

`Ordinals()` is the skeletal category of ordinals.
An ordinal is an object of it, exactly as a cardinal is an object of `Cardinal()` ([cardinality.md](cardinality.md), "Cardinal model"):

```python
OrdinalObject = Ordinals().ObjectType
```

`Ordinals()` owns ordinal construction, both families of ordinal arithmetic, the order predicates, and expression normalization.
Sage supplies private runtime support only.

Two families of operations act on these objects.
Python `+` and `*` denote ordinary ordinal sum and product.
The Hessenberg natural sum and natural product use explicit method names.
Ordinal power uses an explicit method because `**` retains its categorical meaning.

An expression that no normalization rule evaluates is retained exactly.

### Arithmetic ownership

`Ordinals().ObjectType` declares ordinary ordinal sum and product as its local `+` and `*` operations.
This local declaration takes precedence over the generic categorical product and coproduct conveniences.
The categorical constructions remain available as `Ordinals().Products()` and `Ordinals().Coproducts()`.

Mathlib establishes the commutative semiring laws for the two Hessenberg operations.
Its [`Mathlib/SetTheory/Ordinal/NaturalOps.lean`](https://github.com/leanprover-community/mathlib4/blob/v4.14.0/Mathlib/SetTheory/Ordinal/NaturalOps.lean) defines "natural addition and multiplication on ordinals, also known as the Hessenberg sum and product" and states that "they're commutative, associative, preserve order, have the usual `0` and `1` from ordinals, and distribute over one another".
Its `OrderedCommSemiring NatOrdinal` instance supplies the two distributivity fields `left_distrib` and `right_distrib`, the two absorption fields `zero_mul` and `mul_zero`, and `mul_comm`.

```python
Ordinals().zero()
Ordinals().one()

alpha + beta
alpha * beta
alpha.natural_sum(beta)
alpha.natural_product(beta)
```

### Public ordinal constructors

```python
Ordinals()

Ordinals()(n)
InitialOrdinal.on_object(Aleph.on_object(index))

omega0
```

`Ordinals()(n)` constructs the finite ordinal of a nonnegative Python `int` `n`.
Each other presentation has its own named constructor (D52).

The composite `InitialOrdinal.on_object(Aleph.on_object(index))` constructs \(\omega_{\text{index}}\).

Examples:

```python
Ordinals()(0)
Ordinals()(5)

InitialOrdinal.on_object(Aleph.on_object(Ordinals().zero()))       # omega0
InitialOrdinal.on_object(Aleph.on_object(Ordinals().one()))
InitialOrdinal.on_object(Aleph.on_object(InitialOrdinal.on_object(Aleph.on_object(Ordinals().one()))))
```

Negative finite ordinals raise `ValueError`.

### Ordinal expression forms

The private expression model supports:

- Finite ordinals.

- Initial ordinals.

- Ordinary ordinal sums.

- Ordinary ordinal products.

- Ordinary ordinal powers.

- Hessenberg natural sums.

- Hessenberg natural products.

### `Ordinals()` API

`Ordinals().zero()` and `Ordinals().one()` are the finite ordinal constructors for `0` and `1`.
Finite ordinary sums and products fold `+` and `*` from those units.
Finite Hessenberg sums and products fold `natural_sum()` and `natural_product()`.

`Ordinals()` is one cached category.
Construction is cached by expression.
Reconstructing an equal expression returns the same ordinal object.

### Ordinary ordinal arithmetic

Python `+` and `*` are ordinary ordinal sum and ordinary ordinal product.
Each operation is a morphism out of a product,

\[
\alpha,\mu:\operatorname{Ordinals}()\times\operatorname{Ordinals}()
\longrightarrow\operatorname{Ordinals}(),
\]

so applying one to a pair returns an ordinal.
It presents no diagram and carries no cone.

Ordinary ordinal arithmetic uses standard notation:

```python
alpha + beta
alpha * beta
alpha.ordinal_power(beta)
```

These operations evaluate finite inputs exactly.
They also simplify:

```python
alpha + 0 == alpha
0 + alpha == alpha

alpha * 0 == 0
alpha * 1 == alpha

alpha.ordinal_power(0) == 1
0.ordinal_power(beta) == 0       # positive beta
1.ordinal_power(beta) == 1
```

Other cases remain symbolic.

### Hessenberg natural arithmetic

The commutative operations have explicit names:

```python
alpha.natural_sum(beta)
alpha.natural_product(beta)
```

Natural sum:

- Flattens nested natural sums.

- Combines all finite terms.

- Removes additive zero.

- Produces a commutative symbolic expression.

Natural product:

- Distributes across represented natural sums.

- Flattens nested natural products.

- Multiplies finite factors.

- Removes multiplicative identity.

- Returns zero if one factor is zero.

- Sorts symbolic factors.

### Ordinal object API

`OrdinalOrder().EssentialImage(InitialOrdinal)` is the property subcategory of initial ordinals.
Its retained equivalence has source `CardinalOrder()`.
It owns the initiality containment predicate and the retained equivalence from `Cardinal()`.
`cat_kernel` derives the standard `alpha.is_initial()` application (D175).
Apply the inverse of that equivalence to obtain the cardinal index of an initial ordinal.

Every ordinal supplies:

```python
alpha.cardinality()
alpha.cofinality()
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

Thus ordinal comparison operators state order propositions.
They do not replace an unresolved proposition with Boolean `False`.

### Ordinal representations

Representative output is:

```text
5
ω_0
ω_1
ω_0 # ω_1
ω_0 ⊗ ω_1
(ω_0 + ω_1)
(ω_0 · ω_1)
(ω_0 ^o ω_1)
```

Here:

- `#` denotes natural sum.

- `⊗` denotes natural product.

- `+`, `·`, and `^o` denote ordinary ordinal operations.

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

Ordinary ordinal powers do not map to cardinal exponentiation in general.
For example,

\[
2^\omega=\omega,
\qquad
|2^\omega|=\aleph_0,
\qquad
|2|^{|\omega|}=2^{\aleph_0}.
\]

This follows from the limit-power rule in Enderton, [Elements of Set Theory, Chapter 8, Theorem 8L](https://docs.ufpr.br/~hoefel/ensino/CM304_CompleMat_PE3/livros/Enderton_Elements%20of%20set%20theory_%281977%29.pdf).

`alpha.ordinal_power(beta).cardinality()` is an applied query with result category `Cardinal()`.
`ask()` uses exact ordinal normalization rules and returns an owned cardinal when determined, otherwise `Unknown`.
The [typed-query contract](undecidable-properties.md#typed-queries) owns evaluation.

## Cofinality

`alpha.cofinality()` is an applied query with result category `Cardinal()`.
`ask(alpha.cofinality())` evaluates \(\operatorname{cf}(\alpha)\), the cofinality of the ordinal.
This result is a **cardinal**. Mathlib's [`Ordinal.cof`](https://leanprover-community.github.io/mathlib4_docs/Mathlib/SetTheory/Cardinal/Cofinality/Ordinal.html#Ordinal.cof) supplies the reference definition.

The exact rules are:

\[
\operatorname{cf}(0)=0,
\qquad
\operatorname{cf}(\alpha+1)=1,
\qquad
\operatorname{cf}(\omega_0)=\aleph_0,
\]

\[
\operatorname{cf}(\omega_{n})=\aleph_{n}\ (n\geq 1),
\qquad
\operatorname{cf}(\omega_\beta)=\operatorname{cf}(\beta)\ (\beta\text{ a limit ordinal}).
\]

The first two are `Ordinal.cof_zero` and `Ordinal.cof_add_one`; they cover zero and ordinary successor sums. The third is `Ordinal.cof_omega0`. The fourth holds because \(\aleph_n\) is regular for \(n\geq 1\) (`Cardinal.isRegular_aleph_add_one` with `Cardinal.isRegular_iff`). The fifth is `Ordinal.cof_omega`, whose limit hypothesis an initial ordinal satisfies by `Cardinal.isSuccLimit_ord`.

For any other expression, `ask(alpha.cofinality())` returns `Unknown`: the shape that selects a rule is not established.
Cofinality is what [the continuum hypothesis](cardinality.md#the-continuum-hypothesis) needs in order to decide a cardinal power.
