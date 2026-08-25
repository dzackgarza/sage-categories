# Posets and totally ordered sets

This specification defines the public order algorithms and their result categories.
Standard order theory and category theory are assumed.

Order operations specified as predicates follow the proposition interface in
[Property refinement](property-refinement.md). Applying one returns a proposition.
`ask()` returns its decision. Tables mark any total exact operation that returns a
decision directly.

## Category and role surface

The owned category constructors are:

```sage
PartiallyOrderedSets()
TotallyOrderedSets()
FinitePosets()
FiniteTotallyOrderedSets()
```

The structural functors form this commutative graph:

\[
\begin{array}{ccc}
\mathbf{FinTotOrd} & \hookrightarrow & \mathbf{TotOrd} \\
\downarrow & & \downarrow \\
\mathbf{FinPos} & \hookrightarrow & \mathbf{Pos} \\
\downarrow & & \downarrow \\
\mathbf{FinSet} & \hookrightarrow & \mathbf{Set}.
\end{array}
\]

Both routes from finite total orders to sets produce one canonical set image.

Each category owns complete implementation roles:

- `ObjectType` implements its objects.
- `ElementType` implements owned elements.
- `ArrowType` implements owned arrows.

`PartiallyOrderedSets()` introduces the order relation, comparison, and monotone arrows.
`TotallyOrderedSets()` adds only established totality. The finite categories add only
algorithms and constructions that require finiteness.

The relation presentation's `product_projection(0)` supplies membership, iteration,
cardinality, set maps, and set constructions.

## Poset construction and its proposition

A relation input is an owned subobject of `X × X`. A callable can be its private
evaluator. The callable is not the public relation.

The inclusion of the relation subobject into `X * X` determines `X`. Its
partial-order proposition is the conjunction of:

\[
x\leq x,
\qquad
x\leq y\land y\leq x\Rightarrow x=y,
\qquad
x\leq y\land y\leq z\Rightarrow x\leq z.
\]

The owned method returns this proposition without deciding it. `ask()` can use an
exhaustive finite algorithm or another exact handler. Exact `True` invokes the trusted
`PartiallyOrderedSets()` constructor. `False` disproves admission. `Unknown` leaves the
relation in its ambient category.

Selecting the property-category constructor directly asserts the laws:

```python
PartiallyOrderedSets()(relation)
```

An interactive user can instead call `assume(relation.is_partial_order())`. A named
mathematical construction returns through the same property-category constructor.
There are no checked, hypothesis-backed, or theorem-backed constructor families.

Named constructors include:

```python
PartiallyOrderedSets().discrete_order(X)
```

Ordinal orders, natural intervals, and componentwise product orders also use named
theorem-backed routes. They do not repeat exhaustive checks.

For example, the usual order on `{1, ..., 10^10}` must use its construction theorem.
Its constructor must not enumerate all pairs or triples.

An infinite relation can enter `PartiallyOrderedSets()` through its trusted constructor,
an active assumption, exact positive evaluation, or a named mathematical construction.

## Total-order refinement

The method `P.is_total()` returns the proposition:

\[
\forall x,y,\qquad x\leq y\lor y\leq x.
\]

`ask(P.is_total())` returns the decision. Exact `True` invokes the trusted total-order
constructor. An active assumption and a named mathematical construction invoke the same
constructor without exhaustive checking. `False` and `Unknown` keep the object in its
previously established category.

Finite totality can use exhaustive pair checks. Finiteness itself supplies no evidence
of totality.

The equality order on two distinct elements remains a poset. It does not enter either
total-order category.

`FiniteTotallyOrderedSets()` accepts an established finite total order. It uses the same
poset elements, comparisons, and set images as the two structural routes above.

## Canonical simplex orders

The owned constructors are:

```sage
SimplexOrders()[n]
SimplexOrders()[Aleph0]
```

`SimplexOrders()[n]` returns the usual total order on `{0, ..., n}`.
`SimplexOrders()[Aleph0]` returns the usual order on the nonnegative integers.

Both constructors use their order theorem. They return directly in the strongest
established total-order category.

## Poset morphism admission

A candidate poset morphism starts as an owned set arrow between the underlying sets.
A bare callable can only be the private rule of that set arrow.

The owned method `f.is_order_preserving()` returns the proposition:

\[
x\leq_P y\Rightarrow f(x)\leq_Q f(y).
\]

For a represented finite source, exhaustive pair checking is one exact handler for
`ask(f.is_order_preserving())`. A witnessed violation makes `ask()` return `False`. An
unresolved evaluation makes it return `Unknown`. Exact `True` invokes the poset Hom
constructor. Direct property construction, an active assumption, and a named
mathematical construction use that same constructor.

Named theorem-backed routes include identities, composites, product projections, and
product mediating arrows.

The map `n -> n^2` from `NN` to `NN` uses a named theorem-backed constructor. It does
not enumerate `NN`.

A reversing map on the two-element chain fails checked admission. Its underlying set
arrow remains valid.

An admitted poset arrow supplies:

```python
f.is_order_preserving()
f.is_order_reflecting()
f.is_order_embedding()
f.is_order_isomorphism()
```

Every call returns an applied proposition. Hom admission makes
`ask(f.is_order_preserving())` return `True`. The other propositions remain available
for assumption or exact evaluation.

Identity and composition arrive through inherited arrow operations. Poset theory adds
only the theorem-backed admission needed to preserve monotonicity.

