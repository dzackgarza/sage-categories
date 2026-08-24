# Architecture remediation TODO

The architecture is not fixed. The current code violates every major boundary in the
remediation plan.

## Governing admission model

In this document, “establish” does not mean “compute at runtime.” A mathematical
property can enter the type and category system through three distinct routes. These
routes must never be merged.

### Checked admission

A checked constructor accepts arbitrary semantic input. It runs an exact implemented
decision procedure and admits the result only when the answer is `True`.

For example, a checked finite-poset constructor can enumerate all required pairs and
triples. It rejects a relation when reflexivity, antisymmetry, or transitivity is
`False` or `Unknown`.

The checked route is for input whose property is not already known from its
construction. It can return `Unknown` when no represented algorithm decides the
property. It must not treat `Unknown` as theorem-backed knowledge.

### Hypothesis-backed admission

A hypothesis-backed constructor accepts an owned applied predicate and an explicit
owned assumption context. For a set morphism \(f:P\to Q\), the applied predicate can be
`order_preserving(f)`.

The constructor verifies that the context contains that exact applied predicate. It
does not prove the predicate. The explicit hypothesis supplies the mathematical
precondition for this route.

### Theorem-backed construction

A theorem-backed constructor owns a mathematical construction whose result is known to
have the property. It constructs the result directly in the established property
category. It does not run an exhaustive decision procedure.

The specific construction is the authority. Python receives no theorem string, proof
record, certificate, opaque token, or general “trusted owner” value. The supporting
theorem and citation remain source documentation. The returned category placement is
the typed mathematical conclusion.

This is the trusted-builder boundary. Trust attaches to the definition and ownership of
the named constructor, not to data supplied by its caller. In Python, the constructor
“declares” the property by constructing the category-owned result type through its
controlled implementation path. It does not call a general prover or pass a Boolean
claim to a generic constructor.

Theorem-backed construction is required for properties that cannot be obtained by
finite enumeration. It is also preferred when exhaustive checking terminates but would
repeat knowledge already supplied by the construction.

Canonical examples include:

- the owned real-number constructor records that `RR` is uncountable;
- a named squaring constructor builds \(n\mapsto n^2:\mathbb N\to\mathbb N\) directly
  as a poset morphism;
- identity and composition constructors build poset morphisms without checking every
  ordered pair;
- the componentwise-product construction builds a poset and its monotone projections
  from the product theorem;
- a finite-total-order constructor accepts an enumeration, builds its induced relation,
  and returns the finite total order without a pairwise totality check;
- `SimplexOrders()[Aleph0]` builds the standard total order on the natural numbers from
  its defining ordinal construction.

None of these constructors proves its theorem in Python. None should attempt exhaustive
verification as a substitute.

### What remains forbidden

A constructor over arbitrary input cannot borrow a theorem that applies only to one
special construction. For example:

- a method accepting an arbitrary relation cannot declare it total because enumeration
  relations are total;
- a method accepting an arbitrary set morphism cannot declare it monotone because
  squaring on the natural numbers is monotone;
- a method accepting `owner: MathematicalObject` cannot treat object registration as
  theorem authority.

A public generic call such as `refine_from_theorem(value, owner)` does not identify the
construction theorem. The `owner` argument is an authority token, not mathematical
evidence. Adding a runtime check to that method would make the opposite mistake. The
correct repair is to remove permissive general theorem admission and place each theorem
in its specific construction-owned route.

The kernel can provide private allocation, canonical-image, and refinement mechanics.
Those mechanics supply no mathematical authority. A construction-owned method invokes
them only after its own defining data makes the theorem applicable.

The governing policies are `POL-MATH-016`, `POL-MATH-024`, `POL-MATH-028`,
`POL-MATH-030`, `POL-CAT-069`, `POL-CAT-070`, `POL-FUN-021`, `POL-FUN-022`, and
`POL-API-022`. See `CONTRIBUTING.md` and `specs/ordered-sets.md`.

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

## 12. Generic theorem refinement mistakes a value for construction authority

The current hypothesis-backed route receives an owned `Hypothesis` and
`HypothesisContext`. That is the correct kind of boundary for an explicit hypothesis.
The applied predicate and candidate must remain exact.

The theorem-backed route has a different defect. `refine_from_theorem()` accepts
`owner: MathematicalObject` and checks only that the owner is registered.

See `src/sage_categories/abstract_categories/full_subcategories.py:261`.

Object registration establishes no theorem. Any registered object can be supplied with
an arbitrary ambient candidate. The parameter therefore acts as an opaque authority
token.

The repair must not add runtime theorem validation. A theorem-backed fact can be
uncomputable, undecidable by available algorithms, or too expensive to verify. The
repair is structural:

- remove public generic theorem admission;
- put each theorem-backed path on the construction that owns the theorem;
- make that constructor accept only the semantic data to which its theorem applies;
- construct the result directly in the established property category;
- let private kernel refinement seed canonical ambient images without claiming
  mathematical authority.

For example, a componentwise-product constructor can declare its projections monotone.
A squaring constructor on `NN` can declare its map monotone. Neither fact licenses a
general method that accepts an arbitrary set morphism.

## 13. Leaf constructors perform refinement sequences

`ordered_set_owned_by()` constructs a poset, then performs two manual refinements.

See `src/sage_categories/theories/ordered_set_constructors.py:39`.

This leaf knows the implementation sequence:

\[
\text{Poset}\to\text{TotalOrder}\to\text{FiniteTotalOrder}.
\]

The named construction owner must accept the data that makes its theorem applicable and
create the strongest established result. For a finite order derived from an enumeration,
the constructor accepts the enumeration and builds the induced relation itself.

It does not accept an arbitrary relation and then attach totality by assertion. It also
does not need an exhaustive totality check, because the enumeration construction already
establishes totality.

Generic kernel refinement must seed every ambient image after the construction-owned
route establishes the category placement.

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

The target separation is exact:

- `checked_poset(...)` accepts an arbitrary owned relation and requires exact `True` for
  all three laws;
- `poset_from_hypothesis(...)` accepts the relation, its applied partial-order predicate,
  and the explicit hypothesis context;
- named constructors such as `discrete_order(...)` and
  `componentwise_product_order(...)` build their result directly from their defining
  construction theorem.

The theorem-backed routes must bypass exhaustive validation. Their names and controlled
inputs identify the construction. They do not accept proof text or an authority token.

## 15. Checked poset construction handles only finite sets

`PartiallyOrderedSets().__call__()` admits finite sets and rejects all other inputs.

See `src/sage_categories/theories/poset_core.py:464`.

This does not implement checked relation admission. It implements a finite-set branch.

The correct checked route asks whether all three laws evaluate to exact `True`.

This finite implementation does not restrict the theorem-backed routes. Infinite
discrete orders, ordinal orders, and componentwise product orders enter through their
named constructions without enumeration.

## 16. Poset morphism admission is finite-only

`PosetHomCategory.__call__()` requires a finite source before checking monotonicity.

See `src/sage_categories/theories/poset_core.py:328`.

There are no distinct:

- checked;
- hypothesis-backed;
- identity;
- theorem-backed

morphism construction routes.

The checked route accepts an arbitrary owned set morphism and requires exact `True` from
the available monotonicity decision procedure. It can return `Unknown` for an infinite
source.

The other routes do not convert that `Unknown` into `True`:

- a hypothesis-backed route requires the exact applied predicate
  `order_preserving(f)` in its context;
- the identity constructor declares the identity monotone from the identity theorem;
- composition declares the composite monotone from the composition theorem;
- a named squaring constructor on `NN` declares \(n\mapsto n^2\) monotone;
- a componentwise-product lift declares its projections and mediating arrows monotone.

These construction-owned declarations need no finite enumeration. They also do not
justify a public `from_theorem(f, arbitrary_owner)` route.

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

This containment decision governs checked refinement of an arbitrary represented
poset. It does not govern named infinite constructions. A constructor such as
`SimplexOrders()[Aleph0]` places its result directly in total orders because its defining
ordinal construction establishes totality.

Do not force such a constructor through `__contains__()`. Do not change its theorem into
a fabricated `True` decision. Preserve the checked and theorem-backed routes as separate
total methods.

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

Making the lift a subclass of `Functor` is insufficient when its object map works only
after mutable `register_object()` calls. A functor has a total object map on its declared
domain and a total arrow map on the corresponding arrows.

The lift can declare closure and arrow properties supplied by the construction theorem.
It does not need runtime monotonicity checks. Its defect is partial engineering state,
not theorem-backed declaration.

## 26. Poset product lifting performs leaf wiring

`PartiallyOrderedSets().chosen_limit()`:

- obtains the inherited set product;
- extracts product elements;
- builds the componentwise relation;
- constructs the poset apex;
- supplies a private arrow-lifting callback.

See `src/sage_categories/theories/poset_core.py:551`.

The componentwise relation belongs here. Generic product-lift plumbing does not.

The componentwise-product theorem establishes that the apex is a poset and that the
projections and mediating arrows are monotone. The poset construction must record those
typed conclusions directly. It must not enumerate product elements to re-prove them.

The leaf therefore supplies only its new mathematics:

- the componentwise order;
- the construction-owned poset apex;
- the typed conclusion that the lifted arrows are poset morphisms.

The kernel supplies total functorial lifting, comparison transport, cone plumbing, and
canonical images.

## 27. Product arrows bypass the owned Hom constructor

`_monotone_product_arrow()` directly invokes `hom.ObjectType`.

See `src/sage_categories/theories/poset_core.py:611`.

This bypasses normal morphism construction and its explicit theorem-backed route.

The required theorem-backed route is specific to the componentwise-product lift. It can
construct the poset morphism without checking all pairs because the product theorem
establishes monotonicity.

Do not replace the direct `ObjectType` call with a permissive
`hom.from_theorem(image, owner)` call. That only moves the unrestricted entry point. The
construction-owned lift must produce the owned morphism through a route unavailable to
arbitrary set maps.

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
5. Separate checked, hypothesis-backed, and construction-owned theorem-backed
   admission. Never add exhaustive checks to theorem-backed paths or encode theorem
   authority as an owner token.
6. Replace Python collection signatures with owned mathematical types.
7. Make product lifting an object-and-arrow functor.
8. Complete finite Sage lowering and semantic reconstruction.
9. Reduce poset and total-order theory to their mathematical owners.

Work below an unfinished earlier item preserves the broken architecture.

This order does not mean that theorem-backed paths wait for stronger runtime decision
procedures. Their mathematical conclusions are already known. It means the generic
kernel entry and canonical transport must exist before leaves rely on them.
