# Architecture remediation TODO

The architecture is not fixed. The current code violates every major boundary in the
remediation plan.

## 1. Category types are not the canonical implementations

The compiler creates extra refinement classes for each ambient Python type.

- `C.ObjectType` is not necessarily the type used for refined objects.
- `C.ElementType` is not necessarily the type used for refined elements.
- `C.ArrowType` is not necessarily the type used for refined arrows.
- One category can receive several implementation types.
- Static typing cannot name these runtime-generated refinements.

The defect is in `src/sage_categories/compiler.py:165`. `_refinement_type()` creates
another class above the category-owned type.

This directly contradicts `specs/leaves.md`. The category-owned type must be the
implementation.

## 2. Property categories do not declare complete role types

`FinitePosets()` declares only `ObjectType`.

`TotallyOrderedSets()` declares no local object, element, or arrow type.

`FiniteTotallyOrderedSets()` also declares no complete role types.

See:

- `src/sage_categories/theories/finite_posets.py:180`
- `src/sage_categories/theories/total_orders.py:66`
- `src/sage_categories/theories/total_orders.py:114`

The compiler currently hides this defect with generated subclasses. Static typing still
sees shared base types.

## 3. Refinement depends on ambient Python classes

The refinement type cache uses `(category, ambient_type)`.

See `src/sage_categories/compiler.py:267`.

A mathematical property refinement must depend on:

- the property category;
- the ambient mathematical implementation;
- the object, element, or arrow role.

It must not produce a new public implementation class for each ambient Python class.

## 4. Poset elements still implement generic refinement

`PosetElement` defines `_refined_element_from_ambient()`.

See `src/sage_categories/theories/poset_core.py:75`.

This is generic property-refinement machinery inside poset theory. It is not order
mathematics.

`PosetObject.element()` also:

- caches elements;
- selects `category().ElementType`;
- invokes the refinement constructor;
- stores the refined result.

See `src/sage_categories/theories/poset_core.py:170`.

The kernel must construct and cache transported elements. Poset theory must only define
order behavior.

## 5. Structural caches use incomplete keys

Object, element, and arrow structural caches use only the target category identity.

See `src/sage_categories/values.py:60`.

The required identity is:

\[
(\text{source ambient object},\text{source value},\text{target category}).
\]

The current cache cannot represent that key directly.

This affects:

- object images;
- element images;
- arrow images;
- route diamonds;
- canonical preimages.

## 6. Arrow preimages overwrite their normalized source

Functor arrow preimages use only the image hom category and image arrow.

See `src/sage_categories/abstract_categories/functor_core.py:114`.

Line 115 then replaces the normalized source with the original descendant arrow.

The cache cannot retain both source implementations. Reverse transport can therefore
select the wrong arrow.

## 7. Functor application repeats structural normalization

`on_object()`, `on_morphism()`, `on_element()`, and `__call__()` each perform route
normalization.

See:

- `src/sage_categories/abstract_categories/functor_core.py:70`
- `src/sage_categories/abstract_categories/functor_core.py:92`
- `src/sage_categories/abstract_categories/functor_core.py:118`
- `src/sage_categories/abstract_categories/functor_core.py:204`

There is no single canonical application path. Direct `on_*` calls and `__call__()`
reach the same result only incidentally.

## 8. Transport roles are inferred instead of required

`method_signature()` infers roles from Python annotations.

See `src/sage_categories/descriptors.py:94`.

The explicit role declaration is optional. It covers only named parameters and results.

See `src/sage_categories/descriptors.py:62`.

The compiler does not require explicit roles for:

- receivers;
- positional parameters;
- keyword parameters;
- variadic parameters;
- keyword collections;
- results.

It also treats unrecognized types as plain values. This silently disables required
transport.

## 9. Transport uses Python container shapes

Collection transport recognizes:

- `Iterator`;
- `Iterable`;
- `tuple`;
- `list`;
- `set`;
- `frozenset`.

See `src/sage_categories/descriptors.py:301`.

This is representation transport, not mathematical transport.

It does not transport owned:

