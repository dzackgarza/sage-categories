# Functors, `Cat`, and structural inheritance

## Contents

- [Kernel ownership](#kernel-ownership)

- [Functors as morphisms of `Cat`](#functors-as-morphisms-of-cat)

- [The `Mor(n, C)` tower](#the-morn-c-tower)

- [Canonical objects of `Cat`](#canonical-objects-of-cat)

- [Functor property subcategories](#functor-property-subcategories)

- [Property resolution](#property-resolution)

- [Monomorphisms of `Cat()` and placement](#monomorphisms-of-cat-and-placement)

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

The kernel owns `Cat`, the category of categories.
Every category in this repository is an object of `Cat` and uses its implementation type:

```python
Category = Cat().ObjectType
```

Thus `Sets()`, `Mor(C)`, and every property subcategory are instances of `Cat().ObjectType`. They do not form a second Python category hierarchy.

Bootstrap follows the same local/public split.
A stable `CategoryPointKernel` exists without a `Cat()` instance.
Module loading preallocates the compiled `Cat().ElementType` class over that kernel.
`ObjectOfCategory`, `ElementOfObject`, and `MorphismOfCategory` then derive from this one stable class.
When the `Cat()` singleton exists, the compiler copies the distinct `CategoryPointDeclaration` into the preallocated class.
It compiles `Cat().ObjectType` and `Cat().MorphismType` next.
`CategoryDeclaration` supplies the local `Cat` object role.
After the singleton is compiled, `Category` names `Cat().ObjectType`. The local declaration and public category class are distinct.
`Cat` owns the same role types as every other category:

- `Cat().ObjectType` implements categories;

- `Cat().MorphismType` implements functors;

- `Cat().ElementType` is the role "generalized element of a category", a functor `T -> C`; its generalized points `1 -> C` are the objects of `C` and its generalized points `[1] -> C` are the morphisms; every `C.ObjectType` refines it with domain `1`, every `C.MorphismType` with domain `[1]`;

- `Cat()(...)` constructs categories;

- `Fun = Mor(Cat())` constructs the category whose objects are functors.

These domain refinements use one Python inheritance root.
The kernel compiles `Cat().ElementType` first.
A root object role continues through `ObjectOfCategory` to that compiled class.
A root morphism role continues through `MorphismOfCategory` to the same class.
Ordinary `C.ElementType` inheritance keeps its element-role graph and ends at `Cat().ElementType`.

The kernel also supplies the uniform categorical constructions, defined once at the `Cat()` level and applicable to every category:

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

Every generalized element is represented by its defining morphism.
`F.on_element(t)` applies `F.on_morphism` to that morphism.
The functor stores no element callback, element functor, or element capability.

For fixed `C, D in Cat()`, the functor category is endpoint application to `Mor(Cat())`:

```python
Fun(C, D) is Mor(Cat())(C, D)
```

Its objects are functors `C -> D`. Its morphisms are natural transformations.
Natural isomorphisms are the objects of `Mor(Fun(C, D)).Isomorphisms()`.

`Fun(C, D)` is the full subcategory of `Fun` on functors with domain `C` and codomain `D`. It is a genuine full subcategory because a 2-morphism connects parallel 1-morphisms only.

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
Each property has its owned predicate, trusted constructor, assumption route, implication rules, and optional computational routes.
Fixed endpoints use the same dispatch for every property subcategory `P` of `Mor(K)`: `P(A, B)` is `Mor(K)(A, B).P()`, one cached object.

## Canonical objects of `Cat`

`Cat()` owns these objects, each constructed once and retained by identity:

- `Cat().Empty()`: the empty category;

- `Cat().Terminal()`, written `1` and equal to `[0]`;

- `Cat().Simplex(n)`, written `[n]`: the poset `0 < 1 < ... < n` as a category, for `n >= 0`; `[1]` is the walking arrow, `[2]` the walking commutative triangle;

- `Cat().Boundary(n)`, written `d[n]`: the free category on the graph of the boundary of the `n`-simplex; `d[2]` is the walking triangle with no commutation relation;

- `Cat().Horn(n, k)`, written `L(n, k)`: the free category on the `k`-th horn graph of the `n`-simplex; `L(2, 0)` is the walking span and `L(2, 2)` the walking cospan; `L(2, 1)`, the free category on `0 -> 1 -> 2`, contains the composite `0 -> 2` and is the walking composable pair `[2]`, so `Cat().Horn(2, 1) is Cat().Simplex(2)`;

- `Cat().WalkingIsomorphism()`: two objects and two mutually inverse morphisms;

- `Cat().WalkingParallelPair()`: two objects and two parallel morphisms;

- `Cat().Point(X)`, written `{X}`: the one-object category on a distinguished object `X`, one per `X`; see [Point categories and point functors](#point-categories-and-point-functors).

Two calls return one object by identity.
No construction creates a second terminal object, simplex, or walking structure.

### Separators and separating families

A category may choose a family of objects whose generalized points determine its morphisms.
[nLab, separator](https://ncatlab.org/nlab/show/separator) (inspected 2026-08-28) names it: a family `S = (S_a)_{a in A}` is a "separating family or a generating family" when "for every pair of parallel morphisms `f, g : X -> Y`, if `f . e = g . e` for every `e : S_a -> X` sourced in the family, then `f = g`", and for locally small `C`, "`S` is a separating family if the family of hom functors `Hom(S_a, -) : C -> Set` (for `a in A`) is jointly faithful".
The one-element case is a separator: "`S` is a separator if the hom functor `Hom(S, -) : C -> Set` is faithful."

`Category.separating_family()` returns that family, and the leaf's declaration that it separates is trusted (`POL-MATH-037`). `Sets()` chooses `(1,)`, so its separator is the terminal object and its generalized points `1 -> X` are its elements.
`Cat()` chooses `(1, [1])`: objects and morphisms jointly separate functors, so `Cat()` has a separating family of two rather than a single underlying-set functor, and none is built.

A separating family of several is a family of hom functors that is jointly faithful.
It is not one set-valued functor, and no coproduct of the hom-sets is formed: `Category.represented_functor()` therefore constructs `Mor(C)(G, -): C -> Sets()` for a single separator `G` and fails loudly for a larger family, naming the joint faithfulness that a family states instead.

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

- `Full(F)` states that every morphism `F(X) -> F(Y)` has a preimage under `F.on_morphism()`;

- `Faithful(F)` states that each map on morphisms is injective;

- `FullyFaithful(F)` is the conjunction of fullness and faithfulness;

- `EssentiallySurjective(F)` states that every object of `D` is isomorphic to an image of an object of `C`;

- `Equivalence(F)` states that `F` is fully faithful and essentially surjective.

These definitions introduce no selected witnesses.
A separate construction can select a preimage morphism, inverse functor, unit, or counit when an operation requires that data.

The kernel records the categorical implications:

```text
FullyFaithful(F) implies Full(F)
FullyFaithful(F) implies Faithful(F)
Full(F) and Faithful(F) imply FullyFaithful(F)
Equivalence(F) implies FullyFaithful(F)
Equivalence(F) implies EssentiallySurjective(F)
```

These implications induce the corresponding monomorphisms between property subcategories.

## Property resolution

Functor properties use the general `Predicate`, `ask()`, and property-refinement framework.
They have no separate evidence or decision system.

An existing functor can enter a property category by direct construction:

```python
F = Fun(C, D)(on_object, on_morphism)
F = Fun(C, D).Full()(F)
```

This is the property category's trusted constructor.
The code writer uses external mathematics to select `Fun(C, D).Full()`. The constructor records that assertion and refines the same owned functor.
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

uses category placement, active assumptions, and categorical implications.
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

`x in C` is established placement (`POL-CAT-068`). It propagates from `S` to `T` exactly along a functor that is a monomorphism of `Cat()` and an isofibration.
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

Suppose predicates `P` and `Q` on `C` satisfy

\[
P(X)\Longrightarrow Q(X).
\]

The implication is that same declaration between the two property subcategories:

```python
iota = Fun(C.P(), C.Q()).Monomorphisms().Isofibrations().Full()()
```

The source property is stronger and the target property is weaker.
The implication belongs to the property relation, and its fixed-endpoint functor category owns the construction.

A wide subcategory retains every object and restricts morphisms by a multiplicative morphism predicate.
Its monomorphism is faithful by construction.
A general subcategory monomorphism is also faithful.
Neither becomes full unless its mathematical definition establishes fullness.

## Structural inheritance

`structure_functors()` is a repository compiler declaration.
It is not an additional kind of functor and is not part of Mathlib's functor theory.

Every entry is an ordinary owned object of `Fun`. Its mathematical existence and properties come first.
For example, finite sets are a full subcategory of sets, so their subcategory monomorphism exists independently of method compilation.

A category selects an immediate functor only when the functor states the mathematical change of structure that supplies inherited operations:

```python
class FiniteSetsCategory(Category):
    def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
        return (Fun(self, Sets()).Monomorphisms().Isofibrations().Full()(),)
```

The leaf explicitly constructs the monomorphism and records fullness through the selected property category.
The tuple tells the compiler to include the compiled classes owned by `Sets()` through that functor.

The categories `Fun(self, D)` can contain many other functors.
Their existence does not affect the compiled public surface.
Selection changes compiler behavior only.
It does not change a functor's mathematical definition.

Each category lists only immediate selected functors.
The kernel obtains longer routes by composition and applies [resolution.md](resolution.md) to diamonds.

### Compiled roles

A local declaration and the compiled class built from it are distinct classes.
The declaration owns the category's new methods.
`C.ObjectType`, `C.ElementType`, and `C.MorphismType` are the compiled classes, and only they are public.

The bases of a compiled class are the compiled classes of the selected target categories, in the controlled order of [resolution.md](resolution.md).
A role that reaches no other role stands on the kernel class of its role: `Category` for the category role, otherwise the kernel base of objects, elements, or morphisms.

A declaration is not a base.
The kernel copies its class body onto the compiled class and drops the declaration's own Python bases.
The copy carries a category's own declaration onto its own compiled class, which is class construction and not a second owner: no category acquires a method owned by another one this way (`POL-CAT-006`). A method declared with zero-argument `super()` closes over `__class__`, which Python bound to the declaration; the kernel rebinds that closure to the compiled class, so `super()` enters the compiled chain.

Each local constructor accepts one exact typed datum.
That datum contains only the state introduced at its category.
The constructor initializes that state and calls `super().__init__()` once.
A construction input can also carry exact semantic data used only to construct selected ancestor state.
A node that retains none of that data has no local initializer, and its generated wrapper advances.
Every role construction input keeps its datum separate from its identity.
The object identity records its category.
The morphism identity records its category and endpoints.
The `Cat().ElementType` identity is the closed sum

```text
GeneralCategoryPointIdentity(defining_morphism)
ObjectStageIdentity(parent_category)
ArrowStageIdentity(parent_category, domain, codomain)
```

The general form is used by an ordinary generalized element.
Its defining morphism is a functor only when the represented object is a category.
The construction input already stores the canonical object or morphism for the two forms.
Their local `Cat().ElementType` datum is `None`.

A selected functor retains a pure typed conversion from its source construction input to its target construction input for each role.
Thus a poset datum states only its order data.
Its selected functor to `Sets()` uses the source identity and datum to return the input retained by the canonical set image.
The conversion does not inspect a partly initialized poset.

The kernel allocates the compiled value first.
It creates the root input with that value as its canonical image.
It then follows structural edges and computes one construction input for each reachable node.
An object context also precomputes `ObjectStageIdentity(C)`. A morphism context also precomputes `ArrowStageIdentity(C, A, B)`. These inputs initialize the common `Cat().ElementType` root.
The kernel checks every route to a common node by canonical-image and input identity.
Finally, it activates one class-specific construction context and starts initialization.

The controlled C3 order can place unrelated branches next to each other.
For example, the order for `D -> B -> A` and `D -> C -> A` is `D, B, C, A`. Generated wrappers do not interpret `B` followed by `C` as a structural edge.
Each wrapper reads its own node's precomputed input and passes only its datum to that node's local constructor.
Literal `super()` enters the next wrapper.
C3 initializes `D`, `B`, `C`, and `A` once each.

The raw declaration classes do not occur in the public MRO. Python functions copied from them retain a `__class__` closure.
The compiler rebinds that closure to the final compiled class before it installs the function.
This makes literal zero-argument `super()` enter the controlled compiled MRO.

Object, element, and morphism constructor conversions are retained implementation data of the selected functor.
For an object or morphism, the target image retained by a conversion is the canonical `F(x)`. Public object or morphism application returns that exact value.
The element conversion supplies compiler input.
Public element application follows the morphism action described below.
All routes to one node return the same image and construction input by identity.
Identity functors retain identity conversions.
Composite functors retain the composites of their factors' conversions.

Each canonical public value retains one root construction input.
A conversion returns the input retained by its canonical target image.
The input type names its exact canonical role value and local datum.
During source construction, the conversion reads the source input's typed datum and identity, constructs the canonical target through the target category, and retains that image.
Later public object or morphism application reads the source value's retained input and calls the same conversion.
No conversion reads fields of a partly initialized source value.

An inherited method executes on the descendant.
Its declaring class's private state retains the canonical functor image.
A method that must supply an object, element, or morphism in the declaring category uses that image.
A method can inspect its declaring class's local state directly when no category-sensitive value crosses the call boundary.

An element of `X in C` is a generalized element `t: T -> X`, an object of `C.SliceOver(X)` ([nLab, generalized element](https://ncatlab.org/nlab/show/generalized+element), inspected 2026-08-28: "a morphism `x : U -> X` a generalized element of `X`"). `T` is the domain of `t` and `t.parent()` is its codomain `X`, both read from the defining morphism; the repository adds no second accessor for either.
Its general identity retains the defining morphism.
An object `X in C` uses `CategoryPointIdentity(C)`: its domain is `Cat().Terminal()`, its parent is `C`, and `X.defining_morphism()` lazily requests `C.point_functor(X)`. A morphism `f: A -> B` in `C` uses `CategoryArrowIdentity(C, A, B)`: its domain is `Cat().Simplex(1)`, its parent is `C`, and `f.defining_morphism()` lazily requests `C.arrow_functor(f)`. Every `F: C -> D` induces `F/X: C/X -> D/F(X)`, sending `t` to the public image `q = F(t): F(T) -> F(X)` through `F.on_morphism`. This action requires no additional functor data.
The canonical value `q` retains its own root construction input and cache identity.
For a source whose domain is not the separator, the element conversion gives the compiler the input retained by `q`.

A category may choose a separator `G_C`: `1` for `Sets()`; `Cat()` uses `1` for objects and `[1]` for morphisms.
A point of `X` is a generalized element whose domain is exactly `G_C`. A selected structural functor that exposes the target's point methods retains a separator comparison `c_F: G_D -> F(G_C)`. For a a `t: G_C -> X` at the separator, the compiler precomposes `q = F(t)` with `c_F` and obtains the input `p: G_D -> F(X)` at the target separator.
The element conversion gives the compiler the input retained by `p`. The values `q` and `p` have separate identities and cache entries when their domains, defining morphisms, or codomains differ.
For an identity functor, \(c_{\mathrm{id}} = 1_G\). For composable `F: C -> D` and `H: D -> E`, \(c_{H \circ F} = H(c_F) \circ c_H\).

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
    return (Fun(self, D).Monomorphisms().Isofibrations()(),)
```

A point functor is a selected structural functor under exactly this declaration and under no other.
Like every selected functor, it contributes the target's compiled classes, typed construction-input conversions, canonical images, constructor chain, and inherited public methods (`POL-FUN-003`, `POL-FUN-035`). Its generalized-element action is derived from its morphism action (`POL-FUN-002`). The compiler reaches it through composition in `Cat` with the rest of the structural graph.

Before a point-inherited initializer runs, the kernel retains the point category, its selected point functors, and all required role conversions.
The ordinary compiled C3 chain then initializes each reachable target class once.
A target constructor receives its exact converted datum and calls `super().__init__()`. Thus a point placement supplies the target class's state as well as its methods.

A point placement arrives through same-object Sage refinement.
It extends each affected compiled class without invalidating existing descendants or values, then runs every newly required initializer once.
The distinguished object keeps the role identities it already has, and the placement adds no second inheritance registry.

Refinement is what makes a point category formed from a runtime object work.
`Cardinal()` and `Ordinals()` are constructed before `Semirings(Cat())` exists, and each receives its semiring surface when `Cat().Point(Cardinal())` and `Cat().Point(Ordinals())` declare their point functors.
No construction order between the three is required.

The defining morphism `1 -> C` used by an object-class identity remains lazy.
It is distinct from a selected monomorphism `{X} -> D`.  Laziness of the defining morphism does not delay the selected structural declaration or its construction-input conversions.
The same separation applies to the defining functor `[1] -> C` of a morphism.

For `{C} -> D`, the conversions initialize `D.ObjectType` state on `C`, `D.ElementType` state on the objects and morphisms, and `D.MorphismType` state on `1_C`.

### The level shift

Take the distinguished object to be a category `C`. Then `{C}` has one object at the `Cat()` level, while `C` has its own objects and morphisms one level below.
The compiled surface follows that difference from `Cat().ElementType`, which is already the role "generalized element of a category": a functor `T -> C`, refined by `C.ObjectType` at domain `1` and by `C.MorphismType` with domain `[1]`.

A selected point functor `{C} -> D` therefore compiles as:

| Surface of `D` | Surface it supplies |
| --- | --- |
| `D.ObjectType` | the category `C` itself, a `Cat().ObjectType` value |
| `D.ElementType` with domain `1` | `C.ObjectType`, the objects of `C` |
| `D.ElementType` with domain `[1]` | `C.MorphismType`, the morphisms of `C` |
| `D.MorphismType` | `{C}.MorphismType`, whose sole value is `1_C` |

The shift is the domain clause of `Cat().ElementType` applied to one object.
It adds no second inheritance mechanism, no route normalization, and no propagation registry.
`C` remains an object of `Cat()`, `{C}` remains a distinct object of `Cat()`, and `C.structure_functors()` continues to state the structure of `C` as a category.

The middle two rows are the one structural step whose two roles differ, and no functor acts along it.
The value of the step is the value's own defining morphism: an object of `C` names the functor `1 -> C` that selects it, a morphism of `C` names the functor `[1] -> C`, and those are what the generalized elements of `C` are.
`Cat().Point(C)` retains one point category per object; the compiler reads that retention to find `{C}` from `C`, and `C` records nothing.

A level shift contributes the corresponding target compiled class to each affected compiled chain.
The selected point functor supplies the exact construction-input conversion for that role.
The same constructor chain therefore gives `C`, its objects, its morphisms, and `1_C` all state required by their target classes.

`parent()` and `defining_morphism()` never compile.
Every kernel class defines its own, and the compiler calls them to find a value's node, so a compiled copy would call the accessor it is transporting for.
`{C}`'s element node is the first to reach `Cat()`'s, where all three are declared.

The selected installation mechanism must preserve one compiled class identity and one constructor order for `C`, its descendants, and values that already exist when the placement becomes available.

`{C}` retains one generalized element per defining functor.
Two selected routes to `({C}, element)` must produce the same image, and a morphism of `C` placed in several property subcategories is reached by exactly such routes.

### Ambient algebraic categories

An algebraic category takes its ambient category as an argument.
Thus `Semirings(A)` classifies semiring objects whose carrier, operations, units, and laws live in `A`. For example, `Semirings(Sets())` has set carriers and set maps.
`Semirings(Cat())` has category carriers and functors.
A category-valued distinguished object therefore uses a point functor into `Semirings(Cat())`.

`Semirings(Cat())` is the category of strict internal semiring objects.
Associativity, units, symmetry, distributivity, and absorption are equalities of functors, exactly as `Semirings(Sets())` states them as equalities of maps.
`Cat()` supplies the finite products those functors are formed over.

Its two consumers satisfy that strictness by construction.
`Cardinal()` and `Ordinals()` are skeletal (`POL-SET-025`), so each operation selects one representative and `(a + b) + c` and `a + (b + c)` are one object.
The equality of functors therefore holds on objects and on morphisms.

A category-valued semiring whose carrier is not skeletal is outside this definition.

### Ordinals as a semiring

An ordinal is an object of `Ordinals()` ([ordinals.md](ordinals.md)). The commutative semiring of ordinals under the Hessenberg operations is the point functor of `Ordinals()` into `Semirings(Cat())`:

```python
# Cat().Point(Ordinals())
def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
    return (Fun(self, Semirings(Cat())).Monomorphisms().Isofibrations()(),)
```

`Semirings(Cat())` declares `zero()` and `one()` on its object surface and `+` and `*` on its element surface ([magmas-monoids-semirings.md](magmas-monoids-semirings.md)). Its constructors retain the two operation functors, the two unit objects, and the selected law data.
The point functor converts these into the corresponding compiled state.
The level shift places each public operation one level down:

```python
Ordinals().zero()          # the object surface, on the category
Ordinals().one()

alpha + beta               # the element surface on the objects of Ordinals()
alpha * beta
```

With domain `[1]` the same element surface acts on the morphisms of `Ordinals()`, which is the functorial action of the natural sum and natural product.

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

### Identity and composition

`Fun(C, C).Equivalences().identity()` constructs the identity functor on `C`. Functor composition uses the composition of morphisms owned by `Cat`.

### Subcategory monomorphisms

`Fun(S, T).Monomorphisms().Isofibrations()()` constructs an established subcategory monomorphism.
Use `Fun(S, T).Monomorphisms().Isofibrations().Full()()` when `S` is full in `T`.

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
A later structural route uses their functor components and ordinary composition.

### Essential images

For `F: C -> D`, `F.essential_image()` is the full property subcategory of `D` on objects isomorphic to `F(X)` for some `X in C`.  Its monomorphism into `D` is fully faithful by construction.
The original functor factors through this category.

A universal-construction family has more data.
`C.Products()` is the full subcategory of `C` on the chosen products, reached by its retained identity-on-values monomorphism.
It retains the universal data of each diagram `D`: `D` itself, its projections, and its universal maps.
The essential image of the product functor records only which objects are isomorphic to chosen products.

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

Let `P` be a chosen product category.
Let `j: S -> P` present `S` as a subcategory.
The corresponding object of `Cat().Products().ChosenSubobjects()` retains `j` and reads `P` as its codomain.
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

The generic pullback construction is `C.Limits(L(2, 2))` (see [Diagram shapes and universal constructions](#diagram-shapes-and-universal-constructions)). Its legs are the retained projections.
The same rule handles repeated codomains.

## Diagram shapes and universal constructions

A shape is an object of `Cat()`. A diagram of shape `I` in `C` is an object of `Fun(I, C)`, constructed from an object rule and a morphism rule like every functor.

The kernel supplies these shape constructors:

- `Discrete(S)` for `S in Sets()`: the discrete category on `S`; `Discrete` is a functor `Sets() -> Cat()`;

- the canonical objects of `Cat` above;

- `Thin(P)` for a preordered set `P`: the thin category of `P`; `omega = Thin(NN)` with its natural order is the sequential shape;

- finite presented shapes: a finite set of objects, a finite set of generating morphisms, and a finite set of relations between composable words.

A discrete diagram needs only its object rule `i |-> X_i`. The rule is an assignment on `S`; it never enumerates `S`. A Python sequence `(X_0, ..., X_n)` is the convenience form and denotes the diagram over `Discrete([n])`.

`C.Products()(diagram)` constructs one object of `C`, placed in `C.Products()`, with `product_projection(i)` indexed by `i in S` and the universal map.
The selected functor of the family is its retained identity-on-values monomorphism into `C`. `C.Coproducts()` is dual with `coproduct_injection(i)`. `X * Y` is `C.Products()((X, Y))`.

`C.Limits(I)` and `C.Colimits(I)` are the general families for one supplied shape `I`. The named conveniences are instances:

```python
C.Pullbacks()    is C.Limits(L(2, 2))
C.Pushouts()     is C.Colimits(L(2, 0))
C.Equalizers()   is C.Limits(WalkingParallelPair)
C.Coequalizers() is C.Colimits(WalkingParallelPair)
```

`C.Limits(I)` exists as a construction category for every supplied shape `I` without asserting that `C` has `I`-limits.
Constructing an object of it requires an owned limit construction of `C` for that shape, supplied universal data (an apex with its cone and mediator rule), or an exact engine construction on a declared semantic domain.

## Slices and coslices

`C.SliceOver(x)` is the pullback in `Cat()` of `ev_1: Fun([1], C) -> C` along `x: 1 -> C`. `C.CosliceUnder(x)` is the pullback of `ev_0` along `x`. A comma category `(F, G)` for `F: A -> C`, `G: B -> C` is the pullback of `(ev_0, ev_1): Fun([1], C) -> C * C` along `F * G`. Each retains its pullback projections.
The varying object is the composite with `ev_0` or `ev_1`.

For the slice over `x`, an object is `(X, f: X -> x)`. The pullback projection to `Fun([1], C)` returns the defining morphism `f`; composing it with `ev_0` gives the varying object `X`, and composing it with `ev_1` gives the constant object `x`.

For the coslice under `x`, an object is `(X, f: x -> X)`. Composing the projection to `Fun([1], C)` with `ev_1` gives the varying object `X`; composing it with `ev_0` gives the constant object `x`.

Two distinct functors carry distinct lift data:

- the codomain evaluation `ev_1: Fun([1], C) -> C` is a fibration when `C` has pullbacks; the cartesian lift of `f: y -> x` at `p: z -> x` is the pullback `z *_x y -> y`, retained with both pullback projections (nLab "codomain fibration");

- the fixed slice projection `C.SliceOver(x) -> C` is the category of elements of `Mor(C)(-, x)` and a discrete fibration for every `C`; the cartesian lift of `f: y -> z` at `(z, p: z -> x)` is `f: (y, p compose f) -> (z, p)`, by precomposition, with no pullback and no hypothesis on `C` (nLab "discrete fibration").

The fiber of `ev_1` over `x` is `C.SliceOver(x)`. The total category `Fun([1], C)` and its fiber are distinct retained objects with distinct lifts.
Dually, `ev_0` is an opfibration when `C` has pushouts, with cocartesian lifts by pushout, and the fixed coslice projection `C.CosliceUnder(x) -> C` is a discrete opfibration with cocartesian lifts by postcomposition.
These properties come from the construction theorems.
They are not runtime decisions.

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

The additive and multiplicative refinements retain their selected operation roles.

### Pointed sets

A pointed set is an object of the coslice category under the singleton set:

\[
\mathbf{PointedSet}=1\!\downarrow\!\mathbf{Set}.
\]

The selected functor is the composite of the pullback projection to `Fun([1], Sets())` with `ev_1`, that is `(X, x) |-> X`. The pullback projection itself returns the morphism `1 -> X` that selects `x`.

### Product categories and `Fun([1], C)`

For categories `C` and `D`, `product_projection(0)` and `product_projection(1)` are the two functors from `C * D` to its factors.

The construction `Fun([1], C)` creates `ev_0` and `ev_1`. These functors exist without being selected for structural inheritance.

## Compiler contract

The compiler uses `structure_functors()` as its sole structural graph.
It must:

1. require every entry to lie in `Fun`;

2. require each entry's domain to be the declaring category;

3. derive immediate target categories from functor codomains;

4. build longer paths through composition in `Cat`;

5. preserve each functor's exact object and morphism maps;

6. derive each functor's generalized-element action from its morphism action, and precompose a retained separator comparison only for the methods at the separator;

7. reject a selected edge when a target class needs construction input and the functor lacks an exact typed conversion;

8. detect a structural-image or construction-input mismatch during construction or the first public functor application: traverse every route to a reachable category in declaration order, store the first image and input, require each later route to supply the same objects by identity, and raise a construction-defect error naming both routes and the shared ancestor on a mismatch; method compilation constructs no images; diamonds otherwise follow [resolution.md](resolution.md);

9. canonicalize repeated construction of the same declared functor;

10. complete the preallocated `Cat().ElementType` root first, then build each public class from the local members, retained node initializer, generated initializer wrapper, and controlled compiled ancestor classes; rebind copied `__class__` closures to that public class;

11. compute one construction input per reachable node through structural edges; add the one object-role or arrow-role `Cat().ElementType` input to an object or morphism context; activate the matching role context and invoke each constructor once through C3;

12. derive subobject-of-product component functors by composition;

13. install the compiled classes of a point category `{X}` on its distinguished object: `{X}.ObjectType` on the value `X`, and `{X}.ElementType` on the generalized elements of `X`, which for a category `X = C` are `C.ObjectType` with domain `1` and `C.MorphismType` with domain `[1]`.

Natural transformations are trusted constructions, never compiler proofs.
There is no route normalization, route scoring, or preservation registry.

Every inherited method enters the descendant through the compiled class MRO. The declaring method runs on the original descendant instance with the supplied arguments.
It reads the declaring category's state directly on that instance, because each selected functor states how the descendant's construction data produces the data its target's constructor consumes, and the kernel used that statement to thread the descendant's constructor arguments through the ancestor initializers. Nothing is fetched, because no second value exists to fetch.
A point's construction input uses the retained separator comparison.
The method's value is returned exactly as declared.

The public surface is dynamic inheritance in Sage's sense.
The kernel builds `C.ObjectType`, `C.ElementType`, and `C.MorphismType` as dynamic classes carrying the linearized surface of every selected route.
A leaf writes no Python inheritance.
A leaf that wants a source-category result overrides the inherited method or adds its own.

The exact MRO tails are:

```text
C.ObjectType, selected object roles, ObjectOfCategory,
Cat().ElementType, CategoryPointKernel

C.MorphismType, selected morphism roles, MorphismOfCategory,
Cat().ElementType, CategoryPointKernel

ordinary C.ElementType, selected element roles, ElementOfObject,
Cat().ElementType, CategoryPointKernel
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
| `Functor.id C` | `Fun(C, C).Equivalences().identity()` |
| `Functor.fromPUnit X` | the point functor of `X`, an object of `Fun(Cat().Point(X), D)` |
| `ObjectProperty.FullSubcategory P` | the property subcategory `C.P()` |
| `ObjectProperty.ι P` | `Fun(C.P(), C).Monomorphisms().Isofibrations().Full()()` |
| monomorphism induced by `P -> Q` | `Fun(C.P(), C.Q()).Monomorphisms().Isofibrations().Full()()` |
| `wideSubcategoryInclusion P` | `Fun(Wide, C).Monomorphisms().Isofibrations()()` |
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

Mathlib uses propositions and typeclasses to carry established facts.
This repository uses owned predicates, `ask()`, assumptions, direct property construction, and same-object refinement.
The mathematical definitions and implications remain the same.

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

- Established property implications induce subcategory monomorphisms.

- The monomorphism of a full subcategory is fully faithful by construction.

- Every functor is constructed through `Fun(Source, Target)` or an established property subcategory.

- A specialized constructor receives enough mathematical data to select one functor.

- Endpoint categories and object fields never select a functor.

- The repository has no generic constructor selected by the phrase “forget structure.”

- Every structural functor is named by its construction or given as an explicit composite.

- Each category presentation retains all projections and evaluations required by its definition.

- `Cat().Products()` and `Cat().Coproducts()` accept sequence-indexed category diagrams.

- Their objects own `product_projection(i)` and `coproduct_injection(i)` respectively.

- A universal construction returns one value: the constructed object, an object of the ambient category, placed in the construction family and carrying its defining morphisms and universal maps.

- A construction family is a full subcategory of its ambient category, reached by the retained identity-on-values monomorphism, and retains the universal data of each diagram it constructed from.

- Every object of `Cat().Products().ChosenSubobjects()` retains its presenting monomorphism into a chosen product, then derives its component functors by composition.

- Slice and coslice categories are pullbacks of `ev_1` and `ev_0` along the chosen object and retain their pullback projections.

- Fibration and opfibration structure retains its cartesian or cocartesian lifts.

- Kan extensions retain their units, counits, and universally induced natural transformations.

- `Cat().Point(X)`, written `{X}`, is the one-object category on a distinguished object `X`, retained once per `X`.

- A point functor is the monomorphism `{X} -> D`, constructed through `Fun({X}, D)` and selected in `{X}.structure_functors()`.

- A selected point functor `{C} -> D` supplies complete target classes, typed constructor conversions, state, and methods to `C`, `C.ObjectType` with domain `1`, and `C.MorphismType` with domain `[1]`.

- Every selected structural functor is an ordinary object of `Fun`.

- `structure_functors()` determines the structural graph, compiled class bases, construction-input conversions, canonical images, and inherited method surface.

- The compiler derives structural paths only through composition in `Cat`.
