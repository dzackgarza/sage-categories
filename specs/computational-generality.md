# Mathematical generality and computation

This specification owns the distinction between a mathematical domain and the domain
of an algorithm used to compute in it. It applies to `Cat`, its runtime, and every
leaf. [System architecture](system.md) assigns implementation ownership; topic
specifications retain the definitions and public names of individual constructions.

## Contents

- [Mathematical domain](#mathematical-domain)
- [Compositional expressibility](#compositional-expressibility)
- [Independent finiteness conditions](#independent-finiteness-conditions)
- [Representation and execution](#representation-and-execution)
- [Infinitary constructions](#infinitary-constructions)
- [Ordinary infinitary objects](#ordinary-infinitary-objects)
- [Finite observations and approximations](#finite-observations-and-approximations)
- [Acceptance across domains](#acceptance-across-domains)

## Mathematical domain

The framework must accommodate infinite objects, nonenumerable objects, and
infinitary constructions. `ZZ` and `RR` are basic mathematical domains. Infinite
rank modules, infinite dimensional spaces, and infinite diagrams belong to the
ordinary scope of a computer algebra framework.

An operation's declared mathematical hypotheses determine its domain. An engine's
finite tables, terminating algorithms, available normal forms, or finite diagram
syntax do not add hypotheses to that declaration. A computation requiring stronger
hypotheses operates on the corresponding supplied structure or mathematical
restriction. The general operation retains its original domain.

Representing `RR` does not require enumerating its points or encoding every real
number as a finite string. A symbolic real domain, a represented exact point, and a
numerical approximation are distinct objects of computation. A countable set of
encodable points or fixed-precision floating values cannot replace the real domain.
Representations must support the public operations claimed for their inputs; an
object bearing the name `RR` alone establishes none of those operations.

## Compositional expressibility

The mathematical vocabulary must make the objects in this specification ordinary
to construct, express, and combine. A mathematician supplies their defining
objects, maps, families, and hypotheses through the public category language.
The resulting objects participate in the same morphism, functor, subobject,
quotient, and universal-construction vocabulary as other objects of their category.
Their size does not introduce a separate mathematical universe or declaration path.
Runtime construction and static expression must preserve the same mathematical
domains and maps.

Adding a domain may require its mathematical definitions and operations at the
appropriate owner. It must not require redesigning the kernel, category placement,
functor interfaces, or general construction protocols merely because the domain
has infinitely many elements, generators, coefficients, stages, or degrees. If an
ordinary expression encounters such a restriction, that is a defect at the shared
owner. Repair its general contract rather than adding a branch for the named
example. The user supplies mathematical data, not replacement foundation machinery.

This is a requirement on the language's scope and composability. It prescribes no
particular engine, algorithm, storage format, evaluation strategy, or precision
scheme for these examples. It does not assign a separate implementation project
to each row. Specialized computations have their own mathematical hypotheses and
delivery scope. Their availability must remain distinct from the ability to
construct the object, retain its defining structure, and express its maps and
composites. A display name or an opaque placeholder does not supply that structure;
operations claimed as executable must still execute.

The examples constrain families of constructions, not a whitelist of supported
names. Apply the same vocabulary to other admissible parameters and to composites
of the constructions. A quotient of an infinite object, a map between completions,
or a complex of infinite modules must not encounter a finite-only intermediate
owner. Preserve the order and hypotheses of the constructions: expressibility
does not assert that limits, colimits, completion, localization, or forgetting
structure commute in the absence of the appropriate theorem.

## Independent finiteness conditions

Identify which object each condition concerns before using it to select computation:

| Condition | What it does and does not supply |
| --- | --- |
| Finite underlying set | Mathematical cardinality is finite; a chosen enumeration and its executable indexing maps are additional data. |
| Countable underlying set | Does not select an enumeration, a computable enumeration, or a terminating exhaustive search. |
| Chosen enumeration | Supports its declared traversal and indexing operations; an infinite traversal cannot be materialized to completion. |
| Decidable membership | Decides admission of a candidate; it does not enumerate all members or decide equality of two sets. |
| Finite presentation | Finitely many generators and relations in a stated category; neither a finite carrier nor a general decision procedure follows. |
| Finite diagram shape | Bounds the indexing data; diagram values and the resulting limit or colimit can be infinite or nonenumerable. |
| Finite arity of operations | Bounds the inputs to each operation; it does not bound the carrier, the number of generators, or the index of a categorical construction. |
| Finite support of an element | Bounds that element's nonzero components; it does not bound the ambient basis or impose one common finite bound on all elements. |
| Finite rank or finite generation | Requires the stated module or algebra structure and base; forgetting structure need not preserve it. |

A finitely presented category can have infinitely many morphisms: the free category
on one object and one loop contains every finite power of that loop. Native path
composition and representation must therefore exist independently of enumerating
the quotient's arrows or completing a word-problem calculation.

An iterator addresses traversal of an enumerable family. Replacing a list with an
iterator does not provide a representation of a nonenumerable set, an arbitrary
indexed family, or its universal property.

## Representation and execution

Retain the mathematical input through its category, defining maps, selected
presentation, and exact parameter objects. Use native engine representations for
the operations they supply. Several engines may contribute to one owned operation
through the existing private boundary; this introduces no public backend choice.

Select a finite evaluator only after its actual input requirements are established,
including chosen data and decidable comparisons where its algorithm needs them.
The same finite shape with different diagram values may require another exact
engine representation. Backend selection must follow supplied semantic data, not
the presence of a private field, an attempted enumeration, or a caught exception.

Distinguish these outcomes:

- A represented construction retains its defining data and maps. Its promised
  public actions operate on those data without first materializing the domain.
- A proposition or typed query can remain undecided through the existing `ask()`
  contract. That uncertainty concerns the specific question, not the existence of
  the represented object or a separately defined operation.
- A missing implementation, failed import, unsupported required engine operation,
  or crashed evaluator is an implementation gap. It cannot become mathematical
  `Unknown`, nonmembership, an empty result, or a successful formal placeholder.

A supplied morphism rule can be applied at an admitted point without deciding every
equality on its domain. A constructor uses the admission contract of its owner;
neither exhaustive checking nor a raw callable alone establishes all its laws.
An exact construction theorem can supply a map or placement when a general decision
procedure is unavailable.

The absence of one engine algorithm requires investigation of the actual operation
and other mature dependencies. It does not authorize a narrower public domain or a
bespoke replacement. Follow the existing dependency and failure procedure in
[AGENTS.md](../AGENTS.md#ownership-and-dependency-reuse).

## Infinitary constructions

An indexed construction retains the entire supplied index object, diagram, and
action rules. Operations at a supplied index use those rules directly. Products
retain projections, coproducts retain injections, and universal presentations retain
their mediators on the stipulated cones or cocones. A finite prefix cannot replace
this data. [Universal constructions](functor.md#diagram-shapes-and-universal-constructions)
owns the distinction between a construction category, a supplied presentation, and
a chosen construction for every diagram.

Existence still depends on the ambient category and shape. These requirements do
not declare every category complete, every functor continuous, or every diagram
computable. They require preserving exactly the shapes and operations the contract
admits, including infinite ones.

The following mathematical examples constrain the foundation's representation and
composition. Their domain-specific computations belong to their mathematical owners;
they are not special-case branches to add to `Cat`.

| Object | Structure that must survive representation |
| --- | --- |
| `ZZ × ZZ` and `RR × RR` | Two factors, potentially infinite or nonenumerable, with projections and pairing. A finite index does not permit enumerating the factors. |
| `CP^infty` | The colimit of the standard inclusions `CP^n -> CP^(n+1)` for nonnegative integers `n`, with its CW topology, structure maps, and induced maps from compatible families. A selected finite skeleton remains a different object. |
| The adeles of `QQ` | The restricted product `RR × product'_p QQ_p` relative to `ZZ_p`, with its restricted product topology. Components are integral at all but finitely many primes, not zero at all but finitely many primes. Retain the full family and restriction. |
| An arbitrary algebraic direct sum of modules | Each element has finite support; the index set can be infinite or nonenumerable. Maps out are determined by the supplied family of component maps, without listing the entire index. |

For `CP^infty`, see Hatcher, [*Algebraic Topology*, Example 0.6, pp. 6–7](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf#page=15).
For the adelic definition, see Conrad, [*The Character Group of Q*, Definition 3.1, p. 6](https://kconrad.math.uconn.edu/blurbs/gradnumthy/characterQ.pdf#page=6).
The topological construction is specified in Mathlib,
[“Topology on the restricted product”](https://leanprover-community.github.io/mathlib4_docs/Mathlib/Topology/Algebra/RestrictedProduct/TopologicalSpace.html#topology-on-the-restricted-product).
The module and algebra consequences are specified in
[modules.md](modules.md#size-and-coordinate-presentations) and
[algebras.md](algebras.md#finite-presentation-and-the-underlying-module).

## Ordinary infinitary objects

The following families extend the examples above. They state mathematical
expressibility requirements, not implementation selections or a claim of present
runtime support. Here `k` is a field, `A` is a commutative ring, `I` is an ideal of
`A`, `p` and `ell` are primes, `S` is a small indexing set that need not be
enumerable, and `Gamma` is a linearly ordered abelian group. Each construction
retains its additional stated hypotheses and ambient category.

| Family and examples | Structure expressible in the ordinary vocabulary |
| --- | --- |
| Localizations: `ZZ_(p)`, `A_q` for a prime ideal `q`, and fraction fields of domains | The multiplicative subset, localization map, fractions, and universal extension to a ring where its elements become units. The multiplicative subset need not have a finite generating list. |
| Divisible and torsion groups: `QQ`, `QQ/ZZ`, and the Prüfer group `ZZ[1/p]/ZZ` | Their abelian-group and module structures, subgroup inclusions, quotient maps, and torsion subgroups. Neither finite generation nor freeness is an admission condition for the ambient module category. |
| Infinite algebraic extensions: algebraic closures of `QQ` and `GF(p)`, and `QQ(mu_infty)` | The extension field, finite subextensions and their compatible embeddings, arithmetic and induced maps across subextensions, and automorphisms with their stipulated domains. Each element being algebraic does not make the whole extension finite. Preserve a selected embedding when it is part of the input. |
| Formal series: `k[[t]]`, `k((t))`, and multivariate formal power series | Coefficient families, ring operations, coefficient and truncation maps, differentiation, and substitution under its convergence or formal-admissibility hypotheses. A formal series, a polynomial, and a residue modulo a power of the defining ideal are distinct. |
| Adic and profinite objects: `ZZ_p`, `QQ_p`, the profinite integers, and `lim_n A/I^n` for positive `n` | The full compatible inverse systems, their limits and quotient maps, and passage from `ZZ_p` to its fraction field `QQ_p`, with the appropriate topology and continuous maps. Finite quotients and finite-precision observations retain their maps to or from the relevant construction; agreement at one precision is not exact equality. |
| Infinitely generated polynomial and graded algebras: `k[x_s : s in S]`, exterior algebras on infinite modules, and symmetric functions | The entire generator or grading family, finite expressions where the algebra requires finite support, substitutions determined on generators, and graded algebra or Hopf algebra structure. No maximum variable index or degree is part of the ambient object. Distinguish a graded algebra from its degree completion. |
| Unrestricted products and duals: `product_S k` and `Hom_k(direct_sum_S k, k)` | Arbitrary supported coefficient families, projections, evaluation, and the canonical pairing with finitely supported vectors. Algebraic dual, graded dual, and continuous dual retain their distinct definitions and relevant topology. |
| Unbounded complexes and resolutions: periodic free resolutions, bar resolutions, and integer-indexed complexes | The degree-indexed objects, differentials, chain maps, shifts, cones, and the chosen direct-sum or product totalization where defined. A bounded calculation or truncation retains its own meaning and comparison; it does not change the extent of the original complex. |
| Infinite simplicial objects: classifying spaces `BG` for groups `G`, nerves, and bar constructions | Objects in every simplicial degree, face and degeneracy maps with their identities, and maps induced by the original functors or homomorphisms. Finite input can define structure in arbitrarily high degrees. A finite skeleton remains distinct from the whole simplicial object or its realization. |
| Formal schemes and neighbourhoods: `Spf(k[[t]])` and completion along a closed subscheme | The topological ring, compatible infinitesimal thickenings, structure sheaf, and geometric maps corresponding to continuous ring maps under the relevant hypotheses. Preserve the formal scheme rather than replacing it by one thickening or discarding its topology. |
| Arc spaces and jet towers: `J_infty X`, including `J_infty A^1` | The entire compatible jet system, truncation maps, and maps induced by morphisms of schemes. For the affine line over `k`, the arc space is `Spec(k[x_0, x_1, ...])`; its points over a `k`-algebra `R` correspond to `R[[t]]`. The representing scheme and its points are different categorical levels. |
| Torsion towers and Tate modules: `mu_(p^infty)` and `T_ell(B)` for an abelian variety `B` over a field of characteristic different from `ell` | The compatible finite group-scheme stages and transition maps for the divisible group; for the Tate module, the inverse system of geometric torsion points with its induced maps and Galois action. Keep the group scheme, its points over a supplied field, and its resulting module distinct. |
| Generalized series: Hahn series `k((t^Gamma))` | The ordered exponent group, coefficient family with well-ordered support, valuation, and algebraic operations on the defined domain. Well-ordered support need not be finite or an integer-indexed sequence; it is not interchangeable with an arbitrary unrestricted support. |

Two elementary expressions make the scope especially concrete. For any small set
`S`, `Hom_k(direct_sum_S k, k)` is canonically isomorphic to `product_S k` by
pairing a coefficient family with a finitely supported vector.
Evaluation uses only the vector's finite support; the
functional has no finite-support requirement. This is an algebraic dual statement,
not an identification of every notion of dual.

For `R = k[epsilon]/(epsilon^2)`, the free resolution
`... -> R -> R -> R -> k -> 0` has multiplication by `epsilon` at each arrow
between copies of `R` and the quotient map at `R -> k`. The kernel and image of
multiplication by `epsilon` are both the ideal `(epsilon)`. The resolution is
therefore an elementary infinite object specified by a uniform degree rule, with
no largest degree. Periodicity does not turn it into a bounded complex.

Mathematical references and existing examples include Sage's
[universal cyclotomic field](https://doc.sagemath.org/html/en/reference/number_fields/sage/rings/universal_cyclotomic_field.html),
[symmetric functions](https://doc.sagemath.org/html/en/reference/combinat/sage/combinat/sf/sf.html),
and [simplicial sets and nerves](https://doc.sagemath.org/html/en/reference/topology/sage/topology/simplicial_set.html);
the Stacks Project's [completion along a closed subspace, section 87.38](https://stacks.math.columbia.edu/tag/0GXT);
and Mathlib's [Hahn series definition](https://leanprover-community.github.io/mathlib4_docs/Mathlib/RingTheory/HahnSeries/Basic.html).
These references identify mathematical structures and distinctions; they do not
allocate their implementation to those systems.

## Finite observations and approximations

A degree cutoff, finite skeleton, finite set of places, finite quotient, or numerical
precision must be explicit when it changes the returned mathematical object or the
strength of an answer. Retain the relevant inclusion, projection, or comparison to
the original object. Never reuse the original object's identity for a truncation.

A finite computation can give an exact answer about an infinite object when a
theorem establishes sufficiency for that question. State the question and the
theorem's hypotheses and range. Agreement through a tested degree, word length, or
set of indices establishes no unrestricted equality or universal property.
Checking finitely many generators proves a global statement only under the theorem
and presentation hypotheses that make those generators determining.

In particular, deciding a universal predicate over an infinite family requires an
exact argument for the entire family. Keep the quantifier represented when it
cannot be decided. A finite Python conjunction or a nonterminating traversal is not
that representation.

## Acceptance across domains

For an expressibility claim, follow the defining mathematical expression through
its ordinary categories, input data, maps, and compositions. It must construct the
intended structured object without consumer-supplied generic infrastructure or a
foundational change specific to the example. Keep this claim separate from an
algorithmic claim about computing invariants, deciding all equalities, or obtaining
an approximation. Merely writing the expression in a specification establishes
the obligation, not that the current language already satisfies it.

A generality claim must be exercised at the distinctions it crosses, through the
ordinary public construction and the resulting maps. A finite example establishes
the finite case. A larger finite example does not establish the infinite case; a
countably infinite example does not establish the nonenumerable case.

Select examples from the unchanged contract before selecting its engine. For the
shared set-product boundary, use a finite product, a product of rule-defined
integers, and a product of a nonenumerable domain. Read projections and a pairing
on owned points with exact expected values. For an infinite index, use its supplied
rule and an index outside any finite sample retained by the exercise; preserve the
public mediator and verify its component equation. Source inspection must also
establish that the algorithm uses the family rather than an untested fixed cutoff.

These are proof obligations at the affected owner, not a demand to run every domain
in every work unit. A finite backend adapter can be verified on its finite contract;
replacing a shared owner additionally owes its affected nonfinite consumers.
The procedure for preserving that evidence is in
[AGENTS.md](../AGENTS.md#preserve-the-strength-of-the-example).
