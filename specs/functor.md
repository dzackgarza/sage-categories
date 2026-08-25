# Functors, `Cat`, and structural inheritance

## Contents

- [Kernel ownership](#kernel-ownership)
- [Functors as arrows of `Cat`](#functors-as-arrows-of-cat)
- [The arrow-category construction](#the-arrow-category-construction)
- [Functor property subcategories](#functor-property-subcategories)
- [Property resolution](#property-resolution)
- [Inclusion functors](#inclusion-functors)
- [Structural inheritance](#structural-inheritance)
- [Functor construction and presentation data](#functor-construction-and-presentation-data)
- [Products, coproducts, and component functors](#products-coproducts-and-component-functors)
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

Thus `Sets()`, `Ar(C)`, and every property subcategory are instances of
`Cat().ObjectType`. They do not form a second Python category hierarchy.

`Cat` owns the same role types as every other category:

- `Cat().ObjectType` implements categories;
- `Cat().ArrowType` implements functors;
- `Cat().ElementType` is absent because the theory does not use elements of `Cat`;
- `Cat()(...)` constructs categories;
- `Fun = Ar(Cat())` constructs the category whose objects are functors.

The kernel also supplies the uniform categorical constructions:

```python
C.ArrowCategory()       # Ar(C)
C.HomCategory(X, Y)     # Hom_C(X, Y)
C.EndArrowCategory()    # EndAr(C)
C.AutArrowCategory()    # AutAr(C)
```

These constructors are methods of the category object because `Cat().ObjectType` owns
them. Every category inherits them from `Cat`.

For `A, B in C`, endpoint application to the arrow category is the Hom category:

```python
H = Ar(C)(A, B)

H is Hom(C)(A, B)
H is C.HomCategory(A, B)
H is A.Hom(B)
H is B ** A
```

These spellings return one cached category. Supplying arrow data through any spelling
uses that category's object constructor. No spelling owns a parallel Hom or arrow
construction.

## Functors as arrows of `Cat`

A functor is an arrow in `Cat`. Define `Fun = Ar(Cat())`. Therefore, every functor is an
object of `Fun`:

```python
Fun = Ar(Cat())
F = Fun(C, D)(on_object, on_morphism)
```

The inherited `Cat().ArrowType` surface supplies:

```python
F.domain()       # C
F.codomain()     # D
F.on_object(X)   # an object of D
F.on_morphism(f) # an arrow of D
```

The maps preserve identities and composition:

\[
F(1_X)=1_{F(X)},\qquad F(g\circ f)=F(g)\circ F(f).
\]

An action on elements is additional mathematics of a concrete functor. It is not a
third component of every functor. A category of concrete functors can add
`on_element()` through its own arrow or object surface when the relevant underlying-set
maps are defined.

For fixed `C, D in Cat()`, the functor category is the Hom category in `Cat`:

```python
Fun(C, D) == Cat().HomCategory(C, D)
```

Its objects are functors `C -> D`. Its arrows are natural transformations. Natural
isomorphisms are the objects of its isomorphism-arrow category.

`Fun(C, D)` is the fixed-domain and fixed-codomain part of `Ar(Cat())`. The general
arrow-category construction supplies the shared functor implementation. The Hom
category supplies the natural-transformation structure between fixed endpoints.

## The arrow-category construction

For every category `C`, the kernel constructs `Ar(C)` or, equivalently,
`C.ArrowCategory()`.

Objects of `Ar(C)` are arrows of `C`. An object retains its domain, codomain, and
underlying arrow. Arrows of `Ar(C)` are commuting squares.

Applying `Ar(C)` to endpoints `A, B` selects the same Hom category as `A.Hom(B)`.
It does not define a second fixed-endpoint construction.

The construction is uniform. In particular:

- objects of `Ar(Sets())` are set maps;
- objects of `Ar(Cat())` are functors;
- objects of `Ar(Fun(C, D))` are natural transformations.

The related property categories use the same mechanism:

```python
Ar(C).Monomorphisms()
Ar(C).Epimorphisms()
Ar(C).Isomorphisms()
Ar(C).Automorphisms()
```

Each is a property subcategory of an owned arrow category. Each property has its owned
predicate, trusted constructor, assumption route, implication rules, and optional
computational routes.

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

- `Full(F)` states that every arrow `F(X) -> F(Y)` has a preimage under
  `F.on_morphism()`;
- `Faithful(F)` states that each map on arrows is injective;
- `FullyFaithful(F)` is the conjunction of fullness and faithfulness;
- `EssentiallySurjective(F)` states that every object of `D` is isomorphic to an image
  of an object of `C`;
- `Equivalence(F)` states that `F` is fully faithful and essentially surjective.

These definitions introduce no selected witnesses. A separate construction can select
a preimage arrow, inverse functor, unit, or counit when an operation requires that data.

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

This is the property category's trusted constructor. It asserts the defining property
and refines the same owned functor.

An interactive assumption uses the same predicate and refinement:

```python
F = Fun(C, D)(on_object, on_morphism)
assume(F.is_full())
```

A construction that establishes a property constructs directly in the corresponding
property category. For example, the inclusion of a full subcategory is constructed in
`Fun(C, D).FullyFaithful()`.

The functor-property categories currently register no computational routes. Therefore:

```python
ask(F.is_full())
```

uses category placement, active assumptions, cached exact decisions, and categorical
implications. It returns `Unknown` when none establishes the proposition.

This absence of handlers is local to these predicates. Other owned predicates can
register exact computational routes when mathematics and available algorithms supply
them.

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

The defining object predicate selects the objects. The Hom categories, identities, and
composition are inherited from `C`. The leaf records this theorem by constructing
directly in `Fun(C.P(), C).FullyFaithful()`.

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

A wide subcategory retains every object and restricts arrows by a multiplicative arrow
predicate. Its inclusion is faithful by construction. A general subcategory inclusion
is also faithful. Neither becomes full unless its mathematical definition establishes
fullness.

## Structural inheritance

`structure_functors()` is a repository compiler declaration. It is not an additional
kind of functor and is not part of Mathlib's functor theory.

Every entry is an ordinary owned object of `Ar(Cat())`. Its mathematical existence and
properties come first. For example, finite sets are a full subcategory of sets, so their
inclusion functor exists independently of method compilation.

A category selects an immediate functor only when the functor states the mathematical
change of structure that supplies inherited operations:

```python
class FiniteSetsCategory(Category):
    def structure_functors(self) -> tuple[Cat().ArrowType, ...]:
        return (Fun(self, Sets()).FullyFaithful().inclusion(),)
```

The leaf explicitly constructs the inclusion and records full faithfulness through the
selected property category. The tuple tells the compiler to expose operations owned by
`Sets()` through that functor.

The categories `Fun(self, D)` can contain many other functors. Their existence does not
affect the compiled public surface. Selection changes compiler behavior only. It does
not change a functor's mathematical definition.

Each category lists only immediate selected functors. The kernel obtains longer routes
by composition and applies [resolution.md](resolution.md) to diamonds.

## Functor construction and presentation data

`Fun(Source, Target)` owns construction of functors with those endpoints. The endpoint
pair selects a Hom category. It does not select an object of that category.

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

| Construction | Functor or arrow supplied |
| --- | --- |
| subcategory or property subcategory | its specified inclusion |
| product category | each `product_projection(i)` |
| coproduct category | each `coproduct_injection(i)` |
| arrow category `Ar(C)` | `source_projection()` and `target_projection()` |
| slice or coslice presentation | projections to the varying object and defining arrow |
| Grothendieck fibration | its projection and specified cartesian lifts |
| Grothendieck opfibration | its projection and specified cocartesian lifts |
| base change | the functor supplied by pullback, pushforward, or the stated adjunction |
| left or right Kan extension | the extended functor and its universal natural transformation |
| composite construction | the ordinary composite of the supplied functors |

The dual of a Grothendieck fibration is an opfibration. It is also called a cofibered
category. Use “cofibration” only when a cited source uses that synonym. In other
contexts, a cofibration is a class of arrows and is a different notion.

Mathlib's `ConcreteCategory.forget` is part of a concrete-category structure. Its
`HasForget₂.forget₂` also carries a chosen functor as extra structure. These definitions
do not derive a functor from its endpoints. This repository records the exact
construction instead of defining an unnamed default.

### Identity and composition

`Fun(C, C).Equivalences().identity()` constructs the identity arrow on `C`. Functor
composition uses the arrow composition owned by `Cat`.

### Inclusions

`Fun(S, T).Faithful().inclusion()` constructs an established subcategory inclusion.
Use `Fun(S, T).FullyFaithful().inclusion()` when `S` is full in `T`.

### Induced functors

A categorical construction can act on a functor. The result is another object of
`Ar(Cat())`. Examples include arrow-category maps, product functors, comma-category
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
transformation is an arrow in a fixed-endpoint functor category. The Kan extension
construction owns these arrows. A later structural route uses their functor components
and ordinary composition.

### Essential images

For `F: C -> D`, `F.essential_image()` is the full property subcategory of `D` on
objects isomorphic to `F(X)` for some `X in C`. Its inclusion into `D` is fully faithful
by construction. The original functor factors through this category.

## Products, coproducts, and component functors

The generic product and coproduct constructions apply to `Cat()` itself. For a sequence
of categories, construct:

```python
P = Cat().Products()((C_0, ..., C_n))
Q = Cat().Coproducts()((C_0, ..., C_n))
```

Their category-owned public arrows are:

```python
P.product_projection(i)   # an object of Fun(P, C_i)
Q.coproduct_injection(i)  # an object of Fun(C_i, Q)
```

The index is an `int` in the supplied sequence. These methods come from
`Cat().Products().ObjectType` and `Cat().Coproducts().ObjectType`. They return
`Cat().ArrowType` values.

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

The arrow category retains:

```python
Ar(C).source_projection()  # Ar(C) -> C
Ar(C).target_projection()  # Ar(C) -> C
```

The generic pullback construction is a subobject of a product presentation. Its usual
legs are component projections. The same rule handles repeated codomains.

## Slices and coslices

Present a slice or coslice as a subcategory of the sequence product `C * Ar(C)`. The
first component is the varying object. The second component is its defining arrow.

For the coslice under `x`, an object is `(X, f: x -> X)`. Its component functors are:

```python
C.CosliceUnder(x).product_projection(0)  # (X, f) |-> X in C
C.CosliceUnder(x).product_projection(1)  # (X, f) |-> f in Ar(C)
```

Composing the second functor with `Ar(C).source_projection()` gives the constant object
`x`. Composing it with `Ar(C).target_projection()` gives the first projection.

For the slice over `x`, an object is `(X, f: X -> x)`. The source composite gives the
first projection. The target composite gives the constant object `x`.

These presentations supply the natural projections to varying objects and defining
arrows. If `C` has pullbacks, the slice projection has its standard fibration structure.
If `C` has pushouts, the coslice projection has its standard opfibration structure.
These properties come from the construction theorems. They are not runtime decisions.

## Examples

### Finite sets

Finite sets form a full property subcategory of sets. Finiteness is closed under
isomorphism.

```python
class FiniteSetsCategory(Category):
    def structure_functors(self) -> tuple[Cat().ArrowType, ...]:
        return (Fun(self, Sets()).FullyFaithful().inclusion(),)
```

The inclusion is constructed directly in `Fun(self, Sets()).FullyFaithful()`.

### Monoids

`Monoids()` is notation-neutral. It is a subcategory of `Magmas()` because its arrows
preserve all monoid structure:

```python
class MonoidsCategory(Category):
    def structure_functors(self) -> tuple[Cat().ArrowType, ...]:
        return (Fun(self, Magmas()).Faithful().inclusion(),)
```

The additive and multiplicative refinements retain their selected operation roles.

### Pointed sets

A pointed set is an object of the coslice category under the singleton set:

\[
\mathbf{PointedSet}=1\!\downarrow\!\mathbf{Set}.
\]

```python
PointedSets().product_projection(0)  # (X, x) |-> X
```

The selected functor states `(X, x) |-> X`. The second product projection returns the
arrow `1 -> X` that selects `x`.

### Product and arrow categories

For categories `C` and `D`, `product_projection(0)` and `product_projection(1)` are the
two functors from `C * D` to its factors.

The arrow-category construction creates `source_projection()` and `target_projection()`.
These functors exist without being selected for structural inheritance.

## Compiler contract

The compiler uses `structure_functors()` as its sole structural graph. It must:

1. require every entry to lie in `Ar(Cat())`;
2. require each entry's domain to be the declaring category;
3. derive immediate target categories from functor codomains;
4. build longer paths through composition in `Cat`;
5. preserve each functor's exact object and morphism maps;
6. use category-specific element actions only when declared by the applicable theory;
7. reject transport when the selected functor lacks a required mathematical map;
8. resolve diamonds under [resolution.md](resolution.md);
9. canonicalize repeated construction of the same declared functor;
10. derive inherited methods from these paths;
11. derive subobject-of-product component functors by composition.

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

| Mathlib | Repository |
| --- | --- |
| `CategoryTheory.Functor C D` | `Cat().ArrowType` with domain `C` and codomain `D` |
| `C ⥤ D` | `Cat().HomCategory(C, D)` or `Fun(C, D)` |
| `Functor.id C` | `Fun(C, C).Equivalences().identity()` |
| `ObjectProperty.FullSubcategory P` | the property subcategory `C.P()` |
| `ObjectProperty.ι P` | `Fun(C.P(), C).FullyFaithful().inclusion()` |
| inclusion induced by `P -> Q` | `Fun(C.P(), C.Q()).FullyFaithful().inclusion()` |
| `wideSubcategoryInclusion P` | `Fun(Wide, C).Faithful().inclusion()` |
| `ConcreteCategory.forget`, `HasForget₂.forget₂` | an extra structure containing one chosen functor and its required compatibility |
| `Prod.fst`, `Prod.snd` | `product_projection(0)` and `product_projection(1)` |
| `Arrow.leftFunc`, `Arrow.rightFunc` | `source_projection()` and `target_projection()` |
| `Over.forget` | the projection retained by the over-category construction |
| `StructuredArrow.proj` | the projection retained by the structured-arrow construction |
| `F.Full` | `F.is_full()` and `Ar(Cat()).Full()` |
| `F.Faithful` | `F.is_faithful()` and `Ar(Cat()).Faithful()` |
| `F.FullyFaithful` | `F.is_fully_faithful()` and `Ar(Cat()).FullyFaithful()` |
| `F.EssSurj` | `F.is_essentially_surjective()` and its property subcategory |
| `F.IsEquivalence` | `F.is_equivalence()` and `Ar(Cat()).Equivalences()` |

Mathlib uses propositions and typeclasses to carry established facts. This repository
uses owned predicates, `ask()`, assumptions, direct property construction, and
same-object refinement. The mathematical definitions and implications remain the same.

Mathlib's `ConcreteCategory` contains a fixed faithful functor to `Type` as extra
structure. Its `HasForget₂ C D` class also contains a chosen functor `C -> D`; it does
not derive one from the endpoints. See
[ConcreteCategory.Forget](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/ConcreteCategory/Forget.html).

Mathlib defines `Prod.fst` and `Prod.snd` separately. See
[Products.Basic](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Products/Basic.html).
This repository follows that construction-owned pattern for every presentation.

The selection of functors for Python method inheritance has no Mathlib counterpart. It
is kernel infrastructure over already established mathematical functors.

## Acceptance conditions

- `Cat().ObjectType` is the implementation type of every category.
- `Cat().ArrowType` is the implementation type of every functor.
- `Fun = Ar(Cat())` owns functors as its objects.
- `Fun(C, D)` is `Cat().HomCategory(C, D)`.
- Natural transformations are arrows of `Fun(C, D)`.
- Functor properties are property subcategories of `Fun` and its fixed-endpoint categories.
- Every functor predicate returns an applied `Predicate`.
- Direct construction and assumptions use the general same-object refinement path.
- Functor properties have no computational handlers until an exact route is supplied.
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
- Slice and coslice categories use these component functors and arrow source or target projections.
- Fibration and opfibration structure retains its cartesian or cocartesian lifts.
- Kan extensions retain their units, counits, and universally induced natural transformations.
- Every selected structural functor is an ordinary object of `Ar(Cat())`.
- `structure_functors()` affects method compilation only.
- The compiler derives structural paths only through composition in `Cat`.
