# Mathematical remediation assessment

Assessment date: 2026-09-07. Source revision: `7b712e2488af1794c2815be658fb893f178d46c8`.

**Recommendation:** repair the common categorical operations through their existing leaf consumers before extending the algebra and geometry interfaces. The main boundary is between a mathematical property, the data selecting a construction, and the runtime that executes it. Several current mechanisms exchange these roles.

This is an architectural recommendation for discussion. It records source findings and proposed remedies, rather than changing the topic specifications or phase acceptance.

## The principle that should control the repairs

A mathematical definition should determine an object's public interface independently of its engine representation. A named functor explains how one structure supplies another. Its two actions construct actual target objects and morphisms. The kernel makes the selected target implementation available on the source, including the state its methods need.

For example, a finite free module over the integers should obtain set operations through its module structure and its retained finite-power construction. Its enumeration should follow from chosen enumerations of the factors. Neither the module's engine class nor a module-specific enumeration method should determine that interface.

This gives a practical division of responsibility:

| Mathematical content | Owner |
| --- | --- |
| Objects, morphisms, composition, diagrams, universal maps | The relevant category and the shared Cat calculus |
| A structure map and its equations | The category introducing that structure |
| A selected product, quotient, enumeration, or tensor presentation | The corresponding construction, with its defining maps |
| Reuse through a functor | Its ordinary object and morphism actions; private compilation executes the selection |
| Smith coordinates, word reduction, Gröbner computations, engine conversion | Private computation code for the precise mathematical domain |

Elegance means that a new leaf states fewer independent facts because existing mathematics determines the rest. Moving the same wiring behind a helper does not achieve that reduction. Conversely, an explicit action equation is useful mathematical content even when its expression takes several lines.

The inserter/equifier descriptions of modules and the pullback/equifier description of bimodules already point in the right direction. Preserve that constructional reuse. Judge their remaining code by whether it supplies defining data or compensates for an incomplete shared operation.

## Universal constructions must keep their category and presentation

### Intrinsic constructions in subcategories: issue #32

[`Axiom._construct`](../src/sage_categories/cat/predicates.py) turns inherited axioms on a subcategory into inverse images from its ambient category. [`LimitsCategory` and `ColimitsCategory`](../src/sage_categories/cat/constructions.py) use that mechanism. Thus the subcategory's intrinsic construction family can acquire the wrong ambient category.

