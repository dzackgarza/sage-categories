# Exact derived-category implementation

Continuation of [the remediation cutoff](remediation-handoff.md), prerequisite
for [#40](https://github.com/dzackgarza/sage-categories/issues/40).

## Public operation and red consumer

The additive owner is the exact retained inverse-image category:

```python
groups = AdditiveGroups(Cartesian(Sets()))
Ab = groups.Commutative()
```

Its public implementation declaration selects its identity:

```python
class AbelianOperations(Category):
    class ObjectType:
        pass

    class ElementType:
        pass

    class MorphismType:
        pass

    def forgetful(self):
        return forget

    def structure_functors(self):
        return (Fun(Ab, Ab).one(),)


Cat().implement(AbelianOperations)
```

Here `forget` is the retained composite from Ab through its named group, monoid,
and magma restrictions to Sets. Its full construction is in
[`test_exact_derived_category_implementation.sage`](../tests/kernel/test_exact_derived_category_implementation.sage).
That specimen constructs a cyclic group, point, identity arrow, inclusion, and
forgetful composite before requesting the implementation.

At source checkpoint `856a3dc`, `_adopt` rejects this operation because Ab is not
an open named Cat declaration. The later assertions require the same category,
inclusion, commutative membership, existing point parent, identity action,
negation/addition, forgetful image, and retained identity morphism. They remain
unreached at this cutoff.

Run the unchanged specimen through the command in the main handoff. Its local
cutoff log is `/tmp/sage-categories-cutoff-derived-red.log`; the tracked consumer
is sufficient to reproduce the failure after a fresh checkout.

## Contract and provenance

[specs/functor.md](../specs/functor.md), “Implementing a named category,” covers
`D.P1().P2().P3()` and requires in-place implementation with ambient constructors.
[specs/leaves.md](../specs/leaves.md) gives the declaration for `C.P()`.
[The finite-poset declaration](../specs/finite-poset-minimal-template.py) applies
identity selection to an inverse-image category. The retained category identity,
ordinal, and property-class realization belong to
[specs/resolution.md](../specs/resolution.md).

D156's decision locator is Claude session
`54674b9b-d5f3-42bd-9613-e9aea3ae5647`, `2026-09-02T22:33:35Z`.
D160 classifies the concrete public spellings as specification choices. The
original D156 message was not available in the inspected standard transcript
stores during this unit. This is a provenance limit on that locator, rather than
evidence against the explicit derived-category contract.

## Required generic repair

Read these complete definitions and their immediate callers:

- `cat/category.py`: `_declares_implementation`, `_initialize`, `_adopt`, and
  `_select_functors`.
- `kernel/compiler.py`: `implement_category`, `realize_implementation_class`,
  `_install_class_join`, `_own_classes`, and `local_role_class`.
- The inverse-image category constructor and retained functor graph used by Ab.

The current identity recognition already routes to `_adopt`. The guard requiring
an `_open_declarations` entry rejects derived categories. Beyond that guard,
`implement_category` assigns the implementing class directly to the category,
and `_select_functors` replaces its structural graph. Those operations would
discard the existing inverse-image class behavior and its selected defining maps.

Implement exact-category strengthening through the existing Sage class joining
and retention primitives. Preserve the original mathematical construction while
installing the category's new methods and local role declarations. Check which
declaration `local_role_class` selects; a class join alone does not establish that
the new methods become effective.

An identity declaration identifies the retained target. Its reflexive edge adds
no inherited state. The original inclusion and target projection still supply
the category's inherited operations.

The complete preservation boundary is:

- Ab's identity, ordinal, universe, and strongest placement;
- its defining functor, target category, membership predicate, inclusion, target
  projection, and universal presentation;
- selected inherited targets and their actual functor images;
- existing objects, points, arrows, identities, inverses, and construction caches;
- ambient constructors, new category methods, and effective local role methods;
- the same mathematical owners in the generated static projection.

`Axiom.implemented_by` binds an implementation to an entire axiom family. The
required operation here strengthens one exact derived category. Its public
identity-bound implementation expresses that scope.

## First complete result

Make the unchanged consumer reach all assertions. Exercise both values created
before installation and values constructed afterward. Give an effective local
role method a real mathematical use, in addition to the category-level forgetful
method, so the class-joining proof covers the promised roles.

Then return to #40's mixed biproduct, zero maps, linear extension, exact Ab hom
owner, and static images. #32's first abelian coequalizer consumes those additive
operations. Keep the generic repair and additive leaf implementation as separate
owning units with their respective complete consumers.
