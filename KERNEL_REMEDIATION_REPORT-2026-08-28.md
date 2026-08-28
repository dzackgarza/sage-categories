# Kernel-first remediation report

Date: 2026-08-28

> This is a review artifact.
> The active execution owner remains `PLAN-pr-8-functorial-kernel-completion`.
> This report does not change plan status.

## Verdict

The prior report found several real boundary defects.
Its main plan verdict was wrong.

The plan records defects for remediation.
A defect that is now repaired does not make the plan stale.
It shows that the plan caused the intended repair.

The main live problem is in the kernel contract.
The current system mixes three different operations:

1. applying a functor to an object or morphism;
2. converting source constructor data into target constructor data;
3. making target-category methods available on a structured source object.

These operations must stay distinct.
The kernel must connect them once.
Leaves must state only their mathematical data and the conversion required by each selected functor.

The required implementation uses constructor chaining in the compiled superclass order.
A selected functor supplies the exact input for the target class constructor.
The compiler runs that constructor in the controlled superclass chain.
An inherited target method then uses the target state on the same Python instance.
It does not search for a target object during method dispatch.

This preserves the mathematical meaning

```text
x.f() = F(x).f()
```

without a public category-level image lookup.
The explicit functor action `F(x)` remains a separate, inspectable mathematical operation.

## Transcript evidence boundary

The requested session does not contain a design decision.

- Searched: the complete parsed Claude session `e8ad9875-810f-4b88-b553-902320e67825`.
- Found: `/clear`, a request to stop background agents, and a usage-limit message.
- Conclusion: this session identifies the time window only. It supplies no kernel or leaf requirement.
- Confidence: High.
- Gaps: none within that session.

The applicable corrections occur in these adjacent parsed sessions:

- `9aec1c30-e33e-403f-97e2-53daf9bf2e5b` states that plan-versus-tree agreement is not the review target.
- `4544eba5-d6a9-41dc-9f38-78912f0567c8` supplies the current kernel model.
- `b55dc6aa-3466-419e-9e1e-376a975b35b9` supplies related object, element, functor, predicate, and cardinal requirements.

The latest user corrections establish these requirements:

- A poset is the pair `(X, R)`.
- The selected projection sends `(X, R)` to `X`.
- A selected functor teaches the compiler how source constructor data feeds the target constructor.
- The compiled source class can inherit target methods and target state.
- A functor has an image. A target category does not select one functor image.
- Several ordinary functors can have the same endpoints.
- Selecting a functor does not change its mathematical definition.
- A property category owns its membership proposition.
- `is_finite()` is the proposition for membership in `Sets().Finite()`.
- Sage axiom wiring is the model for propagated property categories.
- `ObjectType`, `ElementType`, and `MorphismType` are the category declarations.
- A leaf must not receive a second role-class data model.
- A receiver-returning helper is not a mathematical acceptance witness.

`POL-DOC-012` makes these later decisions control earlier drafts.
`POL-DOC-014` and `POL-DOC-015` require standard terms and deletion of retired terms.

## The corrected kernel contract

### Category declarations

Each category declares its own `ObjectType`, `ElementType`, and `MorphismType` implementation classes.
The compiler reads those declarations directly.

An axiomatic category can use an independent implementation class.
Sage then wires that class to the base category and axiom.
The implementation class need not be nested in the base category class.

This replaces external `Role` maps and instance-owned role factories.

Governing sources:

