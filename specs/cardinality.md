# Cardinalities and ordinals

Cardinals are objects of a thin category. Ordinals are elements of a commutative
semiring. Both models retain symbolic expressions when their exact normalization is not
available.

Cardinal and ordinal operations specified as predicates follow the proposition interface
in [Property refinement](property-refinement.md). Applying one returns a proposition.
Only `ask()` decides it as `True`, `False`, or `Unknown`.

The governing policies are `POL-MATH-034`, `POL-MATH-035`, `POL-CAT-001`,
`POL-CAT-021`, `POL-CAT-028`, `POL-CAT-086`, `POL-SET-009`, `POL-SET-010`,
`POL-SET-025`, `POL-SET-026`, `POL-SET-033` through `POL-SET-035`,
`POL-API-002`, and `POL-API-016`.

## Implementation ownership

[Category ownership](../CONTRIBUTING.md#category-ownership-and-inheritance), [leaf-category encapsulation](../CONTRIBUTING.md#leaf-category-encapsulation), and [functor policies](../CONTRIBUTING.md#functors-and-universal-constructions) govern the general inheritance rules.

`Cardinal()` owns cardinal objects, comparison arrows, arithmetic, and expression normalization.
`Ordinals()` owns ordinal order and arithmetic.
`Sets()` owns set cardinality.

## Cardinal model

`Cardinal()` is the thin category associated with the represented cardinal order.

A cardinal is an object of this category:

```python
CardinalObject = Cardinal().ObjectType
CardinalityHomCategory = Cardinal().HomCatType
CardinalityMorphism = Cardinal().ArrowType
```

For every pair of represented cardinals, the Hom category exists:

\[
\operatorname{Hom}(\kappa,\lambda)
\quad\text{is inhabited exactly when}\quad
\kappa\leq\lambda.
\]

Its `is_inhabited()` predicate is the order proposition `kappa <= lambda`. Its
`is_empty()` predicate is the negation. If neither proposition is decided, the Hom
category remains symbolic. An undecided proposition does not make it empty.

### Public cardinal constructors

```python
Cardinal()(value)
Cardinal().aleph(index)
aleph0
continuum
```

`Cardinal()(value)` is the category-owned constructor. It follows Sage's
[`Parent.__call__()` dispatch model](https://doc.sagemath.org/html/en/reference/structure/sage/structure/parent.html):
the public call selects an exact private constructor route from the semantic input.

Accepted inputs are:

- An existing `CardinalObject`.

- A nonnegative Python `int`.

Examples:

```python
Cardinal()(0)
Cardinal()(5)

Cardinal().aleph(0)
Cardinal().aleph(1)
Cardinal().aleph(Ordinals().omega(1))

aleph0
continuum           # Cardinal()(2) ** aleph0
```

`aleph0` is `Cardinal().aleph(0)`. `continuum` is
`Cardinal()(2) ** aleph0`.

Negative integers are rejected.
Use `aleph0` for countable infinity.

Construction is cached by expression.
Reconstructing an equal expression returns the same cardinal object.

### Cardinal expression forms

The private expression model supports:

- Finite cardinals.

- Aleph cardinals.

- Cardinal powers.

- Cardinalities of unresolved ordinary ordinal powers.

- Finite suprema.

- Set-indexed sums.

- Set-indexed products.

Conceptually:

```python
n
Cardinal().aleph(alpha)
kappa ** lambda
sup(kappa_1, ..., kappa_n)
sum(i in I, kappa_i)
product(i in I, kappa_i)
```

Finite suprema preserve unresolved relationships.
For example, `Cardinal().aleph(2) + continuum` can remain a formal supremum.

This avoids assuming the continuum hypothesis.

### `Cardinal()` API

The category supplies:

```python
C = Cardinal()

C.zero()
C.one()

C.sum(*summands)
C.product(*factors)
C.power(base, exponent)
C.supremum(*cardinals)

C.indexed_sum(index_set, family)
C.indexed_product(index_set, family)

C.sum_morphism(*morphisms)
C.product_morphism(*morphisms)
C.power_morphism(base_morphism, exponent_morphism)
```

`supremum()` requires at least one input.

`indexed_sum()` and `indexed_product()` accept:

```python
index_set: object of Sets()
family: callable from an index to a cardinal
```

A finite index set is evaluated by iteration.
An infinite index set produces a formal indexed expression.

### Cardinal arithmetic

Cardinal objects support ordinary Python notation:

```python
kappa + lambda
kappa * lambda
kappa ** lambda

n + kappa
n * kappa
n ** kappa
```

The implementation normalizes these cases:

- Finite sums, products, and powers evaluate exactly.

- \(0^\kappa=0\) for positive \(\kappa\).

- \(\kappa^0=1\).

- \(1^\kappa=1\).

- An infinite cardinal plus a finite cardinal remains unchanged.

- A positive finite cardinal times an infinite cardinal gives that infinite cardinal.

- Finite sums and products of infinite cardinals become finite suprema.

- An infinite cardinal raised to a positive finite power remains unchanged.

- Nested powers use \((\kappa^\lambda)^\mu=\kappa^{\lambda\mu}\).

- Powers over finite formal suprema distribute into formal suprema.

- A suitable base below an infinite exponent normalizes to base \(2\).

The last rule uses:

\[
2\leq\kappa\leq\lambda
\quad\Longrightarrow\quad
\kappa^\lambda=2^\lambda.
\]

### Finite cardinal modulus

Modulus belongs to the finite-cardinal property category. For finite `kappa` and
positive natural cardinal `n`, Python `%` returns the finite cardinal remainder:

```python
kappa % n
```

It satisfies the natural-number division theorem:

\[
\kappa=q n+r,
\qquad
0\leq r<n.
\]

This is the cardinal form of the division algorithm in Barrus and Clark,
[Elementary Number Theory, Section 1.5, Theorem 1](https://math.libretexts.org/Bookshelves/Combinatorics_and_Discrete_Mathematics/Elementary_Number_Theory_%28Barrus_and_Clark%29/01%3A_Chapters/1.05%3A_The_Division_Algorithm).

The result is the cardinal `r`. Thus a finite-cardinal predicate can state
`kappa % 2 == 0` without extracting or coercing a stored integer.

### Cardinal object API

Every cardinal supplies:

```python
kappa.cardinality()

kappa.is_finite()
kappa.is_infinite()
kappa.is_aleph()
kappa.is_continuum()
kappa.is_countable()
kappa.is_uncountable()
kappa.is_countably_infinite()
kappa.is_uncountably_infinite()

kappa.aleph_index()
kappa.initial_ordinal()
```

Every `is_*()` call in this surface returns an applied proposition. Equality and order
operations also return propositions. Use `ask()` when a decision is required.

It also supports:

```python
kappa == lambda
kappa != lambda
kappa < lambda
kappa <= lambda
kappa > lambda
kappa >= lambda
```

A cardinal has itself as its cardinality:

```python
kappa.cardinality() is kappa
```

### Cardinal representations

Representative output is:

```text
3
ℵ_0
ℵ_1
(2)^(ℵ_0)
sup(ℵ_2, (2)^(ℵ_0))
sum_{i in I} kappa_i
prod_{i in I} kappa_i
```

### Cardinal comparison predicates

Equality and order use standard Python notation. Each expression returns an applied
predicate. The exact handlers know:

- Exact finite comparisons.

- Every finite cardinal is below every represented infinite cardinal.

- Aleph order through ordinal indices.

- `aleph0` is below every represented infinite cardinal.

- `aleph1` is below every represented uncountable cardinal.

- Several monotonicity rules for cardinal powers.

- Componentwise rules for finite formal suprema.

If no handler decides a comparison, `ask()` returns `Unknown`. Mathematical
incomparability requires its own exact proposition. Failure to decide either order does
not establish incomparability.

### Cardinal morphisms

For all cardinals `kappa` and `lambda`:

```python
H = Cardinal().HomCategory(kappa, lambda)

H.is_inhabited()
H.is_empty()
```

After `assert ask(H.is_inhabited()) is True`, the thin Hom category supplies its unique
order arrow. Exact `True` for `ask(H.is_empty())` establishes emptiness. `Unknown`
preserves `H` without either conclusion.

The base-category identity is an object of the endomorphism category:

```python
kappa.identity() in kappa.Hom(kappa)
```

Inherited base-category composition returns the unique composite order arrow. It does
not use composition inside one Hom category as a substitute.

Finite cardinal addition and multiplication act on comparison morphisms:

```python
Cardinal().sum_morphism(*arrows)
Cardinal().product_morphism(*arrows)
```

Exponentiation acts on morphisms when the source base is established as nonzero:

```python
Cardinal().power_morphism(base_arrow, exponent_arrow)
```


The ordinal model is specified in [`ordinals.md`](ordinals.md).

## Integration with `Sets()`

The cardinality functor is:

\[
\#:\operatorname{core}(\mathbf{Sets})\longrightarrow\mathbf{Cardinal}.
\]

Its object map calls:

```python
X.cardinality()
```

Its arrow map accepts a set isomorphism.
The isomorphism theorem establishes equal cardinalities. The functor returns the unique
comparison isomorphism without running a separate equality check.

Public access is category-owned:

```python
Sets().CardinalityFunctor()
```

For a category \(\mathbf C\) with selected forgetful functor \(U_{\mathbf C}:\mathbf C\to\mathbf{Sets}\), the composite

\[
\#\circ\operatorname{core}(U_{\mathbf C})
\]

supplies cardinality.
A constructor can pass known cardinality data to its underlying-set constructor.

Set constructions use cardinal expressions directly:

- Products use indexed products.

- Coproducts use indexed sums.

- Function sets use \(|Y|^{|X|}\).

- Power sets use \(2^{|X|}\).

- Fixed finite-size subsets use binomial coefficients for finite sets.

- Fixed positive finite-size subsets of infinite sets have cardinality \(|X|\).

- Countably infinite sets return `aleph0`.

- Finitely supported function sets use powers for finite index sets.

- Infinite finitely supported function sets use the supremum of the index and value cardinalities.

## Public export surface

The mathematical exports are:

```python
Cardinal
CardinalObject
CardinalityHomCategory
CardinalityMorphism
aleph0
continuum

OrdinalSemirings
Ordinals
Ordinal
omega0

CardinalityFunctor
```
