# Functors, `Cat`, and structural inheritance

## Contents

- [Kernel ownership](#kernel-ownership)
- [Functors as morphisms of `Cat`](#functors-as-morphisms-of-cat)
- [The `Mor(n, C)` tower](#the-morn-c-tower)
- [Canonical objects of `Cat`](#canonical-objects-of-cat)
- [Functor property subcategories](#functor-property-subcategories)
- [Property resolution](#property-resolution)
- [Inclusion functors](#inclusion-functors)
- [Structural inheritance](#structural-inheritance)
- [Point categories and point functors](#point-categories-and-point-functors)
- [Functor construction and presentation data](#functor-construction-and-presentation-data)
- [Products, coproducts, and component functors](#products-coproducts-and-component-functors)
- [Diagram shapes and universal constructions](#diagram-shapes-and-universal-constructions)
- [Slices and coslices](#slices-and-coslices)
- [Examples](#examples)
- [Compiler contract](#compiler-contract)
- [Mathlib correspondence](#mathlib-correspondence)
- [Acceptance conditions](#acceptance-conditions)

## Kernel ownership

The kernel owns `Cat`, the category of categories. Every category in this repository is
an object of `Cat` and uses its implementation type:

```python
Category = Cat().ObjectType
```

Thus `Sets()`, `Mor(C)`, and every property subcategory are instances of
`Cat().ObjectType`. They do not form a second Python category hierarchy.

`Cat` owns the same role types as every other category:

- `Cat().ObjectType` implements categories;
- `Cat().MorphismType` implements functors;
- `Cat().ElementType` is the role "generalized element of a category", a functor
  `T -> C`; its stage-`1` points are the objects of `C` and its stage-`[1]` points are
  the morphisms; every `C.ObjectType` refines it at stage `1`, every `C.MorphismType`
  at stage `[1]`;
- `Cat()(...)` constructs categories;
- `Fun = Mor(Cat())` constructs the category whose objects are functors.

The kernel also supplies the uniform categorical constructions, defined once at the
`Cat()` level and applicable to every category:

```python
Mor(C)                     # the category of morphisms of C
Mor(C)(X, Y)               # the full subcategory on morphisms X -> Y
Mor(C).Endomorphisms()     # morphisms with equal domain and codomain
Mor(C).Automorphisms()     # Mor(C).Endomorphisms().Isomorphisms()
```

For `A, B in C`, endpoint application selects one cached category per pair:

```python
H = Mor(C)(A, B)
```

There are two call forms on categories. `K(data)` constructs an object of `K`.
`Mor(K)(A, B)(data)` constructs a morphism `A -> B`. No spelling owns a parallel
morphism construction.

## Functors as morphisms of `Cat`

A functor is a morphism in `Cat`. Define `Fun = Mor(Cat())`. Therefore, every functor is
an object of `Fun`:

```python
Fun = Mor(Cat())
F = Fun(C, D)(on_object, on_morphism)
```

`Fun(C, D)(on_object, on_morphism)` requires both actions. The inherited
`Cat().MorphismType` surface supplies:

```python
F.domain()       # C
F.codomain()     # D
F.on_object(X)   # an object of D
F.on_morphism(f) # a morphism of D
```

The maps preserve identities and composition:

\[
F(1_X)=1_{F(X)},\qquad F(g\circ f)=F(g)\circ F(f).
\]

Every generalized element is represented by its defining morphism. `F.on_element(t)`
applies `F.on_morphism` to that morphism. The functor stores no element callback,
element functor, or element capability.

For fixed `C, D in Cat()`, the functor category is endpoint application to
`Mor(Cat())`:

```python
Fun(C, D) is Mor(Cat())(C, D)
```

Its objects are functors `C -> D`. Its morphisms are natural transformations. Natural
isomorphisms are the objects of `Mor(Fun(C, D)).Isomorphisms()`.

`Fun(C, D)` is the full subcategory of `Fun` on functors with domain `C` and codomain
`D`. It is a genuine full subcategory because a 2-morphism connects parallel 1-morphisms
only.

A natural transformation `eta: F => G` is constructed as
`Mor(Fun(C, D))(F, G)(assignment)`. The assignment is a rule `X |-> eta_X` on the
objects of `C`, returning a morphism `F(X) -> G(X)` of `D`. It is never a table.
Naturality is trusted.

## The `Mor(n, C)` tower

For every category `C` and every `n >= 0`, `Mor(n, C)` is the category whose objects are
the `n`-morphisms of `C` and whose morphisms are the `(n+1)`-morphisms of `C`:

- `Mor(0, C) = C`;
- `Mor(C) = Mor(1, C)`;
- `Mor(n+1, C) = Mor(Mor(n, C))`.

`C.ObjectType` implements the objects of `Mor(0, C)`. `C.MorphismType` implements the
objects of `Mor(1, C)`. Therefore `Mor(n, C).ObjectType` is `Mor(n-1, C).MorphismType`:
one implementation type, one value, two category placements.

For a 1-category `C`, every 2-morphism is an identity, so `Mor(C)` is discrete. `Cat()`
is a strict 2-category: categories are the objects of `Mor(0, Cat())`, functors are the
objects of `Mor(1, Cat())`, and natural transformations are the objects of
`Mor(2, Cat())` and the morphisms of `Fun`.

Applying `Mor(C)` to endpoints `A, B` selects the full subcategory of `Mor(C)` on the
morphisms with domain `A` and codomain `B`. One cached object exists per `(A, B)`. This
is distinct from `Mor(Mor(C))(f, g)`, the category between two objects of `Mor(C)`.

The construction is uniform. In particular:

- objects of `Mor(Sets())` are set maps, and `Mor(Sets())(X, Y)` is discrete on the maps
  `X -> Y`;
- objects of `Mor(Cat())` are functors;
- objects of `Mor(Fun(C, D))` are natural transformations.

The category whose objects are the morphisms of `C` and whose morphisms are commuting
squares is not a primitive. It is the functor category `Fun([1], C)` from the walking
arrow `[1]`. Its evaluation functors `ev_0, ev_1: Fun([1], C) -> C` supply the domain
and codomain projections. In general, evaluation at `i in I` is the construction-named
functor `Fun(I, C) -> C`.

The related property categories use the same mechanism:

```python
Mor(C).Monomorphisms()
Mor(C).Epimorphisms()
Mor(C).Isomorphisms()
Mor(C).Automorphisms()
```

Each is a property subcategory of an owned morphism category. Each property has its
owned predicate, trusted constructor, assumption route, implication rules, and optional
computational routes. Fixed endpoints use the same dispatch for every property
subcategory `P` of `Mor(K)`: `P(A, B)` is `Mor(K)(A, B).P()`, one cached object.

## Canonical objects of `Cat`

`Cat()` owns these objects, each constructed once and retained by identity:

- `Cat().Empty()`: the empty category;
- `Cat().Terminal()`, written `1` and equal to `[0]`;
- `Cat().Simplex(n)`, written `[n]`: the poset `0 < 1 < ... < n` as a category, for
  `n >= 0`; `[1]` is the walking arrow, `[2]` the walking commutative triangle;
- `Cat().Boundary(n)`, written `d[n]`: the free category on the graph of the boundary of
  the `n`-simplex; `d[2]` is the walking triangle with no commutation relation;
- `Cat().Horn(n, k)`, written `L(n, k)`: the free category on the `k`-th horn graph of
  the `n`-simplex; `L(2, 0)` is the walking span and `L(2, 2)` the walking cospan;
  `L(2, 1)`, the free category on `0 -> 1 -> 2`, contains the composite `0 -> 2` and is
  the walking composable pair `[2]`, so `Cat().Horn(2, 1) is Cat().Simplex(2)`;
- `Cat().WalkingIsomorphism()`: two objects and two mutually inverse morphisms;
- `Cat().WalkingParallelPair()`: two objects and two parallel morphisms;
- `Cat().Point(X)`, written `{X}`: the one-object category on a distinguished object
  `X`, one per `X`; see
  [Point categories and point functors](#point-categories-and-point-functors).

Two calls return one object by identity. No construction creates a second terminal
object, simplex, or walking structure.

Stages: `G_Sets = Sets().Terminal()`; `G_Cat = 1` for objects, with morphism stage `[1]`.

## Functor property subcategories

Functor properties are property subcategories of `Fun`:

```python
FullFunctors = Fun.Full()
FaithfulFunctors = Fun.Faithful()
FullyFaithfulFunctors = Fun.FullyFaithful()
EssentiallySurjectiveFunctors = Fun.EssentiallySurjective()
EquivalenceFunctors = Fun.Equivalences()
```

Fixed endpoints commute with property refinement. For example:

```python
Fun(C, D).Full() is Fun.Full()(C, D)
Fun(C, D).Faithful() is Fun.Faithful()(C, D)
Fun(C, D).FullyFaithful() is Fun.FullyFaithful()(C, D)
```

Each identity denotes one cached property subcategory. A constructor called through it
returns a functor with endpoints `C, D` and the selected trusted property.

Their predicates have the standard public form:

```python
F.is_full()
F.is_faithful()
F.is_fully_faithful()
F.is_essentially_surjective()
F.is_equivalence()
```

Each call returns an applied `Predicate`. It does not return a Boolean.

For `F: C -> D`:

- `Full(F)` states that every morphism `F(X) -> F(Y)` has a preimage under
  `F.on_morphism()`;
- `Faithful(F)` states that each map on morphisms is injective;
- `FullyFaithful(F)` is the conjunction of fullness and faithfulness;
- `EssentiallySurjective(F)` states that every object of `D` is isomorphic to an image
  of an object of `C`;
- `Equivalence(F)` states that `F` is fully faithful and essentially surjective.

These definitions introduce no selected witnesses. A separate construction can select
a preimage morphism, inverse functor, unit, or counit when an operation requires that
data.

The kernel records the categorical implications:

```text
FullyFaithful(F) implies Full(F)
FullyFaithful(F) implies Faithful(F)
Full(F) and Faithful(F) imply FullyFaithful(F)
Equivalence(F) implies FullyFaithful(F)
Equivalence(F) implies EssentiallySurjective(F)
```

These implications induce the corresponding inclusions between property subcategories.

## Property resolution

Functor properties use the general `Predicate`, `ask()`, and property-refinement
framework. They have no separate evidence or decision system.

An existing functor can enter a property category by direct construction:

```python
F = Fun(C, D)(on_object, on_morphism)
F = Fun(C, D).Full()(F)
```

This is the property category's trusted constructor. The code writer uses external
mathematics to select `Fun(C, D).Full()`. The constructor records that assertion and
refines the same owned functor. It does not prove, certify, or check fullness.

An interactive assumption uses the same predicate and refinement:

```python
F = Fun(C, D)(on_object, on_morphism)
assume(F.is_full())
```

A code writer who knows a property from the defining construction places the result
directly in the corresponding property category. For example, the inclusion of a full
subcategory is constructed in `Fun(C, D).FullyFaithful()`.

Put a citation on the construction line or in its immediate source documentation when
the property uses a nontrivial external theorem. The citation supports mathematical
audit. It is not runtime data and the constructor does not inspect it.

The functor-property categories register no computational routes. Therefore:

```python
ask(F.is_full())
```

uses category placement, active assumptions, and categorical implications. It returns
`Unknown` when none establishes the proposition.

This rule is specific to categorical functor properties. Other owned predicates, such
as injectivity of a set map on a declared semantic domain, can register exact
computational routes.

## Inclusion functors

An inclusion `S -> T` is an object of the fixed-endpoint category `Fun(S, T)`. That
category owns its constructor. A general subcategory inclusion is faithful, so construct
it in the established property category:

```python
iota = Fun(S, T).Faithful().inclusion()
```

The leaf writer states that `S` is a subcategory of `T` by choosing this constructor.
The kernel does not compute that relation from Python inheritance or shared storage.

For a full property subcategory `C.P()`, the canonical inclusion is:

```python
iota = Fun(C.P(), C).FullyFaithful().inclusion()
```

The defining object predicate selects the objects. The morphism categories
`Mor(C)(A, B)`, identities, and composition are inherited from `C`. The leaf records
this theorem by constructing directly in `Fun(C.P(), C).FullyFaithful()`.

Suppose predicates `P` and `Q` on `C` satisfy

\[
P(X)\Longrightarrow Q(X).
\]

The kernel records the implication as an inclusion of property subcategories:

```python
iota = Fun(C.P(), C.Q()).FullyFaithful().inclusion()
```

The source property is stronger. The target property is weaker. The implication belongs
to the property relation. Its fixed-endpoint functor category owns the inclusion
constructor.

A wide subcategory retains every object and restricts morphisms by a multiplicative
morphism predicate. Its inclusion is faithful by construction. A general subcategory
inclusion is also faithful. Neither becomes full unless its mathematical definition
establishes fullness.

## Structural inheritance

`structure_functors()` is a repository compiler declaration. It is not an additional
kind of functor and is not part of Mathlib's functor theory.

Every entry is an ordinary owned object of `Fun`. Its mathematical existence and
properties come first. For example, finite sets are a full subcategory of sets, so their
inclusion functor exists independently of method compilation.

A category selects an immediate functor only when the functor states the mathematical
change of structure that supplies inherited operations:

```python
class FiniteSetsCategory(Category):
    def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
        return (Fun(self, Sets()).FullyFaithful().inclusion(),)
```

The leaf explicitly constructs the inclusion and records full faithfulness through the
selected property category. The tuple tells the compiler to include the compiled roles
owned by `Sets()` through that functor.

The categories `Fun(self, D)` can contain many other functors. Their existence does not
affect the compiled public surface. Selection changes compiler behavior only. It does
not change a functor's mathematical definition.

Each category lists only immediate selected functors. The kernel obtains longer routes
by composition and applies [resolution.md](resolution.md) to diamonds.

### Compiled roles

A local declaration and the compiled role built from it are distinct classes. The
declaration owns the category's new methods. `C.ObjectType`, `C.ElementType`, and
`C.MorphismType` are the compiled roles, and only they are public.

The bases of a compiled role are the compiled roles of the selected target categories,
in the controlled order of [resolution.md](resolution.md). A role that reaches no other
role stands on the kernel role class of its role: `Category` for the category role,
otherwise the kernel base of objects, elements, or morphisms.

A declaration is not a base. The kernel copies its class body onto the compiled role and
drops the declaration's own Python bases. A method declared with zero-argument `super()`
closes over `__class__`, which Python bound to the declaration; the kernel rebinds that
closure to the compiled role, so `super()` enters the compiled chain.

One declaration is an exception, because it is the kernel role class the category role
ends on. `Cat().ObjectType` stands on `Category`, which is the class every category is an
instance of: a category is built from its own hand-written `Category` subclass, never
from a compiled role, and only inheritance lets those subclasses override `Category`'s
methods. A chain end is inherited, never copied.

The rule is what makes the result linearizable. The controlled order ranks compiled
roles. A declaration left in the bases is ranked by nothing, so Python places it wherever
each separate class construction allows; two constructions then rank one pair of
declarations opposite ways, and a role reaching both has no method resolution order at
all. With declarations out of the bases, every class in a compiled role's method
resolution order is a compiled role or a kernel role class.

An element of `X in C` is a generalized element `t: T -> X`, an object of
`C.SliceOver(X)`. `t.stage()` is `T` and `t.parent()` is its codomain `X`. Every
`F: C -> D` induces `F/X: C/X -> D/F(X)`, sending `t` to `F(t): F(T) -> F(X)` through
`F.on_morphism`; this action requires no additional functor data.

A category may choose a classical stage `G_C`: `1` for `Sets()`; `Cat()` uses `1` for
objects and `[1]` for morphisms. A classical element of `X` is a generalized element
whose stage is exactly `G_C`. A selected structural functor that exposes the target's
classical element methods retains a stage comparison `G_D -> F(G_C)`. Precomposition
gives `G_D -> F(G_C) -> F(X)`, a classical element of `F(X)`; this forward direction is
the only one the kernel uses.

## Point categories and point functors

For a distinguished mathematical object `X`, `Cat().Point(X)`, written `{X}`, is the
one-object category whose sole object is `X` and whose sole morphism is `1_X`. It is an
object of `Cat()`, retained once per `X`, and it owns the declarations specific to `X`
(`POL-CAT-083`).

A **point functor** of `X` is the inclusion of `{X}` into a category `D` that has `X`
among its objects:

```python
iota = Fun(Cat().Point(X), D).Faithful().inclusion()
```

`{X}` has one hom category, so every functor out of it is faithful. A point functor is
full exactly when `X` has no nonidentity endomorphism in `D`; a construction that
establishes this states it by building the functor in `Fun({X}, D).FullyFaithful()`.

The endpoint pair selects the category `Fun({X}, D)`, as for every other functor. The
distinguished object `X` is the construction data. `X` retains the category placement it
already has; each point functor states one further placement of `X` as an object of `D`.

`{X}` selects its point functors by the ordinary declaration:

```python
# Cat().Point(X)
def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
    return (Fun(self, D).Faithful().inclusion(),)
```

A point functor is a selected structural functor under exactly this declaration and
under no other. Like every entry, it contributes its compiled roles and inherited public
methods through selection alone (`POL-FUN-003`), it is an ordinary object of `Fun`, and its
generalized-element action is derived from its morphism action (`POL-FUN-002`). The
compiler reaches it through composition in `Cat` with the rest of the structural graph.

### The level shift

Take the distinguished object to be a category `C`. Then `{C}` has one object at the
`Cat()` level, while `C` has its own objects and morphisms one level below. The compiled
surface follows that difference from `Cat().ElementType`, which is already the role
"generalized element of a category": a functor `T -> C`, refined by `C.ObjectType` at
stage `1` and by `C.MorphismType` at stage `[1]`.

A selected point functor `{C} -> D` therefore compiles as:

| Surface of `D` | Surface it supplies |
| --- | --- |
| `D.ObjectType` | the category `C` itself, a `Cat().ObjectType` value |
| `D.ElementType` at stage `1` | `C.ObjectType`, the objects of `C` |
| `D.ElementType` at stage `[1]` | `C.MorphismType`, the morphisms of `C` |
| `D.MorphismType` | `{C}.MorphismType`, whose sole value is `1_C` |

The shift is the stage clause of `Cat().ElementType` applied to one object. It adds no
second inheritance mechanism, no route normalization, and no propagation registry. `C`
remains an object of `Cat()`, `{C}` remains a distinct object of `Cat()`, and
`C.structure_functors()` continues to state the structure of `C` as a category.

### Ordinals as a semiring

An ordinal is an object of `Ordinals()` ([ordinals.md](ordinals.md)). The commutative
semiring of ordinals under the Hessenberg operations is the point functor of
`Ordinals()` into `Semirings()`:

```python
# Cat().Point(Ordinals())
def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
    return (Fun(self, Semirings()).Faithful().inclusion(),)
```

`Semirings()` declares `zero()` and `one()` on its object surface and `+` and `*` on its
element surface ([magmas-monoids-semirings.md](magmas-monoids-semirings.md)). The level
shift places each one level down:

```python
Ordinals().zero()          # the object surface, on the category
Ordinals().one()

alpha + beta               # the element surface at stage 1, on objects of Ordinals()
alpha * beta
```

At stage `[1]` the same element surface acts on the morphisms of `Ordinals()`, which is
the functorial action of the natural sum and natural product.

## Functor construction and presentation data

`Fun(Source, Target)` owns construction of functors with those endpoints. The endpoint
pair selects that category. It does not select an object of it.

Construct a functor from its complete actions:

```python
F = Fun(Source, Target)(on_object, on_morphism)
```

When the defining mathematics establishes faithfulness, construct it in that property
category:

```python
F = Fun(Source, Target).Faithful()(on_object, on_morphism)
```

A category presentation can contain several projections or evaluations. Its constructor
creates each one through the applicable `Fun(Source, Target)` category. The presentation
then retains those distinct functor objects as defining data.

### Construction-named functors

There is no generic functor selected by the instruction to “forget structure.” The
source and target select only `Fun(Source, Target)`. They do not select one of its
objects. A category presentation can expose several valid maps, and an equivalent
presentation can expose different immediate maps.

For example, a lattice presentation `(M, b)` has one projection to `M` and another to
`b`. A module presentation by an action morphism has the projections and evaluations
of its chosen action-category construction. The kernel cannot recover a preferred map
from tuple positions, field names, or a supposed underlying object.

Each public functor must name its construction. The fundamental cases are:

| Construction | Functor or morphism supplied |
| --- | --- |
| subcategory or property subcategory | its specified inclusion |
| product category | each `product_projection(i)` |
| coproduct category | each `coproduct_injection(i)` |
| functor category `Fun(I, C)` | each evaluation `ev_i: Fun(I, C) -> C`; for `Fun([1], C)`, `ev_0` and `ev_1` |
| slice or coslice presentation | its pullback projections; the varying object is the composite with `ev_0` or `ev_1` |
| Grothendieck fibration | its projection and specified cartesian lifts |
| Grothendieck opfibration | its projection and specified cocartesian lifts |
| base change | the functor supplied by pullback, pushforward, or the stated adjunction |
| left or right Kan extension | the extended functor and its universal natural transformation |
| composite construction | the ordinary composite of the supplied functors |

The dual of a Grothendieck fibration is an opfibration. It is also called a cofibered
category. Use “cofibration” only when a cited source uses that synonym. In other
contexts, a cofibration is a class of morphisms and is a different notion.

Mathlib's `ConcreteCategory.forget` is part of a concrete-category structure. Its
`HasForget₂.forget₂` also carries a chosen functor as extra structure. These definitions
do not derive a functor from its endpoints. This repository records the exact
construction instead of defining an unnamed default.

### Identity and composition

`Fun(C, C).Equivalences().identity()` constructs the identity functor on `C`. Functor
composition uses the composition of morphisms owned by `Cat`.

### Inclusions

`Fun(S, T).Faithful().inclusion()` constructs an established subcategory inclusion.
Use `Fun(S, T).FullyFaithful().inclusion()` when `S` is full in `T`.

### Induced functors

A categorical construction can act on a functor. The result is another object of
`Fun`. Examples include `Fun([1], -)` maps, product functors, comma-category
maps, diagram postcomposition, restrictions, inverse images, and lifts.

The construction owner supplies the induced object and morphism maps. It also supplies
any natural transformations or natural isomorphisms that compare composites.

For `K: C -> D` and `F: C -> E`, a left Kan extension supplies a functor
`Lan_K(F): D -> E` and a unit natural transformation

\[
F\Longrightarrow Lan_K(F)\circ K.
\]

A right Kan extension supplies a functor `Ran_K(F): D -> E` and a counit natural
transformation

\[
Ran_K(F)\circ K\Longrightarrow F.
\]

Their universal properties induce further natural transformations. Each such
transformation is a morphism in a fixed-endpoint functor category. The Kan extension
construction owns these morphisms. A later structural route uses their functor
components and ordinary composition.

### Essential images

For `F: C -> D`, `F.essential_image()` is the full property subcategory of `D` on
objects isomorphic to `F(X)` for some `X in C`. Its inclusion into `D` is fully faithful
by construction. The original functor factors through this category.

A universal-construction presentation category has more data. For example,
`C.Products()` retains the input diagram, apex, projections, and universal maps. Its
structural apex functor lands in `C`. The essential image of the product functor records
only which objects are isomorphic to product apexes.

## Products, coproducts, and component functors

The generic product and coproduct constructions apply to `Cat()` itself. For a sequence
of categories, construct:

```python
P = Cat().Products()((C_0, ..., C_n))
Q = Cat().Coproducts()((C_0, ..., C_n))
```

Their category-owned public functors are:

```python
P.product_projection(i)   # an object of Fun(P, C_i)
Q.coproduct_injection(i)  # an object of Fun(C_i, Q)
```

The index is an `int` in the supplied sequence. These methods come from
`Cat().Products().ObjectType` and `Cat().Coproducts().ObjectType`. They return
`Cat().MorphismType` values.

Let `j: S -> P` present `S` as a subcategory of the product category `P`. Then `S` is an
object of `Cat().Products().Subobjects()`. Its component functor is

\[
S.\operatorname{product\_projection}(i)=\pi_i\circ j:S\longrightarrow C_i.
\]

Thus every subcategory of a sequence product receives all component functors. The
subobject-of-product construction owns this rule. A leaf supplies its presentation and
selects the required component functors in `structure_functors()`.

A generic component functor need not be faithful or full. A specialized category
construction places it in a functor-property subcategory only when its defining theorem
establishes that property.

Dually, every sequence coproduct category retains all injections. Universal maps out of
the coproduct use the component functors supplied by its defining cocone.

The binary operators are the two-term cases. For categories `C` and `D`, `C * D` is the
product category and `C + D` is the coproduct category.

`Fun([1], C)` retains its evaluation functors:

```python
ev_0: Fun([1], C) -> C   # the domain of a morphism
ev_1: Fun([1], C) -> C   # the codomain of a morphism
```

The generic pullback construction is `C.Limits(L(2, 2))` (see
[Diagram shapes and universal constructions](#diagram-shapes-and-universal-constructions)).
Its legs are the retained projections. The same rule handles repeated codomains.

## Diagram shapes and universal constructions

A shape is an object of `Cat()`. A diagram of shape `I` in `C` is an object of
`Fun(I, C)`, constructed from an object rule and a morphism rule like every functor.

The kernel supplies these shape constructors:

- `Discrete(S)` for `S in Sets()`: the discrete category on `S`; `Discrete` is a functor
  `Sets() -> Cat()`;
- the canonical objects of `Cat` above;
- `Thin(P)` for a preordered set `P`: the thin category of `P`; `omega = Thin(NN)` with
  its natural order is the sequential shape;
- finite presented shapes: a finite set of objects, a finite set of generating
  morphisms, and a finite set of relations between composable words.

A discrete diagram needs only its object rule `i |-> X_i`. The rule is an assignment on
`S`; it never enumerates `S`. A Python sequence `(X_0, ..., X_n)` is the convenience form
and denotes the diagram over `Discrete([n])`.

`C.Products()(diagram)` constructs the apex with `product_projection(i)` indexed by
`i in S` and the universal map. `C.Coproducts()` is dual with `coproduct_injection(i)`.
`X * Y` is `C.Products()((X, Y))`.

`C.Limits(I)` and `C.Colimits(I)` are the general families for one supplied shape `I`.
The named conveniences are instances:

```python
C.Pullbacks()    is C.Limits(L(2, 2))
C.Pushouts()     is C.Colimits(L(2, 0))
C.Equalizers()   is C.Limits(WalkingParallelPair)
C.Coequalizers() is C.Colimits(WalkingParallelPair)
```

`C.Limits(I)` exists as a construction category for every supplied shape `I` without
asserting that `C` has `I`-limits. Constructing an object of it requires an owned limit
construction of `C` for that shape, supplied universal data (an apex with its cone and
mediator rule), or an exact engine construction on a declared semantic domain.

## Slices and coslices

`C.SliceOver(x)` is the pullback in `Cat()` of `ev_1: Fun([1], C) -> C` along
`x: 1 -> C`. `C.CosliceUnder(x)` is the pullback of `ev_0` along `x`. A comma category
`(F, G)` for `F: A -> C`, `G: B -> C` is the pullback of
`(ev_0, ev_1): Fun([1], C) -> C * C` along `F * G`. Each retains its pullback
projections. The varying object is the composite with `ev_0` or `ev_1`.

For the slice over `x`, an object is `(X, f: X -> x)`. The pullback projection to
`Fun([1], C)` returns the defining morphism `f`; composing it with `ev_0` gives the
varying object `X`, and composing it with `ev_1` gives the constant object `x`.

For the coslice under `x`, an object is `(X, f: x -> X)`. Composing the projection to
`Fun([1], C)` with `ev_1` gives the varying object `X`; composing it with `ev_0` gives
the constant object `x`.

Two distinct functors carry distinct lift data:

- the codomain evaluation `ev_1: Fun([1], C) -> C` is a fibration when `C` has
  pullbacks; the cartesian lift of `f: y -> x` at `p: z -> x` is the pullback
  `z *_x y -> y`, retained with both pullback projections (nLab "codomain fibration");
- the fixed slice projection `C.SliceOver(x) -> C` is the category of elements of
  `Mor(C)(-, x)` and a discrete fibration for every `C`; the cartesian lift of
  `f: y -> z` at `(z, p: z -> x)` is `f: (y, p compose f) -> (z, p)`, by precomposition,
  with no pullback and no hypothesis on `C` (nLab "discrete fibration").

The fiber of `ev_1` over `x` is `C.SliceOver(x)`. The total category `Fun([1], C)` and
its fiber are distinct retained objects with distinct lifts. Dually, `ev_0` is an
opfibration when `C` has pushouts, with cocartesian lifts by pushout, and the fixed
coslice projection `C.CosliceUnder(x) -> C` is a discrete opfibration with cocartesian
lifts by postcomposition. These properties come from the construction theorems. They are
not runtime decisions.

## Examples

### Finite sets

Finite sets form a full property subcategory of sets. Finiteness is closed under
isomorphism.

```python
class FiniteSetsCategory(Category):
    def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
        return (Fun(self, Sets()).FullyFaithful().inclusion(),)
```

The inclusion is constructed directly in `Fun(self, Sets()).FullyFaithful()`.

### Monoids

`Monoids()` is notation-neutral. It is a subcategory of `Magmas()` because its morphisms
preserve all monoid structure:

```python
class MonoidsCategory(Category):
    def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
        return (Fun(self, Magmas()).Faithful().inclusion(),)
```

The additive and multiplicative refinements retain their selected operation roles.

### Pointed sets

A pointed set is an object of the coslice category under the singleton set:

\[
\mathbf{PointedSet}=1\!\downarrow\!\mathbf{Set}.
\]

The selected functor is the composite of the pullback projection to `Fun([1], Sets())`
with `ev_1`, that is `(X, x) |-> X`. The pullback projection itself returns the morphism
`1 -> X` that selects `x`.

### Product categories and `Fun([1], C)`

For categories `C` and `D`, `product_projection(0)` and `product_projection(1)` are the
two functors from `C * D` to its factors.

The construction `Fun([1], C)` creates `ev_0` and `ev_1`. These functors exist without
being selected for structural inheritance.

## Compiler contract

The compiler uses `structure_functors()` as its sole structural graph. It must:

1. require every entry to lie in `Fun`;
2. require each entry's domain to be the declaring category;
3. derive immediate target categories from functor codomains;
4. build longer paths through composition in `Cat`;
5. preserve each functor's exact object and morphism maps;
6. derive each functor's generalized-element action from its morphism action, and
   precompose a retained stage comparison only for classical-stage methods;
7. reject transport when the selected functor lacks a required mathematical map;
8. detect a structural-image mismatch at the first transport of a value: traverse every
   route to a reachable category in declaration order, store the first image in the
   canonical cache, require each later image to be the same object by identity, and
   raise a construction-defect error naming both routes and the shared ancestor on a
   mismatch; method compilation constructs no images; diamonds otherwise follow
   [resolution.md](resolution.md);
9. canonicalize repeated construction of the same declared functor;
10. build each compiled role on the controlled compiled ancestor roles, copy the local
    declaration's class body onto it, and rebind copied `__class__` closures to it;
11. derive inherited methods from these paths;
12. derive subobject-of-product component functors by composition;
13. install the compiled roles of a point category `{X}` on its distinguished object:
    `{X}.ObjectType` on the value `X`, and `{X}.ElementType` on the generalized elements
    of `X`, which for a category `X = C` are `C.ObjectType` at stage `1` and
    `C.MorphismType` at stage `[1]`.

Natural transformations are trusted constructions, never compiler proofs. There is no
route normalization, route scoring, or preservation registry.

The meaning of every inherited method is composition: `X.f() := F(X).f()`. The receiver
and every mathematical argument are transported forward along the selected route; for a
classical element the stage comparison is precomposed; the declaring method runs on the
images; its value is returned exactly as `D` returned it.

The public surface is dynamic inheritance in Sage's sense. The kernel builds
`C.ObjectType`, `C.ElementType`, and `C.MorphismType` as dynamic classes carrying the
linearized surface of every selected route. A leaf writes no Python inheritance. A leaf
that wants a source-category result overrides the inherited method or adds its own.

The compiler does not infer a functor from a category pair. It does not infer fullness,
faithfulness, or equivalence from a class name. It does not add computational routes to
any functor predicate.

## Mathlib correspondence

The categorical definitions follow Mathlib where the same construction exists. Python
names remain owned by the relevant category object.

The reference definitions are Mathlib's
[functor API](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Functor/Basic.html),
[full-subcategory API](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/ObjectProperty/FullSubcategory.html),
[full and faithful functor API](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Functor/FullyFaithful.html),
and [arrow-category API](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Comma/Arrow.html).

Mathlib's arrow category has morphisms as objects and commuting squares as morphisms;
here it is `Fun([1], C)`. Mathlib's `C ⥤ D` has functors and natural
transformations; here it is `Mor(Cat())(C, D)`. Repository endpoint application
`Mor(C)(A, B)` selects the full subcategory of `Mor(C)` on morphisms `A -> B`.

| Mathlib | Repository |
| --- | --- |
| `CategoryTheory.Functor C D` | `Cat().MorphismType` with domain `C` and codomain `D` |
| `C ⥤ D` | `Mor(Cat())(C, D)` or `Fun(C, D)` |
| `Functor.id C` | `Fun(C, C).Equivalences().identity()` |
| `Functor.fromPUnit X` | the point functor of `X`, an object of `Fun(Cat().Point(X), D)` |
| `ObjectProperty.FullSubcategory P` | the property subcategory `C.P()` |
| `ObjectProperty.ι P` | `Fun(C.P(), C).FullyFaithful().inclusion()` |
| inclusion induced by `P -> Q` | `Fun(C.P(), C.Q()).FullyFaithful().inclusion()` |
| `wideSubcategoryInclusion P` | `Fun(Wide, C).Faithful().inclusion()` |
| `ConcreteCategory.forget`, `HasForget₂.forget₂` | an extra structure containing one chosen functor and its required compatibility |
| `Prod.fst`, `Prod.snd` | `product_projection(0)` and `product_projection(1)` |
| `Arrow.leftFunc`, `Arrow.rightFunc` | `ev_0` and `ev_1` of `Fun([1], C)` |
| `Over.forget` | the projection retained by the over-category construction |
| `StructuredArrow.proj` | the projection retained by the structured-arrow construction |
| `F.Full` | `F.is_full()` and `Mor(Cat()).Full()` |
| `F.Faithful` | `F.is_faithful()` and `Mor(Cat()).Faithful()` |
| `F.FullyFaithful` | `F.is_fully_faithful()` and `Mor(Cat()).FullyFaithful()` |
| `F.EssSurj` | `F.is_essentially_surjective()` and its property subcategory |
| `F.IsEquivalence` | `F.is_equivalence()` and `Mor(Cat()).Equivalences()` |

Mathlib uses propositions and typeclasses to carry established facts. This repository
uses owned predicates, `ask()`, assumptions, direct property construction, and
same-object refinement. The mathematical definitions and implications remain the same.

Mathlib's `ConcreteCategory` contains a fixed faithful functor to `Type` as extra
structure. Its `HasForget₂ C D` class also contains a chosen functor `C -> D`; it does
not derive one from the endpoints. See
[ConcreteCategory.Forget](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/ConcreteCategory/Forget.html).

Mathlib's `Functor.fromPUnit X : Discrete PUnit ⥤ C` sends the punctual category to a
chosen object, and `Functor.equiv` states the equivalence
`(Discrete PUnit ⥤ C) ≌ C`. See
[PUnit](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/PUnit.html).
Here `Cat().Point(X)` names its sole object `X` and owns the declarations specific to
`X`, so the corresponding functor is an inclusion rather than a constant functor from an
anonymous point.

Mathlib defines `Prod.fst` and `Prod.snd` separately. See
[Products.Basic](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Products/Basic.html).
This repository follows that construction-owned pattern for every presentation.

The selection of functors for Python method inheritance has no Mathlib counterpart. It
is kernel infrastructure over already established mathematical functors.

## Acceptance conditions

- `Cat().ObjectType` is the implementation type of every category.
- `Cat().MorphismType` is the implementation type of every functor.
- `Fun = Mor(Cat())` owns functors as its objects.
- `Fun(C, D)` is `Mor(Cat())(C, D)`.
- Natural transformations are morphisms of `Fun(C, D)`.
- Functor properties are property subcategories of `Fun` and its fixed-endpoint categories.
- Every functor predicate returns an applied `Predicate`.
- Direct construction and assumptions use the general same-object refinement path.
- Functor properties have no computational handlers.
- Established property implications induce category inclusions.
- A full-subcategory inclusion is fully faithful by construction.
- Every functor is constructed through `Fun(Source, Target)` or an established property subcategory.
- A specialized constructor receives enough mathematical data to select one functor.
- Endpoint categories and object fields never select a functor.
- The repository has no generic constructor selected by the phrase “forget structure.”
- Every structural functor is named by its construction or given as an explicit composite.
- Each category presentation retains all projections and evaluations required by its definition.
- `Cat().Products()` and `Cat().Coproducts()` accept sequence-indexed category diagrams.
- Their objects own `product_projection(i)` and `coproduct_injection(i)` respectively.
- Every object of `Cat().Products().Subobjects()` derives its component functors by composition.
- Slice and coslice categories are pullbacks of `ev_1` and `ev_0` along the chosen object and retain their pullback projections.
- Fibration and opfibration structure retains its cartesian or cocartesian lifts.
- Kan extensions retain their units, counits, and universally induced natural transformations.
- `Cat().Point(X)`, written `{X}`, is the one-object category on a distinguished object `X`, retained once per `X`.
- A point functor is the inclusion `{X} -> D`, constructed through `Fun({X}, D)` and selected in `{X}.structure_functors()`.
- A selected point functor `{C} -> D` supplies `D`'s object surface to the category `C`, and `D`'s element surface to `C.ObjectType` at stage `1` and `C.MorphismType` at stage `[1]`.
- Every selected structural functor is an ordinary object of `Fun`.
- `structure_functors()` determines compiled role bases and method compilation, nothing else.
- The compiler derives structural paths only through composition in `Cat`.
