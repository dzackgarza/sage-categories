# Categorical architecture and enforcement

The primary mechanism is **categorical transport along selected functors, with coherence expressed by actual cells in `Cat`**. The intended semantics are ∞-categorical through every level, including the higher cells needed by the construction. Runtime classes and computation engines make that mathematics executable.

The repository already connects its owned `Mor` tower to `homotopy-core` and supplies executable natural transformations through `Cat` and Catlab. Requiring leaf comparison cells is compiler integration over that existing infrastructure. It does not require creating a new higher-category engine.

Make the desired architecture a consequence of the public interfaces and their compilation, then check the resulting boundaries mechanically. This can eliminate whole classes of drift without enumerating every bad implementation pattern.

## Contents

- [Functorial inheritance and leaf simplicity](#functorial-inheritance-and-leaf-simplicity)
- [Coherence and compiler diagnostics](#coherence-and-compiler-diagnostics)
- [Generic constructions and named categories](#generic-constructions-and-named-categories)
- [Engine delegation and research precedents](#engine-delegation-and-research-precedents)
- [Mathematical ownership and typed interfaces](#mathematical-ownership-and-typed-interfaces)
- [Architectural enforcement](#architectural-enforcement)

## Functorial inheritance and leaf simplicity

Complete the existing declaration-to-runtime compiler around the repository's categorical contracts. A leaf supplies:

- Its mathematical data and public constructors.
- Its immediate named functors, including their ordinary object and morphism actions.
- Its additional operations, hypotheses, and genuinely new comparison or lifting data.
- Private bindings to computational engines.

`Cat` owns common categorical mathematics and universal constructions. `cat_kernel` interprets declared functor properties relevant to inheritance and placement. The kernel performs class compilation, initialization, identity retention, and runtime placement. Private engine adapters lower owned inputs, compute, and reconstruct owned results. These responsibilities and import directions remain those of [the system specification](specs/system.md#system-shape): leaves reach `Cat`, their immediate mathematical targets, and their own helpers; neither `Cat` nor the kernel imports production leaves.

The central semantic consequence for an eligible selected functor `F: C -> D` is:

```text
x.f() := F(x).f()
```

This expresses equality of mathematical values. The specified runtime executes the inherited method directly on the structured source instance. The kernel obtains the target initialization from the datum supplied through the ordinary functor action; public application `F(x)` returns the separate image of the completed source. A leaf supplies no second description of transport and calls no inherited initializer. See [inherited execution](specs/functor.md#cobjecttype-celementtype-and-cmorphismtype) and [runtime initialization](specs/resolution.md#direct-inherited-execution).

Inheritance follows every eligible selected path. Eligibility matters: an arbitrary functor that exists in `Fun(C, D)` does not automatically contribute inherited execution. The repository licenses inheritance through a selected declaration in `Isofibrations()` or a subcategory of it; in that selection context, the declaration also asserts faithfulness. An arbitrary isofibration need not be faithful. See [structure functors](specs/functor.md#structure-functors-and-inherited-classes).

Reading an operation on `F(x)` and constructing a result back in `C` are distinct obligations. An isofibration supplies lifting of isomorphisms. A construction returning an object or morphism of `C` can require additional preservation, creation, or executable lifting structure. The selected-isofibration convention is the repository's inheritance contract, not a theorem that every isofibration lifts every operation.

The practical criterion is that **an ordinary new leaf requires no knowledge of how inherited state gets initialized or retained**. Moving a lifecycle helper behind a different import does not satisfy that criterion if the leaf still orchestrates it.

This is information hiding in Parnas's sense: conceal design decisions such as runtime class construction, method resolution, image storage, and backend representation behind stable mathematical interfaces. [Parnas's modularity paper](https://www.cs.lafayette.edu/~gexia/cs301/resources/parnas.html).

## Coherence and compiler diagnostics

For two composites of eligible selected functors

\[
P,Q:C\longrightarrow D,
\]

the relevant comparison is an actual cell \(\alpha:P\Rightarrow Q\) in `Cat`, constructed through the ordinary natural-transformation machinery of `Fun`. It is mathematical data, not a separate coherence certificate, proof record, route registry, or second functor declaration. See [the coherence contract](specs/resolution.md#diamond-diagnostics-and-future-coherence).

### Existing machinery and declaration data

The [native binding](native/homotopy-python/src/lib.rs) already exposes `Signature.add_generator(source, target, invertibility=...)`. The dimension follows from the boundaries. Cells support identities, inverses, boundary access, and attachment/composition; signatures provide typechecking. The [owned-cell adapter](src/sage_categories/engines/cells.py) connects the `Mor` tower to native signatures and retains identities, composites, whiskering, and inverses through `homotopy-core`. Leaves use the owned mathematical objects; the native declaration remains private.

For a **formal generating 2-cell**, the essential declaration consists of the parallel source and target functors, possibly composites, and the invertibility classification. The engine supplies the generator's identity and formal operations. Declaring it invertible requires neither a leaf-written inverse algorithm nor an infinite sequence of inverse witnesses. This declaration style is demonstrated in [homotopy.io's tutorial](https://github.com/homotopy-io/homotopy-rs/blob/master/TUTORIAL.md).

For an **executable natural isomorphism**, the declaration also needs its interpretation: a component rule

\[
X\longmapsto\alpha_X:P(X)\longrightarrow Q(X).
\]

The rule can use an existing canonical construction, an identity where the endpoints permit it, or a small private backend conversion. It is not an enumeration of the objects of `C`. The current [natural-transformation contract](specs/functor.md#functors-as-morphisms-of-cat) constructs this as `Mor(Fun(C, D))(P, Q)(assignment)` and explicitly trusts naturality. A formal declaration alone does not supply this executable interpretation.

The existing [natural_isomorphism helper](src/sage_categories/cat/calculus.py) accepts forward and inverse component rules and retains them as mutually inverse. The [functor category](src/sage_categories/cat/functors.py) also constructs the inverse of a declared natural isomorphism componentwise. Supplying both rules is therefore not an intrinsic leaf obligation when executable component inversion is already available. A formal inverse and an executable inverse remain distinct when component inversion itself has no executable rule.

These are already consumed mathematical interfaces: [monoidal structures](src/sage_categories/cat/monoidal.py) accept associators and unitors as actual natural isomorphisms. The [Catlab adapter](src/sage_categories/engines/catlab.py) realizes component assignments and transformation composition and whiskering. Reuse these constructors and operations for inheritance comparisons.

### Path selection and compiler integration

Interchangeability of the paths generally requires an **invertible comparison**, together with compatibility of the operation with that comparison. An arbitrary noninvertible 2-cell supplies a directed comparison. Choosing either path yields corresponding results under the specified transport; it need not yield identical Python representations or literally equal untransported outputs.

When changing paths changes a representation, execution must use the comparison to transport the affected arguments or results. Declaring two representations equivalent does not tell Python how to convert between them. This transport belongs to the generic interpretation of the supplied cell and operation.

The same carrier may support several distinct structures. Its additive and multiplicative magma structures, for example, must retain their distinct named functors and images. Sharing a target category or implementation class does not identify those structures. Agreement is required where paths are declared to represent the same inherited structure and an operation depends on that identification.

The existing runtime contract gives a shared implementation owner one controlled-C3 occurrence and one initialization. Mathematical access to all selected paths does not require duplicating the shared runtime class. Declaration order supplies the current path preference. It is an execution convention, not mathematical evidence that competing paths are interchangeable.

The compiler should identify missing mathematical data from the declared functors, their composites and endpoints, and the operation whose interpretation depends on the choice. A useful diagnostic identifies:

- The competing composites `P, Q: C -> D`.
- The inherited operation affected by choosing between them.
- The exact category of the required comparison, for example an isomorphism between `P` and `Q` in `Fun(C, D)`.
- Any remaining compatibility needed to transport that operation.

First obtain comparisons already supplied by generic constructions, adjunctions, or retained universal presentations. A leaf supplies only genuinely additional mathematical data. Discovering a required cell's boundary can often be mechanical, and declaring a formal generator uses the existing constructor. Supplying its executable interpretation or establishing its mathematical validity is a separate obligation. The compiler treats ordinary functor actions as opaque and cannot infer arbitrary mathematical facts from their Python bodies.

The current [diamond handler](src/sage_categories/kernel/compiler.py), `_debug_unresolved_diamonds`, collects competing category paths and emits an opt-in `DEBUG` diagnostic. It does not consult comparison cells. The concrete integration is to retain the actual functor composites, consume their supplied comparisons, use the required transport, and identify missing declarations. The existing cell calculus supplies the underlying operations; its availability alone does not establish that this compiler consumer works.

The current [diamond policy](specs/functor.md#structural-diamonds-and-coherence) accepts unresolved diamonds and continues with declaration-order preference and once-only C3 behavior. Requiring a declaration where an operation needs path interchangeability is an enforcement change at that compiler boundary. It uses the same mathematical interface as an informative missing-cell diagnostic. An unresolved comparison remains distinct from a demonstrated justification for freely interchanging paths.

### Higher invertibility and mathematical audit

Declaring mathematical structure and auditing a leaf's interpretation are separate responsibilities. The machinery can accept trusted declarations, as it already does for naturality. A leaf-specific audit establishes whether the supplied components, inverse assertions, and compatibility laws hold. Requiring those proofs before exposing the declaration machinery would impose an additional contract.

If all cells above a chosen dimension are stipulated invertible, that is an ambient semantic condition to handle centrally. **Invertibility of all higher cells does not imply that every desired higher comparison exists.** It provides inverses to existing cells; it does not make every parallel pair connected or every coherence diagram commute. Pairwise comparisons alone therefore do not supply every higher compatibility. Derive structural consequences generically and let leaves declare additional mathematical coherence where needed, with its validity audited separately. This does not require leaves to author an infinite tower of witnesses. Homotopy coherent diagrams and constructions remain the relevant mathematical setting. [Riehl and Verity, homotopy coherent adjunctions](https://arxiv.org/abs/1310.8279).

The [current morphism-tower specification](specs/functor.md#the-morn-c-tower) calls `Cat()` a strict 2-category. This describes the ordinary category/functor/natural-transformation fragment; it does not negate the generic higher-dimensional backend already connected to `Mor`. The intended broader semantics require the appropriate declarations and their interpretation through that infrastructure. The concrete inheritance work identified here is compiler integration, not a new foundational machinery project.

The [single-point-functor restriction](src/sage_categories/cat/category.py) must be addressed at this categorical and runtime boundary. Accepting a longer list alone does not establish correct transport, separation of distinct structures, or coherence.

## Generic constructions and named categories

`Cat` owns generic limits, colimits, products, coproducts, equalizers, coequalizers, their presentations, and their induced maps. A leaf supplies local data to these constructions and receives their categorical consequences.

When a leaf must reconstruct a product, equalizer, mediator, or induced morphism because the shared construction cannot supply it, the deficiency belongs to the generic owner. When a usable shared construction exists but the leaf bypasses it, the defect is leaf integration. Repair the corresponding public consumer through its actual owner in either case.

`Cat` can contain a named mathematical category such as `Sets()` before that category has a computational implementation. Generic constructions and definitions can refer to the existing object. In particular, `Cat().Concrete()` can express the existence of a faithful functor to `Sets()` without importing the sets leaf.

A later leaf implements the already-named category through its identity functor. The existing [named-category implementation contract](specs/functor.md#implementing-a-named-category) strengthens the same object in place, preserving identity and references. The declaration uses the actual category and its identity functor, with no string binding field.

A registry, where needed internally, retains these actual owned mathematical objects. Leaf authors select the category, functor, or retained projection itself. They do not coordinate declarations through string names.

The [concrete-category contract](specs/functor.md#concrete-categories) derives the selected faithful route to `Sets()` by composing existing structure functors. That supplies `functor_to_sets()`, `underlying_set()`, and `underlying_map()` at their generic owner. A leaf need not redeclare the entire route. Failure to find such a route does not prove that no faithful functor exists.

Generic reductions of ordinary limits to products and equalizers, and ordinary colimits to coproducts and coequalizers, also belong in `Cat`, under the relevant existence hypotheses. [Stacks Project, colimits from coproducts and coequalizers](https://stacks.math.columbia.edu/tag/002P). Higher categorical versions must retain the corresponding homotopy-coherent information; the ordinary formula alone does not supply it.

**Concreteness alone does not authorize computing every construction in sets and lifting it back.** The chosen functor must carry the required preservation, creation, or lifting structure. The existing [limit transport contract](specs/functor.md#diagram-shapes-and-universal-constructions) expresses shape-dependent hypotheses through `CreatesLimits(I)` and retains executable lifting data. A theorem declaration and chosen executable data have distinct roles.

For example, the compatible-family construction in [sheaves.py](src/sage_categories/geometry/sheaves.py) has the familiar shape

\[
\operatorname{Eq}\!\left(
\prod_i R_i \rightrightarrows \prod_{i,j}R_{ij}
\right).
\]

Under the relevant gluing hypotheses, the leaf supplies the rings and overlap maps. The generic construction supplies the resulting ring, projections, and mediator. [Stacks Project, gluing algebraic structures](https://stacks.math.columbia.edu/tag/00AM).

Likewise, composition of ringed-space morphisms uses generic operations on their underlying maps and sheaf transformations. The local-ring condition adds a mathematical restriction; it does not require another implementation of ringed-space composition.

The existing `lift_limit` in [constructions.py](src/sage_categories/cat/constructions.py) illustrates the intended division: local additional structure is supplied once, while the generic owner retains the universal data. An engine that computes an apex does not thereby supply projections, a mediator, or support for every declared input domain.

## Engine delegation and research precedents

Research starts from the project's categories, functors, cells, fibrations, and universal constructions, then identifies dependencies that execute the required mathematics faithfully. The public categorical semantics remain authoritative.

Start with the existing `homotopy-core` and Catlab integrations described under [coherence](#existing-machinery-and-declaration-data). They already provide the formal cell calculus and executable transformation operations relevant to this boundary. The precedents below address complementary concerns.

Sage's category framework supplies an established engineering precedent: reconstruct inheritance from mathematical information and attach generic operations and tests through categories. Use its runtime machinery while retaining the repository's own category graph. [Sage category primer](https://doc.sagemath.org/html/en/reference/categories/sage/categories/primer.html).

CAP supplies operation derivations:

- Register primitive operations.
- Describe derived operations by prerequisites and applicability conditions.
- Compute available derivations and select implementations by weights.
- Expose a derivation tree explaining how an operation became available.

Its saturation operation repeats derivation updates until nothing changes. The relevant TCS structure is dependency closure with weighted, multi-prerequisite derivations. For operations CAP owns, use its implementation through the private engine boundary and reconstruct complete public results. This computational selection does not replace the categorical comparison needed to identify different inherited structures. [CAP: Managing Derived Methods](https://homalg-project.github.io/CAP_project/CAP/doc/chap8_mj.html).

GATlab supplies typed terms, theories, models, and interpretation for suitable computational fragments. These notions can themselves have categorical meanings. Its explicit-model design addresses the fact that identical Julia representations can occur in different mathematical categories; its finite-set and matrix-category example uses integers as objects of both. [GATlab's explicit-model design](https://blog.algebraicjulia.org/post/2025/02/refactor1/index.html).

Use that machinery within an appropriate private computational domain. It must not introduce a competing public semantics or replace the owned functors and cells with a second hierarchy of models. Typed expressions alone do not prove backend laws or supply general higher coherence. [GATlab documentation](https://algebraicjulia.github.io/GATlab.jl/dev/).

MathComp's coherence and hierarchy algorithms, and Hierarchy Builder's elaboration of declarations into packed structures, are secondary design references. They are not Python dependencies or the primary semantics of this project. Their hierarchy assumptions must not be imposed indiscriminately on the richer functor graph. [Sakaguchi, IJCAR 2020](https://arxiv.org/html/2002.00620v2), [Hierarchy Builder](https://github.com/math-comp/hierarchy-builder).

Keep each engine's domain and integration requirements explicit. Finite or presented evaluation restrictions belong to the computation and do not narrow the owned mathematical universe.

## Mathematical ownership and typed interfaces

String-keyed interfaces are inappropriate for semantic ownership, category implementation, retained constructions, and coherence. A string identifies neither a mathematical owner nor a type, endpoint, or universal property. The interface should expose the actual category, functor, presentation, projection, or cell. The [leaf contract](specs/leaves.md#pol-leaf-077--declaration-lookup-by-name-string) already prohibits declaration lookup by name string.

Private dictionaries can remain implementation details. Leaf authors must not coordinate mathematical structure through string families or `Any`-valued registries. Concrete typed interfaces preserve the mathematical distinctions.

The responsibilities combined in [cat/assembly.py](src/sage_categories/cat/assembly.py) have distinct owners:

| Data | Appropriate owner |
| --- | --- |
| Chosen basis, cone, presentation, or other mathematical choice | The corresponding mathematical object or construction |
| Constructor interning and runtime identity | Kernel |
| Native engine value and conversion machinery | Private adapter |
| Derived functor image | Its declared functor and the generic retention machinery |
| Comparison between functor paths | The actual cell in the appropriate owned functor or morphism category |

A mathematical author requests a presentation or projection and applies a named functor. Runtime identity, mathematical equality, and comparison by an invertible cell remain distinct obligations.

## Architectural enforcement

Architecture conformance compares source dependencies with the intended ownership relationships. Software reflexion models formalized this approach: map source modules into an architectural model and expose agreements and discrepancies. [Murphy, Notkin, and Sullivan, FSE 1995](https://www.cs.ubc.ca/~murphy/papers/rm/fse95.html).

Use complementary boundaries:

| Obligation | Enforcement |
| --- | --- |
| Every module has an architectural role | Import Linter exhaustive contracts, so newly added modules require classification |
| Only designated owners access runtime or engine internals | Protected-module contracts with allowed importers |
| Dependencies respect the intended direction | Layer/forbidden contracts, including indirect paths where appropriate |
| Public mathematical interfaces preserve types | Existing mypy checks, explicit exports, and checks against `Any` propagation |
| Inheritance preserves owners, endpoints, and selected structures | Validation in the existing declaration compiler |
| A path comparison is needed | The compiler consumes owned comparison cells and names missing boundaries and compatibility; the current diagnostic-only policy and mandatory enforcement remain distinct |
| Generic operations actually work in leaves | Automatically applicable mathematical contract tests through public consumers |

Import Linter supports [exhaustive layers](https://import-linter.readthedocs.io/en/stable/contract_types/layers/) and [protected modules](https://import-linter.readthedocs.io/en/stable/contract_types/protected/). These express architectural relationships without maintaining an expanding list of known offending imports. Preserve legitimate dependencies on immediate mathematical targets: isolatable leaves need not be mutually independent.

Explicit exports and restrictions on untyped calls and `Any` propagation help prevent implementation details from escaping through otherwise permitted modules. Mypy already provides these controls. Types and import checks complement each other; neither establishes semantic ownership or mathematical correctness by itself. [Mypy's documented controls](https://mypy.readthedocs.io/en/stable/command_line.html).

The compiler should validate positive invariants from authoritative declarations: initialized image dependencies, correct endpoints, distinct selected structures, and supplied comparisons where an operation requires them. Completing its comparison consumer and the selected missing-declaration policy protects path interchangeability; the existing diagnostic handler alone does not. Mathematical audits establish the truth of trusted leaf declarations separately. These checks target the mathematical obligation regardless of the particular implementation pattern that violates it.

Generic tests follow the same ownership model as generic operations. Test category and functor laws, transport compatibility, universal mediators, owner separation, and reconstruction through real adapters. Use Hypothesis where generated inputs or operation sequences expose construction-order interactions, repeated construction, and multiple structures on one carrier. Stateful testing generates and shrinks sequences, reducing the need to anticipate each failing sequence manually. [Hypothesis stateful testing](https://hypothesis.readthedocs.io/en/latest/stateful.html).

The strongest achievable guarantee is that whole classes of architectural violations become unrepresentable through the supported interface or are exposed by a general invariant check. Mathematical correctness inside unrestricted Python still requires semantic evidence. Completing categorical transport, actual coherence data, and generic constructions is what makes the small leaf interface sufficient; enforcement protects that architecture once supplied.
