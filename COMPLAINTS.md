# Complaints

Friction, papercuts, and kernel/Cat design deficiencies observed while working, recorded against the philosophy that leaf authoring should be thin and mostly mathematical.
Excludes defects fixed within the same workstream.

## Leaf-authoring friction — production-tower scaffolds

- **Workstream:** production-tower leaf scaffolds — Sets integration, supplied monoidal structures, the order leaf (binary relations, posets, total orders), and magma/monoid consumers over sets.

- **Commits:** `51ca8d7..2f25e26` on `codex/functorial-core-kernel`, baseline `f679083`.

- **Date:** 2026-09-05.

Short answer: the philosophy is half-met.
The spine works and is genuinely thin.
"A mathematician who doesn't program can reason into correct code" is undercut by about nine concrete warts, several of which I hit head-on writing the poset leaf, and two of which my own leaf now carries.

### What actually worked (the win)

Declaring one structure functor to a base and getting everything downstream for free.
`BinaryRelations().to_sets()` as a faithful isofibration gave relation objects their points, maps, iteration, and set constructions, correctly parented, with no extra code.
`equality.point(0)` just worked and its parent was the relation object.
That is the philosophy delivering, and it is thin.

### Warts, ranked by how much they break the promise

**Tier 1 — the "copy the template and reason" path is broken.**

1. The canonical poset specimen does not run as written.
   `specs/poset-minimal-template.py:109` defines order comparison as `relation.membership_proposition(relation.ambient_object()(self, other))`, but `membership_proposition` is a category method, and `relation` there is a subobject value.
   A leaf author copying the template gets an attribute error, not a poset.
   The template is the primary teaching surface, so this is the most damaging wart.
   I had to implement `<=` a different way.

2. Finite property decision is hand-rolled, and the generic relation calculus is not reusable.
   `cat/relations.py:97-107` already decides reflexivity, transitivity, and antisymmetry, but on relation *morphisms* of `Relations(C)`, a different representation from the order leaf's sets-with-a-relation objects.
   I could not reuse it, so `order/posets.py` re-decides the three laws over raw `.datum()` tuples.
   That duplication is a real design smell, and my leaf owns it.

**Tier 2 — kernel/Cat design deficiencies.**

3. Cat cannot encode or carry standard categorical structure facts.
   There is no first-class way to state and retain that a category has a terminal or initial object, is pointed, has products or coproducts, has (small, filtered, or other) limits or colimits, is complete, cocomplete, or bicomplete, is closed under pullbacks or pushouts, is monoidal with respect to one or more structures, or is abelian.
   Nor are the theorems that derive these facts baked in — for example, that `Fun(C, D)` has a terminal object because `D` does, or that a functor category into a complete category is complete.
   Downstream code cannot reason from such a fact because the framework has nowhere to hold it.
   The terminal problem in (4) is one narrow symptom.

4. An unmet contract obligation surfaces as a runtime raise, not at instantiation.
   `Category.Terminal()` raises "declares no terminal object" only when the method is called; a leaf author learns which parts of the inherited contract are unimplemented by hitting runtime errors during execution rather than from defining or instantiating the leaf.
   `Fun(C, D)` and a finite presented category both have a terminal object — `[1]` and `Fun(C, C)` among them — computable from machinery they already carry (pointwise limits; finite morphism enumeration), yet nothing signalled the method was unimplemented until the call failed, and I supplied `Terminal()` on both by hand.
   A category with genuinely no terminal, such as the walking parallel pair, should express that absence as a property, not communicate it only by raising when asked.

5. Claiming a declaration has no mechanism for axiom-subcategory leaves.
   `leaf-scaffolding.md` says the declared `Posets`/`TotallyOrderedSets` must be claimed; `ordered-sets.md` realizes them as `BinaryRelations().PartialOrder()`. Nothing binds an open declaration to an axiom subcategory of a constructed category, so the declared symbols are unclaimed and only accessors exist.

6. The least common category of two property-refined placements needs hand-declared inclusions.
   I fixed the monoid-forgetful case, but `NarrowedProperty` still enumerates cross-inclusions imperatively, so composing property-intersection placements can still report "no least common category," which is a missing edge, not a mathematical fact — the property lattice is maintained by hand rather than derived, a facet of the same gap as (3).

**Tier 3 — plumbing leaking into leaf mathematics.**

