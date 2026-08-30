# Posets and totally ordered sets

This specification defines the public order algorithms and their result categories.
Standard order theory and category theory are assumed.

Order operations specified as predicates follow the proposition interface in [Property refinement](property-refinement.md).
Applying one returns a proposition.
`ask()` returns its decision.
Tables mark any total exact operation that returns a decision directly.

## Category and public surface

The owned category constructors are:

```sage
PartiallyOrderedSets()
TotallyOrderedSets()
FinitePosets()
FiniteTotallyOrderedSets()
```

The structure functors form this commutative graph:

\[
\begin{array}{ccc}
\mathbf{FinTotOrd} & \hookrightarrow & \mathbf{TotOrd} \\
\downarrow & & \downarrow \\
\mathbf{FinPos} & \hookrightarrow & \mathbf{Pos} \\
\downarrow & & \downarrow \\
\mathbf{FinSet} & \hookrightarrow & \mathbf{Set}.
\end{array}
\]

Both paths from finite total orders to sets have the same intended underlying-set
projection. This is coherence of the owned mathematical diamond, not a requirement for
the compiler to compare constructor data or public functor images along the two paths.

Let `U: PartiallyOrderedSets() -> Sets()` be the named projection `(X, R) |-> X`.
Then

\[
\mathbf{FinPos}
=
\mathbf{Pos}\times_{\mathbf{Set}}\mathbf{FinSet}
=
U^{-1}(\mathbf{FinSet}).
\]

Thus `FinitePosets()` is `U.inverse_image(Sets().Finite())` and retains this pullback square.
The corresponding projection from total orders gives

\[
\mathbf{FinTotOrd}
=
\mathbf{TotOrd}\times_{\mathbf{Set}}\mathbf{FinSet}
=
\mathbf{TotOrd}\times_{\mathbf{Pos}}\mathbf{FinPos}.
\]

