# Cardinalities and ordinals

Cardinals are objects of a set-enriched skeletal category of cardinal representatives.
`Cardinal()` is placed as an object of `Semirings(Cat())` by the structure functor `Semirings(Cat()).Point()` in its class (D128, D154).
Cardinal addition and multiplication are its two internal semiring operations.
Ordinals are objects of the skeletal category `Ordinals()`. Their Python addition and multiplication operators are ordinary ordinal arithmetic.
Both models retain exact expressions when no normalization rule applies.

`Cardinal()` and `Ordinals()` own their predicate meanings.
Their public representation and evaluation follow [Propositions and `ask()`](undecidable-properties.md).
Applying a predicate returns a SymPy proposition.
Only `ask()` decides it as `True`, `False`, or `Unknown`.

The governing policies are `POL-MATH-034`, `POL-MATH-035`, `POL-CAT-001`, `POL-GEN-017`, `POL-GEN-020`, `POL-GEN-021`, `POL-CAT-021`, `POL-CAT-028`, `POL-CAT-071`, `POL-CAT-083`, `POL-CAT-085`, `POL-CAT-086`, `POL-CAT-088`, `POL-FUN-002`, `POL-FUN-003`, `POL-FUN-035`, `POL-SET-009`, `POL-SET-010`, `POL-SET-025`, `POL-SET-026`, `POL-SET-033` through `POL-SET-038`, `POL-API-002`, `POL-API-016`, and `POL-DOC-010` through `POL-DOC-013`.

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

