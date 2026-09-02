# System architecture

This specification owns the shape of the complete `sage-categories` system.
It implements D124 through D127.

Detailed mathematical definitions remain in their topic specifications.
This file states how those definitions compose.

## Contents

- [System shape](#system-shape)
- [Mathematical tower](#mathematical-tower)
- [Runtime substrate](#runtime-substrate)
- [Ownership map](#ownership-map)
- [Dependency directions](#dependency-directions)
- [Foundation bootstrap](#foundation-bootstrap)
- [Standard traces](#standard-traces)
- [Agent context](#agent-context)
- [Accretion rule](#accretion-rule)

## System shape

The system has one mathematical tower and one runtime substrate.

```text
decisions
    |
    v
Cat, Mor, Fun, and universal constructions
    |
    v
property categories, propositions, queries, and refinement
    |
    v
sets, cardinals, ordinals, and ordered sets
    |
    v
internal algebraic objects, rings, modules, and algebras
```

The private runtime makes this tower executable.
It is not a mathematical layer in the tower.

## Mathematical tower

| Layer | Content | Canonical owner |
| --- | --- | --- |
| T0 | Decisions and supersession | [decisions.md](decisions.md) |
| T1 | Categories, points, morphisms, functors, and natural transformations | [functor.md](functor.md) |
| T2 | Property categories, public propositions, assumptions, and same-object refinement | [property-refinement.md](property-refinement.md) and [undecidable-properties.md](undecidable-properties.md) |
| T3 | Pullbacks, opposites, images, comma categories, fibers, and universal data | [functor.md](functor.md) |
| T4 | Property intersections and inverse images through retained pullbacks | [property-refinement.md](property-refinement.md) |
| T5 | Sets, elements, maps, and set constructions | [sets.md](sets.md) |
| T6 | Cardinals, ordinals, and ordered sets | [cardinality.md](cardinality.md), [ordinals.md](ordinals.md), and [ordered-sets.md](ordered-sets.md) |
| T7 | Magmas, monoids, groups, semirings, and rings in supplied ambient categories | [magmas-monoids-semirings.md](magmas-monoids-semirings.md) and [rings.md](rings.md) |
| T8 | Modules and algebras in supplied ambient categories | [modules.md](modules.md) and [algebras.md](algebras.md) |

Each layer consumes named objects and functors from lower layers.
It adds only its new mathematical structure.

Predicate and query meanings remain at their mathematical owners.
T2 supplies the shared proposition substrate.
Each typed-query runtime path enters with its first category-owned query.

[Separating families and categorical generators](separating-families-and-categorical-generators.md) owns a cross-layer construction pattern.
Each domain phase instantiates that pattern after its category and `Sets()` exist.

## Runtime substrate

| Responsibility | Runtime owner |
| --- | --- |
| Implementation-class compilation | The private kernel in [resolution.md](resolution.md) |
| Controlled C3, dynamic classes, refinement, and runtime identity | Sage |
| Public predicates, propositions, Boolean algebra, assumptions, and proposition dispatch | SymPy |
| Exact typed-query dispatch | The query owner through private runtime dispatch |
| Finite categorical computation | CAP and the fixed GAP packages in [resolution.md](resolution.md) |
| Finite diagram presentation | Catlab and GATlab |
| Category-specific computation | Private leaf engine helpers under [leaves.md](leaves.md) |

Every runtime path starts with owned mathematical values.
Every public result is an owned value or an authorized public proposition.

## Ownership map

| Concept | Mathematical owner | Runtime representation or implementer |
| --- | --- | --- |
| Category `C` | `Cat()` and `C` | `C.ObjectType` |
| Placement of `C` in structured `D` | the point functor in `{C}.structure_functors()` | Kernel level-shift refinement |
| Point functor of `X` | `Fun(Cat().Point(X), D)` | Ordinary functor value |
| Object of `C` | `C` | `C.ObjectType` |
| Element of an object of `C` | `C` | `C.ElementType` |
| Morphism of `C` | `Mor(C)` | `C.MorphismType` |
| Functor `F: C -> D` | `Fun(C, D)` | `Cat().MorphismType` |
| Natural transformation | `Mor(Fun(C, D))` | `Fun(C, D).MorphismType` |
| Structure functor | Its defining category or retained construction | The compiler selects its target classes |
| Public functor image | The named functor | Its ordinary object or morphism action |
| Inherited execution | The declaring target category | Sage dynamic method resolution |
| Property category `C.P()` | `C.P()` | Sage axiom binding and kernel refinement |
| Mathematical predicate | The category, property, or equality owner | Public SymPy `Predicate` subclass |
| Applied proposition | Its mathematical predicate | SymPy `AppliedPredicate` or Boolean expression |
| Proposition assumptions | The active mathematical session | SymPy `global_assumptions` |
| Proposition evaluation | The predicate and its exact handlers | `sympy.ask()` |
| Undecided proposition | No new mathematical object | Sage `Unknown` |
| Typed query | The category that owns the operation | Repository query application |
| Typed-query result | Its declared result category | Private exact-query dispatch |
| Positive property refinement | The property category | The kernel and Sage |
| Diagram | `Fun(I, C)` | Owned diagram value |
| Universal presentation | Its cone or cocone category | Owned presentation value |
| Restricted Yoneda functor | Its supplied probe family | Owned functor into a set-valued functor category |
| Evaluation epimorphism | Its probe family and target object | Owned coproduct presentation and morphism |
| Finite presentation | Its generator and relation objects | Owned coequalizer presentation |
| Apex | The ambient category `C` | Owned object of `C` |
| Engine representation | No mathematical owner | Private adapter |
| Generated stub | No semantic authority | Derived static projection |
| Work order | Active plan DAG | `agent-memory` |

Mathematical ownership and Python class ownership are different relations.
A category owns the meaning of its predicate.
SymPy owns the public predicate class and proposition algebra.

## Dependency directions

Architecture flows in one direction:

```text
decisions -> specifications -> plans -> theory declarations
            -> private runtime -> owned public results
```

The following source dependencies are valid:

- `Cat` imports no production leaf.
- The kernel imports no production leaf.
- A leaf imports no kernel internal.
- A leaf depends only on its immediate mathematical targets.
- A leaf can call a private engine helper.
- An engine helper does not register categories or refine values.
- An engine helper does not control assumptions.
- A generated projection is never an architecture source.
- Code, tests, reports, and Git history do not define architecture.

A structure functor points from a structured source to an inherited target.
Its ordinary actions accept source values whose own local state is initialized.
Compiler inheritance runs the object action during source construction to initialize the target implementation on the source value (D13).

## Foundation bootstrap

The foundation contains a mathematical cycle:

```text
Semirings(Cat()) -> Cardinal() -> Sets()
                              ^       |
                              |       v
                              +-- cardinality
```

The implementation cuts this cycle without changing its mathematics:

1. Complete `Cat`, `Mor`, `Fun`, properties, and generic constructions.
2. Define minimal `Sets()` without cardinality integration.
3. Define the internal algebraic-object schema with `Cardinal()` as its first consumer.
4. Define `Ordinals()`, `Cardinal()`, and their order categories.
5. Attach cardinality queries and cardinal property categories to `Sets()`.
6. Complete the specified `Sets()` construction surface.
7. Add ordered sets.
8. Add general algebraic families.
9. Add modules and algebras.

The active vault DAG records these stages and their acceptance order.

## Standard traces

### Structural trace

```text
category declaration
-> named structure functor
-> target implementation classes
-> private Sage runtime mirror
-> controlled C3
-> initialized source value
-> direct inherited execution
```

Public functor application is a separate trace:

```text
completed source value
-> F.on_object or F.on_morphism
-> target public constructor
-> separate owned image
```

### Proposition trace

```text
mathematical predicate owner
-> public SymPy Predicate
-> SymPy applied proposition
-> sympy.ask()
-> True, False, or None
-> Sage Unknown for None
-> same-object refinement after an exact positive property result
```

### Universal-construction trace

```text
shape I
-> diagram D in Fun(I, C)
-> cone or cocone category
-> selected universal presentation
-> apex in C
-> retained legs and universal map
```

## Agent context

Load only the contract packet for the assigned work.

| Work | Required contract packet |
| --- | --- |
| Architecture decision | This file, [decisions.md](decisions.md), and the active phase card |
| `Cat`, `Mor`, or `Fun` | This file and the applicable section of [functor.md](functor.md) |
| Private compiler | This file, [resolution.md](resolution.md), and the applicable functor contract |
| Properties and queries | This file, [property-refinement.md](property-refinement.md), and [undecidable-properties.md](undecidable-properties.md) |
| Universal construction | This file and the applicable section of [functor.md](functor.md) |
| Leaf design | This file, [leaves.md](leaves.md), the leaf specification, and its immediate target specifications |
| Engine integration | The leaf specification, the engine boundary in [leaves.md](leaves.md), and the dependency row in [resolution.md](resolution.md) |
| Plan execution | The active plan, current phase, direct prerequisite cards, and governing specification sections |
| Review | The exact phase acceptance, canonical owner sections, and exact revision |

An agent expands this packet only when the target artifact exposes a new owner.
It does not scan unrelated specifications for general confidence.

## Accretion rule

Every new capability attaches to one existing mathematical owner.
It enters the system through a category, functor, property, query, or universal construction.

A new leaf states its local data and immediate functors.
It receives the rest of its interface through the tower.

A completed phase leaves one stronger canonical contract and one accepted artifact.
It adds no parallel status document, inheritance registry, proposition system, or engine interface.

A public runtime mechanism enters with its first real mathematical consumer.
A specification can define its contract earlier.
Acceptance uses objects and functors already owned by the active tower layer.
Each executing phase names that consumer, its exact owner, and its complete functor path.
