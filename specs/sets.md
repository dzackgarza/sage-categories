# Sets specification

`Sets()` is the foundation of every owned mathematical object.
It supplies the complete set-theoretic surface used by higher categories.

This document specifies the public API and its mathematical semantics.
Concrete realizations can use Sage algorithms and runtime machinery internally.

## Fundamental model

`Sets()` owns three fundamental implementation types:

- `Sets.ObjectType`: a set parent.

- `Sets.ElementType`: an element with its parent.

- `Sets.ArrowType`: a total function with a declared domain and codomain.

Every higher mathematical object inherits this set-level surface.
Rings, modules, groups, and lattices do not define parallel notions of cardinality or set maps.

A set can be represented by:

- an existing Sage parent;

- a finite or iterable collection;

- a predicate `Element -> bool | Unknown` inside another set;

- the image of a function;

- the object set of a discrete category;

- a universal construction from other sets.

The public constructors are `Set`, `ConditionSet`, `ImageSet`, and `ObjectSet`.

Infinite objects do not require enumeration.
A predicate or callable can define them directly.

`Unknown` records unavailable computational knowledge.
It never means `False` and never changes the underlying mathematical object.

## API on every set object

Every object of `Sets()` is intended to support:

```python
X.cardinality()
X.is_finite()
X.is_infinite()
X.is_countable()
X.is_uncountable()
X.contains(x)

X.Hom(Y)
X.End()
X.Aut()
X.Iso(Y)
X.Mono(Y)
X.Epi(Y)
X.identity()

X.subobjects()
X.superobjects()
X.covering_objects()
X.covered_objects()

X.exponential(Y)
X ** Y
X.power_set()
X.subsets_of_size(k)
X.finite_subsets()
```

The categorical operations come from `_CategoricalObject`. They are not redefined independently for sets.

`X.cardinality()` always returns a cardinal object.
The cardinal can remain a formal expression when no normalization is available.

The predicates and `X.contains(x)` return `bool | Unknown`. Placement in a property subcategory supplies a definite answer.

## Functions and function sets

`X.Hom(Y)` is the category of functions \(X\to Y\). A function can use:

- a callable for arbitrary domains;

- an explicit mapping for finite domains.

Every evaluation checks both membership facts when their procedures return definite answers:

```python
X.contains(x)
Y.contains(f(x))
```

A function remains a total semantic arrow when a membership procedure returns `Unknown`. Unavailable validation does not reject the arrow.

The Hom category supplies:

```python
f(x)
f.domain()
f.codomain()
f.is_injective()
f.is_surjective()
f.is_bijective()

X.Hom(X).identity()
X.Hom(Z).compose(g, f)
X.Hom(Y).objects()
```

The function set \(Y^X\) is the object set of `X.Hom(Y)`. Its elements are the same semantic functions.

Thus these represent one construction:

```python
X.Hom(Y).objects()
ExponentialOfSets(Y, X)
Y ** X
```

The exponential functor acts contravariantly in \(X\) and covariantly in \(Y\). It acts by precomposition and postcomposition.

This model supports arbitrary rules such as `QQ -> NN`, `QQ -> ZZ`, or `RR -> RR^2`. The rules need not be linear or continuous.

## Isomorphisms, monomorphisms, and epimorphisms

A set isomorphism stores a forward function and its declared inverse.

A monomorphism stores its underlying injective set arrow.
It acts as the semantic representation of a subset.

An epimorphism stores its underlying surjective set arrow.

These are objects of their own arrow categories.
They are not Boolean annotations on ordinary functions.

## Products

The product API supports arbitrary set-indexed families:

```python
CartesianProductOfFamily(I, lambda i: X_i)
CartesianProductOfSets((X, Y, Z))
```

It also acts on indexed families of functions:

```python
CartesianProductMorphismOfFamily(I, lambda i: f_i)
cartesian_product_morphism(f, g, h)
```

A product object supplies:

```python
P.diagram()
P.index_category()
P.projection(i)
P.universal_morphism(cone)
P.cardinality()
P.factor_cardinalities()
```

A product element is an indexed family.
Its representation can be a callable or explicit mapping.

```python
x[i]
x.components()
iter(x)  # only for finite index sets
```

Its cardinality is the indexed product \(\prod_i |X_i|\).