These are instances of the inverse-image subcategory construction in [Functors and structural inheritance](functor.md#inverse-image-subcategories).

Each category owns complete implementation classes:

- `ObjectType` implements its objects.

- `ElementType` implements owned elements.

- `MorphismType` implements owned morphisms.

`PartiallyOrderedSets()` introduces the order relation, comparison, and monotone morphisms.
`TotallyOrderedSets()` adds only established totality.
The finite categories add only algorithms and constructions that require finiteness.

The relation presentation's `product_projection(0)` supplies membership, iteration, cardinality, set maps, and set constructions.

## Poset construction and its proposition

A relation input is an owned subobject of `X × X`. A callable can be its private evaluator.
The callable is not the public relation.

The monomorphism of the relation subobject into `X * X` determines `X`. Its partial-order proposition is the conjunction of:

\[
x\leq x,
\qquad
x\leq y\land y\leq x\Rightarrow x=y,
\qquad
x\leq y\land y\leq z\Rightarrow x\leq z.
\]

The registered `PartiallyOrderedSets()` implementation inherits `PredicateSubcategory` and
implements this proposition as its private `_predicate()` method. The axiom declaration makes
the subcategory available and generates `is_partial_order()` on the ambient relation class.
`ask()` can use an exhaustive finite algorithm or another exact handler.
Exact `True` refines the relation into `PartiallyOrderedSets()`.
`False` disproves admission.
`Unknown` leaves the relation in its ambient category.

Selecting the property-category constructor directly asserts the laws:

```python
PartiallyOrderedSets()(relation)
```

Its standard property application can be passed to `assume()`. A named mathematical construction returns its result already placed in the property category.
There are no checked, hypothesis-backed, or theorem-backed constructor families.

Named constructors include:

```python
PartiallyOrderedSets().discrete_order(X)
```

Ordinal orders, natural intervals, and componentwise product orders also use named theorem-backed routes.
They do not repeat exhaustive checks.

For example, the usual order on `{1, ..., 10^10}` must use its construction theorem.
Its constructor must not enumerate all pairs or triples.

An infinite relation can enter `PartiallyOrderedSets()` through direct construction, an active assumption, exact positive evaluation, or a named mathematical construction.

## Total-order refinement

The containment predicate of `TotallyOrderedSets()` is the proposition:

\[
\forall x,y,\qquad x\leq y\lor y\leq x.
\]

The registered `TotallyOrderedSets()` implementation inherits `PredicateSubcategory` and
implements this proposition as its private `_predicate()` method. The axiom generates
`is_total()` on `PartiallyOrderedSets().ObjectType`. The application returns this proposition,
and `ask()` returns its decision.
Exact `True` refines the object into `TotallyOrderedSets()`.
An active assumption and a named mathematical construction establish the same placement without exhaustive checking.
`False` and `Unknown` keep the object in its previously established category.

Finite totality can use exhaustive pair checks.
Finiteness itself supplies no evidence of totality.

The equality order on two distinct elements remains a poset.
It does not enter either total-order category.

`FiniteTotallyOrderedSets()` accepts an established finite total order.
It uses the same poset elements, comparisons, and named set images as the two structure-functor branches above.
Its two displayed pullback presentations retain the same named projection to sets.

## Canonical simplex orders

The owned constructors are:

```sage
SimplexOrders()[n]
```

`SimplexOrders()[n]` returns the usual total order on `{0, ..., n}`.
The index `n` is finite. The infinite ordinal is `omega0`, constructed by the ordinal API.

The constructor uses its order theorem and returns directly in the strongest established total-order category.

## Poset morphism admission

A candidate poset morphism starts as an owned set morphism between the underlying sets.
A bare callable can only be the private rule of that set morphism.

The containment predicate for the fixed-endpoint poset-morphism category is the proposition:

\[
x\leq_P y\Rightarrow f(x)\leq_Q f(y).
\]

For a represented finite source, exhaustive pair checking is one exact handler for `ask()`. A witnessed violation makes `ask()` return `False`. An unresolved evaluation makes it return `Unknown`. Exact `True` refines the morphism into `Mor(PartiallyOrderedSets())(P, Q)`. Direct property construction, an active assumption, and a named mathematical construction establish the same placement.

Named theorem-backed routes include identities, composites, product projections, and product mediating morphisms.

The map `n -> n^2` from `NN` to `NN` uses a named theorem-backed constructor.
It does not enumerate `NN`.

A reversing map on the two-element chain fails checked admission.
Its underlying set morphism remains valid.

Order preservation, order reflection, order embedding, and order isomorphism use their morphism-property subcategories.
Each predicate-backed implementation inherits `PredicateSubcategory` and implements its
private `_predicate()` method. Their axioms generate `is_order_preserving()`,
`is_order_reflecting()`, `is_order_embedding()`, and `is_order_isomorphism()` on the
ambient set-map class. The kernel derives each standard property application.
Admission makes the preservation proposition evaluate to `True`.
The other propositions remain available for assumption or exact evaluation.

Identity and composition arrive through inherited morphism operations.
Poset theory adds only the theorem-backed admission needed to preserve monotonicity.

## Products

The generic product contract is specified in [Products, coproducts, and component functors](functor.md#products-coproducts-and-component-functors).
The projection `U: PartiallyOrderedSets() -> Sets()` creates small limits. It is therefore an object of each applicable `Fun(PartiallyOrderedSets(), Sets()).CreatesLimits(I)`.

For a discrete shape, the generic creates-limits construction lifts the selected set-product cone. Its apex carries the componentwise order:

\[
x\leq y\quad\Longleftrightarrow\quad
\forall i,\ x_i\leq_i y_i.
\]

The poset leaf states this coordinatewise theorem once as the creates-limits property of `U`. The generic lift supplies the monotone projections and universal morphism. Applying `U` to the lifted cone returns the selected set-product cone.

The product of total orders need not be total.
In a product of two nontrivial chains, the two crossed elements are incomparable.
Such a product remains a poset.

## Finite-poset API

`PartiallyOrderedSets().Subobjects(P).from_predicate(predicate)` constructs the induced subposet, its restricted order, and its monomorphism into `P`.
Finite-poset algorithms use owned poset elements and owned finite subobjects.
They do not expose backend elements, Python iterators, or built-in containers.
They expose these primitive operations:

| Operation | Public result |
| --- | --- |
| `covers(lower, upper)` | Applied proposition for the cover relation. |
| `height()` | Cardinality of a largest chain. |
| `width()` | Cardinality of a largest antichain. |
| `linear_extension()` | Finite total order on the same underlying set. |

Derived finite subobjects use `from_predicate()` at the call site.

| Selected subobject | Defining predicate on `z` |
| --- | --- |
| Lower covers of `x` | `covers(z, x)` |
| Upper covers of `x` | `covers(x, z)` |
| Open interval from `x` to `y` | Proposition conjunction of `x < z` and `z < y` |
| Closed interval from `x` to `y` | Proposition conjunction of `x <= z` and `z <= y` |
| Principal order ideal of `x` | `z <= x` |
| Principal order filter of `x` | `x <= z` |

Finite conjunctions over an owned subobject give common covers.
Finite existential predicates give the order ideal or filter generated by that subobject.
Minimal and maximal elements use the corresponding strict-order predicates.

Chainhood is totality of the induced subposet.
Antichainhood is equality of its induced order with its discrete order.
Both use the existing property and equality predicates.

Height counts elements.
The empty poset has height and width zero.

Bottom and top are operations of the matching property subcategories.
They are not partial methods on every finite poset.

Ranked finite posets add:

| Operation | Public result |
| --- | --- |
| `rank_of_element(x)` | Owned natural cardinal. |

Each level set is the predicate subobject selected by `rank_of_element(x) == r`.
The rank of a nonempty finite ranked poset is the maximum element rank.
Ranked and graded finite posets are property subcategories with their owned containment predicates.

`linear_extension()` uses the finite linear-extension algorithm.
It reconstructs a finite total-order object on the same set.
The returned order extends the source order.

Backend algorithms can use Sage finite-poset objects privately.
Each public method lowers semantic inputs and reconstructs the owned result before return.

## Thin category

The named functor `Thin: PartiallyOrderedSets() -> Cat()` constructs the thin category of a poset.
Apply it as `Thin.on_object(P)`.
The result is an owned category.
Its objects are the owned elements of `P`. Its fixed-endpoint category `Mor(-)(x, y)` is terminal when `x <= y` and empty otherwise.

A monotone morphism induces the corresponding functor between thin categories.

## Inherited surface and implementation ownership

`PartiallyOrderedSets()` owns order comparison and monotone-map admission.
`TotallyOrderedSets()` owns only totality-specific constructors and queries.
`FinitePosets()` owns only finite-poset algorithms and their semantic reconstruction.

Set membership, iteration, cardinality, identity, composition, and universal set constructions arrive through structural inheritance.

Each category-owned `ObjectType`, `ElementType`, and `MorphismType` is its implementation class.
A leaf can use Sage or another engine through private helpers.

Leaf methods remain ordinary typed mathematical methods.
Their signatures state only the methods' ordinary Python and mathematical types. Selected
structure functors determine the inherited implementation classes; a method signature does
not encode a functor action or an initializer-state transport.
Leaf code declares only its mathematical classes and structure functors.

See [Leaf category implementations](leaves.md) and [Structural resolution](resolution.md).

The governing policies include `POL-MATH-001`, `POL-MATH-016` through `POL-MATH-035`, `POL-CAT-020`, `POL-CAT-061` through `POL-CAT-100`, `POL-LEAF-018` through `POL-LEAF-057`, and `POL-KERNEL-001` through `POL-KERNEL-026`.

## Acceptance conditions

The implementation satisfies this specification when the public API establishes these facts:

- invalid relations make their partial-order proposition evaluate to `False`;

- `Unknown` is returned only by `ask()` and never establishes partial order, totality, or monotonicity;

- theorem-backed constructors handle large finite and infinite objects without exhaustive checks;

- the two-element equality order remains outside total-order categories;

- total-order elements use inherited poset comparison;

- `FinitePosets()` and `FiniteTotallyOrderedSets()` expose their inverse-image pullback squares;

- all inherited set operations work through Sage's controlled class linearization;

- iteration returns elements owned by the public ambient poset;

- nonmonotone set morphisms fail poset morphism admission;

- theorem-backed identities, composites, projections, and standard infinite maps enter `Mor(PartiallyOrderedSets())`;

- the projection to sets creates poset products and their universal morphisms;

- crossed product elements remain incomparable;

- finite-poset collection algorithms return owned finite subobjects;

- level sets return an owned indexed family;

- linear extensions return finite total orders on the same underlying set;

- no total-order class repeats poset comparisons, set operations, or element caches;

- no leaf method contains compiler routing metadata.