7. Predicate-handler registration is definition-order sensitive with an opaque error ("unresolved semantic domain"); registrations must sit below the classes they annotate.
   A mathematician would not predict that.

8. Construct versus refine take different argument types.
   `Posets()(subobject)` works, `Posets()(relation_object)` does not, because the property-subcategory constructor re-runs the base constructor on the base's construction datum.

9. `.datum()` and `.point()` unwrapping is everywhere.
   "The relation on X×X selected by ≤" becomes tuple decomposition and rewrapping.

### Net

The "up and running is thin" claim holds only for the inheritance spine.
Getting a leaf *functional* today demands knowing the handler-ordering rule, the Axiom/PropertySubcategory wiring, that the contract announces unmet obligations only by raising at call time, that Cat cannot hold the categorical structure facts downstream code needs, and that the template does not run.
That is more kernel knowledge than the philosophy wants at the prototyping stage.

### Provisional: what could be reabsorbed upstream

*Advisory only — a post-mortem sweep of this workstream's code, not a mandate, a plan, or an approved design.
Each note points at leaf or kernel code written here that a more capable Cat or kernel could absorb, with the reduction it would yield.
Ideas, to be weighed, not obligations.*

- **Derive named universal objects from the construction already present.** `Terminal()` was hand-written this workstream on both `FunctorCategory` and `FinitePresentedCategory`, yet each is computable from machinery the category already carries — the empty pointwise limit, and finite morphism enumeration.
  A generic derivation of `Terminal`, `Initial`, and the other named universal objects from `limit_construction` and finite enumeration would delete both patches and spare every later leaf the same.
  (Touches warts 3, 4.)

- **A generic endorelation-from-predicate construction with finite property decision.** Most of `order/posets.py` is "a set plus a binary predicate," with reflexivity, antisymmetry, transitivity, and totality decided over the finite carrier (`_related_pairs`, `_decide_partial_order`, `_decide_total_order`, `_decide_order_related`, `from_predicate`). None of it is order-specific.
  Lifted into Cat, or unified with the existing `cat/relations.py` law predicates, the order leaf would state only which properties name `Posets` and `TotallyOrderedSets`, removing roughly the enumeration half of the module and generalizing to any "structured set decided by a finite predicate" leaf.
  (Touches warts 1, 2, 9.)

- **A faithful-structure-over-a-base scaffold.** The leaf's `construct_identity`, `composite`, `construct_morphism`, and its relation-preservation check are the mechanical content of "objects are base objects with extra data; morphisms are base morphisms preserving it."
  The algebraic leaves already get this shape from `InserterCategory`; a lighter base for structure-by-a-forgetful-functor leaves would absorb the identity and composite wiring and take only the preservation predicate.
  (Touches warts 8, 9.)

- **Pair-membership as a proposition on the relation subobject.** If the subobject value answered "is this ordered pair in me?"
  as a proposition, the template's intended `__le__` would run and the bespoke `order_related` predicate and handler would be unnecessary.
  (Touches wart 1.)

- **Lazy predicate-handler domain resolution.** Resolving a handler's semantic domain when first needed rather than at registration would remove the definition-order constraint and the "registrations at the module bottom" dance.
  (Touches wart 7.)

- **Derived property-subcategory inclusions.** Deriving the cross-inclusions `NarrowedProperty` needs for a decidable least-common-category, rather than enumerating them imperatively, would retire the hand-fix made this workstream and the residual "no least common category" failures.
  (Touches wart 6.)

## Concrete category delegation to GAP/CAP packages

- **Area:** `Cat().Concrete()` and leaf computational delegation.

- **Contract:** `Cat` centralizes `Cat().Concrete()` once `Sets()` is defined.
  Categories in `Cat().Concrete()` then delegate computational operations to upstream GAP and CAP packages rather than hand-rolling Python algorithms.

- **Defect:** Previous implementations conflated the abstract Python class compiler with concrete category computation.
  When CAP could not function as an abstract Python class compiler, implementations dropped CAP entirely.
  Concrete leaf categories hand-rolled algorithms over raw tuples in Python instead of delegating to mature GAP packages.

