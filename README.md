# sage-categories

`sage-categories` is a categorical replacement universe for a significant subset of standard Sage mathematics.
It shadows familiar Sage objects with package-owned versions whose categories own their objects, morphisms, constructors, and methods.

The central rule is simple:

> A category owns implementations and constructors.
> A functor constructs an implementation in another category.

This rule replaces accidental inheritance with explicit mathematics.
It also lets one public object receive operations from every category reached by the declared functors.

The public API is not stable.
The repository contains the categorical kernel, the `Mor(n, C)` tower, and an owned `Sets()` implementation.
The complete acceptance design described below remains the current implementation target.

## One import, one mathematical universe

The required opt-in surface is a `sage_categories.all` module analogous to `sage.all`:

```python
from sage_categories.all import *
```

Python module names cannot contain hyphens, so the import uses `sage_categories`, not the distribution name `sage-categories`.

This import shadows supported standard Sage names with package-owned objects.
For example, an owned `ZZ` starts every later operation inside the package universe.
Products, modules, morphisms, subobjects, scalar changes, and every other supported construction return package-owned results.
Their public operations remain mediated by the package's categorical APIs.

The closure requirement applies recursively: every public result produced from package-owned inputs remains package-owned.
A private computation can use a Sage value or algorithm, but it reconstructs the owned mathematical result before returning.

The package does not refine arbitrary Sage objects into its category hierarchy.
It also does not promise that ordinary Sage code accepts package-owned objects or that package code accepts ordinary Sage objects.
Any such interoperability is incidental Python compatibility, not part of the contract.

A notebook that imports `sage_categories.all` commits to this package universe.
If a Sage construction is not yet owned, its downstream Sage code has no compatibility guarantee, even when that code internally uses familiar objects such as `ZZ` or free modules.
The intended remedy is to absorb the required construction, use Sage privately as its computation engine, and expose a new owned categorical API.

## Why this project exists

Sage implements many mathematical structures.
Its category framework also binds mathematical structure to dynamic Python inheritance and implementation-specific parent classes.
These mechanisms can obscure three different facts:

- which category owns an operation;

- which functor transports an object or morphism;

- which implementation performs a computation.

This project separates those facts.
Theory code should state the mathematical definition and the immediate functors that connect it to existing theory.
The kernel should compile that information into a direct method surface.

Sage's `super_categories()` is compiler input presented as if it were one mathematical
relation. It supplies dynamic class inheritance, but it does not name the functor that
makes inherited operations meaningful or explain how a source construction initializes
the target class. A Sage supercategory edge need not be a subcategory inclusion.

This repository replaces each such edge with a **structure functor** `F: C -> D` returned
by `C.structure_functors()`. A structure functor is an ordinary functor selected for class
inheritance. It can be a named projection, fibration, subcategory
monomorphism, or another mathematically specified functor. Selection alone asserts none
of those properties.

The kernel uses selection of `F` to construct `C.ObjectType`, `C.ElementType`, and `C.MorphismType`
with the applicable target classes and private runtime state. This Python inheritance
does not assert that `C` is a subcategory of `D` or that an object of `C` is an object of
`D`. The public image `F(x)` remains a separate object of `D`. Only an explicitly
declared subcategory monomorphism states a subcategory relation.

The two ordinary functor actions are complete executable constructions.
`F.on_object(X)` calls a public constructor of `D` and returns the resulting object.
`F.on_morphism(f)` calls the exact target hom-category constructor and returns the resulting morphism.
Selecting `F` adds no writer-supplied compiler description.

The separation also preserves mathematical consequences that concrete Sage implementations can lose.
For example, let `M = ZZ^3` be a free module with its standard coordinate presentation.
The selected functors to modules and then to `Sets()` give `M` the set-owned cardinality and countability interface.
The retained finite-product presentation proves that its underlying set is countable.
The chosen enumerations of the three `ZZ` factors also supply the standard product enumeration.
Countability alone does not select an enumeration; the retained construction data does.
These consequences do not depend on which Sage free-module class performs the private computation.

For example, an integral-lattice presentation has a product projection to finite-rank `ZZ`-modules.
The resulting composite of named functors to `Sets()` supplies cardinality and supports lazy enumeration.
A concrete lattice implementation that does not retain those categorical relationships can fail to expose either operation.
Long-running searches, including bounded enumeration in Vinberg-type algorithms, need those consequences without bespoke lattice-level implementations.

A leaf category should define only its new structure.
It should not copy methods from every category above it.
For example, a finite mathematical object should receive `cardinality()` from its implementation in `Sets()`. The same rule must work through long chains of functors.

## Mathematical auditability