- set subobjects;
- finite subobjects;
- discrete diagrams;
- indexed families;
- total-order objects.

## 10. Descriptor invocation performs runtime name dispatch

`_invoke_declared()` searches the receiver type by method name.

See `src/sage_categories/descriptors.py:343`.

This can select a different method body at runtime. The compiled declaration is
therefore not the sole executable owner.

The compiler must install the correct inherited descriptor during compilation. It must
not resolve implementations during invocation.

## 11. Full-subcategory element ownership is wrong

`FullSubcategoryElement` records the ambient element's category.

See `src/sage_categories/abstract_categories/full_subcategories.py:84`.

A refined element must have the refined category and refined ambient object. Its ambient
image remains a separate element.

The current constructor mixes those roles.

## 12. Refinement authority is unrestricted

`refine_with_hypothesis()` accepts no `AssumptionsContext`.

`refine_from_theorem()` accepts no construction owner or theorem authority.

See `src/sage_categories/abstract_categories/full_subcategories.py:318`.

Any caller can claim theorem-backed admission. The API does not encode who owns the
theorem.

## 13. Leaf constructors perform refinement sequences

`ordered_set_owned_by()` constructs a poset, then performs two manual refinements.

See `src/sage_categories/theories/ordered_set_constructors.py:39`.

This leaf knows the implementation sequence:

\[
\text{Poset}\to\text{TotalOrder}\to\text{FiniteTotalOrder}.
\]

The construction owner must create the strongest established result. Generic refinement
must seed every ambient image.

## 14. Poset construction mixes checked and theorem-backed entry

`PosetObject.__init__()` validates every finite object automatically.

See `src/sage_categories/theories/poset_core.py:143`.

`from_theorem()` calls the same constructor.

See `src/sage_categories/theories/poset_core.py:486`.

Therefore:

- checked construction and theorem construction are not separate;
- theorem-backed finite construction repeats exhaustive validation;
- hypothesis-backed construction has no distinct route;
- construction authority is not represented.

## 15. Checked poset construction handles only finite sets

`PartiallyOrderedSets().__call__()` admits finite sets and rejects all other inputs.

See `src/sage_categories/theories/poset_core.py:464`.

This does not implement checked relation admission. It implements a finite-set branch.

The correct checked route asks whether all three laws evaluate to exact `True`.

## 16. Poset morphism admission is finite-only

`PosetHomCategory.__call__()` requires a finite source before checking monotonicity.

See `src/sage_categories/theories/poset_core.py:328`.

There are no distinct:

- checked;
- hypothesis-backed;
- identity;
- theorem-backed

morphism construction routes.

## 17. Morphism checking uses a raw callable

`check_order_preserving()` accepts a Python callable between poset elements.

See `src/sage_categories/theories/poset_core.py:289`.

The mathematical input is an owned set morphism. Callable lowering belongs inside a
private boundary.

## 18. Public finite-poset APIs use representation types

Finite-poset methods return iterators and built-in integers.

See `src/sage_categories/theories/finite_posets.py:63`.

The required results are:

- finite set subobjects for covers, intervals, ideals, filters, and extrema;
- a discrete indexed family for level sets;
- a finite total-order object for linear extensions;
- owned natural-number or cardinal values where required.

`rank()` also combines two operations through an optional argument.

See `src/sage_categories/theories/finite_posets.py:155`.

The specification requires separate total methods.

## 19. Finite-poset inputs use generic iterables

Methods such as `order_ideal()` and `is_chain_of_poset()` accept
`Iterable[PosetElement]`.

See `src/sage_categories/theories/finite_posets.py:114`.

These inputs must be owned mathematical collections. Python iteration belongs only
inside traversal code.

## 20. Finite algorithms do not reconstruct semantic results

The leaf calls Sage and returns Sage-produced elements through Python iterators.

See `src/sage_categories/theories/finite_posets.py:70`.

It does not explicitly:

- lower refined elements to the selected Sage representation;
- map Sage results to canonical refined elements;
- construct owned result collections;
- preserve the original finite-poset ambient object.

Direct Sage use is valid. The missing semantic reconstruction is the violation.