## Products

The poset product constructor starts from the chosen set-product presentation. It keeps
that set apex and installs the componentwise order:

\[
x\leq y\quad\Longleftrightarrow\quad
\forall i,\ x_i\leq_i y_i.
\]

The result retains:

- the original diagram;
- the chosen set-product apex;
- monotone projections;
- the universal monotone map;
- the underlying set cone.

The coordinatewise theorem admits the order and all product arrows. The constructor
does not enumerate the product.

The set-projection square to the chosen set product commutes. Product elements remain
owned by the product poset and pass set membership through that projection.

The product of total orders need not be total. In a product of two nontrivial chains,
the two crossed elements are incomparable. Such a product remains a poset.

## Finite-poset API

Finite-poset algorithms use owned poset elements and owned finite subobjects. They do
not expose backend elements, Python iterators, or built-in containers.

| Operation | Public result |
| --- | --- |
| `covers(lower, upper)` | Exact decision for the cover relation. |
| `lower_covers(x)` | Finite subobject of the ambient poset. |
| `upper_covers(x)` | Finite subobject of the ambient poset. |
| `common_lower_covers(A)` | Finite subobject for an owned finite subobject `A`. |
| `common_upper_covers(A)` | Finite subobject for an owned finite subobject `A`. |
| `open_interval(x, y)` | Finite subobject of the ambient poset. |
| `closed_interval(x, y)` | Finite subobject of the ambient poset. |
| `principal_order_ideal(x)` | Finite subobject of the ambient poset. |
| `principal_order_filter(x)` | Finite subobject of the ambient poset. |
| `order_ideal(A)` | Finite subobject generated by an owned finite subobject `A`. |
| `order_filter(A)` | Finite subobject generated by an owned finite subobject `A`. |
| `minimal_elements()` | Finite subobject of the ambient poset. |
| `maximal_elements()` | Finite subobject of the ambient poset. |
| `height()` | Cardinality of a largest chain. |
| `width()` | Cardinality of a largest antichain. |
| `is_chain()` | Exact decision for the whole poset. |
| `is_chain_of_poset(A)` | Exact decision for an owned finite subobject `A`. |
| `is_antichain_of_poset(A)` | Exact decision for an owned finite subobject `A`. |
| `linear_extension()` | Finite total order on the same underlying set. |

Height counts elements. The empty poset has height and width zero.

Bottom and top are operations of the matching property subcategories. They are not
partial methods on every finite poset.

Ranked finite posets add:

| Operation | Public result |
| --- | --- |
| `rank_of_element(x)` | Owned natural cardinal. |
| `level_sets()` | Discrete indexed family of finite subobjects. |
| `rank()` | Owned natural cardinal for a nonempty ranked poset. |

Graded finite posets refine ranked finite posets. `is_ranked()` and `is_graded()` are
property decisions on the appropriate candidate category.

`linear_extension()` uses the finite linear-extension algorithm. It reconstructs a
finite total-order object on the same set. The returned order extends the source order.

Backend algorithms can use Sage finite-poset objects privately. Each public method
lowers semantic inputs and reconstructs the owned result before return.

## Thin category

Every poset supplies:

```python
P.thin_category()
```

The result is an owned category. Its objects are the owned elements of `P`. Its Hom
category is terminal when `x <= y` and empty otherwise.

A monotone arrow induces the corresponding functor between thin categories.

## Inherited surface and implementation ownership

`PartiallyOrderedSets()` owns order comparison and monotone-map admission.
`TotallyOrderedSets()` owns only totality-specific constructors and queries.
`FinitePosets()` owns only finite-poset algorithms and their semantic reconstruction.

Set membership, iteration, cardinality, identity, composition, and universal set
constructions arrive through structural inheritance.

Each category-owned `ObjectType`, `ElementType`, and `ArrowType` is its implementation
class. A leaf can use Sage or another engine through private helpers.

Leaf methods remain ordinary typed mathematical methods. The compiler derives transport
from those signatures and category declarations. Leaf code does not declare compiler
roles or route metadata.

See [Leaf category implementations](leaves.md) and [Structural resolution](resolution.md).

The governing policies include `POL-MATH-001`, `POL-MATH-016` through `POL-MATH-035`,
`POL-CAT-020`, `POL-CAT-061` through `POL-CAT-084`, `POL-LEAF-018` through
`POL-LEAF-057`, and `POL-KERNEL-001` through `POL-KERNEL-026`.

## Acceptance conditions

The implementation satisfies this specification when the public API establishes these
facts:

- invalid relations make their partial-order proposition evaluate to `False`;
- `Unknown` is returned only by `ask()` and never establishes partial order, totality,
  or monotonicity;
- theorem-backed constructors handle large finite and infinite objects without
  exhaustive checks;
- the two-element equality order remains outside total-order categories;
- total-order elements use inherited poset comparison;
- all inherited set operations work through every structural route;
- iteration returns elements owned by the public ambient poset;
- nonmonotone set arrows fail poset Hom admission;
- theorem-backed identities, composites, projections, and standard infinite maps enter
  the poset Hom category;
- poset products retain the chosen set-product apex and universal arrows;
- crossed product elements remain incomparable;
- finite-poset collection algorithms return owned finite subobjects;
- level sets return an owned indexed family;
- linear extensions return finite total orders on the same underlying set;
- no total-order class repeats poset comparisons, set operations, or element caches;
- no leaf method contains compiler routing metadata.