## Coproducts

The coproduct API mirrors products:

```python
CoproductOfFamily(I, lambda i: X_i)
CoproductOfSets((X, Y, Z))
CoproductMorphismOfFamily(I, lambda i: f_i)
coproduct_morphism(f, g, h)
```

A coproduct element is a tagged element:

```python
x.index()
x.value()
```

A coproduct object supplies:

```python
C.injection(i)
C.universal_morphism(cocone)
C.cardinality()
C.cofactor_cardinalities()
```

Its cardinality is the indexed sum \(\sum_i |X_i|\).

## Subsets and power objects

A subset of \(X\) is represented as a monomorphism \(A\hookrightarrow X\).

It carries:

```python
A.inclusion()
A.underlying_set()
A.characteristic_morphism()
A.power_set()
A.cardinality()
```

Membership is classified by a total characteristic morphism \(X\to\Delta[1]\). `A.contains(x)` is its computational query and can return `Unknown`.

The power object `PowerSet(X)` supports:

```python
P.base_set()
P.from_predicate(predicate)
P.from_characteristic_morphism(chi)
P.top()
P.bottom()
P.inverse_image_morphism(f)
P.direct_image_morphism(f)
P.cardinality()
```

Subset elements support:

```python
x in A
A.contains(x)
A <= B
A.union(B)
A.intersection(B)
A.difference(B)
A.symmetric_difference(B)
A.complement()

A | B
```

`A.contains(x)`, subset equality, and subset order return `bool | Unknown`. The `in` syntax is reserved for represented decidable membership.

This makes \(P(X)\) both:

- the set of subobjects of \(X\);

- the function set \(\operatorname{Hom}(X,\Delta[1])\);

- a bounded distributive Boolean lattice.

Inverse image makes the power object contravariant.
Every set arrow also induces a direct-image arrow.

Direct image constructs the semantic image subobject without enumerating its source.
Its membership evaluator can return `Unknown`.

## Finite and fixed-cardinality subsets

The additional constructors are:

```python
FiniteSubsets(X)
SubsetsOfSize(X, k)
```

For countable \(X\), both receive chosen enumerations.

`FiniteSubsets(X)` supports:

```python
S.cardinality()
S.index(subset)
S[n]
```

`SubsetsOfSize(X, k)` supports:

```python
S.subset_cardinality()
S.cardinality()
S[n]
```

For infinite \(X\) and positive finite \(k\), the implementation records:

\[
|[X]^k|=|X|.
\]

For infinite \(X\):

\[
|P_{\mathrm{fin}}(X)|=|X|.
\]

## Cardinalities

Cardinalities are mathematical objects, not integers or metadata.

`Cardinalities()` is the thin category defined by cardinal order.
A unique arrow \(\kappa\to\lambda\) exists when the represented theory proves \(\kappa\leq\lambda\).

Constructors include:

```python
cardinal(n)
aleph(alpha)

aleph0
continuum
Sets.ℵ[n]
Sets.א[n]
```

Cardinal objects support:

```python
k + l
k * l
k ** l

k <= l
k < l

k.is_finite()
k.is_infinite()
k.is_countable()
k.is_uncountable()
k.is_aleph()
k.is_continuum()
k.aleph_index()
k.initial_ordinal()
```

The category supports:

```python
Cardinalities().sum(...)
Cardinalities().product(...)
Cardinalities().indexed_sum(I, family)
Cardinalities().indexed_product(I, family)
Cardinalities().power(base, exponent)
Cardinalities().supremum(...)
Cardinalities().compare(k, l)
```

Symbolic expressions remain symbolic when the represented theory cannot normalize them.
This avoids assuming the continuum hypothesis.

Cardinal predicates and comparisons return `bool | Unknown`. Failure to prove an inequality does not prove its negation.

`Cardinalities().compare(k, l)` returns a proved order relation or `Unknown`.

The cardinality functor is:

\[
\#:\operatorname{core}(\mathbf{Set})\longrightarrow\mathbf{Cardinalities}.
\]

It sends isomorphic sets to equal cardinal objects.
It also supplies comparison arrows for products, coproducts, and power objects.

The cardinality functor is defined on every owned set.
It returns formal cardinal expressions when a concrete simplification is unavailable.

