# Mathematical audit of leaf boundaries

Historical source review, not the current remediation plan. Its implementation
recommendations and work order are superseded by `PLAN-native-engine-remediation`;
see [the governing-plan locator](remediation-handoff.md). The recorded source
findings and examples remain evidence at the revisions named below.

Reviewed on 2026-09-07 at `097b4c4`. The reviewed source is unchanged from `7b712e2488af1794c2815be658fb893f178d46c8`.

**The strongest departures are state transport for named structures, representation-dependent algebra interfaces, and order operations that bypass their mathematical maps.** Explicit products, projections, functor images, and coherence maps are useful mathematical content. Their length is not a defect.

This review examines existing implementations. [The remediation assessment](remediation-assessment.md) gives the broader dependency order. The findings below distinguish confirmed framework accommodations from local implementation choices; source complexity alone cannot establish that the framework forced a choice.

## The distinction to preserve

A mathematical audit should identify each value's domain, each arrow's endpoints, and the equation justifying each construction. A change of mathematical object needs its declared map. A change of coordinates needs its representation map. Those are different obligations.

In particular, these operations have legitimate mathematical meaning:

- Applying a forgetful functor on objects, morphisms, or the induced point categories.
- Forming an ordered pair through the selected product and then applying a specified universal map.
- Constructing a morphism in a fixed hom category, with its actual source and target.
- Reading components of an indexed family through its retained projections.
- Applying an associator or unitor to make a composition well typed.
- Passing from a carrier point to the corresponding structured point through a retained comparison.

A raw-data round trip needs a different assessment. Inside an engine adapter, converting an element to Smith coordinates and reconstructing its image is proper computation. Inside the formula defining a functor, the same round trip can hide which mathematical map acts. Replacing it with a short wrapper does not expose that map.

The useful question for a line is: **does its justification use a definition, a map, an equation, or a documented representation invariant?** A line justified only by constructor order, a shared attribute name, or the location of a cache belongs to runtime implementation.

## 1. Named structures carry state that compensates for inherited family access

