# Sets specification

`Sets()` owns the set-theoretic surface inherited by categories with a selected functor to `Sets()`.

This document specifies the public API and its mathematical semantics.
Concrete realizations can use Sage algorithms and runtime machinery internally.

## Mathematical foundation

This specification uses the ordinary category \(\mathbf{Set}\).

*Definition.* An object of \(\mathbf{Set}\) is a set \(X\). An element of \(X\) is a
mathematical value \(x\) satisfying \(x\in X\).

*Definition.* A morphism \(f:X\to Y\) is a total single-valued function. Equivalently,
its graph \(\Gamma_f\subseteq X\times Y\) satisfies

\[
\forall x\in X,\quad \exists!y\in Y,\quad (x,y)\in\Gamma_f.
\]

Two functions \(f,g:X\to Y\) are equal exactly when

\[
\forall x\in X,\quad f(x)=g(x).
\]

The identity is \(\operatorname{id}_X(x)=x\). Composition is
\((g\circ f)(x)=g(f(x))\). These operations make sets and total functions a category.

For sets \(X\) and \(Y\), the Hom object, function set, and exponential are the same
set:

\[
\operatorname{Hom}_{\mathbf{Set}}(X,Y)=Y^X
=\{f\mid f:X\to Y\}.
\]

*Definition.* A subset of \(X\) is a set \(A\) with \(A\subseteq X\), together with
its inclusion \(\iota_A:A\hookrightarrow X\). A subobject of \(X\) is an isomorphism
class of monomorphisms into \(X\). Two monomorphisms \(m:A\to X\) and \(n:B\to X\)
represent the same subobject when an isomorphism \(u:A\to B\) satisfies \(n\circ u=m\).
Every subobject of a set has one canonical subset representative, its image. Thus
\(\operatorname{Sub}(X)\) is canonically identified with the power set
\(\mathcal P(X)\), but a chosen monomorphism is not literally the same datum as its image
subset.

Let \(\mathbf 2=\{0,1\}\). Each subset \(A\subseteq X\) has the characteristic function

\[
\chi_A:X\to\mathbf 2,
\qquad
\chi_A(x)=1\iff x\in A.
\]

Hence

\[
\mathcal P(X)\cong \mathbf 2^X
=\operatorname{Hom}_{\mathbf{Set}}(X,\mathbf 2).
\]

Membership, equality, totality, injectivity, surjectivity, and cardinality are
mathematical facts. `Unknown` describes the present decision procedure, not another
truth value and not another kind of set or function.

## Owned implementation model

`Sets()` owns three fundamental implementation types:

- `Sets.ObjectType`: a set parent.

- `Sets.ElementType`: an element with its parent.

- `Sets.ArrowType`: a total function with a declared domain and codomain.

The object and arrow maps of a selected forgetful functor provide this surface to another category.

An owned element represents an incidence \((X,x)\) with \(x\in X\). The same underlying
mathematical value can belong to two sets, but its two owned element values have different
ambient objects. Morphism evaluation and structural transport preserve that ambient
object.

A set can have a private representation such as:

- an existing Sage parent;

- a finite or iterable collection;

- a formula defining a subset of another set, with a partial decision procedure;

- the image of a function;

- the object set of a discrete category;

- a universal construction from other sets.

The public surface constructs a set directly, a predicate subobject through `X.subset_from(predicate)`, an image through `f.image()`, and the object set through `C.objects()`.

Infinite objects do not require enumeration.
A formula, construction, or theorem can define them directly. A callable can serve as a
private evaluator for that definition.

The implementation types represent the mathematical roles above. They do not create
those roles through markers, registries, or transport annotations.

## Implementation ownership

