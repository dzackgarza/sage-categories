# Sets specification

`Sets()` owns the public algorithms for sets, set elements, and total functions.
Categories with a selected structural functor to `Sets()` inherit this API.

Standard set theory and category theory are assumed. This specification fixes API
ownership, constructors, algorithms, result categories, and exact failure states.

## Owned API roles

`Sets()` owns three implementation types:

- `Sets.ObjectType` implements set objects.
- `Sets.ElementType` implements elements with an ambient set.
- `Sets.ArrowType` implements total functions with a domain and codomain.

An owned element records both its value and its ambient set. Transport must preserve
that ambient set. The same mathematical value can produce distinct owned elements in
distinct sets.

Private representations can include Sage parents, predicates, symbolic expressions,
finite collections, indexed families, tagged values, or universal-construction data.
No private representation becomes another public owner.

The `Sets()` subtree owns:

- membership and available iteration;
- total set maps and their arrow properties;
- cardinality;
- subobjects and images;
- function sets and exponentials;
- products, coproducts, limits, and colimits.

Property subcategories add only their stated property. They inherit all set operations.

## Set-object API

Every object of `Sets()` supplies these operations when their input data exists:

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

Y.exponential(X)
Y ** X
X.powerset()
X.subsets_of_size(k)
X.finite_subsets()
```

Generic categorical methods come from the category foundation. `Sets()` does not
create another implementation of identity, composition, or arrow-category formation.

`X.cardinality()` returns a cardinal object. It can remain symbolic or unknown.

## Set maps and function sets

`X.Hom(Y)` is the owned set of total functions from `X` to `Y`.

A map constructor can use a callable or explicit mapping as its private rule. The
constructor must establish that the rule is total and lands in `Y`.

The public construction routes are distinct:

- a checked route requires an exact `True` result;
- a hypothesis route uses a scoped assumption about the applied map;
- a named construction uses its defining theorem.

`False` rejects checked admission. `Unknown` does not admit the rule as a set arrow.
A callable does not establish totality by itself.

After admission, a set arrow supplies:

```python
f(x)
f.domain()
f.codomain()
f.image()
```

Evaluation requires `x in f.domain()`. It returns an owned element of `f.codomain()`.
Identity and composition arrive through inherited arrow operations.

The following expressions construct the same owned object:

```python
X.Hom(Y)
ExponentialOfSets(Y, X)
Y.exponential(X)
Y ** X
```

This object is (Y^X). It retains the evaluation arrow. Its currying operation returns
the unique arrow required by the exponential universal property.

Function rules need no enumeration. This supports maps such as `QQ -> ZZ` and
`RR -> RR^2`.

## Arrow property categories

Set isomorphisms, monomorphisms, and epimorphisms are objects of their inherited arrow
property categories.

In `Sets()`:

- isomorphisms are bijections;
- monomorphisms are injective functions;
- epimorphisms are surjective functions.

A checked property query returns a decision. A property constructor refines an arrow
only after an exact result, scoped hypothesis, or named theorem establishes the property.

An inverse of an isomorphism is an owned set arrow. It satisfies both inverse equations.

## Products

The product API accepts arbitrary set-indexed families:

```python
CartesianProductOfFamily(I, lambda i: X_i)
CartesianProductOfSets((X, Y, Z))
CartesianProductMorphismOfFamily(I, lambda i: f_i)
cartesian_product_morphism(f, g, h)
```

A product presentation retains:

```python
P.diagram()
P.index_category()
P.projection(i)
P.universal_morphism(cone)
P.cardinality()
P.factor_cardinalities()
```

`P.projection(i)` and `P.universal_morphism(cone)` are owned set arrows. They satisfy
the product equations.

A product element is an indexed family:

```python
x[i]
x.components()
iter(x)  # only when the index set has a chosen finite enumeration
```

The product cardinality is the indexed product of the factor cardinalities.

## Coproducts

The coproduct API mirrors the product API:

```python
CoproductOfFamily(I, lambda i: X_i)
CoproductOfSets((X, Y, Z))
CoproductMorphismOfFamily(I, lambda i: f_i)
coproduct_morphism(f, g, h)
```

A coproduct presentation retains:

```python
C.diagram()
C.index_category()
C.injection(i)
C.universal_morphism(cocone)
C.cardinality()
C.cofactor_cardinalities()
```

A coproduct element is a tagged element:

```python
x.index()
x.value()
```

The coproduct cardinality is the indexed sum of the factor cardinalities.

## General limits and colimits

The limit constructor accepts an arbitrary small diagram in `Sets()`. Its result retains:

- the diagram;
- the limiting cone;
- every cone component;
- the universal map from another cone.

The standard set algorithm realizes the apex as a subobject of the product of diagram
objects. Its predicate is compatibility with every diagram arrow.

The colimit constructor also accepts an arbitrary small diagram. Its result retains:

- the diagram;
- the colimiting cocone;
- every cocone component;
- the universal map to another cocone.

The standard set algorithm realizes the apex as a quotient of the coproduct of diagram
objects by the generated diagram relation.

Products and coproducts use discrete diagrams. Other diagram shapes use the same limit
and colimit interfaces.

## Subobjects, images, and power objects

`X.subset_from(predicate)` constructs a chosen subset with its inclusion into `X`.
The predicate is a private membership evaluator. It can return `Unknown`.

A chosen subset supplies:

```python
A.inclusion()
A.underlying_set()
A.characteristic_morphism()
A.powerset()
A.cardinality()
```

An abstract subobject is represented by a monomorphism. Its image supplies the canonical
chosen subset representative. The chosen monomorphism remains part of the subobject data.

`f.image()` constructs an owned subobject of `f.codomain()`. It does not require source
enumeration. Membership in the image can remain `Unknown`.

`PowerSet(X)` and `X.powerset()` construct the owned set of subsets of `X`. The same
object is the function set from `X` to the owned two-element set.

The power object supplies:

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

Its elements supply:

```python
x in A
A <= B
A.union(B)
A.intersection(B)
A.difference(B)
A.symmetric_difference(B)
A.complement()