Addition, multiplication, and exponentiation act on cardinals.
The sum, product, and function type on the right are constructions on types.
`Sets()` constructions register the corresponding exact cardinality-query cases; see [Cardinal arithmetic](#cardinal-arithmetic).

A cardinal is an object of this category:

```python
CardinalObject = Cardinal().ObjectType
CardinalElement = Cardinal().ElementType
CardinalityMorphism = Cardinal().MorphismType
```

Its complete structure-functor tuple selects the representative functor:

```python
def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
    return (Fun(self, Sets()).FullyFaithful()(self.representative, lambda morphism: morphism.set_map()),)
```

It sends each cardinal to its selected representative, and a cardinal morphism to its retained set map.
Thus a generalized element `t: T -> kappa` maps to the generalized set element `R(t): R_T -> R_kappa` through the same morphism action.

`Cardinal()` is a skeleton, so this functor is fully faithful and injective on objects, hence monic; it is not an isofibration, because a set isomorphic to a representative need not be one.
Placement therefore does not follow it, and a cardinal is not a set (`specs/functor.md`, "Monomorphisms of `Cat()` and placement"). It is the representative transport from cardinal objects to sets.
`Semirings(Cat())` is the general internal semiring category at ambient `Cat()`. Its objects, its addition and multiplication functors, its zero and one points, and its laws are defined in [Semirings](magmas-monoids-semirings.md#semirings).
`Cardinal()` supplies cardinal addition with zero and cardinal multiplication with one.
Its selected point functor regards `Cardinal()` with these operations as an object of that category and, through the categorical level shift, supplies the compiled classes, retained state, and public methods of `Semirings(Cat())` ([functor.md](functor.md#the-categorical-level-shift)).
The law data is the equations between these functors ([functor.md](functor.md#ambient-algebraic-categories)). `Cardinal()` is skeletal, so each binary operation selects one representative and the laws hold as equalities ([Laws in the supplied ambient](magmas-monoids-semirings.md#laws-in-the-supplied-ambient)).

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

### Cardinal and ordinal order categories

`CardinalOrder()` and `OrdinalOrder()` are thin categories on the owned cardinal and ordinal objects.
Each has one morphism `a -> b` exactly when `a <= b`.
Their morphisms are order arrows, not functions between cardinal representatives.

The named order functors are:

```python
Aleph: OrdinalOrder() -> CardinalOrder()
InitialOrdinal: CardinalOrder() -> OrdinalOrder()
```

They act on the unique order arrows by monotonicity.
Their object actions return the same `CardinalObject` and `OrdinalObject` values used by `Cardinal()` and `Ordinals()`.

### Public cardinal constructors

```python
Cardinal()(n)
Aleph.on_object(index)
aleph0
continuum
```

`Cardinal()(n)` is the category-owned constructor of the finite cardinal of a nonnegative Python `int` `n`.
Each other presentation has its own named constructor (D52).

Examples:

```python
Cardinal()(0)
Cardinal()(5)

Aleph.on_object(Ordinals().zero())
Aleph.on_object(Ordinals().one())
Aleph.on_object(InitialOrdinal.on_object(Aleph.on_object(Ordinals().one())))

aleph0
continuum           # Cardinal()(2) ** aleph0
```

`Aleph: OrdinalOrder() -> CardinalOrder()` is the order functor from an ordinal index to its aleph cardinal.
`InitialOrdinal: CardinalOrder() -> OrdinalOrder()` is the order functor from a cardinal to its initial ordinal representative.
`aleph0` is `Aleph.on_object(Ordinals().zero())`.
`continuum` is `Cardinal()(2) ** aleph0`.

Negative integers are rejected.
Use `aleph0` for countable infinity.

Construction is cached by expression.
Reconstructing an equal expression returns the same cardinal object.

### Cardinal expression forms

The private engine behind `Cardinal()` is two Sage semirings, declared into Sage's poset and semiring categories.
They stay behind the computation-engine boundary of [leaves.md](leaves.md#computation-engine-boundary); the public category graph shares only the `Parent` root with Sage's (D01, D65, D153).
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
Aleph.on_object(alpha)
kappa ** lambda
sup(kappa_1, ..., kappa_n)
sum(i in I, kappa_i)
product(i in I, kappa_i)
```

Finite suprema preserve unresolved relationships.
For example, `Aleph.on_object(Ordinals()(2)) + continuum` can remain a formal supremum.

These are the forms of the ZFC-only state, which [The continuum hypothesis](#the-continuum-hypothesis) describes.
With the hypothesis assumed, exponentiation evaluates and these forms are reached only by an expression the hypothesis leaves open.

### `Cardinal()` API

The category supplies:

```python
C = Cardinal()

C.zero()
C.one()
```

Use the standard finite `sup(cardinals)` operation for a nonempty finite indexed family.

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

Addition and multiplication are the internal semiring operations ([Semirings](magmas-monoids-semirings.md#semirings)). Each is a morphism out of a product,

\[
\alpha,\mu:\operatorname{Cardinal}()\times\operatorname{Cardinal}()
\longrightarrow\operatorname{Cardinal}(),
\]

so applying one to a pair returns a cardinal.
It presents no diagram, retains no injection or projection, and carries no cone.
The indexed constructions `Cardinal().Coproducts()` and `Cardinal().Products()` are separate operations with their own presentations; see [`Cardinal()` API](#cardinal-api).

The `Sets()` implementations of these constructions register the corresponding exact cardinality-query cases.
For `X, Y in Core(Sets())`,

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

It is a zero-argument SymPy proposition under [Propositions and `ask()`](undecidable-properties.md). SymPy `global_assumptions` records it and `ask()` reads it.
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

A finite base \(n\geq 2\) has the power of two, so \(n^{\aleph_\beta}=2^{\aleph_\beta}=\aleph_{\beta+1}\). The cofinality is `InitialOrdinal.on_object(Aleph.on_object(alpha)).cofinality()`; see [Cofinality](ordinals.md#cofinality).
When the ordinal expression does not establish the cofinality, the power stays formal.

Addition and multiplication are unchanged.
They are already the maximum and do not depend on the hypothesis.

Assumed, the normal form of an infinite cardinal is `Aleph.on_object(alpha)`, so the formal powers and formal suprema are reached only where the expression escapes these rules.
Retracted, they return: `Cardinal()(2) ** aleph0` is a formal power, neither order between it and `Aleph.on_object(Ordinals()(2))` is decided, and their sum is a formal supremum.
Both states are exact.
The hypothesis is a hypothesis in either.

The cardinals constructed under one state persist under the other.
Retracting the hypothesis does not rewrite a cardinal that was normalized while it held.

### Remainder for finite cardinals

For finite `kappa` and positive natural cardinal `n`, Python `%` is the ordinary natural-number remainder, returned as a finite cardinal:

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

`CardinalOrder().EssentialImage(Aleph)` is the property subcategory of aleph cardinals.
The retained equivalence from `OrdinalOrder()` to this image supplies its inverse functor.
Apply that inverse to obtain an aleph index.
Apply `InitialOrdinal.on_object(kappa)` to obtain the initial ordinal representative of any cardinal.

Unary cardinal properties use the property-subcategory contract in [Property refinement](property-refinement.md).
The inverse images of the corresponding `Sets()` property subcategories along the representative functor own finiteness and countability.
The property applications `cat_kernel` derives return those containment predicates (D175).
Specific-cardinal queries use equality and order directly; countable infinity is `kappa == aleph0`, uncountability is `aleph0 < kappa`, and the continuum query is `kappa == continuum`.
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
Each expression returns a proposition.
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

These are the applications generated by `Cat().Inhabited()` and `Cat().Empty()`.
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

`X.cardinality()` returns an applied query with result category `Cardinal()`.
`ask(X.cardinality())` returns an owned cardinal when an exact evaluation case applies and Sage `Unknown` otherwise.
Calling `X.cardinality()` never invokes `ask()`.

The category-owned `Sets()` implementation declares the query.
Each set construction registers its exact cases from retained construction data.
A structured object uses the same inherited query on the original object.
A structure functor to `Sets()` constructs its actual set image through the public `Sets()` API.
Selecting that functor gives the source object the inherited set implementation surface.
It does not replace predicate evaluation with a separate image lookup.

The registered cases route on the index set, the selected presentation's diagram, its codomain placement (`Sets().Finite()`, `Sets().Countable()`, `Sets().Uncountable()`), and any retained constant diagram.
For a finite chosen enumeration, they apply `p.diagram().on_object(i).cardinality()` to each index of the selected product presentation `p`.
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
CardinalOrder
aleph0
continuum
generalized_continuum_hypothesis

Ordinals
OrdinalObject
OrdinalOrder
omega0

```
