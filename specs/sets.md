# Sets specification

`Sets()` owns the public algorithms for sets, set elements, and total functions.
Categories with a structure functor to `Sets()` inherit this API.

Standard set theory and category theory are assumed.
This specification fixes API ownership, constructors, algorithms, result categories, and exact failure states.

Every set operation specified as a predicate follows the interface in [Property refinement](property-refinement.md).
Applying it returns a proposition.
Only `ask()` decides that proposition as `True`, `False`, or `Unknown`.

The governing policies are `POL-MATH-034`, `POL-MATH-035`, `POL-CAT-001`, `POL-CAT-021`, `POL-CAT-028`, `POL-CAT-086`, `POL-CAT-088`, `POL-CAT-092` through `POL-CAT-095`, `POL-SET-001` through `POL-SET-036`, and `POL-API-002`, `POL-API-009`, `POL-API-010`, `POL-API-015`, and `POL-API-016`.

## Owned API classes

`Sets()` owns three implementation types:

- `Sets().ObjectType` implements set objects.

- `Sets().ElementType` implements points `t: 1 -> X`, the actual elements of `X`.

- `Sets().MorphismType` implements total functions with a domain and codomain.

An owned element is a point `t: 1 -> X`, and its parent is `X`.
A generalized element `T -> X` with nonterminal domain is an ordinary morphism in `Sets()`, not a `Sets().ElementType` value.
The same point datum can produce distinct owned elements in distinct sets.

Private representations can include Sage parents, predicates, symbolic expressions, finite collections, indexed families, tagged pairs, or universal-construction data.
No private representation becomes another public owner.

The `Sets()` subtree adds:

- membership and available iteration;

- total set maps and their morphism properties;

- cardinality;

- the set structure on inherited subobjects and images;

- the set structure on inherited exponentials;

- the set structure, predicates, cardinality cases, and private engines for inherited universal constructions.

Property subcategories add only their stated property.
They inherit all set operations.

## Sets-owned operations

`Sets()` adds the operations whose mathematics is specific to sets:

```python
X.cardinality()
Sets().Subobjects(X).from_predicate(predicate)
```

Morphism categories, fixed-object methods, universal-construction methods, and operators are inherited from `Cat().ObjectType`.
Their contract is in [Functors, `Cat`, and structural inheritance](functor.md).
`Sets()` supplies only their set-specific realizations and algorithms.

`X.cardinality()` returns an applied query with result category `Cardinal()`.
`ask(X.cardinality())` returns an owned cardinal or Sage `Unknown`.

## Canonical objects and the terminal object

`Sets()` realizes these inherited constructions, each retained by identity:

- `Sets().Initial()`, the empty set `{}`;

- `Sets().Terminal()`, the one-point set `1 = {*}`.

The coproduct `1 + 1` is the two-element set `2` used in the power object `2 ** X`.

A point of `X` is a morphism `1 -> X` from `Sets().Terminal()`. Set membership, enumeration, and cardinality use `Mor(Sets())(1, X)` through the terminal object.

## Set maps, morphism categories, and function sets

`Mor(Sets())(X, Y)` is the discrete category on the total set maps from `X` to `Y`. It exists for every pair `X, Y in Sets()`. Its inhabitation and emptiness are owned predicates.

The generic exponential construction comes from `Cat`.
Its realization in `Sets()` is the function set from `X` to `Y`.
It is a distinct owned object, and `Mor(Sets())(X, Y)` is the discrete category on its elements.

`Mor(Sets())(X, Y)(rule)` constructs a set map.
The rule can be a callable or explicit mapping as its private rule.
The constructor must establish that the rule is total and lands in `Y`.

A raw rule determines propositions stating totality and codomain closure.
`ask()` can evaluate those propositions.
Exact `True` invokes the owned morphism constructor.
Exact `False` rejects admission.
`Unknown` leaves the rule outside the set-morphism category.
Direct construction, an active assumption, exact positive evaluation, and a named mathematical construction all establish the same morphism placement.
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

