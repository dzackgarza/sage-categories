# Complaints

Friction, papercuts, and kernel/Cat design deficiencies observed while working,
recorded against the philosophy that leaf authoring should be thin and mostly
mathematical. Excludes defects fixed within the same workstream.

## Leaf-authoring friction — production-tower scaffolds

- **Workstream:** production-tower leaf scaffolds — Sets integration, supplied
  monoidal structures, the order leaf (binary relations, posets, total orders),
  and magma/monoid consumers over sets.
- **Commits:** `51ca8d7..2f25e26` on `codex/functorial-core-kernel`, baseline
  `f679083`.
- **Date:** 2026-09-05.

Short answer: the philosophy is half-met. The spine works and is genuinely thin.
"A mathematician who doesn't program can reason into correct code" is undercut by
about eight concrete warts, several of which I hit head-on writing the poset leaf,
and two of which my own leaf now carries.

### What actually worked (the win)

Declaring one structure functor to a base and getting everything downstream for
free. `BinaryRelations().to_sets()` as a faithful isofibration gave relation
objects their points, maps, iteration, and set constructions, correctly parented,
with no extra code. `equality.point(0)` just worked and its parent was the
relation object. That is the philosophy delivering, and it is thin.

### Warts, ranked by how much they break the promise

**Tier 1 — the "copy the template and reason" path is broken.**

1. The canonical poset specimen does not run as written.
   `specs/poset-minimal-template.py:109` defines order comparison as
   `relation.membership_proposition(relation.ambient_object()(self, other))`, but
   `membership_proposition` is a category method, and `relation` there is a
   subobject value. A leaf author copying the template gets an attribute error,
   not a poset. The template is the primary teaching surface, so this is the most
   damaging wart. I had to implement `<=` a different way.

2. Finite property decision is hand-rolled, and the generic relation calculus is
   not reusable. `cat/relations.py:97-107` already decides reflexivity,
   transitivity, and antisymmetry, but on relation *morphisms* of `Relations(C)`,
   a different representation from the order leaf's sets-with-a-relation objects.
   I could not reuse it, so `order/posets.py` re-decides the three laws over raw
   `.datum()` tuples. That duplication is a real design smell, and my leaf owns it.

**Tier 2 — kernel/Cat gaps the leaf author should not have to patch.**

3. Terminal objects that exist and are computable are not derived.
   `Category.Terminal()` unconditionally raises "declares no terminal object"
   unless a category overrides it. `Fun(C, D)` has a pointwise terminal, the
   constant diagram at `D`'s terminal, derivable from its `limit_construction`; a
   finite presented category has a terminal object computable from its finite
   morphism enumeration. Neither is computed, so I added `Terminal()` to both
   `FunctorCategory` and `FinitePresentedCategory`. Consumers hit the error on
   objects as basic as `[1]` and `Fun(C, C)` that mathematically have a terminal.
   A category with genuinely no terminal, such as the walking parallel pair,
   raising is correct; the gap is only the computable terminals.

4. Claiming a declaration has no mechanism for axiom-subcategory leaves.
   `leaf-scaffolding.md` says the declared `Posets`/`TotallyOrderedSets` must be
   claimed; `ordered-sets.md` realizes them as `BinaryRelations().PartialOrder()`.
   Nothing binds an open declaration to an axiom subcategory of a constructed
   category, so the declared symbols are unclaimed and only accessors exist.

5. The least common category of two property-refined placements needs
   hand-declared inclusions. I fixed the monoid-forgetful case, but
   `NarrowedProperty` still enumerates cross-inclusions imperatively, so composing
   property-intersection placements can still report "no least common category,"
   which is a missing edge, not a mathematical fact.

**Tier 3 — plumbing leaking into leaf mathematics.**

6. Predicate-handler registration is definition-order sensitive with an opaque
   error ("unresolved semantic domain"); registrations must sit below the classes
   they annotate. A mathematician would not predict that.

7. Construct versus refine take different argument types. `Posets()(subobject)`
   works, `Posets()(relation_object)` does not, because the property-subcategory
   constructor re-runs the base constructor on the base's construction datum.

8. `.datum()` and `.point()` unwrapping is everywhere. "The relation on X×X
   selected by ≤" becomes tuple decomposition and rewrapping.

### Net

The "up and running is thin" claim holds only for the inheritance spine. Getting a
leaf *functional* today demands knowing the handler-ordering rule, the
Axiom/PropertySubcategory wiring, that a computable `Terminal` is not derived, and
that the template does not run. That is more kernel knowledge than the philosophy
wants at the prototyping stage.
