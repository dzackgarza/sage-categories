# Sets specification

`Sets()` owns the set-theoretic surface inherited by categories with a selected functor to `Sets()`.

This document specifies the public API and its mathematical semantics.
Concrete realizations can use Sage algorithms and runtime machinery internally.

## Fundamental model

`Sets()` owns three fundamental implementation types:

- `Sets.ObjectType`: a set parent.

- `Sets.ElementType`: an element with its parent.

- `Sets.ArrowType`: a total function with a declared domain and codomain.

The object and arrow maps of a selected forgetful functor provide this surface to another category.

A set can be represented by:

- an existing Sage parent;

- a finite or iterable collection;

- a predicate `Element -> bool | Unknown` inside another set;

- the image of a function;

- the object set of a discrete category;

- a universal construction from other sets.

The public surface constructs a set directly, a predicate subobject through `X.subset_from(predicate)`, an image through `f.image()`, and the object set through `C.objects()`.

Infinite objects do not require enumeration.
A predicate or callable can define them directly.

`Unknown` records unavailable computational knowledge.
It never means `False` and never changes the underlying mathematical object.

## Implementation ownership

[Category ownership](../CONTRIBUTING.md#category-ownership-and-inheritance), [leaf-category encapsulation](../CONTRIBUTING.md#leaf-category-encapsulation), and [functor policies](../CONTRIBUTING.md#functors-and-universal-constructions) govern inheritance.

The `Sets()` subtree owns sets, elements, total functions, set subobjects, cardinality, and universal constructions in `Sets()`. For \(U_C:C\to\mathbf{Sets}\), declaring its object and arrow maps supplies this surface to \(C\). Property subcategories such as `Sets().Finite()` add their property-specific constructions and inherit the rest through inclusion.

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
X.powerset()
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
A.powerset()
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

## Powersets, subset posets, and thin categories

Every set supplies:

```python
X.powerset()
X.subset_poset()
```

`X.powerset()` is the set of subobjects of \(X\). `X.subset_poset()` has the same subsets as its elements and orders them by containment:

\[
A\leq B \quad\Longleftrightarrow\quad A\hookrightarrow X
\text{ factors through } B\hookrightarrow X.
\]

Every poset \(P\) determines its thin category `P.thin_category()`. The elements of \(P\) become objects, and

\[
\operatorname{Hom}(p,q)=
\begin{cases}
\{p\leq q\},&p\leq q,\\
\varnothing,&\text{otherwise.}
\end{cases}
\]

For a set \(X\), the following constructions are canonically equivalent:

- the thin category of `X.subset_poset()`;

- the thin category of the Boolean-lattice order on `X.powerset()`;

- the category of subobjects of \(X\) in `Sets()`.

If \(X\) later receives the discrete topology, the topology layer identifies this category with \(\operatorname{Open}(X)\). Topology remains owned by its own category; `Sets()` supplies only the powerset, the containment order, and their categorical compatibility.

Because `X.powerset()` is itself a set, it has the standard predicate-subobject interface:

```python
tau = X.powerset().subset_from(is_open)
```

This constructs a subobject \(\tau\hookrightarrow P(X)\) without enumerating \(P(X)\). A topology layer can accept \(\tau\), establish the topology axioms, and construct the associated topological space.
In order-theoretic terms, \(\tau\) contains the bottom and top subsets and is closed under arbitrary joins and finite meets.
The discrete topology is the case \(\tau=P(X)\).

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

## Cardinalities and ordinals

The complete cardinal and ordinal APIs are specified in [cardinality.md](cardinality.md).
Within `Sets()`, `X.cardinality()` and the cardinality functor expose that theory; each set construction supplies its own cardinal expression.

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

## Ordered sets

The complete API is specified in [ordered-sets.md](ordered-sets.md).
Within `Sets()`, partial and total order are independent of cardinality, while a chosen enumeration supplies positional access.

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

[Representation policies](../CONTRIBUTING.md#semantic-representations), [engine-boundary policies](../CONTRIBUTING.md#computation-engine-encapsulation), and [repository-layout policies](../CONTRIBUTING.md#mathematical-encapsulation-and-repository-layout) govern the general boundary.

Set-specific representations preserve the mathematics: callables for infinite maps, indexed families for products, tagged values for coproducts, monomorphisms for subsets, symbolic cardinal expressions, and diagrams for universal constructions.
Enumeration remains optional structure.

## SymPy integration strategy

SymPy supplies private symbolic representations and simplification algorithms behind the owned `Sets()` API.

| Owned requirement | SymPy contribution | Integration contract |
| --- | --- | --- |
| Three-valued membership | `Contains(x, X)` can remain symbolic. Fuzzy queries return `True`, `False`, or `None`. | Translate definite results to `bool` and `None` to Sage `Unknown`. Retain an unevaluated `Contains` proposition for later symbolic evaluation. |
| Predicate-defined subobjects | `ConditionSet(x, P(x), X)` represents \(\{x\in X\mid P(x)\}\) without enumeration. | Use `ConditionSet` as a private representation. The public object retains its inclusion arrow. |
| Three-valued subset relations | SymPy set properties can return `None` when unresolved. | Normalize every public subset predicate to <code>bool &#124; Unknown</code>. Translate `None` and unresolved symbolic propositions to `Unknown`. |
| Semantic equality of sets | SymPy `==` supplies structural equality. | Treat structural equality as sufficient evidence for `True`. Use the owned subobject order for semantic equality. Return `Unknown` when available methods prove neither equality nor inequality. |
| Cardinal objects | SymPy supplies finite sizes and Lebesgue measure for supported representations. | `Cardinalities()` owns cardinal arithmetic, normalization, comparisons, and the cardinality functor. Construction data and proved relationships determine cardinality. |
| Cardinal predicates and comparisons | SymPy supplies symbolic expression simplification. | `Cardinalities()` evaluates finite, countable, continuum-sized, and larger cardinal expressions. Unproved predicates and comparisons return `Unknown`. |
| Images of arbitrary sets | `ImageSet(f, X)` represents \(\{f(x)\mid x\in X\}\) and can remain unevaluated. | Use `ImageSet` as a private symbolic representation. The public result retains its monomorphism into the codomain. |
| Subobjects | `ConditionSet` supplies the predicate-defined underlying set expression. | The owned subobject stores both that set object and the inclusion arrow \(A\hookrightarrow X\). |
| Universal set constructions | SymPy represents and simplifies products, unions, intersections, power sets, and images. | The owned categories retain diagrams, cones, cocones, projections, injections, and universal morphisms. |
| Non-finitary function sets | SymPy supplies symbolic expressions used by callable rules. | Construct \(Y^X\) through `X.Hom(Y).objects()`, `ExponentialOfSets(Y, X)`, and `Y ** X`. Callable rules represent arbitrary domains. |

Membership queries use `Contains(x, X)` or `X.contains(x)` and translate into the owned `bool | Unknown` contract.

SymPy integration is confined to set representations and computations.
Sheaves, morphisms of sheaves, functors, and other categorical objects retain their own categories.

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