## 21. The finite Sage cache is not tied to an owned representation boundary

`FinitePosetObject` stores `_sage_value` directly and builds it from `tuple(self)`.

See `src/sage_categories/theories/finite_posets.py:46`.

This is permitted in principle. The current implementation still lacks explicit
conversion in both directions.

It also uses `isinstance()` to classify a mathematical decision.

See `src/sage_categories/theories/finite_posets.py:52`.

The correct boundary requires exact `True` or `False`.

## 22. Finite-poset construction bypasses category admission

`FinitePosetsCategory.__call__()` directly invokes `PartiallyOrderedSets().ObjectType`.

See `src/sage_categories/theories/finite_posets.py:192`.

This bypasses the checked, hypothesis-backed, and theorem-backed category constructors.

It then manually refines the result.

## 23. Totality is outside category containment

Totality is implemented by the module function `is_total_order()`.

See `src/sage_categories/theories/total_orders.py:32`.

The plan places totality computation in `TotallyOrderedSets().__contains__()`.

The current predicate wrapper also converts `Unknown` to `False` through `is True`.

See `src/sage_categories/theories/total_orders.py:125`.

That loses the distinction between rejection and unavailable computation.

## 24. The finite-total-order diamond is handwritten

`FiniteTotallyOrderedSetsCategory` manually defines:

- a restricted structural functor;
- two structural branches;
- a natural isomorphism;
- an identity component.

See `src/sage_categories/theories/total_orders.py:55`.

Some diamond declaration is mathematical. The current code also compensates for
noncanonical transport.

Line 99 asserts that both images are already identical. The kernel does not establish
this independently.

## 25. Product lifting is callback-based

`ProductLift` stores `lift_morphism`, a raw callback.

See `src/sage_categories/abstract_categories/product_presentations.py:70`.

`StructuralFunctor.lift_product()` accepts another optional callback.

See `src/sage_categories/abstract_categories/functor_core.py:326`.

A construction lift must have object and arrow maps. It must act functorially.

## 26. Poset product lifting performs leaf wiring

`PartiallyOrderedSets().chosen_limit()`:

- obtains the inherited set product;
- extracts product elements;
- builds the componentwise relation;
- constructs the poset apex;
- supplies a private arrow-lifting callback.

See `src/sage_categories/theories/poset_core.py:551`.

The componentwise relation belongs here. Generic product-lift plumbing does not.

## 27. Product arrows bypass the owned Hom constructor

`_monotone_product_arrow()` directly invokes `hom.ObjectType`.

See `src/sage_categories/theories/poset_core.py:611`.

This bypasses normal morphism construction and its explicit theorem-backed route.

## 28. Relation construction has no public set-owned operation

Poset constructors import `_predicate_relation()` from another theory module.

See:

- `src/sage_categories/theories/poset_core.py:659`
- `src/sage_categories/theories/ordered_set_constructors.py:16`

The relation is correctly represented as a subobject of \(X\times X\). Its constructor
remains private and representation-shaped.

`Sets()` must provide the owned public construction before poset theory depends on it.

## 29. The repository is in a mixed architecture

The computation decorator and mirrored Sage implementation surface are gone from the
live source.

However, their removal did not repair:

- canonical transport;
- category-owned role types;
- generic refinement;
- mathematical collection transport;
- poset admission;
- functorial product lifting;
- semantic Sage reconstruction.

The current finite-poset methods now follow the correct leaf ownership rule. Their
surrounding kernel and public types remain incorrect.

## Required repair order

The dependency order is strict:

1. Fix canonical object, element, and arrow transport.
2. Make compiled role types category-owned and statically visible.
3. Replace dynamic ambient-type refinement with generic property refinement.
4. Remove refinement logic from poset elements and objects.
5. Separate checked, hypothesis-backed, and theorem-backed admission.
6. Replace Python collection signatures with owned mathematical types.
7. Make product lifting an object-and-arrow functor.
8. Complete finite Sage lowering and semantic reconstruction.
9. Reduce poset and total-order theory to their mathematical owners.

Work below an unfinished earlier item preserves the broken architecture.
