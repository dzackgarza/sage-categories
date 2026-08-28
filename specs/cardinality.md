# Cardinalities and ordinals

Cardinals are objects of a set-enriched skeletal category of cardinal representatives.
The point functor of `Cardinal()` into `Semirings(Cat())` presents cardinal addition and multiplication as its two semiring operations.
Ordinals are objects of the skeletal category `Ordinals()`. Its point functor into `Semirings(Cat())` presents the Hessenberg operations as ordinal addition and multiplication.
Both models retain exact expressions when no normalization rule applies.

Cardinal and ordinal operations specified as predicates follow the proposition interface in [Property refinement](property-refinement.md).
Applying one returns a proposition.
Only `ask()` decides it as `True`, `False`, or `Unknown`.

The governing policies are `POL-MATH-034`, `POL-MATH-035`, `POL-CAT-001`, `POL-GEN-017`, `POL-GEN-020`, `POL-GEN-021`, `POL-CAT-021`, `POL-CAT-028`, `POL-CAT-071`, `POL-CAT-083`, `POL-CAT-085`, `POL-CAT-086`, `POL-CAT-088`, `POL-FUN-002`, `POL-FUN-003`, `POL-FUN-035`, `POL-SET-009`, `POL-SET-010`, `POL-SET-025`, `POL-SET-026`, `POL-SET-033` through `POL-SET-035`, `POL-API-002`, `POL-API-016`, and `POL-DOC-010` through `POL-DOC-013`.

## Implementation ownership