## Ordinals

`Ordinals()` is the commutative semiring under Hessenberg natural sum and product.

Its user API includes:

```python
ordinal(n)
omega(alpha)
omega0

a + b
a * b
a.ordinal_sum(b)
a.ordinal_product(b)
a.ordinal_power(b)

a.is_initial()
a.initial_index()
a.cardinality()
```

Natural operations use `+` and `*`. Ordinary noncommutative ordinal operations have explicit names.

`omega(alpha).cardinality()` returns `aleph(alpha)`.

## Cardinality and enumeration are distinct

The set axioms are:

```python
Sets().Finite()
Sets().Infinite()
Sets().Countable()
Sets().Uncountable()
Sets().PartiallyOrdered()
Sets().TotallyOrdered()
```

Countability means that an injection into `NN` exists.
It does not select an enumeration.

For a generic set, countability predicates can return `Unknown`. Placement in `Countable()` or `Uncountable()` records an established result.

A chosen enumeration adds:

```python
X[n]
X.position(x)
X.enumeration_injection()
```

`enumeration_injection()` returns the actual monomorphism \(X\hookrightarrow\mathbb N\).

Countably infinite sets have exact cardinality `aleph0`. Uncountable sets inherit infinitude.

## Ordered sets and finite ordinals

`finite_ordered_set(elements)` transports the displayed enumeration into a total order.
It does not sort the elements.

`ordered_set_owned_by(elements)` preserves an already meaningful order.

The standard indexing objects are:

```python
Sets.Δ[-1]  # empty
Sets.Δ[n]   # {0, ..., n}
Sets.Δ[aleph0]  # NN with its standard order
```

Partially ordered sets add:

```python
f.is_order_preserving()
f.is_order_reflecting()
f.is_order_embedding()
f.is_order_isomorphism()
f.inverse()

X.hasse_layout()
X.hasse_tikz()
X.tikz()
```

Order predicates return `bool | Unknown` when no applicable decision procedure is available.

Finite posets render as TikZ, LaTeX, HTML, and notebook MIME output.

## Finitely supported function sets

For a pointed set \((X,x_0)\) and index set \(S\), the implementation represents:

\[
X^{(S)}=\{a:S\to X:\operatorname{supp}(a)\text{ is finite}\}.
\]

The object records:

```python
A.index_set()
A.value_set()
A.basepoint()
A.cardinality()
```

For finite \(S\), its cardinality is \(|X|^{|S|}\).

For infinite \(S\) and nontrivial \(X\), it is:

\[
\max(|X|,|S|).
\]

## Representation strategy

The representation boundaries are:

- Owned parents and elements define the public set surface.

- Sage parents can supply private concrete realizations.

- Elements retain their exact parent.

- Infinite set maps use callables.

- Finite set maps can use explicit mappings.

- Product elements use indexed functions.

- Coproduct elements use tagged values.

- Subsets use monomorphisms and characteristic morphisms.

- Function sets reuse Hom-category objects.

- Universal constructions retain their diagrams.

- Cardinalities and ordinals retain symbolic expression trees.

- Category refinement records only established properties.

- Enumeration remains optional structure.

No construction must enumerate an infinite set merely to establish its mathematical form.

## Unknown and partial computation

The mathematical object and the available decision procedure are separate data.

These operations return `bool | Unknown`:

```python
X.contains(x)
X.is_finite()
X.is_infinite()
X.is_countable()
X.is_uncountable()

A == B
A <= B

kappa < lambda
kappa <= lambda
kappa.is_finite()
kappa.is_infinite()
kappa.is_countable()
kappa.is_uncountable()
```

The following rules apply uniformly:

- A proved proposition returns `True`.

- A proved negation returns `False`.

- Missing data or an unavailable algorithm returns `Unknown`.

- Boolean negation preserves `Unknown`.

- Conjunction and disjunction use Sage's three-valued logic.

- A universal construction remains available when a predicate is unknown.

- Category refinement occurs only after a definite result or cited theorem.

A predicate-defined subobject remains an honest monomorphism when membership is not decidable for every input.

An image remains an honest subobject when preimage existence cannot be decided computationally.

A cardinal remains a cardinal object when its expression cannot be normalized or compared with another expression.