Sage already supplies most of the underlying computations.
This project exists to make their interfaces uniform, their mathematical ownership explicit, and their composition categorical.
Category theory supplies the reuse mechanism: actual functors replace copied methods and engineering inheritance throughout the theory layer.

The kernel absorbs the Python machinery needed to compile that structure.
Outside the kernel, category code should read as the mathematical definition it implements.
A leaf-category contributor should mainly state new objects, morphisms, complete functor actions, axioms, and constructors.
The inherited categorical machinery should supply the rest.

The intended reviewer of a theory subtree is a mathematician with little programming experience.
They should be able to compare a method with its definition without auditing dynamic inheritance, container plumbing, backend types, or dispatch machinery.
Legibility and categorical uniformity are therefore primary requirements, not decoration around successful computation.

## Architecture boundaries

| Layer | Responsibility |
| --- | --- |
| Kernel | Private Sage class compilation, controlled linearization, initialization, identity caches, bootstrap, same-object refinement mechanics, and generated projections. It defines no mathematical meaning. |
| `Cat` theory | Categories, morphism and functor categories, natural transformations, universal constructions, property inverse images, fibrations, and their retained functors. This code reads as mathematics. |
| Leaf | One category's new objects, elements, morphisms, constructors, immediate functors, properties, operations, exact handlers, and theorem-backed constructions. |
| Private backend | Sage, SymPy, GAP, Julia, matrices, processes, caches, and conversions used inside category-owned methods. It returns results to their mathematical owner. |
| Generated surface | Stubs and manifests projected from accepted declarations. They are never runtime or mathematical authority. |

One mathematical fact has one semantic owner.
No second runtime or generated entity can restate a fact already owned by the mathematics.
Kernel and `Cat` theory modules do not import production leaves.
Leaves do not import kernel internals.

## Leaf-category end state

Once the kernel is established, a researcher adding a leaf category should not need to understand its implementation.
They should begin from a shipped category template, declare the new mathematical structure, connect it to nearby familiar categories through declared functors, and implement only the new methods.
They should need to read only the mathematically relevant neighboring subtrees and their functor contracts.

The compiler then supplies the complete inherited object, element, morphism, and construction interfaces.
Let \((\mathcal M,\odot,1)\) be monoidal, let \(\mathcal C\) be an \(\mathcal M\)-actegory, and let \(A\) be a monoid object of \(\mathcal M\). An object of [`Modules(A, C)`](specs/modules.md) is an object \(X\) of \(\mathcal C\) with an action \(A\mathbin{\bullet}X\to X\). The category retains the ambient monoidal category, the actegory, the acting monoid, and the action.

When closed or enriched structure represents these actions by an internal endomorphism monoid, the same module structure is equivalently a monoid morphism \(A\to\operatorname{End}_{\mathcal C}(X)\). The action morphism is the general definition.

[`Algebras(R, C)`](specs/algebras.md) is the base-relative presentation of the monoid objects in the supplied monoidal category `Modules(R, C)`. Its immediate structure functors supply the applicable general monoid, magma, and module interfaces.
A general module or algebra object reaches `Sets()` only through an explicit declared functor from its ambient category.
Cardinality and other distant capabilities arrive through functor composition rather than leaf-specific code.

For example, a researcher can add `FiniteSubsetsOfNN()` after the complete theory of sets exists.
They declare its nested `ObjectType`, `ElementType`, and `MorphismType` classes, its constructors, its monomorphism into `Sets()`, and only its new methods, such as `minimal_element()` or `gcd_of_elements()`. A nested class can have no local method when the category adds no operation of that kind. The kernel fills its bases and supplies the full inherited `Sets.ElementType` interface.
The inherited set interface also makes products, coproducts, filtered limits, and other set constructions available without new implementations in the leaf.
Each result remains an object of the category that owns the construction.
The leaf returns it to `FiniteSubsetsOfNN()` by overriding the inherited construction and refining its result through the leaf's own constructor when the mathematics lands there.

The same goal applies to functorial constructions.
A full replete subcategory receives the inherited categorical interface automatically.
Limits, colimits, and similar constructions descend to a subcategory when its leaf overrides the inherited construction and refines the result through the leaf's own constructor.
The leaf author supplies only that override, closure, or lift, which is the mathematics specific to the new structure.

## Core model

`Cat`, the category of categories, is defined here and read as mathematics; the kernel implements it.
Every category in this repository is an object of `Cat`. The public `Category` implementation is `Cat().ObjectType`.

### Declared structure of `Cat`

`Cat` is an abstract, package-owned universe in which all represented categories live.
Its foundation is intentionally unspecified.
The repository declares the categories, functors, natural transformations, universal constructions, and laws that it needs.
Those declarations are the complete usable structure of `Cat`.

