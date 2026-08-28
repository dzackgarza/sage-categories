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

The separation also preserves mathematical consequences that concrete Sage implementations can lose.
For example, an integral-lattice presentation has a product projection to finite-rank `ZZ`-modules.
The resulting structural path to `Sets()` determines cardinality and supports lazy enumeration.
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
A leaf-category contributor should mainly state new objects, morphisms, functors, axioms, and construction rules.
The inherited categorical machinery should supply the rest.

The intended reviewer of a theory subtree is a mathematician with little programming experience.
They should be able to compare a method with its definition without auditing dynamic inheritance, container plumbing, backend types, or dispatch machinery.
Legibility and categorical uniformity are therefore primary requirements, not decoration around successful computation.

## Leaf-category end state

Once the kernel is established, a researcher adding a leaf category should not need to understand its implementation.
They should begin from a shipped category template, declare the new mathematical structure, connect it to nearby familiar categories through declared functors, and implement only the new methods.
They should need to read only the mathematically relevant neighboring subtrees and their functor contracts.

The compiler then supplies the complete inherited object, element, morphism, and construction interfaces.
Let \((\mathcal M,\odot,1)\) be monoidal, let \(\mathcal C\) be an \(\mathcal M\)-actegory, and let \(A\) be a monoid object of \(\mathcal M\). An object of [`Modules(A, C)`](specs/modules.md) is an object \(X\) of \(\mathcal C\) with an action \(A\mathbin{\bullet}X\to X\). The category retains the ambient monoidal category, the actegory, the acting monoid, and the action.

When closed or enriched structure represents these actions by an internal endomorphism monoid, the same module structure is equivalently a monoid morphism \(A\to\operatorname{End}_{\mathcal C}(X)\). The action morphism is the general definition.

[`Algebras(R, C)`](specs/algebras.md) is the base-relative presentation of the monoid objects in the supplied monoidal category `Modules(R, C)`. Its selected route through the general monoid, magma, and module categories supplies the applicable operations.
A general module or algebra object reaches `Sets()` only through an explicit declared functor from its ambient category.
Cardinality and other distant capabilities arrive through functor composition rather than leaf-specific code.

For example, a researcher can add `FiniteSubsetsOfNN()` after the complete theory of sets exists.
They declare its constructors, its monomorphism into `Sets()`, and only its new methods, such as `minimal_element()` or `gcd_of_elements()`. The kernel constructs `FiniteSubsetsOfNN.ElementType` and supplies the full `Sets.ElementType` interface without a leaf-specific element class.
The inherited set interface also makes products, coproducts, filtered limits, and other set constructions available without new implementations in the leaf.
Each result remains an object of the category that owns the construction.
The leaf returns it to `FiniteSubsetsOfNN()` by overriding the inherited construction and refining its result through the leaf's own constructor when the mathematics lands there.

The same goal applies to functorial constructions.
A full replete subcategory receives the inherited categorical interface automatically.
Limits, colimits, and similar constructions descend to a subcategory when its leaf overrides the inherited construction and refines the result through the leaf's own constructor.
The leaf author supplies only that override, closure, or lift, which is the mathematics specific to the new structure.

## Core model

The kernel owns `Cat`, the category of categories.
Every category in this repository is an object of `Cat`. The public `Category` implementation is `Cat().ObjectType`.

### Declared structure of `Cat`

`Cat` is an abstract, package-owned universe in which all represented categories live.
Its foundation is intentionally unspecified.
The repository declares the categories, functors, natural transformations, universal constructions, and laws that it needs.
Those declarations are the complete usable structure of `Cat`.

A declaration of particular categorical operations does not select a realization of `Cat`. In particular, it does not make `Cat` a category of simplicial sets or Kan complexes, and it supplies no unstated horn-filling or higher-categorical properties.

A borrowed mathematical name imports no surrounding theory.
Names such as `Simplex`, `Boundary`, `Horn`, and `strict` denote only the constructions and laws stated here and in the governing specifications.
For example, `Cat().Horn(n, k)` is the declared free category on its horn graph.
Its name supplies no additional simplicial-set structure.

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

If `S` is a subcategory of `P`, then `S` is an object of `Cat().Products().ChosenSubobjects()`. Its `product_projection(i)` is the subcategory monomorphism followed by the corresponding projection of `P`.

`C.SliceOver(x)` is the pullback in `Cat()` of `ev_1: Fun([1], C) -> C` along `x: 1 -> C`; `C.CosliceUnder(x)` is the pullback of `ev_0`. Each retains its pullback projections; the varying object is the composite with `ev_0` or `ev_1`.

For `X, Y in C`, the categorical operators are:

```python
Y ** X  # exponential object, where C is declared cartesian closed
X * Y   # product
X + Y   # coproduct
X @ Y   # biproduct
```

The category foundation defines these operations once and retains their universal data.

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
Only declared functors contribute methods to the public surface.
The selection is compiler input over an already established mathematical functor.
It is not an additional kind of functor.

For an object `x` in `C`, the kernel constructs and caches `F(x)` in `D`. It then exposes methods declared by `D.ObjectType` directly on `x`. The same process applies to elements and morphisms.

The method compiler records the category that declares each method.
Local declarations take precedence.
Two routes to the same declaration share one implementation.
Incoherent routes and unrelated name collisions fail during compilation.

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

- cores and wide subcategories;

- slices, coslices, subobjects, superobjects, covering objects, and covered objects.

Subobjects of product categories receive component functors by composition.
Slices and coslices are pullbacks of the evaluation functors `ev_1` and `ev_0` of `Fun([1], C)` and retain their pullback projections.

These constructions must use the same `ObjectType`, `ElementType`, and `MorphismType` inheritance mechanism.

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
A product of sets is therefore still a set and receives set operations through the same structural route.

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