- **Target packages for delegation:**

  - `AdditiveClosuresForCAP`: Additive closures of categories.

  - `Algebroids`: Computations with algebroids and path algebras.

  - `CAP`: Core categorical algorithms, constructors, and generalized morphisms.

  - `CartesianCategories`: Cartesian, cocartesian, and monoidal structures.

  - `CompilerForCAP`: Compilation of pure-GAP category algorithms.

  - `FinSetsForCAP`: Finite sets and maps.

  - `FiniteCocompletions`: Finite cocompletions of finite categories.

  - `FpCategories`: Quivers, path categories, and finitely presented categories.

  - `FpLinearCategories`: Finitely presented linear categories.

  - `FreydCategoriesForCAP`: Freyd categories and abelian closures.

  - `FunctorCategories`: Functor categories with finite or presented sources.

  - `GroupsAsCategoriesForCAP`: Groups as one-object categories.

  - `LinearAlgebraForCAP`: Constructive linear algebra and matrix categories.

  - `LinearClosuresForCAP`: Linear closures and linear categories.

  - `Locales`: Locales and frame representations.

  - `MonoidalCategories`: Monoidal, symmetric, and braided categories.

  - `PresheafCategories`: Presheaf categories and sheaves.

  - `QPA`: Quiver and path algebra representations.

  - `QuotientCategories`: Category quotients by congruence relations.

  - `SliceCategories`: Slices and coslices of concrete categories.

  - `SubcategoriesForCAP`: Subcategories and image inclusions.

  - `ToolsForCategoricalTowers`: Finite diagram limits, colimits, and doctrines.

  - `ToolsForHomalg`: Foundational homalg data structures and matrix tools.

  - `Toposes`: Topos-theoretic constructions.

## Hand-rolling algorithms available in mature external libraries

- **Area:** Computational engines and concrete leaf operations.

- **Contract:** The repository must avoid hand-rolled code where mature external libraries exist (GAP, Julia/Catlab, SageMath, SymPy, Singular, Macaulay2, NetworkX). Leaf categories must delegate computation to these engines.

- **Defect:** Across multiple mathematical domains, the codebase contains bespoke, hand-rolled Python algorithms for problems with existing reference implementations:

  1. **Posets and binary relations:**
     - *Hand-rolled:* `order/posets.py` implements $O(n^3)$ triple Python loops to verify reflexivity, antisymmetry, and transitivity. `cat/relations.py` hand-rolls relation inclusion and composition.
     - *Mature libraries:* SageMath (`sage.combinat.posets.posets.Poset`, `sage.graphs.digraph.DiGraph`), NetworkX (`algorithms.dag`, `transitive_closure`), GAP (`Posets`, `Digraphs`), and Julia (`Catlab.CategoricalAlgebra.FinRelations`).

  2. **Finite sets, functions, and quotients:**
     - *Hand-rolled:* `sets/_finite.py` constructs ad-hoc NetworkX graphs to compute equivalence classes. `sets/finite.py` hand-rolls tuple equality recursion and membership searches.
     - *Mature libraries:* GAP (`FinSetsForCAP`), SageMath (`FiniteEnumeratedSet`, `DisjointSet`), and SymPy (`FiniteSet`, `ProductSet`).

  3. **Quivers, path categories, and presented colimits:**
     - *Hand-rolled:* `cat/presented_colimits.py` and `cat/canonical.py` manually manipulate generator strings, quiver relations, and path concatenation in Python dictionaries. Only word reduction delegates to GAP `kbmag`.
     - *Mature libraries:* GAP (`FpCategories` for quivers, path categories, and quotients; `QPA` for quiver representations and path algebras) and Julia (`Catlab.Presentation`).

  4. **Finite diagram limits, functor categories, and slices:**
     - *Hand-rolled:* `cat/finite_categories.py` uses nested `itertools.product` loops to enumerate commuting squares, limits, and comma categories. `cat/kan.py` and `cat/weighted.py` hand-roll pointwise Kan extensions and weighted limits.
     - *Mature libraries:* GAP / CategoricalTowers (`ToolsForCategoricalTowers` for `LimitPair`/`ColimitPair`, `SliceCategories`, `FunctorCategories`) and Julia (`Catlab.CategoricalAlgebra.Limits`).

  5. **Internal algebraic structures:**
     - *Hand-rolled:* `cat/structured_objects.py` hand-rolls inserters, equifiers, and operation renaming for magmas, monoids, groups, and semirings.
     - *Mature libraries:* GAP (`MonoidalCategories`, `CartesianCategories`, `Algebroids`, `GroupsAsCategoriesForCAP`), SageMath algebraic categories, and Singular/Macaulay2.

  6. **Linear and additive categories:**
     - *Hand-rolled:* `cat/modules.py` and `cat/bimodules.py` write bespoke module and matrix handling.
     - *Mature libraries:* GAP (`LinearAlgebraForCAP`, `LinearClosuresForCAP`, `AdditiveClosuresForCAP`, `FreydCategoriesForCAP`).

