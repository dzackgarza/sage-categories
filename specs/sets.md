# Sets specification

`Sets()` owns the public algorithms for sets, set elements, and total functions.
Categories with a declared functor to `Sets()` inherit this API.

Standard set theory and category theory are assumed.
This specification fixes API ownership, constructors, algorithms, result categories, and exact failure states.

Every set operation specified as a predicate follows the interface in [Property refinement](property-refinement.md).
Applying it returns a proposition.
Only `ask()` decides that proposition as `True`, `False`, or `Unknown`.

The governing policies are `POL-MATH-034`, `POL-MATH-035`, `POL-CAT-001`, `POL-CAT-021`, `POL-CAT-028`, `POL-CAT-086`, `POL-CAT-088`, `POL-SET-001` through `POL-SET-036`, and `POL-API-009`, `POL-API-010`, `POL-API-015`, and `POL-API-016`.

## Owned API classes

`Sets()` owns three implementation types:

- `Sets.ObjectType` implements set objects.

- `Sets.ElementType` implements points `t: 1 -> X`, the actual elements of `X`.

- `Sets.MorphismType` implements total functions with a domain and codomain.

An owned element is a point `t: 1 -> X`, and its parent is `X`.
A generalized element `T -> X` with nonterminal domain is an ordinary morphism in `Sets()`, not a `Sets.ElementType` value.
The same point datum can produce distinct owned elements in distinct sets.

Private representations can include Sage parents, predicates, symbolic expressions, finite collections, indexed families, tagged values, or universal-construction data.
No private representation becomes another public owner.

The `Sets()` subtree owns:

- membership and available iteration;

- total set maps and their morphism properties;

- cardinality;

- subobjects and images;

- function sets and exponentials;

- products, coproducts, limits, and colimits.

Property subcategories add only their stated property.
They inherit all set operations.

## Set-object API

Every object of `Sets()` supplies these operations when their input data exists:

```python
X.cardinality()
Mor(Sets())(X, Y)
Mor(Sets())(X, X)
Mor(Sets())(X, X).Automorphisms()
Mor(Sets())(X, Y).Isomorphisms()
Mor(Sets())(X, Y).Monomorphisms()
Mor(Sets())(X, Y).Epimorphisms()
X.identity()

X.subobjects()
X.superobjects()
X.covering_objects()
X.covered_objects()

Y ** X
X * Y
X + Y
```

Generic categorical methods come from the category foundation.
`Sets()` does not create another implementation of identity, composition, or morphism-category formation.

`X.cardinality()` returns an exact cardinal or Sage `Unknown`.

## Canonical objects and the separator

`Sets()` owns these objects, each constructed once and retained by identity:

- `Sets().Empty()`, the empty set `{}`;

- `Sets().Terminal()`, the one-point set `1 = {*}`;

- `Sets().Simplex(n)`, the set `[n] = {0, ..., n}` for `n >= 0`.

`[1] = {0, 1}` is the object `2` of the power object `2 ** X`.

`G_Sets = Sets().Terminal()` is the separator of `Sets()`. A point of `X` is a point `1 -> X`. Set membership, enumeration, and cardinality use `Mor(Sets())(1, X)` through this separator.

## Set maps, morphism categories, and function sets

`Mor(Sets())(X, Y)` is the discrete category on the total set maps from `X` to `Y`. It exists for every pair `X, Y in Sets()`. Its inhabitation and emptiness are owned predicates.

The function set `Y ** X` is the exponential object of `Sets()`. It is a distinct owned object: `Mor(Sets())(X, Y)` is the discrete category on the elements of `Y ** X`.

`Mor(Sets())(X, Y)(rule)` constructs a set map.
The rule can be a callable or explicit mapping as its private rule.
The constructor must establish that the rule is total and lands in `Y`.

