# Cardinalities and ordinals

Cardinals are objects of a set-enriched skeletal category of cardinal representatives.
Ordinals are elements of a commutative semiring. Both models retain symbolic
expressions when their exact normalization is not available.

Cardinal and ordinal operations specified as predicates follow the proposition interface
in [Property refinement](property-refinement.md). Applying one returns a proposition.
Only `ask()` decides it as `True`, `False`, or `Unknown`.

The governing policies are `POL-MATH-034`, `POL-MATH-035`, `POL-CAT-001`,
`POL-CAT-021`, `POL-CAT-028`, `POL-CAT-086`, `POL-CAT-088`, `POL-SET-009`, `POL-SET-010`,
`POL-SET-025`, `POL-SET-026`, `POL-SET-033` through `POL-SET-035`,
`POL-API-002`, and `POL-API-016`.

## Implementation ownership

[Category ownership](../CONTRIBUTING.md#category-ownership-and-inheritance), [leaf-category encapsulation](../CONTRIBUTING.md#leaf-category-encapsulation), and [functor policies](../CONTRIBUTING.md#functors-and-universal-constructions) govern the general inheritance rules.

`Cardinal()` owns cardinal objects, maps between cardinal representatives, order
predicates, universal arithmetic, and expression normalization.
`Ordinals()` owns ordinal order and arithmetic.
`Sets()` owns set cardinality.

## Cardinal model

`Cardinal()` is a skeletal presentation of `Sets()` at cardinal numbers. Its
construction selects one representative set \(R_\kappa\) for each cardinal \(\kappa\).
Mathlib's
[cardinal definitions](https://leanprover-community.github.io/mathlib4_docs/Mathlib/SetTheory/Cardinal/Defs.html)
define cardinals as types modulo bijection and define addition, multiplication, and
exponentiation through sum, product, and function types. This category retains the same
constructions and their universal arrows.

A cardinal is an object of this category:

```python
CardinalObject = Cardinal().ObjectType
CardinalityHomCategory = Cardinal().HomCatType
CardinalityMorphism = Cardinal().ArrowType
```

Its complete structural tuple selects the skeletal inclusion:

```python
def structure_functors(self) -> tuple[Cat().ArrowType, ...]:
    return (Fun(self, Sets()).FullyFaithful().inclusion(),)
```

The inclusion sends each cardinal to its selected representative and acts identically
on the corresponding function sets.

For every pair of represented cardinals, the Hom category is the owned function set
between their representatives:

\[
\operatorname{Hom}_{\mathbf{Cardinal}}(\kappa,\lambda)
=
\operatorname{Hom}_{\mathbf{Set}}
  (R_\kappa,R_\lambda).
\]

Its objects are functions. Cardinal order is the existence of an injective function:

\[
\kappa\leq\lambda
\quad\Longleftrightarrow\quad
\operatorname{Ar}(\mathbf{Cardinal}).\operatorname{Monomorphisms()}
  (\kappa,\lambda)\text{ is inhabited}.
\]

Cardinal equality is represented by isomorphism of the selected representatives. Mere
inhabitation of the unrestricted Hom category does not define cardinal order.

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

C.supremum(cardinals)

C.Coproducts()(diagram)
C.Products()(diagram)
```

`supremum()` accepts a nonempty finite indexed family.

The indexed coproduct and product constructors accept an owned diagram. A finite
diagram can normalize by iteration. An infinite diagram produces a formal indexed
expression when no stronger normalization is available.

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

These are the inherited categorical constructions:

\[
\kappa+\lambda=\kappa\sqcup\lambda,
\qquad
\kappa\lambda=\kappa\times\lambda,
\qquad
\lambda^\kappa=
\operatorname{Hom}_{\mathbf{Cardinal}}(\kappa,\lambda).
\]

The coproduct and product retain their injections, projections, and universal maps. The
Hom category retains the representative functions. Their cardinal objects are exactly
cardinal addition, multiplication, and exponentiation.

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

Objects of `H` are functions from the selected representative of `kappa` to the
selected representative of `lambda`. Exact `True` for `ask(H.is_empty())` establishes
that no such function exists. `Unknown` preserves `H` without either conclusion.

The order proposition uses the monomorphism endpoint category:

```python
M = Ar(Cardinal()).Monomorphisms()(kappa, lambda)
kappa <= lambda  # dispatches to M.is_inhabited()
```

The base-category identity is an object of the endomorphism category:

```python
kappa.identity() in kappa.Hom(kappa)
```

Inherited base-category composition is ordinary function composition. Coproduct,
product, and Hom functoriality act on these arrows through their universal
constructions. These constructions supply the complete action on arrows.


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

Its arrow map accepts a set isomorphism. The construction retains a selected bijection
between each set and its cardinal representative. It conjugates the set isomorphism by
these selected bijections to construct the corresponding cardinal isomorphism.

Public access is category-owned:

```python
Sets().CardinalityFunctor()
```

For a category \(\mathbf C\) with selected set-valued structural functor
\(U_{\mathbf C}:\mathbf C\to\mathbf{Sets}\), the composite

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
