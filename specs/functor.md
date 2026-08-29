# Functors, `Cat`, and structural inheritance

## Contents

- [`Cat` and its implementation](#cat-and-its-implementation)

- [Functors as morphisms of `Cat`](#functors-as-morphisms-of-cat)

- [The `Mor(n, C)` tower](#the-morn-c-tower)

- [Canonical objects of `Cat`](#canonical-objects-of-cat)

- [The core functor](#the-core-functor)

- [Functor property subcategories](#functor-property-subcategories)

- [Property resolution](#property-resolution)

- [Monomorphisms of `Cat()` and placement](#monomorphisms-of-cat-and-placement)

- [Structural inheritance](#structural-inheritance)

- [Declared categories and their implementations](#declared-categories-and-their-implementations)

- [Point categories and point functors](#point-categories-and-point-functors)

- [Functor construction and presentation data](#functor-construction-and-presentation-data)

- [Adjunctions and equivalences](#adjunctions-and-equivalences)

- [Products, coproducts, and component functors](#products-coproducts-and-component-functors)

- [Diagram shapes and universal constructions](#diagram-shapes-and-universal-constructions)

- [Comma categories, slices, coslices, and fibers](#comma-categories-slices-coslices-and-fibers)

- [Fixed-object construction categories](#fixed-object-construction-categories)

- [Indexed categories, Yoneda, and representability](#indexed-categories-yoneda-and-representability)

- [Examples](#examples)

- [Compiler contract](#compiler-contract)

- [Mathlib correspondence](#mathlib-correspondence)

- [Acceptance conditions](#acceptance-conditions)

## `Cat` and its implementation

`Cat`, the category of categories, is defined by this repository and is read as mathematics.
The kernel implements it and no leaf redefines it; the kernel is the wiring, not the mathematics.
Every category in this repository is an object of `Cat` and uses its implementation type:

```python
Category = Cat().ObjectType
```

Thus `Sets()`, `Mor(C)`, and every property subcategory are instances of `Cat().ObjectType`. They do not form a second Python category hierarchy.

Bootstrap follows the same direct class-declaration model.
A stable kernel class exists before the `Cat()` singleton.
`Cat().ElementType` keeps one public class identity throughout bootstrap.
`Cat` then declares and compiles the same three classes as every other category:

- `Cat().ObjectType` implements categories;

- `Cat().MorphismType` implements functors;

- `Cat().ElementType` implements a point `* -> C`, where `*` is the terminal category;

- `Cat()(...)` constructs categories;

- `Fun = Mor(Cat())` constructs the category whose objects are functors.

The points `* -> C` are the actual objects of `C`, so every `C.ObjectType` inherits `Cat().ElementType`. `C.ElementType` is the shared implementation and API for the elements of objects of `C`. When an object `X` is regarded as a category, its elements are points `* -> X`; a set uses its discrete, 0-truncated category. `Fun(T, X)` constructs generalized elements `T -> X`.
`C.MorphismType` is `Mor(C).ObjectType`, because a morphism of `C` is an object of the morphism category.

`Cat()` also supplies the uniform categorical constructions, defined once at that level and applicable to every category.
They are mathematics, and the kernel implements them:

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

There are two call forms on categories.
`K(data)` constructs an object of `K`. `Mor(K)(A, B)(data)` constructs a morphism `A -> B`. No spelling owns a parallel morphism construction.

## Functors as morphisms of `Cat`

A functor is a morphism in `Cat`. Define `Fun = Mor(Cat())`. Therefore, every functor is an object of `Fun`:

```python
Fun = Mor(Cat())
F = Fun(C, D)(on_object, on_morphism)
```

`Fun(C, D)(on_object, on_morphism)` requires both actions.
The inherited `Cat().MorphismType` surface supplies:

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

A point `x: * -> X` is represented by its defining functor. A functor `G: X -> Y` maps it by composition to `G after x: * -> Y`. A generalized element `T -> X` maps by the same composition to `T -> Y`. This point action belongs to `G`. Selection of a structure functor can add the applicable target element implementation to the compiled source class.

For fixed `C, D in Cat()`, the functor category is endpoint application to `Mor(Cat())`:

```python
Fun(C, D) is Mor(Cat())(C, D)
```

Its objects are functors `C -> D`. Its morphisms are natural transformations.
Natural isomorphisms are the objects of `Mor(Fun(C, D)).Isomorphisms()`.

`Fun(C, D)` is the full subcategory of `Fun` on functors with domain `C` and codomain `D`. It is a genuine full subcategory because a 2-morphism connects parallel 1-morphisms only.

### Functor actions are concrete constructors

The writer of `F: C -> D` implements two ordinary Python functions.
They are the complete mathematical and executable definition of `F`:

```python
def on_object(X: C.ObjectType) -> D.ObjectType:
    target_data = ...  # computed with the API of C
    return D(target_data)

def on_morphism(f: C.MorphismType) -> D.MorphismType:
    source = on_object(f.domain())
    target = on_object(f.codomain())
    target_morphism_data = ...  # computed with the API of C
    return Mor(D)(source, target)(target_morphism_data)

F = Fun(C, D)(on_object, on_morphism)
```

`on_object` can use arbitrary ordinary Python and every method supplied by `C.ObjectType`.
It returns an actual object built through one of the finite public constructors of `D`.
`on_morphism` returns an actual morphism built through the exact target hom category.
The writer knows the source leaf, the immediate target category, and the standard categorical calculus needed to navigate their data.

For example, an algebra presentation can retain a morphism `R -> Z(A)`.
Its functor to rings can recover `Z(A)` as the codomain and then use the ambient-object operation supplied by the generic `MonoOver` construction:

```python
def to_rings(self) -> Cat().MorphismType:
    D = Rings()

    def on_object(A):
        center = A._algebra_structure_morphism().codomain()
        return center.ambient_object()

    def on_morphism(f):
        source = on_object(f.domain())
        target = on_object(f.codomain())
        return Mor(D)(source, target)(...)

    return Fun(self, D)(on_object, on_morphism)
```

The leading underscore is required when that source helper exists only for this leaf-internal action.
A defining morphism that is itself part of the public algebra interface keeps its public mathematical name.
Local functions are preferred when no other leaf code needs the helper.

The kernel treats both functions as opaque executable actions.
Selecting `F` in `structure_functors()` only selects the applicable target implementation surface for compilation.
This is D08 and D120, with stable policy references `POL-FUN-035`, `POL-LEAF-058`, and `POL-LEAF-062`.

A natural transformation `eta: F => G` is constructed as `Mor(Fun(C, D))(F, G)(assignment)`. The assignment is a rule `X |-> eta_X` on the objects of `C`, returning a morphism `F(X) -> G(X)` of `D`. It is never a table.
Naturality is trusted.

## The `Mor(n, C)` tower

For every category `C` and every `n >= 0`, `Mor(n, C)` is the category whose objects are the `n`-morphisms of `C` and whose morphisms are the `(n+1)`-morphisms of `C`:

- `Mor(0, C) = C`;

- `Mor(C) = Mor(1, C)`;

- `Mor(n+1, C) = Mor(Mor(n, C))`.

`C.ObjectType` implements the objects of `Mor(0, C)`. `C.MorphismType` implements the objects of `Mor(1, C)`. Therefore `Mor(n, C).ObjectType` is `Mor(n-1, C).MorphismType`: one implementation type, one value, two category placements.

For a 1-category `C`, every 2-morphism is an identity, so `Mor(C)` is discrete.
`Cat()` is a strict 2-category: categories are the objects of `Mor(0, Cat())`, functors are the objects of `Mor(1, Cat())`, and natural transformations are the objects of `Mor(2, Cat())` and the morphisms of `Fun`.

Applying `Mor(C)` to endpoints `A, B` selects the full subcategory of `Mor(C)` on the morphisms with domain `A` and codomain `B`. One cached object exists per `(A, B)`. This is distinct from `Mor(Mor(C))(f, g)`, the category between two objects of `Mor(C)`.

The construction is uniform.
In particular:

- objects of `Mor(Sets())` are set maps, and `Mor(Sets())(X, Y)` is discrete on the maps `X -> Y`;

- objects of `Mor(Cat())` are functors;

- objects of `Mor(Fun(C, D))` are natural transformations.

The category whose objects are the morphisms of `C` and whose morphisms are commuting squares is not a primitive.
It is the functor category `Fun([1], C)` from the walking arrow `[1]`. Its evaluation functors `ev_0, ev_1: Fun([1], C) -> C` supply the domain and codomain projections.
In general, evaluation at `i in I` is the construction-named functor `Fun(I, C) -> C`.

The related property categories use the same mechanism:

```python
Mor(C).Monomorphisms()
Mor(C).Epimorphisms()
Mor(C).Isomorphisms()
Mor(C).Automorphisms()
```

Each is a property subcategory of an owned morphism category.
Each property has its owned predicate, construction dispatcher, assumption route, the property subcategories it is a full subcategory of, and optional computational routes.
Fixed endpoints use the same dispatch for every property subcategory `P` of `Mor(K)`: `P(A, B)` is `Mor(K)(A, B).P()`, one cached object.

## Canonical objects of `Cat`

`Cat()` owns these objects, each constructed once and retained by identity:

- `Groupoids()`: the category of groupoids, declared as a point of `Cat`; the current foundation requires no further implementation of groupoid theory;

- `Cat().Initial()`: the empty category;

- `Cat().Terminal()`, written `1` and equal to `[0]`;

- `Cat().Simplex(n)`, written `[n]`: the poset `0 < 1 < ... < n` as a category, for `n >= 0`; `[1]` is the walking arrow, `[2]` the walking commutative triangle;

- `Cat().WalkingSpan()`: the free category on `0 <- 1 -> 2`;

- `Cat().WalkingCospan()`: the free category on `0 -> 1 <- 2`;

- `Cat().WalkingIsomorphism()`: two objects and two mutually inverse morphisms;

- `Cat().WalkingParallelPair()`: two objects and two parallel morphisms;

- `Cat().Point(X)`, written `{X}`: the one-object category on a distinguished object `X`, one per `X`; see [Point categories and point functors](#point-categories-and-point-functors).

Two calls return one object by identity.
No construction creates a second terminal object, simplex, or walking structure.

### Separators and separating families

A category may choose a family of objects whose generalized elements determine its morphisms.
[nLab, separator](https://ncatlab.org/nlab/show/separator) (inspected 2026-08-28) names it: a family `S = (S_a)_{a in A}` is a "separating family or a generating family" when "for every pair of parallel morphisms `f, g : X -> Y`, if `f . e = g . e` for every `e : S_a -> X` sourced in the family, then `f = g`", and for locally small `C`, "`S` is a separating family if the family of hom functors `Hom(S_a, -) : C -> Set` (for `a in A`) is jointly faithful".
The one-element case is a separator: "`S` is a separator if the hom functor `Hom(S, -) : C -> Set` is faithful."

No category declares its separating family (`D100`). Separation is a theorem, and a tuple returned at runtime is that theorem as metadata, which `POL-MATH-031`, `POL-MATH-032`, and `POL-MATH-045` exclude.
A category that needs the hom functor of a generator `G` constructs it where the theorem lives:

```python
Fun(C, Sets()).Faithful()(on_object, on_morphism)
```

Constructing `Mor(C)(G, -)` in the faithful subcategory is the assertion that `G` separates `C` (`POL-MATH-037`); nothing verifies it and nothing reads a second declaration of it.
A separating family of several is a family of hom functors that is jointly faithful, so it is a family of such constructions and not one set-valued functor.
The uses this repository has for generators — presentations, restricted Yoneda functors, density, and evaluation epimorphisms — are named mathematical constructions, recorded in [Separating families and categorical generators](separating-families-and-categorical-generators.md).

Points do not travel through a separator. A point `* -> X` travels along a named functor with domain `X` by ordinary composition.

## Functor property subcategories

Functor properties are property subcategories of `Fun`:

```python
FullFunctors = Fun.Full()
FaithfulFunctors = Fun.Faithful()
FullyFaithfulFunctors = Fun.FullyFaithful()
EssentiallySurjectiveFunctors = Fun.EssentiallySurjective()
EquivalenceFunctors = Fun.Equivalences()
```

Fixed endpoints commute with property refinement.
For example:

```python
Fun(C, D).Full() is Fun.Full()(C, D)
Fun(C, D).Faithful() is Fun.Faithful()(C, D)
Fun(C, D).FullyFaithful() is Fun.FullyFaithful()(C, D)
```

Each identity denotes one cached property subcategory.
A constructor called through it returns a functor with endpoints `C, D` and the selected trusted property.

The axiom declarations give the kernel their names and their ambient category `Mor(Cat())`.
The kernel generates these applications on `Cat().MorphismType`:

```python
F.is_full()
F.is_faithful()
F.is_fully_faithful()
F.is_essentially_surjective()
F.is_equivalence()
```

Each call returns the containment proposition of its property subcategory.

For `F: C -> D`:

- `Full(F)` states that every morphism `F(X) -> F(Y)` has a preimage under `F.on_morphism()`;

- `Faithful(F)` states that each map on morphisms is injective;

- `FullyFaithful(F)` is the conjunction of fullness and faithfulness;

- `EssentiallySurjective(F)` states that every object of `D` is isomorphic to an image of an object of `C`;

- `Equivalence(F)` states that `F` is fully faithful and essentially surjective.

These are properties of the named functor `F`, not properties of `C` or `D` alone.
Use `Faithful` for injectivity on each fixed-endpoint morphism collection, `Full` for
surjectivity, and `FullyFaithful` for bijectivity. Use `EssentiallySurjective` for object
coverage up to isomorphism. These standard terms replace strict object counts and an
ambiguous global claim that a functor is bijective on morphisms.

These definitions introduce no selected witnesses.
A separate construction can select a preimage morphism, inverse functor, unit, or counit when an operation requires that data.

These property subcategories contain one another, and each containment is the
monomorphism presenting it (D83):

```text
Fun.FullyFaithful() is a full subcategory of Fun.Full()
Fun.FullyFaithful() is a full subcategory of Fun.Faithful()
Fun.Full().Faithful() is Fun.FullyFaithful()
Fun.Equivalences() is a full subcategory of Fun.FullyFaithful()
Fun.Equivalences() is a full subcategory of Fun.EssentiallySurjective()
```

The containment is the statement, and nothing induces it from a relation between
predicates. `Fun.Equivalences()` is a full subcategory of `Fun.FullyFaithful()` the same
way `Sets().Finite()` is one of `Sets().Countable()`; "fully faithful implies full" is
set-theoretic logic and has no category-theoretic formulation. `Axiom`'s
`full_subcategory_of` is where a category states it (`cat/properties.py`).

## Property resolution

Functor properties use the general `Predicate`, `ask()`, and property-refinement framework.
They have no separate evidence or decision system.

An existing functor can enter a property category by direct construction:

```python
F = Fun(C, D)(on_object, on_morphism)
F = Fun(C, D).Full()(F)
```

This category call asserts the property and supplies an existing owned functor.
The code writer uses external mathematics to select `Fun(C, D).Full()`. The kernel records that assertion by refining the same owned functor.
It does not prove, certify, or check fullness.

An interactive assumption uses the same predicate and refinement:

```python
F = Fun(C, D)(on_object, on_morphism)
assume(F.is_full())
```

A code writer who knows a property from the defining construction places the result directly in the corresponding property category.
For example, the monomorphism of a full subcategory is constructed in `Fun(C, D).FullyFaithful()`.

Put a citation on the construction line or in its immediate source documentation when the property uses a nontrivial external theorem.
The citation supports mathematical audit.
It is not runtime data and the constructor does not inspect it.

The functor-property categories register no computational routes.
Therefore:

```python
ask(F.is_full())
```

uses category placement, active assumptions, and declared subcategory containments.
It returns `Unknown` when none establishes the proposition.

This rule is specific to categorical functor properties.
Other owned predicates, such as injectivity of a set map on a declared semantic domain, can register exact computational routes.

## Monomorphisms of `Cat()` and placement

### The two conditions

A subcategory of `T` is a subobject of `T` in `Cat()`: an isomorphism class of monomorphisms into `T` ([nLab, subobject](https://ncatlab.org/nlab/show/subobject), inspected 2026-08-28; "an isomorphism class of monomorphisms"). Two conditions apply, and the kernel needs both.

**Monic.** [nLab, subcategory](https://ncatlab.org/nlab/show/subcategory) (inspected 2026-08-28): "subcategories of a category `C` can be identified with isomorphism classes of monic functors into `C`. A functor is easily verified to be monic iff it is faithful and injective on objects."
[nLab, full embedding](https://ncatlab.org/nlab/show/full+embedding) (inspected 2026-08-28) names the same class: "Embeddings in this sense are straightforwardly the same thing as monomorphisms in the 1-category `Cat`", and a full embedding is a monomorphism in `Cat` that is also full, hence fully faithful.
So the owned property is `Fun.Monomorphisms()`, and the monomorphism of a full subcategory is an object of `Fun.Monomorphisms().Full()`. `Fun` needs no further property for this.

**Replete.** Monicity alone is not enough, because a skeleton satisfies it.
`Cardinal()` selects one representative set per cardinal; its functor to `Sets()` is fully faithful and injective on objects, hence monic, hence an embedding.
A cardinal is still not a set.
The condition that separates them is repleteness of the image: [Kerodon, Example 4.4.1.12](https://kerodon.net/tag/01EX) (inspected 2026-08-28) states that a subcategory is replete exactly when an isomorphism of `C` with one endpoint in the subcategory has its other endpoint and itself in the subcategory, and that this holds exactly when **that monomorphism is an isofibration**. [nLab, replete subcategory](https://ncatlab.org/nlab/show/replete%2Bsubcategory) (inspected 2026-08-28) states why this is the right condition: a replete subcategory "is a subcategory for which the property of (strictly) belonging to it respects the principle of equivalence of categories."

`Sets().Finite()` is replete: a set isomorphic to a finite set is finite.
Every property subcategory whose defining predicate is an isomorphism invariant is replete for the same reason.
A skeleton is the opposite extreme and is replete only when it is everything.

### Placement traces monic isofibrations

`x in C` asks `C`'s membership proposition (`POL-CAT-043`, `POL-CAT-044`). Placement is a positive shortcut inside that one question: construction or same-object refinement into the property category already established the defining predicate, so `ask()` answers from placement without recomputing (`POL-CAT-068`). Placement propagates from `S` to `T` exactly along a functor that is a monomorphism of `Cat()` and an isofibration.
Monicity gives one value rather than a copy; repleteness makes the resulting membership statement invariant, so an object of `Sets().Finite()` is an object of `Sets()` while a cardinal is not a set.

The choice is data.
`Cardinal() -> Sets()` and `Sets().Finite() -> Sets()` are both monic, and nothing derives which one placement follows: nLab, *subobject*, states that for representatives of a subobject "there is no intrinsic way of defining such representatives".
A leaf therefore declares which monomorphism placement follows by constructing it in the property category below, and the kernel trusts that declaration (`POL-CAT-069`). It does not infer the relation from Python inheritance, shared storage, or a cache of previously constructed functors.

### Declaring one

`Fun.Monomorphisms()` and `Fun.Isofibrations()` are the two owned properties, so the declaration is an ordinary construction in the property category their intersection names:

```python
iota = Fun(S, T).Monomorphisms().Isofibrations()()
```

The leaf writer states that `S` is a subcategory of `T` by constructing there.
The kernel does not compute that relation from Python inheritance or shared storage, and it does not recognize the functor by consulting a table of ones it built earlier.

A full subcategory adds fullness, so a property subcategory `C.P()` declares:

```python
iota = Fun(C.P(), C).Monomorphisms().Isofibrations().Full()()
```

The defining object predicate selects the objects, and it is an isomorphism invariant, so `C.P()` is replete and the functor is an isofibration.
The morphism categories `Mor(C)(A, B)`, identities, and composition are inherited from `C`.

A property subcategory can be contained in another, `C.P()` in `C.Q()`. That containment
is the same declaration between them (D83):

```python
iota = Fun(C.P(), C.Q()).Monomorphisms().Isofibrations().Full()()
```

The containment is the statement. Nothing induces it from a relation between the
predicates, and `P(X) ⟹ Q(X)` is set-theoretic logic with no category-theoretic
formulation. `Axiom`'s `full_subcategory_of` is where `C` states it, and its
fixed-endpoint functor category owns the construction.

### The core functor

`Groupoids()` is a declared point of `Cat()`. This foundation needs only that declaration.

Let

```text
U: Groupoids() -> Cat()
Core: Cat() -> Groupoids()
```

where `U` is the inclusion. For every `C in Cat()`, `Core.on_object(C)` is written
`C.Core()`. It has the objects of `C`, and its morphisms are the isomorphisms of `C`.
For `F: C -> D`, `Core.on_morphism(F)` restricts `F` to these isomorphisms.

The inclusion

```text
epsilon_C: U(C.Core()) -> C
```

is the component at `C` of the natural inclusion `U * Core => End_Cat(Cat()).one()`.
The construction retains this functor. It is faithful, monic, and an isofibration.

`Core(C)` is not `Mor(C).Isomorphisms()`. The latter has the isomorphisms of `C` as
objects and lies one categorical level higher. It can state which arrows occur in the
core, but it is not the core.

The public API has no generic `WideSubcategory` construction. Do not reintroduce one
unless a later user decision requires it. State category relations through their named
structure functors and the standard functor properties above.

## Structure functors and inherited classes

`structure_functors()` replaces Sage's `super_categories()` declaration.
Each entry is an ordinary functor and is called a structure functor because the kernel
uses it for class inheritance. This use adds no new kind of morphism in `Cat`.

Every entry is an ordinary owned object of `Fun`. Its mathematical existence and
properties come first. A structure functor need not be a subcategory monomorphism.
For example, the functor from posets to sets forgets the order. A poset is not thereby an
object of `Sets()`, and `Posets()` is not thereby a subcategory of `Sets()`.

The fixed-endpoint category `Fun(C, D)` owns construction of every functor `C -> D`.
`Cat()` supplies the categorical calculus but does not construct or choose a leaf-specific
functor. A leaf either returns the exact functor retained by its defining categorical
construction or constructs its new action in `Fun(self, Target)`. In the second case the
leaf supplies complete executable object and morphism actions. Each action computes with
the source API and directly returns a value built through the target category's public
constructors. The kernel compiles the selected target surface. It derives nothing from the
function bodies.

This ownership also fixes discovery:

```python
H = Fun(C, D)
H(...)                         # construct a functor C -> D
H.Monomorphisms()(...)         # construct a monic functor C -> D
H.Monomorphisms().Full()(...)  # construct a full monic functor C -> D
```

Named convenience constructors belong to `H` or one of its property subcategories.
There is no parallel `Cat`, kernel, or helper constructor for the same functor
(`POL-LEAF-061`, `POL-API-028`).

A category returns an immediate structure functor when that exact functor supplies inherited operations:

```python
class FiniteSetsCategory(Category):
    def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
        return (Fun(self, Sets()).Monomorphisms().Isofibrations().Full()(),)
```

This example explicitly constructs a subcategory monomorphism and records fullness through the selected property category.
The tuple tells the compiler to include the compiled classes owned by `Sets()` through that functor.

The categories `Fun(self, D)` can contain many other functors.
Their existence does not affect the compiled public surface.
Use as a structure functor changes compiler behavior only.
It does not change a functor's mathematical definition.

Each category lists only immediate structure functors.
The kernel supplies their target classes as immediate dynamic bases. Sage dynamic-class
construction and Sage's controlled linearization handle transitive inheritance and shared
ancestors.

### Private Sage implementation categories

For each owned category `C` and each of its three implementation-class kinds, the kernel
constructs one private Sage category:

```python
_RuntimeImplementationCategory(C, ImplementationKind.OBJECT)
_RuntimeImplementationCategory(C, ImplementationKind.ELEMENT)
_RuntimeImplementationCategory(C, ImplementationKind.MORPHISM)
```

This adapter exists only to compile Python classes. It states no subcategory relation in
`Cat()`.

Its `super_categories()` method returns the private implementation categories for the
immediate targets supplied by `C.structure_functors()`. Its `ParentMethods` provider is
the corresponding local `C.ObjectType`, `C.ElementType`, or `C.MorphismType` declaration.
The kernel uses only its Sage `parent_class`.

Sage `_all_super_categories`, `_super_categories_for_classes`, `_make_named_class`,
controlled C3, and `dynamic_class` therefore own class linearization, the minimal direct
bases, dynamic-class identity, and method-source metadata. The kernel does not maintain a
second class graph.

The adapter cache uses the identity of `C` and the exact implementation-class kind.
Owned category equality is proposition-valued, so this cache uses `MonoDict`. The kernel
normalizes identities such as `Mor(C).ObjectType = C.MorphismType` before lookup and
anchors each graph at its existing kernel base class.

The kernel retains four tasks that Sage cannot infer:

- reject one public method name owned by incomparable mathematical categories;

- rebind a copied method whose zero-argument `super()` still names the provider class;

- make the target implementation state available on each selected source surface;

- initialize each class in the compiled MRO once.

Public application of a functor still constructs its owned image. The private Sage graph
does not construct or identify public functor images.

### `C.ObjectType`, `C.ElementType`, and `C.MorphismType`

A category specifies `C.ObjectType`, `C.ElementType`, and `C.MorphismType` directly.
The kernel constructs these classes dynamically from the structure functors.
For each structure functor `F: C -> D`, `C.ObjectType` inherits `D.ObjectType`.
`C.ElementType` and `C.MorphismType` inherit the corresponding target classes when that
class kind applies. This applicability is a compiler consequence of selection and adds no
functor-writer declaration. A class with no structure-functor target inherits the kernel
base for its mathematical kind. A leaf never constructs this inheritance.

The kernel preserves the body specified for each class. Each category has exactly one
`C.ObjectType`, one `C.ElementType`, and one `C.MorphismType`.

Each local constructor accepts only the exact data introduced by its category.
It initializes that state and calls `super().__init__()` once.
The ordinary object action of `F` uses one of the finite public constructors of `D` and
returns the resulting `D.ObjectType`. Its morphism action does the same in the exact target
hom category. Ordinary functors that are not selected do not participate in class construction.

The structured source instance carries the state required by every class in Sage's MRO.
A shared ancestor occurs once and its initializer runs once. Each local constructor
receives only its own datum and contributes its state once.

Every object-class constructor initializes `Cat().ElementType` with its point into the parent category.
Thus `C.ObjectType` represents a point `* -> C`. A morphism uses the same object rule through `Mor(C).ObjectType`, as a point `* -> Mor(C)`. A `C.ElementType` value has parent `X in C` and uses the shared element implementation owned by `C`.

Public `F(x)` runs the named functor's ordinary action and returns the separate image owned by `F`.
Different functors with the same endpoints can return different images.

An inherited method runs directly on the structured source instance through ordinary Python inheritance.
The target constructor already initialized the state that the method reads on that instance.
Thus `x.f()` and `F(x).f()` have the same mathematical value.
The equality is semantic; method dispatch does not replace `x` with `F(x)`.

Identity and composite structure functors use their ordinary functor actions.

For a category `X`, `Fun(*, X)` models its points and `Fun(T, X)` models its generalized elements with domain `T`. A functor `G: X -> Y` maps both by composition. The category `Fun([1], X)` models arrows of `X` separately.

An ambient functor `F: C -> D` maps objects and morphisms of `C`. Selecting `F` for compiled inheritance adds the applicable target implementation classes to the source classes. This compiler effect adds nothing to the public functor definition.

## Category classes and category-valued families

A category is constructed by its category class. The class declares its nested
`ObjectType`, `ElementType`, and `MorphismType`, its constructors, and its immediate
structure functors. The kernel compiles those declarations on the resulting object of
`Cat()`.

```python
class Sets(Cat().ObjectType):
    class ObjectType: ...
    class ElementType: ...
    class MorphismType: ...

    def structure_functors(self): ...
```

A category family is a functor into `Cat()` when its mathematics gives object and morphism
actions. For example, `Discrete: Sets() -> Cat()` maps a set to its discrete category, and
`MonoidObjects: Cat() -> Cat()` maps a category to its category of monoid objects.
Their functoriality comes from these actions.

A constant category such as `Sets()` needs only its category class. A parameterized
category such as `Modules(R)` uses its mathematical parameter in its category constructor.
A one-object category such as `{X}` uses the point-category construction in the next
section.

Generic kernel and `cat` modules accept ambient categories as arguments. They do not import
production leaves. A category construction fails when its own class declaration,
constructor, or functor action is incomplete.

## Point categories and point functors

For a distinguished mathematical object `X`, `Cat().Point(X)`, written `{X}`, is the one-object category whose sole object is `X` and whose sole morphism is `1_X`. It is an object of `Cat()`, retained once per `X`, and it owns the declarations specific to `X` (`POL-CAT-083`).

A **point functor** of `X` is the monomorphism of `{X}` into a category `D` that has `X` among its objects:

```python
iota = Fun(Cat().Point(X), D).Monomorphisms().Isofibrations()()
```

`{X}` has one hom category, so every functor out of it is faithful.
A point functor is full exactly when `X` has no nonidentity endomorphism in `D`; a construction that establishes this states it by building the functor in `Fun({X}, D).FullyFaithful()`.

The endpoint pair selects the category `Fun({X}, D)`, as for every other functor.
The distinguished object `X` is the construction data.
`X` retains the category placement it already has; each point functor states one further placement of `X` as an object of `D`.

`{X}` selects its point functors by the ordinary declaration:

```python
# Cat().Point(X)
def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
    return (Fun(self, D).Monomorphisms()(),)
```

A point functor becomes a structure functor only through this declaration.
It lies in `.Isofibrations()` only when its image is [replete](glossary.md#inspected-sources) in `D` (`POL-FUN-036`). Like every structure functor, it contributes the applicable target classes and inherited public methods (`POL-FUN-003`, `POL-FUN-035`). Its target classes become immediate dynamic bases. Their own bases supply Sage's transitive MRO.

The point placement supplies each structure-functor target class's state and methods.
The distinguished object keeps its identity and existing category placement.
Existing descendants and values keep their public class identity and behavior.

Refinement is what makes a point category formed from a runtime object work.
`Cardinal()` is constructed before `Semirings(Cat())` exists and receives its semiring surface when `Cat().Point(Cardinal())` declares its point functor.
No eager construction order between `Cardinal()` and `Semirings(Cat())` is required.

The point `* -> C` represented by an object is distinct from a selected monomorphism `{X} -> D`. For `{C} -> D`, selection makes `D.ObjectType` state available on `C` and `D.ElementType` state available on the actual objects of `C`. The functor's ordinary morphism action returns the image of the sole morphism of `{C}`.

### The level shift

Take the distinguished object to be a category `C`. Then `{C}` has one object at the `Cat()` level, while `C` has its own objects and morphisms one level below.
`Cat().ElementType` models the points `* -> C`, which are exactly the actual objects of `C`.

A point structure functor `{C} -> D` therefore compiles as:

| Surface of `D` | Surface it supplies |
| --- | --- |
| `D.ObjectType` | the category `C` itself, a `Cat().ObjectType` value |
| `D.ElementType` | `C.ObjectType`, the points `* -> C` |
| `D.MorphismType` | `{C}.MorphismType`, whose sole value is `1_C` |

The shift follows from the element relation in `Cat`. It adds no second inheritance mechanism, no route normalization, and no propagation registry.
`C` remains an object of `Cat()`, `{C}` remains a distinct object of `Cat()`, and `C.structure_functors()` continues to state the structure of `C` as a category.

`Cat().Point(C)` gives the point category `{C}` without adding another declaration to `C`.

A level shift contributes the corresponding target class to each affected public class.
The point structure functor supplies its ordinary object and morphism actions.
Thus `C`, its objects, and `1_C` carry the state required by their target classes.

Shared target classes follow Sage dynamic-class construction and occur once in Sage's MRO.

### Ambient algebraic categories

An algebraic category takes its ambient category as an argument.
Thus `Semirings(A)` classifies semiring objects whose underlying objects, addition, multiplication, zero, one, and laws live in `A`. For example, `Semirings(Sets())` has underlying sets and set maps.
`Semirings(Cat())` has underlying categories and functors.
A category-valued distinguished object therefore uses a point functor into `Semirings(Cat())`.

`Semirings(Cat())` is the category of strict internal semiring objects.
Associativity, units, symmetry, distributivity, and absorption are equalities of functors, exactly as `Semirings(Sets())` states them as equalities of maps.
`Cat()` supplies the finite products those functors are formed over.

Its cardinal consumer satisfies that strictness by construction.
`Cardinal()` is skeletal (`POL-SET-025`), so addition and multiplication each select one representative and `(a + b) + c` and `a + (b + c)` are one object.
The equality of functors therefore holds on objects and on morphisms.

A category-valued semiring whose underlying category is not skeletal is outside this definition.

## Functor construction and presentation data

`Fun(Source, Target)` owns construction of functors with those endpoints.
The endpoint pair selects that category.
It does not select an object of it.

Construct a functor from its complete actions:

```python
F = Fun(Source, Target)(on_object, on_morphism)
```

When the defining mathematics establishes faithfulness, construct it in that property category:

```python
F = Fun(Source, Target).Faithful()(on_object, on_morphism)
```

A category presentation can contain several projections or evaluations.
Its constructor creates each one through the applicable `Fun(Source, Target)` category.
The presentation then retains those distinct functor objects as defining data.

### Construction-named functors

There is no generic functor selected by the instruction to “forget structure.”
The source and target select only `Fun(Source, Target)`. They do not select one of its objects.
A category presentation can expose several valid maps, and an equivalent presentation can expose different immediate maps.

For example, a lattice presentation `(M, b)` has one projection to `M` and another to `b`. A module presentation by an action morphism has the projections and evaluations of its chosen action-category construction.
The kernel cannot recover a preferred map from tuple positions, field names, or a supposed underlying object.

Each public functor must name its construction.
The fundamental cases are:

| Construction | Functor or morphism supplied |
| --- | --- |
| subcategory or property subcategory | its specified monomorphism |
| product category | each `product_projection(i)` |
| coproduct category | each `coproduct_injection(i)` |
| functor category `Fun(I, C)` | each evaluation `ev_i: Fun(I, C) -> C`; for `Fun([1], C)`, `ev_0` and `ev_1` |
| slice or coslice presentation | its pullback projections; the varying object is the composite with `ev_0` or `ev_1` |
| Grothendieck fibration | its projection and specified cartesian lifts |
| Grothendieck opfibration | its projection and specified cocartesian lifts |
| base change | the functor supplied by pullback, pushforward, or the stated adjunction |
| left or right Kan extension | the extended functor and its universal natural transformation |
| composite construction | the ordinary composite of the supplied functors |

The dual of a Grothendieck fibration is an opfibration.
It is also called a cofibered category.
Use “cofibration” only when a cited source uses that synonym.
In other contexts, a cofibration is a class of morphisms and is a different notion.

Mathlib's `ConcreteCategory.forget` is part of a concrete-category structure.
Its `HasForget₂.forget₂` also carries a chosen functor as extra structure.
These definitions do not derive a functor from its endpoints.
This repository records the exact construction instead of defining an unnamed default.

### Functor-category calculus

For categories `A`, `B`, and `C`, `Fun.composition(A, B, C)` is the functor

\[
\operatorname{Fun}(B,C)\times\operatorname{Fun}(A,B)
\longrightarrow
\operatorname{Fun}(A,C).
\]

For categories `C` and `D`, `Fun.evaluation(C, D)` is the evaluation functor

\[
\operatorname{Fun}(C,D)\times C\longrightarrow D.
\]

Fixing one input gives precomposition and postcomposition functors. Their morphism actions give left and right whiskering. Horizontal composition of natural transformations is the corresponding composite of these actions.

The public natural-transformation operations are:

```python
eta.whisker_left(H)
eta.whisker_right(K)
eta.horizontal(theta)
```

The construction retains the associator and left and right unitor natural isomorphisms. It follows [Mathlib, whiskering](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Whiskering.html).

For `X in C`, let `End_C(X)` be the endomorphism monoid on `Mor(C)(X, X)` under composition. Its unit `End_C(X).one()` is the identity morphism of `X`. For `C in Cat()`, this gives the identity functor as `End_Cat(C).one()`.

### Subcategory monomorphisms

`Fun(S, T).Monomorphisms().Isofibrations()()` constructs an established subcategory monomorphism.
Use `Fun(S, T).Monomorphisms().Isofibrations().Full()()` when `S` is full in `T`.

### Opposites and dualization

`Op: Cat() -> Cat()` is the dualizing functor.
Its public actions are

```python
C.op()       # Op.on_object(C)
F.op()       # Op.on_morphism(F)
eta.op()     # G.op() => F.op(), for eta: F => G
```

It retains the natural isomorphism `Op compose Op ≅ Id`.
Thus duality acts on categories, functors, and natural transformations.
The limit-side constructions own the implementation: terminal objects, products, limits, slices, monomorphisms, fibrations, and right Kan extensions.
Their duals are initial objects, coproducts, colimits, coslices, epimorphisms, opfibrations, and left Kan extensions.
For example, a colimit in `C` is the opposite of the corresponding limit in `C.op()`, and a coslice is the opposite of the corresponding slice in `C.op()`.
The dualizing functor and its involutivity follow [Mathlib, `CategoryTheory.Cat.opFunctor`](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Category/Cat/Op.html); the actions on morphisms, functors, and natural transformations follow [Mathlib, `CategoryTheory.Opposites`](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Opposites.html).

### Inverse-image subcategories

Let `F: D -> C` and let `i: P -> C` present a subcategory.
The inverse-image subcategory is the pullback

\[
F^{-1}(P)=D\times_C P.
\]

The public construction is `F.inverse_image(P)`.
It retains both pullback projections.
The projection `F.inverse_image(P) -> D` is its subcategory monomorphism.
Fullness and repleteness pass from `P` to the inverse image.

For a property subcategory `C.P()`, a category declares `D.P()` as `F.inverse_image(C.P())` when the named functor `F` defines that inherited property.
The pullback owns the resulting category and both structure functors.
The axiom machinery registers the property name, and the compiler exposes the implementation classes of this pullback.
This construction is the category attached to the standard inverse image of an object property; see [Mathlib, `ObjectProperty.inverseImage`](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/ObjectProperty/Basic.html) and [its full subcategory](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/ObjectProperty/FullSubcategory.html).

For subcategories `P -> C` and `Q -> C`, their intersection is

\[
P.\operatorname{intersection}(Q)=P\times_C Q.
\]

It retains both projections and its monomorphism into `C`. Chained property refinements are iterated pullbacks. Pullback associativity supplies their coherence.

### Restrictions and change of base

Let `F: C -> D`, with subcategory monomorphisms `i: P -> C` and `j: Q -> D`. When the defining mathematics supplies a factorization of `F compose i` through `j`, `F.restrict(P, Q)` is the induced functor `P -> Q`. The leaf states the theorem that its objects and morphisms land in `Q`. The general restriction construction supplies the functor and the commuting square.

A morphism between two pullback diagrams induces the corresponding functor between their pullbacks. The pullback construction owns this action on objects, morphisms, and comparison natural transformations.

For `p: E -> C` and `F: D -> C`, `F.base_change(p)` is the pullback projection

\[
D\times_C E\longrightarrow D.
\]

It retains the other projection to `E` and the comparison square. The inverse-image subcategory is the case in which `p` is a subcategory monomorphism. Base change of a fibration retains the pulled-back cartesian lifts.

### Induced functors

A categorical construction can act on a functor.
The result is another object of `Fun`. Examples include `Fun([1], -)` maps, product functors, comma-category maps, diagram postcomposition, restrictions, inverse images, and lifts.

The construction owner supplies the induced object and morphism maps.
It also supplies any natural transformations or natural isomorphisms that compare composites.

For `K: C -> D` and `F: C -> E`, a left Kan extension supplies a functor `Lan_K(F): D -> E` and a unit natural transformation

\[
F\Longrightarrow Lan_K(F)\circ K.
\]

A right Kan extension supplies a functor `Ran_K(F): D -> E` and a counit natural transformation

\[
Ran_K(F)\circ K\Longrightarrow F.
\]

Their universal properties induce further natural transformations.
Each such transformation is a morphism in a fixed-endpoint functor category.
The Kan extension construction owns these morphisms.
A later named construction uses their functor components and ordinary composition.

### Strict, full, and essential images

For `F: C -> D`, three constructions retain different information:

| Construction | Objects | Morphisms |
| --- | --- | --- |
| `D.StrictImage(F)` | literal values `F(X)` | morphisms of `D` equal to some value `F(f)` |
| `D.FullImage(F)` | literal values `F(X)` | all morphisms of `D` between them |
| `D.EssentialImage(F)` | objects isomorphic in `D` to some `F(X)` | all morphisms of `D` between them |

The essential image is full and replete. The functor factors through it as an essentially surjective functor followed by a fully faithful inclusion. Membership records only the existential property. A selected preimage is separate data. This follows [Mathlib, essential image](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/EssentialImage).

A universal presentation contains more information than any image category. A limiting cone retains its diagram, legs, apex, and universal maps. Its apex can lie in an image subcategory without owning that presentation.

## Adjunctions and equivalences

For `F: C -> D` and `G: D -> C`, `Adjunctions(F, G)` is the category of adjunction data. An object retains

\[
\eta:\operatorname{Id}_C\Longrightarrow G\circ F,
\qquad
\epsilon:F\circ G\Longrightarrow\operatorname{Id}_D,
\]

with the triangle identities. The category is inhabited exactly when this pair admits an adjunction with the stated orientation. Selecting an object supplies the unit and counit needed by later constructions. This is the standard package in [Mathlib, adjunctions](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Adjunction/Basic.html).

A morphism in `Adjunctions(F, G)` is a pair of endotransformations of `F` and `G` compatible with the two units and counits. Composition is componentwise.

`Equivalences(C, D)` is the category of selected equivalence data. An object retains `F: C -> D`, an inverse `G: D -> C`, and the unit and counit natural isomorphisms. A morphism is a natural transformation between the forward functors. This follows Mathlib's category structure on equivalences and its functor to `Fun(C, D)`. This is distinct from membership of `F` in the property subcategory `Fun(C, D).Equivalences()`. The property stores no inverse. See [Mathlib, equivalences](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Equivalence.html).

For a shape `I`, the diagonal functor is

\[
\Delta_I:C\longrightarrow\operatorname{Fun}(I,C).
\]

When chosen `I`-limits exist, the retained limit functor `Lim_I` is a right adjoint of `Delta_I`. The selected object of `Adjunctions(Delta_I, Lim_I)` owns its unit and counit. Colimits and their adjunction derive through `Op`.

Mates under adjunctions are a later operation on this data. They do not belong to PR-8 acceptance.

## Products, coproducts, and component functors

The generic product and coproduct constructions apply to `Cat()` itself.
For a sequence of categories, construct:

```python
P = Cat().Products()((C_0, ..., C_n))
Q = Cat().Coproducts()((C_0, ..., C_n))
```

Their category-owned public functors are:

```python
P.product_projection(i)   # an object of Fun(P, C_i)
Q.coproduct_injection(i)  # an object of Fun(C_i, Q)
```

Here `P` and `Q` are the product and coproduct categories themselves: `Cat().Products()` is the full subcategory of `Cat()` on the chosen product categories.
The index is an `int` in the supplied sequence.
These methods come from `Cat().Products().ObjectType` and `Cat().Coproducts().ObjectType`. They return `Cat().MorphismType` values.

Let `P` be a product category.
Let `j: S -> P` present `S` as a subcategory.
The corresponding object of `Cat().MonoOver(P)` retains `j` and reads `P` as its codomain.
Its component functor is

\[
S.\operatorname{product\_projection}(i)=\pi_i\circ j:S\longrightarrow C_i.
\]

Thus every subcategory of a sequence product receives all component functors.
The subobject-of-product construction owns this rule.
A leaf supplies its monomorphism and selects the required component functors in `structure_functors()`.

A generic component functor need not be faithful or full.
A specialized category construction places it in a functor-property subcategory only when its defining theorem establishes that property.

Dually, every sequence coproduct category retains all injections.
Universal maps out of the coproduct use the component functors supplied by its defining cocone.

The binary operators are the two-term cases.
For categories `C` and `D`, `C * D` is the product category and `C + D` is the coproduct category.

`Fun([1], C)` retains its evaluation functors:

```python
ev_0: Fun([1], C) -> C   # the domain of a morphism
ev_1: Fun([1], C) -> C   # the codomain of a morphism
```

The generic pullback construction is `C.Limits(Cat().WalkingCospan())` (see [Diagram shapes and universal constructions](#diagram-shapes-and-universal-constructions)). Its legs are the retained projections.
The same rule handles repeated codomains.

## Diagram shapes and universal constructions

A shape is an object of `Cat()`. A diagram of shape `I` in `C` is an object of `Fun(I, C)`, constructed from an object rule and a morphism rule like every functor.
For `D: I -> C`, the index category is exactly `I = D.domain()`.
The construction retains `I` and `D`; every descendant category inherits that presentation.
For a discrete diagram on `S`, the retained `Discrete(S)` construction supplies the index set `S`.

The kernel supplies these shape constructors:

- `Discrete(S)` for `S in Sets()`: the discrete category on `S`; `Discrete` is a functor `Sets() -> Cat()`;

- the canonical objects of `Cat` above;

- `Thin.on_object(P)` for a preordered set `P`: the thin category of `P`; `omega = Thin.on_object(NN)` with its natural order is the sequential shape;

- finite presented shapes: a finite set of objects, a finite set of generating morphisms, and a finite set of relations between composable words.

A discrete diagram needs only its object rule `i |-> X_i`. The rule is an assignment on `S`; it never enumerates `S`. A Python sequence `(X_0, ..., X_n)` is the convenience form and denotes the diagram over `Discrete([n])`.

For `D: I -> C`, `Cones(D)` is the cone category. A limiting cone is a terminal object of this category. `LimitCones(D)` is the full subcategory on these objects. A selected presentation `p in LimitCones(D)` supplies:

```python
p.diagram()     # D
p.apex()        # an object of C
p.leg(i)        # p.apex() -> D(i)
p.lift(q)       # the unique cone morphism from q
```

This follows the standard cone-category description in [Mathlib, cone categories](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Limits/ConeCategory.html). Cocones and colimit cocones derive through `Op`.

For fixed `I`, the total category of limiting cones has a diagram projection to `Fun(I, C)` and an apex functor to `C`. A chosen limit functor is a section of the diagram projection followed by the apex functor. Thus the diagram, universal presentation, and apex are three distinct objects. The fiber of the apex functor over `X` is the category of limiting presentations with apex `X`.

For each nontrivial discrete shape `J`, the selected limiting cones give a product functor

\[
\operatorname{Prod}_J:C^J\longrightarrow C.
\]

`C.Products()` is the union of the full images of these chosen product functors. It is the shared apex interface for objects constructed as nontrivial products. `C.Coproducts()` is dual. The essential image gives the replete category of objects isomorphic to such chosen products. Singleton limits remain available through their standard limit construction; they do not make every object a member of `C.Products()`.

`C.Products()(diagram)` selects a product presentation `p in LimitCones(diagram)` and returns `p.apex()` placed in `C.Products()`. The presentation remains an object over the apex. A second limiting cone can have the same apex without replacing the first.

The common unambiguous case can expose `product_projection(i)` as a convenience. Code that must select among presentations uses `p.leg(i)`. The inherited default `X * Y` is `C.Products()((X, Y))`; a category-owned standard algebraic operation can override that default.

For a point `x: * -> p.apex()`, its component at `i` is the composite `p.leg(i) after x`. This construction belongs to the selected product presentation.

`C.Limits(I)` and `C.Colimits(I)` are the general families for one supplied shape `I`. The named conveniences are instances:

```python
C.Pullbacks()    is C.Limits(Cat().WalkingCospan())
C.Pushouts()     is C.Colimits(Cat().WalkingSpan())
C.Equalizers()   is C.Limits(WalkingParallelPair)
C.Coequalizers() is C.Colimits(WalkingParallelPair)
```

`C.Limits(I)` exists as a construction category for every supplied shape `I` without asserting that `C` has `I`-limits.
Constructing an object of it requires an owned limit construction of `C` for that shape, supplied universal data (an apex with its cone and mediator rule), or an exact engine construction on a declared semantic domain.

For `F: C -> D`, the shape-indexed property categories

```python
Fun(C, D).PreservesLimits(I)
Fun(C, D).CreatesLimits(I)
```

state that `F` preserves or creates `I`-limits. Their colimit forms derive through `Op`. A right adjoint preserves limits. An equivalence creates and reflects limits and colimits. These implications follow [Mathlib, adjunctions and limits](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Adjunction/Limits.html) and [Mathlib, creates limits](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Limits/Creates.html).

When a structural functor creates the required limits, its leaf states that property on the functor. The general creates-limits construction supplies the lifted cone and its universal maps. The leaf does not implement a separate lift for each named limit.

## Comma categories, slices, coslices, and fibers

For `F: A -> C` and `G: B -> C`, `Comma(F, G)` has objects `(a, b, f)` with `f: F(a) -> G(b)`. It retains its projections to `A` and `B` and the natural transformation between their composites with `F` and `G`. It is the pullback of `(ev_0, ev_1): Fun([1], C) -> C * C` along `F * G`. This is the standard comma construction in [Mathlib](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Comma/Basic.html).

`C.SliceOver(x)` and `C.CosliceUnder(x)` are the fixed-object comma categories. Equivalently, the slice is the pullback of `ev_1: Fun([1], C) -> C` along `x: * -> C`, and the coslice is the pullback of `ev_0` along `x`. Each retains its pullback projections. The varying object is the composite with `ev_0` or `ev_1`.

For the slice over `x`, an object is `(X, f: X -> x)`. The pullback projection to `Fun([1], C)` returns the defining morphism `f`; composing it with `ev_0` gives the varying object `X`, and composing it with `ev_1` gives the constant object `x`.

For the coslice under `x`, an object is `(X, f: x -> X)`. Composing the projection to `Fun([1], C)` with `ev_1` gives the varying object `X`; composing it with `ev_0` gives the constant object `x`.

Two distinct functors carry distinct lift data:

- the codomain evaluation `ev_1: Fun([1], C) -> C` is a fibration when `C` has pullbacks; the cartesian lift of `f: y -> x` at `p: z -> x` is the pullback `z *_x y -> y`, retained with both pullback projections (nLab "codomain fibration");

- the fixed slice projection `C.SliceOver(x) -> C` is the category of elements of `Mor(C)(-, x)` and a discrete fibration for every `C`; the cartesian lift of `f: y -> z` at `(z, p: z -> x)` is `f: (y, p compose f) -> (z, p)`, by precomposition, with no pullback and no hypothesis on `C` (nLab "discrete fibration").

The fiber of `ev_1` over `x` is `C.SliceOver(x)`. The total category `Fun([1], C)` and its fiber are distinct retained objects with distinct lifts.
Dually, `ev_0` is an opfibration when `C` has pushouts, with cocartesian lifts by pushout, and the fixed coslice projection `C.CosliceUnder(x) -> C` is a discrete opfibration with cocartesian lifts by postcomposition.
These properties come from the construction theorems.
They are not runtime decisions.

For any functor `p: E -> B` and point `b: * -> B`, the public fiber category is

```python
p.Fiber(b)
```

It is the pullback of `p` along `b`. Its objects lie over `b`, and its morphisms lie over the identity of `b`. It retains its inclusion into `E`; see [Mathlib, functor fibers](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/FiberedCategory/Fiber.html). A fibration adds cartesian lifts and reindexing functors. The fiber exists before this added property.

## Fixed-object construction categories

For `X in C`, the ambient category in the call fixes the role of `X`:

```python
C.MonoOver(X)   = C.SliceOver(X).Monomorphisms()
C.MonoUnder(X)  = C.CosliceUnder(X).Monomorphisms()
C.EpiOver(X)    = C.SliceOver(X).Epimorphisms()
C.EpiUnder(X)   = C.CosliceUnder(X).Epimorphisms()
```

`Cat().ObjectType` defines these methods once, and every category inherits them.
The slice or coslice retains a functor to `Mor(C)` that returns its defining arrow.
`Monomorphisms()` and `Epimorphisms()` pull back the corresponding property subcategory of `Mor(C)` along that functor.

Thus `C.MonoOver(X)` is the full subcategory of `C.SliceOver(X)` on monomorphisms.
Its objects are pairs `(A, i)` with `i: A -> X` monic.
A morphism `(A, i) -> (B, j)` is a morphism `f: A -> B` with `j compose f = i`.

`C.MonoUnder(X)` is the full subcategory of `C.CosliceUnder(X)` on monomorphisms.
`C.EpiOver(X)` is the full subcategory of `C.SliceOver(X)` on epimorphisms.
`C.EpiUnder(X)` is the full subcategory of `C.CosliceUnder(X)` on epimorphisms.
Every object retains its defining morphism.

## Indexed categories, Yoneda, and representability

For a pseudofunctor `P: C.op() -> Cat()`, `Grothendieck(P)` is its total category. Its objects are pairs `(c, x)` with `x in P(c)`. Its projection to `C` is a fibration and its fiber over `c` is equivalent to `P(c)`. The construction acts on morphisms of indexed categories. See [Mathlib, Grothendieck construction](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Bicategory/Grothendieck.html).

Conversely, a fibration `p: E -> C` supplies fibers and cartesian reindexing. Base change along `F: D -> C` is `F.base_change(p)`. This is the general transfer operation for categories of objects equipped with selected data. An inverse-image property category is the subterminal-fiber case.

The Yoneda and co-Yoneda embeddings are retained functors:

\[
y:C\longrightarrow\operatorname{Fun}(C^{op},\mathbf{Set}),
\qquad
y^\vee:C^{op}\longrightarrow\operatorname{Fun}(C,\mathbf{Set}).
\]

The Yoneda embedding is fully faithful. Its object action supplies the representable hom functors. See [Mathlib, Yoneda](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Yoneda.html).

For `F: C.op() -> Sets()`, `Representations(F)` has objects `(X, eta)` with `X in C` and a natural isomorphism `eta: y(X) -> F`. A morphism `(X, eta) -> (Y, theta)` is a morphism `u: X -> Y` such that `theta compose y(u) = eta`. Yoneda makes such a morphism invertible. The functor is representable exactly when this category is inhabited. Selecting an object supplies the representing object and isomorphism. This property-and-data distinction follows [Mathlib, represented functors](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/RepresentedBy.html).

For a test functor `j: A -> C`, `j.restricted_yoneda()` is

\[
N_j:C\longrightarrow\operatorname{Fun}(A^{op},\mathbf{Set}),
\qquad
N_j(X)(a)=\operatorname{Mor}(C)(j(a),X).
\]

A separating test category places this functor in `.Faithful()`. A dense test category places it in `.FullyFaithful()`. The canonical evaluation morphisms and presentations belong to this functorial construction, as specified in [Separating families and categorical generators](separating-families-and-categorical-generators.md).

Monads, comonads, Eilenberg--Moore categories, mates, and reflective or coreflective subcategories extend this calculus after PR-8. M1 retains enough adjunction data to add them without a new transport mechanism.

## Examples

### Finite sets

Finite sets form a full property subcategory of sets.
Finiteness is closed under isomorphism.

```python
class FiniteSetsCategory(Category):
    def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
        return (Fun(self, Sets()).Monomorphisms().Isofibrations().Full()(),)
```

The functor is constructed directly in `Fun(self, Sets()).FullyFaithful()`.

### Monoid objects

For a selected monoidal category `V`, `Monoids(V)` is notation-neutral.
It is a subcategory of `Magmas(V)` because its morphisms preserve all monoid structure:

```python
class MonoidsCategory(Category):
    def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
        return (Fun(self, Magmas(V)).Monomorphisms().Isofibrations()(),)
```

The additive and multiplicative refinements retain their selected element interfaces.

### Pointed sets

A pointed set is an object of the coslice category under the singleton set:

\[
\mathbf{PointedSet}=1\!\downarrow\!\mathbf{Set}.
\]

The structure functor is the composite of the pullback projection to `Fun([1], Sets())` with `ev_1`, that is `(X, x) |-> X`. The pullback projection itself returns the morphism `1 -> X` that selects `x`.

### Product categories and `Fun([1], C)`

For categories `C` and `D`, `product_projection(0)` and `product_projection(1)` are the two functors from `C * D` to its factors.

The construction `Fun([1], C)` creates `ev_0` and `ev_1`. These functors exist without being returned from `structure_functors()`.

## Compiler contract

The compiler uses `structure_functors()` as its sole source of dynamic target classes.
It must:

1. require every entry to lie in `Fun`;

2. require each entry's domain to be the declaring category;

3. derive immediate target categories from functor codomains;

4. create the private Sage implementation category for each class kind, and use its `parent_class` as the compiled class;

5. preserve each functor's exact object and morphism maps;

6. map points and generalized elements by ordinary functor composition at their category level;

7. require each object and morphism action to return an owned value in its exact target category;

8. initialize each class in Sage's MRO once; each public functor action remains independent;

9. retain one object of `Fun(C, D)` for each named functor construction;

10. preserve each written public class as the private Sage category's method provider;

11. make each structured value carry the state required by every reachable class, with each local constructor contributing its state once;

12. derive subobject-of-product component functors by composition;

13. install the compiled classes of a point category `{X}` on its distinguished object: `{X}.ObjectType` on `X`, and `{X}.ElementType` on the points of `X`; for a category `X = C`, these points are `C.ObjectType`;

14. normalize categorical level identities before private implementation-category lookup;

15. use Sage's class-graph calculation and dynamic-class cache instead of repository graph linearization or controlled-base code;

16. rebind local methods that use zero-argument `super()` after Sage copies the method provider;

17. keep the semantic collision check, private runtime state sharing, and once-only initialization pass.

Natural transformations are trusted constructions, never compiler proofs.
There is no route normalization, route scoring, or preservation registry.

Every inherited method enters the descendant through the compiled class MRO. The declaring method runs on the original descendant instance with the supplied arguments.
It reads the declaring category's state directly on that instance.
Each structure functor already contains complete executable object and morphism actions.
The compiler makes the applicable target state available on the descendant without another writer declaration.
The method's value is returned exactly as declared.

The public surface is dynamic inheritance in Sage's sense.
The kernel obtains `C.ObjectType`, `C.ElementType`, and `C.MorphismType` from the
`parent_class` values of their private Sage implementation categories.
A leaf writes no Python inheritance.
A leaf that wants a source-category result overrides the inherited method or adds its own.

`CachedRepresentation`, `UniqueRepresentation`, and `cached_method` own runtime caches
whose keys have ordinary exact equality. `MonoDict` and `TripleDict` remain only for keys
that contain owned values with proposition-valued equality. A direct kernel call to
`dynamic_class` keeps its cache enabled.

Sage `Hom`, `Homset`, `Map`, `Morphism`, and `IdentityMorphism` can implement concrete
leaf morphisms whose endpoints are Sage parents. Generic `Mor` and `Fun` remain owned
categorical constructions. They follow the corresponding parent, domain, codomain,
composition, and functor-action protocols without forcing abstract categories to become
Sage parents. Sage `ForgetfulFunctor` does not implement a selected structure functor.

The MROs have these forms:

```text
C.ObjectType, immediate structure-functor target ObjectType classes,
Cat().ElementType, object kernel class

C.MorphismType = Mor(C).ObjectType,
immediate structure-functor target MorphismType classes, morphism kernel class

C.ElementType, immediate structure-functor target ElementType classes,
element kernel class
```

The compiler does not infer a functor from a category pair.
It does not infer fullness, faithfulness, or equivalence from a class name.
It does not add computational routes to any functor predicate.

## Mathlib correspondence

The categorical definitions follow Mathlib where the same construction exists.
Python names remain owned by the relevant category object.

The reference definitions are Mathlib's [functor API](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Functor/Basic.html), [full-subcategory API](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/ObjectProperty/FullSubcategory.html), [full and faithful functor API](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Functor/FullyFaithful.html), and [arrow-category API](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Comma/Arrow.html).

Mathlib's arrow category has morphisms as objects and commuting squares as morphisms; here it is `Fun([1], C)`. Mathlib's `C ⥤ D` has functors and natural transformations; here it is `Mor(Cat())(C, D)`. Repository endpoint application `Mor(C)(A, B)` selects the full subcategory of `Mor(C)` on morphisms `A -> B`.

| Mathlib | Repository |
| --- | --- |
| `CategoryTheory.Functor C D` | `Cat().MorphismType` with domain `C` and codomain `D` |
| `C ⥤ D` | `Mor(Cat())(C, D)` or `Fun(C, D)` |
| `Functor.id C` | `End_Cat(C).one()` |
| `Functor.comp` and whiskering functors | `Fun.composition(A, B, C)` and its morphism action |
| `Functor.fromPUnit X` | the point functor of `X`, an object of `Fun(Cat().Point(X), D)` |
| `ObjectProperty.FullSubcategory P` | the property subcategory `C.P()` |
| `ObjectProperty.ι P` | `Fun(C.P(), C).Monomorphisms().Isofibrations().Full()()` |
| monomorphism induced by `P -> Q` | `Fun(C.P(), C.Q()).Monomorphisms().Isofibrations().Full()()` |
| `CategoryTheory.Core` | `Core.on_object(C)`, written `C.Core()` |
| `Core.inclusion` | `epsilon_C: U(C.Core()) -> C` |
| `ConcreteCategory.forget`, `HasForget₂.forget₂` | an extra structure containing one chosen functor and its required compatibility |
| `Prod.fst`, `Prod.snd` | `product_projection(0)` and `product_projection(1)` |
| `Arrow.leftFunc`, `Arrow.rightFunc` | `ev_0` and `ev_1` of `Fun([1], C)` |
| `Over.forget` | the projection retained by the over-category construction |
| `StructuredArrow.proj` | the projection retained by the structured-arrow construction |
| `Comma F G` | `Comma(F, G)` with its projections and defining natural transformation |
| `Functor.Fiber p b` | `p.Fiber(b)` |
| `EssentialImage F` | `D.EssentialImage(F)` and its retained factorization |
| `Adjunction F G` | an object of `Adjunctions(F, G)` |
| `C ≌ D` | an object of `Equivalences(C, D)` |
| `Cone D`, `IsLimit` | `Cones(D)`, `LimitCones(D)` |
| `PreservesLimitsOfShape`, `CreatesLimitsOfShape` | `.PreservesLimits(I)`, `.CreatesLimits(I)` |
| `yoneda`, `RepresentableBy` | the Yoneda functor and an object of `Representations(F)` |
| `F.Full` | `F.is_full()` and `Mor(Cat()).Full()` |
| `F.Faithful` | `F.is_faithful()` and `Mor(Cat()).Faithful()` |
| `F.FullyFaithful` | `F.is_fully_faithful()` and `Mor(Cat()).FullyFaithful()` |
| `F.EssSurj` | `F.is_essentially_surjective()` and its property subcategory |
| `F.IsEquivalence` | `F.is_equivalence()` and `Mor(Cat()).Equivalences()` |

Mathlib uses propositions and typeclasses to carry established facts.
This repository uses owned predicates, `ask()`, assumptions, direct property construction, and same-object refinement.
The mathematical definitions and the declared containments remain the same.

Mathlib's `ConcreteCategory` contains a fixed faithful functor to `Type` as extra structure.
Its `HasForget₂ C D` class also contains a chosen functor `C -> D`; it does not derive one from the endpoints.
See [ConcreteCategory.Forget](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/ConcreteCategory/Forget.html).

Mathlib's `Functor.fromPUnit X : Discrete PUnit ⥤ C` sends the punctual category to a chosen object, and `Functor.equiv` states the equivalence `(Discrete PUnit ⥤ C) ≌ C`. See [PUnit](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/PUnit.html).
Here `Cat().Point(X)` names its sole object `X` and owns the declarations specific to `X`, so the corresponding functor is a subcategory monomorphism rather than a constant functor from an anonymous point.

Mathlib defines `Prod.fst` and `Prod.snd` separately.
See [Products.Basic](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Products/Basic.html).
This repository follows that construction-owned pattern for every construction.

The selection of functors for Python method inheritance has no Mathlib counterpart.
It is kernel infrastructure over already established mathematical functors.

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

- A declared containment between property subcategories is its monomorphism.

- The monomorphism of a full subcategory is fully faithful by construction.

- `Op: Cat() -> Cat()` acts on categories and functors, dualizes natural transformations, and retains `Op compose Op ≅ Id`.

- `F.inverse_image(P)` is the retained pullback `D ×_C P` for `F: D -> C` and `P -> C`.

- Property categories inherited along a named functor use this inverse-image construction.

- Composition and evaluation are functors. Their morphism actions supply whiskering and horizontal composition.

- Subcategory intersections, functor restrictions, induced pullback functors, fibers, and change of base use the generic pullback calculus.

- `Comma(F, G)` retains its projections and defining natural transformation. Slices and coslices are its fixed-object forms.

- `D.StrictImage(F)`, `D.FullImage(F)`, and `D.EssentialImage(F)` have the stated distinct morphisms and closure properties.

- `Adjunctions(F, G)` and `Equivalences(C, D)` retain selected data. Their existence is inhabitation of these categories.

- Every functor is constructed through `Fun(Source, Target)` or an established property subcategory.

- A specialized constructor receives enough mathematical data to select one functor.

- Endpoint categories and object fields never select a functor.

- The repository has no generic constructor selected by the phrase “forget structure.”

- Every functor is named by its construction or given as an explicit composite.

- Each category presentation retains all projections and evaluations required by its definition.

- `Cat().Products()` and `Cat().Coproducts()` accept sequence-indexed category diagrams.

- Selected product and coproduct presentations own their legs and universal maps.

- `Cones(D)` and `LimitCones(D)` separate the universal presentation from its apex.

- The total category of limiting cones retains its diagram projection and apex functor. Apex interfaces are full images of the applicable chosen limit functors.

- `.PreservesLimits(I)` and `.CreatesLimits(I)` are functor-property categories. Their colimit forms derive through `Op`.

- Every object of `Cat().MonoOver(P)` for a product category `P` retains its presenting monomorphism, then derives its component functors by composition.

- Slice and coslice categories are pullbacks of `ev_1` and `ev_0` along the chosen object and retain their pullback projections.

- Fibration and opfibration structure retains its cartesian or cocartesian lifts.

- `p.Fiber(b)` exists for every functor. `F.base_change(p)` retains the pullback projection and comparison square.

- `Grothendieck(P)`, Yoneda, co-Yoneda, restricted Yoneda, and `Representations(F)` are generic constructions.

- Kan extensions retain their units, counits, and universally induced natural transformations.

- `Cat().Point(X)`, written `{X}`, is the one-object category on a distinguished object `X`, retained once per `X`.

- A point functor is the monomorphism `{X} -> D`, constructed through `Fun({X}, D)` and returned from `{X}.structure_functors()` when it supplies inherited implementation.

- A point structure functor `{C} -> D` supplies target object state to `C` and target element state to `C.ObjectType`, the points of `C`.

- Every structure functor is an ordinary object of `Fun`.

- `structure_functors()` determines the immediate compiled class bases and inherited method surface.
  Each named functor owns its public images.

- Sage dynamic classes and Sage's controlled linearization derive the complete MRO from those immediate bases.
