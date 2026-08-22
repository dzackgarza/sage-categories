## Posets and totally ordered sets: API and capability specification

The implementation treats order as structure on a set. It does not treat order as a Python sorting convention.

The main source surfaces are [owned_sets.py](/home/dzack/research/src/dzack_research/preamble/categories/sets/owned_sets.py:1591) and [sets.sage](/home/dzack/research/src/dzack_research/preamble/categories/sets/sets.sage:1065).

### 1. Category structure

The public category constructors are:

```sage
Sets().PartiallyOrdered()
Sets().TotallyOrdered()
```

An object of `Sets().PartiallyOrdered()` is a set \(X\) equipped with a partial order \(\le_X\).

An object of `Sets().TotallyOrdered()` is a set \(X\) equipped with a total order. The implementation declares:

\[
\operatorname{TotOrdSets}\subseteq \operatorname{Posets}\subseteq \operatorname{Sets}.
\]

Thus every totally ordered set inherits the capabilities of partially ordered sets and sets.

Order and cardinality are independent properties. Valid intersections include:

```sage
Sets().Finite().PartiallyOrdered()
Sets().Finite().TotallyOrdered()
Sets().Countable().TotallyOrdered()
Sets().Countable().Infinite().TotallyOrdered()
Sets().Uncountable().TotallyOrdered()
```

The category does not infer finiteness from order.

### 2. Construction of partially ordered sets

Finite posets can be constructed from:

```sage
Poset((members, leq))
```

Here:

- `members` specifies the underlying finite set.
- `leq(x, y)` specifies whether \(x\le y\).
- The relation determines the order.
- The order need not arise from the native comparisons of the elements.

Typical constructions include inclusion posets:

```sage
Poset((subobjects, lambda A, B: A <= B))
```

and application-specific orders:

```sage
Poset((orbits, orbit_below))
```

A constructed finite poset enters `Sets().PartiallyOrdered()` automatically. This gives it the category-owned arrow and display operations.

### 3. Construction of finite totally ordered sets

The principal constructor is:

```sage
finite_ordered_set(source)
```

Its mathematical action is:

\[
(x_0,x_1,\ldots,x_n)\longmapsto
\bigl(\{x_0,x_1,\ldots,x_n\},x_0<x_1<\cdots <x_n\bigr).
\]

The displayed enumeration supplies the order. The constructor does not sort the elements.

Supported inputs include:

- an ordered enumeration;
- an existing finite set;
- an existing totally ordered finite set.

Its behavior is:

- It preserves the input order.
- It removes repeated elements.
- It retains the first occurrence of each element.
- It converts an unordered finite set using that set’s chosen iteration.
- It returns an existing totally ordered object unchanged.
- It rejects a set not known to be finite.
- Equivalent enumerations produce the same canonical object.

For example:

```sage
finite_ordered_set([a, b, a, c])
```

represents the totally ordered set

\[
a<b<c.
\]

The constructor also normalizes integer members into the mathematical integer objects used by the preamble. Thus equivalent integer spellings give the same set.

A second constructor is:

```sage
ordered_set_owned_by(elements)
```

This constructor is for elements already in the mathematical vocabulary. It preserves them without raw-input normalization. See [sets.sage](/home/dzack/research/src/dzack_research/preamble/categories/sets/sets.sage:1120).

The semantic result type is `OrderedSet[E]`. It means a set with a distinguished total order, not a list or sequence. See [foundations.py](/home/dzack/research/src/dzack_research/preamble/lexicon/foundations.py:45).

### 4. Canonical simplex orders

The preamble supplies canonical ordered sets through:

```sage
Sets.Δ[n]
```

For an integer \(n\ge -1\),

\[
\Delta[n]=\{0<1<\cdots<n\}.
\]

Consequently:

- `Sets.Δ[-1]` is the empty ordered set.
- `Sets.Δ[0]` is the singleton ordered set.
- `Sets.Δ[n]` has cardinality \(n+1\).

It also supports:

```sage
Sets.Δ[Sets.ℵ[0]]
```

This is the countably infinite ordered set of nonnegative integers. It belongs to:

```sage
Sets().Countable().Infinite().TotallyOrdered()
```

See [sets.sage](/home/dzack/research/src/dzack_research/preamble/categories/sets/sets.sage:1152).

### 5. Underlying set capabilities

Every partially or totally ordered set inherits the `Sets()` API.

This includes:

```sage
X.cardinality()
X.is_finite()
X.is_infinite()
X.is_countable()
X.is_uncountable()

X.power_set()
X.subsets_of_size(k)
X.finite_subsets()

Y.exponential(X)
Y ** X

X.Hom(Y)
```

A finite ordered set also supplies:

```sage
X.symmetric_group()
```

This is the automorphism group of the underlying set in `Sets()`. It is not the order-automorphism group.

For a finite total order, every order automorphism fixes each element. Its order-automorphism group is therefore trivial.

### 6. Enumeration and positional access

When an ordered set has a chosen enumeration, it supports:

```sage
X[n]
X.position(x)
X.enumeration_injection()
```

The contracts are:

```sage
X[n]                  # element at position n
X.position(x)         # position of x
X[X.position(x)] == x
```

The enumeration injection is the monomorphism

\[
X\hookrightarrow \mathbb Z_{\ge 0},
\qquad
x\longmapsto \operatorname{position}(x).
\]

For a finite total order, the chosen enumeration is also the order data.

For an infinite enumeration, `position(x)` terminates for members. It has no termination promise for a nonmember.

### 7. Order-relation API

Finite poset objects expose semantic relation queries such as:

```sage
P.is_lequal(x, y)
P.is_less_than(x, y)
P.compare_elements(x, y)
P.covers(x, y)

P.lower_covers(x)
P.upper_covers(x)
P.common_lower_covers(elements)
P.common_upper_covers(elements)
```

They also expose interval and closure operations:

```sage
P.open_interval(x, y)
P.closed_interval(x, y)
P.principal_order_ideal(x)
P.principal_order_filter(x)
P.order_ideal(elements)
P.order_filter(elements)
```

A finite totally ordered set exposes its relation through:

```sage
T.le(x, y)
```

Its enumeration also gives:

```sage
T.rank(x)
T.unrank(n)
T[n]
T.position(x)
```

### 8. Extrema, rank, and decomposition

Finite posets support:

```sage
P.minimal_elements()
P.maximal_elements()
P.has_bottom()
P.bottom()
P.has_top()
P.top()
P.is_bounded()

P.height()
P.width()
P.rank()
P.rank_function()
P.level_sets()
P.is_ranked()
P.is_graded()
```

The API supports connected components and ordinal decompositions:

```sage
P.connected_components()
P.ordinal_summands()
```

### 9. Chains and antichains

The finite-poset surface includes:

```sage
P.chains()
P.maximal_chains()
P.maximal_chains_iterator()
P.is_chain()
P.is_chain_of_poset(elements)

P.antichains()
P.antichains_iterator()
P.maximal_antichains()
P.is_antichain_of_poset(elements)

P.dilworth_decomposition()
P.greene_shape()
P.is_sperner()
```

It can also construct and enumerate linear extensions:

```sage
P.linear_extension()
P.linear_extensions()
P.is_linear_extension(order)
P.random_linear_extension()
```

### 10. Subposets and standard constructions

Finite posets support:

```sage
P.subposet(members)
P.relabel(mapping)
P.with_bounds()
P.without_bounds()
P.completion_by_cuts()
P.intervals_poset()
```

They also support categorical and order-theoretic combinations:

```sage
P.product(Q)
P.disjoint_union(Q)
P.ordinal_sum(Q)
P.ordinal_product(Q)
P.lexicographic_sum(...)
```

The source uses induced subposets to represent classes such as elliptic, parabolic, or hyperbolic subdiagrams.

### 11. Lattice-theoretic capabilities

A finite poset can answer:

```sage
P.is_lattice()
P.is_meet_semilattice()
P.is_join_semilattice()
P.meet(x, y)
P.join(x, y)
```

These operations belong only where the required meets or joins exist.

### 12. Enumerative and algebraic invariants

Finite posets expose:

```sage
P.moebius_function(x, y)
P.moebius_function_matrix()
P.zeta_polynomial()
P.order_polynomial()
P.chain_polynomial()
P.characteristic_polynomial()

P.incidence_algebra(R)
P.order_complex()
P.order_polytope()
P.chain_polytope()
P.comparability_graph()
P.incomparability_graph()
```

The implementation also retains finite-poset dynamics such as promotion, evacuation, rowmotion, toggles, and Panyushev complementation.

### 13. Morphisms of posets

For posets \(P\) and \(Q\), construct a morphism with:

```sage
C = Sets().PartiallyOrdered()
f = C.Hom(P, Q)(definition)
```

The definition can be:

- a callable `lambda x: ...`;
- an explicit mapping when the domain is finite;
- an existing arrow in the same Hom category.

The resulting arrow supports:

```sage
f.domain()
f.codomain()
f(x)
f.is_order_preserving()
f.is_order_reflecting()
f.is_order_embedding()
f.is_order_isomorphism()
f.inverse()
```

The semantic meanings are:

\[
\begin{aligned}
f\text{ preserves order}
&\iff x\le_P y\Longrightarrow f(x)\le_Q f(y),\\
f\text{ reflects order}
&\iff f(x)\le_Q f(y)\Longrightarrow x\le_P y,\\
f\text{ is an order embedding}
&\iff f\text{ preserves and reflects order},\\
f\text{ is an order isomorphism}
&\iff f\text{ is a bijective order embedding}.
\end{aligned}
\]

`is_order_reflecting()` currently computes over all pairs in a represented finite domain. Therefore `is_order_embedding()`, `is_order_isomorphism()`, and `inverse()` have the same effective finite-domain scope.

Order preservation is trusted when the arrow enters the poset Hom category. The constructor does not attempt to prove monotonicity for an arbitrary callable.

The arrow also inherits ordinary set-map capabilities:

```sage
f.is_injective()
f.is_surjective()
f.is_bijective()
f.is_monomorphism()
f.is_epimorphism()
f.is_isomorphism()
```

### 14. Hasse diagrams and notebook display

Finite posets support:

```sage
P.hasse_layout()
P.hasse_tikz()
P.hasse_tikz(label_map=labels, scale=1.5)
P.tikz()
```

The display surface provides:

- coordinates arranged by order level;
- edges for cover relations;
- custom labels;
- adjustable scale;
- TikZ output;
- inline SVG notebook output;
- LaTeX output;
- rich MIME output;
- light and dark notebook themes.

The installation hook places constructed finite posets into the owned category. They then receive these display methods through category inheritance. See [owned_sets.py](/home/dzack/research/src/dzack_research/preamble/categories/sets/owned_sets.py:1314).

### 15. Effective scope

The category model itself permits finite and infinite partial or total orders.

The concrete constructors provide:

- general represented finite posets;
- canonical finite total orders from enumerations;
- the countably infinite order `Sets.Δ[Sets.ℵ[0]]`.

The Hasse-diagram surface is for finite represented posets. Exhaustive order-reflection checks also require finite represented domains. Infinite ordered sets retain the categorical structure, set operations, cardinality properties, and declared morphisms without forced enumeration.