A | B
A & B
```

These operations return owned subsets or exact decisions. They do not return Python
containers.

`X.subset_poset()` orders the same subset objects by inclusion. The result belongs to
the owned poset category and retains `X` as its base set.

## Finite and fixed-cardinality subsets

The public constructors are:

```python
FiniteSubsets(X)
SubsetsOfSize(X, k)
```

Their elements are owned finite subobjects of `X`.

If `X` has a chosen enumeration, these constructions can derive a chosen enumeration.
Countability alone does not select one.

With an induced enumeration, `FiniteSubsets(X)` supplies:

```python
S.cardinality()
S.index(subset)
S[n]
```

With an induced enumeration, `SubsetsOfSize(X, k)` supplies:

```python
S.subset_cardinality()
S.cardinality()
S[n]
```

The cardinality methods use cardinal arithmetic. They do not enumerate an infinite base
set.

## Cardinality and enumeration

The cardinal and ordinal APIs are specified in [cardinality.md](cardinality.md).

The cardinality property subcategories are:

```python
Sets().Finite()
Sets().Infinite()
Sets().Countable()
Sets().Uncountable()
```

Their checked membership procedures can return `Unknown`. Named theorem-backed
constructors can place a set directly in one of these categories.

Countability does not select an enumeration. A chosen enumeration adds:

```python
X[n]
X.position(x)
X.enumeration_injection()
```

The enumeration is owned structure. Its inverse is the stated injection into the index
set.

## Ordered sets

The ordered-set API is specified in [ordered-sets.md](ordered-sets.md).

A partial order is chosen structure on a set. It is not a property of the bare set.
Totality is a property of that chosen partial order. Cardinality and enumeration remain
independent structures.

## Finitely supported function sets

For a pointed set `(X, x0)` and index set `S`, the constructor for (X^{(S)}) retains:

```python
A.index_set()
A.value_set()
A.basepoint()
A.cardinality()
```

Its elements are owned functions with finite support. The cardinality method uses the
applicable cardinal formula without enumerating an infinite function set.

## Private computation engines

`Sets.ObjectType` is the sole public implementation of a set. It can use Sage, SymPy,
GAP, Julia packages, Singular, Macaulay2, or several engines together. These are private
algorithm providers, not competing set implementations.

Choose an engine from the mathematical construction and the exact algorithm it supplies.
Use its native construction whenever that discharges logic which the repository would
otherwise have to implement. A single owned set can use different engines for
membership, simplification, enumeration, cardinality, images, and other operations.

Typical engine contributions include:

| Construction or query | Suitable private engine contribution |
| --- | --- |
| Explicit or enumerated sets | Sage parents, enumerated sets, and exact iterators |
| Symbolic subsets and set algebra | SymPy `ConditionSet`, `Intersection`, `Union`, and `Complement` |
| Symbolic images and arithmetic progressions | SymPy `imageset`, `ImageSet`, and `Range` |
| Finite-group orbits, cosets, and conjugacy classes | GAP or Sage interfaces to GAP |
| Polynomial solution sets and algebraic loci | Singular, Macaulay2, Sage, or SymPy algorithms appropriate to the coefficient domain |
| Specialized exact algorithms exposed by a Julia package | The package's native mathematical construction |

An owned operation can compose engine results. For example, SymPy can normalize a
predicate intersection to a finite symbolic set. Sage can then supply an owned finite
enumeration. The set implementation reconstructs one owned result from both computations.

Engine choice is private to the owning method or its private helper. The public API has
no backend argument, backend registry, engine-specific set class, or alternative method
name. Engine methods never enter the public surface automatically.

Select engines through the known semantic form of the input. Do not probe engines by
exception or attempt implementations until one succeeds. If no applicable exact
algorithm or construction theorem decides the result, return the typed unknown value.

Construction-owned mathematics remains authoritative. For example, the image of an
established monomorphism has the domain cardinality. No engine must rediscover that
theorem.

### SymPy set constructions

SymPy supplies mature symbolic set representations and simplification algorithms. Use
them instead of implementing local symbolic set algebra.

The primary SymPy representations are:

| Mathematical input | SymPy representation or algorithm |
| --- | --- |
| Explicit finite set | `FiniteSet` |
| Finite or infinite arithmetic progression | `Range` |
| Standard number set | `Naturals`, `Integers`, `Rationals`, or `Reals` |
| Predicate subobject | `ConditionSet(symbol, condition, base_set)` |
| Membership proposition | `Contains(element, set)` |
| Image of a symbolic map | `imageset(lambda, domain)` or unevaluated `ImageSet` |
| Union, intersection, or complement | `Union`, `Intersection`, or `Complement` |
| Cartesian product | `ProductSet` |
| Power object | `PowerSet` |

For example, SymPy 1.14 performs these computations:

```python
Intersection(S.Naturals, FiniteSet(1, 2, 3))
# FiniteSet(1, 2, 3)

