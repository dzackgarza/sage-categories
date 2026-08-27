# Resolution of structural-functor diamonds

This specification records the architectural decision for diamonds in the selected
structural-functor graph. It preserves the discussion that established the decision.

This is a forward requirement. It does not claim that the current implementation
satisfies the requirement.

## Contents

- [Question](#question)
- [What Sage resolves](#what-sage-resolves)
- [Why this framework has a stronger obligation](#why-this-framework-has-a-stronger-obligation)
- [The first proposed resolution](#the-first-proposed-resolution)
- [Preserve both branches](#preserve-both-branches)
- [Rings as the basic diamond](#rings-as-the-basic-diamond)
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

> We potentially have diamond issues. Sage supercategories presumably have them too.
> How does this framework handle them, and how does Sage handle them? Does our use case
> introduce problems that Sage does not have? Does implicit coherence matter? Can an
> assumption of coherence be harmful or false?

A structural diamond has the form

\[
D\longrightarrow B\longrightarrow A,
\qquad
D\longrightarrow C\longrightarrow A.
\]

An object of \(D\) has structure inherited through both \(B\) and \(C\). Both paths
also reach \(A\).

There are three separate questions:

1. Which methods introduced by \(B\) and \(C\) reach the public object?
2. Which route supplies a method owned by the common category \(A\)?
3. Do both routes construct the same object, elements, morphisms, and universal data in
   \(A\)?

These questions must not be combined into one method-resolution rule.

## What Sage resolves

Sage builds parent, element, and morphism method classes from its category graph. It
uses a controlled C3 method-resolution order for diamonds.

Sage requires two incomparable supercategories with the same method name to give that
name the same mathematical meaning. Their order is then an implementation detail. A
common subcategory can override the method when one implementation is preferable.

Sage documents `FiniteCoxeterGroups.some_elements()` as such a choice. The finite
Coxeter group category selects the Coxeter implementation instead of the generic
finite-group implementation. This is an algorithm choice. It does not change the
meaning of `some_elements()`.

The relevant Sage documentation is:

- [Category framework](https://doc.sagemath.org/html/en/reference/categories/sage/categories/category.html)
- [Order of supercategories](https://doc.sagemath.org/html/en/reference/categories/sage/categories/primer.html#on-the-order-of-super-categories)
- [Finite Coxeter groups](https://doc.sagemath.org/html/en/reference/categories/sage/categories/finite_coxeter_groups.html)

Sage therefore resolves a Python method hierarchy. Its controlled order ensures that
parents and elements use a consistent method-resolution order.

## Why this framework has a stronger obligation

This framework compiles more than methods. A selected structural functor supplies:

- objects;
- elements;
- morphisms;
- the construction-input conversion for each state-bearing target role;
- the target implementation methods;
- the morphisms in universal constructions.

The compiler also keeps canonical images in reachable categories. Therefore, a route
choice can affect exact parent identity, morphism domains and codomains, element
parents, projections, injections, and mediating morphisms.

Two implementations can be mathematically isomorphic without being the same chosen
implementation. A tuple product and a vector-space product are a simple example. Their
elements can use different parents. Their projections can have different exact domains.

Thus, method order alone is insufficient. A route resolution must select or identify the
complete mathematical image and initialize its role state, not only choose a method body.

Implicit coherence is safe when both routes are strict in this framework. They must
produce the same canonical object, element, and morphism images by identity. It is
unsafe to treat a nonidentity natural isomorphism as literal identity.

## The first proposed resolution

The first proposed practical rule was:

> Force a leaf to hand-pick a resolution through each diamond. The principal purpose is
> to manage a catalogue of algorithms and methods by categorical placement. For a
> product in `Modules(R)`, it is normally enough to select one implementation that has
> the expected factors, projections or inclusions, mediating morphisms, and factoring
> maps.

This remains valid for a genuine choice of presentation or algorithm. It is not valid
as a rule that discards an entire branch of the category graph.

A category can make a small mathematical declaration that selects one coherent
presentation. The kernel must execute that declaration. The leaf must not traverse
routes, move values, manage caches, or install methods.

General higher-coherence machinery is not required only because a diamond exists. It
becomes necessary only if one public object must use several nonidentical presentations
at the same time and transport inherited operations transparently between them.

## Preserve both branches

The discussion then added this important concern:

> Diamonds could genuinely introduce more functionality on one route than another.

That concern changes the rule. A leaf can select a route to a common ancestor. It must
not select one whole branch and discard the other.

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
| \(A\) | Both routes return one canonical \(A\)-image by identity; the compiler initializes \(A\)'s role once. |
| Both \(B\) and \(C\) under one name | Require a mathematical resolution or reject compilation. |

The public surface is the union of both branches. Route resolution applies only to
duplicate access to a common owner.

This distinction separates two different facts:

- a route can pass through an intermediate category that introduces new operations;
- two routes can later reach the same category that owns one operation.

The compiler preserves the intermediate operations. It deduplicates only the operation
from the shared owner.

## Rings as the basic diamond

A ring gives the clearest mathematical example:

\[
\operatorname{Rings}\longrightarrow
\begin{cases}
\operatorname{AdditiveGroups},\\
\operatorname{Monoids}
\end{cases}
\longrightarrow\operatorname{Sets}.
\]

The additive branch supplies addition, zero, and additive inverses. The multiplicative
branch supplies multiplication, one, and powers. A ring must receive both catalogues.

Both branches reach the same underlying set. Membership or another method owned by
sets needs one canonical route to that set. Selecting that route must not remove either
the additive or multiplicative branch.

Sage's documented diamond uses sets, additive groups, multiplicative monoids, and rings
as its model. The final category receives the methods introduced on every branch. C3
only resolves a shared method name.

This is the correct general model for structural inheritance in this framework:

- take the union of branch-owned mathematics;
- resolve duplicate routes to a shared owner;
- reject an independent semantic collision.

## Products in modules

For a family \((M_i)_{i\in I}\) in \(\operatorname{Modules}(R)\), a chosen product
contains:

- the module apex \(P\);
- linear projections \(\pi_i:P\to M_i\);
- the linear mediating morphism;
- componentwise addition and scalar multiplication;
- its complete product universal property.

Let the module presentation select a structural functor

\[
U:\operatorname{Modules}(R)\longrightarrow\operatorname{Sets}
\]

that preserves products. The set image of the module product is the product of the set
images:

\[
U\!\left(\prod_i M_i\right)
=
\prod_i U(M_i),
\]

after the framework chooses compatible product presentations.

The module branch supplies linear structure and linear universal morphisms. The set branch
supplies membership, elements, iteration when available, and cardinality. These are
compatible capabilities. They are not competing product implementations.

The module product must select one complete presentation. Its apex, projections,
elements, mediating morphisms, and set image must belong to that presentation. The
implementation must not take the apex from one presentation and projections or elements
from another merely isomorphic presentation.

If a specialized vector realization and a tuple realization are both useful, one is the
chosen public presentation. The other remains an explicit realization functor or an
explicit isomorphic presentation. It does not become a second structural identity.

## Finite-rank free modules over finite fields

The discussion tested the rule on a finite-rank free module over a finite field:

> Let the object be \(\mathbf F_p^n\). As a module, it reaches a product construction.
> Each factor \(\mathbf F_p\) has underlying finite set
> \(\{0,1,\ldots,p-1\}\). Products of finitely many finite sets are finite. A
> correctly wired kernel should therefore resolve the object naturally into finite
> sets. Is there a real conflict here?

There is no genuine conflict in this example.

One correction is required. As a module, \(\mathbf F_p^n\) is a product in
\(\operatorname{Modules}(\mathbf F_p)\), not a product in rings. Componentwise
multiplication gives \(\mathbf F_p^n\) an additional product-ring structure, but module
structure alone does not include multiplication.

For the explicitly chosen product module

\[
M=\prod_{i=1}^{n}\mathbf F_p,
\]

the selected structural functor gives

\[
U(M)=\prod_{i=1}^{n}U(\mathbf F_p).
\]

Each factor is finite. The index set is finite. Hence the resulting set is finite. The
two relevant paths are

\[
M\longrightarrow\operatorname{Modules}(\mathbf F_p)
\longrightarrow\operatorname{Sets},
\]

and

\[
M\longrightarrow\operatorname{FiniteSets}
\longrightarrow\operatorname{Sets}.
\]

Both paths reach the same canonical underlying set. The module placement supplies
linear operations. The finite-set placement supplies finite cardinality and finite
enumeration. Neither path competes with the other.

A correctly designed kernel derives this placement. The module leaf contains no route
selection code. The kernel uses these mathematical facts:

- the selected module-to-set structural functor preserves products;
- a finite product of finite sets is finite;
- both routes have one canonical set image;
- methods from both category placements belong on the public object.

There is a further distinction between a chosen product module and an abstract
finite-dimensional vector space. A vector space without a chosen basis has no canonical
isomorphism with \(\mathbf F_p^n\). It is still finite by the theorem

\[
\#M=p^{\dim_{\mathbf F_p}M}.
\]

The theorem establishes its placement in finite sets. The runtime does not need to
choose a basis or enumerate its elements to establish finiteness.

Likewise, the tuple realization does not create a ring structure on an abstract module.
The ring placement is valid only when componentwise multiplication or another ring
structure is part of the object's mathematical data.

This example therefore supports automatic kernel resolution. It does not justify a
leaf-level route choice.

## The actual product and coproduct boundary

Modules give a concrete case where an unjustified coherence assumption is false.

Finite products and finite coproducts agree in modules. Their common object is a
biproduct:

\[
M\oplus N.
\]

After applying the selected structural functor to sets,

\[
U(M\oplus N)=U(M)\times U(N).
\]

This set is not the set coproduct

\[
U(M)\sqcup U(N).
\]

The selected module-to-set structural functor preserves products. It does not preserve
module coproducts as set coproducts.

Therefore, the compiler must not assume that every structural functor preserves every
universal construction. Construction preservation is separate mathematical data. A
functor can preserve limits without preserving colimits.

This is not a reason for leaf wiring. A construction states each preservation or lift
fact at that construction. The compiler has no general preservation registry.

## Several presentations of one construction

Suppose a product in modules has two available realizations:

1. a tuple realization with componentwise operations;
2. a specialized Sage vector or free-module realization.

They can be canonically isomorphic without being identical Python parents. Either can
implement the module product. The category selects one complete public presentation.

The choice includes:

- the apex;
- its elements and their ambient object;
- all projections;
- all injections when the product is also used as a finite biproduct;
- mediating and factoring morphisms;
- the image under every selected structural functor.

This choice does not remove algorithms associated with another category branch. It only
selects the representation of one mathematical construction.

An alternate realization remains available through an ordinary functor or explicit
isomorphism. It does not contribute methods through structural inheritance unless the
category declares it as the selected structural realization.

General non-strict coherence is needed only if the public object must accept methods and
universal morphisms from both nonidentical presentations transparently. The present goal of
managing a mathematical algorithm catalogue does not require that behavior.

## Method-name collisions

The compiler distinguishes two kinds of duplicate names.

### One declaration reached twice

If a method is owned by \(A\) and both branches reach \(A\), there is one mathematical
declaration. The compiled role contains the \(A\) node once in its Python MRO. Object
construction checks that both routes give the same canonical \(A\)-image. Method
compilation installs no route wrapper.

Membership on a ring is such a case. Both the additive and multiplicative branches reach
sets. `Sets()` remains the sole owner of membership.

### Independent declarations with one spelling

If incomparable categories independently introduce the same spelling, route order is
not a mathematical resolution. The leaf must either provide the exact common operation
or the API must use distinct names.

For example, `gens()` can mean group generators, module generators, or algebra
generators. These are different mathematical sets. Use names such as
`group_generators()`, `module_generators()`, and `algebra_generators()`.

When both declarations have the same meaning but different algorithms, the common
subcategory can select the preferred algorithm. Sage's
`FiniteCoxeterGroups.some_elements()` is the grounding example.

The compiler must not use arbitrary route order to decide a semantic collision.

## Strict equality and natural isomorphism

For each public value and each reachable category, the kernel keeps one canonical
image. A diamond can satisfy this rule in either of two ways.

### Strictly coherent routes

Both routes return the same selected image by identity. The object image, element
image, morphism image, parents, domains, and codomains are the same objects. The
compiler deduplicates the routes.

This identity holds by construction. A source value retains each ancestor value supplied
as defining data. A derived ancestor image is constructed once from retained data and
cached for that source value. A selected structural functor returns that retained or
cached ancestor value on every call and never reconstructs an equal or isomorphic
replacement.

The compiler checks the identity during construction. If no constructor reaches the
target node, it checks at the first public functor application. It traverses every route in
`structure_functors()` declaration order, stores the first image in the canonical cache,
and asserts that each later image `is` the stored image. On the first mismatch it raises
a construction-defect error that names the source value's construction, the two routes,
and the shared ancestor category. Nothing is repaired, replaced, or retried. The compiler
never asks whether the two values are mathematically equal.

Routine structural diamonds have this form. The two selected paths from a finite module
to sets reach the same set object.

### Merely isomorphic routes

A functor enters `structure_functors()` only when every shared-ancestor route through it
returns the retained canonical value by identity. Two routes that construct different
presentations connected by a natural isomorphism are therefore never both selected. The
second presentation remains an ordinary functor of `Fun` or an explicit isomorphism.

Natural transformations are trusted constructions. They never rewrite, normalize, or
identify structural routes, and the compiler performs no naturality or higher-categorical
proof.

## Final decision

The architecture uses the following rules.

1. Selected structural functors form the complete inheritance graph.
2. The compiler collects methods from every reachable branch.
3. A branch-specific method remains available on every structural descendant.
4. Two routes to the same declaring category return one canonical image by identity.
5. Routine strictly coherent diamonds resolve automatically in the kernel.
6. A leaf never traverses a route, normalizes to an ancestor, moves images, manages a
   canonical-image cache, or installs inherited methods.
7. A genuine presentation or algorithm choice is a small mathematical declaration by
   the category that owns the choice. The kernel executes it.
8. A choice of presentation includes objects, elements, morphisms, and universal data.
   It cannot mix data from different presentations.
9. Independent method declarations with different meanings require distinct names or an
   explicit mathematical operation at the common descendant.
10. Method-resolution order never decides mathematical meaning.
11. Each compiled role contains the copied local members and the compiled roles of every
    selected ancestor in controlled C3 order. The object and morphism chains then join
    the one compiled `Cat().ElementType` root through `ObjectOfCategory` or
    `MorphismOfCategory`. An ordinary element chain joins it through `ElementOfObject`.
    Copied functions bind `__class__` to the compiled role. The rebound local initializer
    remains separate from the generated `__init__` wrapper.
12. The kernel allocates the public value first. Before the C3 chain starts, each selected
    functor converts complete typed construction inputs along structural edges. The
    object context adds `ObjectStageIdentity(C)`. The morphism context adds
    `ArrowStageIdentity(C, A, B)`. An ordinary element keeps its defining morphism.
    A generated class wrapper reads the input for its own node and passes only its local
    datum to the node initializer. Thus adjacent C3 classes need not be joined by a
    structural edge. The compiler initializes every reachable role and every common
    ancestor once.
13. A source value retains each ancestor value supplied as defining data. A derived
    ancestor image is constructed once and cached. A selected structural functor returns
    that retained value on every call and never reconstructs an equal or isomorphic
    replacement.
14. During construction or the first public functor application, the compiler
    traverses every route to that category in declaration order, stores the first image
    and construction input, and asserts that each later route supplies those same objects
    by identity. A mismatch raises a
    construction-defect error naming both routes and the shared ancestor.
15. The compiler never asks whether two images are mathematically equal and performs no
    naturality or higher-categorical proof. Natural transformations are trusted
    constructions. A construction states each preservation or lift fact at that
    construction; the compiler has no preservation registry.
16. A functor enters `structure_functors()` only when every shared-ancestor route through
    it returns the retained canonical value by identity. A route pair that is only
    naturally isomorphic remains a pair of ordinary functors of `Fun`.

The short form is:

> Preserve every branch. Initialize every role once. Resolve only duplicate access to a
> common owner. Identity holds by construction and is checked during construction. Ask a category for a choice
> only when the mathematics contains a real choice.

## Acceptance examples

The resolution design must support these examples.

### Ring inheritance

A ring receives additive-group operations and multiplicative-monoid operations. Both
routes reach one canonical underlying set. Set membership has one owner and one public
implementation.

### Finite vector spaces

A finite-dimensional vector space over \(\mathbf F_p\) belongs to finite sets by its
construction theorem. It receives both module operations and finite-set operations. It
does not enumerate its \(p^n\) elements to establish finiteness.

### Module products

A product in \(\operatorname{Modules}(R)\) retains its module apex, projections, and
mediating morphism. Its underlying set is the chosen set product. Product elements belong
to that exact apex.

### Module coproducts

The underlying set of a module coproduct is not identified with the set coproduct. The
compiler does not invent preservation of colimits by the selected structural functor.

### Algorithm selection

When two inherited methods have the same meaning but different algorithms, the common
category can select one implementation. The selection does not remove other methods
from either branch.

### Semantic collision

When two branches use one spelling for different mathematics, compilation rejects the
ambiguity or the public API gives the operations distinct mathematical names.

### Nonidentical presentations

When two routes would yield merely isomorphic product presentations, projections and
elements from one presentation are not attached to the other apex. One complete
presentation is canonical and selected; the other remains an ordinary functor or an
explicit isomorphism and is never a selected route.