[Category ownership](../CONTRIBUTING.md#category-ownership-and-inheritance), [leaf-category encapsulation](../CONTRIBUTING.md#leaf-category-encapsulation), and [functor policies](../CONTRIBUTING.md#functors-and-universal-constructions) govern the general inheritance rules.

`Cardinal()` owns cardinal objects, maps between cardinal representatives, order predicates, universal arithmetic, and expression normalization.
`Ordinals()` owns ordinal order and arithmetic.
`Sets()` owns set cardinality.

## Cardinal model

`Cardinal()` is a skeletal presentation of `Sets()` at cardinal numbers.
Its construction selects one representative set \(R_\kappa\) for each cardinal \(\kappa\). Mathlib's [cardinal definitions](https://leanprover-community.github.io/mathlib4_docs/Mathlib/SetTheory/Cardinal/Defs.html) define cardinals "as a quotient of types under the equivalence relation of equinumerosity (i.e., existence of a bijection)". Its section "Main definitions" fixes the arithmetic by three equations:

\[
\#\alpha+\#\beta=\#(\alpha\oplus\beta),
\qquad
\#\alpha\cdot\#\beta=\#(\alpha\times\beta),
\qquad
\#\alpha^{\#\beta}=\#(\beta\to\alpha).
\]

Each operation acts on cardinals.
The sum, product, and function type on the right are constructions on types.
`Sets()` constructions register the corresponding exact cardinality-predicate cases; see [Cardinal arithmetic](#cardinal-arithmetic).

A cardinal is an object of this category:

```python
CardinalObject = Cardinal().ObjectType
CardinalElement = Cardinal().ElementType
CardinalityMorphism = Cardinal().MorphismType
```

Its complete structural tuple selects the representative functor:

```python
def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
    return (Fun(self, Sets()).FullyFaithful()(self.representative, lambda morphism: morphism.set_map()),)
```

It sends each cardinal to its selected representative, and a cardinal morphism to its retained set map.
Thus a generalized element `t: T -> kappa` maps to the generalized set element `R(t): R_T -> R_kappa` through the same morphism action.

`Cardinal()` is a skeleton, so this functor is fully faithful and injective on objects, hence monic; it is not an isofibration, because a set isomorphic to a representative need not be one.
Placement therefore does not follow it, and a cardinal is not a set (`specs/functor.md`, "Monomorphisms of `Cat()` and placement"). It is the representative transport from cardinal objects to sets.
The point category of `Cardinal()` owns its separate placement as a semiring object in `Cat()`:

```python
# Cat().Point(Cardinal())
def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
    return (Fun(self, Semirings(Cat())).Monomorphisms().Isofibrations()(),)
```

`Semirings(Cat())` is the general internal semiring category at ambient `Cat()`. Its objects, its two operation morphisms, its unit points, and its laws are defined in [Semirings](magmas-monoids-semirings.md#semirings).
`Cardinal()` adds only which functors those are: the additive operation functor is cardinal addition, with unit object `0`, and the multiplicative operation functor is cardinal multiplication, with unit object `1`. The selected point functor supplies their complete compiled classes, exact constructor conversions, retained state, and public methods.
The law data is the equations between these functors ([functor.md](functor.md#ambient-algebraic-categories)). `Cardinal()` is skeletal, so each operation selects one representative and the laws hold as equalities ([Laws in the supplied ambient](magmas-monoids-semirings.md#laws-in-the-supplied-ambient)).

For every pair of represented cardinals, `Mor(Cardinal())(kappa, lambda)` is the discrete category on the owned function set between their representatives:

\[
\operatorname{Mor}_{\mathbf{Cardinal}}(\kappa,\lambda)
=
\operatorname{Mor}_{\mathbf{Set}}
  (R_\kappa,R_\lambda).
\]

Its objects are functions.
Cardinal order is the existence of an injective function:

\[
\kappa\leq\lambda
\quad\Longleftrightarrow\quad
\operatorname{Mor}(\mathbf{Cardinal}).\operatorname{Monomorphisms()}
  (\kappa,\lambda)\text{ is inhabited}.
\]

Cardinal equality is represented by isomorphism of the selected representatives.
Mere inhabitation of the unrestricted morphism category does not define cardinal order.

### Public cardinal constructors

```python
Cardinal()(value)
Cardinal().aleph(index)
aleph0
continuum
```

`Cardinal()(value)` is the category-owned constructor.
It follows Sage's [`Parent.__call__()` dispatch model](https://doc.sagemath.org/html/en/reference/structure/sage/structure/parent.html): the public call selects an exact private constructor route from the semantic input.

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

`aleph0` is `Cardinal().aleph(0)`. `continuum` is `Cardinal()(2) ** aleph0`.

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

These are the forms of the ZFC-only state, which [The continuum hypothesis](#the-continuum-hypothesis) describes.
With the hypothesis assumed, exponentiation evaluates and these forms are reached only by an expression the hypothesis leaves open.

### `Cardinal()` API

The category supplies:

```python
C = Cardinal()

C.zero()
C.one()

C.supremum(cardinals)
```

`supremum()` accepts a nonempty finite indexed family.

`Cardinal()` inherits the indexed product and coproduct constructions specified in [Diagram shapes and universal constructions](functor.md#diagram-shapes-and-universal-constructions).
Its delta makes their apexes the indexed cardinal product and indexed cardinal sum.
Mathlib defines these as the cardinalities of the corresponding pi type and sigma type.
A finite diagram can normalize by iteration.
An infinite diagram produces a formal indexed expression when no stronger normalization is available.

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

Addition and multiplication are the semiring operations that the point functor exposes ([Semirings](magmas-monoids-semirings.md#semirings)). Each is a morphism out of a product,

\[
\alpha,\mu:\operatorname{Cardinal}()\times\operatorname{Cardinal}()
\longrightarrow\operatorname{Cardinal}(),
\]

so applying one to a pair returns a cardinal.
It presents no diagram, retains no injection or projection, and carries no cone.
The indexed constructions `Cardinal().Coproducts()` and `Cardinal().Products()` are separate operations with their own presentations; see [`Cardinal()` API](#cardinal-api).

The `Sets()` implementations of these constructions register the corresponding exact cardinality-predicate cases.
For `X, Y in core(Sets())`,

\[
\#(X\sqcup Y)=\#X+\#Y,
\qquad
\#(X\times Y)=\#X\cdot\#Y,
\qquad
\#\!\left(Y^{X}\right)=(\#Y)^{\#X},
\]

and the exponential of cardinals is the cardinal of the function set between the chosen representatives, \(\lambda^{\kappa}=\#\!\left(R_\lambda^{\,R_\kappa}\right)\). The coproduct, product and function set on the left are constructions in `Sets()` and retain their injections, projections and universal maps there.
The operations on the right are the semiring operations, and the equalities are the statement that `#` carries one to the other.

`Cardinal()` is skeletal, so these operations collapse: `c_2 * c_3` is `c_6`, and so is `c_6 * c_1`. An expression that no normalization rule below evaluates is retained exactly.

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

### The continuum hypothesis

The generalized continuum hypothesis is an assumable proposition, not an axiom of the arithmetic:

```python
generalized_continuum_hypothesis()
```

It is a proposition in the sense of [Property refinement](property-refinement.md) and `POL-ASSUME-004`. The active Sage or SymPy assumption state records it and `ask()` reads it.
`assume()` records it and `retract()` withdraws it.
`Cardinal()` records it when the package loads, so the package's own default state assumes it.

It states that \(2^{\aleph_\alpha}=\aleph_{\alpha+1}\) for every ordinal \(\alpha\), and it thereby decides every infinite power.
For ordinals \(\alpha\) and \(\beta\):

\[
\aleph_\alpha^{\aleph_\beta}=
\begin{cases}
\aleph_{\beta+1} & \alpha\leq\beta+1,\\
\aleph_\alpha & \beta+1<\alpha \text{ and } \aleph_\beta<\operatorname{cf}(\aleph_\alpha),\\
\aleph_{\alpha+1} & \beta+1<\alpha \text{ and } \aleph_\beta\geq\operatorname{cf}(\aleph_\alpha).
\end{cases}
\]

A finite base \(n\geq 2\) has the power of two, so \(n^{\aleph_\beta}=2^{\aleph_\beta}=\aleph_{\beta+1}\). The cofinality is `alpha.initial_ordinal().cofinality()`; see [Cofinality](ordinals.md#cofinality).
When the ordinal expression does not establish the cofinality, the power stays formal.

Addition and multiplication are unchanged.
They are already the maximum and do not depend on the hypothesis.

Assumed, the normal form of an infinite cardinal is `aleph(alpha)`, so the formal powers and formal suprema are reached only where the expression escapes these rules.
Retracted, they return: `Cardinal()(2) ** aleph0` is a formal power, neither order between it and `Cardinal().aleph(2)` is decided, and their sum is a formal supremum.
Both states are exact.
The hypothesis is a hypothesis in either.

The cardinals constructed under one state persist under the other.
Retracting the hypothesis does not rewrite a cardinal that was normalized while it held.

### Finite cardinal modulus

Modulus belongs to the finite-cardinal property category.
For finite `kappa` and positive natural cardinal `n`, Python `%` returns the finite cardinal remainder:

```python
kappa % n
```

It satisfies the natural-number division theorem:

\[
\kappa=q n+r,
\qquad
0\leq r<n.
\]

This is the cardinal form of the division algorithm in Barrus and Clark, [Elementary Number Theory, Section 1.5, Theorem 1](https://math.libretexts.org/Bookshelves/Combinatorics_and_Discrete_Mathematics/Elementary_Number_Theory_%28Barrus_and_Clark%29/01%3A_Chapters/1.05%3A_The_Division_Algorithm).

The result is the cardinal `r`. Thus a finite-cardinal predicate can state `kappa % 2 == 0` without extracting or coercing a stored integer.

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

Every `is_*()` call in this surface returns an applied proposition.
Equality and order operations also return propositions.
Use `ask()` when a decision is required.

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

Equality and order use standard Python notation.
Each expression returns an applied predicate.
The exact handlers know:

- Exact finite comparisons.

- Every finite cardinal is below every represented infinite cardinal.

- Aleph order through ordinal indices.

- `aleph0` is below every represented infinite cardinal.

- `aleph1` is below every represented uncountable cardinal.

- Several monotonicity rules for cardinal powers.

- Componentwise rules for finite formal suprema.

If no handler decides a comparison, `ask()` returns `Unknown`. Mathematical incomparability requires its own exact proposition.
Failure to decide either order does not establish incomparability.

### Cardinal morphisms

For all cardinals `kappa` and `lambda`:

```python
H = Mor(Cardinal())(kappa, lambda)

H.is_inhabited()
H.is_empty()
```

Objects of `H` are functions from the selected representative of `kappa` to the selected representative of `lambda`. Exact `True` for `ask(H.is_empty())` establishes that no such function exists.
`Unknown` preserves `H` without either conclusion.

The order proposition uses the monomorphism endpoint category:

```python
M = Mor(Cardinal()).Monomorphisms()(kappa, lambda)
kappa <= lambda  # dispatches to M.is_inhabited()
```

Cardinal morphisms compose by ordinary function composition.
The coproduct, product, and function set of `Sets()` act on the representative functions through their universal constructions there.
Addition, multiplication, and exponentiation act on cardinal morphisms through the universal constructions of `Cardinal()` itself.

The ordinal model is specified in [`ordinals.md`](ordinals.md).

## Integration with `Sets()`

`X.cardinality()` returns an applied predicate with result category `Cardinal()`.
`ask(X.cardinality())` returns an owned cardinal when an exact evaluation case applies and Sage `Unknown` otherwise.

The category-owned `Sets()` implementation declares the predicate.
Each set construction registers its exact cases from retained construction data.
An inherited call on a structured object uses the same predicate on that original object.
A selected functor to `Sets()` supplies the set constructor data used by these cases; it does not replace predicate evaluation with a separate image lookup.

The registered cases route on the index set, the retained diagram's codomain placement (`Sets().Finite()`, `Sets().Countable()`, `Sets().Uncountable()`), and any retained constant diagram.
For a finite chosen enumeration, they obtain each factor query by applying `X_i.cardinality()` to `P.product_factors()`.
Each case cites the theorem that decides it.
When no case applies, `ask()` returns `Unknown`. The cases are:

- Products over a finite index with every factor exact use the exact product; a finite index with an empty factor gives \(0\); the constant diagram at \(X\) over \(S\) gives \(|X|^{|S|}\); an infinite index with codomain `Sets().Uncountable()` places the product in `Sets().Uncountable()`; a finite index with codomain `Sets().Countable()` places the product in `Sets().Countable()`.

- Coproducts use the dual sum cases.

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
CardinalityMorphism
aleph0
continuum
generalized_continuum_hypothesis

Ordinals
OrdinalObject
omega0

```
