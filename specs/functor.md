# Functors, `Cat`, and structural inheritance

## Contents

- [Kernel ownership](#kernel-ownership)
- [Functors as arrows of `Cat`](#functors-as-arrows-of-cat)
- [The arrow-category construction](#the-arrow-category-construction)
- [Functor property subcategories](#functor-property-subcategories)
- [Property resolution](#property-resolution)
- [Inclusion functors](#inclusion-functors)
- [Structural inheritance](#structural-inheritance)
- [Standard functor constructions](#standard-functor-constructions)
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
- `Ar(Cat())` constructs the category whose objects are functors.

The kernel also supplies the uniform categorical constructions:

```python
C.ArrowCategory()       # Ar(C)
C.HomCategory(X, Y)     # Hom_C(X, Y)
C.EndArrowCategory()    # EndAr(C)
C.AutArrowCategory()    # AutAr(C)
```

These constructors are methods of the category object because `Cat().ObjectType` owns
them. Every category inherits them from `Cat`.

## Functors as arrows of `Cat`

A functor is an arrow in `Cat`. Therefore, every functor is an object of
`Ar(Cat())`:

```python
FunctorArrows = Ar(Cat())
F = FunctorArrows(C, D, on_object, on_morphism)
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

Functor properties are property subcategories of `Ar(Cat())`:

```python
FunctorArrows = Ar(Cat())
FullFunctors = FunctorArrows.Full()
FaithfulFunctors = FunctorArrows.Faithful()
FullyFaithfulFunctors = FunctorArrows.FullyFaithful()
EssentiallySurjectiveFunctors = FunctorArrows.EssentiallySurjective()
EquivalenceFunctors = FunctorArrows.Equivalences()
```

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
F = Ar(Cat())(C, D, on_object, on_morphism)
F = Ar(Cat()).Full()(F)
```

This is the property category's trusted constructor. It asserts the defining property
and refines the same owned functor.

An interactive assumption uses the same predicate and refinement:

```python
F = Ar(Cat())(C, D, on_object, on_morphism)
assume(F.is_full())
```

A construction that establishes a property constructs directly in the corresponding
property category. For example, the inclusion of a full subcategory is constructed in
`Ar(Cat()).FullyFaithful()`.

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

An inclusion is an arrow of `Cat` owned by its source category. The source and target
categories determine its object and arrow maps:

```python
iota = D.inclusion(C)
```

Use this construction only when `D` is already established as a subcategory of `C`.
The construction does not infer a relation from Python inheritance or shared storage.

For a full property subcategory `C.P()`, the canonical inclusion is:

```python
iota = C.P().inclusion(C)
```

The defining object predicate selects the objects. The Hom categories, identities, and
composition are inherited from `C`. The construction therefore places `iota` directly
in `Ar(Cat()).FullyFaithful()`.

Suppose predicates `P` and `Q` on `C` satisfy

\[
P(X)\Longrightarrow Q(X).
\]

The kernel records the implication as an inclusion of property subcategories:

```python
iota = C.P().inclusion(C.Q())
```

The source property is stronger. The target property is weaker. The implication belongs
to the property relation, and the resulting functor belongs to the source category.

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
        return (self.inclusion(Sets()),)
```

The tuple does not define the inclusion. It tells the compiler to expose operations
owned by `Sets()` on finite-set objects through that established inclusion.

A category can own many other functors. Their existence does not affect the compiled
public surface. Selection changes compiler behavior only. It does not change the
functor's mathematical definition.

Each category lists only immediate selected functors. The kernel obtains longer routes
by composition and applies [resolution.md](resolution.md) to diamonds.

## Standard functor constructions

The kernel implements standard arrows of `Cat` once. Category objects expose their
owned instances through mathematical names.

### Identity and composition

`C.identity_functor()` constructs the identity arrow on `C`. Functor composition uses
the arrow composition owned by `Cat`.

### Inclusions

`D.inclusion(C)` constructs the established inclusion of a subcategory. Category
placement determines whether the result is also full, faithful, or fully faithful.

### Forgetful functors

A category with chosen structure owns its standard forgetful functor:

```python
forget = Source.forget(Target)
```

The source category determines which structure is forgotten. A category pair is valid
only when the declared mathematical presentation selects one canonical functor.

The functor's properties follow from its construction. For example, a forgetful functor
can be faithful without being full.

### Projections

Product, comma, arrow, slice, and structured-arrow categories own their standard
projection functors. Use their established names:

- `fst` and `snd` for product-category projections;
- `left` and `right` for arrow-category projections;
- `proj` for a structured-arrow projection;
- `forget` for an over-category projection.

The arrow itself gives a natural transformation from `left` to `right` on `Ar(C)`.

### Induced functors

A categorical construction can act on a functor. The result is another object of
`Ar(Cat())`. Examples include arrow-category maps, product functors, comma-category
maps, diagram postcomposition, restrictions, inverse images, and lifts.

The construction owner supplies the induced object and morphism maps. It also supplies
any natural transformations or natural isomorphisms that compare composites.

### Essential images

For `F: C -> D`, `F.essential_image()` is the full property subcategory of `D` on
objects isomorphic to `F(X)` for some `X in C`. Its inclusion into `D` is fully faithful
by construction. The original functor factors through this category.

## Examples

### Finite sets

Finite sets form a full property subcategory of sets. Finiteness is closed under
isomorphism.

```python
class FiniteSetsCategory(Category):
    def structure_functors(self) -> tuple[Cat().ArrowType, ...]:
        return (self.inclusion(Sets()),)
```

The inclusion is constructed directly in `Ar(Cat()).FullyFaithful()`.

### Monoids

`Monoids()` is notation-neutral. It is a subcategory of `Magmas()` because its arrows
preserve all monoid structure:

```python
class MonoidsCategory(Category):
    def structure_functors(self) -> tuple[Cat().ArrowType, ...]:
        return (self.inclusion(Magmas()),)
```

The additive and multiplicative refinements retain their selected operation roles.

### Pointed sets

A pointed set is a pair `(X, x)` with `x in X`. Its category owns the carrier functor to
`Sets()`:

```python
class PointedSetsCategory(Category):
    def structure_functors(self) -> tuple[Cat().ArrowType, ...]:
        return (self.carrier(),)
```

The selected functor supplies the inherited set surface. The chosen point remains part
of the source object's defining data.

### Product and arrow categories

For categories `C` and `D`, their product category owns `fst: C * D -> C` and
`snd: C * D -> D`.

`Ar(C)` owns `left: Ar(C) -> C` and `right: Ar(C) -> C`. These functors exist without
being selected for structural inheritance.

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
10. derive inherited methods from these paths.

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
| `Functor.id C` | `C.identity_functor()` |
| `ObjectProperty.FullSubcategory P` | the property subcategory `C.P()` |
| `ObjectProperty.ι P` | `C.P().inclusion(C)` |
| inclusion induced by `P -> Q` | `C.P().inclusion(C.Q())` |
| `wideSubcategoryInclusion P` | the inclusion owned by the corresponding wide subcategory |
| `forget`, `forget₂` | `Source.forget(Target)` for the declared forgetful structure |
| `Prod.fst`, `Prod.snd` | `fst`, `snd` on the product category |
| `Arrow.leftFunc`, `Arrow.rightFunc` | `left`, `right` on `Ar(C)` |
| `Over.forget` | `forget` on the over category |
| `StructuredArrow.proj` | `proj` on the structured-arrow category |
| `F.Full` | `F.is_full()` and `Ar(Cat()).Full()` |
| `F.Faithful` | `F.is_faithful()` and `Ar(Cat()).Faithful()` |
| `F.FullyFaithful` | `F.is_fully_faithful()` and `Ar(Cat()).FullyFaithful()` |
| `F.EssSurj` | `F.is_essentially_surjective()` and its property subcategory |
| `F.IsEquivalence` | `F.is_equivalence()` and `Ar(Cat()).Equivalences()` |

Mathlib uses propositions and typeclasses to carry established facts. This repository
uses owned predicates, `ask()`, assumptions, direct property construction, and
same-object refinement. The mathematical definitions and implications remain the same.

The selection of functors for Python method inheritance has no Mathlib counterpart. It
is kernel infrastructure over already established mathematical functors.

## Acceptance conditions

- `Cat().ObjectType` is the implementation type of every category.
- `Cat().ArrowType` is the implementation type of every functor.
- `Ar(Cat())` owns functors as its objects.
- `Fun(C, D)` is `Cat().HomCategory(C, D)`.
- Natural transformations are arrows of `Fun(C, D)`.
- Functor properties are property subcategories of `Ar(Cat())`.
- Every functor predicate returns an applied `Predicate`.
- Direct construction and assumptions use the general same-object refinement path.
- Functor properties have no computational handlers until an exact route is supplied.
- Established property implications induce category inclusions.
- A full-subcategory inclusion is fully faithful by construction.
- Every selected structural functor is an ordinary object of `Ar(Cat())`.
- `structure_functors()` affects method compilation only.
- The compiler derives structural paths only through composition in `Cat`.
