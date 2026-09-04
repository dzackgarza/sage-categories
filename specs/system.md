# System architecture

This file owns layer responsibilities, source dependencies, and the foundation bootstrap.
Topic specifications own the mathematics. [AGENTS.md](../AGENTS.md#sources-of-truth) owns document authority and work procedure.

## System shape

The mathematical foundation is `Cat`, its morphisms and functors, and generic constructions.
Properties and queries use that foundation. Production categories build on these through named functors.
The private runtime makes the mathematics executable.

| Layer | Responsibility |
| --- | --- |
| `sage_categories.kernel` | Engineering: class compilation, Sage runtime access, initializer threading, identity retention, and executing placement/refinement |
| `sage_categories.cat` | Mathematics shared by categories: objects, points, morphism semantics, `Mor`, `Fun`, axiom declarations, and universal constructions |
| `sage_categories.cat_kernel` | Joint interpretation requiring both layers: generating property subcategories, their inclusions and `is_p()` methods; reading declared functor properties to select placement and inheritance |
| Production leaf | Its new objects, data, immediate named functors, and category-specific operations |
| Private engine helper | Lowering owned input, computing in an external engine, and reconstructing an owned result |

Mathematical ownership and implementation-class ownership are distinct.
The mathematical category owns the meaning of a predicate; SymPy supplies its public expression machinery.
The kernel executes class refinement; the property category owns what that refinement means.

## Ownership map

| Contract | Canonical specification |
| --- | --- |
| `Cat`, `Mor`, `Fun`, points, natural transformations, and categorical calculus | [functor.md](functor.md) |
| Selected functors and conditions for inheritance | [functor.md — Structure functors](functor.md#structure-functors-and-inherited-classes) |
| Diagrams, pullbacks, images, opposites, fibers, and universal presentations | [functor.md — Universal constructions](functor.md#diagram-shapes-and-universal-constructions) and its related construction sections |
| Axioms, property containment, intersections, inverse images, and refinement | [property-refinement.md](property-refinement.md) |
| Public predicates, equality, assumptions, typed queries, and `ask()` | [undecidable-properties.md](undecidable-properties.md) |
| Private compiler, controlled C3, caches, and dependency versions | [resolution.md](resolution.md) |
| Leaf declarations, exact types, templates, and engine boundary | [leaves.md](leaves.md) |
| Sets, maps, elements, and set constructions | [sets.md](sets.md) |
| Cardinals, ordinals, and ordered sets | [cardinality.md](cardinality.md), [ordinals.md](ordinals.md), [ordered-sets.md](ordered-sets.md) |
| Internal magmas, monoids, groups, semirings, and rings | [magmas-monoids-semirings.md](magmas-monoids-semirings.md), [rings.md](rings.md) |
| Modules and algebras in supplied ambient categories | [modules.md](modules.md), [algebras.md](algebras.md) |
| Restricted Yoneda, evaluation epimorphisms, generators, and presentations | [separating-families-and-categorical-generators.md](separating-families-and-categorical-generators.md) |
| Generated static projection | [functor.md — Static semantic projection](functor.md#static-semantic-projection) |

## Dependency directions

- The kernel imports neither `Cat`, `cat_kernel`, nor a production leaf.
- `Cat` imports neither `cat_kernel` nor a production leaf.
- `cat_kernel` imports the kernel and `Cat`. A leaf imports neither kernel internals nor `cat_kernel`.
- A leaf reaches `Cat`, its immediate mathematical targets, and its private engine helpers.
- Only `kernel/sage_runtime.py` and the engine modules named in the import contract import Sage.
- Engine helpers neither register categories nor control placement, refinement, or assumptions.
- Generated projections derive from mathematical declarations and compiler interpretation.

`cat_kernel` supplies callback references through package bootstrap; the kernel holds those references and executes its engineering operations.
[resolution.md](resolution.md#the-closed-kernel-surface) specifies initialization order and the closed runtime surface.

Sage supplies controlled C3, dynamic classes, refinement, and identity facilities.
SymPy supplies proposition algebra, assumptions, and proposition dispatch.
Typed queries use private exact dispatch. CAP, GAP packages, Catlab, and GATlab serve their declared finite computation domains.
The exact dependency scope is recorded once in [resolution.md](resolution.md#fixed-private-dependencies).
Every public computation returns an owned value or the authorized public SymPy expression containing private identity atoms.

## Foundation bootstrap

`Semirings(Cat())`, `Cardinal()`, and `Sets()` have a dependency cycle when cardinality is included in the first set implementation.
The implementation cuts it in this order:

1. Complete `Cat`, `Mor`, `Fun`, properties, and generic constructions.
2. Define minimal `Sets()` without cardinality integration.
3. Define the internal algebraic-object schema with `Cardinal()` as its first consumer.
4. Define `Ordinals()`, `Cardinal()`, and their order categories.
5. Attach cardinality queries and cardinal property categories to `Sets()`.
6. Complete the specified set construction surface.
7. Add ordered sets, then general algebraic families, modules, and algebras.

The vault DAG holds work boundaries and current acceptance.
Generic pullbacks needed by property intersections and inverse images enter with those first consumers.
Later universal-construction work extends that same calculus.
A domain's separating-family constructions enter after the domain category and `Sets()` exist.

## Accretion rule

Each capability belongs to an existing category, functor, property, query, or universal construction.
A leaf supplies local data and immediate functors, then receives the remaining interface through those functors.
A runtime mechanism enters with its first complete mathematical consumer.
Its specification can precede implementation; its acceptance cannot precede a working consumer.

The active phase names that consumer and the full constructor and functor path.
Procedure and status remain with [AGENTS.md](../AGENTS.md) and the vault cards.
