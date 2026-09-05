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
about nine concrete warts, several of which I hit head-on writing the poset leaf,
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

**Tier 2 — kernel/Cat design deficiencies.**

3. Cat cannot encode or carry standard categorical structure facts. There is no
   first-class way to state and retain that a category has a terminal or initial
   object, is pointed, has products or coproducts, has (small, filtered, or other)
   limits or colimits, is complete, cocomplete, or bicomplete, is closed under
   pullbacks or pushouts, is monoidal with respect to one or more structures, or
   is abelian. Nor are the theorems that derive these facts baked in — for
   example, that `Fun(C, D)` has a terminal object because `D` does, or that a
   functor category into a complete category is complete. Downstream code cannot
   reason from such a fact because the framework has nowhere to hold it. The
   terminal problem in (4) is one narrow symptom.

4. An unmet contract obligation surfaces as a runtime raise, not at instantiation.
   `Category.Terminal()` raises "declares no terminal object" only when the method
   is called; a leaf author learns which parts of the inherited contract are
   unimplemented by hitting runtime errors during execution rather than from
   defining or instantiating the leaf. `Fun(C, D)` and a finite presented category
   both have a terminal object — `[1]` and `Fun(C, C)` among them — computable from
   machinery they already carry (pointwise limits; finite morphism enumeration),
   yet nothing signalled the method was unimplemented until the call failed, and I
   supplied `Terminal()` on both by hand. A category with genuinely no terminal,
   such as the walking parallel pair, should express that absence as a property,
   not communicate it only by raising when asked.

5. Claiming a declaration has no mechanism for axiom-subcategory leaves.
   `leaf-scaffolding.md` says the declared `Posets`/`TotallyOrderedSets` must be
   claimed; `ordered-sets.md` realizes them as `BinaryRelations().PartialOrder()`.
   Nothing binds an open declaration to an axiom subcategory of a constructed
   category, so the declared symbols are unclaimed and only accessors exist.

6. The least common category of two property-refined placements needs
   hand-declared inclusions. I fixed the monoid-forgetful case, but
   `NarrowedProperty` still enumerates cross-inclusions imperatively, so composing
   property-intersection placements can still report "no least common category,"
   which is a missing edge, not a mathematical fact — the property lattice is
   maintained by hand rather than derived, a facet of the same gap as (3).

**Tier 3 — plumbing leaking into leaf mathematics.**

7. Predicate-handler registration is definition-order sensitive with an opaque
   error ("unresolved semantic domain"); registrations must sit below the classes
   they annotate. A mathematician would not predict that.

8. Construct versus refine take different argument types. `Posets()(subobject)`
   works, `Posets()(relation_object)` does not, because the property-subcategory
   constructor re-runs the base constructor on the base's construction datum.

9. `.datum()` and `.point()` unwrapping is everywhere. "The relation on X×X
   selected by ≤" becomes tuple decomposition and rewrapping.

### Net

The "up and running is thin" claim holds only for the inheritance spine. Getting a
leaf *functional* today demands knowing the handler-ordering rule, the
Axiom/PropertySubcategory wiring, that the contract announces unmet obligations
only by raising at call time, that Cat cannot hold the categorical structure facts
downstream code needs, and that the template does not run. That is more kernel
knowledge than the philosophy wants at the prototyping stage.
