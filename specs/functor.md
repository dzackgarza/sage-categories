# Functors and structural inheritance

## Contents

- [Foundational rule](#foundational-rule)
- [Why Sage supercategories are insufficient](#why-sage-supercategories-are-insufficient)
- [Selected functors and ordinary functors](#selected-functors-and-ordinary-functors)
- [Kernel-owned standard functors](#kernel-owned-standard-functors)
- [Classifying an edge](#classifying-an-edge)
- [Functor taxonomy](#functor-taxonomy)
- [Naming rules](#naming-rules)
- [Functor properties](#functor-properties)
- [Property subcategories and repleteness](#property-subcategories-and-repleteness)
- [Derived functors](#derived-functors)
- [Examples](#examples)
- [Compiler contract](#compiler-contract)
- [Mathlib correspondence](#mathlib-correspondence)
- [Acceptance conditions](#acceptance-conditions)

## Foundational rule

Every category declares its complete tuple of immediate structural functors:

```python
class Category:
    def structure_functors(self) -> tuple[Functor, ...]:
        return ()
```

The tuple contains functors. It never contains bare target categories.

Each functor has:

- a domain category;
- a codomain category;
- an object map;
- an arrow map;
- an element map when that mathematical functor acts on elements.

Membership in `structure_functors()` selects the functor for public inheritance.
The selection does not require a second `StructuralFunctor` class or registry.

The kernel derives the structural category graph from these functors. It does not store
an independent `super_categories()` graph.

## Why Sage supercategories are insufficient

Sage defines `C` as a supercategory of `D` when it can apply an implicit canonical
functor from `D` to `C`. Sage states that this functor is normally an inclusion or a
forgetful functor. Sage also warns that its “subcategory” terminology differs from the
standard definition. See the
[Sage category primer](https://doc.sagemath.org/html/en/reference/categories/sage/categories/primer.html#on-the-category-hierarchy-subcategories-and-super-categories)
and [Sage issue 16183](https://github.com/sagemath/sage/issues/16183).

The category pair alone does not determine the functor. The same Sage hierarchy edge can
hide several different mathematical relations:

| Sage hierarchy use | Required explicit relation |
| --- | --- |
| Objects and arrows form a genuine subcategory | `SubcategoryInclusionFunctor` |
| All ambient arrows between selected objects remain | `FullSubcategoryInclusionFunctor` |
| All objects remain and only arrows are restricted | `WideSubcategoryInclusionFunctor` |
| Operations, topology, grading, or chosen data are discarded | A kernel-owned standard forgetful functor |
| One component of a structured object is selected | A kernel-owned standard projection |
| A functorial construction is applied to an existing edge | The induced functor |
| Objects are selected up to isomorphism | A full-subcategory inclusion for an isomorphism-closed object property |
| Object properties are intersected inside one category | One inclusion induced by each property implication |
| Structured categories are combined by a pullback | The pullback projections |
| A category records realizations or presentations | The applicable realization, projection, or inclusion functor |

Sage's axiom framework also shows that property refinements need different inclusions.
For example, finite sets form a full subcategory of sets. The `Unital` refinement of
semigroups is not full because a semigroup morphism need not preserve the unit. See the
[Sage category-with-axiom documentation](https://doc.sagemath.org/html/en/reference/categories/sage/categories/category_with_axiom.html#upcoming-features).

No category-only edge can preserve these distinctions.

## Selected functors and ordinary functors

A category can own many mathematical functors. Only the functors listed in
`structure_functors()` contribute inherited public methods.

For example, an arrow category owns source and target projection functors. Their mere
existence does not make every source or target method a method on an arrow. The arrow
category selects a projection only when that projection defines intended structural
inheritance.

An engine realization also remains an ordinary functor or private representation. It
enters `structure_functors()` only when it is the selected mathematical change of
structure.

Each category lists only immediate functors. The kernel obtains longer routes by functor
composition. Diamond resolution follows [resolution.md](resolution.md).

### Selection is an inheritance declaration

`structure_functors()` answers one question. It selects the functors whose codomain
catalogues form the inherited public surface of the source category.

It does not list every functor whose domain is the source category. Such functors remain
ordinary mathematical functors. Omitting one from `structure_functors()` does not remove
it. The omission only prevents its codomain catalogue from becoming source methods.

For a selected functor `F: D -> C`, each inherited operation creates a construction
obligation. The functor must construct every image required by that operation:

- `F(X)` for a receiver or object argument;
- `F(f)` for an arrow argument;
- `F(x)` when the mathematical functor acts on elements;
- the canonical source-owned result when the result role requires reverse transport.

The compiler inherits an operation only when the selected functor meets its required
role obligations. It does not infer missing maps from annotations, storage, method names,
or Python types.

Kernel-owned standard functors meet these obligations once for every leaf. A leaf only
selects the appropriate instance. A custom structural functor must define genuine
mathematical maps for the roles it supports.

Selection therefore has two independent tests:

1. The codomain catalogue is the intended public structure of the source object.
2. The functor can construct the images required to transport that catalogue.

A functor can satisfy the second test and fail the first. It remains an ordinary functor.

### The construction obligation

A selected functor \(F:C\to D\) connects the category-owned implementation roles:

\[
C.\mathrm{ObjectType}\longrightarrow D.\mathrm{ObjectType},
\]

\[
C.\mathrm{ElementType}(X)\longrightarrow D.\mathrm{ElementType}(F(X)),
\]

and

\[
C.\mathrm{ArrowType}(X,Y)
\longrightarrow
D.\mathrm{ArrowType}(F(X),F(Y)).
\]

The element map is required only when the mathematical functor acts on elements. Each
map produces the category-owned implementation in the codomain. It never produces a
backend value or an unnamed Python wrapper.

The object map can use any valid public constructor route owned by \(D\). The arrow and
element maps use the corresponding category-owned constructors. The functor fixes these
maps when it is defined. The runtime does not search among constructors.

The conceptual constructor contract is:

| Source role | Required image | Constructor responsibility |
| --- | --- | --- |
| `X: C.ObjectType` | `F(X): D.ObjectType` | Construct from `X` or the semantic data selected by \(F\) |
| `x: C.ElementType` over `X` | `F(x): D.ElementType` over `F(X)` | Use the target ambient object's element construction |
| `f: C.ArrowType` from `X` to `Y` | `F(f): D.ArrowType` from `F(X)` to `F(Y)` | Use the target Hom constructor with image data defined by \(F\) |

This table states mathematical inputs and outputs. It does not prescribe exact Python
call syntax. Schematically, the object case can look like `D(X)`. The arrow case can look
like `Hom_D(F(X), F(Y))(F_data(f))`.

This is the construction obligation behind inherited methods. The compiler transports a
receiver from `C.ObjectType` to its canonical `D.ObjectType` image. It transports each
mathematical argument through the same functor. It then calls the method owned by \(D\).
It reconstructs a source-owned result when the method's result role requires that step.

This process is not equivalent to assigning forwarding methods in the leaf. A leaf never
writes code with the following conceptual repetition:

```python
def inherited_operation(self, argument):
    return F(self).inherited_operation(F(argument))
```

The selected functor and compiler already contain that general mechanism.

### Standard functors discharge standard obligations

An inclusion functor states that each source object, arrow, and applicable element already
has the codomain structure. Conceptually, its object map is the canonical result of
regarding `X: C.ObjectType` as an object of \(D\). This can be written schematically as
`D(X)`.

That notation does not require the same Python instance in both categories. The kernel
can retain a distinct canonical `D.ObjectType` image. It can also reuse one instance when
the category-owned representation permits this. The public functor remains the inclusion
in both cases.

The kernel implements the role maps for `SubcategoryInclusionFunctor`,
`FullSubcategoryInclusionFunctor`, and `WideSubcategoryInclusionFunctor`. Their leaves do
not define forwarding constructors, element conversions, or arrow conversions.

Selecting one of these inclusion functors asserts the standard inclusion contract. The
kernel can regard each category-owned source role as the corresponding codomain role. If
that contract does not hold, the declaration is not an inclusion. Leaf adapters cannot
make it one.

For example, `Sets().Finite()` introduces no new underlying set data. Its `ObjectType`
does not need an initializer that repeats set construction. Construction into the finite
subcategory creates the strongest finite-set implementation. The inclusion gives that
object its canonical image in `Sets()` through the existing set construction contract.

A product projection uses the standard tuple-presentation contract. If
`C.ObjectType.defining_data[i]` is an object of \(D\), then
`ProductProjectionFunctor(i, C, D)` selects that object. The kernel can normalize it
through the category-owned constructor for \(D\). The leaf does not write an accessor
functor, copy methods from that component, or define role-by-role forwarding.

Selecting this projection asserts the same contract for every source object. Component
`i` supplies the codomain object. The declared presentation supplies the corresponding
element and arrow images when those roles are used. If the presentation lacks these
maps, the projection cannot supply the affected inherited catalogue.

Thus the projection does not mean this leaf-level assignment:

```python
X.d_method = X.defining_data[i].d_method
```

It means that inherited calls use the canonical codomain image selected by the projection.

If no standard functor expresses the mathematics, the category can define a new functor
\(F:C\to D\). Its object map can choose any public constructor owned by \(D\). Its arrow
and element maps can use the corresponding public constructors. These maps define one
bespoke mathematical functor. They do not form a backend registry or automatic dispatch
system.

Most Sage `super_categories()` edges require no bespoke functor implementation here. A
leaf selects the correct kernel-owned inclusion, projection, or forgetting functor. The
more precise functor name records the mathematical distinction that Sage leaves implicit.

## Kernel-owned standard functors

The kernel implements standard categorical functors once. Leaves instantiate and select
them. They do not repeat object, element, or arrow maps.

Kernel-owned constructors include:

- `IdentityFunctor`;
- `SubcategoryInclusionFunctor`;
- `FullSubcategoryInclusionFunctor`;
- `WideSubcategoryInclusionFunctor`;
- `ProductProjectionFunctor`;
- arrow, comma, slice, and structured-arrow projections;
- standard forgetful functors determined by a declared structure presentation;
- restrictions, inverse images, and lifts induced from an existing functor.

For an object presented as a tuple, `ProductProjectionFunctor(i, D, C)` selects component
`i` of each object and the corresponding component of each arrow. It also acts on
elements when that component has a mathematical element map.

The standard structured-object contract stores one private `defining_data` tuple.
Projection `i` maps an object to entry `i`. The kernel derives the corresponding arrow
and element maps. A leaf does not implement those maps.

The constructor first extracts this tuple from the strongest semantic datum. It does not
request weaker components that the datum already determines. For example, a relation
subobject `R` of `X × X` already determines `X` from its ambient product.

The tuple returned by `structure_functors()` is not the category's complete functor
catalogue. It contains only the immediate functors selected to supply inherited public
structure.

For a poset \(P=(X,R)\), the carrier projection \(P\mapsto X\) is selected. It
supplies the set catalogue used when working with \(P\) as a set.

The relation projection \(P\mapsto R\) can still exist as an ordinary functor. It is not
selected for inheritance. Selecting it would expose the catalogue of a subset of
\(X\times X\) as methods on \(P\). Those methods describe the relation object, not the
poset as an object with elements.

The relation remains available through the poset's `order_relation()` operation and the
ordinary projection functor. Sage expresses the same inheritance choice by listing only
`Sets()` as a supercategory of posets.

## Classifying an edge

Classify an edge from its mathematical action. Do not classify it from Python identity,
shared storage, or a property such as faithfulness.

First ask whether `D` is defined from objects and arrows already in `C`. A canonical
image in `C` is not enough. The source values must be ambient values selected by object
or arrow predicates.

| Objects of `D` | Arrows of `D` | Edge to `C` |
| --- | --- | --- |
| Selected ambient objects | Every ambient arrow between them | Full-subcategory inclusion |
| Every ambient object | Selected ambient arrows | Wide-subcategory inclusion |
| Selected ambient objects | Selected ambient arrows | General subcategory inclusion |
| Objects presented as tuples with selected components | Corresponding component arrows | Kernel-owned projection |
| Objects with an underlying structure not presented as a component | Structure-preserving arrows | Kernel-owned forgetful functor |
| A second presentation of the same theory | Corresponding arrows | Equivalence or realization functor |

Then ask whether the edge is induced from another functor. Arrow maps, diagram
postcomposition, restrictions, inverse images, and lifts are induced functors owned by
their constructions.

If none of these cases applies, define the actual named functor. The structural graph
can select any functor whose maps define the intended inheritance. It does not force
every edge into an inclusion, forgetting, or projection class.

A functor can be full, faithful, or an equivalence without being an inclusion. For
example, a forgetful functor can be fully faithful. These properties do not change the
kind of edge.

An equivalence between two presentations is also not an inclusion. Store its inverse,
unit, and counit as equivalence data. Select one direction for structural inheritance
only when that direction is the intended public change of structure.

## Functor taxonomy

### Subcategory inclusions

For a genuine subcategory `D` of `C`, use the kernel constructor:

```python
iota = SubcategoryInclusionFunctor(D, C)
```

The functor is faithful. It need not be full. Its object and arrow maps are the stated
inclusions.

Use this form only when the source objects and arrows are literally a subcategory of the
target. A faithful forgetful functor is not thereby a
`SubcategoryInclusionFunctor`.

### Full-subcategory inclusions

For a full subcategory `D` of `C`, use the kernel constructor:

```python
iota = FullSubcategoryInclusionFunctor(D, C)
```

This inclusion is fully faithful by definition.

The source object property supplies the objects. Its Hom categories, identities, and
composition are the ambient ones. The inclusion is the identity on each Hom category.
No runtime predicate, algorithm, or check establishes fullness.

Mathlib models an object property `P` by `P.FullSubcategory`. Its inclusion is
`ObjectProperty.ι`, and Mathlib records that this functor is full and faithful. See
[Mathlib's full-subcategory API](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/ObjectProperty/FullSubcategory.html).

### Wide-subcategory inclusions

For a subcategory with every ambient object and selected arrows, use the kernel
constructor:

```python
iota = WideSubcategoryInclusionFunctor(D, C)
```

The arrow property must contain identities and be closed under composition. Mathlib uses
the name `wideSubcategoryInclusion`; see
[Mathlib's wide-subcategory API](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Widesubcategory.html).

The core of `C` is the wide subcategory whose arrows are the isomorphisms of `C`.

### Forgetful functors

Use a standard forgetful functor when the declared structure presentation determines an
underlying object that is not a tuple component. Mirror Mathlib's public names `forget`
and `forget₂`.

```python
forget = ForgetfulFunctor(source, target)
```

The kernel owns the standard implementation. The source category selects the exact
instance. When several underlying structures exist, the declared structure presentation
selects the route. A category pair alone does not select left or right module structure
on a bimodule.

Examples include:

- pointed sets to sets;
- topological spaces to sets;
- groups to sets;
- modules to their underlying additive groups;
- sets with a chosen operation to sets.

Several structures can exist on the same target object. Therefore, these functors are
not subcategory inclusions.

A forgetful functor is often faithful. It can also be full or an equivalence. Record
those facts as properties of the functor. Do not rename it as an inclusion.

Mathlib uses `forget` for a concrete category's functor to types. It uses `forget₂` for
a forgetful functor between concrete categories. See
[Mathlib's concrete-category API](https://leanprover-community.github.io/mathlib_docs/category_theory/concrete_category/basic.html).

### Projection functors

The kernel owns standard projections. The source category selects the required instance.
Use the construction's standard public name.

For a tuple presentation, instantiate:

```python
carrier = ProductProjectionFunctor(0, source, target)
```

Mathlib uses:

- `Prod.fst` and `Prod.snd` for product categories;
- `Comma.fst` and `Comma.snd` for comma categories;
- `Arrow.leftFunc` and `Arrow.rightFunc` for arrow categories;
- `Over.forget` for an over category;
- `StructuredArrow.proj` and `CostructuredArrow.proj` for structured arrows.

See Mathlib's
[product-category API](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Products/Basic.html),
[comma-category API](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Comma/Basic.html),
and [arrow-category API](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Comma/Arrow.html).

A projection can lose objects or arrows from other components. Its faithfulness and
fullness must follow from its definition. The name “projection” alone establishes neither.

### Induced functors

A construction can act on a functor. The result is another functor, not a category-only
hierarchy edge.

Examples include:

- `F.mapArrow()` between arrow categories;
- product functors built componentwise;
- comma-category functors induced from functors on their entries;
- diagram postcomposition by `F`;
- restrictions and lifts through property subcategories.

The kernel derives standard induced object and arrow maps from the supplied functor. The
construction owner states any new natural transformations or isomorphisms that compare
composites.

### Image and realization functors

The image of `F : C -> D` and its essential image are categories with inclusion functors
into `D`. The original functor factors through its image.

Mathlib treats the essential image as the full subcategory for the object property
`F.essImage`. That property is closed under isomorphisms. See
[Mathlib's essential-image API](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/EssentialImage.html).

A realization or presentation can instead be an equivalence, a fully faithful functor,
or an arbitrary functor. Its actual functor properties determine the case. The word
“realization” does not define a structural edge.

## Naming rules

Use the shortest standard name that identifies the mathematical construction:

- use `inclusion` for a category's canonical inclusion;
- use `inclusion_of_le` for the inclusion induced by implication between object
  properties;
- use `forget` for the canonical functor to the final underlying category;
- use `forget_to_<category>` when several forgetful targets exist;
- use `fst` and `snd` for product-category projections;
- use `left` and `right` for arrow-category projections;
- use `proj` for the canonical structured-arrow projection;
- use `lift` for factorization through a property subcategory;
- use `inverse_image` for pulling a property back along a functor.

Use a longer category-qualified name when the short name is ambiguous. Do not encode
fullness, faithfulness, repleteness, or equivalence in the functor's public name unless
the name denotes the corresponding standard inclusion constructor.

The reusable kernel constructors use the Python names
`SubcategoryInclusionFunctor`, `FullSubcategoryInclusionFunctor`, and
`WideSubcategoryInclusionFunctor`. Category APIs can expose the resulting functors under
the standard names above.

## Functor properties

Fullness, faithfulness, essential surjectivity, and preservation properties are
mathematical properties of a functor. They are not substitutes for the functor.
Repleteness is a property of a subcategory or its defining object property.

Mirror Mathlib's distinctions:

| Property | Meaning |
| --- | --- |
| `F.Faithful` | Each map on homs is injective. |
| `F.Full` | Each map on homs is surjective. |
| `F.FullyFaithful` | `F` is full and faithful, with the required hom preimages. |
| `F.EssSurj` | Every target object is isomorphic to an image object. |
| `F.IsEquivalence` | `F` is full, faithful, and essentially surjective. |
| `F.ReflectsIsomorphisms` | `F` reflects isomorphisms. |
| `PreservesLimitsOfShape(J, F)` | `F` preserves limits of shape `J`. |
| `CreatesLimitsOfShape(J, F)` | `F` creates limits of shape `J`. |

Mathlib defines `Full` and `Faithful` as properties of a functor. It defines
`FullyFaithful` with the hom-preimage operation. See
[Mathlib's full-and-faithful API](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Functor/FullyFaithful.html).

In this repository, each propositional query returns a proposition. Category placement,
assumptions, and exact algorithms decide that proposition as specified in
[undecidable-properties.md](undecidable-properties.md).

Specialized constructors can place a functor directly in the strongest established
property category. They do not create parallel functor implementations.

## Property subcategories and repleteness

An object property `P` defines a full subcategory when it retains every ambient arrow
between objects satisfying `P`.

Repleteness adds this condition:

```text
P(X) and X isomorphic to Y imply P(Y).
```

This condition belongs to the object property and source category. It does not change
the inclusion's object or arrow map.

Therefore, finite sets use:

```python
iota = FullSubcategoryInclusionFunctor(Sets().Finite(), Sets())
```

The `Finite` property states closure under isomorphism. A separate
functor type is not required. Repleteness changes the source object property, not the
inclusion map.

Mathlib follows this split. It uses `ObjectProperty.ι` for the full-subcategory
inclusion. It uses `ObjectProperty.IsClosedUnderIsomorphisms` for repleteness. See
[Mathlib's object-property API](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/ObjectProperty/CompleteLattice.html).

A property refinement can also restrict arrows. In that case, use
`SubcategoryInclusionFunctor`, not `FullSubcategoryInclusionFunctor`.

## Derived functors

Mathlib supplies standard operations around property subcategories:

- `ObjectProperty.ι` includes a full property subcategory;
- `ObjectProperty.ιOfLE` includes a stronger property into a weaker property;
- `ObjectProperty.lift` lifts a functor whose image satisfies a property;
- `ObjectProperty.inverseImage` pulls an object property back along a functor;
- `MorphismProperty.inverseImage` pulls a morphism property back along a functor.

The kernel should supply the corresponding constructions. A leaf states the property,
the functor, and the established category placement. It does not implement restriction
or lift wiring.

For selected `F : D -> C` and property `P` on `C`, the inverse-image category is:

```text
D.P = {X in D | P(F(X))}.
```

The kernel derives the restricted functor `D.P -> C.P`. It records the comparison with
the composite through `D` and `C`.

## Examples

### Finite sets

Finite sets form a full replete property subcategory of sets:

```python
class Finite(FullRepletePropertySubcategory):
    def structure_functors(self) -> tuple[Functor, ...]:
        iota = FullSubcategoryInclusionFunctor(self, Sets())
        return (iota,)
```

The declaration lists the inclusion explicitly. The inclusion constructor supplies its
canonical object and arrow maps.

### Monoids

`Monoids()` is notation-neutral. It is a subcategory of `Magmas()` because its arrows
also preserve the neutral element:

```python
class MonoidsCategory(Category):
    def structure_functors(self) -> tuple[Functor, ...]:
        return (SubcategoryInclusionFunctor(self, Magmas()),)
```

The additive and multiplicative axiomatic refinements preserve the neutral monoid and
the selected notation branch. See
[Magmas, monoids, and semirings](magmas-monoids-semirings.md).

### Pointed sets

A pointed set is a pair `(X, x)` with `x in X`. Distinct points give distinct pointed
sets with the same underlying set. The structural edge is forgetful:

```python
class PointedSetsCategory(Category):
    def structure_functors(self) -> tuple[Functor, ...]:
        carrier = ProductProjectionFunctor(0, self, Sets())
        return (carrier,)
```

The selected projection supplies the underlying set surface. The point remains defining
data. No leaf-defined functor class or map methods are required.

See [poset-minimal-template.py](poset-minimal-template.py) for the complete minimal
shape of a structured category with a selected kernel-owned carrier projection to
`Sets()`.

### Product and arrow categories

For categories `C` and `D`, the product category owns `fst : C × D -> C` and
`snd : C × D -> D`.

The arrow category `Ar(C)` owns `left : Ar(C) -> C` and `right : Ar(C) -> C`. The
arrow itself is a natural transformation from `left` to `right`.

These functors exist independently of structural selection. A category places them in
`structure_functors()` only when they define its intended inherited surface.

## Compiler contract

The compiler uses `structure_functors()` as the sole structural graph.

It must:

1. require each entry to be an owned `Functor`;
2. require each entry's domain to be the declaring category;
3. derive immediate target categories from functor codomains;
4. build longer paths by functor composition;
5. preserve the exact functor and its maps on every edge;
6. apply the selected object, arrow, and element maps;
7. reject transport when the selected functor lacks the required role map;
8. resolve diamonds under [resolution.md](resolution.md);
9. canonicalize repeated construction of the same declared functor;
10. derive all inherited methods from these paths.

The compiler must not infer a functor from a category pair. It must not infer fullness,
faithfulness, repleteness, or equivalence from a class name.

## Mathlib correspondence

Use Mathlib's mathematical divisions and names as the primary precedent:

Mathlib does not use one generic “supercategory edge.” It constructs functors from
object properties, morphism properties, concrete forgetful structure, and the category
construction that owns a projection. This repository follows that division.

| Mathlib | Repository spelling |
| --- | --- |
| `Functor` | `Functor` |
| `Functor.id` | `IdentityFunctor` or the category-owned identity |
| `ObjectProperty.ι` | `FullSubcategoryInclusionFunctor` |
| `ObjectProperty.ιOfLE` | `inclusion_of_le` |
| `ObjectProperty.lift` | `lift` through a property subcategory |
| `wideSubcategoryInclusion` | `WideSubcategoryInclusionFunctor` |
| `forget`, `forget₂` | Kernel-owned `ForgetfulFunctor`, exposed through the source category |
| `Prod.fst`, `Prod.snd` | Product-category `fst`, `snd` |
| `Comma.fst`, `Comma.snd` | Comma-category `fst`, `snd` |
| `Arrow.leftFunc`, `Arrow.rightFunc` | Arrow-category `left`, `right` |
| `Over.forget` | Over-category `forget` |
| `StructuredArrow.proj` | Structured-arrow `proj` |
| `Full`, `Faithful`, `FullyFaithful` | Functor property categories and propositions |
| `EssSurj`, `IsEquivalence` | Functor property categories and propositions |

The repository uses Python names that preserve these nouns. It does not copy Lean's
typeclass implementation.

## Acceptance conditions

- Every structural edge is an explicit functor.
- Every category declares its complete tuple of immediate structural functors.
- No independent `super_categories()` graph exists.
- Inclusion, fullness, wide inclusion, forgetting, and projection remain distinct.
- Repleteness is an isomorphism-closure property of the source category.
- Functor properties remain propositions about a functor.
- Ordinary functors do not contribute methods unless selected.
- Leaves do not own structural-functor caches or registries.
- Leaves do not implement standard functor object, element, or arrow maps.
- The compiler derives paths only by functor composition.
- Finite sets declare one full-subcategory inclusion into sets.