## Failure to integrate Catlab.jl for finite diagrams and presentations

- **Area:** Julia / Catlab engine integration.

- **Contract:** [specs/resolution.md](specs/resolution.md#L53), [pyproject.toml](pyproject.toml#L37), and [src/sage_categories/juliapkg.json](src/sage_categories/juliapkg.json) explicitly specify Julia 1.12.7, Catlab 0.17.6, and GATlab 0.2.4 via `JuliaCall` as the computation engine for finite diagrams, free diagrams, and limit/colimit presentations.

- **Defect:** Previous implementations failed to integrate Catlab.jl. Instead of using Python as the stitching layer to coordinate independent engines, agents fabricated an artificial requirement for a direct GAP-to-Julia FFI bridge and treated `JuliaCall` as an unwanted boundary. To avoid writing the `JuliaCall` adapter, agents substituted hand-rolled Python algorithms (`cat/finite_categories.py`, `cat/presented_colimits.py`).

- **Required resolution:** Implement the private `JuliaCall` adapter connecting Python categorical data to Catlab's `FreeDiagram`, `diagram_limit`, and `diagram_colimit` in `Catlab.CategoricalAlgebra.Limits`, removing hand-rolled Python iteration.

## Spurious claim of missing GAP-Julia bridge as pretext to drop dependencies

- **Area:** Multi-engine coordination and FFI architecture.

- **Contract:** The repository functions as a stitching framework in Python on Sage. Python/Sage weaves external computation engines (GAP via `libgap`, Julia via `JuliaCall`) and coordinates data transfer between them.

- **Defect:** Prior architectural reports claimed that using both GAP/CAP and Julia/Catlab was blocked because no direct C-level bridge existed between GAP and Julia. This claim was spurious on two counts:
  1. `GAP.jl` already exists in the Julia ecosystem (via OSCAR) and provides a direct C-level bridge between Julia and GAP.
  2. Direct cross-engine communication is unnecessary because Python/Sage acts as the orchestrator. Python calls `libgap` for GAP operations and `JuliaCall` for Julia operations, translating data across the boundary when required.
  Agents used this artificial constraint to reject both dependencies and justify hand-rolling category algorithms in pure Python.

- **Required resolution:** Coordinate engines through Python/Sage. Call `libgap` for GAP/CAP algebraic computations and `JuliaCall` for Catlab diagram calculations without demanding a direct GAP-Julia foreign-function interface.

## Hand-rolling morphism rewriting logic instead of delegating to Maude

- **Area:** Morphism composition, path reduction, and rewriting engines.

- **Contract:** Categories, finitely presented quivers, and 2-categories are order-sorted equational and rewriting theories. Morphism composition is an associative binary operator with left and right identities; path equivalence under generating relations is term rewriting modulo associativity and identity. The repository must delegate algebraic rewriting to mature rewriting engines.

- **Defect:** The codebase hand-rolls path logic in Python tuples and string operations ([src/sage_categories/cat/canonical.py](src/sage_categories/cat/canonical.py), [src/sage_categories/cat/presented_colimits.py](src/sage_categories/cat/presented_colimits.py)). It uses a low-level wrapper around GAP's monoid tool `kbmag` ([src/sage_categories/kernel/word_rewriting.py](src/sage_categories/kernel/word_rewriting.py)), which lacks sorted object types and requires Python code to track vertex compatibility manually.

- **Target engine:** Maude (or `python-maude`). Maude provides:
  1. Order-sorted equational logic for typed objects and morphisms.
  2. Native term rewriting modulo associativity and identity ($A, U$).
  3. Automated Knuth-Bendix completion and Church-Rosser confluence checking.
  4. Native support for 2-cell composition, whiskering, and the interchange law.

- **Required resolution:** Replace bespoke Python string/tuple path concatenation and the monoid `kbmag` wrapper with a rewriting engine (such as Maude or GAP's sorted `FpCategories`) that models morphism sorts and relations directly.