A raw rule determines propositions stating totality and codomain closure.
`ask()` can evaluate those propositions.
Exact `True` invokes the owned morphism constructor.
Exact `False` rejects admission.
`Unknown` leaves the rule outside the set-morphism category.
The trusted morphism constructor, an active assumption, exact positive evaluation, and a named mathematical construction all use the same category constructor.
A callable does not establish totality by itself.

After admission, a set morphism supplies:

```python
f(x)
f.domain()
f.codomain()
f.image()
```

Evaluation requires `x in f.domain()` and evaluates the retained rule on the point datum.
For a generalized element `t: T -> X`, morphism composition gives `f * t: T -> Y`.
Identity and composition arrive through inherited morphism operations.

The exponential object is:

```python
Y ** X
```

This object is (Y^X). It retains the evaluation morphism.
Its currying operation returns the unique morphism required by the exponential universal property.

Function rules need no enumeration.
This supports maps such as `QQ -> ZZ` and `RR -> RR^2`.

## Morphism property categories

Set isomorphisms, monomorphisms, and epimorphisms are objects of the property subcategories `Mor(Sets()).Isomorphisms()`, `Mor(Sets()).Monomorphisms()`, and `Mor(Sets()).Epimorphisms()`, defined once at the `Cat()` level.
Fixed endpoints use `Mor(Sets())(X, Y).Monomorphisms()`.

In `Sets()`:

- isomorphisms are bijections;

- monomorphisms are injective functions;

- epimorphisms are surjective functions.

A morphism-property predicate returns its applied proposition.
`ask()` evaluates it.
A property constructor refines a morphism only after an exact result, scoped hypothesis, or named theorem establishes the property.

An inverse of an isomorphism is an owned set morphism.
It satisfies both inverse equations.

## Products

The product construction accepts a discrete diagram over `Discrete(S)` for `S in Sets()` through its category-owned constructor.
The diagram is given by its object rule `i |-> X_i`; it never requires a finite tuple.
A Python sequence `(X_0, ..., X_n)` is the convenience form and denotes the diagram over `Discrete([n])`.

```python
P = Sets().Products()(diagram)
P2 = X * Y
```

`X * Y` is `Sets().Products()((X, Y))`. The product functor maps diagram morphisms to the induced product morphisms.

A product presentation retains:

```python
P.diagram()
P.index_category()
P.product_projection(i)
P.universal_morphism(cone)
P.cardinality()
P.factor_cardinalities()
```

`P.product_projection(i)` and `P.universal_morphism(cone)` are owned set morphisms.
They satisfy the product equations.

A product element is an indexed family:

```python
x[i]
x.components()
iter(x)  # only when the index set has a chosen finite enumeration
```

