## Posets and totally ordered sets: specification

This package models order as mathematical structure on a set.

### 1. Category hierarchy

The category constructors are:

```sage
PartiallyOrderedSets()
TotallyOrderedSets()
FinitePosets()
FiniteTotallyOrderedSets()
```

The categorical inclusions and forgetful functors form the commutative graph:

\[
\begin{array}{ccc}
\mathbf{FinTotOrd} & \hookrightarrow & \mathbf{TotOrd} \\
\downarrow & & \downarrow \\
\mathbf{FinPoset} & \hookrightarrow & \mathbf{Poset} \\
\downarrow & & \downarrow \\
\mathbf{FinSet} & \hookrightarrow & \mathbf{Set}
\end{array}
\]

Every totally ordered set inherits partial-order operations through its structural inclusion.
Every partially ordered set inherits set operations through its forgetful functor.

Order and cardinality remain independent properties.

### 2. Partial-order validation

A partially ordered set is a set \(X\) equipped with a relation \(\le\) that satisfies:

- Reflexivity: \(x \le x\) for all \(x \in X\).

- Antisymmetry: \(x \le y \land y \le x \implies x = y\).

- Transitivity: \(x \le y \land y \le z \implies x \le z\).

Construct a poset with:

```sage
Poset((members, leq))
PartiallyOrderedSets()(underlying_set, relation)
```

For finite sets, construction evaluates the relation on all pairs and triples:

- The constructor rejects non-reflexive relations.

- The constructor rejects non-antisymmetric relations.

- The constructor rejects non-transitive relations.

- The constructor rejects relations that return `Unknown`.

### 3. Totality and category refinement

A total order is a partial order whose elements are pairwise comparable:

\[
\forall x, y \in X, \quad x \le y \lor y \le x.
\]

Construct a total order with:

```sage
finite_ordered_set(elements)
TotallyOrderedSets()(poset)
FiniteTotallyOrderedSets()(poset)
```

The totality query `is_total_order(poset)` returns:

- `True` when every pair of elements in a finite poset is comparable.

- `False` when an incomparable pair exists.

- `Unknown` when totality cannot be determined algorithmically.

Category refinement requires totality to be `True`. The constructor rejects non-total posets and unknown comparisons.

### 4. Canonical simplex orders

Canonical simplex orders are provided by `SimplexOrders()`:

```sage
SimplexOrders()[n]
SimplexOrders()[Aleph0]
```

- `SimplexOrders()[n]` is the finite total order \(\{0 < 1 < \cdots < n\}\).

- `SimplexOrders()[Aleph0]` is the countably infinite total order of natural numbers with standard ordinal comparison.

### 5. Morphisms and monotonicity

Poset morphisms are order-preserving set maps:

\[
x \le_P y \implies f(x) \le_Q f(y).
\]

Construct a morphism with:

```sage
Hom = PartiallyOrderedSets().Hom(P, Q)
f = Hom(mapping)
```

Admission rules:

- For finite domains, the constructor verifies monotonicity on all pairs \(x \le_P y\).

- It rejects candidate maps where \(f(x) \le_Q f(y)\) is `False` or `Unknown`.

Arrow properties:

- `f.is_order_preserving()` returns `True`.

- `f.is_order_reflecting()` checks whether \(f(x) \le_Q f(y) \implies x \le_P y\).

- `f.is_order_embedding()` returns whether \(f\) preserves and reflects order.

- `f.is_order_isomorphism()` returns whether \(f\) is a bijective order embedding.

### 6. Categorical limits and products

Categorical products in `PartiallyOrderedSets()` lift products in `Sets()`:

- Apex: The set product \(X = \prod_i X_i\) equipped with the componentwise order:
  \[
  x \le y \iff \forall i, \; \pi_i(x) \le_i \pi_i(y).
  \]

- Projections: Each projection \(\pi_i: X \to X_i\) is an order-preserving morphism in `PartiallyOrderedSets()`.

- Universal map: For any cone \(C \to X_i\), the mediating arrow \(\langle f_i \rangle: C \to X\) is order-preserving.

### 7. Method compilation and full-route transport

Structural method forwarding follows the compiled route:

- Receivers and arguments transport to the declaring category.

- Stored methods invoke on their target category implementation.

- Return values and iterator elements reverse-transport to the caller's category.

- Canonical image caching ensures coherent representations across parallel routes.