- `POL-CAT-017`, `POL-CAT-057` through `POL-CAT-060`;
- `POL-KERNEL-012` through `POL-KERNEL-014`, and `POL-KERNEL-026`;
- `POL-LEAF-059`, which needs revision to permit Sage's independent axiom class form;
- `specs/property-refinement.md`, "One constructor per property category" and "Category membership is proposition-backed Boolean admission";
- [Sage category-with-axiom reference](https://doc.sagemath.org/html/en/reference/categories/sage/categories/category_with_axiom.html).

### Ordinary functor action

Every functor has complete object and morphism actions.
Its object action accepts an owned source object.
Its morphism action accepts an owned source morphism.
The generalized-element action follows from the morphism action.

An ordinary functor remains ordinary when a category returns it from `structure_functors()`.
Selection changes compiler input only.

Functor images belong to exact functors and exact composites.
They do not belong to a target category.
Thus `F(x)` and `G(x)` remain distinct expressions when `F` and `G` have the same endpoints.

When selected routes reach one compiled target role, their constructor inputs must be coherent.
The compiler can require identity agreement for that one inherited role.
This rule applies only to selected inheritance routes.
It does not merge the images of arbitrary functors with the same codomain.

Governing sources:

- `POL-CAT-012` through `POL-CAT-016`, and `POL-CAT-085`;
- `POL-KERNEL-017` and `POL-KERNEL-027`;
- `POL-LEAF-058`;
- `specs/functor.md`, "Structural inheritance" and "Functor construction and presentation data".

### Constructor conversion

A selected functor also supplies an exact constructor conversion for each compiled role it contributes.
That conversion is not the functor's object or morphism action.

For `U: Posets() -> Sets()`, the contracts are different:

- `U.on_object(P)` applies the projection to the owned poset `P = (X, R)` and returns `X`;
- the object-constructor conversion maps the poset constructor data to the exact input accepted by `Sets().ObjectType`;
- the morphism-constructor conversion maps monotone-map constructor data to the exact input accepted by `Sets().MorphismType`.

The kernel owns conversion composition, route traversal, and constructor order.
The leaf owns the semantic conversion at one immediate functor edge.

Current conflicts:

- `src/sage_categories/cat/functors.py:293-321` treats retained images as constructor conversions;
- `src/sage_categories/cat/functors.py:402-427` derives constructor conversions by reinterpreting ordinary functor actions;
- `src/sage_categories/posets/category.py:293-307` gives the functor constructor records instead of owned posets and monotone maps;
- `src/sage_categories/sets/cardinals.py:737-761` imports kernel construction envelopes to state a leaf conversion.

Governing sources:

- `POL-SCOPE-011`, `POL-SCOPE-012`;
- `POL-LEAF-058`;
- `POL-KERNEL-017`, `POL-KERNEL-027`, `POL-KERNEL-029`;
- `specs/functor.md`, "Structural inheritance" and "Functor construction and presentation data";
- `specs/leaves.md`, "Construct from the strongest defining data".

### Compiled inheritance

The compiler builds the public source role from the selected target roles.
It threads each exact converted input through one controlled constructor chain.
Each target initializer runs once.

An inherited method uses ordinary Python method resolution on the structured value.
Its target-category state is already initialized on that value.
The method does not call a transport function or recover another object before it can work.

The explicit functor action remains available as `F.on_object(x)` or standard callable syntax.
Constructor threading does not replace that mathematical operation.

The current D18 decision is partly correct.
It correctly requires one controlled constructor chain and direct inherited calls.
It is wrong where it permits a method to read a separate canonical target object from private dispatch state.
Its receiver-returning acceptance case proves only Python identity.

Normalize these sources:

- `CONTRIBUTING.md`: `POL-CAT-061`, `POL-CAT-062`, `POL-CAT-066`, `POL-KERNEL-018`, `POL-KERNEL-028`, and `POL-KERNEL-029`;
- `specs/functor.md`: "Compiled roles" and "Compiler contract";
- `specs/leaves.md`: "Inherited methods use compiled implementation inheritance";
- the active plan: D12, D18, and the inherited-execution witness row.

Current implementation evidence:

- `src/sage_categories/kernel/compiler.py:940-1001` compiles the direct MRO;
- `src/sage_categories/cat/category.py:140-161` exposes `structural_image()`;
- `src/sage_categories/sets/objects.py:139-215` uses that lookup in set methods;
- `src/sage_categories/sets/maps.py:63-75` repeats it for set maps.

The direct MRO can remain.
The category-level lookup and its leaf call sites must go.

### Property containment

A property category declares one membership proposition.
Its public predicate method applies that proposition.
Category containment asks the same proposition at Python's Boolean boundary.

For finite sets:

```text
X.is_finite()
```

is the proposition owned by `Sets().Finite()`.
The mathematical condition belongs in that category once.
Descendants receive the one `Sets()` method through selected structural functors.

The current policy set contains both a placement-only model and a proposition-backed model.
Normalize these sources to one model:

- `POL-CAT-025`, `POL-CAT-043`, `POL-CAT-044`, `POL-CAT-060`, and `POL-CAT-068`;
- `specs/property-refinement.md`, "Property categories supply evaluation rules" and "Category membership is proposition-backed Boolean admission";
- `specs/sets.md`, "Cardinality and enumeration";
- `specs/undecidable-properties.md`, the property-category and containment sections.

The Boolean boundary must state one result for `Unknown`.
The current specifications require a loud failure because Python containment cannot return `Unknown`.

Current conflicts:

- `src/sage_categories/cat/properties.py:100-150` stores a predicate and a role map but does not own the complete membership operation;
- `src/sage_categories/cat/category.py:264-281` uses generic placement membership;
- `src/sage_categories/sets/objects.py:190-200` calls `.predicate()` directly.

### Refinement, generalized elements, and the point level shift

The kernel owns same-object refinement for objects, generalized elements, and morphisms.
The exact property category supplies the first compiled role.
Identity and already-constructed state remain unchanged.

The kernel also owns generalized-element construction and identity.
`F.on_element(t)` follows from `F.on_morphism(t.defining_morphism())`.
A leaf supplies no generalized-element cache.

The point level shift must enter the normal compiled graph.
It must not add methods later with `setattr`.

Current conflicts:

- `src/sage_categories/kernel/refinement.py:154-159` excludes elements from the generic path;
- `src/sage_categories/cat/category.py:403-416` delegates generalized-element construction;
- `src/sage_categories/kernel/compiler.py:1004-1040` mutates existing compiled classes;
- `src/sage_categories/posets/category.py:71-110` and `389-399` add local element caches and construction;
- `src/sage_categories/sets/category.py:226-235` adds another local element path.

Governing sources:

- `POL-KERNEL-001`, `POL-KERNEL-002`, and `POL-KERNEL-012` through `POL-KERNEL-014`;
- `POL-CAT-057` through `POL-CAT-059`, `POL-CAT-083`, and `POL-CAT-084`;
- `POL-CODE-013`;
- `specs/functor.md`, "Point categories and point functors" and "The level shift".

### Universal data and morphism-property operations

Universal-construction families own diagrams, projections, injections, cones, cocones, and universal maps.
The data are indexed by the construction input.
One apex can retain distinct universal data for distinct diagrams.

Morphism-property categories own operations implied by placement.
In particular, `Mor(C).Isomorphisms()` owns inversion.
A leaf can supply the mathematical construction of the inverse rule.
It must not own the public inverse operation or its generic cache.

Current conflicts:

- `src/sage_categories/cat/constructions.py:332-340` rejects distinct diagrams with one apex;
- set construction modules use `retained_method` for generic universal data;
- `src/sage_categories/posets/category.py:428-434` adds inverse retention locally;
- set and cardinal modules repeat inverse construction and retention paths.

Governing sources:

- `POL-CAT-046`, `POL-CAT-079`, and `POL-CAT-080`;
- `POL-LEAF-056`;
- `POL-KERNEL-025`;
- `POL-FUN-023` and `POL-API-023`;
- `specs/functor.md`, "Diagram shapes and universal constructions".

### Stable public type owners

The compiler owns generated public types.
Each source module owns its declarations.
A leaf must not write compiled types into another module.

Current conflicts:

- `src/sage_categories/sets/category.py:429-438` writes types into neighboring modules;
- `src/sage_categories/sets/cardinals.py:929-935` writes the cardinal type into other modules;
- `src/sage_categories/ordinals/category.py:71-84` uses global late binding.

Governing sources:

- `POL-CODE-013`;
- `POL-KERNEL-021`, `POL-KERNEL-023`, and `POL-KERNEL-028`;
- `POL-LEAF-025` and `POL-LEAF-032`.

## Dependency-ordered remediation workstreams

### K1. Normalize the contract

Revise the policies, specifications, and active plan together.
Keep direct inheritance and its controlled constructor chain.
Remove target-category image lookup from method execution.
Remove the receiver-returning witness.
State functor action, constructor conversion, and compiled inheritance as separate contracts.

Acceptance:

- No governing source gives a target category an image operation.
- No governing source treats selection as a new functor kind.
- D18 states that the constructor chain initializes target state without a dispatch-time image lookup.
- Property containment has one stated proposition and one Boolean boundary.
- Axiom wiring permits an independent Sage category implementation class.

### K2. Replace role metadata with category declarations

Make the compiler read `ObjectType`, `ElementType`, and `MorphismType` directly.
Wire axiomatic categories through Sage's category-with-axiom mechanism.
Remove `Role` dictionaries from property and construction APIs.

Acceptance:

- An independent `FiniteSets` class is the implementation of `Sets().Finite()`.
- A property category refines object, element, and morphism roles without a leaf role map.
- The compiler derives all three role families from category declarations.

### K3. Separate functor action from constructor conversion

Give every functor semantic object and morphism actions.
Give selected edges exact constructor conversions as separate retained data.
Compose those conversions in the kernel.

Acceptance:

- `U.on_object(P)` accepts a poset and returns its underlying set.
- `U.on_morphism(f)` accepts a monotone map and returns its set map.
- Poset construction initializes the inherited set state from `(X, R)` without a kernel construction-input import in the leaf.
- Two ordinary functors with the same endpoints retain their own images.
- Only coherent selected routes can initialize one compiled target role.

### K4. Complete the compiled constructor chain

Run every selected target initializer once in the C3 chain.
Make target methods use initialized target state on the source instance.
Delete the public category-level image lookup.

Acceptance:

- For `P = (X, R)`, `P.cardinality()` obtains the cardinality of `X` through the selected projection.
- The `Sets()` method needs no knowledge of `Posets()`.
- No `Sets()` method calls a transport or image lookup.
- Ordinary and special methods use the same compiled inheritance mechanism.
- A mathematical leaf override adds only the result structure that the target construction does not provide.

### K5. Complete containment, refinement, and generalized elements

Make each property category own its membership proposition.
Use one same-object refinement path for all three role families.
Compile point-level inheritance without post-construction class mutation.

Acceptance:

- `X.is_finite()` applies the proposition owned by `Sets().Finite()`.
- `X in Sets().Finite()` asks that same proposition.
- Exact `True` uses the same property constructor as a trusted mathematical construction.
- `F.on_element(t)` is derived from `F.on_morphism`.
- Objects, generalized elements, and morphisms use no leaf-owned identity cache.

### K6. Move universal data and inverse operations to their generic owners

Index universal data by the input diagram.
Expose inverse through the generic isomorphism category.
Let leaves supply only the defining mathematical algorithms.

Acceptance:

- Two diagrams with one apex retain distinct universal data.
- Product projections and universal maps come from the product family.
- A poset isomorphism receives `.inverse()` from `Mor(Posets()).Isomorphisms()`.
- The poset leaf supplies only the proof or construction that the inverse set map is monotone.

### K7. Stabilize public types

Bind public generated types at their compiler owner.
Remove cross-module assignments and late global binding.
Regenerate static projections only after the runtime role surface is stable.

Acceptance:

- Import order does not change a public type.
- No leaf module assigns a public implementation type into another module.
- Runtime types and generated stubs come from one category declaration graph.

## Leaf remediation after the kernel

These changes are leaf migrations.
They are not substitutes for K1 through K7.

### `Sets()`

Remove calls to `structural_image()` from `sets/objects.py` and `sets/maps.py`.
Remove direct `.predicate()` routing from set methods.
Remove `Role` maps from property and construction declarations.
Remove leaf retention decorators after universal families own the data.

Keep the set-specific mathematics:

- membership, iteration, and cardinality algorithms;
- set maps and function sets;
- products, coproducts, subsets, quotients, limits, and colimits;
- private computation-engine adapters.

### `Posets()`

Make the object data the pair `(X, R)`.
Give the projection functor semantic object and morphism actions.
Give it the exact conversions needed by set constructors.

Remove local generalized-element caches, route lookup, generic inverse retention, and role maps.
Replace generic `_construct` entry points with exact category constructors.

Keep the poset-specific mathematics:

- the order relation and partial-order laws;
- monotone-map validation;
- induced orders and poset constructions;
- finite-poset algorithms and their private Sage adapter;
- the proof or algorithm that a set-map inverse is monotone.

### Number sets, cardinals, and ordinals

Move direct refinement calls to the generic point and property paths.
Remove kernel construction-input types from cardinal functor declarations.
Remove cross-module public type assignments.

Keep number-set membership and coercion rules.
Keep cardinal and ordinal normalization, arithmetic, order, and cofinality algorithms.

### Universal-construction leaves

Remove generic retention and forwarding machinery from products, exponentials, limits, power objects, finite subsets, and subobjects.
Keep each construction's set-specific algorithm and defining mathematical maps.

## Disposition of the prior report

| Prior finding | Disposition |
| --- | --- |
| V1: the plan is stale | Reject. It treats the remediation source as a source snapshot. |
| V2: cardinality functor domain | Keep as a separate mathematical defect. It is not a kernel-boundary finding. |
| V3: number sets bypass point placement | Keep as a post-kernel leaf migration. Reassess after generic point refinement works. |
| V4: property categories require role maps | Keep the observed defect. Replace the proposed nested-class remedy with Sage axiom wiring and direct category declarations. |
| V5: `Posets()` owns generic mechanisms | Split. Move caches, route work, generalized elements, and public inverse ownership to the kernel. Keep order mathematics in the leaf. |
| V6: set constructions own generic retention | Split. Move universal retention to construction families. Keep set algorithms in the leaves. |
| V7: function-set property placement | Reassess after the property and containment contract is normalized. |
| V8: internal tests are public witnesses | Keep only the demand for mathematical acceptance. Remove the receiver-returning helper. |
| V9: plan gaps | Do not treat plan administration as a kernel defect. Record only active requirements and acceptance in the plan. |

## Separate mathematical defect

The cardinality functor remains partial on its declared domain.

`specs/cardinality.md` declares a functor from `core(Sets())` to `Cardinal()`.
The same specification permits a set cardinality to be `Unknown`.
`src/sage_categories/sets/cardinals.py:987-1001` asserts that every object image is an exact cardinal.

The project must choose one honest mathematical contract:

- restrict the functor domain to sets with an established exact cardinal; or
- change the target model so every allowed result is an object of the codomain.

This decision follows the kernel work.
It must be complete before `Sets()` is called mathematically complete.

Governing sources:

- `POL-SET-010`, `POL-SET-025`, and `POL-API-021`;
- `specs/cardinality.md`, "Integration with `Sets()`";
- `specs/functor.md`, "Acceptance conditions".

## Final acceptance surface

The remediation is complete only when the public mathematics proves the kernel boundary:

1. Construct `P = (X, R)` through `Posets()`.
2. Apply its selected projection to objects and monotone maps.
3. Call inherited set operations on `P` without leaf routing code.
4. Apply one property predicate through its property category and containment boundary.
5. Refine an object, generalized element, and morphism through the same generic mechanism.
6. Apply a functor to a generalized element through its defining morphism.
7. Construct two diagrams with one apex and recover each diagram's universal data.
8. Invert a poset isomorphism through the generic isomorphism category.
9. Inspect two ordinary functors with one codomain without a category-level image selector.
10. Verify that public types do not depend on import order or cross-module mutation.

These specimens test mathematical calls.
They do not test the absence of historical mistakes.

SLOP-REPORT-COMPLIANCE: I hereby assert that the above report is formatted in compliance with all slop report requirements.