`P.cardinality()` is the computational case tree owned by the product implementation (see [Cardinality and enumeration](#cardinality-and-enumeration)).

## Coproducts

The coproduct construction uses the dual category-owned interface:

```python
Q = Sets().Coproducts()(diagram)
Q2 = X + Y
```

`X + Y` is `Sets().Coproducts()((X, Y))`. The diagram is a discrete diagram over `Discrete(S)` given by rule, as for products.
The coproduct functor maps diagram morphisms to the induced coproduct morphisms.

A coproduct presentation retains:

```python
Q.diagram()
Q.index_category()
Q.coproduct_injection(i)
Q.universal_morphism(cocone)
Q.cardinality()
Q.cofactor_cardinalities()
```

A coproduct element is a tagged element:

```python
x.index()
x.value()
```

`Q.cardinality()` is the computational case tree owned by the coproduct implementation (see [Cardinality and enumeration](#cardinality-and-enumeration)).

## General limits and colimits

`Sets().Limits(I)` and `Sets().Colimits(I)` are indexed by one supplied shape `I in Cat()`. A diagram of shape `I` is an object of `Fun(I, Sets())`. The limit constructor accepts such a diagram `D`. Its result retains:

- the diagram;

- the limiting cone;

- every cone component;

- the universal map from another cone.

The limit of `D: I -> Sets()` is the predicate subset of the product `prod_{i in Ob(I)} D(i)` cut out by compatibility: a family `(x_i)` is a member when `ask(D(u)(x_i) == x_j) is True` for every generating morphism `u: i -> j` of `I`. Membership decides when `I` is finitely presented and every generating equality decides, and is `Unknown` otherwise.
The projections are the restricted product projections.
The mediating map of a cone is its map into the product.

The colimit constructor also accepts a diagram of shape `I`. Its result retains:

- the diagram;

- the colimiting cocone;

- every cocone component;

- the universal map to another cocone.

The colimit of `D` is the quotient of the coproduct `coprod_i D(i)` by the equivalence relation generated by `(i, x) ~ (j, D(u)(x))`. Its injections are the coproduct injections followed by the quotient map.
Its element equality is an owned predicate.
For `I = omega`, the exact handler decides `True` when two representatives agree at the larger of their two indices under the transition maps and returns `Unknown` otherwise; for every other infinite shape it returns `Unknown`.

Products and coproducts are these constructions at discrete shapes.
Pullbacks, pushouts, equalizers, and coequalizers are these constructions at their named shapes: `Sets().Pullbacks() = Sets().Limits(L(2, 2))`, `Sets().Pushouts() = Sets().Colimits(L(2, 0))`, `Sets().Equalizers() = Sets().Limits(WalkingParallelPair)`, and `Sets().Coequalizers() = Sets().Colimits(WalkingParallelPair)`. Each retains its named projections and injections.

## Subobjects, images, and power objects

`X.subset_from(predicate)` constructs a chosen subset with its monomorphism into `X`. The predicate returns the membership proposition for a candidate element.
`ask()` can evaluate that proposition as `True`, `False`, or `Unknown`.

A chosen subset supplies:

```python
A.monomorphism()
A.characteristic_morphism()
A.cardinality()
```

`A` is itself an object of `Sets()`, and the set it sits inside is
`A.monomorphism().codomain()`. Neither needs an accessor, and a name such as
`underlying_set()` would choose a codomain silently (`POL-FUN-037`).

An abstract subobject is represented by a monomorphism.
Its image supplies the canonical chosen subset representative.
The chosen monomorphism remains part of the subobject data.

`f.image()` constructs an owned subobject of `f.codomain()`. It does not require source enumeration.
Image membership remains a proposition when no handler can decide it.

`2 ** X`, with `2 = [1] = Sets().Simplex(1)`, constructs the power object of `X`. It is the function set from `X` to `2`.

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

These operations return owned subsets or applied propositions.
They do not return Python containers.

`X.subset_poset()` orders the same subset objects by inclusion.
The result belongs to the owned poset category and retains `X` as its base set.

## Finite and fixed-cardinality subsets

The public constructors are:

```python
Sets().FiniteSubsets()(X)
Sets().SubsetsOfSize(k)(X)
```

Their elements are owned finite subobjects of `X`.

If `X` has a chosen enumeration, these constructions can derive a chosen enumeration.
Countability alone does not select one.

With an induced enumeration, `Sets().FiniteSubsets()(X)` supplies:

```python
S.cardinality()
S.index(subset)
S[n]
```

With an induced enumeration, `Sets().SubsetsOfSize(k)(X)` supplies:

```python
S.subset_cardinality()
S.cardinality()
S[n]
```

The cardinality methods use cardinal arithmetic.
They do not enumerate an infinite base set.

## Cardinality and enumeration

The cardinal and ordinal APIs are specified in [cardinality.md](cardinality.md).

The cardinality property subcategories are:

```python
Sets().Finite()
Sets().Infinite()
Sets().Countable()
Sets().Uncountable()
```

Each category declares its membership proposition once.
The kernel implements `__contains__()` by calling `ask()` on that proposition.
An `Unknown` decision fails loudly there, since a bool cannot carry it; ask the proposition when the undecided case must be handled.
A trusted category constructor or named mathematical construction places a set directly in the property category.

### Exact cardinality or `Unknown`

The cardinality operation returns an exact cardinal or Sage `Unknown`:

```python
X.cardinality() -> Cardinal | UnknownClass
```

A cardinal is an exact value: a finite cardinal, `aleph(alpha)`, `2 ** aleph(0)`, or another value formed by exact cardinal arithmetic.
There is no placeholder cardinal, no unknown cardinal kind, and no symbolic "cardinality of X" value.

Cardinal arithmetic, equality, and order are defined on cardinals only.
Cardinals implement no `Unknown` handling.

A set construction's `cardinality()` is a computational case tree owned by the `Sets()` implementation of that construction.
It routes on the data the construction retains: the index set's cardinality, the retained diagram's codomain placement (`Sets().Finite()`, `Sets().Countable()`, `Sets().Uncountable()`), a retained constant diagram, and the factor cardinalities when the index is finite.
Each case cites the theorem that decides it.
The product cases are: a finite index with every factor exact gives the exact product; a finite index with an empty factor gives `0`; the constant diagram at `X` over `S` gives `(#X) ** (#S)`; an infinite index with codomain `Sets().Uncountable()` places the product in `Sets().Uncountable()`; a finite index with codomain `Sets().Countable()` places the product in `Sets().Countable()`. When no case applies the result is `Unknown`. Coproducts use the dual sum cases.

If SymPy normalizes a subset to `FiniteSet(1, 2, 3)`, its cardinality is `3`.

If the image morphism is monic, the construction theorem gives

\[
\lvert\operatorname{im}(f)\rvert=\lvert\operatorname{dom}(f)\rvert.
\]

If neither route applies, `cardinality()` returns `Unknown`.

`X.is_finite()`, `X.is_countable()`, and the other cardinal property methods return applied predicates.
`ask()` decides them from category placement, active assumptions, and the routes the owning implementation registers: a known cardinality decides finiteness and countability, and a `Sets()` construction registers the case routes that external mathematics supplies for it.
`assume(X.is_finite())` and the property subcategory constructors `Sets().Finite()`, `Sets().Countable()`, and `Sets().Uncountable()` are the positive routes.

Countability does not select an enumeration.
A chosen enumeration adds:

```python
X[n]
X.position(x)
X.enumeration_injection()
```

The enumeration is owned structure.
Its inverse is the stated injection into the index set.

## Ordered sets

The ordered-set API is specified in [ordered-sets.md](ordered-sets.md).

A partial order is chosen structure on a set.
It is not a property of the bare set.
Totality is a property of that chosen partial order.
Cardinality and enumeration remain independent structures.

## Finitely supported function sets

For a pointed set `(X, x0)` and index set `S`, the constructor for (X^{(S)}) retains:

```python
A.index_set()
A.value_set()
A.basepoint()
A.cardinality()
```

Its elements are owned functions with finite support.
The cardinality method uses the applicable cardinal formula without enumerating an infinite function set.

## Private computation engines

Each compiled set class owns one private state record.
The object record retains its membership rule and cardinality.
The element record retains its selected point datum.
The morphism record retains its domain, codomain, and rule.

Direct `Sets()` construction initializes this state on the new set value.
A selected functor's pure conversion supplies the same constructor data to the `Sets()` initializer on a structured source instance.
Thus an inherited set method reads set state directly on the value to which it applies.
Public `F(x)` remains a separate set image owned by the named functor.

`Sets.ObjectType` is the sole public implementation of a set.
It can use Sage, SymPy, GAP, Julia packages, Singular, Macaulay2, or several engines together.
These are private algorithm providers, not competing set implementations.

Choose an engine from the mathematical construction and the exact algorithm it supplies.
Use its native construction whenever that discharges logic which the repository would otherwise have to implement.
A single owned set can use different engines for membership, simplification, enumeration, cardinality, images, and other operations.

Typical engine contributions include:

| Construction or query | Suitable private engine contribution |
| --- | --- |
| Explicit or enumerated sets | Sage parents, enumerated sets, and exact iterators |
| Symbolic subsets and set algebra | SymPy `ConditionSet`, `Intersection`, `Union`, and `Complement` |
| Symbolic images and arithmetic progressions | SymPy `imageset`, `ImageSet`, and `Range` |
| Finite-group orbits, cosets, and conjugacy classes | GAP or Sage interfaces to GAP |
| Polynomial solution sets and algebraic loci | Singular, Macaulay2, Sage, or SymPy algorithms appropriate to the coefficient domain |
| Specialized exact algorithms exposed by a Julia package | The package's native mathematical construction |

An owned operation can compose engine results.
For example, SymPy can normalize a predicate intersection to a finite symbolic set.
Sage can then supply an owned finite enumeration.
The set implementation reconstructs one owned result from both computations.

Engine choice is private to the owning method or its private helper.
The public API has no backend argument, backend registry, engine-specific set class, or alternative method name.
Engine methods never enter the public surface automatically.

Select engines through the known semantic form of the input.
Do not probe engines by exception or attempt implementations until one succeeds.
If no applicable exact algorithm or construction theorem decides the result, return Sage `Unknown`.

Construction-owned mathematics remains authoritative.
For example, the image of an established monomorphism has the domain cardinality.
No engine must rediscover that theorem.

### SymPy set constructions

SymPy supplies mature symbolic set representations and simplification algorithms.
Use them instead of implementing local symbolic set algebra.

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

The first two results reconstruct an owned finite subset with cardinality `3`. The last result reconstructs an owned countably infinite subset with cardinality `aleph0`.

SymPy can also leave a construction unresolved:

```python
ImageSet(Lambda(n, sympy.Integer(2) * n), S.Naturals).is_finite_set
# None

imageset(Lambda(n, n ** sympy.Integer(2)), S.Naturals).is_finite_set
# None

ConditionSet(n, Eq(p(n), 0), S.Naturals).is_finite_set
# None
```

An unevaluated `ImageSet` or `ConditionSet` remains a valid private representation.
Its owned cardinality is `Unknown` unless defining data or a construction theorem supplies an exact cardinal.

SymPy sets do not supply one general `cardinality()` operation.
Reconstruct the owned cardinal from the normalized result:

- `FiniteSet` contributes its exact finite size.

- A finite `Range` contributes its exact finite size.

- An infinite `Range` contributes `aleph0`.

- A standard number set contributes its established cardinal.

- An unresolved symbolic set contributes `Unknown`.

An image receives the domain cardinality when injectivity or another theorem establishes that equality.

| Owned operation | SymPy value | Required reconstruction |
| --- | --- | --- |
| Membership | `Contains(x, X)` | Return the owned membership proposition. |
| Predicate subset | `ConditionSet(x, P(x), X)` | Return the owned subset with its monomorphism. |
| Image | `imageset(f, X)` or `ImageSet(f, X)` | Return the owned image subobject. Preserve an unevaluated image. |
| Finite normalization | `FiniteSet` | Return an owned finite set and exact finite cardinal. |
| Progression normalization | `Range` | Return an owned enumerated set and its finite cardinal or `aleph0`. |
| Set algebra | `Union`, `Intersection`, `Complement`, `ProductSet` | Return the corresponding owned construction. |
| Set equality or inclusion | symbolic set relations | Return the owned proposition; use `ask()` for its decision. |
| Cardinal calculation | normalized set type and symbolic properties | Return an exact cardinal or `Unknown`, never `None`. |
| Universal constructions | symbolic set expressions | Retain all defining morphisms and universal maps. |

The owning set method reconstructs the owned mathematical result.
See the [SymPy sets documentation](https://docs.sympy.org/latest/modules/sets.html) for the supported representations and simplifications.

## Unknown and partial algorithms

Membership, subset order, set equality, cardinal comparisons, and cardinal property methods return propositions.
Their handlers can be exact, partial, or unavailable.

The `ask()` contract is:

- return `True` after an exact positive result;

- return `False` after an exact negative result;

- return `Unknown` when available exact handlers establish neither result;

- preserve `Unknown` under three-valued Boolean operations;

- refine a property category only after exact evidence or a construction theorem.

No public propositional method returns any of these decisions.
Python `in` is the Boolean boundary.
Set and category `__contains__()` methods ask their declared membership proposition.
An `Unknown` decision fails loudly rather than being returned as `False`: `Unknown` is not `False`, and no negative mathematical result is recorded.

`Unknown` does not block construction of an honest predicate subobject, symbolic image, or universal construction.

### Equality

Every owned category owns an equality predicate for its objects, for its morphisms, and for the elements of its objects.
`__eq__` on every owned object, element, and morphism returns the applied equality predicate, and `ask(a == b)` decides it.
Identity is the first exact positive handler of every equality predicate.

The applied predicate defines `__bool__` to raise.
The mature references are SymPy `Relational.__bool__` and Sage `UnknownClass.__bool__`. Therefore `if a == b:` fails loudly, and repository code writes `ask(a == b) is True`. Containment (`in`) remains the one Boolean boundary.

`__hash__` is defined explicitly on every owned value.
Objects, morphisms, and generalized elements with nonterminal domains hash by identity.
A point hashes by its chosen datum, so two points whose equality is `True` hash equal.

For two points of one set, the exact handler compares their chosen data through the private computation boundary.
Two generalized elements with nonterminal domains compare by identity unless an exact handler for their defining maps decides equality.
For two rule-defined sets, equality is `Unknown` unless identity or a cited exact handler decides it; no handler inspects contents.
For two set maps with one finite enumerable domain, the exact handler compares images pointwise over that domain's enumeration; two maps with a rule-defined infinite domain compare by identity only and are otherwise `Unknown`.

## Acceptance conditions

The implementation satisfies this specification when the public API establishes these facts:

- every admitted morphism is total and has its stated domain and codomain;

- evaluation returns an owned codomain element;

- identity and composition use inherited morphism operations;

- the function set `Y ** X` is one canonical object, and `Mor(Sets())(X, Y)` is the discrete category on its elements;

- every chosen subset retains its monomorphism;

- every abstract subobject retains its monomorphism and canonical image;

- products retain `product_projection(i)` and universal maps;

- coproducts retain `coproduct_injection(i)` and universal maps;

- limits and colimits retain their diagrams and universal data;

- power-object operations return owned subsets and morphisms;

- countability does not create a chosen enumeration;

- `cardinality()` returns an exact cardinal or `Unknown`;

- every operation uses a mature engine construction when one supplies the required exact mathematics;

- one owned set can combine several private engines without exposing an engine choice;

- supported symbolic set operations use SymPy instead of duplicate local algorithms;

- normalized `FiniteSet` and `Range` results reconstruct their exact owned cardinalities;

- unevaluated `ConditionSet` and `ImageSet` results reconstruct valid owned sets whose cardinality is `Unknown` when no theorem decides more;

- cardinal arithmetic is defined on exact cardinals only;

- `a == b` on owned values is an applied predicate, `bool(a == b)` raises, and identity decides `ask(a == a) is True`;

- every operation specified as a predicate returns an applied proposition;

- only `ask()` returns `True`, `False`, or `Unknown` for that proposition;

- every category declares one potentially compound membership proposition;

- Python containment asks that proposition and treats `Unknown` as unproved admission;

- private engine values never cross the public boundary.

The governing policies include `POL-MATH-001` through `POL-MATH-035`, `POL-CAT-020`, `POL-CAT-027` through `POL-CAT-032`, `POL-CAT-040` through `POL-CAT-045`, `POL-CAT-086`, `POL-SET-001` through `POL-SET-036`, and `POL-KERNEL-001` through `POL-KERNEL-026`.