A declaration of particular categorical operations does not select a realization of `Cat`. In particular, it does not make `Cat` a category of simplicial sets or Kan complexes, and it supplies no unstated horn-filling or higher-categorical properties.

The finite shape constructors use their standard categorical names.
They include the ordinal categories `[n]`, the walking span, the walking cospan,
the walking parallel pair, and the walking isomorphism.

Each category `C` owns the implementation types relevant to its theory:

- `C.ObjectType` for objects;

- `C.ElementType` for elements, when the category uses elements;

- `C.MorphismType` for morphisms;

- `C(...)` for category-owned construction.

`C(...)` dispatches from semantic input to the exact private constructor route.
This follows Sage's [`Parent.__call__()` constructor model](https://doc.sagemath.org/html/en/reference/structure/sage/structure/parent.html).

For `A, B in C`, the one owned hom category is `Mor(C)(A, B)`: the full subcategory of `Mor(C)` on the morphisms `A -> B`. `Mor(C)(A, B)(data)` constructs a morphism `A -> B`; `C(data)` constructs an object of `C`.

`Mor(C)` has the morphisms of `C` as objects and the 2-morphisms of `C` as morphisms; for a 1-category it is discrete.
The category whose objects are morphisms and whose morphisms are commuting squares is `Fun([1], C)`, the functor category from the walking arrow, with evaluation functors `ev_0, ev_1: Fun([1], C) -> C`. For `C = Cat()`, the morphisms of `Fun(C, D)` are natural transformations.

Define `Fun = Mor(Cat())`. The endpoint hom category `Fun(C, D) = Mor(Cat())(C, D)` owns construction of functors from `C` to `D`. The endpoints select the category, not a particular functor.

```python
Fun(C, D)(on_object, on_morphism)
Fun(S, T).Monomorphisms().Isofibrations().Full()()
Fun(C, C).Equivalences().identity()
```

A category construction creates its named functors there and retains them.
Product and pullback presentations retain each projection separately.
A leaf selects the functors that supply inherited operations.

The selected property category records the theorem known by the leaf writer.
The constructor does not compute that property.
The kernel never selects a component by inspecting fields or tuple positions.

The same construction system applies to `Cat()` itself:

```python
P = Cat().Products()((C_0, ..., C_n))
Q = Cat().Coproducts()((C_0, ..., C_n))
P.product_projection(i)   # P -> C_i
Q.coproduct_injection(i)  # C_i -> Q
```

If `S` is a subcategory of `P`, then its monomorphism is an object of `Cat().MonoOver(P)`. Its `product_projection(i)` is that monomorphism followed by the corresponding projection of `P`.

`C.SliceOver(x)` is the pullback in `Cat()` of `ev_1: Fun([1], C) -> C` along `x: 1 -> C`; `C.CosliceUnder(x)` is the pullback of `ev_0`. Each retains its pullback projections; the varying object is the composite with `ev_0` or `ev_1`.

For `X, Y in C`, the inherited categorical defaults are:

```python
Y ** X  # exponential object, where C is declared cartesian closed
X * Y   # product
X + Y   # coproduct
X @ Y   # biproduct
```

The category foundation defines these defaults and retains their universal data.
A category-owned implementation can override a default when standard notation names a different algebraic operation on its objects.
The explicit categorical constructions remain available through `C.Products()`, `C.Coproducts()`, and the other named construction families.

A functor `F: C -> D` is a morphism in `Cat` and an object of `Fun = Mor(Cat())`. It inherits its domain, codomain, object map, and morphism map from `Cat().MorphismType`. For fixed endpoints, `Fun(C, D)` is `Mor(Cat())(C, D)`. Its morphisms are natural transformations.

Functor properties use property subcategories of `Mor(Cat())`:

```python
Mor(Cat()).Full()
Mor(Cat()).Faithful()
Mor(Cat()).FullyFaithful()
```

Their `is_full()`, `is_faithful()`, and `is_fully_faithful()` methods return applied predicates.
Direct property construction and assumptions refine the same owned functor.
These predicates have no computational routes.

Every functor is an explicit mathematical object.
Only structure functors contribute methods to the public surface.
A structure functor is an ordinary functor used as compiler input, not another kind of
morphism in `Cat`.

For an object `x` in `C`, the named functor constructs and caches `F(x)` in `D`.
When `F` is a structure functor, the kernel also exposes methods declared by
`D.ObjectType` directly on `x`. The same distinction applies to elements and morphisms.
The source value remains an object of `C`; dynamic Python inheritance is the mechanism
that supplies the method surface.

The method compiler records the category that declares each method.
Local declarations take precedence.
Sage's dynamic-class construction and controlled linearization include a shared ancestor
class once and initialize it once. Unrelated name collisions still fail during compilation.