[Category ownership](../CONTRIBUTING.md#category-ownership-and-inheritance), [leaf-category encapsulation](../CONTRIBUTING.md#leaf-category-encapsulation), and [functor policies](../CONTRIBUTING.md#functors-and-universal-constructions) govern inheritance.

The `Sets()` subtree owns sets, elements, total functions, set subobjects, cardinality, and universal constructions in `Sets()`. For \(U_C:C\to\mathbf{Sets}\), declaring its object and arrow maps supplies this surface to \(C\). Property subcategories such as `Sets().Finite()` add their property-specific constructions and inherit the rest through inclusion.

## API on every set object

Every object of `Sets()` is intended to support:

```python
X.cardinality()
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

Finiteness, infinitude, countability, and uncountability are property subcategories.
Their membership procedures return an exact decision when the available mathematics
determines one. Placement in such a subcategory records an established proposition.

## Functions and function sets

`X.Hom(Y)` denotes the owned Hom object of functions \(X\to Y\). A private function
representation can use:

- a callable for arbitrary domains;

- an explicit mapping for finite domains.

The construction route must establish that the rule is total and lands in \(Y\).
It can use an exact check, an explicit scoped hypothesis, or the theorem of a named
construction. An `Unknown` validation result does not admit an arbitrary callable as a
set morphism.

After admission, evaluation requires \(x\in X\) and returns the owned element
\(f(x)\in Y\). The public arrow therefore retains its domain, codomain, and totality even
when its private rule is callable.

The owned set-Hom structure supplies:

```python
f(x)
f.domain()
f.codomain()

X.Hom(X).identity()
X.Hom(Z).compose(g, f)
```

The function set \(Y^X\), exponential, and set Hom object are one construction:

```python
X.Hom(Y)
ExponentialOfSets(Y, X)
Y ** X
```

The exponential functor acts contravariantly in \(X\) and covariantly in \(Y\). It acts by precomposition and postcomposition.

Its evaluation map is

\[
\operatorname{ev}:Y^X\times X\to Y,
\qquad
\operatorname{ev}(f,x)=f(x).
\]

For every map \(h:T\times X\to Y\), there is one map

\[
\lambda h:T\to Y^X
\]

satisfying \(\operatorname{ev}\circ((\lambda h)\times\operatorname{id}_X)=h\). This
currying property defines the exponential object.

This model supports arbitrary rules such as `QQ -> NN`, `QQ -> ZZ`, or `RR -> RR^2`. The rules need not be linear or continuous.

## Isomorphisms, monomorphisms, and epimorphisms

A function \(f:X\to Y\) is injective when

\[
\forall x,x'\in X,\quad f(x)=f(x')\Longrightarrow x=x'.
\]

It is surjective when

\[
\forall y\in Y,\quad \exists x\in X,\quad f(x)=y.
\]

It is bijective when it is injective and surjective. A set isomorphism is exactly a
bijection. Its inverse satisfies both inverse equations.

A monomorphism in \(\mathbf{Set}\) is exactly an injective function. A chosen
monomorphism represents a subobject; its image is the corresponding subset.

An epimorphism in \(\mathbf{Set}\) is exactly a surjective function.

These are objects of their own arrow categories.
They are not Boolean annotations on ordinary functions.

## Products

For a family \((X_i)_{i\in I}\), the product set is

\[
\prod_{i\in I}X_i
=\{x:I\to\bigcup_{i\in I}X_i\mid \forall i\in I,\ x(i)\in X_i\}.
\]

Its projection \(\pi_i\) evaluates a family at \(i\). For every set \(T\) and family
of maps \(f_i:T\to X_i\), there is one map

\[
\langle f_i\rangle:T\to\prod_{i\in I}X_i,
\qquad
\pi_i\circ\langle f_j\rangle=f_i
\]

for all \(i\in I\). This universal property, not a tuple representation, defines the
categorical product.

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

For a family \((X_i)_{i\in I}\), the coproduct set is the disjoint union

\[
\coprod_{i\in I}X_i=\{(i,x)\mid i\in I,\ x\in X_i\}.
\]

Its injection is \(\iota_i(x)=(i,x)\). For every family of maps
\(f_i:X_i\to T\), there is one map \([f_i]:\coprod_iX_i\to T\) satisfying

\[
[f_i]\circ\iota_i=f_i
\]

for all \(i\in I\).

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

## General limits and colimits

Let \(D:J\to\mathbf{Set}\) be a small diagram. Its limit is the set of compatible
families

\[
\varprojlim D
=\left\{(x_j)_{j\in\operatorname{Ob}(J)}\in\prod_jD(j)
\ \middle|\
\forall(\alpha:j\to k),\ D(\alpha)(x_j)=x_k
\right\}.
\]

The coordinate maps form its limiting cone. For every other cone, the unique mediating
map sends an element to its family of cone components.

The colimit is the quotient

\[
\varinjlim D
=\left(\coprod_{j\in\operatorname{Ob}(J)}D(j)\right)\!\big/\sim,
\]

where \(\sim\) is the least equivalence relation satisfying

\[
(j,x)\sim(k,D(\alpha)(x))
\]

for every arrow \(\alpha:j\to k\) and every \(x\in D(j)\). The quotient maps form the
colimiting cocone. Every other cocone factors uniquely through this quotient.

Products and coproducts are the limits and colimits of discrete diagrams. Equalizers,
pullbacks, coequalizers, and pushouts are the corresponding finite diagram shapes. The
owned construction retains the diagram, cone or cocone, and universal map in every
case.

## Subsets and power objects

A chosen subset of \(X\) retains its inclusion monomorphism \(A\hookrightarrow X\).

It carries:

```python
A.inclusion()
A.underlying_set()
A.characteristic_morphism()
A.powerset()
A.cardinality()
```

Membership is classified by the characteristic morphism \(\chi_A:X\to\mathbf 2\).
Its mathematical value is definite. A computation of that value can return `Unknown`.

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
A <= B
A.union(B)
A.intersection(B)
A.difference(B)
A.symmetric_difference(B)
A.complement()

A | B
```

Computations of membership, subset equality, and subset order can return
`bool | Unknown`. The mathematical relations remain fixed when computation is
unavailable.

This gives canonical identifications among:

- the set of canonical subset representatives of subobjects of \(X\);

- the function set \(\operatorname{Hom}_{\mathbf{Set}}(X,\mathbf 2)\);

- a complete Boolean algebra.

The Boolean-algebra order is inclusion. Arbitrary joins are unions, arbitrary meets
are intersections, bottom is \(\varnothing\), top is \(X\), and complement is relative
complement in \(X\).

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

When \(X\) carries a chosen enumeration, both constructions can receive induced chosen
enumerations. Countability alone does not select one.

With that additional enumeration structure, `FiniteSubsets(X)` supports:

```python
S.cardinality()
S.index(subset)
S[n]
```

With that additional enumeration structure, `SubsetsOfSize(X, k)` supports:

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

The cardinality property subcategories are:

```python
Sets().Finite()
Sets().Infinite()
Sets().Countable()
Sets().Uncountable()
```

Countability means that an injection into `NN` exists.
It does not select an enumeration.

Uncountability means that no such injection exists.

For a generic set, countability predicates can return `Unknown`. Placement in `Countable()` or `Uncountable()` records an established result.

A chosen enumeration is a bijection \(e:I\to X\), where \(I\) is a finite initial
segment or \(\mathbb Z_{\geq 0}\). It adds:

```python
X[n]           # e(n)
X.position(x)  # e^{-1}(x)
X.enumeration_injection()
```

`enumeration_injection()` returns the inverse monomorphism
\(e^{-1}:X\hookrightarrow\mathbb Z_{\geq 0}\).

Countably infinite sets have exact cardinality `aleph0`. Uncountable sets inherit infinitude.

## Ordered sets

The complete API is specified in [ordered-sets.md](ordered-sets.md).
A partial order is chosen relation structure on a set, not a property of the bare set.
Different partial orders can have the same underlying set. The forgetful functor from
posets to sets discards that chosen relation. Totality is a property of a partial order,
not of its underlying set alone.

Order structure is independent of cardinality. A chosen enumeration is additional
structure and supplies positional access.

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
| Non-finitary function sets | SymPy supplies symbolic expressions used by callable rules. | Construct \(Y^X\) through `X.Hom(Y)`, `ExponentialOfSets(Y, X)`, and `Y ** X`. Callable rules privately represent maps already established to be total. |

Private membership evaluation can use `Contains(x, X)`. The public result is the owned
decision for the semantic proposition \(x\in X\).

SymPy integration is confined to set representations and computations.
Sheaves, morphisms of sheaves, functors, and other categorical objects retain their own categories.

## Unknown and partial computation

The mathematical proposition and the available decision procedure are distinct.
In the classical semantics used here, each proposition is true or false. `Unknown`
means only that the current exact computation establishes neither value.

Exact decision procedures for the following propositions return `bool | Unknown`:

- \(x\in X\);
- \(X\) is finite, infinite, countable, or uncountable;
- \(A=B\) or \(A\subseteq B\);
- \(\kappa<\lambda\) or \(\kappa\leq\lambda\);
- \(\kappa\) is finite, infinite, countable, or uncountable.

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

## Mathematical acceptance conditions

The implementation satisfies this specification only when these facts hold:

- every admitted set arrow is a total single-valued function with its stated domain and
  codomain;
- identity and composition satisfy the category laws;
- function equality is extensional;
- `X.Hom(Y)`, `ExponentialOfSets(Y, X)`, and `Y ** X` construct the same function set
  \(Y^X\);
- every chosen subset retains its inclusion, and every abstract subobject has its image
  subset as canonical representative;
- the power set is canonically \(\operatorname{Hom}_{\mathbf{Set}}(X,\mathbf 2)\) and
  carries its complete Boolean-algebra structure;
- products retain their projections and unique mediating maps;
- coproducts retain their injections and unique mediating maps;
- every small limit is the set of compatible families with its limiting cone;
- every small colimit is the stated quotient of a disjoint union with its colimiting
  cocone;
- exponentials satisfy evaluation and currying;
- `Unknown` never changes a mathematical truth value or establishes a category
  refinement;
- countability does not supply an enumeration;
- a chosen enumeration is a bijection with its stated index set;
- private representations never become another mathematical owner or public result.

The governing policies include `POL-MATH-001` through `POL-MATH-033`,
`POL-CAT-020`, `POL-CAT-027` through `POL-CAT-032`, `POL-CAT-040` through
`POL-CAT-045`, `POL-SET-001` through `POL-SET-034`, and `POL-KERNEL-001` through
`POL-KERNEL-024`.