**Location:** [NamedFamilyData and its construction](https://github.com/dzackgarza/sage-categories/blob/7b712e2488af1794c2815be658fb893f178d46c8/src/sage_categories/cat/structured_objects.py#L516-L553); [the named operation initializers](https://github.com/dzackgarza/sage-categories/blob/7b712e2488af1794c2815be658fb893f178d46c8/src/sage_categories/cat/structured_objects.py#L629-L744).

`NamedFamilyData` stores both a family rule and `neutral`, computed as that rule's zeroth component. The additive and multiplicative declarations copy `neutral` into distinct attributes such as `_additive_magma` and `_multiplicative_magma`. Their operations then read those attributes.

The mathematical data is the selected object of the named copy, together with its projection to the neutral structure. The additional state exists so that an inherited method reads the correct level of a nested family. This purpose is explicit in the implementation and in [the introducing change](https://github.com/dzackgarza/sage-categories/commit/f382015).

Storing a defining structure map or its owner in a local field is ordinary mathematical representation. The extra burden here is maintaining both the family representation and separate snapshots of its components to accommodate inherited execution.

The immediate generic boundary is [LimitCategory's family access](https://github.com/dzackgarza/sage-categories/blob/7b712e2488af1794c2815be658fb893f178d46c8/src/sage_categories/cat/cat_constructions.py#L133-L167): it reads `self._rule`, `self._shape`, and the current category. [Retained projections](https://github.com/dzackgarza/sage-categories/blob/7b712e2488af1794c2815be658fb893f178d46c8/src/sage_categories/cat/cat_constructions.py#L451-L471) call that same method. A mathematician cannot infer which inherited family is meant from those fields alone.

**Remedy:** retain the selected functor images and the state of their declarations at the generic inheritance boundary. The operation's definition can then explicitly apply the projection belonging to its named copy. The distinction between the additive and multiplicative projections remains mathematical data. Copy-specific initializer bookkeeping should not be required to make those projections usable.

This is a confirmed accommodation for inherited execution. It is not a finding that every stored structure map is redundant, nor does it establish a current wrong answer from these particular accessors.

## 2. Tensor consumers cross through untyped data instead of their declared maps

**Location:** [tensor morphisms](https://github.com/dzackgarza/sage-categories/blob/7b712e2488af1794c2815be658fb893f178d46c8/src/sage_categories/algebra/abelian.py#L492-L501), [relative tensor morphisms](https://github.com/dzackgarza/sage-categories/blob/7b712e2488af1794c2815be658fb893f178d46c8/src/sage_categories/algebra/abelian.py#L683-L700), and [the mediator interface](https://github.com/dzackgarza/sage-categories/blob/7b712e2488af1794c2815be658fb893f178d46c8/src/sage_categories/algebra/abelian.py#L465-L489).

The relative tensor morphism defines:

```python
apply = lambda arrow, datum: arrow(arrow.domain().point(datum)).datum()
```

It then passes another data callback to the mediator. The absolute tensor morphism performs the same conversion inline. These callbacks accept `Hashable`; their signatures do not distinguish a point of the source group from a point of its carrier or an engine element.

The mathematical definition is already available:

\[
h\circ q_{X,Y}=q_{X',Y'}\circ(f\otimes g).
\]

This equation determines the induced morphism through a coequalizer presentation. Its definition can use the actual tensor image of the pair of morphisms and the actual mediator. The present implementation instead requires knowledge of the point constructor, the raw-data representation, and the callback convention of another local function.

**Remedy:** make the universal construction consume its owned diagram and compatible morphism. Keep matrix evaluation behind that operation. Where a biadditive map is the input, identify its underlying set map and its two additivity hypotheses. Generator assignments and total biadditive maps have different mathematical domains and should have corresponding construction interfaces.

[Mathlib's TensorProduct.lift](https://leanprover-community.github.io/mathlib4_docs/Mathlib/LinearAlgebra/TensorProduct/Basic.html#TensorProduct.lift) gives a precise reference: the input carries the linearity structure, and `lift.tmul` states the factorization equation. This separates the universal map's mathematical domain from its evaluation algorithm.

The current `tensor_mediator` reads a callback on generator pairs and constructs the resulting linear map. A finite exercise exposes the boundary: on A=Z/4, supply a rule that is 1 at (2,2) and zero elsewhere. The function returns the zero homomorphism, whose value on the tensor of that pair differs from the supplied rule.

That rule is not biadditive, so this is **not** a counterexample under the method's stated mathematical precondition. It establishes that callback admission does not prove that precondition. Similarly, the samples in `abelian_homomorphism` can refute agreement with a linear extension but cannot establish agreement on the whole domain. A review must keep the caller's hypothesis separate from what these checks establish.

### A point comparison is not the same problem

[simple_tensor](https://github.com/dzackgarza/sage-categories/blob/7b712e2488af1794c2815be658fb893f178d46c8/src/sage_categories/algebra/abelian.py#L447-L462) uses the tensor object's `object_at` realization after applying the universal biadditive map. That change of point ownership has mathematical meaning. A leaf can state those steps explicitly. The defect is requiring consumers to implement the comparison by extracting a datum and guessing the constructor that restores its ownership.

The [earlier consumer change](https://github.com/dzackgarza/sage-categories/commit/cd81063) records this exact pressure. A convenience function alone does not establish that the generic point comparison works throughout the category framework.

## 3. The set layer maintains additive representations for algebra leaves

**Location:** [ObjectForm](https://github.com/dzackgarza/sage-categories/blob/7b712e2488af1794c2815be658fb893f178d46c8/src/sage_categories/sets/finite.py#L101-L135), [constant maps and registration](https://github.com/dzackgarza/sage-categories/blob/7b712e2488af1794c2815be658fb893f178d46c8/src/sage_categories/sets/finite.py#L502-L527), [products](https://github.com/dzackgarza/sage-categories/blob/7b712e2488af1794c2815be658fb893f178d46c8/src/sage_categories/sets/finite.py#L608-L665), and [abelian-group construction](https://github.com/dzackgarza/sage-categories/blob/7b712e2488af1794c2815be658fb893f178d46c8/src/sage_categories/algebra/abelian.py#L245-L262).

An abelian carrier registers a `Presentation` in Sets. General set operations then propagate direct sums, zero maps, matrix projections, and matrix pairings. `linear_form` retrieves the resulting algebraic matrix by passing through the underlying set map.

There is sound mathematics behind preserving these computations: the forgetful functor carries homomorphisms to set maps, and finite biproducts give the corresponding underlying products. But the implementation requires the algebra leaf to participate in a second representation protocol owned by Sets. A reader must follow both the categorical diagram and the side registry to know how its equations are decided.

**Remedy:** let the additive owner supply the biproduct and matrix calculations. Let the declared forgetful functor carry the resulting objects and maps to Sets, including the computational information needed there. A private set-map evaluator can retain an engine representation; the general set interface should not require a distinguished zero or select a direct-sum implementation from its first factor.

The matrix calculations in `Presentation` and `LinearForm` are suitable private engine work. Moving their mathematical decisions into raw set-map dispatch is the ownership problem.

## 4. Outer actions and associators expose quotient representatives

**Location:** [the abelian associator](https://github.com/dzackgarza/sage-categories/blob/7b712e2488af1794c2815be658fb893f178d46c8/src/sage_categories/algebra/abelian.py#L504-L532), [quotient lifts and induced actions](https://github.com/dzackgarza/sage-categories/blob/7b712e2488af1794c2815be658fb893f178d46c8/src/sage_categories/algebra/abelian.py#L619-L680).

`_rebracket` reads `t.lift()`, generator positions, and coordinate coefficients while defining an associator component. The induced outer actions call `coequalizer_lift`, apply an action to the selected representative, then extract another datum.

Choosing representatives is a legitimate quotient algorithm. Its mathematical obligations include independence of the choice. The problem is that the construction of the outer action depends directly on this particular algorithm and on `_quotient_covers`. The caller must understand the free cover and the Smith-generator convention to audit a formula about bimodules.

For q:X⊗Y→Q, the left action should be the unique morphism \(\bar\lambda:R\otimes Q\to Q\) satisfying

\[
\bar\lambda\circ(1_R\otimes q)
=q\circ(\lambda_X\otimes1_Y)\circ a^{-1}_{R,X,Y}.
\]

The preservation of the balancing coequalizer by R⊗− supplies this descent. The commuting action law supplies compatibility. Both facts belong in the construction. A private evaluator may use the current coordinate lifts to calculate its values.

For the associator, retain the universal trilinear comparison and derive each map by the tensor universal properties. The coordinate calculation can implement that comparison privately.

**Owner:** the selected tensor presentation and Cat's universal-map operations, with a private abelian engine. The existing code shows the representation coupling; it does not prove that every such coupling was forced by a kernel failure.

## 5. Order code recovers mathematical data from representations

### Recovering the carrier from all presentations of a square

**Location:** [_square_factor and the relation constructor](https://github.com/dzackgarza/sage-categories/blob/7b712e2488af1794c2815be658fb893f178d46c8/src/sage_categories/order/posets.py#L51-L112).

The relation constructor receives a subobject, then searches product diagrams presenting its codomain to recover X. It reads their first factors and requires those factors to be identical.

A binary relation includes the specific datum R↪X×X. Its carrier and selected square are part of that datum. Other presentations of the same apex are irrelevant. Requiring their first factors to agree introduces a condition that the definition of a relation does not contain.

**Remedy:** preserve X and the selected square presentation in the construction. Use its projections when reading related pairs. This is a local loss of defining data combined with the presentation-selection problem in Cat. It does not call for a shorter carrier accessor.

### Applying maps and transporting relations

**Location:** [predicate construction and limit lifting](https://github.com/dzackgarza/sage-categories/blob/7b712e2488af1794c2815be658fb893f178d46c8/src/sage_categories/order/posets.py#L162-L200), [transport](https://github.com/dzackgarza/sage-categories/blob/7b712e2488af1794c2815be658fb893f178d46c8/src/sage_categories/order/posets.py#L202-L230), and [morphism admission](https://github.com/dzackgarza/sage-categories/blob/7b712e2488af1794c2815be658fb893f178d46c8/src/sage_categories/order/posets.py#L248-L260).

`from_predicate` unpacks `pair.datum()` and reconstructs two points. `lift_order` reconstructs factor points from the data returned by its cone legs. `construct_morphism` calls another category's private `_action` and constructs a table of raw images. `transport` builds its own inverse table and reverse map.

The corresponding mathematics uses the square's two projections, the cone legs, the underlying morphism, and the supplied isomorphism's inverse. These operations already have mathematical owners. The order definition should use them explicitly.

The finite relation checks themselves are straightforward mathematics: reflexivity, antisymmetry, transitivity, and relation preservation. Their loops can remain in a finite computation helper. Raw labels are appropriate there if the helper owns their conversion. They are an unnecessary dependency in the generic relation definition.

There is also a concrete lower-layer restriction: [SetSubobjects.from_predicate](https://github.com/dzackgarza/sage-categories/blob/7b712e2488af1794c2815be658fb893f178d46c8/src/sage_categories/sets/finite.py#L786-L796) enumerates the ambient set, and `lift_order` requires `shape.labels()`. The general relation and limit constructions therefore inherit finite-presentation requirements from their current implementations. Fix that restriction at Sets and the indexed-construction owner; retain the finite evaluator for its proper domain. These findings refine the current scope of issues [#9](https://github.com/dzackgarza/sage-categories/issues/9) and [#30](https://github.com/dzackgarza/sage-categories/issues/30).

## 6. Unit comparisons return pairs because retained inverses fail

**Location:** [_unitor and relative unit comparisons](https://github.com/dzackgarza/sage-categories/blob/7b712e2488af1794c2815be658fb893f178d46c8/src/sage_categories/algebra/abelian.py#L708-L744).

The code constructs both directions, checks both inverse equations, and returns a tuple. Constructing and checking both maps is proper mathematics. The engineering accommodation is that callers must manage the pair because the standard retained inverse operation fails.

This cause is recorded in [the implementing change](https://github.com/dzackgarza/sage-categories/commit/7b712e2) and has the concrete public failure in [issue #33](https://github.com/dzackgarza/sage-categories/issues/33). Repair the morphism owner and retain the isomorphism with its inverse. Preserve the inverse equations and the explicit unit maps.

## 7. Mathematical typing exposes defects that concise notation would hide

### Transport in a general actegory uses the wrong category

**Location:** [ModuleCategory.transport](https://github.com/dzackgarza/sage-categories/blob/7b712e2488af1794c2815be658fb893f178d46c8/src/sage_categories/cat/modules.py#L110-L116).

For an action \(\mathcal M\times\mathcal C\to\mathcal C\), a scalar object A belongs to \(\mathcal M\). The transport formula needs \(1_A\) in \(\mathcal M\). The method instead constructs it through `self.underlying_category().morphism_category(1)`, which is Mor(\(\mathcal C\)).

The formula in the docstring is correct. The code is well typed only in special cases where the scalar also has the required placement in \(\mathcal C\), including self-actions. The constructor `Modules` already uses the acting monoidal category for `identity_scalar`, which identifies the intended owner.

This is a source-derived domain error, not a reproduced failure of a general-actegory consumer. Its repair belongs to Modules under the general-action obligation. Keep the explicit identity morphism and correct its category.

### The declared abelian tensor rejects its unit tensored with itself

**Location:** [_tensor_object](https://github.com/dzackgarza/sage-categories/blob/7b712e2488af1794c2815be658fb893f178d46c8/src/sage_categories/algebra/abelian.py#L425-L431).

The function requires its quotient engine to be finite. A direct public evaluation at (Z,Z) raises that assertion:

```python
from sage_categories.algebra import AbelianTensor, integer_group

V = AbelianTensor()
Z = integer_group()
V.tensor().on_object(V.tensor().domain()((Z, Z)))
```

Z⊗Z is Z, and Z is the declared monoidal unit. The selected structure therefore fails on its own unit. This is a valid-input counterexample to the declared monoidal interface, within the foundational obligation in [issue #4](https://github.com/dzackgarza/sage-categories/issues/4).

The constructor immediately below the assertion uses a membership-defined carrier, and the tensor presentation uses finite matrices even for free summands. Repair the complete finitely presented tensor operation, including its maps and unit components. An enumeration constraint must not determine the domain of the mathematical tensor functor.

## Existing code that retains the right kind of explicitness

These definitions are useful models for the repaired leaves. This is an assessment of their mathematical expression, not certification of every dependency they execute.

| Source | Why its explicit steps are useful |
| --- | --- |
| [Module laws](https://github.com/dzackgarza/sage-categories/blob/7b712e2488af1794c2815be658fb893f178d46c8/src/sage_categories/cat/modules.py#L138-L175) | The two action composites, unit comparison, natural transformations, and equifiers state the definition with its endpoints. |
| [Bimodule commuting law](https://github.com/dzackgarza/sage-categories/blob/7b712e2488af1794c2815be658fb893f178d46c8/src/sage_categories/cat/bimodules.py#L177-L209) | The pullback identifies the carrier; the equifier compares the two correctly bracketed actions. |
| [Semiring distributivity](https://github.com/dzackgarza/sage-categories/blob/7b712e2488af1794c2815be658fb893f178d46c8/src/sage_categories/cat/structured_objects.py#L928-L952) | Projections explicitly select the three variables. Pairings and compositions express each side of distributivity and absorption. |
| [Group inversion from the shear map](https://github.com/dzackgarza/sage-categories/blob/7b712e2488af1794c2815be658fb893f178d46c8/src/sage_categories/cat/structured_objects.py#L420-L430) | The identity, unit map, pairing, inverse, and projection derive inversion from the group structure. |
| [Cartesian associator](https://github.com/dzackgarza/sage-categories/blob/7b712e2488af1794c2815be658fb893f178d46c8/src/sage_categories/cat/monoidal.py#L133-L155) | It changes bracketing through product projections and the universal pairing, without inspecting tuple storage. |
| [The Thin functor](https://github.com/dzackgarza/sage-categories/blob/7b712e2488af1794c2815be658fb893f178d46c8/src/sage_categories/order/posets.py#L336-L354) | A monotone map sends each object to its image and each comparison to the corresponding comparison. Both actions are present. |

Likewise, `_points` and `_point_map` in the abelian leaf apply a chain of actual forgetful functors. The nested applications describe structure being forgotten. Their existence is not evidence of an engineering defect. The relevant question is whether the functors and their endpoints remain explicit and correct.

Assembling compatible object or morphism families in `RingCategory` and `ActionPairsCategory` is also mathematical construction data. A tuple can represent that family faithfully. It becomes problematic when a later operation guesses which family an inherited field contains, or reconstructs the defining diagram from incidental storage.

## Repair boundary

The review identifies three distinct responsibilities:

1. **Generic framework repair:** retain declaration-specific state and selected images, preserve point comparisons and inverses, and retain universal presentations. Named structures and unit comparisons provide existing consumers.
2. **Leaf mathematics:** state relations, actions, and induced morphisms through those maps; retain exact scalar categories and construction parameters.
3. **Private computation:** keep Smith coordinates, quotient representatives, symbolic normalization, and finite relation tables together with their conversion invariants.

The target is a leaf definition whose mathematical dependencies remain visible after every repair. The engine can execute that definition through coordinates. The leaf should not have to recover the definition from the engine's coordinates or from the runtime's state.

## Coverage and limits

The review read the complete current `sets/finite.py`, `sets/_finite.py`, `order/posets.py`, and `algebra/abelian.py`, with their package exports. It also read the algebraic definitions in `cat/structured_objects.py`, `cat/modules.py`, `cat/bimodules.py`, and `cat/monoidal.py`, and the immediate family, projection, and point-construction owners cited above. These generic definitions matter because they are the substrate used by the current leaves.

The tensor-unit failure and the callback-boundary example were exercised with `sage -c`. Historical commits establish the stated motivation for the named-state and inverse-pair accommodations; they do not establish correctness. No claim is made here that every observed conversion was unavoidable, or that the proposed generic repairs already exist.
