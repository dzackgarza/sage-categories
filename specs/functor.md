# Functors, `Cat`, and structural inheritance

This specification supplies the categorical layers of the tower in [system.md](system.md).

## Contents

- [`Cat` and its implementation](#cat-and-its-implementation)

- [Functors as morphisms of `Cat`](#functors-as-morphisms-of-cat)

- [The `Mor(n, C)` tower](#the-morn-c-tower)

- [Canonical objects of `Cat`](#canonical-objects-of-cat)

- [The core functor](#the-core-functor)

- [Functor property subcategories](#functor-property-subcategories)

- [Property resolution](#property-resolution)

- [Monomorphisms of `Cat()` and placement](#monomorphisms-of-cat-and-placement)

- [Structure functors and inherited classes](#structure-functors-and-inherited-classes)

- [Static semantic projection](#static-semantic-projection)

- [Category classes and category-valued families](#category-classes-and-category-valued-families)

- [Point categories and point functors](#point-categories-and-point-functors)

- [Functor construction and presentation data](#functor-construction-and-presentation-data)

- [Adjunctions and equivalences](#adjunctions-and-equivalences)

- [Products, coproducts, and component functors](#products-coproducts-and-component-functors)

- [Diagram shapes and universal constructions](#diagram-shapes-and-universal-constructions)

- [Comma categories, slices, coslices, and fibers](#comma-categories-slices-coslices-and-fibers)

- [Fixed-object construction categories](#fixed-object-construction-categories)

- [Indexed categories, Yoneda, and representability](#indexed-categories-yoneda-and-representability)

- [Examples](#examples)

- [Compiled public consequence](#compiled-public-consequence)

- [Mathlib correspondence](#mathlib-correspondence)

- [Acceptance conditions](#acceptance-conditions)

## `Cat` and its implementation

`Cat`, the category of categories, is defined by this repository and is read as mathematics.
The layer responsibilities are fixed in [system.md](system.md#system-shape).
For this project, assume `Cat` is bicomplete and biclosed; universe-size distinctions are outside its modeled scope (D36).
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
The mathematical constructions live in `Cat`; their runtime interpretation follows [system.md](system.md#system-shape):

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

A functor that computes its images is declared by both actions, `Fun(C, D)(on_object, on_morphism)`.
A subcategory inclusion computes nothing: it is declared as `Fun(S, T).Monomorphisms().Isofibrations()()`, the zero-argument call on the property category of `Fun(S, T)`, and no action is written for it (D10, D11, D146; [Declaring one](#declaring-one)).
A point functor is `D.Point()`, an arrow `* -> D` that the leaf class of the point adds to its structure functors (D154; [Point categories and point functors](#point-categories-and-point-functors)).
A structure functor such as `Posets() -> Sets()` is defined by the leaf with its two actions and constructed into the strongest property subcategory of `Fun(C, D)` that states what is known about it (D08, D162; [Diagram shapes and universal constructions](#diagram-shapes-and-universal-constructions)).
A functor retained by a construction is selected by the named method of that construction, and a composite is `G * F` (D157; [Functor-category calculus](#functor-category-calculus)). A retained functor carries the properties its construction declares for it: `C.SliceOver(X).projection()` and `C.CosliceUnder(X).projection()` are the pullback projections to `Fun([1], C)`, and their composites with `Fun([1], C).ev(0)` and `ev(1)` are the discrete fibration `C.SliceOver(X) -> C` and the discrete opfibration `C.CosliceUnder(X) -> C` ([Comma categories, slices, coslices, and fibers](#comma-categories-slices-coslices-and-fibers)); `Fun(I, C).ev(i)` is an isofibration (transport of a diagram along an isomorphism at `i`). `Fun.Opfibrations()` is retained inside `Fun.Isofibrations()` as `Fun.Fibrations()` is (a cocartesian lift of an isomorphism is an isomorphism), and isofibrations compose ([nLab, "isofibration"](https://ncatlab.org/nlab/show/isofibration), `POL-MATH-040`), so the composite `G * F` of two functors in `Isofibrations()` is constructed into `Isofibrations()` by `Cat`; a leaf that selects such a composite as a structure functor inherits along it (D167, D169).
A class that implements a category otherwise named selects that category's identity functor (D156; [Implementing a named category](#implementing-a-named-category)).
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

A point `x: * -> X` is represented by its defining functor. A functor `G: X -> Y` maps it by composition to `G * x: * -> Y`. A generalized element `T -> X` maps by the same composition to `T -> Y`. This point action belongs to `G`. Selection of a structure functor can add the applicable target element implementation to the compiled source class.

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
Both actions are ordinary maps on values of their stated source category whose own local state is initialized.
Returning `F` from `structure_functors()` lets the kernel run the object action during source construction to initialize the target implementation on the source value (D13).

For example, an algebra presentation can retain a morphism `R -> Z(A)`.
Its functor to rings can recover `Z(A)` as the codomain and then use the ambient-object operation supplied by `Subobjects`:

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
This is D08, D120, and D123, with stable policy references `POL-FUN-035`, `POL-LEAF-058`, and `POL-LEAF-062`.

A natural transformation `eta: F => G` is constructed as `Mor(Fun(C, D))(F, G)(assignment)`. The assignment is a rule `X |-> eta_X` on the objects of `C`, returning a morphism `F(X) -> G(X)` of `D`. It is never a table.
Naturality is trusted.

## The `Mor(n, C)` tower

`Cat` owns formal composition, recognition of composites, and any mathematical word-reduction extension (D173).

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
It is the functor category `Fun([1], C)` from the walking arrow `[1]`. Its evaluation functors `Fun([1], C).ev(0)` and `Fun([1], C).ev(1)`, each `Fun([1], C) -> C`, supply the domain and codomain projections.
In general, evaluation at `i in I` is the retained functor `Fun(I, C).ev(i): Fun(I, C) -> C` (D157).

The related property categories use the same mechanism:

```python
Mor(C).Monomorphisms()
Mor(C).Epimorphisms()
Mor(C).Isomorphisms()
Mor(C).Automorphisms()
```

Each is a property subcategory of an owned morphism category.
Each property category owns its predicate meaning and declared subcategory relations.
SymPy supplies its public predicate class, applied propositions, assumptions, and exact proposition dispatch.
Fixed endpoints use the same dispatch for every property subcategory `P` of `Mor(K)`: `P(A, B)` is `Mor(K)(A, B).P()`, one cached object.

## Canonical objects of `Cat`

Canonical shapes include simplicial horns and their boundaries when a construction needs them (D71).

`Cat()` owns these objects, each constructed once and retained by identity:

- `Groupoids()`: the category of groupoids, declared as a point of `Cat`; the current foundation requires no further implementation of groupoid theory;

- `Cat().Initial()`: the empty category;

- `Cat().Terminal()`, written `1` and equal to `[0]`;

- `Cat().Simplex(n)`, written `[n]`: the poset `0 < 1 < ... < n` as a category, for `n >= 0`; `[1]` is the walking arrow, `[2]` the walking commutative triangle;

- `Cat().WalkingSpan()`: the free category on `0 <- 1 -> 2`;

- `Cat().WalkingCospan()`: the free category on `0 -> 1 <- 2`;

- `Cat().WalkingIsomorphism()`: two objects and two mutually inverse morphisms;

- `Cat().WalkingParallelPair()`: two objects and two parallel morphisms.

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

The axiom declarations give `cat_kernel` their names and their ambient category `Mor(Cat())`.
`cat_kernel` generates these applications on `Cat().MorphismType`:

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
set-theoretic logic and has no category-theoretic formulation. A category states a
containment by constructing and retaining that monomorphism
([property-refinement.md](property-refinement.md#property-containment)).

## Property resolution

Functor properties use the public SymPy proposition, `ask()`, and property-refinement framework.
They have no separate evidence or decision system.

A functor is constructed into the strongest property category its writer knows (D21):

```python
F = Fun(C, D).Full()(on_object, on_morphism)
```

This category call asserts the property.
The code writer uses external mathematics to select `Fun(C, D).Full()`.
The kernel does not prove, certify, or check fullness.

An interactive assumption uses the same predicate and refines the same owned functor:

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
Other category-owned predicate meanings, such as injectivity on an exact set-map domain, can register exact SymPy handlers.

## Monomorphisms of `Cat()` and placement

### The two conditions

A subcategory of `T` is a subobject of `T` in `Cat()`: an isomorphism class of monomorphisms into `T` ([nLab, subobject](https://ncatlab.org/nlab/show/subobject), inspected 2026-08-28; "an isomorphism class of monomorphisms"). Two conditions apply, and `cat_kernel` needs both to read the declaration (D175).

**Monic.** [nLab, subcategory](https://ncatlab.org/nlab/show/subcategory) (inspected 2026-08-28): "subcategories of a category `C` can be identified with isomorphism classes of monic functors into `C`. A functor is easily verified to be monic iff it is faithful and injective on objects."
[nLab, full embedding](https://ncatlab.org/nlab/show/full+embedding) (inspected 2026-08-28) names the same class: "Embeddings in this sense are straightforwardly the same thing as monomorphisms in the 1-category `Cat`", and a full embedding is a monomorphism in `Cat` that is also full, hence fully faithful.
So the owned property is `Fun.Monomorphisms()`, and the monomorphism of a full subcategory is an object of `Fun.Monomorphisms().Full()`. `Fun` needs no further property for this.

**Isofibration.** Monicity alone is not enough, because a skeleton satisfies it.
`Cardinal()` selects one representative set per cardinal; its functor to `Sets()` is fully faithful and injective on objects, hence monic, hence an embedding.
A cardinal is still not a set.
The condition that separates them is on the arrows: **that monomorphism is an isofibration**, so every isomorphism of `T` at an object in the image lifts to `S`. [Kerodon, Example 4.4.1.12](https://kerodon.net/tag/01EX) (inspected 2026-08-28) states that this holds exactly when an isomorphism of `C` with one endpoint in the subcategory has its other endpoint and itself in the subcategory, the object condition called replete. [nLab, replete subcategory](https://ncatlab.org/nlab/show/replete%2Bsubcategory) (inspected 2026-08-28) states why this is the right condition: such a subcategory "is a subcategory for which the property of (strictly) belonging to it respects the principle of equivalence of categories." The documents state the arrow condition (D170).

`Sets().Finite() -> Sets()` is an isofibration: a set isomorphic to a finite set is finite.
The inclusion of every property subcategory whose defining predicate is an isomorphism invariant is an isofibration for the same reason.
The inclusion of a skeleton is the opposite extreme and is an isofibration only when the skeleton is everything.

The two properties are declared differently because their mathematics differs.
`Fun.Monomorphisms()` is a full subcategory of `Fun.Faithful()`, and states that containment by the monomorphism it retains: monic is faithful together with injectivity on objects.
`Fun.Isofibrations()` is a full subcategory of nothing but `Fun`, because an isofibration need not be faithful: `Fun(I, C).ev(i)` is one, and two natural transformations of `Fun(I, C)` that agree at `i` need not be equal.
The faithful isofibrations that carry inheritance (D167, `POL-FUN-036`) are therefore not the whole of `Fun.Isofibrations()`, and their faithfulness is not separately declared: the leaf writer asserts it by constructing a structure functor into `Fun(C, D).Isofibrations()` or a subcategory of it, and `cat_kernel` reads that declaration and trusts it, exactly as it trusts the isofibration condition itself (D169, D175).
Declaring `Fun.Isofibrations()` inside `Fun.Faithful()` would state something false, and a containment is a declared monomorphism and never induced from an implication between predicates in any case (D83).

### Placement traces monic isofibrations

`x in C` asks `C`'s membership proposition (`POL-CAT-043`, `POL-CAT-044`). Placement is a positive shortcut inside that one question: construction or same-object refinement into the property category already established the defining predicate, so `ask()` answers from placement without recomputing (`POL-CAT-068`). Placement propagates from `S` to `T` exactly along a functor that is a monomorphism of `Cat()` and an isofibration.
Monicity gives one value rather than a copy; the isofibration condition makes the resulting membership statement invariant, so an object of `Sets().Finite()` is an object of `Sets()` while a cardinal is not a set.

The choice is data.
`Cardinal() -> Sets()` and `Sets().Finite() -> Sets()` are both monic, and nothing derives which one placement follows: nLab, *subobject*, states that for representatives of a subobject "there is no intrinsic way of defining such representatives".
A leaf therefore declares which monomorphism placement follows by constructing it in the property category below, and `cat_kernel` reads that declaration and trusts it (`POL-CAT-069`, D175). It infers the relation from nothing else — not Python inheritance, not shared storage, not a cache of previously constructed functors. A point functor is declared the same way and is no exception: `C.Point()` writes the declaration in the call that constructs the arrow, so what `cat_kernel` reads there is a declaration like any other. The arrow's own property category is `Fun(*, C).Monomorphisms()` and not an isofibration subcategory — an isomorphism `X -> Y` of `C` has nothing to lift to in `*`, which has one morphism — so the arrow declares placement and the inclusion `<X> -> C` declares the isofibration (D161). `Monomorphisms()` is the strongest of `Fun`'s named property subcategories that holds for every `C` and `X`, which is what D162 asks for. The arrow is also full exactly when `End_C(X)` is trivial, and that is not declared: `C.Point()` takes no argument to decide it, `POL-CAT-091` forbids a fullness handler, `ask(F.is_full())` is `Unknown` in the general case, and nothing reads it — placement and inheritance both run along `<X> -> C`.

### Declaring one

`Fun.Monomorphisms()` and `Fun.Isofibrations()` are owned properties of `Fun`, so the declaration is an ordinary construction in the property category their intersection names:

```python
iota = Fun(S, T).Monomorphisms().Isofibrations()()
```

This zero-argument call on the property category is the declaration of every subcategory inclusion; the inclusion computes nothing, and no action is written for it (D146).
The leaf writer states that `S` is a subcategory of `T` by constructing there.
The kernel does not compute that relation from Python inheritance or shared storage, and it does not recognize the functor by consulting a table of ones it built earlier.

The property category the call names is the whole declaration, and the functor is placed in it and in nothing wider or narrower (D146, D162).
So the call is available on a monomorphism subcategory of `Fun(S, T)` and is refused on every other property category of it: a functor that computes nothing is a subcategory inclusion, and every other functor is written with its two actions and constructed into the strongest property subcategory that states what is known about it (D08, D21).
`Fun(S, T).Monomorphisms()()` declares a monomorphism and declares nothing further, so `ask()` answers `Unknown` for the isofibration condition and placement does not follow it; `Fun(S, T).Monomorphisms().Isofibrations()()` is the declaration placement follows.
One identity-on-values functor exists per endpoint pair (`POL-FUN-027`), so two declarations on one pair narrow one retained value.

A full subcategory adds fullness, so a property subcategory `C.P()` declares:

```python
iota = Fun(C.P(), C).Monomorphisms().Isofibrations().Full()()
```

The defining object predicate selects the objects, and it is an isomorphism invariant, so the functor is an isofibration.
The morphism categories `Mor(C)(A, B)`, identities, and composition are inherited from `C`.

A property subcategory can be contained in another, `C.P()` in `C.Q()`. That containment
is the same declaration between them (D83):

```python
iota = Fun(C.P(), C.Q()).Monomorphisms().Isofibrations().Full()()
```

The containment is the statement. Nothing induces it from a relation between the
predicates, and `P(X) ⟹ Q(X)` is set-theoretic logic with no category-theoretic
formulation. `C` states it by constructing and retaining this monomorphism, and the
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

`structure_functors()` selects immediate named functors in the owned category graph.
Selection provides access to the declared structure. The inheritance condition below determines which target classes enter the source implementation.
Sage supplies the private class-building mechanism; the owned graph has its own categories and functors.

Every entry is an ordinary owned object of `Fun`. Its mathematical existence and
properties come first. A structure functor need not be a subcategory monomorphism.
For example, the structure functor `Posets() -> Sets()` sends a poset to its underlying set, `(X, R) |-> X`, never to its relation (D163).
A poset is not thereby an object of `Sets()`, and `Posets()` is not thereby a subcategory of `Sets()`.

A selected functor declared in `Fun(C, D).Isofibrations()` or a subcategory of it carries target inheritance (D167, D177).
In this selection context, the declaration also asserts faithfulness; review checks that assertion.
`Fun.Isofibrations()` itself has no containment in `Fun.Faithful()`: an arbitrary isofibration need not be faithful.
A selected functor without the inheritance declaration provides access to its structure through its public actions.
For several inheritance-carrying targets, declaration order fixes precedence; controlled C3 chooses the first shared occurrence and assumes coherence.
`Posets()` admits two functors to `Sets()` that do not agree, `(X, R) |-> X` and `(X, R) |-> R`.
For a lattice `(L, b)`, both projections are structure functors: `(L, b) |-> L` into modules is a faithful isofibration (a form pulls back along an isomorphism of modules), so a lattice is a module and inherits along it; `(L, b) |-> b` into `Mor(Mod)` is not an isofibration (an isomorphism of arrows `M -> Z` with `L * L -> Z` need not be of the form `f * f`), so it gives access to `b`, through which `L.b()` and `L.q()` are reached, and inherits nothing from bilinear forms (D166). A bimodule's two projections are both isofibrations, and the declared order decides between them (D165).

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

A category selects an immediate structure functor for its named structure; the condition above governs inherited operations.
The complete finite-set declaration appears once in [finite-set-minimal-template.py](finite-set-minimal-template.py).

The categories `Fun(self, D)` can contain many other functors.
Their existence does not affect the compiled public surface.
Use as a structure functor changes compiler behavior only.
It does not change a functor's mathematical definition.

### Implementing a named category

A category otherwise named, such as `D.P1().P2().P3()`, exists before any class is written for it.
A class declares itself the implementation of that category by selecting its identity functor as a structure functor (D156):

```python
class Implementation(Category):
    def structure_functors(self) -> tuple[Functor, ...]:
        x = D.P1().P2().P3()
        return (End_Cat(x).one(), ...)


Cat().implement(Implementation)
```

`End_Cat(x).one()` is the identity of the endofunctor category at `x` ([Functor-category calculus](#functor-category-calculus)).
The interface is uniform: `Fun` provides identity functors, and this selection is the whole declaration.
There is no binding field, and no name of `x` is written as a string.

`Cat().implement` constructs the class to read that declaration, and the construction stops there: the identity functor names `x`, so the class has no category of its own to build, and `Cat` strengthens `x` in place to the implementing class, keeping its ordinal, so every reference already written against `x` uses the implementation from that moment.
Reading it by construction rather than off the class is what lets the functors after the identity be written against `self`, as `Fun(self, D)(on_object, on_morphism)`, the shape every leaf's structure functors have ([poset template](poset-minimal-template.py)); a read taken before the value exists would build those functors over nothing.
That is also why the identity functor comes first: it is what says which category, and it is read before the rest of the declaration is used.
Between the class statement and `Cat().implement`, `x` is still an open declaration, and a functor selected into it is refused as one.

The class writes no constructor; `x` keeps exactly the constructors of its ambient category (D150).
A class implementing an axiom subcategory `C.P()` is the one-property instance, `x = C.P()` ([poset template](poset-minimal-template.py), [finite-poset template](finite-poset-minimal-template.py)).
A class implementing a generic construction category is the same declaration, `x = Sets().CosliceUnder(Sets().Terminal())` ([pointed-sets template](pointed-sets-minimal-template.py)).

### Selecting a retained functor

A functor retained by a construction is selected by the named method of that construction (D157):

```python
C.CosliceUnder(X).projection()   # the retained projection of a coslice
Fun(I, C).ev(i)                  # evaluation at i in I
P.product_projection(i)          # the i-th projection of a product
G * F                            # the composite of F: A -> B and G: B -> C
```

`G * F` is the morphism composition of `Cat`, and it is the one spelling of a composite functor.

Each category lists only immediate structure functors.
The kernel supplies inheritance-carrying target classes as immediate dynamic bases. Sage dynamic-class
construction and Sage's controlled linearization handle transitive inheritance and shared
ancestors.

### Structural diamonds and coherence

Two distinct paths of owned structure functors can reach one target implementation owner.
This is an ordinary diamond in the new graph. The private Sage runtime mirror gives those
targets to controlled C3, which places the shared implementation class once in the MRO.
There is one private implementation occurrence, not one occurrence per path; no public
functor images from the competing paths are constructed or compared in order to resolve
the diamond. Declaration order remains the existing preference rule of D56 wherever a
path preference is required.

Coherence of a diamond is mathematical information about the relevant composite functors.
Its absence is not a compiler failure. Until explicit owned coherence is supplied, the
kernel reports the diamond only through opt-in `DEBUG` logging and continues with the
single controlled-C3 implementation occurrence. A future extension can let theory code
supply an actual 2-morphism, using the ordinary natural-transformation machinery of `Fun`,
to mark the composites as coherent and silence that diagnostic. This extension must not
introduce a proof record, certificate, route registry, or second functor declaration; its
exact spelling is deferred.

### `C.ObjectType`, `C.ElementType`, and `C.MorphismType`

A category specifies `C.ObjectType`, `C.ElementType`, and `C.MorphismType` directly.
The kernel constructs these classes from the immediate targets satisfying the [inheritance condition](#structure-functors-and-inherited-classes).
For each selected `F: C -> D`, the applicable `D` implementation class contributes inherited execution on the source value.
This consequence adds no functor-writer declaration.

The kernel preserves the body specified for each class. Each category has exactly one
`C.ObjectType`, one `C.ElementType`, and one `C.MorphismType`.

The ordinary object action of `F` uses one of the finite public constructors of `D` and
returns the resulting `D.ObjectType`. Its morphism action does the same in the exact target
hom category. Ordinary functors that are not selected do not participate in class construction.

Public `F(x)` runs the named functor's ordinary action on the completed source value and returns the separate image owned by `F`.
Different functors with the same endpoints can return different images.

An inherited method runs directly on the structured source instance through ordinary Python inheritance.
Thus `x.f()` and `F(x).f()` have the same mathematical value.
The equality is semantic; method dispatch does not replace `x` with `F(x)`.

Identity and composite structure functors use their ordinary functor actions.

For a category `X`, `Fun(*, X)` models its points and `Fun(T, X)` models its generalized elements with domain `T`. A functor `G: X -> Y` maps both by composition. The category `Fun([1], X)` models arrows of `X` separately.

An ambient functor `F: C -> D` maps objects and morphisms of `C`. Selecting `F` for compiled inheritance adds the applicable target implementation classes to the source classes. This compiler effect adds nothing to the public functor definition.

The private class compiler, initialization, and cache rules live only in [resolution.md](resolution.md).

## Static semantic projection

The dynamic compiler has one static semantic model.  This section fixes the model that
the compiler projector emits; it is not a second declaration language and no runtime
class consumes it (`POL-TYPE-024` through `POL-TYPE-029`).

For a category, the three associated types are its structural parameters:

```python
class Category[Obj: CategoryPoint, Elem: CategoryPoint, Mor: CategoryPoint]:
    ObjectType: type[Obj]
    ElementType: type[Elem]
    MorphismType: type[Mor]
```

`Category[Obj, Elem, Mor]` denotes exactly the category whose values have those three
category-owned types.  A declaration fixes all three parameters.  It does not replace
one with `Cat().ElementType`, a universal morphism type, or a structural duck type
(`POL-TYPE-018`, `POL-TYPE-019`, `POL-TYPE-027`).  A generated static declaration for a
concrete category family binds its exact `ObjectType`, `ElementType`, and
`MorphismType`; this includes `CategoryOfCategories`, `MorphismCategory`,
`FunctorsCategory`, finite presented categories such as `Simplex(n)`, and pullback
categories.

The semantic signature of a functor keeps both endpoint triples:

```python
class Functor[
    DomainCat: Category[DomainObj, DomainElem, DomainMor],
    CodomainCat: Category[CodomainObj, CodomainElem, CodomainMor],
]:
    def domain(self) -> DomainCat: ...
    def codomain(self) -> CodomainCat: ...
    def on_object(self, member_object: DomainObj) -> CodomainObj: ...
    def on_morphism(self, morphism: DomainMor) -> CodomainMor: ...
```

Here the type variables in each endpoint triple are determined by that endpoint
category.  Thus the displayed form is semantic notation for
`DomainCat.ObjectType`, `DomainCat.ElementType`, `DomainCat.MorphismType`, and their
codomain counterparts.  The projector emits the concrete nominal spelling that the
checker supports.  It never widens either action to `Callable[[Any], Any]`,
`Callable[..., Any]`, a broad union, or a structural capability (`POL-FUN-001`,
`POL-TYPE-017`, `POL-TYPE-028`, `POL-TYPE-029`).

The same model fixes the morphism tower and endpoint categories:

```python
Mor(C): Category[C.MorphismType, MorElement, MorTwoMorphism]
Mor(C)(A, B): FixedEndpointCategory[C, A, B]

class FixedEndpointCategory[
    C: Category[Obj, Elem, MorType],
    A: Obj,
    B: Obj,
]:
    def domain(self) -> A: ...
    def codomain(self) -> B: ...
    def __call__(self, ...) -> MorType: ...
```

The returned `MorType` is statically the morphism type of `C`; its stored domain and
codomain are exactly `A` and `B`.  `Mor(C).ObjectType = C.MorphismType` is a
level identity, not a wrapper, conversion, or additional class hierarchy.

For a full property subcategory `P = C.P()`, the associated-type triple has the same
semantic values as `C`.  A positive proposition evaluated by `ask()`, an assumption,
or construction in `P` returns the identical owned value with the compiler-generated
refined nominal type.  The generated type is the one dynamic class computed from
`C` and `P`; it exposes both the ambient and property surfaces.  This is the static
intersection for same-object refinement.  It is not a `Protocol`, `TypeIs` guard,
adapter, wrapper allocation, cast, or false runtime inheritance (`POL-TYPE-020`,
`POL-TYPE-027`; [property-refinement.md](property-refinement.md#same-object-refinement)).

The compiler projector is the sole consumer of this model.  It derives every `.pyi`
symbol from the authoritative category declarations, selected structure functors, and
the compiler's declared inheritance computation.  No source module maintains a
parallel hand-written type graph; generated stubs are output-only and do not become
semantic authority (`POL-TYPE-025`, `POL-TYPE-026`).

## Category classes and category-valued families

A category is constructed by its category class. The class declares its nested
`ObjectType`, `ElementType`, and `MorphismType`, its constructors, and its immediate
structure functors. The kernel compiles those declarations on the resulting object of
`Cat()`.

```python
class Sets(Category):
    class ObjectType: ...
    class ElementType: ...
    class MorphismType: ...

    def structure_functors(self): ...
```

A category class extends one of the curated base classes `Category`, `CategoryOverRing`, and `CategoryOfXObjectsIn`, for example `Rings = RingObjectsIn(Sets)`; `RingObjectsIn(C)` is the class, and `Rings(C)` is the category it constructs ([rings.md](rings.md)).
Writing the class populates its structure functor `Sets: * -> Cat` automatically: every category class is a point in `Cat` (D154).
A class that implements a category otherwise named selects that category's identity functor as a structure functor (D156; [Implementing a named category](#implementing-a-named-category)).

A category family is a functor into `Cat()` when its mathematics gives object and morphism
actions. For example, `Discrete: Sets() -> Cat()` maps a set to its discrete category, and
`MonoidObjects: Cat() -> Cat()` maps a category to its category of monoid objects.
Their functoriality comes from these actions.

A constant category such as `Sets()` needs only its category class. A parameterized
category such as `Modules(R)` uses its mathematical parameter in its category constructor.
A named object such as `NN` is a category class, a completely abstract new category; the
next section states how it registers itself as a point.

Generic kernel and `cat` modules accept ambient categories as arguments. They do not import
production leaves. A category construction fails when its own class declaration,
constructor, or functor action is incomplete.

## Point categories and point functors

A named mathematical object `X` is a leaf class, a completely abstract new category (D161).
Writing that class populates its structure functor `X: * -> Cat` automatically, so every leaf class is a point in `Cat`; here `*` is the terminal category `Cat().Terminal()` (D154).

`C.Point()` constructs an arrow, not an object: `F = C.Point()` is a functor `F: * -> C`, the point functor of its source.
`C.Point()` constructs one thing, the arrow `F: * -> C` selecting `X` (D154); its image generates `<X>`, the smallest full subcategory of `C` containing `X` whose inclusion is an isofibration, the isomorphism class of `X` with all morphisms between its objects, and `C.Point()` registers `F` in `Fun(*, C).Monomorphisms()` in the same call that constructs it, which is `Cat`'s and is the declaration D162 requires be named (`54674b9b` 2026-09-02T22:00:14Z: the call constructs the functor and automatically registers it). `cat_kernel` then reads that declaration, and the kernel carries placement and inheritance along the inclusion `<X> -> C`, declared in `Fun(<X>, C).Monomorphisms().Isofibrations()` (`POL-FUN-036`, D128, D167, D170). That inclusion is what "point" denotes in D161; the arrow `F` itself is faithful and monic and is full exactly when `X` has no nonidentity endomorphism.
The leaf class of `X` registers `X` as a point in `C` by adding `C.Point()` to its structure functors:

```python
class NN(Category):
    def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
        return (Sets().Countable().Point(),)
```

`Sets().Countable().Point()` and `Sets().Point()` are both admissible here, and all relevant point diagrams commute.
The point in `C` gives `X` itself the `C.ObjectType` inheritance, and gives `X.ObjectType` the `C.ElementType` inheritance, through the categorical level shift below (D128, D154, D161): every object of the category `NN` is an element of the set `NN`, and every set is a discrete category.
`NN` later lifts its point to magmas in two ways, so `+` and `*` are supported, then to monoids, and then into semirings (D161).
This structure functor is the whole declaration of a point; there are no further conveniences or shortcuts.

### The categorical level shift

Let a category `C` be an object of a category `D` whose objects are structured categories, through the structure functor `D.Point()` in the class of `C`.
That placement supplies these implementation surfaces:

| Surface of `D` | Surface it supplies |
| --- | --- |
| `D.ObjectType` | The category `C` itself |
| `D.ElementType` | `C.ObjectType`, the points `* -> C` |
| Applicable structured morphism surface | The exact functors or natural transformations declared by `D` |

This shift follows from the point relation in `Cat`.
It is the effect of selecting the point functor.
It is not a second inheritance mechanism.

Shared target classes use the ordinary Sage dynamic-class construction and occur once in the MRO.

### Ambient algebraic categories

An algebraic category takes its ambient category as an argument.
Thus `Semirings(A)` classifies semiring objects whose underlying objects, addition, multiplication, zero, one, and laws live in `A`. For example, `Semirings(Sets())` has underlying sets and set maps.
`Semirings(Cat())` has underlying categories and functors.
A category `C` is placed as an object of `Semirings(Cat())` by the structure functor `Semirings(Cat()).Point()` in its class (D128, D154).

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

Every functor has a construction name or is an explicit composite.
The source and target select only `Fun(Source, Target)`. They do not select one of its objects.
A category presentation can expose several valid maps, and an equivalent presentation can expose different immediate maps.

For example, a lattice presentation `(M, b)` has one projection to `M` and another to `b`. A module presentation by an action morphism has the projections and evaluations of its chosen action-category construction.
The kernel cannot recover a preferred map from tuple positions or field names.

Each public functor must name its construction.
The fundamental cases are:

| Construction | Functor or morphism supplied |
| --- | --- |
| subcategory or property subcategory | its specified monomorphism |
| product category | each `product_projection(i)` |
| coproduct category | each `coproduct_injection(i)` |
| functor category `Fun(I, C)` | each evaluation `Fun(I, C).ev(i): Fun(I, C) -> C`; for `Fun([1], C)`, `ev(0)` and `ev(1)` |
| slice or coslice presentation | its pullback projection `C.SliceOver(X).projection()` or `C.CosliceUnder(X).projection()`; the varying object is its composite with `Fun([1], C).ev(0)` or `Fun([1], C).ev(1)` |
| Grothendieck fibration | its projection and specified cartesian lifts |
| Grothendieck opfibration | its projection and specified cocartesian lifts |
| base change | the functor supplied by pullback, pushforward, or the stated adjunction |
| left or right Kan extension | the extended functor and its universal natural transformation |
| composite construction | the composite `G * F` of the supplied functors |

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

For `F: A -> B` and `G: B -> C`, the composite is `G * F`, the morphism composition of `Cat` (D157).
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

It retains the natural isomorphism `Op * Op ≅ Id`.
Thus duality acts on categories, functors, and natural transformations.
Dualizing an intersection retains the intersection of its dual roots, independently of construction order.
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
When `i` is full, or an isofibration, that projection has the same property.

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

Let `F: C -> D`, with subcategory monomorphisms `i: P -> C` and `j: Q -> D`. When the defining mathematics supplies a factorization of `F * i` through `j`, `F.restrict(P, Q)` is the induced functor `P -> Q`. The leaf states the theorem that its objects and morphisms land in `Q`. The general restriction construction supplies the functor and the commuting square.

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

The essential image is full, and its inclusion is an isofibration; the inclusion of the strict image need not be. The functor factors through it as an essentially surjective functor followed by a fully faithful inclusion. Membership records only the existential property. A selected preimage is separate data. This follows [Mathlib, essential image](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/EssentialImage).

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
P = Cat().Products()(C_0, ..., C_n)
Q = Cat().Coproducts()(C_0, ..., C_n)
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
The corresponding object of `Cat().Subobjects(P)` retains `j` and reads `P` as its codomain.
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
For categories `C` and `D`, `C * D = Cat().Products()(C, D)` is the product category, an object of `Cat().Products()`, and `C + D` is the coproduct category.
`(C * D)(X, Y)` constructs the element `(X, Y)` of `C * D`.
For `D = C`, the chosen binary product functor `C * C -> C` maps this element to its product object in `C` (D181).

`Fun([1], C)` retains its evaluation functors:

```python
Fun([1], C).ev(0)   # Fun([1], C) -> C, the domain of a morphism
Fun([1], C).ev(1)   # Fun([1], C) -> C, the codomain of a morphism
```

The generic pullback construction is `C.Limits(Cat().WalkingCospan())` (see [Diagram shapes and universal constructions](#diagram-shapes-and-universal-constructions)). Its legs are the retained projections.
The same rule handles repeated codomains.

## Diagram shapes and universal constructions

A shape is an object of `Cat()`. A diagram of shape `I` in `C` is an object of `Fun(I, C)`, constructed from an object rule and a morphism rule like every functor.
For `D: I -> C`, the index category is exactly `I = D.domain()`.
The construction retains `I` and `D`; every descendant category inherits that presentation.
For a discrete diagram on `S`, the retained `Discrete(S)` construction supplies the index set `S`.

`Cat` supplies these shape constructors (D173; `leaves.md` "Inherited constructions"):

- `Discrete(S)` for `S in Sets()`: the discrete category on `S`; `Discrete` is a functor `Sets() -> Cat()`;

- the canonical objects of `Cat` above;

- `Thin.on_object(P)` for a preordered set `P`: the thin category of `P`; `omega = Thin.on_object(NN)` with its natural order is the sequential shape;

- finite presented shapes: a finite set of objects, a finite set of generating morphisms, and a finite set of relations between composable words.

A discrete diagram needs only its object rule `i |-> X_i`. The rule is an assignment on `S`; it never enumerates `S`. The positional arguments `X_0, ..., X_n` are the convenience form and denote the diagram over `Discrete([n])`.

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

`C.Products()` is the union of the essential images of these chosen product functors (D168).
Its objects are isomorphic to nontrivial chosen products; its inclusion is a full monic isofibration.
`C.Coproducts()` is dual. Singleton limits remain available through their standard limit construction.
A chosen presentation retains its own legs and universal maps, independently of apex membership.

`C.Products()(X, Y)` selects a product presentation `p in LimitCones((X, Y))` and returns `p.apex()` placed in `C.Products()`. The presentation remains an object over the apex. A second limiting cone can have the same apex without replacing the first.

The product-object operation at every level is:

```python
X * Y == C.Products()(X, Y)
```

`C` inherits its `Products()` subcategory construction, the nontrivial product objects, from `Cat`. The specifications spell the general case `C.Products()(X, Y)`.
The common unambiguous case can expose `product_projection(i)` as a convenience. Code that must select among presentations uses `p.leg(i)`. A category-owned standard algebraic operation can override the inherited `*`.

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

state that `F` preserves or creates `I`-limits. `CreatesLimits(I)` is a property subcategory of `Fun`, so of `Fun(C, D)` for every `C, D`, and its generated property is `F.is_limit_creating(I)` (D158). For the shape family `Discrete: Sets() -> Cat()`, `CreatesLimits(Discrete)` states creation of the limits of every discrete shape. Their colimit forms derive through `Op`. A right adjoint preserves limits. An equivalence creates and reflects limits and colimits. These implications follow [Mathlib, adjunctions and limits](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Adjunction/Limits.html) and [Mathlib, creates limits](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Limits/Creates.html).

A functor's theorem is the property subcategory it is constructed into (D158).
A leaf states that a structure functor `U` creates `I`-limits by constructing `U` into `Fun(C, D).CreatesLimits(I)` at its declaration.
`Fun.Fibrations()` is the property subcategory of fibrations, constructed and retained as a full subcategory of `Fun.Isofibrations()`: a fibration is an isofibration, since the cartesian lift of an isomorphism is an isomorphism ([nLab, "Grothendieck fibration"](https://ncatlab.org/nlab/show/Grothendieck+fibration), `POL-MATH-040`), and the containment is stated as that monomorphism, not induced (D83). A structure functor declared into `Fibrations()` therefore carries inheritance under D167. The poset forgetful functor is faithful and an isofibration; it preserves small limits. Its exact declaration and chosen lifts belong to [ordered sets](ordered-sets.md#products).
A lifted construction can additionally require its chosen apex and defining morphisms to map exactly to the chosen ambient construction (D76).
Preservation alone supplies an isomorphic comparison. The construction states which requirement it imposes.
For a faithful functor, executable lifting data is supplied once per shape or discrete shape family:

```python
U.with_limit_lifting(I, on_apex, on_morphism)
```

`on_apex(K, c)` receives `K: I -> C` and a retained limiting cone `c` over `U * K`. It returns an object `L` of `C` with `U(L) is c.apex()`.
`on_morphism(X, Y, f)` returns a morphism `X -> Y` whose image under `U` equals `f`.
It is required on the ambient projections and on the ambient mediators from every competing source cone. Existence on this domain is the supplied lifting theorem.
The generic construction forms the lifted cone and obtains each mediator by mapping a competing cone through `U`, applying `c.lift`, and lifting that map.
Faithfulness reflects the cone equations and proves uniqueness of the mediator. This is the constructive content of [Mathlib's `LiftsToLimit`](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Limits/Creates.html#CategoryTheory.LiftsToLimit).
The exact shape takes precedence over the `Discrete` family. Among selected structure functors, declaration order chooses the construction.
`C.Limits(I)(K)` and its named product and equalizer forms use these retained data automatically. A category with another realization supplies its owned `limit_construction` or complete universal data.
The [poset-products template](poset-products-minimal-template.py) supplies componentwise order and the existing monotone-map constructor. Limit creation additionally requires reflection of limits; the theorem declaration and chosen executable data have distinct roles.

## Comma categories, slices, coslices, and fibers

For `F: A -> C` and `G: B -> C`, `Comma(F, G)` has objects `(a, b, f)` with `f: F(a) -> G(b)`. It retains its projections to `A` and `B` and the natural transformation between their composites with `F` and `G`. It is the pullback of `(ev(0), ev(1)): Fun([1], C) -> C * C` along `F * G`. This is the standard comma construction in [Mathlib](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Comma/Basic.html).

For `K = Cat().Comma(F, G)`, `K.from_arrow(a, b, f)` constructs that object.
Its `first()`, `second()`, and `arrow()` methods return `a`, `b`, and `f`.
`Mor(K)(x, y)(u, v)` constructs the pair satisfying `G(v) * x.arrow() == y.arrow() * F(u)`.
The morphism's `first()` and `second()` return its components.
The generic limit of categories supplies componentwise identity, composition, and universal mediation.

`Fun(I, C).TotalCones()` specializes the comma category of the diagonal `C -> Fun(I, C)` and the identity of `Fun(I, C)`.
It inherits the comma constructors and maps through its declared inclusion.
Its objects recover their cone presentations from the defining arrows; its morphisms expose the apex map and diagram transformation.

`C.SliceOver(x)` and `C.CosliceUnder(x)` are the fixed-object comma categories. Equivalently, the slice is the pullback of `Fun([1], C).ev(1)` along `x: * -> C`, and the coslice is the pullback of `Fun([1], C).ev(0)` along `x`. Each retains its pullback projection to `Fun([1], C)`, selected as `C.SliceOver(x).projection()` or `C.CosliceUnder(x).projection()` (D157). The varying object is the composite of that projection with `Fun([1], C).ev(0)` or `Fun([1], C).ev(1)`.

For the slice over `x`, an object is `(X, f: X -> x)`. `C.SliceOver(x).projection()` returns the defining morphism `f`; `Fun([1], C).ev(0) * C.SliceOver(x).projection()` gives the varying object `X`, and the composite with `Fun([1], C).ev(1)` gives the constant object `x`.

For the coslice under `x`, an object is `(X, f: x -> X)`. `Fun([1], C).ev(1) * C.CosliceUnder(x).projection()` gives the varying object `X`; the composite with `Fun([1], C).ev(0)` gives the constant object `x`.

Two distinct functors carry distinct lift data:

- the codomain evaluation `Fun([1], C).ev(1)` is a fibration when `C` has pullbacks; the cartesian lift of `f: y -> x` at `p: z -> x` is the pullback `z *_x y -> y`, retained with both pullback projections (nLab "codomain fibration");

- the fixed slice projection `C.SliceOver(x) -> C` is the category of elements of `Mor(C)(-, x)` and a discrete fibration for every `C`; the cartesian lift of `f: y -> z` at `(z, p: z -> x)` is `f: (y, p compose f) -> (z, p)`, by precomposition, with no pullback and no hypothesis on `C` (nLab "discrete fibration").

The fiber of `Fun([1], C).ev(1)` over `x` is `C.SliceOver(x)`. The total category `Fun([1], C)` and its fiber are distinct retained objects with distinct lifts.
Dually, `Fun([1], C).ev(0)` is an opfibration when `C` has pushouts, with cocartesian lifts by pushout, and the fixed coslice projection `C.CosliceUnder(x) -> C` is a discrete opfibration with cocartesian lifts by postcomposition.
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
C.Subobjects(X)       = C.SliceOver(X).Monomorphisms()
C.Superobjects(X)     = C.CosliceUnder(X).Monomorphisms()
C.CoveringObjects(X)  = C.SliceOver(X).Epimorphisms()
C.CoveredObjects(X)   = C.CosliceUnder(X).Epimorphisms()
```

`Cat().ObjectType` defines these methods once, and every category inherits them.
The slice or coslice retains the projection `C.SliceOver(X).projection()` or `C.CosliceUnder(X).projection()`, which returns its defining arrow.
`Monomorphisms()` and `Epimorphisms()` pull back the corresponding property subcategory of `Mor(C)` along that functor.

Thus `C.Subobjects(X)` is the full subcategory of `C.SliceOver(X)` on monomorphisms.
Its objects are pairs `(A, i)` with `i: A -> X` monic.
A morphism `(A, i) -> (B, j)` is a morphism `f: A -> B` with `j compose f = i`.

`C.Superobjects(X)` is the full subcategory of `C.CosliceUnder(X)` on monomorphisms.
`C.CoveringObjects(X)` is the full subcategory of `C.SliceOver(X)` on epimorphisms.
`C.CoveredObjects(X)` is the full subcategory of `C.CosliceUnder(X)` on epimorphisms.
Every object retains its defining morphism.

## Indexed categories, Yoneda, and representability

For a pseudofunctor `P: C.op() -> Cat()`, `Grothendieck(P)` is its total category. Its objects are pairs `(c, x)` with `x in P(c)`. A morphism `(c, x) -> (d, y)` is `(f, phi)` with `f: c -> d` and `phi: x -> P(f)(y)`.
Its projection to `C` is a fibration and its fiber over `c` is equivalent to `P(c)`. The construction acts on morphisms of indexed categories. See [Mathlib, Grothendieck construction](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Bicategory/Grothendieck.html).

A category of chosen data specifies which morphisms preserve that datum and which morphisms are cartesian (D75).
Its name alone does not determine these choices. See [Stacks, Definition 4.33.5, tag 02XJ](https://stacks.math.columbia.edu/tag/02XJ) and [nLab, Grothendieck construction](https://ncatlab.org/nlab/show/Grothendieck+construction).

Conversely, a fibration `p: E -> C` supplies fibers and cartesian reindexing. Base change along `F: D -> C` is `F.base_change(p)`. This is the general transfer operation for categories of objects equipped with selected data. An inverse-image property category is the subterminal-fiber case.

The Yoneda and co-Yoneda embeddings are retained functors:

\[
y:C\longrightarrow\operatorname{Fun}(C^{op},\mathbf{Set}),
\qquad
y^\vee:C^{op}\longrightarrow\operatorname{Fun}(C,\mathbf{Set}).
\]

The Yoneda embedding is fully faithful. Its object action supplies the representable hom functors. See [Mathlib, Yoneda](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Yoneda.html).

This section fixes the mathematical declaration before `Sets()` is executable.
The executable object and morphism actions activate only after the production `Sets()` phase.
Before that phase, the core retains only the generic signature and universal laws.

For `F: C.op() -> Sets()`, `Representations(F)` has objects `(X, eta)` with `X in C` and a natural isomorphism `eta: y(X) -> F`. A morphism `(X, eta) -> (Y, theta)` is a morphism `u: X -> Y` such that `theta compose y(u) = eta`. Yoneda makes such a morphism invertible. The functor is representable exactly when this category is inhabited. Selecting an object supplies the representing object and isomorphism. This property-and-data distinction follows [Mathlib, represented functors](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/RepresentedBy.html).

For a test functor `j: A -> C`, `j.restricted_yoneda()` is

\[
N_j:C\longrightarrow\operatorname{Fun}(A^{op},\mathbf{Set}),
\qquad
N_j(X)(a)=\operatorname{Mor}(C)(j(a),X).
\]

A separating test category places this functor in `.Faithful()`. A dense test category places it in `.FullyFaithful()`. The canonical evaluation morphisms and presentations belong to this functorial construction, as specified in [Separating families and categorical generators](separating-families-and-categorical-generators.md).

Monads, comonads, Eilenberg--Moore categories, mates, and reflective or coreflective subcategories extend this calculus after the categorical core.
The retained adjunction data supports them without a new transport mechanism.

## Examples

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

`PointedSets()` is `Sets().CosliceUnder(Sets().Terminal())`.
Its structure functor to `Sets()` is `Fun([1], Sets()).ev(1) * Sets().CosliceUnder(Sets().Terminal()).projection()`, that is `(X, x) |-> X` (D157). The projection `Sets().CosliceUnder(Sets().Terminal()).projection()` itself returns the point `* -> X`, that is, the morphism `1 -> X`, that selects `x`.
The leaf class declares itself the implementation of this coslice through its identity structure functor (D156; [pointed-sets template](pointed-sets-minimal-template.py)).

### Product categories and `Fun([1], C)`

For categories `C` and `D`, `product_projection(0)` and `product_projection(1)` are the two functors from `C * D` to its factors.

The construction `Fun([1], C)` creates `Fun([1], C).ev(0)` and `Fun([1], C).ev(1)`. These functors exist without being returned from `structure_functors()`.

## Compiled public consequence

[Structure functors](#structure-functors-and-inherited-classes) owns the declaration and inheritance condition.
For a target that carries inheritance, its methods run directly on the initialized source object, element, or morphism.
The named functor constructs its separate public images.
[resolution.md](resolution.md#direct-inherited-execution) owns the private mechanism.

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
| `Functor.comp` and whiskering functors | `G * F`; `Fun.composition(A, B, C)` and its morphism action |
| `Functor.fromPUnit X` | `D.Point()` in the structure functors of the class of `X`, an object of `Fun(*, D)` |
| `ObjectProperty.FullSubcategory P` | the property subcategory `C.P()` |
| `ObjectProperty.ι P` | `Fun(C.P(), C).Monomorphisms().Isofibrations().Full()()` |
| monomorphism induced by `P -> Q` | `Fun(C.P(), C.Q()).Monomorphisms().Isofibrations().Full()()` |
| `CategoryTheory.Core` | `Core.on_object(C)`, written `C.Core()` |
| `Core.inclusion` | `epsilon_C: U(C.Core()) -> C` |
| `ConcreteCategory.forget`, `HasForget₂.forget₂` | an extra structure containing one chosen functor and its required compatibility |
| `Prod.fst`, `Prod.snd` | `product_projection(0)` and `product_projection(1)` |
| `Arrow.leftFunc`, `Arrow.rightFunc` | `Fun([1], C).ev(0)` and `Fun([1], C).ev(1)` |
| `Over.forget` | `Fun([1], C).ev(0) * C.SliceOver(x).projection()` |
| `StructuredArrow.proj` | the projection retained by the structured-arrow construction; for a coslice, `Fun([1], C).ev(1) * C.CosliceUnder(x).projection()` |
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
This repository uses category-owned predicate meanings, public SymPy propositions, `ask()`, direct property construction, and same-object refinement.
The mathematical definitions and the declared containments remain the same.

Mathlib's `ConcreteCategory` contains a fixed faithful functor to `Type` as extra structure.
Its `HasForget₂ C D` class also contains a chosen functor `C -> D`; it does not derive one from the endpoints.
See [ConcreteCategory.Forget](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/ConcreteCategory/Forget.html).

Mathlib's `Functor.fromPUnit X : Discrete PUnit ⥤ C` sends the punctual category to a chosen object, and `Functor.equiv` states the equivalence `(Discrete PUnit ⥤ C) ≌ C`. See [PUnit](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/PUnit.html).
Here the class of `X` is the category `X` itself, an abstract new category (D161).
`D.Point()` in its structure functors is the point functor of `X`; selecting it places `X` in `D` (D128, D154).

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

- Every functor property method returns its containment proposition.

- Assumptions and exact positive results use the general same-object refinement path.

- Functor properties have no computational handlers.

- A declared containment between property subcategories is its monomorphism.

- The monomorphism of a full subcategory is fully faithful by construction.

- `Op: Cat() -> Cat()` acts on categories and functors, dualizes natural transformations, and retains `Op * Op ≅ Id`.

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

- Every functor is named by its construction or given as an explicit composite.

- A retained functor is selected by the named method of its construction, `C.CosliceUnder(X).projection()`, `Fun(I, C).ev(i)`, `P.product_projection(i)`; a composite is `G * F`.

- A class implements a category otherwise named by selecting that category's identity functor as a structure functor.

- A functor's theorem is the property subcategory it is constructed into; `CreatesLimits(I)` is one, with property `is_limit_creating(I)`.

- Each category presentation retains all projections and evaluations required by its definition.

- `Cat().Products()` and `Cat().Coproducts()` accept sequence-indexed category diagrams.

- Selected product and coproduct presentations own their legs and universal maps.

- `Cones(D)` and `LimitCones(D)` separate the universal presentation from its apex.

- The total category of limiting cones retains its diagram projection and apex functor. Product and coproduct apex interfaces use the essential images specified above.

- `.PreservesLimits(I)` and `.CreatesLimits(I)` are functor-property categories. Their colimit forms derive through `Op`.

- Every object of `Cat().Subobjects(P)` for a product category `P` retains its presenting monomorphism, then derives its component functors by composition.

- Slice and coslice categories are pullbacks of `Fun([1], C).ev(1)` and `Fun([1], C).ev(0)` along the chosen object and retain their pullback projections, `C.SliceOver(x).projection()` and `C.CosliceUnder(x).projection()`.

- Fibration and opfibration structure retains its cartesian or cocartesian lifts.

- `p.Fiber(b)` exists for every functor. `F.base_change(p)` retains the pullback projection and comparison square.

- `Grothendieck(P)`, Yoneda, co-Yoneda, restricted Yoneda, and `Representations(F)` are generic constructions.

- Kan extensions retain their units, counits, and universally induced natural transformations.

- Every category class is a point in `Cat`: writing the class populates its structure functor `* -> Cat`.

- `C.Point()` is a functor `* -> C`, registered in the relevant subcategory of `Fun(*, C)`; a leaf class places its object `X` in `C` by adding `C.Point()` to its structure functors.

- Placement of a category `C` in a structured category `D` through `D.Point()` gives `C` the `D.ObjectType` inheritance and `C.ObjectType` the `D.ElementType` inheritance.

- Every structure functor is an ordinary object of `Fun`.

- `structure_functors()` determines the immediate compiled class bases and inherited method surface.
  Each named functor owns its public images.

- Sage dynamic classes and Sage's controlled linearization derive the complete MRO from those immediate bases.
