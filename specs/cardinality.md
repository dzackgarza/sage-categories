The preamble implements cardinals as objects of a thin category.
It implements ordinals as elements of a commutative semiring.

The design is symbolic and supports several nontrivial normalization rules.
It is not yet a complete cardinal or ordinal calculus.

This specification describes the current working tree.
The two core files are committed and clean.
Their set-integration files contain current uncommitted changes.

## Source boundary

I read these files completely:

- [cardinals.py](/home/dzack/research/src/dzack_research/preamble/categories/sets/cardinals.py:1), 821 lines.

- [ordinals.py](/home/dzack/research/src/dzack_research/preamble/categories/sets/ordinals.py:1), 391 lines.

- [cardinality.sage](/home/dzack/research/src/dzack_research/preamble/categories/functors/cardinality.sage:1), 56 lines.

I also traced relevant definitions in:

- [owned_sets.py](/home/dzack/research/src/dzack_research/preamble/categories/sets/owned_sets.py:221)

- [sets.sage](/home/dzack/research/src/dzack_research/preamble/categories/sets/sets.sage:231)

- [install.sage](/home/dzack/research/src/dzack_research/preamble/install.sage:99)

## Implementation ownership

[Category ownership](../CONTRIBUTING.md#category-ownership-and-inheritance), [leaf-category encapsulation](../CONTRIBUTING.md#leaf-category-encapsulation), and [functor policies](../CONTRIBUTING.md#functors-and-universal-constructions) govern the general inheritance rules.

`Cardinalities()` owns cardinal objects, comparison arrows, arithmetic, and expression normalization.
`Ordinals()` owns ordinal order and arithmetic.
`Sets()` owns set cardinality.

## Cardinal model

`Cardinalities()` is the thin category associated with the represented cardinal order.

A cardinal is an object of this category:

```python
Cardinal = Cardinalities().ObjectType
CardinalityHomCategory = Cardinalities().HomCatType
CardinalityMorphism = Cardinalities().ArrowType
```

The intended categorical rule is:

\[
\operatorname{Hom}(\kappa,\lambda)=
\begin{cases}
\{\kappa\leq\lambda\},&\text{when the implementation proves }\kappa\leq\lambda,\\
\varnothing,&\text{otherwise.}
\end{cases}
\]

This is currently the order proved by the expression evaluator.
It is not the complete mathematical cardinal order.

### Public cardinal constructors

```python
Cardinalities()
cardinal(value)
aleph(index)

aleph0
continuum
```

Accepted `cardinal(value)` inputs are:

- An existing `Cardinal`.

- A nonnegative Python `int`.

- A nonnegative Sage `Integer`.

- Sage `Infinity`, interpreted as `aleph0`.

Examples:

```python
cardinal(0)
cardinal(5)
cardinal(Infinity)  # aleph0

aleph(0)
aleph(1)
aleph(omega(1))

aleph0
continuum           # cardinal(2) ** aleph0
```

Negative integers are rejected.
Other scalar rings are rejected.

Construction is cached by expression.
Reconstructing an equal expression returns the same cardinal object.

### Cardinal expression forms

The private expression model supports:

- Finite cardinals.

- Aleph cardinals.

- Cardinal powers.

- Finite suprema.

- Set-indexed sums.

- Set-indexed products.

Conceptually:

```python
n
aleph(alpha)
kappa ** lambda
sup(kappa_1, ..., kappa_n)
sum(i in I, kappa_i)
product(i in I, kappa_i)
```

Finite suprema preserve unresolved relationships.
For example, `aleph(2) + continuum` can remain a formal supremum.

This avoids assuming the continuum hypothesis.

### `Cardinalities()` API

The category supplies:

```python
C = Cardinalities()

C.zero()
C.one()

C.sum(*summands)
C.product(*factors)
C.power(base, exponent)
C.supremum(*cardinals)

C.indexed_sum(index_set, family)
C.indexed_product(index_set, family)

C.le(kappa, lambda)
C.lt(kappa, lambda)
C.ge(kappa, lambda)
C.gt(kappa, lambda)
C.compare(kappa, lambda)
C.are_incomparable(kappa, lambda)

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

### Cardinal object API

Every cardinal supplies:

```python
kappa.cardinality()
kappa.expression()
kappa.sort_key()

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
kappa.finite_value()
```

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

For finite cardinals, these conversions exist:

```python
int(kappa)
operator.index(kappa)
ZZ(kappa)
QQ(kappa)
```

Infinite cardinals reject these conversions.

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

### Cardinal comparisons

`CardinalComparison` has these values:

```python
LESS
EQUAL
GREATER
LESS_OR_EQUAL
GREATER_OR_EQUAL
INCOMPARABLE
```

The evaluator knows:

- Exact finite comparisons.

- Every finite cardinal is below every represented infinite cardinal.

- Aleph order through ordinal indices.

- `aleph0` is below every represented infinite cardinal.

- `aleph1` is below every represented uncountable cardinal.

- Several monotonicity rules for cardinal powers.

- Componentwise rules for finite formal suprema.

Unknown comparisons currently return `False` from `le()` and `lt()`.

Therefore, `INCOMPARABLE` currently means “neither direction was proved.”
It does not prove mathematical incomparability.

### Cardinal morphisms

For a proved relation \(\kappa\leq\lambda\):

```python
H = Cardinalities().Hom(kappa, lambda)

H.objects()
H.unique_morphism()
H()
```

`H.objects()` is a singleton set containing the unique order arrow.

For an unproved relation, it is empty.

Endomorphism categories support:

```python
Cardinalities().Hom(kappa, kappa).identity()
```

Composition returns the unique composite order arrow:

```python
Hom(kappa, mu).compose(lambda_to_mu, kappa_to_lambda)
```

Finite cardinal addition and multiplication act on comparison morphisms:

```python
Cardinalities().sum_morphism(*arrows)
Cardinalities().product_morphism(*arrows)
```

Exponentiation acts on morphisms when the source base is proved nonzero:

```python
Cardinalities().power_morphism(base_arrow, exponent_arrow)
```

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

It supports structural hashing and comparisons:

```python
alpha == beta
alpha != beta
alpha < beta
alpha <= beta
alpha > beta
alpha >= beta
```

### Ordinal order support

`proves_le(alpha, beta)` recognizes:

- Structural equality.

- Exact order between finite ordinals.

- Every finite ordinal below a represented nonfinite ordinal.

- Order between initial ordinals through recursive index comparison.

Other represented comparisons return `False`.

Thus ordinal comparison operators also express proved order, not complete mathematical order.

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

## Integration with `Sets()`

The cardinality functor is:

\[
\#:\operatorname{core}(\mathbf{Sets})\longrightarrow\mathbf{Cardinalities}.
\]

Its object map calls:

```python
X.cardinality()
```

Its arrow map accepts a set isomorphism.
It checks equal cardinalities and returns the unique identity comparison arrow.

Public access is:

```python
cardinality_functor()
Sets().CardinalityFunctor()
```

See [CardinalityFunctor](/home/dzack/research/src/dzack_research/preamble/categories/functors/cardinality.sage:22).

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

- Finite power sets have size \(2^{|X|}\) for finite \(X\), and \(|X|\) for infinite \(X\).

- Fixed finite-size subsets use binomial coefficients for finite sets.

- Fixed positive finite-size subsets of infinite sets have cardinality \(|X|\).

- Countably infinite sets return `aleph0`.

- Finitely supported function sets use powers for finite index sets.

- Infinite finitely supported function sets use the supremum of the index and value cardinalities.

The session also installs:

```python
Sets.ℵ[n]
Sets.א[n]
```

This indexed spelling currently accepts finite integer indices.
The `aleph(index)` function accepts arbitrary represented ordinal indices.

## Effective export surface

`install_preamble()` exports every non-underscore name from both modules.

The intended mathematical exports are:

```python
Cardinalities
Cardinal
CardinalityHomCategory
CardinalityMorphism
CardinalComparison
cardinal
aleph
aleph0
continuum

OrdinalSemirings
Ordinals
Ordinal
ordinal
omega
omega0

CardinalityFunctor
cardinality_functor
```

The installation mechanism also exports imported non-underscore helper names.
Neither module defines `__all__`.

## Current capability limits

- Indexed cardinal expressions preserve the index set and callable family.

- Their equality therefore depends on the stored callable and object identities.

- Finiteness and countability queries on indexed expressions raise `NotImplementedError`.

- Cardinal equality is normalized-expression equality.

- Ordinal equality is normalized-expression equality.

- Cardinal and ordinal order queries return `False` when the evaluator lacks a proof.

- The comparison API has no `Unknown` result.

- Ordinal arithmetic does not compute general Cantor normal forms.

- It has no local implementation of arbitrary ordinal suprema, cofinality, or successor and limit classification.

- `.expression()` exposes the private expression representation publicly.

- Cardinal inputs and conversions expose Sage `Integer`, `Infinity`, `ZZ`, and `QQ`.

- `Cardinalities()` directly declares Sage `Objects()` as its supercategory.

- `OrdinalSemirings` directly declares Sage’s commutative-semiring category.

For the last local-surface claim:

- Searched: all 821 lines of `cardinals.py` and all 391 lines of `ordinals.py`.

- Found: no local methods for cofinality, Cantor normal form, arbitrary ordinal suprema, or successor and limit classification.

- Conclusion: those capabilities are absent from these two implementations.

- Confidence: High for locally defined methods.

- Gaps: inherited Sage or owned-category methods could add unrelated generic operations.

## Runtime status

The declared API is not executable through the current Sage launcher.

- Searched: `sage -c` with the complete preamble import, then a direct cardinal and ordinal import.

- Found: the complete import fails with `KeyError: 'Homsets'`. The direct import fails with `TypeError: duplicate base class Cardinalities.parent_class`.

- Conclusion: the specification above describes the current source API. It is not a verified working runtime API.

- Confidence: High for the current `/home/dzack/.local/bin/sage` launcher.

- Gaps: another running notebook kernel or older installed checkout may have different loaded state.