At the assessed revision, `AbelianGroups().Colimits(Cat().WalkingParallelPair()).ambient() is AbelianGroups()` evaluates to `False`. The private quotient computation instead enters through [`coequalizer_projection`](../src/sage_categories/algebra/abelian.py), outside the retained colimit calculus. This is the boundary described in [issue #32](https://github.com/dzackgarza/sage-categories/issues/32).

**The mathematical question has a definite answer:** a full, replete subcategory can have a colimit which its ambient category lacks.

For a small counterexample, regard posets as thin categories. Let D have distinct objects a, b, c, d, with precisely the nonidentity relations a<c, b<c, a<d, b<d. Let C be its full subcategory on a, b, c.

1. In C, c is the least upper bound of a and b, hence their coproduct.
2. In D, c and d are incomparable minimal upper bounds. Thus a and b have no coproduct.
3. C is replete because a poset has only identity isomorphisms.

Therefore fullness and repleteness cannot justify deriving C's colimit operation from D's operation. Full faithfulness reflects a universal cone when its image is universal. Transport in the other direction requires the appropriate lifting data and hypotheses. [Mathlib's construction interface](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Limits/Creates.html) makes that distinction explicit.

The repair should give `C.Limits(J)` and `C.Colimits(J)` the exact parameter C. Define their universality using cones and cocones in C. Keep ordinary inverse-image property formation for predicates that actually are restrictions along the supplied functor. Derive comparisons between construction families through preservation or creation results with their hypotheses intact.

The first consumer should install the abelian quotient B/im(f−g), its cocone, and its mediator through `Ab.Colimits(J)`. The abelian engine computes the quotient. Cat retains the presentation and derives induced maps. This same path must serve the balancing diagram for relative tensor products.

### A property cannot select a presentation

[`specs/functor.md`](../specs/functor.md#diagram-shapes-and-universal-constructions) distinguishes a diagram, its limiting presentation, and its apex. That distinction should control the implementation.

For example, if C has a terminal object and binary products, every X is isomorphic to X×1. Excluding singleton indexing shapes still permits this binary presentation. Membership in the essential image of product functors therefore need not distinguish a special class of objects. It certainly cannot identify particular factors or projections.

Keep factor access, legs, the indexing diagram, and the mediator on the selected presentation. An apex convenience can refer to a retained selected presentation, but selection must be explicit when several presentations apply. A new presentation must coexist with an earlier one on the same apex.

This also fixes the basis for duality. A cocone over D corresponds to a cone over D.op(). Their apex may share its object representation. Their indexing categories and maps retain their orientation. Runtime class sharing cannot identify those presentations.

[Issue #24](https://github.com/dzackgarza/sage-categories/issues/24) needs this current reading. The written-declaration collision repair is already present in `_assert_no_semantic_collisions`. `_nontrivial_discrete` now recurses on an opposite shape. A current coproduct of `Cat().Simplex(1)` and `Cat().Simplex(2)` retains the original diagram, its index category, and both construction memberships. Repeating the issue's original spelling repair would address old code. The general `Discrete(X)` path still reaches issue #30; dual subcategory construction must also be checked with #32.

### Existence, choice, and evaluation are separate

`LimitsCategory.__init__` immediately constructs a `limit_functor` on `Fun(J,C)`, although the specification permits C to lack J-limits. A total limit functor on that whole domain requires the corresponding existence and choices.

Use the existing total category of limiting cones as the foundation. Its diagram projection exists without choosing a limit for every diagram. A selected limit functor is obtained from a section where such choices are supplied. A theorem can justify formal limit objects even when a concrete engine cannot evaluate them. An engine's finite evaluation domain is a separate constraint.

This preserves the full mathematical ambition of [issue #4](https://github.com/dzackgarza/sage-categories/issues/4) without treating a finite evaluator as an arbitrary-small-diagram algorithm.

## Refinement must preserve semantic ownership

### Existing values after refinement: issue #31

The public module specimen in [`test_ring_module_scaffold.sage`](../tests/algebra/test_ring_module_scaffold.sage) still fails at the assessed revision. After `ask(AbelianGroups().is_concrete())`, a previously built module loses `action()`.

The source boundary is [`apply_level_shift`](../src/sage_categories/kernel/compiler.py), its dependent runtime classes, and `_replace_runtime_classes`. The observed failure establishes loss of the module's local declaration. It does not yet establish which replacement step first loses it.

The remedy should preserve the written declaration and semantic role independently of each compiled Python class. Recompile affected roles from those declarations and their selected functors. Preserve the value's identity and initialized source data; initialize only genuinely added inherited state. Reuse Sage's [parent and category mechanisms](https://doc.sagemath.org/html/en/reference/structure/sage/structure/parent.html) for their runtime responsibilities.

The decisive consumer remains the same module action before and after refinement. The repair must also preserve existing points and morphisms which depend on the affected classes. Asking a category property before object construction is not a mathematical precondition.

### Morphism properties and their base: issue #33

[`Category.base_category`](../src/sage_categories/cat/category.py) consults `_object_role_source`, which normalizes through compiler role nodes. A runtime sharing relation thereby influences the mathematical base returned for a morphism.

The [issue #33](https://github.com/dzackgarza/sage-categories/issues/33) specimen still fails: retaining two inverse homomorphisms of a presented cyclic group, then calling `inverse()`, reaches `LimitCategory.construct_morphism` without its required family data.

Retain the mathematical morphism category and its fixed endpoints through refinement. `Mor(C)` must retain C even when its implementation is shared with another role. A property of morphisms changes which arrows qualify; it does not by itself change their base. A declared inclusion `Mor(C′) → Mor(C)` can add a stronger base placement and must retain that fact separately from runtime normalization.

The inverse relation belongs to the retained isomorphism data. Its access must remain valid through full-subcategory inclusions and subsequent refinement. This lets a relative unitor return one owned isomorphism whose `inverse()` supplies the reverse map. The current pair-returning unitor functions can then use that common interface.

Together, issues #31 and #33 require one invariant: compiled implementation identity must not determine retained mathematical ownership. They require distinct behavioral repairs at their respective owners.

## Return additive computation to its mathematical owner

[`ObjectForm`](../src/sage_categories/sets/finite.py) requires `direct_sum`, `zero_datum`, and `zero_map`. `Sets._product_object` invokes the first factor's `direct_sum`; `Sets.constant` recognizes a distinguished zero. [`abelian.py`](../src/sage_categories/algebra/abelian.py) installs Smith presentations through this interface.

These operations make the set layer depend on additive structure supplied by a later leaf. A set does not determine a zero or a direct sum. Merely changing the protocol's name would preserve that dependency.

Put finite biproducts, zero morphisms, and matrix composition at the additive-category owner. Put Smith coordinates and the matrix evaluator in its private engine. The faithful functor to Sets supplies actual set maps and transports established equalities. If a set-map evaluator retains a computational representation, its interface should express set-map evaluation and equality, with exact representation domains.

Forgetting structure can retain usable computational data. The key restriction is that a general set operation must not require additive data or choose an algebraic engine by inspecting its first input.

The same ownership repair should divide the current abelian module into mathematical category/construction definitions and private computation. Its public exports currently include `Presentation`, `LinearForm`, and `coequalizer_lift`. Smith coordinates and a chosen quotient lift are engine data. Public group points, homomorphisms, bilinear maps, and universal mediators should supply the mathematical interface.

This is work under the foundational closure in #4 and the current additive-group/module/bimodule consumers. It is necessary for those consumers to demonstrate the intended leaf boundary.

## Relative tensor products should be the common algebraic consumer

The current [`Bimodules`](../src/sage_categories/cat/bimodules.py) construction retains both actions through a pullback and commuting-law equifier. However, `relative_tensor` in [`abelian.py`](../src/sage_categories/algebra/abelian.py) accepts two action arrows and returns a projection in Ab. `relative_tensor_morphism` is a separate function. The inspected definitions do not construct the corresponding object of `Fun` between bimodule categories.

The target is the bifunctor

$$
\otimes_S:\operatorname{Bimod}(R,S;V)\times\operatorname{Bimod}(S,T;V)
\longrightarrow\operatorname{Bimod}(R,T;V).
$$

Its object action forms the balancing coequalizer. Its morphism action is the unique h satisfying

$$
h\,q_{X,Y}=q_{X',Y'}(f\otimes g).
$$

The two outer actions descend by the same universal property, using the stated preservation of the required coequalizers by tensoring. The unit comparisons and associator likewise arise from their universal maps. [The standard bimodule construction](https://stacks.math.columbia.edu/tag/0FQM) supplies the intended scalar directions; [right exactness](https://stacks.math.columbia.edu/tag/00CV) supports the ordinary module instance.

The general construction belongs with bimodules and Cat's colimit calculus. Smith quotient lifts can evaluate its maps privately. They should not define separate public descent machinery.

Preserve the noncommutative middle ring in the current consumer. Also compare induced maps under composition, retain the outer scalar objects, and use the inverse accessor on the unit comparisons. These demands distinguish the bifunctor from isolated computations of its values.

## Presentations: issues #21, #22, and #23

The issue bodies refer to the earlier `algebra/groups.py`, `algebra/modules.py`, and `algebra/algebras.py` implementations. Those paths are absent from the assessed source tree. The required presentation operations remain obligations; their old implementations are not repair targets.

The common construction is a coequalizer presentation

$$
P_1\rightrightarrows P_0\xrightarrow{q}X.
$$

For every Y, maps X→Y correspond to maps P₀→Y that equalize the relation arrows. Use the existing free constructions, adjunctions, and coequalizer mediator to implement that correspondence once. Each leaf supplies its generators, relation morphisms, and exact computation domain.

| Issue | Mathematical repair | Distinguishing result |
| --- | --- | --- |
| [#21](https://github.com/dzackgarza/sage-categories/issues/21), groups | Form free groups on generators and relations. Send each relation generator to its relation word along one leg, and to the unit along the other. | A generator assignment satisfying the relations factors through the quotient; an assignment violating a relation does not. |
| [#22](https://github.com/dzackgarza/sage-categories/issues/22), modules | Form finite free modules from the regular module. Construct the matrix map by linear extension with the specified scalar side, then take its cokernel. | A presentation over the integers yields the expected torsion module and factors a nonzero compatible map. |
| [#23](https://github.com/dzackgarza/sage-categories/issues/23), algebras | Form the appropriate free algebra and quotient by the actual relation morphisms. | In the dual-number example, the nilpotent generator remains nonzero, its square is zero, and scaling it gives the required algebra automorphism. |

Use Sage/GAP's [free-group quotient implementation](https://doc.sagemath.org/html/en/reference/groups/sage/groups/finitely_presented.html) for its supported domain. Use the existing module and polynomial engines for their exact domains. The repository owns their categorical interpretation and universal maps.

The group remedy applies to ordinary groups. Internal free groups in an arbitrary cartesian category require the appropriate existence results. Likewise, a general module actegory need not supply finite free modules or cokernels automatically.

For associative algebras, use the tensor-algebra construction when the required coproducts exist and tensoring preserves them. A commutative polynomial algebra is the symmetric case. The noncommutative-base case uses R-bimodules and their relative tensor product. A polynomial constructor cannot silently supply that more general construction.

A finite presentation also does not guarantee a decision procedure for equality. Retain the exact presentation and give `ask()` the supported exact answers. The finite presentation must remain meaningful when equality is undecided.

## Sets and order: issues #30, #9, and #10

[Issue #30](https://github.com/dzackgarza/sage-categories/issues/30) is live. The public call `Cat().Limits(Discrete(Sets((0, 1))))` raises `AttributeError` at the missing `has_chosen_enumeration` accessor. A tuple-based shape reaches a different path.

Implement a chosen enumeration as the actual retained isomorphism e:I→X, where I is the specified index subobject of the natural numbers. Finite set construction can provide the finite instance. Finite products should compose chosen enumerations through their retained construction; countability alone supplies no choice. Sage's [cartesian-product implementation](https://doc.sagemath.org/html/en/reference/sets/sage/sets/cartesian_product.html) is a computation reference, subject to checking its supported enumeration domains.

Make the consumers in `diagrams.py`, `cat_constructions.py`, `constructions.py`, and `canonical.py` use that same mathematical object. Returning a raw tuple under the missing name would leave the selection and inverse map implicit.

[Issue #9](https://github.com/dzackgarza/sage-categories/issues/9) also names an earlier source layout. The present order leaf already constructs its relation through `Sets.Subobjects(X×X).from_predicate` and accepts an owned underlying morphism. Its current limitations require a more precise repair:

- [`BinaryRelationsCategory.transport`](../src/sage_categories/order/posets.py) builds an inverse table by enumerating both carriers. Transport should use the given isomorphism's inverse and the inverse image of the relation under its product map.
- `lift_order` reads `shape.labels()`. A componentwise order is defined by the indexed family of projection comparisons. Finite evaluation can enumerate a supplied finite presentation; the general definition must retain that family.
- Finite-poset algorithms should return the specified subobjects, maps, or ordered objects. Their engines must reconstruct points in the original ambient poset.

[Issue #10](https://github.com/dzackgarza/sage-categories/issues/10) remains visible in `ordered-sets.md`. Repair the whole admission definition: a semantic constructor receives the declared mathematical data; a predicate decides a proposed property; a named construction supplies its mathematical conclusion. Preserve exact False and undecided outcomes for proposed structures. The documentation must make the trust attached to direct construction explicit and use the same model in its examples.

## Remaining algebra, geometry, and static work

For algebras, first supply the selected monoidal category on which `Monoids` operates. For a commutative base, this can be left modules under the relative tensor product. For a general base, use bimodules. The equivalence with monoids should provide multiplication, unit, and their laws directly. In the ordinary noncentral ring case, the coslice R↓Rings gives a further mathematical comparison; it must not be confused with central R-algebras.

For geometry, complete commutative-ring presentations and localization, then the relevant topology, sheaves, and locally ringed spaces. `Spec` must act on both rings and maps, including localization maps on sections. The affine anti-equivalence supplies a strong public comparison. Gluing belongs to locally ringed spaces, with local affineness establishing the scheme result. These are the constructions in [Stacks, affine schemes](https://stacks.math.columbia.edu/tag/01I1) and [scheme gluing](https://stacks.math.columbia.edu/tag/01JA).

Retain the projective-line consumer with its sheaf and chart-swap map. A list of rational points would not determine that scheme. Broader ordinal/cardinal algorithms remain separate from the scaffold, but the original inherited cardinality and enumeration obligation in #4 must remain visible after scaffold delivery.

The static projection needs the same semantic repair as runtime ownership. [`compiler._inheritance_projection`](../src/sage_categories/kernel/compiler.py) merges bases under a declaration's qualified name. [`stub_generator.py`](../src/sage_categories/kernel/stub_generator.py) projects those bases into source-generated stubs. This loses distinctions needed for parameter-dependent categories unless the projection represents those parameters too.

Project one semantic declaration relation into runtime and static views. Use ordinary generics and narrowly scoped [mypy extension hooks](https://mypy.readthedocs.io/en/stable/extending_mypy.html) where they can express the dependency. Keep exact runtime endpoint checks. General value-dependent category identities require a concrete static representation and a demonstrated consumer before claiming static exactness; a union of every observed base is not that representation.

The first static examples should be the same public functor application, fixed-endpoint hom construction, refinement, and relative tensor operation used at runtime. Repair the projection at those boundaries while repairing the runtime owners.

## Recommended dependency order

1. Repair semantic role retention and refinement through the existing module and inverse consumers: #31 and #33.
2. Give universal constructions their exact category and selected presentation. Integrate the abelian coequalizer and put its additive computation at its owner: #32, the remaining duality boundary in #24, and #4.
3. Complete chosen enumeration and remove finite-presentation assumptions from general definitions: #30 and the current order work in #9. Reconcile #10 with the resulting admission semantics.
4. Deliver the actual relative tensor bifunctor, with its outer actions and coherence maps, through the shared colimit operation and private additive engine.
5. Use those shared constructions for presentations and algebra objects: #21–#23. Extend the resulting commutative algebra into affine geometry and scheme gluing.

Exact static consumers accompany each repaired boundary. This ordering follows dependencies, rather than issue numbers or old phase labels. Independent local computations can be retained, but downstream acceptance must use the repaired shared operation.

[Issue #5](https://github.com/dzackgarza/sage-categories/issues/5) calls for mathematical review of these claims. An independent reviewer should challenge the public construction with a nonidentity map or a competing universal family. The review should inspect how the leaf obtains the operation. Scanner results cannot establish either proposition. This requires a focused mathematical review of the delivered boundary, not an additional review framework.

## Evidence boundary

The assessment used all open issue bodies and their comments, the open PR metadata, the production and static plans, and the source definitions linked above. It inspected the active plans' public consumer requirements; their status labels were not treated as proof of implementation. The conceptual synthesis uses the project discussion about uniform category-owned interfaces and ordinary executable functor actions as background, while deriving the recommendations from the current source and mathematics.

Direct Sage exercises reproduced #30, #31, and #33 and established the incorrect ambient parameter relevant to #32. The stated Cat coproduct specimen supplies limited current evidence for #24. This is not whole-system certification or an independent R6 acceptance.

For the remaining negative findings:

| Searched | Found | Conclusion | Confidence | Gaps |
| --- | --- | --- | --- | --- |
| Tracked source tree; current algebra exports; complete bimodule constructor and relative-tensor functions | The old presentation modules are absent; current relative tensor functions return Ab maps | The earlier presentation obligations and the categorical relative-tensor consumer remain open in the inspected source | High | Broader historical implementations were not re-executed |
| `stub_generator.py`; compiler inheritance and subtyping projections | Class bases are merged by declaration name | Parameter-sensitive static ownership needs further representation work | High for the mechanism; unmeasured for its full impact | No full mypy run or plugin implementation audit |
| Foundation and leaf plans; topic specifications; current source inventory | Geometry and broad cardinal APIs remain planned beyond the inspected scaffold | Their completion requires the mathematical owners described above | High for the scoped recommendation | Full API-by-API implementation certification was outside this assessment |
