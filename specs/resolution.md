# Resolution of structural-functor diamonds

This specification records the architectural decision for diamonds in the selected structural-functor graph.
It preserves the discussion that established the decision.

This is a forward requirement.
It does not claim that the current implementation satisfies the requirement.

## Contents

- [Question](#question)

- [What Sage resolves](#what-sage-resolves)

- [Why this framework has a stronger obligation](#why-this-framework-has-a-stronger-obligation)

- [The first proposed resolution](#the-first-proposed-resolution)

- [Preserve both branches](#preserve-both-branches)

- [Ring objects as the basic diamond](#ring-objects-as-the-basic-diamond)

- [Products in modules](#products-in-modules)

- [Finite-rank free modules over finite fields](#finite-rank-free-modules-over-finite-fields)

- [The actual product and coproduct boundary](#the-actual-product-and-coproduct-boundary)

- [Several presentations of one construction](#several-presentations-of-one-construction)

- [Method-name collisions](#method-name-collisions)

- [Strict equality and natural isomorphism](#strict-equality-and-natural-isomorphism)

- [Final decision](#final-decision)

- [Acceptance examples](#acceptance-examples)

## Question

The discussion began with this question:

> We potentially have diamond issues.
> Sage supercategories presumably have them too.
> How does this framework handle them, and how does Sage handle them?
> Does our use case introduce problems that Sage does not have?
> Does implicit coherence matter?
> Can an assumption of coherence be harmful or false?

A structural diamond has the form

\[
D\longrightarrow B\longrightarrow A,
\qquad
D\longrightarrow C\longrightarrow A.
\]

An object of \(D\) has structure inherited through both \(B\) and \(C\). Both paths also reach \(A\).

There are three separate questions:

1. Which methods introduced by \(B\) and \(C\) reach the public object?

2. Which route supplies a method owned by the common category \(A\)?

3. Do both routes construct the same object, elements, morphisms, and universal data in \(A\)?

These questions must not be combined into one method-resolution rule.

## What Sage resolves

Sage builds parent, element, and morphism method classes from its category graph.
It uses a controlled C3 method-resolution order for diamonds.

Sage requires two incomparable supercategories with the same method name to give that name the same mathematical meaning.
Their order is then an implementation detail.
A common subcategory can override the method when one implementation is preferable.

Sage documents `FiniteCoxeterGroups.some_elements()` as such a choice.
The finite Coxeter group category selects the Coxeter implementation instead of the generic finite-group implementation.
This is an algorithm choice.
It does not change the meaning of `some_elements()`.

The relevant Sage documentation is:

- [Category framework](https://doc.sagemath.org/html/en/reference/categories/sage/categories/category.html)

- [Order of supercategories](https://doc.sagemath.org/html/en/reference/categories/sage/categories/primer.html#on-the-order-of-super-categories)

- [Finite Coxeter groups](https://doc.sagemath.org/html/en/reference/categories/sage/categories/finite_coxeter_groups.html)

Sage therefore resolves a Python method hierarchy.
Its controlled order ensures that parents and elements use a consistent method-resolution order.

## Why this framework has a stronger obligation

This framework compiles more than methods.
A selected functor supplies:

- objects;

- elements;

- morphisms;

- the construction-input conversion for each state-bearing target class;

- the target implementation methods;

- the morphisms in universal constructions.

Each named functor owns its public images.
The compiler keeps only the constructor data needed to initialize each reachable class on the structured source instance.

Two implementations can be mathematically isomorphic without being the same chosen implementation.
A tuple product and a vector-space product are a simple example.
Their elements can use different parents.
Their projections can have different exact domains.

Thus, method order alone is insufficient.
All selected paths to one target class must supply the same exact constructor datum.
This requirement does not identify the public images of different functors.

## The first proposed resolution

The first proposed practical rule was:

> Force a leaf to hand-pick a resolution through each diamond.
> The principal purpose is to manage a catalogue of algorithms and methods by categorical placement.
> For a product in `Modules(A, C)`, it is normally enough to select one implementation that has the expected factors, projections or injections, mediating morphisms, and factoring maps.

This remains valid for a genuine choice of presentation or algorithm.
It is not valid as a rule that discards an entire branch of the category graph.

A category can make a small mathematical declaration that selects one presentation: one
apex together with its universal data.
The kernel must execute that declaration.
The leaf must not traverse routes, move values, manage caches, or install methods.

A diamond needs no coherence machinery. The condition is equality of the two composites,
checked by identity of the constructor data they supply, and a failure is a defect in the
construction rather than a case for a comparison isomorphism. A public object that would
have to expose operations from two nonidentical presentations at once has not chosen its
presentation; choosing is the fix.

## Preserve both branches

The discussion then added this important concern:

> Diamonds could genuinely introduce more functionality on one route than another.

That concern changes the rule.
A leaf can select a route to a common ancestor.
It must not select one whole branch and discard the other.

For

\[
D\longrightarrow B\longrightarrow A,
\qquad
D\longrightarrow C\longrightarrow A,
\]

the compiler applies this ownership rule:

| Method owner | Public resolution |
| --- | --- |
| \(D\) | Use the local declaration. |
| \(B\) | Use the route \(D\to B\). |
| \(C\) | Use the route \(D\to C\). |
| \(A\) | Both routes supply the same \(A\) constructor datum; the compiler initializes \(A\)'s class once. |
| Both \(B\) and \(C\) under one name | Require a mathematical resolution or reject compilation. |

The public surface is the union of both branches.
Route resolution applies only to duplicate access to a common owner.

This distinction separates two different facts:

- a route can pass through an intermediate category that introduces new operations;

- two routes can later reach the same category that owns one operation.

The compiler preserves the intermediate operations.
It deduplicates only the operation from the shared owner.

## Ring objects as the basic diamond

Let \(\mathcal C\) be a category with finite products.
Write \(\mathcal C_\times\) for its specified cartesian monoidal structure.
A ring object gives the clearest mathematical example:

\[
\operatorname{Rings}(\mathcal C)\longrightarrow
\begin{cases}
\operatorname{Semirings}(\mathcal C),\\
\operatorname{Groups}(\mathcal C_\times).\operatorname{Additive}().
  \operatorname{Commutative}()
\end{cases}
\longrightarrow\mathcal C.
\]

The semiring branch supplies addition, multiplication, zero, and one.
The group branch supplies additive inverses and subtraction.
A ring must receive both catalogues.

Both branches reach the same additive monoid and the same object of \(\mathcal C\).
Their selected paths must supply the same constructor datum for the inherited
\(\mathcal C\) class. The compiler can then initialize that class once on the ring
instance. The two composite functors keep their independent public actions and images.

For \(\mathcal C=\operatorname{Sets}()\), both paths supply the set from which the ring
was constructed. Membership and other set-owned methods occur once in the compiled MRO
and read the initialized set state on the ring instance.
Sage's documented diamond is this specialization.
The final category receives the methods introduced on every branch.
C3 only resolves a shared method name.

This is the correct general model for structural inheritance in this framework:

- take the union of branch-owned mathematics;

- resolve duplicate routes to a shared owner;

- reject an independent semantic collision.

## Products in modules

Let \((\mathcal M,\odot,1)\) be monoidal, let \(\mathcal C\) be an \(\mathcal M\)-actegory with action \(\bullet\), and let \(A\in\operatorname{Monoids}(\mathcal M)\). An object of `Modules(A, C)` is an object \(X\in\mathcal C\) with an action

\[
\rho:A\mathbin{\bullet}X\longrightarrow X
\]

that satisfies the unit and action diagrams.
When closed or enriched structure represents these actions by an internal endomorphism monoid, this data is equivalently a monoid morphism \(A\to\operatorname{End}_{\mathcal C}(X)\).

Assume that `Modules(A, C)` has the selected products below, and that its selected functor
to \(\mathcal C\) carries the chosen product to the chosen product on the nose.
That is stronger than preservation of products. A functor `U` preserves a product when the
canonical comparison morphism `U(prod X_i) -> prod U(X_i)`, induced by the cone
`(U(pi_i))`, is an isomorphism. The kernel needs that comparison to be the identity,
because sameness here is identity and never isomorphism.
It is the identity by construction rather than by theorem: the module product is lifted
from the ambient product, so its apex is the ambient apex and its projections are the
ambient projections carrying the induced action.
For a family \((X_i)_{i\in I}\) in this category, a product contains:

- the module apex \(P\);

- module morphisms \(\pi_i:P\to X_i\);

- the module mediating morphism;

- the induced \(A\)-action on \(P\);

- its complete product universal property.

Let the module presentation select a functor

\[
U:\operatorname{Modules}(A,\mathcal C)\longrightarrow\mathcal C.
\]

The \(\mathcal C\)-image of the module product is then literally the product of the
\(\mathcal C\)-images:

\[
U\!\left(\prod_i X_i\right)
=
\prod_i U(X_i),
\]

with equality rather than a comparison isomorphism, because the module construction was
built on that ambient product.

The module branch supplies the action and module universal morphisms.
The \(\mathcal C\)-branch supplies the capabilities owned by \(\mathcal C\). When \(\mathcal C=\operatorname{Sets}()\), these include membership, elements, iteration when available, and cardinality.
These are compatible capabilities.
They are not competing product implementations.

The module product must select one complete presentation.
Its apex, action, projections, mediating morphisms, and \(\mathcal C\)-image must belong to that presentation.
The implementation must not combine an apex with universal data from another merely isomorphic presentation.

If a specialized vector realization and a tuple realization are both useful, one is the chosen public presentation.
The other remains an explicit realization functor or an explicit isomorphic presentation.
It does not become a second structural identity.

## Finite-rank free modules over finite fields

This example takes the ambient to be `Sets()`. Let

\[
\mathcal C=
\operatorname{Groups}(\operatorname{Sets}_\times()).
\operatorname{Additive}().\operatorname{Commutative}()
\]

with its tensor product, and regard \(\mathbf F_p\) as a commutative monoid object of \(\mathcal C\). The category `Modules(F_p, C)` is the ordinary category of \(\mathbf F_p\)-modules.
Its selected route

\[
U:\operatorname{Modules}(\mathbf F_p,\mathcal C)
\longrightarrow\mathcal C
\longrightarrow\operatorname{Sets}
\]

is the ordinary underlying-set functor.
The module structure places \(\mathbf F_p^n\) in a product construction in `Modules(F_p, C)`. Taking the same product in `Rings` supplies the componentwise product-ring structure,
since a product of rings is a ring. Which structure the object has follows from where its
product was taken, not from what the construction happened to keep.

For the explicitly chosen product module

\[
M=\prod_{i=1}^{n}\mathbf F_p,
\]

the selected functor gives

\[
U(M)=\prod_{i=1}^{n}U(\mathbf F_p).
\]

Each factor is finite.
The index set is finite.
Hence the resulting set is finite.
The two relevant paths are

\[
M\longrightarrow\operatorname{Modules}(\mathbf F_p,\mathcal C)
\longrightarrow\mathcal C
\longrightarrow\operatorname{Sets},
\]

and

\[
M\longrightarrow\operatorname{FiniteSets}
\longrightarrow\operatorname{Sets}.
\]

Both paths supply the same underlying-set constructor datum.
The module placement supplies linear operations.
The finite-set placement supplies finite cardinality and finite enumeration.
Neither path competes with the other.

A correctly designed kernel derives this placement.
The module leaf contains no route selection code.
The kernel uses these mathematical facts:

- the selected composite functor from `Modules(F_p, C)` to `Sets()` carries the chosen
  product to the chosen set product on the nose;

- a finite product of finite sets is finite;

- both paths supply one set constructor datum;

- methods from both category placements belong on the public object.

There is a further distinction between a product module and an abstract finite-dimensional vector space.
A vector space without a chosen basis has no canonical isomorphism with \(\mathbf F_p^n\). It is still finite by the theorem

\[
\#M=p^{\dim_{\mathbf F_p}M}.
\]

The theorem establishes its placement in finite sets.
The runtime does not need to choose a basis or enumerate its elements to establish finiteness.

Likewise, the tuple realization does not create a ring structure on an abstract module.
The ring placement is valid only when componentwise multiplication or another ring structure is part of the object's mathematical data.

This example therefore supports automatic kernel resolution.
It does not justify a leaf-level route choice.

## The actual product and coproduct boundary

The ordinary set-based module category gives a concrete boundary.
Let \(\mathcal C=\operatorname{Groups}(\operatorname{Sets}_\times()). \operatorname{Additive}().\operatorname{Commutative}()\), let \(R\) be a ring object, and use the selected composite functor

\[
U:\operatorname{Modules}(R,\mathcal C)
\longrightarrow\mathcal C
\longrightarrow\operatorname{Sets}.
\]

Finite products and finite coproducts agree in this additive module category.
Their common object is a biproduct:

\[
M\oplus N.
\]

After applying the selected functor to sets,

\[
U(M\oplus N)=U(M)\times U(N).
\]

This set is not the set coproduct

\[
U(M)\sqcup U(N).
\]

The selected composite functor to `Sets()` carries the chosen module product to the
chosen set product on the nose.
It does not preserve module coproducts as set coproducts.

Therefore, the compiler must not assume that every selected functor preserves every universal construction.
Construction preservation is separate mathematical data.
A functor can preserve limits without preserving colimits.

This is not a reason for leaf wiring.
A construction states each preservation or lift fact at that construction.
The compiler has no general preservation registry.

## Several presentations of one construction

Suppose a product in modules has two available realizations:

1. a tuple realization with componentwise operations;

2. a specialized Sage vector or free-module realization.

They can be canonically isomorphic without being identical Python parents.
Either can implement the module product.
The category selects one complete public presentation.

The choice includes:

- the apex;

- its elements and their ambient object;

- all projections;

- all injections when the product is also used as a finite biproduct;

- mediating and factoring morphisms;

- the image under every selected functor.

This choice does not remove algorithms associated with another category branch.
It only selects the representation of one mathematical construction.

An alternate realization remains available through an ordinary functor or explicit isomorphism.
It does not contribute methods through structural inheritance unless the category declares it as the selected structural realization.

General non-strict coherence is needed only if the public object must accept methods and universal morphisms from both nonidentical presentations transparently.
The present goal of managing a mathematical algorithm catalogue does not require that behavior.

## Method-name collisions

The compiler distinguishes two kinds of duplicate names.

### One declaration reached twice

If a method is owned by \(A\) and both branches reach \(A\), there is one mathematical declaration.
The compiled class contains the \(A\) class once in its Python MRO. Construction checks that both paths supply the same \(A\) constructor datum.
Method compilation installs no route wrapper.

Membership on a ring object in `Sets()` is such a case.
Both the additive and multiplicative branches reach the same object of `Sets()`. That category remains the sole owner of membership.

### Independent declarations with one spelling

If incomparable categories independently introduce the same spelling, route order is not a mathematical resolution.
The leaf must either provide the exact common operation or the API must use distinct names.

For example, `gens()` can mean group generators, module generators, or algebra generators.
These are different mathematical sets.
Use names such as `group_generators()`, `module_generators()`, and `algebra_generators()`.

When both declarations have the same meaning but different algorithms, the common subcategory can select the preferred algorithm.
Sage's `FiniteCoxeterGroups.some_elements()` is the grounding example.

The compiler must not use arbitrary route order to decide a semantic collision.

## Constructor agreement and functor images

Each named functor constructs and caches its own public images.
Two functors with the same endpoints can return different objects.
Selection in `structure_functors()` does not change this mathematical action.

An inherited method does not run on a public functor image.
It runs on the structured source instance after the selected conversions initialize every target class in its MRO.

When two selected paths reach one target class, they must supply the same exact constructor datum for that class.
The kernel compares those data during source construction and raises a construction-defect error on disagreement.
It names both paths and the common target class.

This check does not compare, merge, or replace public functor images.
A natural isomorphism between two images also does not identify their constructor data.
If two presentations require different target state, the category selects one presentation or declares a separate mathematical resolution.

## Final decision

The architecture uses the following rules.

1. Functors selected by `structure_functors()` form the complete inheritance graph.

2. The compiler collects methods from every reachable branch.

3. A branch-specific method remains available on every structural descendant.

4. Two selected paths to the same target class supply one exact constructor datum.

5. Repeated selected paths to one target class resolve from their constructor-data
   agreement.

6. A category-owned method reads its initialized state on the structured source instance through direct Python MRO.

7. A genuine presentation or algorithm choice is a small mathematical declaration by the category that owns the choice.
   The kernel executes it.

8. A choice of presentation includes objects, elements, morphisms, and universal data.
   It cannot mix data from different presentations.

9. Independent method declarations with different meanings require distinct names or an explicit mathematical operation at the common descendant.

10. Method-resolution order never decides mathematical meaning.

11. Each written class contains its local members and receives the classes of every selected target in controlled C3 order.
    `C.ObjectType` also inherits `Cat().ElementType`, which models points `* -> C`.
    `C.MorphismType` is `Mor(C).ObjectType`.
    `C.ElementType` models points `1_C -> X` and does not share the `Cat().ElementType` base for that reason.

12. Each selected functor converts complete typed construction data for its target classes, and every reachable class and common ancestor is initialized exactly once.
    The object context supplies the point `* -> C`; the element context supplies the point `1_C -> X`.
    Allocation and initialization order are implementation choices (`POL-DOC-017`).

13. Each named functor owns and caches its public images.
    Different functors with the same endpoints remain independent.

14. During source construction, the compiler compares the target constructor data from all selected paths to one class.
    A mismatch raises a construction-defect error naming both paths and the target class.

15. The compiler never identifies public functor images or proves naturality.
    Natural transformations remain trusted mathematical constructions.

16. A functor enters `structure_functors()` only when its conversions are coherent with every other selected path to the same target class.

The short form is:

> Preserve every branch.
> Initialize every class once.
> Resolve only duplicate access to a common owner.
> Constructor data agree by construction.
> Ask a category for a choice only when the mathematics contains a real choice.

## Acceptance examples

The resolution design must support these examples.

### Ring inheritance

A ring object in `Sets()` receives additive-group operations and multiplicative-monoid operations.
Both paths supply one underlying-set constructor datum.
Set membership has one owner and one public implementation.

### Finite vector spaces

A finite-dimensional vector space over \(\mathbf F_p\) belongs to finite sets by its construction theorem.
It receives both module operations and finite-set operations.
It does not enumerate its \(p^n\) elements to establish finiteness.

### Module products

A product in `Modules(A, C)` retains its module apex, action, projections, and mediating morphism.
When the selected functor to \(\mathcal C\) carries the chosen product to the chosen
product on the nose, its \(\mathcal C\)-image is that chosen product.
At the ambient `Sets()`, the composite underlying-set image is the set product.

### Module coproducts

At the ambient `Sets()`, the underlying set of a module coproduct is not identified with the set coproduct.
A construction supplies each required lift or equality. The compiler infers neither.

### Algorithm selection

When two inherited methods have the same meaning but different algorithms, the common category can select one implementation.
The selection does not remove other methods from either branch.

### Semantic collision

When two branches use one spelling for different mathematics, compilation rejects the ambiguity or the public API gives the operations distinct mathematical names.

### Nonidentical presentations

When two routes would yield merely isomorphic product presentations, projections and elements from one presentation are not attached to the other apex.
One complete presentation is canonical and selected; the other remains an ordinary functor or an explicit isomorphism and is never a selected route.
