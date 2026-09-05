# Minimal leaf scaffolding

A leaf scaffold is an executable mathematical category with a small public consumer.
Its purpose is to expose whether the category definition, inherited structure, and computation boundary are suitable for further API work.
The project vault's `PLAN-foundation-production-tower` owns the delivery graph and individual leaf plans.
Topic specifications retain the broader mathematical contracts.

## Common consumer boundary

Every scaffold supplies its object constructor, owned elements where applicable, fixed-endpoint morphisms, identities, and composition.
It exposes each immediate structure functor with both actions.
One nonidentity morphism must change observable data through the named functor.
The example reads an inherited operation on the completed public object and checks its result and parent.

For a property category, the example includes a lawful object and a mathematical counterexample to the property.
An undecided proposition remains undecided.
For a universal construction, a competing cone, cocone, or balanced map determines an executable mediator.
The defining equations and uniqueness statement belong to that construction's mathematical owner.

The audit reads the complete leaf and the immediate owners used by its example.
It asks whether the remaining leaf code consists of defining data, structure maps, laws, and local evaluation.
Imports alone cannot answer this question: a helper that assembles classes or copies inherited state still performs runtime work.
The kernel owns that work; Cat owns generic categorical mathematics.
The source-level audit therefore follows the constructor, selected functors, inherited operation, and public result.
Source length is supporting information, not an acceptance criterion.

Each scaffold has an exact public type example for its constructor, morphism endpoints, and inherited result.
Generated declarations must express those same domains.
The static-projection plan owns general compiler and projector repairs exposed by that example.

## Mathematical minimum

| Category | Required defining structure | Small distinguishing consumer |
| --- | --- | --- |
| Sets | Owned sets, points, total maps, finite constructions, and a represented infinite set | A noninjective map, a product mediator, and an infinite-set map without enumeration |
| Posets | A relation subobject, partial-order laws, and monotone maps | The product of two two-element chains with crossed incomparable elements |
| Totally ordered sets | Totality on a poset, inherited comparison, and monotone maps | A chain and a two-element antichain, with finite placement through the set projection |
| Magmas | A multiplication morphism for a supplied tensor and its preserving maps | An asymmetric multiplication and a nonidentity homomorphism |
| Monoids | Multiplication, unit, associativity, and both unit diagrams | A unit-preserving map and a monoid in a noncartesian tensor category |
| Semirings | Compatible additive and multiplicative monoids, distributivity, and absorption | Distinct addition and multiplication with both routes to one carrier |
| Rings | A semiring and compatible additive inversion | A unital quotient map and a noncommutative ring |
| Modules | A monoid acting through a supplied actegory | A nonidentity linear map, a transported action, and two different scalar actions |
| Bimodules | Commuting left and right actions with their scalar objects retained | A balanced tensor product over a noncommutative middle ring |
| Algebras | A monoid in a supplied monoidal module or bimodule category | Multiplication in the exact module hom category and a scalar-preserving morphism |
| Schemes | A locally ringed space with an affine open cover | An affine spectrum, a contravariant ring-map image, and a scheme glued from two charts |

Only the operations needed to construct and examine these consumers enter the scaffold.
Further algorithms remain with their topic specifications until separate API work is assigned.

## Reuse from Cat

[The universal calculus](functor.md#universal-calculus) supplies comma categories, inserters, equifiers, universal arrows, adjunctions, and ordinary and weighted limits.
Leaves retain the projections and presentations produced there.
Algebraic leaves supply the structure maps and law diagrams.
Order leaves supply relation predicates and chosen order structures on inherited set limits.
Relative tensor products supply balancing data to the colimit construction.
Geometric leaves supply topology, sheaves, local rings, and affine charts to the appropriate categorical constructions.

The noncartesian monoidal and actegory structure required by modules is a prerequisite owned by Cat.
The current cartesian `Monoids(C)` construction does not by itself supply that structure.
Abelian groups and their tensor product provide the ordinary ring/module instance without defining abelian groups through modules over the integers.

## Public names and implementation boundary

The exported `FiniteSets` is an executable finite consumer.
The declared `Sets`, `Posets`, and `TotallyOrderedSets` are the identities their production implementations must claim.
The finite-set implementation must be integrated with the finite property of the implemented set category.

The following distinctions must remain explicit when the scaffold APIs are implemented:

| Current construction | Scaffold contract |
| --- | --- |
| `cat.relations.Relations(C)` | Relations as arrows between objects of a regular category; retained public name `Relations(C)` |
| `Relations()` in the order specifications | Sets equipped with one endorelation; published by the leaf as `BinaryRelations()` |
| `cat.structured_objects.Algebras(T)` | Endofunctor algebras; the planned unambiguous public spelling is `EndofunctorAlgebras(T)` |
| `Algebras(R, C)` in the algebra specification | Base-relative monoid objects in the selected module category |
| `Magmas(tensor)` and cartesian `Monoids(C)` | Current cases of the supplied tensor/monoidal-structure contracts `Magmas(V)` and `Monoids(V)` |

This table records the implementation transition required by the leaf plans.
It does not claim the planned entrypoints already execute.
The categories' mathematical meanings stay distinct through the public import surface and generated signatures.

## Audit result

A scaffold is ready for API expansion when its public consumer exhibits the stated mathematics and its local source contains only the leaf's responsibility.
If the consumer needs generic class assembly, state transport, property construction, or universal-map implementation in the leaf, repair the corresponding shared owner first.
An audit records the exact remaining mathematical or runtime responsibility and its caller.
It does not replace that responsibility with a leaf-specific workaround.