ConditionSet(n, Contains(n, FiniteSet(1, 2, 3)), S.Naturals)
# FiniteSet(1, 2, 3)

imageset(Lambda(n, sympy.Integer(2) * n), S.Naturals)
# Range(2, oo, 2)
```

The first two results reconstruct an owned finite subset with cardinality `3`. The last
result reconstructs an owned countably infinite subset with cardinality `aleph0`.

SymPy can also leave a construction unresolved:

```python
ImageSet(Lambda(n, sympy.Integer(2) * n), S.Naturals).is_finite_set
# None

imageset(Lambda(n, n ** sympy.Integer(2)), S.Naturals).is_finite_set
# None

ConditionSet(n, Eq(p(n), 0), S.Naturals).is_finite_set
# None
```

An unevaluated `ImageSet` or `ConditionSet` remains a valid private representation. Its
owned cardinality is `UnknownCardinality()` unless defining data or a construction
theorem supplies a stronger result.

SymPy sets do not supply one general `cardinality()` operation. Reconstruct the owned
cardinal from the normalized result:

- `FiniteSet` contributes its exact finite size.
- A finite `Range` contributes its exact finite size.
- An infinite `Range` contributes `aleph0`.
- A standard number set contributes its established cardinal.
- An unresolved symbolic set contributes `UnknownCardinality()`.

Never use `None` for an unknown cardinality. Never assign the domain cardinality to an
image unless injectivity or another theorem establishes that equality.

| Owned operation | SymPy value | Required reconstruction |
| --- | --- | --- |
| Membership | `Contains(x, X)` | Return `True`, `False`, or Sage `Unknown`. |
| Predicate subset | `ConditionSet(x, P(x), X)` | Return the owned subset with its inclusion. |
| Image | `imageset(f, X)` or `ImageSet(f, X)` | Return the owned image subobject. Preserve an unevaluated image. |
| Finite normalization | `FiniteSet` | Return an owned finite set and exact finite cardinal. |
| Progression normalization | `Range` | Return an owned enumerated set and its finite cardinal or `aleph0`. |
| Set algebra | `Union`, `Intersection`, `Complement`, `ProductSet` | Return the corresponding owned construction. |
| Set equality or inclusion | symbolic set relations | Return an exact decision or `Unknown`. |
| Cardinal calculation | normalized set type and symbolic properties | Return an owned cardinal value, never `None`. |
| Universal constructions | symbolic set expressions | Retain all defining arrows and universal maps. |

The owning set method reconstructs the owned mathematical result. See the [SymPy sets
documentation](https://docs.sympy.org/latest/modules/sets.html) for the supported
representations and simplifications.

## Unknown and partial algorithms

Exact queries can return `bool | Unknown`. This includes membership, subset order,
set equality, cardinal comparisons, and cardinal property queries.

The algorithm contract is:

- return `True` after an exact proof;
- return `False` after an exact disproof;
- return `Unknown` when available exact algorithms establish neither result;
- preserve `Unknown` under three-valued Boolean operations;
- refine a property category only after exact evidence or a construction theorem.

`Unknown` does not block construction of an honest predicate subobject, symbolic image,
universal construction, or cardinal expression.

## Acceptance conditions

The implementation satisfies this specification when the public API establishes these
facts:

- every admitted arrow is total and has its stated domain and codomain;
- evaluation returns an owned codomain element;
- identity and composition use inherited arrow operations;
- all four function-set entry points return one canonical object;
- every chosen subset retains its inclusion;
- every abstract subobject retains its monomorphism and canonical image;
- products retain projections and universal maps;
- coproducts retain injections and universal maps;
- limits and colimits retain their diagrams and universal data;
- power-object operations return owned subsets and arrows;
- countability does not create a chosen enumeration;
- cardinal methods return cardinal objects;
- every operation uses a mature engine construction when one supplies the required exact
  mathematics;
- one owned set can combine several private engines without exposing an engine choice;
- supported symbolic set operations use SymPy instead of duplicate local algorithms;
- normalized `FiniteSet` and `Range` results reconstruct their exact owned cardinalities;
- unevaluated `ConditionSet` and `ImageSet` results reconstruct valid owned sets with
  `UnknownCardinality()` when no theorem decides more;
- exact failures remain `False` or `Unknown`;
- private engine values never cross the public boundary.

The governing policies include `POL-MATH-001` through `POL-MATH-033`,
`POL-CAT-020`, `POL-CAT-027` through `POL-CAT-032`, `POL-CAT-040` through
`POL-CAT-045`, `POL-SET-001` through `POL-SET-034`, and `POL-KERNEL-001` through
`POL-KERNEL-024`.
