# Posets and totally ordered sets

This specification uses the ordinary mathematics of binary relations, partial orders,
total orders, and monotone maps. The mathematical definitions determine the category
graph, implementation roles, construction obligations, and inherited operations.

## Contents

- [Mathematical foundation](#mathematical-foundation)
- [Categories and structural functors](#categories-and-structural-functors)
- [Construction and admission](#construction-and-admission)
- [Total-order refinement](#total-order-refinement)
- [Canonical simplex orders](#canonical-simplex-orders)
- [Monotone maps](#monotone-maps)
- [Products](#products)
- [Finite-poset mathematics](#finite-poset-mathematics)
- [Thin categories](#thin-categories)
- [Implementation ownership](#implementation-ownership)
- [Acceptance conditions](#acceptance-conditions)

## Mathematical foundation

*Definition.* A binary relation on a set \(X\) is a subset

\[
R\subseteq X\times X.
\]

Equivalently, it is a subobject \(R\hookrightarrow X\times X\) in
\(\mathbf{Set}\). Write \(x\leq_R y\) when \((x,y)\in R\).

*Definition.* A partially ordered set is a pair \(P=(X,\leq_P)\) such that

\[
\begin{aligned}
&\forall x\in X, &&x\leq_P x,\\
&\forall x,y\in X, &&x\leq_P y\land y\leq_P x\Longrightarrow x=y,\\
&\forall x,y,z\in X, &&x\leq_P y\land y\leq_P z\Longrightarrow x\leq_P z.
\end{aligned}
\]

These are reflexivity, antisymmetry, and transitivity. They are defining laws, not
optional properties supplied by an implementation.

The relations \(\leq_P\) and \(<_P\) have domain \(X\times X\). Thus comparison takes
two elements of the same ambient poset. Elements of different posets require a stated
map or coercion before comparison. The mathematical signature already determines both
argument roles.

*Definition.* A total order is a partial order \(P=(X,\leq_P)\) satisfying

\[
\forall x,y\in X,\qquad x\leq_P y\lor y\leq_P x.
\]

Totality adds one proposition. It does not add another underlying set, relation,
element notion, or comparison operation.

*Definition.* For posets \(P=(X,\leq_P)\) and \(Q=(Y,\leq_Q)\), a monotone map
\(f:P\to Q\) is a function \(f:X\to Y\) satisfying

\[
\forall x,y\in X,\qquad
x\leq_P y\Longrightarrow f(x)\leq_Q f(y).
\]

Identity functions are monotone. Composites of monotone functions are monotone.
Therefore posets and monotone maps form the category \(\mathbf{Pos}\).

The forgetful functor

\[
U:\mathbf{Pos}\longrightarrow\mathbf{Set}
\]

sends \((X,\leq_P)\) to \(X\) and a monotone map to its underlying function. It is
faithful. It is not full because an arbitrary function between underlying sets need not
preserve order.

## Categories and structural functors

The owned category constructors are:

```sage
PartiallyOrderedSets()
TotallyOrderedSets()
FinitePosets()
FiniteTotallyOrderedSets()
```

Their inclusions and forgetful functors form the commutative diagram

\[
\begin{array}{ccc}
\mathbf{FinTotOrd} & \hookrightarrow & \mathbf{TotOrd} \\
\downarrow & & \downarrow \\
\mathbf{FinPos} & \hookrightarrow & \mathbf{Pos} \\
\downarrow & & \downarrow \\
\mathbf{FinSet} & \hookrightarrow & \mathbf{Set}.
\end{array}
\]

Each horizontal or upper vertical inclusion is a full property-subcategory inclusion.
The lower vertical maps forget order. Both routes from
\(\mathbf{FinTotOrd}\) to \(\mathbf{Set}\) produce the same underlying set and the same
underlying functions.

Order and cardinality are independent properties. Finiteness does not establish
totality. Totality does not supply an enumeration, rank function, or well-order.

The category-owned implementation roles follow directly:

- a poset object implements \((X,\leq_P)\);
- a poset element implements an element \(x\in X\) with ambient object \(P\);
- a poset arrow implements a monotone set map;
- a total-order object is a poset object whose relation satisfies totality.

No role requires a decorator, marker, authority object, or parallel metadata record.

## Construction and admission

An owned relation is a subobject of \(X\times X\). A private callable can evaluate that
relation, but the callable is not the mathematical relation or its proof obligations.

There are three construction routes.

### Checked construction

The checked route evaluates reflexivity, antisymmetry, and transitivity with an exact
decision procedure. It admits the pair \((X,\leq)\) only when all three decisions are
`True`.

For a represented finite set, exhaustive evaluation of all required elements, pairs,
and triples is one exact algorithm. `False` rejects the relation. `Unknown` establishes
no poset.

Finiteness is not the definition of this route. Any exact algorithm that decides all
three laws can supply checked admission.

### Hypothesis-backed construction

The hypothesis-backed route receives an explicit scoped assumption context containing
the three applied predicates for the owned relation. It constructs the poset under those
hypotheses. The context is semantic hypothesis data; it is not theorem prose or an
authority token.

### Theorem-backed named construction

A named construction whose defining theorem supplies the three laws constructs its
result directly in `PartiallyOrderedSets()`. Examples include:

- the equality relation on any set;
- the usual order on a natural interval;
- the usual order on `NN`;
- an ordinal order;
- the componentwise order on a product of posets.

The construction owns this conclusion through its definition and return category. It
does not pass proof text, a Boolean flag, or an authority object.

This distinction matters for scale. Let

\[
X=\{1,\ldots,10^{10}\}
\]

with its usual order. The natural-interval constructor establishes the order laws by
the standard theorem. It does not enumerate pairs or triples.

## Total-order refinement

Totality is the proposition

\[
\operatorname{Total}(P)
\;:\Longleftrightarrow\;
\forall x,y\in P,\quad x\leq_P y\lor y\leq_P x.
\]

The same three admission forms apply:

- a checked route requires an exact `True` result;
- a hypothesis-backed route requires the applied totality hypothesis;
- a theorem-backed named construction returns the object directly in
  `TotallyOrderedSets()`.

An exact `False` or `Unknown` checked result does not refine the poset. The object
remains in the strongest category already established.

The equality order on a set with two distinct elements is a poset but not a total
order. Finiteness supplies no missing comparability.

`FiniteTotallyOrderedSets()` accepts an established finite total order. Its two
structural routes preserve the same poset and set images.

## Canonical simplex orders

For \(n\in\mathbb Z_{\geq0}\), define

\[
[n]=\{0,1,\ldots,n\}
\]

with the usual order. It has order type \(n+1\) and cardinality \(n+1\). The constructor
is:

```sage
SimplexOrders()[n]
```

The countably infinite simplex order has underlying set \(\mathbb Z_{\geq0}\) and order
type \(\omega\):

```sage
SimplexOrders()[Aleph0]
```

This object has cardinality \(\aleph_0\). It is not named `NN` because this repository
uses `NN` for the positive integers.

## Monotone maps

A candidate poset morphism starts as an owned set morphism \(f:U(P)\to U(Q)\). A bare
Python callable is only a private representation of such a rule.

The checked route decides

\[
\forall x,y\in P,\qquad
x\leq_P y\Longrightarrow f(x)\leq_Q f(y).
\]

For a represented finite source, exhaustive evaluation of all ordered pairs is one
exact algorithm. A witnessed violation gives `False`. An unresolved implication gives
`Unknown`. Only `True` admits the arrow to the poset Hom object.

A hypothesis-backed route accepts a scoped `order_preserving(f)` hypothesis. A named
theorem-backed route constructs a monotone arrow directly. The standard theorem-backed
routes include:

- identity arrows;
- composites of monotone arrows;
- product projections;
- product mediating arrows;
- the map \(n\mapsto n^2\) from `NN` to `NN` with the usual order.

The last map is admitted by its elementary monotonicity theorem. It is not checked by
enumerating `NN`.

If monotonicity is `False` or `Unknown` and no hypothesis or construction theorem
applies, the candidate remains a set morphism. It does not enter the poset Hom object.

Order-reflecting maps, order embeddings, and order isomorphisms are arrow property
subcategories:

\[
\begin{aligned}
f\text{ reflects order}
&\Longleftrightarrow
\forall x,y,\ f(x)\leq_Q f(y)\Longrightarrow x\leq_P y,\\
f\text{ is an order embedding}
&\Longleftrightarrow
f\text{ is monotone and order-reflecting},\\
f\text{ is an order isomorphism}
&\Longleftrightarrow
f\text{ is a bijective order embedding}.
\end{aligned}
\]

Category membership states these properties. Poset arrows do not fabricate Boolean
answers for unestablished properties.

## Products

For a family of posets \(P_i=(X_i,\leq_i)\) indexed by a set \(I\), define

\[
\prod_{i\in I}P_i
=\left(\prod_{i\in I}X_i,\leq\right),
\qquad
x\leq y\Longleftrightarrow\forall i\in I,\ x_i\leq_i y_i.
\]

Reflexivity, antisymmetry, and transitivity follow coordinatewise. The set projections

\[
\pi_i:\prod_jX_j\longrightarrow X_i
\]

are monotone. For every poset \(C\) and family of monotone maps \(f_i:C\to P_i\), the
set-product mediating map

\[
\langle f_i\rangle:C\longrightarrow\prod_iP_i
\]

is monotone and is the unique arrow satisfying

\[
\pi_i\circ\langle f_j\rangle=f_i
\]

for every \(i\in I\). Thus this is the categorical product in \(\mathbf{Pos}\), and the
forgetful functor creates it:

\[
U\!\left(\prod_iP_i\right)=\prod_iU(P_i).
\]

The componentwise product of total orders need not be total. If \(P\) and \(Q\) each
contain \(0<1\), then \((0,1)\) and \((1,0)\) are incomparable in \(P\times Q\).
Therefore the poset product does not refine to `TotallyOrderedSets()` in this case.

The product constructor uses the coordinatewise theorem. It does not validate the order
or projection maps by exhaustive enumeration.

## Finite-poset mathematics

Let \(P=(X,\leq)\) be a finite poset.

For \(x,y\in X\), write \(x<y\) when \(x\leq y\) and \(x\neq y\). The element \(y\)
*covers* \(x\) when

\[
x<y
\quad\text{and}\quad
\nexists z\in X,\ x<z<y.
\]

The lower covers of \(y\) are the elements covered by \(y\). The upper covers of
\(x\) are the elements that cover \(x\). Common lower or upper covers are intersections
of these cover sets over the stated finite subset.

For \(x\leq y\), the open and closed intervals are

\[
(x,y)=\{z\in X\mid x<z<y\},
\qquad
[x,y]=\{z\in X\mid x\leq z\leq y\}.
\]

For a subset \(A\subseteq X\), its generated order ideal and order filter are

\[
\downarrow A=\{x\in X\mid \exists a\in A,\ x\leq a\},
\qquad
\uparrow A=\{x\in X\mid \exists a\in A,\ a\leq x\}.
\]

The principal cases are \(\downarrow x=\downarrow\{x\}\) and
\(\uparrow x=\uparrow\{x\}\). An order ideal is a subset \(I\subseteq X\) satisfying
\(\downarrow I=I\). An order filter satisfies \(\uparrow I=I\).

An element \(m\in X\) is minimal when no \(x<m\) exists. It is maximal when no
\(x>m\) exists. A bottom element \(\bot\) satisfies \(\bot\leq x\) for every \(x\in X\).
A top element \(\top\) satisfies \(x\leq\top\) for every \(x\in X\). Bottom and top,
when they exist, are unique.

The operations `bottom()` and `top()` therefore belong to the property subcategories of
posets with bottom and with top. They are not partial methods on every finite poset. The
subcategory of bounded posets is their intersection.

A chain is a subset whose induced order is total. An antichain is a subset whose
distinct elements are pairwise incomparable. The height and width are

\[
\operatorname{height}(P)=\max\{|C|\mid C\subseteq X\text{ is a chain}\},
\]

\[
\operatorname{width}(P)=\max\{|A|\mid A\subseteq X\text{ is an antichain}\}.
\]

Both are cardinal values. The empty subset is a chain and an antichain, so the empty
poset has height and width \(0\). This convention counts elements, so a one-element
poset has height \(1\).

A rank function is a map

\[
\rho:X\to\mathbb Z_{\geq0}
\]

such that every minimal element has rank \(0\), and \(\rho(y)=\rho(x)+1\) whenever
\(y\) covers \(x\). A finite poset is ranked when such a function exists. Its level
sets are \(\rho^{-1}(k)\). For a nonempty ranked poset, its rank is
\(\max_{x\in X}\rho(x)\).

A finite ranked poset is graded when all maximal elements have the same rank. Element
rank and level sets belong to the ranked-poset property subcategory. The poset rank
belongs to its nonempty part. None is a total operation on an arbitrary finite poset.

A linear extension of \(P\) is a total order \(L\) on the same set \(X\) satisfying

\[
x\leq_P y\Longrightarrow x\leq_L y.
\]

Every finite poset has a linear extension. A chosen linear-extension constructor returns
a finite total-order object with the same underlying set. The theorem supplies totality
and order preservation; the constructor does not recheck them exhaustively.

Cover sets, intervals, ideals, filters, extrema, chains, antichains, and level sets are
owned finite subobjects of \(X\), not Python iterators or built-in containers.

## Thin categories

Every poset \(P\) determines a thin category \(\mathcal T(P)\). Its objects are the
elements of \(P\), and

\[
\operatorname{Hom}_{\mathcal T(P)}(x,y)=
\begin{cases}
\{*\},&x\leq_P y,\\
\varnothing,&x\nleq_P y.
\end{cases}
\]

Reflexivity supplies identities. Transitivity supplies composition. Antisymmetry makes
the thin category skeletal. A monotone map \(P\to Q\) induces a functor
\(\mathcal T(P)\to\mathcal T(Q)\).

Hence posets are the same mathematical data as skeletal thin categories, up to the
usual equivalence between a poset and its thin category.

## Implementation ownership

`PartiallyOrderedSets()` introduces the relation, order-specific object operations,
order-specific element operations, monotone arrows, and constructions such as the thin
category and componentwise products.

Its selected forgetful functor to `Sets()` supplies elements, membership, iteration,
cardinality, set maps, and set universal constructions. Poset theory does not reimplement
that surface.

`TotallyOrderedSets()` introduces totality and the named construction routes whose
theorems establish it. It does not implement another comparison method, element cache,
set wrapper, or poset constructor.

`FinitePosets()` introduces only mathematics that requires finiteness, including exact
finite-poset algorithms and finite mathematical result collections. It inherits the
poset and finite-set surfaces through its two inclusions.

The ordinary method signatures on the category-owned implementation types determine
receivers, arguments, results, and mathematical roles. The kernel alone compiles
inherited methods and transports canonical images. See [Leaf category
implementations](leaves.md) and [Structural resolution](resolution.md).

The governing policies include `POL-MATH-001`, `POL-MATH-016` through `POL-MATH-033`,
`POL-CAT-020`, `POL-CAT-061` through `POL-CAT-078`, `POL-LEAF-018` through
`POL-LEAF-055`, and `POL-KERNEL-001` through `POL-KERNEL-024`.

## Acceptance conditions

The implementation satisfies this specification only when these mathematical facts hold:

- every admitted poset relation satisfies reflexivity, antisymmetry, and transitivity;
- every admitted total order also satisfies pairwise comparability;
- every admitted poset arrow is monotone;
- checked `False` and `Unknown` results cause no property refinement;
- named theorem-backed constructors admit large finite and infinite examples without
  exhaustive verification;
- the two-element equality order remains a poset and does not become a total order;
- the reversing function on the two-element chain remains a set map and does not become
  a poset morphism;
- identities, composites, product projections, product mediating maps, and
  \(n\mapsto n^2\) on `NN` enter through their defining theorems;
- the underlying set of a poset product is the chosen set product;
- product projections and mediating arrows satisfy the universal equations;
- crossed elements in the product of two nontrivial chains are incomparable;
- height counts elements in a largest chain, and width counts elements in a largest
  antichain;
- `bottom()` and `top()` occur only on their property subcategories;
- element rank and level sets occur only on ranked finite posets, and poset rank also
  requires nonemptiness;
- every chosen linear extension uses the same underlying set and extends the original
  partial order;
- finite-poset collection results are owned finite subobjects or indexed families;
- every inherited set operation works on posets through the selected forgetful functor;
- every returned element has the original structured ambient object;
- total-order classes contain no second comparison implementation or element cache;
- leaf method declarations contain no compiler decorators, transport roles, signature
  mirrors, or authority values.