The realized exponential retains the evaluation morphism.
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
The kernel refines a morphism only after an exact result, scoped hypothesis, or named theorem establishes the property.

An inverse of an isomorphism is an owned set morphism.
It satisfies both inverse equations.

## Products

The inherited product contract is specified in [Products, coproducts, and component functors](functor.md#products-coproducts-and-component-functors).
For a diagram `i |-> X_i` on `S`, `Sets()` constructs the owned set

\[
\prod_{i\in S} X_i=\{(x_i)_{i\in S}\mid x_i\in X_i\text{ for every }i\in S\}.
\]

Membership is the conjunction of the component membership propositions.
Equality is the conjunction of the component equality propositions.
`ask()` evaluates either proposition when the retained diagram and the selected set engines supply an exact algorithm.
The set implementation selects a private exact representation from the retained diagram.
The membership and equality predicates use the components obtained through the inherited projections.
The cardinality query uses the computational cases in [Cardinality and enumeration](#cardinality-and-enumeration).

## Coproducts

The inherited coproduct contract is specified in [Products, coproducts, and component functors](functor.md#products-coproducts-and-component-functors).
For a diagram `i |-> X_i` on `S`, `Sets()` constructs an owned set `Q` whose inherited injections

\[
\iota_i:X_i\longrightarrow Q
\]

are injective, have pairwise disjoint images, and have images whose union is `Q`.
Membership and equality are the owned set propositions determined by this disjoint-union structure.
The set implementation selects a private exact representation from the retained diagram.
The cardinality query uses the computational cases in [Cardinality and enumeration](#cardinality-and-enumeration).

## General limits and colimits

`Sets()` inherits `Limits(I)` and `Colimits(I)` with the complete retained-data contract in [Diagram shapes and universal constructions](functor.md#diagram-shapes-and-universal-constructions).
The specialization supplies the following set-valued realizations.

The limit of `D: I -> Sets()` is the predicate subset of the product `prod_{i in Ob(I)} D(i)` cut out by compatibility. A family's membership proposition is the conjunction of `D(u)(x_i) == x_j` over every generating morphism `u: i -> j` of `I`. `ask()` decides this proposition when `I` is finitely presented and every generating equality decides; otherwise it returns `Unknown`.

The colimit of `D` is the quotient of the coproduct `coprod_i D(i)` by the equivalence relation generated by `(i, x) ~ (j, D(u)(x))`.
Its element equality is an owned predicate.
For `I = omega`, the exact handler decides `True` when two representatives agree at the larger of their two indices under the transition maps and returns `Unknown` otherwise; for every other infinite shape it returns `Unknown`.

## Subobjects, images, and power objects

The inherited fixed-object method is specified in [Fixed-object construction categories](functor.md#fixed-object-construction-categories).
Its specialization to `Sets()` identifies subobjects with subsets of `X` together with their inclusion monomorphisms.
`Sets().Subobjects(X).from_predicate(predicate)` constructs the selected subset and its monomorphism into `X`.
It lifts no additional structure: when a poset is presented as `(X, R)`, this construction returns a set subobject (`POL-LEAF-060`).
The predicate returns the membership proposition for a candidate element.
`ask()` can evaluate that proposition as `True`, `False`, or `Unknown`.

The inherited subobject retains its monomorphism.
Its codomain is the containing set.
Its placement in `Sets()` supplies cardinality and the other set operations.
The set-specific characteristic morphism maps the selected subset to `1 in 2` and its complement to `0 in 2`.

`f.image()` constructs an owned subobject of `f.codomain()`. It does not require source enumeration.
Image membership remains a proposition when no handler can decide it.

`2 ** X`, with `2 = 1 + 1`, constructs the power object of `X`. It is the function set from `X` to `2`.
Its points are characteristic morphisms and therefore correspond to the objects of `Sets().Subobjects(X)`.
Set inclusion is an applied proposition.
The set operations on these subobjects construct owned set subobjects.

## Finite and fixed-cardinality subsets

Let `U_X: Sets().Subobjects(X) -> Sets()` be the inherited varying-object functor.
The inverse image of `Sets().Finite()` along `U_X` is:

```python
Sets().Subobjects(X).Finite()
```

Its objects are the finite subobjects of `X`.
The parameterized property category `Sets().OfCardinality(k)` has containment predicate `A.cardinality() == k`.
The inherited narrowing `Sets().Subobjects(X).OfCardinality(k)` contains the subobjects of cardinality `k`.

If `X` has a chosen enumeration, these constructions can retain a derived enumeration isomorphism.
Countability alone does not select one.

Their category-owned implementations register exact cardinality cases from cardinal arithmetic.
They do not enumerate an infinite base set.

## Cardinality and enumeration

The cardinal and ordinal APIs are specified in [cardinality.md](cardinality.md).

The set axioms generate these public applications on `Sets().ObjectType`:

| Property subcategory | Generated application |
| --- | --- |
| `Sets().Empty()` | `is_empty()` |
| `Sets().Inhabited()` | `is_inhabited()` |
| `Sets().Finite()` | `is_finite()` |
| `Sets().Infinite()` | `is_infinite()` |
| `Sets().Countable()` | `is_countable()` |
| `Sets().Uncountable()` | `is_uncountable()` |

Each method returns its property subcategory's containment proposition.
Every category whose compiled object class inherits `Sets().ObjectType` receives these methods.
The kernel implements `__contains__()` by calling `ask()` on that proposition.
An `Unknown` decision fails loudly there, since a bool cannot carry it; ask the proposition when the undecided case must be handled.
A trusted category constructor or named mathematical construction places a set directly in the property category.

### Cardinality query

The cardinality operation constructs an applied query:

```python
X.cardinality()  # applied query with result category Cardinal()
```

`ask(X.cardinality())` returns an object of `Cardinal()` or the Sage `Unknown` singleton.

A cardinal is an exact value: a finite cardinal, `Aleph.on_object(alpha)`, `2 ** Aleph.on_object(Ordinals().zero())`, or another value formed by exact cardinal arithmetic.
There is no placeholder cardinal, no unknown cardinal kind, and no symbolic "cardinality of X" value.

Cardinal arithmetic, equality, and order are defined on cardinals only.
Cardinals implement no `Unknown` handling.

A set construction registers exact evaluation cases for the category-owned cardinality query.
Each case uses the index set, the selected presentation's diagram, its codomain placement (`Sets().Finite()`, `Sets().Countable()`, `Sets().Uncountable()`), and any retained constant diagram.
For a finite chosen enumeration, it obtains each factor query from the selected product cone `p` by applying `p.diagram().on_object(i).cardinality()`.
Each case cites the theorem that decides it.
The product cases are: a finite index with every factor exact gives the exact product; a finite index with an empty factor gives `0`; the constant diagram at `X` over `S` gives `(#X) ** (#S)`; an infinite index with codomain `Sets().Uncountable()` places the product in `Sets().Uncountable()`; a finite index with codomain `Sets().Countable()` places the product in `Sets().Countable()`. When no case applies, `ask()` returns `Unknown`. Coproducts use the dual sum cases.

If SymPy normalizes a subset to `FiniteSet(1, 2, 3)`, its cardinality is `3`.

If the image morphism is monic, the construction theorem gives

\[
\lvert\operatorname{im}(f)\rvert=\lvert\operatorname{dom}(f)\rvert.
\]

If neither route applies, `ask(X.cardinality())` returns `Unknown`.

Each cardinal property subcategory owns one containment predicate.
The kernel-derived `X.is_finite()`, `X.is_countable()`, and related property applications return those propositions.
`ask()` decides them from category placement, active assumptions, and the routes the owning implementation registers: a known cardinality decides finiteness and countability, and a `Sets()` construction registers the case routes that external mathematics supplies for it.
`assume(X.is_finite())` and the property subcategory constructors `Sets().Finite()`, `Sets().Countable()`, and `Sets().Uncountable()` are the positive routes.

Countability does not select an enumeration.
A chosen enumeration retains an owned index subobject `I -> NN` and an isomorphism `e: I -> X`.
The isomorphism is the defining structure.
Use `e(n)` for the element at `n` and `e.inverse()(x)` for the index of `x`.

## Ordered sets

The ordered-set API is specified in [ordered-sets.md](ordered-sets.md).

A partial order is chosen structure on a set.
It is not a property of the bare set.
Totality is a property of that chosen partial order.
Cardinality and enumeration remain independent structures.

## Finitely supported function sets

For a pointed set `(X, x0)` and index set `S`, construct (X^{(S)}) as the predicate subobject of `X ** S` whose functions have finite support relative to `x0`.
The generic subobject retains its monomorphism into the function set.
Its placement in `Sets()` supplies cardinality and the complete set surface.
The category-owned implementation registers applicable cardinal formulas from the retained construction data.

## Private computation engines

Each compiled set class owns one private state record.
The object record retains its membership rule and cardinality.
The element record retains its selected point datum.
The morphism record retains its domain, codomain, and rule.

Direct `Sets()` construction initializes this state on the new set value.
A selected structure functor states which `Sets().ObjectType` constructor consumes its converted source construction data.
Thus an inherited set method reads set state directly on the value to which it applies.
Public `F(x)` remains a separate set image owned by the named functor.

`Sets().ObjectType` is the sole public implementation of a set.
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
If no applicable exact algorithm or construction theorem determines a query, leave its application unresolved so `ask()` returns Sage `Unknown`.

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

Membership, subset order, set equality, cardinal comparisons, and generated cardinal-property applications return propositions.
Their handlers can be exact, partial, or unavailable.

The `ask()` contract is:

- return `True` after an exact positive result;

- return `False` after an exact negative result;

- return `Unknown` when available exact handlers establish neither result;

- compose propositions before evaluation and preserve an unresolved result;

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
The mature reference is SymPy `Relational.__bool__`.
Therefore `if a == b:` fails loudly.
Repository code asks the proposition, requires a decided result where necessary, and then branches on that decision.
Containment (`in`) remains the one Python Boolean boundary.

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

- every subset retains its monomorphism;

- every abstract subobject retains its monomorphism and chosen image;

- products retain `product_projection(i)` and universal maps;

- coproducts retain `coproduct_injection(i)` and universal maps;

- limits and colimits retain their diagrams and universal data;

- power-object operations return owned subsets and morphisms;

- countability does not create a chosen enumeration;

- `cardinality()` returns an applied query with result category `Cardinal()`;

- `ask(X.cardinality())` returns an owned cardinal or `Unknown`;

- every operation uses a mature engine construction when one supplies the required exact mathematics;

- one owned set can combine several private engines without exposing an engine choice;

- supported symbolic set operations use SymPy instead of duplicate local algorithms;

- normalized `FiniteSet` and `Range` results reconstruct their exact owned cardinalities;

- unevaluated `ConditionSet` and `ImageSet` results reconstruct valid owned sets whose cardinality query remains unresolved when no theorem decides more;

- cardinal arithmetic is defined on exact cardinals only;

- `a == b` on owned values is an applied predicate, `bool(a == b)` raises, and identity makes `ask(a == a)` return `True`;

- every operation specified as a predicate returns an applied proposition;

- only `ask()` returns `True`, `False`, or `Unknown` for that proposition;

- every category declares one potentially compound membership proposition;

- Python containment asks that proposition and treats `Unknown` as unproved admission;

- private engine values never cross the public boundary.

The governing policies include `POL-MATH-001` through `POL-MATH-035`, `POL-CAT-020`, `POL-CAT-027` through `POL-CAT-032`, `POL-CAT-040` through `POL-CAT-045`, `POL-CAT-086`, `POL-SET-001` through `POL-SET-036`, and `POL-KERNEL-001` through `POL-KERNEL-026`.
