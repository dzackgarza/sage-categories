# sage-categories

`sage-categories` is a categorical replacement universe for a significant subset of standard Sage mathematics.
It shadows familiar Sage objects with package-owned versions whose categories own their objects, arrows, constructors, and methods.

The central rule is simple:

> A category owns implementations and constructors.
> A functor constructs an implementation in another category.

This rule replaces accidental inheritance with explicit mathematics.
It also lets one public object receive operations from every category reached by the selected functors.

The public API is not stable.
The repository currently contains the categorical kernel and a finite Sets specimen.
The complete Sets design described below remains the current implementation target.

## One import, one mathematical universe

The required opt-in surface is a `sage_categories.all` module analogous to `sage.all`:

```python
from sage_categories.all import *
```

Python module names cannot contain hyphens, so the import uses `sage_categories`, not the distribution name `sage-categories`. The `all` module is part of the target public API and is not yet present in the current implementation.

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

Sage has powerful mathematical implementations.
Its category framework also binds mathematical structure to dynamic Python inheritance and implementation-specific parent classes.
These mechanisms can obscure three different facts:

- which category owns an operation;

- which functor transports an object or arrow;

- which implementation performs a computation.

This project separates those facts.
Theory code should state the mathematical definition and the immediate functors that connect it to existing theory.
The kernel should compile that information into a direct method surface.

The separation also preserves mathematical consequences that concrete Sage implementations can lose.
For example, an integral lattice has an underlying finite-rank `ZZ`-module, hence an underlying set modeled by a finite product of copies of `ZZ`. That functor chain determines cardinality and supports lazy enumeration.
A concrete lattice implementation that does not retain those categorical relationships can fail to expose either operation.
Long-running searches, including bounded enumeration in Vinberg-type algorithms, need those consequences without bespoke lattice-level implementations.

A leaf category should define only its new structure.
It should not copy methods from every category above it.
For example, a finite mathematical object should receive `cardinality()` from its implementation in `Sets()`. The same rule must work through long chains of functors.

## Core model

Each category `C` owns the implementation types relevant to its theory:

- `C.ObjectType` for objects;

- `C.ElementType` for elements, when the category uses elements;

- `C.ArrowType` for arrows;

- `C(...)` for category-owned construction.

A functor `F: C -> D` owns its domain, codomain, object map, and arrow map.
It can also own an element map when that notion is part of the theory.

Every functor is an explicit mathematical object.
Only selected structural functors contribute methods to the public surface.
This distinction prevents an implementation engine from changing the mathematical API.

For an object `x` in `C`, the kernel constructs and caches `F(x)` in `D`. It then exposes methods declared by `D.ObjectType` directly on `x`. The same process applies to elements and arrows.

The method compiler records the category that declares each method.
Local declarations take precedence.
Two routes to the same declaration share one implementation.
Incoherent routes and unrelated name collisions fail during compilation.

This gives one public mathematical object instead of a chain of user-visible wrappers.
The functor images remain available for inspection when their mathematical role matters.

## Foundation first

The implementation order follows the mathematical dependency order.

The first layer is `Cat`, the category of categories.
It includes functor categories, natural transformations, and natural isomorphisms.

The next layer is the complete family of arrow categories.
This family includes:

- arrow categories and commuting squares;

- hom categories and endomorphism categories;

- monomorphism, epimorphism, isomorphism, and automorphism categories;

- cores and wide subcategories;

- slices, coslices, subobjects, superobjects, covering objects, and covered objects.

These constructions must use the same `ObjectType`, `ElementType`, and `ArrowType` inheritance mechanism.

The next layer is an owned category `Sets()`. It must replace Sage's Sets category for this project.
Its design includes:

- arbitrary sets and arbitrary functions between them;

- exact, symbolic, infinite, and unknown cardinalities;

- function sets and exponentials;

- predicate-defined subsets with inclusion arrows;

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

For a predicate \(P: B \to \{\mathop{\rm True},\mathop{\rm False},\mathop{\rm Unknown}\}\), the subset

\[
A = \{x \in B \mid P(x)\}
\]

is an object of `Sets()` together with an inclusion arrow \(A \hookrightarrow B\). Examples include the even integers and the prime integers as subobjects of \(\mathbb{Z}\). Membership can return `bool | Unknown`; an unavailable answer is not a false answer.

Finite products are only one specimen of the general product construction.
The final interface must accept arbitrary small diagrams.
The same requirement applies to coproducts, limits, colimits, and function sets.

## Universal constructions

Universal constructions are categorical data, not container factories.
A product retains its projections and its mediating arrow.
A coproduct retains its injections and its mediating arrow.
Limits and colimits retain the diagrams, cones, cocones, and universal maps that define them.

These constructions act on objects and arrows through functors.
Their results then receive methods from the categories in which they live.
A product of sets is therefore still a set and receives set operations through the same structural route.

This design removes the need for a separate method-propagation registry.
Functor composition already records how structure moves.
Natural transformations record comparisons between such constructions.

## Sage as a computation engine

Sage remains valuable for arithmetic, symbolic computation, and mature algorithms.
This project places each Sage implementation behind an explicit realization functor.

A realization can construct a Sage value and use it to compute a result.
It is not a structural functor.
Its Python methods therefore do not enter the public mathematical API by accident.

This boundary keeps mathematical ownership in this framework.
It also permits several computation engines to realize the same mathematical object.

## Design standard

The kernel can be intricate when that complexity removes repetition from theory code.
The theory layer must read like mathematics:

- categories own operations at their natural level;

- functors state every change of structure;

- constructions preserve their defining arrows;

- inherited methods follow structural functors;

- implementations do not impose unjustified finiteness or countability assumptions.

The framework succeeds when a new category states only its mathematical contribution.
The existing category and functor structure should supply the rest.