This gives one public mathematical object instead of a chain of user-visible wrappers.
The functor images remain available for inspection when their exact mathematical type matters.

## Foundation first

The implementation order follows the mathematical dependency order.

The first layer is `Cat`, the category of categories.
Its `ObjectType` implements every category, and its `MorphismType` implements every functor.
The kernel constructs `Mor(C)` for all `C`, including `Fun = Mor(Cat())`. It also constructs functor categories, natural transformations, natural isomorphisms, and sequence products and coproducts from the same category and morphism mechanisms.

The next layer is the complete `Mor(n, C)` tower.
This family includes:

- `Mor(C)` and the commuting-square category `Fun([1], C)`;

- fixed-endpoint categories `Mor(C)(A, B)` and endomorphism categories;

- monomorphism, epimorphism, isomorphism, and automorphism categories;

- `Groupoids()` and the core functor `Core: Cat() -> Groupoids()`;

- slices, coslices, subobjects, superobjects, covering objects, and covered objects.

Subobjects of product categories receive component functors by composition.
Slices and coslices are pullbacks of the evaluation functors `ev_1` and `ev_0` of `Fun([1], C)` and retain their pullback projections.

These constructions must use the same `ObjectType`, `ElementType`, and `MorphismType` inheritance mechanism.

`Groupoids()` is a declared object of `Cat`; this foundation requires no further groupoid
implementation. For `C in Cat()`, `C.Core()` is `Core.on_object(C)`. It keeps the objects
of `C` and only its isomorphisms. The inclusion `U(C.Core()) -> C` is a component of the
natural inclusion from `U * Core` to the identity functor on `Cat()`.

Category relations belong to named structure functors. Use the standard properties
`Faithful`, `Full`, `FullyFaithful`, and `EssentiallySurjective` on `Fun(C, D)`.
Do not reintroduce `WideSubcategory` without a later user decision that requires it.

The next layer is an owned category `Sets()`. It must replace Sage's Sets category for this project.
Its design includes:

- arbitrary sets and arbitrary functions between them;

- exact, symbolic, infinite, and unknown cardinalities;

- function sets and exponentials;

- predicate-defined subsets with their monomorphisms;

- products, coproducts, limits, and colimits of arbitrary small diagrams;

- inherited methods on the objects produced by these constructions.

A function in `Sets()` needs only a domain, a codomain, and a rule.
It does not need linearity, continuity, or a finite table.
The framework must therefore represent maps such as

\[
\mathbb{Q} \to \mathbb{N}, \qquad
\mathbb{Q} \to \mathbb{Z}, \qquad
\mathbb{R} \to \mathbb{R}^{2}.
\]

Here \(\mathbb{N}\) excludes zero.
The map rule can use any valid mathematical definition.

For an owned predicate \(P\) on `B`, applying `P` to `x` constructs a proposition.
The subset

\[
A = \{x \in B \mid P(x)\}
\]

is an object of `Sets()` together with a monomorphism \(A \hookrightarrow B\). Examples include the even integers and the prime integers as subobjects of \(\mathbb{Z}\). `ask(P(x))` returns `True`, `False`, or Sage's `Unknown`. Python containment converts that decision to a Boolean admission result.

Finite products are only one specimen of the general product construction.
The final interface must accept arbitrary small diagrams.
The same requirement applies to coproducts, limits, colimits, and function sets.

## Universal constructions

Universal constructions are categorical data, not container factories.
A product retains its `product_projection(i)` morphisms and its mediating morphism.
A coproduct retains its `coproduct_injection(i)` morphisms and its mediating morphism.
Limits and colimits retain the diagrams, cones, cocones, and universal maps that define them.

These constructions act on objects and morphisms through functors.
Their results then receive methods from the categories in which they live.
A product of sets is therefore still a set and receives set operations through its retained monomorphism into `Sets()`.

This design removes the need for a separate method-propagation registry.
Functor composition already records how structure moves.
Natural transformations record comparisons between such constructions.

## Sage as a computation engine

Sage remains valuable for arithmetic, symbolic computation, and mature algorithms.
A modeled mathematical realization is an explicit functor.

A category-owned method can also use a private Sage value directly inside its computation boundary.
It reconstructs the owned mathematical result before returning.
A private computation representation supplies no public methods.

This boundary keeps mathematical ownership in this framework.
It also permits one owned implementation to use several private computation engines.

## Design standard

The kernel can be intricate when that complexity removes repetition from theory code.
The theory layer must read like mathematics:

- categories own operations at their natural level;

- functors state every change of structure;

- constructions preserve their defining morphisms;

- inherited methods follow declared functors;

- implementations do not impose unjustified finiteness or countability assumptions.

The framework succeeds when a new category states only its mathematical contribution.
The existing category and functor structure should supply the rest.
