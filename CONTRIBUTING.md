# Contributing

This repository implements a categorical foundation for Sage-based mathematics.
Mathematical structure controls the code architecture.

Each coding policy has a permanent identifier of the form `POL-AREA-NNN`. Use these identifiers in code review and design discussion.
Do not reuse a retired identifier.

## Current implementation boundary

| ID | Policy |
| --- | --- |
| `POL-SCOPE-001` | Build the foundation in dependency order: `Cat`, the morphism categories `Mor(n, C)`, method inheritance, then `Sets()`. |
| `POL-SCOPE-002` | Keep current feature work within the foundation through `Sets()` until that foundation meets its acceptance criteria. |
| `POL-SCOPE-003` | Implement the complete morphism-category family: `Mor(n, C)`, its fixed-endpoint subcategories `Mor(C)(A, B)`, its endomorphism, monomorphism, epimorphism, isomorphism, and automorphism property subcategories, `Fun([1], C)`, and the slice, coslice, subobject, and superobject categories. |
| `POL-SCOPE-004` | Make object, element, and morphism inheritance work before adding theories that depend on it. |
| `POL-SCOPE-005` | Treat the full owned `Sets()` category as foundational work, not as a finite-set helper library. |
| `POL-SCOPE-006` | Use algebra cardinality and the path from lattice isometries through module homs to set homs only as vertical acceptance examples. Do not implement those higher categories yet. |
| `POL-SCOPE-007` | Judge the project by categorical uniformity, explicit mathematical ownership, functorial reuse, and legibility. Successful computation or compilation alone does not satisfy its purpose. |
| `POL-SCOPE-008` | Make every theory subtree outside the implementation kernel auditable by a mathematician with little programming experience. Keep compiled structural inheritance and role construction in the kernel. Keep engine representations behind private computation boundaries while permitting category-owned methods to invoke a fixed engine directly. |
| `POL-SCOPE-009` | Judge an architectural claim from the live method owners, structural functors, compiled role graph, construction-input conversions, constructor obligations, and universal data. Agent reports, passing tests, route metadata, generated type identities, and runtime output cannot replace that inspection. |
| `POL-SCOPE-010` | Theory code declares categories and implements their objects, elements, morphisms, functors, constructions, and mathematical operations. |
| `POL-SCOPE-011` | Leaf code is theory code for one category. It states only that category's new data, operations, structural functors, constructors, and lifts. |
| `POL-SCOPE-012` | Kernel code implements category-independent role compilation, structural routes, construction-input conversion, dynamic types, C3 constructor composition, and canonical images. It contains no category-specific mathematics. |
| `POL-SCOPE-013` | Backend-adapter code converts owned mathematical values to and from a computation engine. It does not define the public mathematical interface. |
| `POL-SCOPE-014` | Interpret a primitive ban by its named role and layer. A ban on mathematical classification does not ban implementation-only use inside the kernel. |
| `POL-SCOPE-015` | Apply a bare primitive ban to every layer. Only an explicit layer-specific policy can permit a narrower use. |
| `POL-SCOPE-016` | Keep kernel and backend primitives private. Return typed semantic values or declarations before theory code receives control. |

## Shadowed package universe

| ID | Policy |
| --- | --- |
| `POL-SHADOW-001` | Build a package-owned categorical replacement for a significant subset of the standard Sage mathematical surface. Shadow supported Sage names with owned objects rather than re-exporting Sage objects. |
| `POL-SHADOW-002` | Provide `sage_categories.all` as the primary opt-in import surface, analogous to `sage.all`. Its imports expose the supported owned universe under the familiar mathematical names. |
| `POL-SHADOW-003` | Keep the public API closed over package-owned objects. Every public operation or construction applied to owned inputs returns owned categories, objects, elements, morphisms, or functors. |
| `POL-SHADOW-004` | Do not refine, register, or graft arbitrary Sage objects into the owned category hierarchy. Construct the corresponding owned object explicitly when the package supports it. |
| `POL-SHADOW-005` | Give no compatibility guarantee between package-owned objects and ordinary Sage APIs. Treat any duck-typed interoperability as incidental behavior outside the public contract. |
| `POL-SHADOW-006` | Absorb each required Sage construction into the package universe. Use its Sage implementation privately when useful and re-express its public behavior through owned categorical APIs. |
| `POL-SHADOW-007` | Treat importing `sage_categories.all` as a commitment to the package universe. Unsupported ordinary Sage constructions and their downstream code remain outside the guaranteed interface. |

For example, shadowing `ZZ` means that a finite-rank free `ZZ`-module, its elements, its products, and every later supported construction remain package-owned.
If elliptic curves are not yet owned, ordinary Sage elliptic-curve code receives no guarantee merely because it internally uses Sage integers or free modules.
The package must absorb the elliptic-curve construction before claiming that workflow.

## Mathematical model

| ID | Policy |
| --- | --- |
| `POL-MATH-001` | Identify the mathematical objects, elements, morphisms, categories, functors, and universal properties before choosing Python representations. |
| `POL-MATH-002` | Model a named category as a category, not as a class with similarly named methods. |
| `POL-MATH-003` | Model a named functor with an object map and a morphism map. |
| `POL-MATH-004` | Model a natural transformation by its components and naturality data. |
| `POL-MATH-005` | Keep a mathematical object distinct from a presentation, coordinate tuple, matrix, or computation-engine value. |
| `POL-MATH-006` | Keep an element distinct from its image under a morphism. |
| `POL-MATH-007` | Store chosen mathematical structure as mathematical data, usually an object or morphism in an owned category. |
| `POL-MATH-008` | Do not duplicate data that a defining morphism already determines. |
| `POL-MATH-009` | Put each operation at the weakest categorical level whose hypotheses imply it. |
| `POL-MATH-010` | Implement the general mathematical notion and obtain special cases by restriction or specialization. |
| `POL-MATH-011` | Use established mathematical terminology. Name each operation by the structure that owns it. |
| `POL-MATH-012` | Treat a missing general construction as a foundational gap. Do not patch only one existing example. |
| `POL-MATH-013` | Keep axiomatic truths distinct from runtime algorithms. |
| `POL-MATH-014` | Use an inspected theorem to justify the owning implementation. Cite it in source documentation and encode only its mathematical consequence. Never use the citation or theorem prose as runtime validation. |
| `POL-MATH-015` | Treat a form as a callable object of its fixed-endpoint morphism category `Mor(C)(A, B)`. A matrix can represent a form but cannot define the general notion. |
| `POL-MATH-016` | Refine a result into a property subcategory when its defining construction, an exact computation, an explicit hypothesis, or an inspected theorem establishes the property. Runtime derivation is not required for a theorem-backed fact. |
| `POL-MATH-017` | Return an object in the strongest category established by available mathematics. Never represent mathematical evidence with certificate classes, proof records, prose fields, opaque proof tokens, marker objects, or justification wrappers. |
| `POL-MATH-018` | Prefer kernels, cokernels, exact sequences, fibers, cofibers, pullbacks, limits, and colimits over element-wise definitions. |
| `POL-MATH-019` | State each public definition so it remains meaningful in a category without elements. Treat element-wise formulas as implementations or consequences. |
| `POL-MATH-020` | Treat one Python realization in different categories as different mathematical objects when their structure maps differ. |
| `POL-MATH-021` | Preserve the base category and structure morphism in every parent, type, and morphism that depends on them. |
| `POL-MATH-022` | State the weakest algebraic hypotheses that make a definition or algorithm valid. |
| `POL-MATH-023` | Open and inspect a mathematical source before adding a definition or citation. Record the exact theorem, section, table, or page that supports it. |
| `POL-MATH-024` | Treat definitionally known and theorem-established values as exact knowledge. When no runtime algorithm can derive the value, the owning construction supplies the typed mathematical conclusion directly. The inspected theorem justifies that implementation in source documentation; Python does not prove it. |
| `POL-MATH-025` | Return `Unknown` only when defining data, explicit hypotheses, construction theorems, inspected sources, and available exact algorithms do not decide the proposition. The absence of a Python derivation does not make a theorem-established fact unknown. Never convert `Unknown` to a Boolean through an unrelated proxy. |
| `POL-MATH-026` | A runtime API never accepts, stores, inspects, or branches on prose that purports to establish a mathematical proposition. This ban includes arguments or fields named `theorem`, `proof`, `certificate`, `citation`, `justification`, `evidence`, `trusted_reason`, and every renamed equivalent. |
| `POL-MATH-027` | Renaming theorem prose as metadata, an opaque token, a marker type, a record, or a callback that returns the same text does not make it mathematical evidence. Runtime evidence must be typed mathematical data, an exact predicate result, an explicit hypothesis, or a construction rule. |
| `POL-MATH-028` | A theorem-backed method constructs its result directly in the established property category. That category placement is the typed mathematical conclusion. The citation remains documentation. Runtime stores no proof text or fabricated `Decision`. |
| `POL-MATH-029` | For a `Decision`-valued proposition, only the value `True` establishes the proposition. Tests such as `decision is not False`, truthiness, fallthrough, and absence of rejection never turn `Unknown` into evidence. An explicit hypothesis or construction theorem is a separate source of knowledge. |
| `POL-MATH-030` | Prefer a defining construction or theorem over exhaustive verification, even when verification terminates. Finiteness alone does not justify enumeration when the construction already establishes the property. |
| `POL-MATH-031` | Make a mathematical fact explicit through the semantic value that states it: category placement, an exact type, a defining morphism, a functor, a universal construction, a named mathematical construction, an exact predicate result, or an active-session assumption. Never create runtime metadata merely to repeat that fact. |
| `POL-MATH-032` | Treat construction authority as the category, functor, universal construction, or named method whose definition establishes the result. This authority is static mathematical ownership, not runtime data. Never pass, store, register, or inspect an authority token, authority object, marker, or callback to authorize category refinement. |
| `POL-MATH-033` | Treat ordinary category theory and the stated mathematical definitions as the source model. A missing, unclear, or failing Python representation does not make the mathematics unresolved. Derive the representation from the definition, or report the missing foundational category, functor, morphism, construction, or type. |
| `POL-MATH-034` | Represent most mathematical truth-valued operations as owned predicates. Applying a predicate constructs its proposition; `ask()` returns its decision through the predicate's registered computational routes. Predicate application and `ask()` are the complete public predicate surface. A specification can declare a direct decision only for a total exact operation whose public result is itself a decision. |
| `POL-MATH-035` | An assertion on an applied predicate must use `assert ask(proposition) is True`. An assertion records known truth; it must not use the proposition's Python truth value. A direct exact decision needs no additional `ask()` call. |
| `POL-MATH-036` | Treat Sage as an implementation and computation system, not as a proof assistant for category theory or homotopy theory. The repository never tries to prove or certify categorical laws, universal properties, coherence, equivalences, or property implications. |
| `POL-MATH-037` | Trust the code writer to choose the correct category or property subcategory from external mathematics. Constructing a value directly in that category is the repository assertion of the stated theorem. The constructor performs no proof, certification, search, or validation of that theorem. |
| `POL-MATH-038` | Express every categorical-core requirement through standard category theory or homotopy theory before choosing a Python mechanism. Use named categories, functors, natural transformations, fibrations, Kan extensions, universal constructions, and their compositions. Do not replace a missing mathematical construction with a verifier or certificate system. |
| `POL-MATH-039` | Make the categorical core independently auditable by mathematicians. Theory code must expose the standard definition, its defining data, and the construction line that asserts each nontrivial categorical property. Keep reflection, dispatch, transport, and computation representations outside that mathematical reading path. |
| `POL-MATH-040` | Support each nontrivial categorical declaration with an inspected external source. Use an exact theorem, definition, section, page, tag, or stable link from a textbook, a relevant item in the local Zotero library, nLab, the Stacks Project, Kerodon, or a primary paper. Put the citation on the construction line or in its immediate source documentation. |
| `POL-MATH-041` | Treat citations, tests, runtime checks, and successful computations as aids to human audit. None certifies the categorical mathematics. The typed construction records what the writer asserts; the source lets a mathematician audit that assertion. |
| `POL-MATH-042` | Register a computational route only for a predicate with an exact algorithm on its declared semantic domain. Never add a route that purports to prove a general category-theoretic property. Keep unsupported decisions `Unknown`. |
| `POL-MATH-043` | Treat `Cat` as an abstract universe whose foundation is unspecified. Use only the structure that the repository explicitly declares. A declared ordinary or 2-categorical operation does not select a set-theoretic, simplicial, enriched, or higher-categorical realization. |
| `POL-MATH-044` | A mathematical term imports only its explicit repository definition. Do not infer surrounding theory, laws, properties, or constructions from the term alone. |

For example, an owned constructor for `RR` records its cardinality as $2^{\aleph_0}$.
The implementation cites the supporting theorem in source documentation.
Runtime stores the typed cardinality; it does not derive uncountability or carry theorem prose.

### Trust boundary for the categorical core

The categorical core is executable mathematical notation. It is not a formalization in
a proof assistant. Sage cannot certify that an arbitrary functor is full, that a square
is a pullback in every model, or that a declared universal construction satisfies its
universal property.

The code writer determines these facts from external mathematics. The writer then uses
the constructor of the exact category that states the fact. For example, a known full
functor is constructed through `Fun(C, D).Full()`. That call asserts fullness. It does
not run a fullness test or create a proof object.

When the assertion is not immediate from the standard definition, place an exact source
reference on that construction line or in its immediate documentation. Suitable sources
include textbooks and papers in the local Zotero library, nLab, the Stacks Project,
Kerodon, and primary arXiv papers. Inspect the cited statement before using it.

A mathematician audits the core by comparing its categories, morphisms, functors, natural
transformations, universal data, and compositions with those sources. Keep the code in
that order. Do not insert certification machinery between the mathematical definition
and its typed construction.

## Predicates, hypotheses, and assumptions

An applied predicate is a symbolic proposition with typed mathematical arguments, such as `order_preserving(f)`.
The active Sage or SymPy session is the mathematical assumption context.
A predicate handler is an exact computation or inference rule for specified semantic types.

| ID | Policy |
| --- | --- |
| `POL-ASSUME-001` | Give every assumable proposition an owned mathematical definition. Represent it by a property category or an owned predicate. |
| `POL-ASSUME-002` | Use SymPy predicates or Sage and Maxima declarations for bespoke runtime assumptions. Do not implement an ad hoc assumption store. |
| `POL-ASSUME-003` | In a SymPy backend, subclass `Predicate` and register the bespoke predicate on `Q`. Register typed handlers for exact evaluation. |
| `POL-ASSUME-004` | Store interactive hypotheses as applied predicates in the active Sage or SymPy assumption state. Let `ask()` read that standard global state. Translate SymPy `None` to Sage's `sage.misc.unknown.Unknown` singleton. Use that singleton directly. Never define or export a repository-local `Unknown` class, enum, sentinel, or replacement singleton. Never create or pass a repository-owned assumption-context object. |
| `POL-ASSUME-005` | In a Sage symbolic backend, define a bespoke positive property as a user-defined Maxima feature. Use `GenericDeclaration` for Maxima-representable symbols and functions. |
| `POL-ASSUME-006` | Maxima `featurep()` returns `false` when a feature is not established. Translate this result to `Unknown` unless an exact rule establishes falsity. |
| `POL-ASSUME-007` | `assume(P(x))` supplies the hypothesis and immediately invokes the constructor of the property subcategory defined by `P`. It refines the same owned value without running the decision procedure. |
| `POL-ASSUME-008` | A predicate handler returns `True` only when its exact rule establishes the proposition. Category placement and an active-session assumption short-circuit that handler. Without either source or an exact rule, return `Unknown`. |
| `POL-ASSUME-009` | Keep engine predicate representations inside the backend. Public APIs use owned categories, applied predicates, the standard session-level `assume()` operation, and `Decision`. |
| `POL-ASSUME-010` | A construction-owned theorem does not enter the assumption state. Its implementation constructs directly in the property subcategory under `POL-MATH-028`. |
| `POL-ASSUME-011` | Backend and theory code never call `assume()` to justify a result. They construct directly in the property subcategory already established by their computation, definition, or theorem. |

For a semantic morphism $f:P\to Q$, `order_preserving(f)` states that $f$ preserves the two owned orders.
A bare Python callable cannot state this proposition because it does not own the domain and codomain.

In a SymPy backend, `Q.order_preserving(f)` is an applied bespoke predicate.
Adding it to the active assumption state records the session hypothesis.
The public `assume(order_preserving(f))` operation then refines the owned morphism through
the constructor of its order-preserving property category.
A registered handler can instead establish the proposition for supported semantic morphism types.
When that handler returns exact `True`, it invokes the same property-category constructor.

In a Sage backend, a user-defined Maxima feature can record the corresponding positive symbolic hypothesis.
This declaration mechanism does not provide a proof or a general inference rule.

See the official documentation for [SymPy predicates and assumptions](https://docs.sympy.org/latest/modules/assumptions/index.html), [Sage symbolic assumptions](https://doc.sagemath.org/html/en/reference/calculus/sage/symbolic/assumptions.html), and [Maxima features](https://maxima.sourceforge.io/docs/manual/maxima_singlepage.html).

## Semantic representations

| ID | Policy |
| --- | --- |
| `POL-REP-001` | Treat Sage vectors and matrices only as private computation representations. The owned linear-algebra object is always a tensor. |
| `POL-REP-002` | Accept and return the semantic mathematical object at every public API. |
| `POL-REP-003` | Compare tensor elements through their parent and element interface, not by unwrapping coordinate data. |
| `POL-REP-004` | Compare and compose morphisms as morphisms, not by unwrapping their representing matrices. |
| `POL-REP-005` | Expose `f.kernel()`, `f.image()`, and `f.cokernel()` as semantic objects with their defining morphisms. |
| `POL-REP-006` | Ask `f.is_surjective()` instead of testing whether a presentation of `f.image()` is isomorphic to `f.codomain()`. |
| `POL-REP-007` | Treat a bilinear form as a callable hom element encoded by its Gram tensor. |
| `POL-REP-008` | Encode every linear-algebra element as a tensor. A vector or matrix notation does not create another semantic type. |
| `POL-REP-009` | Lower a tensor to a Sage computation representation once, inside one private computation boundary. |
| `POL-REP-010` | Keep matrix algorithms behind private hooks such as `_kernel_matrix_`. Do not expose those hooks to callers or tests. |
| `POL-REP-011` | Reconstruct the tensor, semantic object, or morphism before returning from a private computation. |
| `POL-REP-012` | Do not reinterpret a list, tuple, or numerical vector as a module, algebra, lattice, or tensor element. |
| `POL-REP-013` | Form `sum(a_i * g_i)` from semantic module generators when a finite linear combination is required. |
| `POL-REP-014` | Do not provide a coefficient-vector helper that bypasses construction from semantic module generators. |
| `POL-REP-015` | Type a module morphism by its semantic morphism and tensor element. Keep any Sage matrix realization private and unexported. |
| `POL-REP-016` | Implement scalar change and other functors on tensors, semantic objects, and morphisms. Choose a private computation representation only after the functor acts. |
| `POL-REP-017` | Define the tensor model at the module `ElementType` layer. Every module element has tensor valence `(p, q)`. |
| `POL-REP-018` | Make `tensor()` the fundamental linear-algebra constructor. It accepts valence `(p, q)`, a base ring, and multi-indexable coefficient data. |
| `POL-REP-019` | Shadow Sage's `vector()` and `matrix()` constructors. Make both delegate to `tensor()` with the corresponding valence. |
| `POL-REP-020` | Return tensor elements from `vector()` and `matrix()`. Do not expose Sage vector or matrix elements through the owned API. |
| `POL-REP-021` | Require tensor coefficient data to support one index per tensor slot. Keep storage order private to the tensor implementation. |

## Computation-engine encapsulation

| ID | Policy |
| --- | --- |
| `POL-ENGINE-001` | Define the public API entirely from the owned categorical mathematics. A computation engine supplies private realizations and algorithms only. |
| `POL-ENGINE-002` | Keep every engine type, constructor, method name, exception, return convention, and storage choice behind a private computation boundary. |
| `POL-ENGINE-003` | Return owned categories, objects, elements, morphisms, and functors from every public operation. Reconstruct the semantic result before it crosses the computation boundary. |
| `POL-ENGINE-004` | Expose a set-theoretic image as `f.image()` and a predicate subobject as `X.subset_from(predicate)`. Keep constructors such as Sage or SymPy `ImageSet` and `ConditionSet` private. |
| `POL-ENGINE-005` | Let categorical construction data select refinements and additional methods. An image subobject can retain its defining morphism and inherit operations owned by the corresponding image-subobject category. |
| `POL-ENGINE-006` | Expose no engine selection or dispatch. The category-owned method chooses and uses its private computation directly. Public signatures, return types, representations, documentation examples, and exceptions use only owned mathematical notions. |
| `POL-ENGINE-007` | Keep public semantics independent of computation technology. Never add an engine interface, registry, selectable backend, replaceability layer, or competing implementation class. |
| `POL-ENGINE-008` | Write tests, notebooks, and downstream packages against the owned semantic API. Do not import, inspect, or assert engine implementation types or constructors. |
| `POL-ENGINE-009` | Do not re-export an engine API, imitate its naming scheme, or let its available operations determine the owned public method surface. |
| `POL-ENGINE-010` | Translate engine-specific partial results into the owned result type, including `Unknown` for unresolved semantic predicates. |
| `POL-ENGINE-011` | Treat a timeout, crash, incomplete computation, or indeterminate engine verdict as establishing no mathematical result. It cannot justify category refinement or a Boolean answer. |
| `POL-ENGINE-012` | Treat an engine as a private source of representations and algorithms. It never owns a parallel `ObjectType`, `ElementType`, `MorphismType`, public method catalogue, or semantic implementation surface. |
| `POL-ENGINE-013` | Distinguish a modeled mathematical realization functor from a private computation representation. A private Sage value, cache, or algorithm call requires no functor, category, compiler binding, or natural transformation. |
| `POL-ENGINE-014` | A category-owned method can call a fixed engine through its private computation boundary. This is dependency use, not runtime backend selection or public engine dispatch. |
| `POL-ENGINE-015` | Permit any suitable private computation technology. An implementation can use Sage, SymPy, NumPy, a maintained domain package, custom research code, Cython, a shell program, or another language system. None of these choices changes the owned public class or API. |
| `POL-ENGINE-016` | Select private algorithms inside the owning method from established mathematical hypotheses and available representations. Algorithm selection does not create multiple implementations of the mathematical object. |

See [Leaf category implementations](specs/leaves.md) for the complete engine boundary,
the rejected mirrored-surface design, and the required reconstruction of owned results.

## Algebraic generality

| ID | Policy |
| --- | --- |
| `POL-GEN-001` | Parameterize each algebraic-object category by all ambient categorical data in its definition. A typed base object supplies its owning category. It does not determine an independent actegory, action, tensor product, or coherence data. |
| `POL-GEN-002` | Do not hard-code `ZZ` when the definition or algorithm works over a PID, integral domain, or commutative ring. |
| `POL-GEN-003` | Select algorithms by proved ring properties, not by identity checks against `ZZ`, `QQ`, or another named ring. |
| `POL-GEN-004` | Do not import vector-space equivalences into modules over a general ring. |
| `POL-GEN-005` | Do not infer that a module is zero from `M.rank() == 0`; a nonzero torsion module can have rank zero. |
| `POL-GEN-006` | Do not infer that `ker(f) = 0` from a zero matrix-nullspace rank; a nonzero torsion kernel can have rank zero. |
| `POL-GEN-007` | Use matrix-rank criteria for injectivity, surjectivity, or exactness only when the required field hypotheses are established. |
| `POL-GEN-008` | Use the semantic zero-object, kernel, cokernel, and exactness predicates supplied by the relevant category. |
| `POL-GEN-009` | Treat one Python realization with different base objects, ambient categories, actions, or structure morphisms as different mathematical objects. Relate them through the applicable scalar-change functor. |
| `POL-GEN-010` | Preserve infinite algebra-generation data. Do not force a finitely generated presentation onto an algebra such as `QQ` over `ZZ`. |
| `POL-GEN-011` | Keep rank, dimension, cardinality, and minimum number of module generators distinct. Use each invariant only under its defining hypotheses. |
| `POL-GEN-012` | Assume finiteness only when the mathematical definition or a selected property subcategory requires it. Define the arbitrary small indexed construction first and obtain its finite form by restriction. |
| `POL-GEN-013` | Place a coefficient family with potentially infinite support in the appropriate formal power-series ring. Do not declare its sum to be a polynomial without established finite support. |
| `POL-GEN-014` | Recover polynomials as the finitely supported elements of a formal power-series ring. Make polynomial-valued methods restrictions of the general power-series-valued construction. |
| `POL-GEN-015` | Return a lazy iterator when a method enumerates a result family and materialization is not part of the mathematics. Do not encode an unproved finiteness assumption by returning a list or tuple. |
| `POL-GEN-016` | For a supplied tensor category `V`, let `Magmas(V)` own magma objects. For a supplied monoidal category `V`, let `Monoids(V)` own monoid objects. When `V` is cartesian monoidal, let `Groups(V)` own group objects. The applicable tensor product, unit object, associator, unitors, and cartesian structure are part of `V`'s retained structure. |
| `POL-GEN-017` | Let `Semirings(C)` and `Rings(C)` own the corresponding internal algebraic models in a supplied category `C`. The owning specification states the products or monoidal structures and every strictness or coherence requirement. `Semirings(Sets())` and `Semirings(Cat())` are different categories. |
| `POL-GEN-018` | Given a monoidal category `M`, a chosen left `M`-actegory `C`, and `A in Monoids(M)`, let `Modules(A, C)` own pairs `(X, rho)` with `X in C` and `rho: A bullet X -> X` satisfying the unit and action diagrams. Retain `M`, `C`, the action functor, and `A`; never infer `C` from `A`. |
| `POL-GEN-019` | Define `Algebras(R, C)` only when `Modules(R, C)` has a supplied monoidal structure `V_R`. Present it through a retained equivalence to `Monoids(V_R)`. The general monoid category owns multiplication, unit, and monoid laws. Reach the module carrier through the monoid and magma carrier functors. A noncommutative base requires a supplied monoidal category of bimodule objects. |
| `POL-GEN-020` | State each algebraic family's definition once, at the family, over its ambient parameter. Fixing the ambient gives an instance of that definition, never a specialization of it, and no ambient is the definition. Name each instance with its own source. A downstream specification cites the family definition and states only its own new mathematics. |
| `POL-GEN-021` | Keep every algebraic law an equation between morphisms of the supplied ambient. Do not weaken a law to an isomorphism or a coherence datum. A structure map is a morphism out of a tensor or cartesian product; it presents no diagram, retains no injection or projection, and carries no cone. At `C = Cat()` the laws are equalities of functors. |

For a family \((X_i)_{i\in I}\), the product \(\prod_{i\in I}X_i\) is the limit of the corresponding discrete diagram.
The foundational product constructor therefore accepts an arbitrary small index set \(I\).
A finite product is its restriction to `I in Sets().Finite()`.
A constructor based on a finite tuple of factors cannot express the integral adeles \(\prod_p\mathbb Z_p\).

Likewise, \(\sum_{n\in\mathbb N}a_nt^n\) belongs to \(R[[t]]\) for a general coefficient family.
It belongs to \(R[t]\) after the support of \((a_n)\) is known to be finite.
Thus the public operation is `poincare_series()`, not `poincare_polynomial()`.
The series remains defined when every grading has nonzero cohomology and becomes a polynomial when its support is finite.

## Forms and lattices

| ID | Policy |
| --- | --- |
| `POL-FORM-001` | Model an `R`-lattice as a finitely generated projective `R`-module `M` with the specified form, not as a free `ZZ`-module. |
| `POL-FORM-002` | Model a `W`-valued bilinear form as a morphism `M tensor_R M -> W`, encoded by its Gram tensor. |
| `POL-FORM-003` | Use “inner product” only for a positive-definite symmetric bilinear form. |
| `POL-FORM-004` | Do not assume that a lattice is positive definite, embedded in a vector space, free, based, or unimodular. |
| `POL-FORM-005` | Distinguish left and right radicals for a nonsymmetric bilinear form. |
| `POL-FORM-006` | Define orthogonal complements, norms, and reflections only under the symmetry and nondegeneracy hypotheses they require. |
| `POL-FORM-007` | Determine definiteness from the exact behavior of the form on elements, not from floating eigenvalues or numerical spectra. |
| `POL-FORM-008` | Use exact coefficient rings and exact arithmetic for form and lattice predicates. |
| `POL-FORM-009` | Choose the minimal exact coefficient extension required by the mathematical object. Do not approximate algebraic coefficients by floats. |
| `POL-FORM-010` | Use “Gram tensor” for the tensor that encodes a bilinear form. Keep its chosen-basis coefficient data inside that tensor. |

## Category ownership and inheritance

| ID | Policy |
| --- | --- |
| `POL-CAT-001` | A category owns its constructors, local operations, and implementation types. `C(...)` is the public construction dispatcher for objects of `C`; it delegates to exact private constructor routes selected from the supplied semantic data. |
| `POL-CAT-002` | Use `ObjectType`, `ElementType`, and `MorphismType` for compiled category-owned implementations. The kernel owns `Cat`; every repository category uses `Cat().ObjectType`, every functor uses `Cat().MorphismType`, and every natural transformation uses `Fun.MorphismType`. Compile `Cat().ElementType` as the common generalized-point root before `Cat().ObjectType` and `Cat().MorphismType`; every `C.ObjectType` refines it at stage `1`, and every `C.MorphismType` refines it at stage `[1]`. Bootstrap uses distinct local declarations, one stable point-kernel token, and a preallocated compiled `Cat().ElementType` root, then binds the public names. `Cat()` is an object of `Cat()` by runtime convention: size is outside the model, no kernel operation quantifies over or scans the objects of `Cat()`, and `Cat().category() is Cat()` is never read as an existence theorem. |
| `POL-CAT-003` | Apply the same inheritance mechanism to objects, elements, and morphisms. |
| `POL-CAT-004` | A category level defines only the structure and operations introduced at that level. |
| `POL-CAT-005` | A leaf category knows only itself and its immediate structural functors. |
| `POL-CAT-006` | Do not copy or forward methods already owned by another category. |
| `POL-CAT-007` | Do not build a second Python class graph to duplicate the category graph. |
| `POL-CAT-008` | Compile category declarations into the public method surface. Do not generate opaque method bodies. |
| `POL-CAT-009` | Give a local declaration precedence over inherited declarations. |
| `POL-CAT-010` | Deduplicate routes that reach the same declaring category and implementation. |
| `POL-CAT-011` | Reject unrelated method-name collisions during method compilation. |
| `POL-CAT-012` | Detect a structural-image or construction-input mismatch during construction or the first public functor application, not during method compilation. Traverse every route to a reachable category in `structure_functors()` declaration order, retain the first image and input, and require each later route to supply the same objects by identity. A mismatch raises a construction-defect error naming the source construction, both routes, and the shared ancestor category; nothing is repaired or replaced. Natural transformations are trusted constructions and never compiler proofs; they never identify or rewrite routes. |
| `POL-CAT-013` | Maintain one canonical implementation in each category reached from a public object. |
| `POL-CAT-014` | Expose inherited operations directly on the public mathematical object. |
| `POL-CAT-015` | Keep functor images inspectable when their mathematical role matters. |
| `POL-CAT-016` | Derive supercategory information from the selected structural functors. Do not maintain a second inheritance registry. |
| `POL-CAT-017` | Put an axiom at the highest category that can state it. |
| `POL-CAT-018` | Distinguish a property subcategory from a category whose objects contain chosen data. Membership in a property subcategory records a proposition, not a selected witness. |
| `POL-CAT-019` | Require chosen data only when it is part of the mathematical structure. Do not require or store a witness merely because an object belongs to a property subcategory. |
| `POL-CAT-020` | Make every construction path account for the defining obligations of its result category. Declare the typed conclusion of its construction theorem, compute the obligation exactly, or accept it as an explicit hypothesis. Runtime proof is not required. Never infer an obligation from an unrelated property. |
| `POL-CAT-021` | Make `Mor(n, C)` for every `n >= 0`, its fixed-endpoint subcategories `Mor(C)(A, B)`, and its property subcategories categories and therefore objects of `Cat`. `Mor(0, C) = C`, `Mor(C) = Mor(1, C)`, and `Mor(n + 1, C) = Mor(Mor(n, C))`. Make every functor an object of `Fun = Mor(Cat())`, and identify `Fun(C, D)` with `Mor(Cat())(C, D)`. |
| `POL-CAT-022` | Keep the hom object category-valued at the `Cat` level: `Mor(C)(A, B)` is the full subcategory of `Mor(C)` on the morphisms `A -> B`. `Fun(C, D) = Mor(Cat())(C, D)` has functors as objects and natural transformations as morphisms. For a 1-category `C`, `Mor(C)` is discrete. A hom object becomes a function set only through the exact structure supplied by `Sets()`. |
| `POL-CAT-023` | Supply `Mor(n, C)`, `Mor(C)(A, B)`, `Mor(C).Endomorphisms()`, `Mor(C).Automorphisms()`, and `Fun([1], C)` at the `Cat` level. A category has two call forms: `K(data)` constructs an object of `K`, and `Mor(K)(A, B)(data)` constructs a morphism `A -> B`. `Mor(K)(A, B)` is the sole fixed-endpoint spelling, and every property subcategory `P` of `Mor(K)` applies endpoints by the same dispatch, `P(A, B) = Mor(K)(A, B).P()`. `Y ** X` denotes only the exponential object. |
| `POL-CAT-024` | Make the generic `MorphismType` store its endpoints and expose them through `domain()` and `codomain()`. |
| `POL-CAT-025` | Implement a general morphism predicate as containment in its property subcategory of `Mor(C)`, such as `f in Mor(C).Monomorphisms()`. |
| `POL-CAT-026` | Represent a covering object of `Y` as `(X, p: X -> Y)` with `p` an epimorphism. The morphism `p` alone is not the object. |
| `POL-CAT-027` | Never assume that an arbitrary mathematical entity is a set. Treat it as a category or as an object in its stated category. |
| `POL-CAT-028` | Keep `Mor(C)(X, Y)` category-valued at the general level. Obtain a set of morphisms only through an explicit set-valued construction with the required hypotheses. |
| `POL-CAT-029` | Distinguish an internal Hom object from its global morphisms. Apply the relevant global-sections, object-set, or underlying-set functor explicitly. |
| `POL-CAT-030` | Establish `X in Sets()` or apply an explicit functor to `Sets()` before using elements, membership, cardinality, enumeration, subsets, or set equality. |
| `POL-CAT-031` | Treat an unjustified reduction to `Sets()` as a foundational error. Rebuild every dependent definition, type, morphism, and conclusion in the correct category. |
| `POL-CAT-032` | Put an operation at the most general category where its mathematical result can be declared. Partial knowledge or the absence of one general algorithm does not justify moving the operation to a narrower category. |
| `POL-CAT-033` | Define a subcategory only for a genuine mathematical property, structure, or declared algebraic operation role. Additive and multiplicative axiomatic refinements can select the role of one neutral operation. Never define a subcategory only to select, store, or expose an implementation. |
| `POL-CAT-034` | Retired. Use `POL-API-021`. |
| `POL-CAT-035` | Treat an implementation-shaped category or object name as evidence that an established mathematical owner or construction has been missed. Resolve the object, morphisms, and construction before adding terminology. |
| `POL-CAT-036` | Use mathematically standard, total category constructors. Give genuinely different mathematical input forms their own explicit constructors and required inputs. Do not create constructor families merely to distinguish checked, assumed, or theorem-established evidence for one property. |
| `POL-CAT-037` | Place each constructed result in every property subcategory established by that named route and its required inputs. |
| `POL-CAT-038` | Make each property subcategory's constructor its standard public trust boundary. Choosing that constructor asserts the defining property and constructs or self-refines the same owned value in that subcategory. |
| `POL-CAT-039` | Make each named construction route discoverable through its parameterized category, such as `Sets()`, `Monoids(V)`, `Semirings(C)`, `Rings(C)`, `Modules(A, C)`, and `Algebras(R, C)`. Keep every ambient category and route selection explicit at the call site. |
| `POL-CAT-040` | For \(f:X\to Y\), evaluate `f` only on elements of `X` and return elements of `Y`. A morphism never accepts or returns an unowned Python value. |
| `POL-CAT-041` | Construct or coerce raw representations into elements of the appropriate category objects before morphism evaluation. Keep this conversion outside the morphism. |
| `POL-CAT-042` | Make the operations of `Mor(C)(X, Y)` verify that each element's owning object lies in the base category and that evaluation respects the declared domain and codomain. |
| `POL-CAT-043` | Let a named property subcategory and its owned predicate state one mathematical condition. Use the predicate to request a decision and self-refinement. Use containment to ask whether the value already has that categorical placement. Never replace either with an unrelated invariant comparison. |
| `POL-CAT-044` | Put each exact decision procedure behind the owning mathematical predicate. Applying the predicate returns its proposition. `ask()` evaluates that proposition. Exact `True` invokes the property-subcategory constructor. Category placement then makes later evaluation return `True`. Do not override the predicate with a Boolean method or duplicate the computation in `__contains__`. |
| `POL-CAT-045` | Present every derived object through the complete public interface of the category in which it lives. Its construction can add methods but never replace or duplicate the inherited interface. |
| `POL-CAT-046` | Make a universal-construction category the full subcategory of its ambient category on the constructed objects, with the retained identity-on-values inclusion as its selected structural functor. For each input diagram `D`, the constructor returns one value: the constructed object itself, an object of the ambient category with that category's whole method surface, placed in the family. The family retains the universal data of each diagram: `D`, its defining morphisms, and its universal maps. Distinct diagrams have distinct universal data, including when the objects they construct are identical. Use a separate property subcategory when the mathematics states only existence or closure under that construction. |
| `POL-CAT-047` | Decide inheritance functors case by case. Select one only when standard mathematical practice treats the source object as an object of the target category with additional structure. |
| `POL-CAT-048` | Treat structure that an object has, rather than structure that it is, as attached mathematical data. Expose that object by its exact mathematical name without grafting its full method surface. |
| `POL-CAT-049` | Scrutinize every public `underlying_*()` accessor. When the source is canonically a target-category object with additional structure, expose the target interface directly through inheritance instead of requiring accessor indirection. |
| `POL-CAT-050` | Define every axiomatic or functorial category constructor at the highest categorical level where its mathematical meaning exists. Define it once and inherit it throughout the category graph. `C.Products()`, `C.Coproducts()`, `C.Limits(I)`, `C.Colimits(I)`, and the other universal-construction interfaces are defined once on `Cat().ObjectType` and apply when `C` is `Cat()`, `Sets()`, `Fun(C, D)`, or any other category. |
| `POL-CAT-051` | Let a construction subcategory exist without asserting that it is nonempty or that its parent category is complete or cocomplete. Do not require a decision procedure for those properties. |
| `POL-CAT-052` | Make generic category constructors propagate through selected structural functors. A descendant category supplies no boilerplate merely to form the inherited construction subcategory. |
| `POL-CAT-053` | A leaf never writes Python subclass relations between category-owned roles. The kernel makes each compiled `C.ObjectType`, `C.ElementType`, and `C.MorphismType` a Python subclass of the corresponding compiled roles reached through selected structural functors. A root object role continues through `ObjectOfCategory` to the one compiled `Cat().ElementType`; a root morphism role continues through `MorphismOfCategory` to that same root. An ordinary element role continues through its own element chain to `Cat().ElementType`. These generated bases are the runtime form of the functor graph and the two stated stage refinements. |
| `POL-CAT-054` | Declare every relation between categories by a selected structural functor, including an inclusion, identity, or other trivial functor. A category without these functors is disconnected from the owned category graph. |
| `POL-CAT-055` | Treat a failed structural functor or method compiler as a foundational defect. Its failure does not permit explicit subclassing or another inheritance path. |
| `POL-CAT-056` | Apply the structural-functor framework to every functorial, universal, and morphism-based construction. Each construction creates and retains its distinct inclusion, projection, or evaluation functors through `Fun(Source, Target)`. The endpoint pair never selects one functor. |
| `POL-CAT-057` | Give every category its own object, element, and morphism role declarations. A full property subcategory self-refines the same owned value and places its category-owned role first in the Sage dynamic MRO. Do not allocate a wrapper or second owned value for that refinement. |
| `POL-CAT-058` | Compile `ElementType` inheritance from selected structural functors by the same mechanism used for `ObjectType` and `MorphismType`. A subcategory never reuses another category's element implementation type. |
| `POL-CAT-059` | Let each category add local methods to its `ElementType` while inheriting the complete applicable element interface through structural functors. Preserve the category-specific element type even when it adds no local methods. |
| `POL-CAT-060` | Every property subcategory declares one owned `is_X()` predicate method on its largest meaningful ambient category. Applying the method returns the category-owned proposition. `ask()` can use its computational routes and self-refine the ambient value. Category placement makes `ask()` return `True`; the method keeps the same proposition-valued contract. The method is a required part of the property declaration and its public predicate surface. |
| `POL-CAT-061` | Compile an inherited declaration into the descendant role MRO. Execute it on the original descendant instance. Before the local constructor chain starts, compute the declaring role's construction input through every complete selected-functor route. For an object or morphism, also compute the one `Cat().ElementType` stage input used by the common MRO root. Never replace the receiver merely to call the method. |
| `POL-CAT-062` | Make inherited calls use ordinary Python inheritance. The receiver and arguments remain the supplied values. A method that needs an object in its declaring category uses the canonical image retained in that role's private state. A leaf that changes the mathematics overrides the method or adds its own. |
| `POL-CAT-063` | Preserve object, element, morphism, iterator, and mathematical collection roles in compiled method signatures. Derive these roles from the owning implementation role and exact declared types. Do not infer them from runtime registries, `isinstance`, method names, descriptors, or duplicate per-method metadata. |
| `POL-CAT-064` | Compile special methods and ordinary methods through the same dynamic MRO. Do not add per-method wrappers. Generated role-constructor wrappers are part of class construction, not method dispatch. |
| `POL-CAT-065` | Return a lazy result and an owned collection exactly as the inherited method returns them, one value at a time. Do not wrap or relabel the collection or its items. |
| `POL-CAT-066` | Key structural images by the source value's public data: an object by its identity; a generalized element by its stage, defining morphism, and codomain; a morphism by its domain, codomain, and identity. Values with different stages, defining morphisms, or codomains never share a cached image. |
| `POL-CAT-067` | Apply the same property-constructor rule to the morphism categories `Mor(C)`. Direct property construction, an active-session assumption, exact computation, and construction-owned mathematics all invoke the same property-morphism constructor and self-refine the same owned morphism. |
| `POL-CAT-068` | Let `ask()` return `True` from category placement only when the value entered through its property-subcategory constructor under `POL-CAT-020` or `POL-CAT-067`. The public predicate continues to return its applied proposition. |
| `POL-CAT-069` | Give each property subcategory one constructor that trusts its defining property. Do not add checked, hypothesis-backed, or theorem-backed constructor families. An ambient value's owned predicate performs any check; `assume(P(x))` and exact `True` invoke the same property constructor; a named mathematical construction returns through it directly. |
| `POL-CAT-070` | Treat direct implementation construction, private constructors, inclusions, lifts, and internal helpers as category-entry paths. Each path selects the exact established property category through direct construction, an active assumption, exact computation, or construction-owned mathematics. Internal access is not an exemption. Call `_construct`, `ObjectType`, or another raw allocator only inside the owning category constructor after that target category has been established for the exact supplied value. |
| `POL-CAT-071` | Reject a selected structural edge when an inherited target role needs construction input and the functor supplies no exact typed conversion. Compute conversions along structural edges before the C3 constructor chain starts. Compute the common `Cat().ElementType` input directly from the root object's parent or the root morphism's parent and endpoints; this is the specified stage refinement, not a selected structural edge. Never derive a conversion from adjacent classes in the linear order. |
| `POL-CAT-072` | Preserve a collection's declared mathematical type and item role through ordinary inherited calls. Do not infer collection semantics from `Iterable` checks or assume that every lazy result contains elements. |
| `POL-CAT-073` | Treat `X in C` as the mathematical admissibility fact. Exact identity such as `X.category() is C` is an implementation fact and never triggers structural normalization. |
| `POL-CAT-074` | Preserve the strongest established category of every object. Do not replace it with an ancestor implementation merely to call an inherited operation. |
| `POL-CAT-075` | Treat the ordinary typed signature and executable body on the owning implementation class as the sole authoritative declaration of a method. Copy that declaration into its compiled role and derive every generated typing artifact from it. Never maintain a second description of its receiver, parameters, call shape, result, or mathematical roles. |
| `POL-CAT-076` | Keep mathematical type, Python call shape, and structural construction provenance distinct. Exact types state mathematical roles. The Python signature states positional, keyword, and variadic shape. Canonical-image and construction-input relations state structural provenance. No one of these facts can replace another. |
| `POL-CAT-077` | Determine method ownership from its definition on the category-owned implementation class and the selected structural functors. No decorator, marker, annotation payload, registry entry, or descriptor argument can create mathematical ownership or repair a missing category declaration. |
| `POL-CAT-078` | The owner of a mathematical fact is the category, object, morphism, functor, or universal construction whose definition states it. A metadata holder, descriptor, registry, adapter, backend, compiler component, or generated type is never its mathematical owner. |
| `POL-CAT-079` | Place every operation forced by category placement at the highest category that first guarantees it. The isomorphism category owns inversion; a chosen product owns `product_projection(i)` and its universal map. Descendants receive these operations through inheritance and never reconstruct them locally. |
| `POL-CAT-080` | Before placing code in a leaf, trace the complete public call from its mathematical owner through construction families, selected structural functors, compiled role inheritance, construction-input conversion, direct inherited execution, and the declared result. Perform this trace for objects, elements, and morphisms. A missing step is a foundational defect, not permission for a leaf implementation. |
| `POL-CAT-081` | Construct every owned value in the strongest property-based subcategory established by its defining construction, exact computation, or trusted programmer assertion. Never construct it weakly and recompute a property already known at construction time. |
| `POL-CAT-082` | Permit a category-owned predicate handler to return `True` when the construction or definition establishes that property for every value it builds. The public predicate still returns an applied proposition. The exact handler result invokes the same property-subcategory constructor; it is not a proof object, metadata field, or separate admission route. |
| `POL-CAT-083` | Represent a distinguished named mathematical object by its parameterized one-object category. Let that category own the object-specific declarations and selected structural functors that place its sole object in all established ambient and property categories. Each selected point functor supplies complete compiled roles, constructor conversions, and initialized ancestor state for its distinguished object. Install that placement by same-object refinement: extend each affected compiled role in place, preserve every existing role identity, descendant, and value, and run each newly required initializer once. A point category formed from a runtime object needs no construction order against its point-functor targets. |
| `POL-CAT-084` | If `C.P()` is a property subcategory and `D` has a selected structural inclusion into `C`, derive `D.P()` automatically as the corresponding narrowing of `D`. Define the property constructor once. Never require a descendant category to repeat its class, predicate, constructor, or transport wiring. |
| `POL-CAT-085` | Replace Sage's category-only `super_categories()` edges with `structure_functors()`. Return the complete tuple of immediate objects of `Fun = Mor(Cat())` selected for inheritance. Each entry is constructed by the category's defining presentation or through `Fun(self, Target)`. Selection is compiler input and does not define another kind of functor. Endpoints and object fields never determine a selected entry. See `specs/functor.md`. |
| `POL-CAT-086` | Make `Mor(C)(A, B)` a category for every `A, B in C`. Represent its inhabitation and emptiness as owned predicates. An unresolved decision leaves the morphism category symbolic; it never replaces that category with an empty category. |
| `POL-CAT-087` | Define a full subcategory from an object predicate `P` on `C`. Its objects are the objects of `C` satisfying `P`; its morphism categories `Mor(C.P())(A, B)`, identities, and composition are inherited definitionally from `C`. Construct its inclusion as `Fun(C.P(), C).FullyFaithful().inclusion()`. Follow [mathlib's `CategoryTheory.ObjectProperty.FullSubcategory` definition](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/ObjectProperty/FullSubcategory.html). |
| `POL-CAT-088` | Define the universal binary operators once at the categorical level, in two roles. On `Cat().ObjectType`, `C * D` is the product category `Cat().Products()((C, D))`, `C + D` the coproduct category, and `D ** C = Fun(C, D)`. On `Cat().ElementType`, for `X, Y in C`, `X * Y` is `C.Products()((X, Y))`, `X + Y` their coproduct, `X @ Y` their biproduct where declared, and `Y ** X` the exponential object where `C` is declared cartesian closed; each object operator takes its construction in the narrowest category containing both operands, and asserts that such a category exists. Identity of the two strongest placements is not the condition: a full subcategory's objects are objects of its ambient, so an object refined into `C.P()` and an object of `C` are both objects of `C` and their product is the product in `C`. An external pair is constructed explicitly as `(C * D)((X, Y))`. `Y ** X` is not a spelling of `Mor(C)(X, Y)`. Each universal construction retains its defining morphisms. Every descendant category uses the inherited operation directly. |
| `POL-CAT-089` | Define `Mor(C)` once in the kernel for every `C in Cat()`. Its objects are the morphisms of `C`, and its morphisms are the 2-morphisms of `C`; for a 1-category it is discrete. Endpoint application `Mor(C)(A, B)` is the full subcategory on the morphisms `A -> B`, one cached object per pair. Obtain `Fun = Mor(Cat())` from the same construction: its objects are functors, and `Fun(C, D) = Mor(Cat())(C, D)` has natural transformations as morphisms. The category whose objects are the morphisms of `C` and whose morphisms are commuting squares is the functor category `Fun([1], C)` from the walking arrow, with evaluation functors `ev_0, ev_1: Fun([1], C) -> C`; it is not a primitive. |
| `POL-CAT-090` | Define `Mor(Cat()).Full()`, `.Faithful()`, `.FullyFaithful()`, `.EssentiallySurjective()`, and `.Equivalences()` through the ordinary property-subcategory mechanism. Their owned `is_*()` methods return applied predicates. Direct construction, assumptions, category placement, and implications use the standard same-object refinement path. |
| `POL-CAT-091` | Register no computational handlers for functor fullness, faithfulness, full faithfulness, essential surjectivity, or equivalence. `ask()` uses property-category placement, active assumptions, and declared categorical implications. It returns `Unknown` when those sources do not decide the predicate. |
| `POL-CAT-092` | Define `Products()`, `Coproducts()`, `Subobjects()`, `Limits(I)`, `Colimits(I)`, and the standard dual constructions at the `Cat` level. Apply them to every category, including `Cat()` itself. Each limit or colimit family is indexed by one supplied shape `I in Cat()`; `C.Limits(Cat())` never denotes limits over all small shapes. A discrete diagram is a rule `i |-> X_i` on an index set; a Python sequence is the convenience form over `Discrete([n])`. Bicompleteness and cartesian closure of `Cat()` are trusted declarations attached to the constructors the kernel supplies; they assert nothing about a shape or category not supplied to a constructor. |
| `POL-CAT-093` | Give `C.Products().ObjectType` the method `product_projection(i) -> C.MorphismType`, indexed by the index set of its diagram. Give `C.Coproducts().ObjectType` the method `coproduct_injection(i) -> C.MorphismType`. For `C = Cat()`, these morphisms are functors. |
| `POL-CAT-094` | Let `P` be a chosen product and let `j: S -> P` present a subobject. Make the corresponding object of `Cat().Products().ChosenSubobjects()` retain `j`, and read `P` as its codomain. Define its `product_projection(i)` as `P.product_projection(i) after j`. Thus every such object has all component functors. Do not ask a leaf to repeat their maps. |
| `POL-CAT-095` | Present `C.SliceOver(x)` as the pullback in `Cat()` of `ev_1: Fun([1], C) -> C` along `x: 1 -> C`, and `C.CosliceUnder(x)` as the pullback of `ev_0` along `x`; a comma category `(F, G)` is the pullback of `(ev_0, ev_1): Fun([1], C) -> C * C` along `F * G`. Each retains its pullback projections; the varying object is the composite with `ev_0` or `ev_1`. Two distinct functors carry distinct lift data: `ev_1` is a fibration when `C` has pullbacks, with the cartesian lift of `f: y -> x` at `p: z -> x` given by pullback; the fixed slice projection `C.SliceOver(x) -> C` is a discrete fibration for every `C`, with the cartesian lift of `f: y -> z` at `(z, p)` given by precomposition, `(y, p compose f) -> (z, p)`. Retain each lift at its construction owner. |

Grounding examples:

- Limits, colimits, products, coproducts, tensor products, and direct sums declare their structural functors to the categories of their resulting objects.
  Their implementation types do not subclass the target category's implementation types.

- Subobjects, superobjects, covering objects, and covered objects retain the functors that select each stated component of their defining morphisms.
  Their implementation types do not obtain structure through Python subclassing.

- `Sets().Finite()` declares its inclusion functor to `Sets()` even when both categories use the same realization.
  The inclusion states the categorical relation that replaces a Sage `super_categories` declaration.

- An element of a finite set has type `Sets().Finite().ElementType`, not `Sets().ElementType`.
  The inclusion functor supplies the set-element interface to the finite-set element type.

- An element of a product has type `C.Products().ElementType`.
  It inherits the applicable `C.ElementType` interface and can add `factors()` to return its indexed component family.

- Cardinality belongs on every object of `Sets()` because every set has a cardinality.
  A constructor can supply exact or symbolic cardinal data.
  Pattern matching on available data can select a computation without defining a subcategory for its implementation.

- Every set can construct `X.subset_from(predicate)`.
  The result is a subobject \(A\hookrightarrow X\), including infinite examples such as the even or prime integers inside \(\mathbb Z\).
  A private representation can retain the predicate or other construction provenance for computation.
  `PropertySet` or `Sets.PropertyCategory()` does not name a mathematical class: every set can be characterized by a property.
  Such a name mistakes the construction of an ordinary subset for a new kind of set.

- `Sets().Finite()(members, cardinality)` requires the semantic data needed for a finite
  set and constructs directly in the finite-set subcategory.
  The countable and uncountable property subcategories own their corresponding constructors.

- Use `ask(X.is_finite())` when asking the owned predicate to decide finiteness and refine
  `X`. Use `X in Sets().Finite()` when asking whether that placement is already established.
  After refinement, category placement makes `ask(X.is_finite())` return `True`.

- Every `C in Cat` can form `C.Products()`.
  This subcategory can be empty, and its existence does not assert that `C` has all products.
  Thus `Modules(A, C).Products()` requires no module-specific reconstruction of the generic product category.

## Leaf-category encapsulation

| ID | Policy |
| --- | --- |
| `POL-LEAF-001` | Integrate a new leaf category by supplying its selected structural functors to known categories. These functors are the complete inheritance declaration. |
| `POL-LEAF-002` | Make a leaf constructor accept only its strongest minimal semantic datum. Recover every weaker component through the datum's domains, codomains, ambient products, defining morphisms, and selected structural functors. Never require an underlying set, module, ring, or other ancestor object as a second argument when the supplied relation, morphism, form, or structure map already determines it. |
| `POL-LEAF-003` | Explicitly construct and select each inclusion, projection, restriction, lift, or evaluation functor. Obtain it from the defining category construction or construct it through `Fun(self, Target)`. Define its object and morphism maps when its mathematical presentation requires them. |
| `POL-LEAF-004` | Make a realization constructor idempotent on an object already owned by its target category. In particular, `Sets(X)` returns `X` when `X in Sets()`. |
| `POL-LEAF-005` | Let the category compiler inherit the target categories' object, element, and morphism methods along selected structural functors. A leaf category defines no forwarding methods. |
| `POL-LEAF-006` | Treat a leaf implementation of an inherited operation as evidence of a missing structural functor, an incorrect functor image, or an operation placed at the wrong owner. |
| `POL-LEAF-007` | Permit a structural functor to land in a morphism category `Mor(C)` when the defining morphism determines the required inherited object data through its domain or codomain. |
| `POL-LEAF-008` | Confine private-field access to constructors and genuinely new functor maps that cannot recover their required defining data through owned semantic interfaces. A standard kernel functor never requires leaf access code. |
| `POL-LEAF-009` | Keep private representations out of inherited methods, public signatures, callers, tests, and downstream packages. A leaf-owned executable method can access a private representation inside its computation boundary. |
| `POL-LEAF-010` | Validate a leaf integration by calling inherited mathematical operations directly on its objects, elements, and morphisms through the compiled public surface. |
| `POL-LEAF-011` | Lift an inherited construction to a leaf category by specifying only how the leaf's additional structure acts on the inherited result and morphisms. Make this lift compatible with the selected structural functors. |
| `POL-LEAF-012` | Do not redefine the inherited construction's objects, elements, universal property, or general methods in a leaf subtree. Those remain owned by the category where the construction was introduced. |
| `POL-LEAF-013` | Design the kernel so leaf authors can treat inheritance and method compilation as established infrastructure. Adding a mathematical leaf must not require reading or modifying kernel code or kernel tests. |
| `POL-LEAF-014` | Ship and maintain a standard template for new leaf categories. The template contains only the category declaration, minimal constructor, selected structural functors, and sites for new methods. |
| `POL-LEAF-015` | Let a leaf author work from the new mathematics and the contracts of nearby categories. Do not require knowledge of distant subtrees or the complete category graph. |
| `POL-LEAF-016` | After the selected functors are declared, automatically supply the complete applicable object, element, morphism, and construction interfaces from their target categories. |
| `POL-LEAF-017` | Give a full replete subcategory the inherited categorical interface without extra wiring. A limit, colimit, or other functorial construction descends to the subcategory when the subcategory leaf overrides the inherited construction and refines its result through its own constructor; no ancestor category and no kernel branch lifts a result for a descendant. |
| `POL-LEAF-018` | Do not implement an inherited category-owned mathematical operation in a leaf object. A local `__iter__`, `__contains__`, or `cardinality()` on a poset object duplicates the set interface instead of receiving it through the selected functor to `Sets()`. |
| `POL-LEAF-019` | Do not create a free-standing category to hold the elements of another category. Poset elements belong to `Posets().ElementType`; a separate `PosetElements()` category disconnects their type and inheritance from `Posets()`. |
| `POL-LEAF-020` | Give every refinement and construction its own category-owned object, element, and morphism role declarations. Property refinement keeps the same owned value and updates its Sage dynamic class so the refined role precedes inherited roles. It never allocates another value merely to obtain the refined type. |
| `POL-LEAF-021` | Lift a construction through functors, natural transformations, and the new mathematical structure only. A poset product supplies the componentwise order and its action on morphisms; its implementation types do not subclass generic product types or reconstruct the underlying set product interface. |
| `POL-LEAF-022` | Do not require data that defines a stronger structure than the named leaf category. A total order requires a partial order with total comparison; indexing, ranking, unranking, and enumeration belong to separate enumerable or well-ordered refinements. |
| `POL-LEAF-023` | Do not copy inherited storage, caches, or constructor arguments into a property refinement. A finite poset adds finite-poset operations and declares its categorical inclusions. Same-object refinement preserves its underlying set, relation, elements, private realizations, and existing structural images. The refined dynamic MRO supplies inherited operations; the leaf never traverses an inclusion to recover its own state. |
| `POL-LEAF-024` | A finished leaf contains its category, minimal defining data, new operations, immediate structural functors, and named constructors. It can also state leaf-specific lifts. |
| `POL-LEAF-025` | Stop leaf work when it requires route traversal, canonical-image caches, registries, compiler metadata, type reconstruction, or runtime backend selection. A fixed private computation dependency is not backend selection. |
| `POL-LEAF-026` | Use the first leaf that exposes missing generic infrastructure as an acceptance specimen. Repair the foundation, then delete the leaf workaround. |
| `POL-LEAF-027` | Identity morphisms and morphism composition are fundamental categorical operations. Every leaf morphism receives its domain, codomain, and composition surface automatically from the owning categories through compiled structural inheritance. |
| `POL-LEAF-028` | Never define `compose()` in a leaf merely to expose, forward, route, coerce, inspect generic caches, or reconstruct the inherited operation. A missing inherited composition method is a kernel defect. |
| `POL-LEAF-029` | Refine an inherited method in a leaf only when the leaf's additional mathematical structure or owned realization requires a new step. Form the inherited semantic result first. |
| `POL-LEAF-030` | A leaf refinement adds only its leaf-specific structure or private realization. It preserves the inherited method's name, laws, domain, codomain, and mathematical owner. |
| `POL-LEAF-031` | Delete any leaf method that adds no leaf-specific mathematical or realization step. Generic algorithms, structural transport, wrappers, and public-surface installation belong to their existing owners. |
| `POL-LEAF-032` | Treat selected structural functors as the complete inheritance program. A finished leaf contains no forwarding, descriptor, route, cache, wrapper, or type-repair boilerplate. |
| `POL-LEAF-033` | A property-subcategory leaf declares its predicate, inclusion, and trusted property constructor. The public `is_*()` method always returns the applied predicate. Category placement makes `ask()` return `True`. The leaf declares one constructor only. |
| `POL-LEAF-034` | Never give a leaf an ambient-to-refined cache, an identity-keyed refinement table, an ambient wrapper field, or a local refinement constructor. |
| `POL-LEAF-035` | Direct construction, `assume(P(x))`, exact `True`, and construction-owned mathematics all invoke the same generic self-refinement through the property-subcategory constructor. The leaf performs no allocation, cache mutation, narrowing, or repeated membership assertion. |
| `POL-LEAF-036` | Treat a type error in leaf refinement machinery as evidence that the kernel lacks a typed refinement contract. Repair that contract and delete the leaf machinery. |
| `POL-LEAF-037` | Never discover, inspect, compose, or traverse structural routes in a leaf. Declare immediate structural functors and use the resulting public inherited surface. |
| `POL-LEAF-038` | Never traverse a structural route from a leaf to obtain an object, element, or morphism image. The kernel constructs and retains every selected canonical image and role input. |
| `POL-LEAF-039` | Call an inherited operation directly on the original structured value. If that call fails, stop the leaf edit and repair structural compilation. |
| `POL-LEAF-040` | Never normalize a leaf input to an ancestor implementation, add an exact-category branch, or repeat membership after transport. Store and pass the established mathematical object. |
| `POL-LEAF-041` | Make `C.ObjectType`, `C.ElementType`, and `C.MorphismType` the sole executable implementation classes for operations owned by `C`. Each class is the public firewall that hides every supported representation, dependency, and algorithm for that mathematical role. |
| `POL-LEAF-042` | Let the category declaration define or link exactly one implementation class for each mathematical role. Never offer competing implementation classes, backend choices, realization variants, or parallel public surfaces for one mathematical notion. |
| `POL-LEAF-043` | Implement every leaf-local public operation as an ordinary executable method on its owning implementation class. Never replace its body with `assert False`, `@realized_method`, `@realized_operation`, another computation-routing decorator, a descriptor marker, or a backend-name mapping. |
| `POL-LEAF-044` | Let a leaf-owned method lower semantic inputs to a fixed private engine, invoke a mature exact algorithm, and reconstruct the owned mathematical result. This computation is part of the leaf implementation, not structural wiring. |
| `POL-LEAF-045` | Treat a short category-owned method that invokes a dependency as a valid implementation when it owns the public contract and semantic reconstruction. Repetition of private realization access alone does not justify a dispatcher or parallel hierarchy. |
| `POL-LEAF-046` | Permit a private neighboring engine helper only for a substantial shared computation boundary. It exposes no public method surface, category roles, runtime registry, compiler binding, or mirror of the leaf operations. |
| `POL-LEAF-047` | Give each local implementation constructor one exact typed datum containing only the new state required by its category. A construction input can also carry exact semantic data consumed only by a selected functor to construct ancestor state. Keep the role identity separate from that datum. A node with no local state has no local initializer. Let selected functors convert the complete typed construction input into the target input required by ancestor role constructors. Each local initializer calls `super().__init__()` once, including the role-specific kernel initializer and the common `Cat().ElementType` initializer at the end of the chain. |
| `POL-LEAF-048` | Make the public operation surface depend only on categorical placement. Every object of the category receives the same owned operations, regardless of which private dependency or representation computes them. |
| `POL-LEAF-049` | Select each immediate structural functor in the category layer. Reuse the exact functor retained by the defining category construction. Otherwise, define its maps once through `Fun(self, Target)`. Select the strongest established functor-property subcategory before construction. Construct exact images through target-category constructors. Add an element action only when its mathematics defines one. |
| `POL-LEAF-050` | Quarantine substantial Python, foreign-function, process, conversion, caching, and engine-adaptation code in private helpers. Keep mathematical ownership, public methods, semantic inputs, and semantic reconstruction on the sole category implementation class. |
| `POL-LEAF-051` | Write a leaf method as one ordinary typed Python method. Never attach or place beside it transport metadata, compiler annotations, descriptor arguments, role tables, signature mirrors, or another record of facts already present in its declaration. This rule applies by function, regardless of mechanism name or syntax. |
| `POL-LEAF-052` | Stop a change that repeats the same non-mathematical declaration across leaf methods or categories. Such repetition identifies missing kernel derivation. Repair the kernel once, or reject the unsupported semantic signature during compilation. |
| `POL-LEAF-053` | Require no framework-specific decorator on a mathematical leaf method. Never use a decorator to establish ownership, compilation, inheritance, transport, dispatch, engine selection, result reconstruction, or type repair. An ordinary typed method on the owning implementation class is complete. |
| `POL-LEAF-054` | Keep kernel concerns out of every leaf import, decorator, annotation, signature, class attribute, and method body. Leaves never mention compiler descriptors, transport roles, structural routes, canonical images, refinement caches, generated types, or dispatch machinery. |
| `POL-LEAF-055` | Use only ordinary Python call syntax and exact mathematical types in a leaf method signature. Never require `Annotated` payloads, marker types, empty metadata fields, sentinel fields, parameter-role inventories, result-role labels, or declarations of absent positional, keyword, variadic, or result cases. |
| `POL-LEAF-056` | Never implement an operation supplied by an inherited morphism category, morphism-property category, or universal construction. This includes inversion of isomorphisms and every other operation implied by established categorical placement. If the operation is absent from a descendant morphism, repair the generic owner, structural functor, or compiler. |
| `POL-LEAF-057` | A named-object leaf states its known properties by its strongest category placement or by ordinary defining predicates that return `True`. Never enumerate the object, query an engine, or run a general decision procedure to rediscover a property supplied by its definition. |

See [Leaf category implementations](specs/leaves.md) for the complete ownership model,
the allowed private computation sequence, and the rejected decorator and mirrored-class
designs.

For example, a free-module morphism inherits categorical composition.
A leaf refinement can attach a private matrix realization to the inherited composite when bases are chosen.
It does not reimplement composition, structural transport, domain checks, codomain checks, or public method installation.

## Leaf and kernel boundary

| ID | Policy |
| --- | --- |
| `POL-KERNEL-001` | The kernel owns category-independent role compilation and structural construction for objects, elements, and morphisms. This includes route composition, typed construction inputs, C3 initializer composition, canonical images, and their caches. |
| `POL-KERNEL-002` | The kernel owns generic same-object property refinement. It strengthens the owned value's category, rebuilds its Sage dynamic MRO from category-owned role declarations, and preserves identity, construction data, private realizations, and existing structural images. Structural functor images remain a separate mechanism. |
| `POL-KERNEL-003` | A leaf functor states only its immediate mathematical action on objects and morphisms; its action on generalized elements is derived by applying the morphism action to each element's defining morphism. It never implements route normalization or cache management. |
| `POL-KERNEL-004` | The kernel lifts inherited universal constructions and their morphisms. A leaf supplies only its additional structure and its typed closure or preservation conclusion. |
| `POL-KERNEL-005` | Add a kernel abstraction only when one mathematical declaration replaces the same infrastructure in every applicable leaf. Keep category-specific branches out of the kernel. |
| `POL-KERNEL-006` | Kernel complexity is valid only when it removes that complexity from theory code. Expose each kernel capability through a mathematical declaration. |
| `POL-KERNEL-007` | Kernel code can use `isinstance`, `issubclass`, `getattr`, `setattr`, `inspect`, descriptor protocols, and Python collection protocols to implement declared runtime mechanics. |
| `POL-KERNEL-008` | Each kernel primitive must inspect a Python implementation role. It must not establish category membership, a mathematical property, method ownership, or functorial structure. |
| `POL-KERNEL-009` | Derive mathematical roles from typed category and functor declarations. Use Python inspection only to realize those declarations in the runtime. |
| `POL-KERNEL-010` | Keep compiled-role construction and C3 initializer composition inside the kernel. Expose the resulting typed mathematical surface through ordinary Python inheritance. |
| `POL-KERNEL-011` | Kernel permissions do not permit `Any`, `object`, casts, ignored diagnostics, fallbacks, or fabricated mathematical evidence. |
| `POL-KERNEL-012` | Provide one typed same-object self-refinement operation for objects, elements, and morphisms of every full property subcategory. Every positive evidence source converges on that operation through the property-subcategory constructor. |
| `POL-KERNEL-013` | Generic property refinement preserves the same Python and mathematical identity. It joins the current category with the property subcategory and updates the Sage dynamic class and MRO in place. It creates no target implementation, ambient wrapper, canonical refinement image, or refinement cache. |
| `POL-KERNEL-014` | Compile each property subcategory's category-owned object, element, and morphism role declarations into the refined value's dynamic MRO. The property role contributes its new mathematics before inherited roles. A leaf never constructs a wrapper or second value to obtain that surface. |
| `POL-KERNEL-015` | A kernel `try`/`except` can only add exact context, translate to a more precise kernel exception while preserving the cause, or perform mandatory cleanup before re-raising. |
| `POL-KERNEL-016` | Every kernel catch terminates the current operation. It never selects another implementation, retries, suppresses a diagnostic, continues computation, or returns an ordinary value. |
| `POL-KERNEL-017` | The kernel alone discovers, composes, and traverses structural routes and computes retained canonical images and construction inputs. Theory code never sees these operations. |
| `POL-KERNEL-018` | Make each inherited method callable directly on every structural descendant through its compiled role MRO. The original descendant is the receiver, its arguments remain unchanged, and the method can read its retained canonical ancestor image from role-private state. |
| `POL-KERNEL-019` | Let a constructor requiring an object of `C` accept every `X` with `X in C`. Resolve any required canonical implementation inside the generic kernel boundary. |
| `POL-KERNEL-020` | Copy locally declared operations into compiled roles and inherit them through the role MRO. Never route a locally owned operation into Sage or another engine, replace its executable method, match it to an engine method by name, or interpret a decorator, annotation, registry entry, or marker as a computation route. |
| `POL-KERNEL-021` | Derive a method receiver's role from its owning `ObjectType`, `ElementType`, or `MorphismType`. Derive parameter and result roles from their exact mathematical types. Derive call shape from the Python signature. Fail compilation when any required role is not exact. Never require a leaf to restate these facts. |
| `POL-KERNEL-022` | Use mathematical roles to type construction inputs and canonical-image relations. Never relabel a category, object, element, morphism, or mathematical collection as a plain value to avoid an exact role. |
| `POL-KERNEL-023` | Compile every supported ordinary typed leaf method without any kernel import or framework annotation in the leaf. A required decorator, role marker, or signature mirror is a kernel API defect. |
| `POL-KERNEL-024` | Inspect standard Python signatures and exact mathematical type annotations inside the kernel. Never require a theory module to use a signature DSL, encode standard call mechanics, describe absent parameters, or state compiler mechanics. |
| `POL-KERNEL-025` | Compile operations from inherited categories, morphism-property categories, and construction categories onto every descendant `ObjectType`, `ElementType`, and `MorphismType`. A missing inherited inverse, universal morphism, or other placement-forced operation is a kernel defect. It never licenses leaf wiring. |
| `POL-KERNEL-026` | Propagate each property-subcategory constructor through selected structural inclusions, following Sage's `with_axiom` model. Build the descendant refinement, role MRO, constructor, and inherited predicate behavior generically. A leaf supplies no propagation machinery. |
| `POL-KERNEL-027` | Let `Fun(Source, Target)` construct functors from complete object and morphism actions. Implement identity, composition, and inclusions established by subcategory data there. Let each product, pullback, comma, `Fun([1], C)`, or other category construction create and retain its own named functors. The kernel never interprets a leaf presentation to select one. |
| `POL-KERNEL-028` | Keep each `DeclaredObjectType`, `DeclaredElementType`, and `DeclaredMorphismType` distinct from its compiled public role. Build the public role with Sage's dynamic-class technique. Copy each local member except `__init__` onto the controlled compiled-ancestor bases. Rebind each copied `__class__` closure to the compiled class. Retain the rebound local initializer as the node initializer. Install one generated `__init__` wrapper. The exact object tail is the selected object roles, `ObjectOfCategory`, `Cat().ElementType`, and `CategoryPointKernel`. The exact morphism tail is the selected morphism roles, `MorphismOfCategory`, `Cat().ElementType`, and `CategoryPointKernel`. The exact ordinary element tail is the selected element roles, `ElementOfObject`, `Cat().ElementType`, and `CategoryPointKernel`. |
| `POL-KERNEL-029` | Allocate the public role instance first. Create its root construction input with that value as canonical image. Before local initialization starts, traverse the structural graph and compute one exact input for each reachable role node. Also compute one common `Cat().ElementType` input for every object and morphism. Its closed identity is one of: a general defining morphism, an object-stage parent category, or an arrow-stage parent category with endpoints. The defining morphism is a functor only for an element of a category. The object and arrow forms realize their point or arrow functor only when `defining_morphism()` is requested. Each input keeps its role identity separate from its local datum; the `Cat().ElementType` local datum is `None`. Check all routes to a common node by canonical-image and input identity. Activate a role-specific construction context. Each generated class wrapper passes only its node's datum to its rebound local constructor. Each local constructor initializes only its new state and calls `super().__init__()` once. A node without a local initializer advances to the next C3 initializer. C3 initializes each node once, even when adjacent classes have no structural edge. The kernel bases consume the precomputed identities. |

See [Leaf category implementations](specs/leaves.md) for the exact boundary between
kernel-owned inheritance and leaf-owned computation.

Selected structural functors are executable inheritance declarations.
A leaf states its immediate mathematics and then uses inherited operations as native methods.
If a leaf must inspect a route or recover an ancestor implementation, the kernel abstraction has failed.

For example, `__pow__(self, exponent: ObjectType) -> ObjectType` (the exponential object) already states
its receiver, argument, call shape, and result type.
The leaf does not repeat those facts in a transport decorator.
The result remains an `ObjectType`; it is not a plain value used to evade transport.
The same rule excludes mandatory `@transport_roles(...)`, `receiver=...`, empty
`keyword=()`, and `variadic=None` declarations from every theory module.

Given `A in Monoids(M)` and a chosen left `M`-actegory `C`, a presentation of
`Modules(A, C)` retains an object `X in C` and an action morphism
\(\rho:A\mathbin{\bullet}X\to X\). It also retains the unit and action equations.
Its projection to `X` supplies the inherited `C` interface. When `C` has the required
closed or enriched structure, the same action can correspond to a monoid morphism
\(A\to\operatorname{End}_{C}(X)\).

Present an \(R\)-lattice \(L=(N,b)\) as a subobject of a product category whose first factor is the applicable `Modules(R, C)`. The corresponding product projection supplies the module interface.
The lattice exposes `L.bilinear_form()` to return \(b\); it does not inherit the full interface of a bilinear-form morphism.
An internal pair representation remains valid, but callers do not need `L.underlying_module()` to use \(L\) as a module.
Cardinality then arrives through the selected carrier functor from `C` to `Sets()`.
A lattice-specific cardinality implementation signals a missing or incorrect structural functor.

If `Modules(R, C)` has a supplied monoidal structure, every structural descendant can form its tensor-product subcategory.
For lattices, the leaf-specific lift is

\[
\bigotimes_i(L_i,b_i)=\left(\bigotimes_iL_i,\ \bigotimes_i b_i\right).
\]

The module subtree owns the tensor-product objects, elements, morphisms, and universal property.
The lattice subtree supplies only the induced bilinear form and its compatibility with `product_projection(0)` to `Modules(R, C)`.

A new specialized algebra category should start from the leaf template, declare its selected functors to nearby algebra and module categories, and add only its new algebraic methods.
It receives distant operations such as cardinality through the resulting functor chain without importing or reimplementing them.

For a toy leaf, `FiniteSubsetsOfNN()` declares its research-specific constructors, its inclusion functor into `Sets()`, and methods such as `minimal_element()` or `gcd_of_elements()`.
Its elements automatically receive the `Sets.ElementType` interface through `FiniteSubsetsOfNN.ElementType`, even when the leaf adds no element methods.
Products, coproducts, filtered limits, and other set constructions require no leaf implementations.
Their results use the category that owns each construction and return to the leaf when closure is declared or derived.

For `Posets()`, the minimal new object data is an object of `Sets()` together with a partial-order relation.
Its product-subobject construction supplies `product_projection(0)` to `Sets()`. This functor supplies membership, iteration, cardinality, elements, and set maps through the compiled interface.
`FinitePosets()` declares its inclusion to `Posets()` and its compatible route to `FiniteSets()`.
It does not copy the poset representation or reuse the poset element type.

`Posets().Products()` is the formal product-construction subcategory obtained from the product functor.
Its lift equips the inherited product apex with componentwise order and maps product morphisms accordingly.
It does not subclass the generic product implementation or construct a second set product API.

`TotallyOrderedSets()` refines partial orders by the totality property alone.
An enumeration is additional mathematical structure and therefore belongs to a separate category with its own structural functor to `TotallyOrderedSets()`.

## Mathematical encapsulation and repository layout

| ID | Policy |
| --- | --- |
| `POL-LAYOUT-001` | Keep a leaf subtree expressed in the language of its own category, its defining structure, and its immediate structural functors. Deeply underlying operations belong to the category that owns them. |
| `POL-LAYOUT-002` | Treat a reference to cardinality inside a lattice subtree as an ownership defect. Cardinality reaches lattice objects through their structural functors to modules and sets. |
| `POL-LAYOUT-003` | Make filesystem subtrees follow mathematical ownership boundaries. A reader must be able to audit one category without reading implementations owned by unrelated categories. |
| `POL-LAYOUT-004` | Quarantine the non-mathematical implementation kernel in its own subtree. Category compilation, descriptors, dispatch, and other standard Python machinery belong behind this boundary and never mix with mathematical theory code. |
| `POL-LAYOUT-005` | Mirror each source subtree in the test layout. Quarantine all implementation-kernel tests in a dedicated kernel testing subtree and keep each category's tests with that category's proof obligations. |
| `POL-LAYOUT-006` | Split `Cat`, `Sets()`, modules, formed modules, algebras, and other substantial mathematical owners into separate subtrees when one-file or shared-subtree organization impedes a complete local audit. |
| `POL-LAYOUT-007` | Give a frequently used property subcategory its own nested subtree when its constructors, morphisms, algorithms, and tests form a substantial unit. Examples include finite or countable sets and free modules or algebras under stated ring hypotheses. |
| `POL-LAYOUT-008` | Keep public mathematical signatures and results free of engine types, storage vocabulary, generic container types, and non-mathematical dispatch. Permit private engine use inside an executable category-owned computation boundary. |
| `POL-LAYOUT-009` | Put category-independent Sage, SymPy, and other engine adapters in dedicated backend subtrees. A category-specific private engine helper can remain beside its mathematical owner under `POL-LAYOUT-020`. |
| `POL-LAYOUT-010` | Confine engine imports, engine classes, conversion code, and engine-specific exceptions to private computation boundaries. Translate inputs before the engine call and reconstruct owned results before return. |
| `POL-LAYOUT-011` | Define and implement the public mathematical operation on its category-owned implementation class. A backend module supplies private representations, conversions, or raw computations rather than another implementation of that interface. |
| `POL-LAYOUT-012` | Keep a mathematical leaf change outside the kernel code and kernel-test subtrees. If the kernel boundary cannot support the leaf, treat that fact as a separate foundational defect instead of modifying the kernel as part of the leaf. |
| `POL-LAYOUT-013` | Make dependency direction visible in the layout: category implementations depend on the kernel, immediate mathematical owners, and any fixed private computation helper. Engine helpers never depend on compiler dispatch or define public category roles. |
| `POL-LAYOUT-014` | Audit mathematical purity by public semantic surface. Engine types in signatures or results, primitive collection semantics, coordinate representations, and unrelated invariants indicate misplaced responsibility. A private exact engine call does not. |
| `POL-LAYOUT-015` | Permit a private engine boundary to use engine-specific types and required Python representations. Keep those values private and return them only to the category-owned method that reconstructs the semantic result. |
| `POL-LAYOUT-016` | Split a large mathematical module by coherent mathematical owners, properties, or constructions, not by line count, implementation technique, or an arbitrary group of helpers. Keep the owning category visible in each module name. For `Sets()`, suitable modules include `setsubsets.py`, `setproducts.py`, `setcoproducts.py`, and `setlimitscolimits.py` when each forms a substantive mathematical unit. |
| `POL-LAYOUT-017` | Move generic non-mathematical wiring into relatively private infrastructure modules whenever it can be separated from the definitions. Keep registration, compiler hooks, structural dispatch, and route caches out of mathematical modules. A local private computation call is not generic wiring. |
| `POL-LAYOUT-018` | Preserve separate audit surfaces for mathematics and engineering. A mathematical module must be reviewable against definitions and theorems without following private runtime wiring; an infrastructure module must be reviewable for implementation correctness without deciding new mathematics. |
| `POL-LAYOUT-019` | When one implementation class becomes a substantial audit unit, place that sole class in a neighboring module named for its mathematical role and link it from the category declaration. Do not duplicate declarations in the category module. |
| `POL-LAYOUT-020` | Create a neighboring engine-specific module only for substantial shared lowering, conversion, caching, foreign-function or process integration, or raw computation. Use the concrete engine name, keep the module private, and do not create one by default for every category. |

See [Leaf category implementations](specs/leaves.md) for the permitted file layouts and
the single-source-of-truth rule.

Grounding examples: a sheaf is an object of a sheaf category, and an internal Hom of sheaves is again a sheaf.
A functor is an object of `Fun = Mor(Cat())` and of `Fun(C, D) = Mor(Cat())(C, D)` for its fixed endpoints. None enters `Sets()` without a specified functor.

Do not split `sets.py` into `sets_part_1.py`, `sets_helpers.py`, or files chosen only to satisfy a length limit.
Split it into category-qualified mathematical units such as `setsubsets.py`, `setproducts.py`, `setcoproducts.py`, and `setlimitscolimits.py` when those units have distinct objects, morphisms, universal properties, or algorithms.
Place role compilation, generated constructor setup, caches, registration, and backend conversion in private infrastructure modules outside those mathematical units.

## Functors and universal constructions

| ID | Policy |
| --- | --- |
| `POL-FUN-001` | Every functor is a morphism in `Cat` and uses `Cat().MorphismType`. It owns its domain, codomain, object map, and morphism map through that uniform morphism implementation. |
| `POL-FUN-002` | Derive every functor's action on generalized elements from its morphism action: `F.on_element(t)` applies `F.on_morphism` to the defining morphism of `t`. A functor stores no element callback, element map, or element capability. A classical-stage element method arrives only through the stage comparison retained by a selected functor. |
| `POL-FUN-003` | Only functors selected in `structure_functors()` contribute inherited public methods. Selection affects compiler behavior only; it does not change the selected object's mathematical type in `Fun`. |
| `POL-FUN-004` | Use ordinary functors for mathematical transport that does not define public inheritance. |
| `POL-FUN-005` | Represent each projection, scalar change, and modeled mathematical realization as an explicit functor. Do not treat a private engine representation, cache, or algorithm call as a realization functor. |
| `POL-FUN-006` | Use functor composition to propagate structure. Do not add a separate propagation registry. |
| `POL-FUN-007` | A categorical construction must define its action on objects and morphisms. |
| `POL-FUN-008` | When constructing a limit or colimit, preserve its diagram and universal morphisms as an available witness. Do not make that selected witness part of property-subcategory membership. |
| `POL-FUN-009` | A product constructor retains its factors, `product_projection(i)` morphisms, and mediating morphism as an available witness. |
| `POL-FUN-010` | A coproduct constructor retains its factors, `coproduct_injection(i)` morphisms, and mediating morphism as an available witness. |
| `POL-FUN-011` | Let the apex of a universal construction inherit operations from the category in which it lives. |
| `POL-FUN-012` | Implement arbitrary small diagrams. Do not encode finiteness into the general construction. |
| `POL-FUN-013` | Represent a subobject by an object together with its monomorphism. |
| `POL-FUN-014` | Obtain the containing object of a subobject from the monomorphism's codomain. |
| `POL-FUN-015` | For `F: D -> C`, define `C.ImagesOfFunctor(F)` as the full replete subcategory on objects `Y` for which there exist `X in D` and an isomorphism `F(X) -> Y`. Make `C` its immediate structural supercategory. |
| `POL-FUN-016` | Implement products, coproducts, limits, and colimits as functors on diagrams, including their action on diagram morphisms. |
| `POL-FUN-017` | Define `Fun = Mor(Cat())`. Represent a functor `F: C -> D` as an object of `Fun(C, D) = Mor(Cat())(C, D)`. Its object and morphism actions come from `Cat().MorphismType`. Do not reduce it to a callable or set of assignments. |
| `POL-FUN-018` | Treat membership in `C.ImagesOfFunctor(F)` as the existential image property. A preimage can be selected when an operation needs one, but no selected preimage belongs to the membership data. |
| `POL-FUN-019` | Define `C.Products()`, `C.Coproducts()`, `C.TensorProducts()`, and analogous named constructions as full subcategories of `C` on the constructed objects, reached by the retained identity-on-values inclusion. For each input diagram `D`, their constructor returns one value: the constructed object, an object of `C`, placed in the family. The family retains the universal data of each diagram: `D`, its defining morphisms, and its universal maps. Distinct diagrams have distinct universal data, including when the objects they construct are identical. Keep these categories distinct from the full replete subcategory `C.ImagesOfFunctor(F)`, which records only the existential image property. |
| `POL-FUN-020` | Lift an inherited universal construction through the selected structural functor. Retain its chosen diagram, constructed object, universal morphisms, and comparison map instead of reconstructing a parallel result. |
| `POL-FUN-021` | Establish properties of lifted objects and morphisms from the theorem of the construction. Record those facts at the construction owner instead of replacing that theorem with a presentation-specific check. |
| `POL-FUN-022` | Discharge closure and morphism-property obligations through the construction-owned lift. The lift can declare the typed conclusion of its construction theorem without runtime proof. Do not rely on a permissive general constructor that would admit the same property for arbitrary inputs. |
| `POL-FUN-023` | Implement the functor laws for every functor. Preserve identities and composition, and map an isomorphism inverse to the inverse of its image: `F(f.inverse()) == F(f).inverse()`. Structural descendants use this generic action and never add leaf-specific inverse transport. |
| `POL-FUN-024` | Define fullness, faithfulness, full faithfulness, essential surjectivity, and equivalence as properties of objects in `Fun`. Give each one its property subcategory and owned predicate. |
| `POL-FUN-025` | Define `FullyFaithful(F)` as `Full(F) and Faithful(F)`. Treat it as a property without selected preimage morphisms. A construction that needs a chosen preimage morphism owns that separate choice. |
| `POL-FUN-026` | Use external mathematics to select the strongest applicable functor-property subcategory. The code writer constructs the functor directly there, and the constructor trusts that assertion. Use `assume(F.is_P())` for an interactive hypothesis. Neither route proves or certifies the property. |
| `POL-FUN-027` | Let `Fun(C, D)` own construction of every functor `C -> D`. The endpoints determine only this morphism category `Mor(Cat())(C, D)`. A specialized constructor needs mathematical data that selects one functor. Category constructions create their projection and evaluation functors through `Fun(C, D)` and retain them as defining data. |
| `POL-FUN-036` | Propagate established placement from `S` to `T` along a functor that is both a monomorphism of `Cat()` and an isofibration, and along no other functor. There is no separate notion of an inclusion functor; `inclusion()` is the package's shorthand for exactly those two conditions. Monicity is faithfulness with injectivity on objects, so one value is shared rather than copied. The isofibration condition is repleteness of the subcategory, which is what makes strict membership respect the principle of equivalence; without it a skeleton would qualify, and a cardinal would be a set. A subcategory is a subobject of `T` in `Cat()`, and no intrinsic choice of representative exists, so the leaf declares its inclusion through the owning property category and the kernel trusts that declaration. Never infer the relation from Python inheritance, shared storage, or a table of previously constructed functors. See `specs/functor.md`, "Monomorphisms of `Cat()` and placement". |
| `POL-FUN-028` | Do not define a generic “forgetful functor.” That phrase does not select an object of `Fun(C, D)`. A source, target, object presentation, or collection of Python fields can admit several distinct functors. |
| `POL-FUN-029` | Name and construct each functor by its mathematical source: a product projection, coproduct injection, subcategory inclusion, evaluation at an object of the shape, base change, fibration projection, opfibration projection, Kan extension, or explicit composition. Retain the data that defines it. |
| `POL-FUN-030` | Treat a Grothendieck fibration as a functor with specified cartesian lifts. Treat its dual as an opfibration, also called a cofibered category, with specified cocartesian lifts. Use “cofibration” only when a cited source uses it for this dual notion. Do not confuse it with a class of morphisms in topology or a model category. |
| `POL-FUN-031` | Form slice and coslice projections from the pullback projections of `C.SliceOver(x)` and `C.CosliceUnder(x)` as pullbacks of `Fun([1], C)`, composed with the evaluation functors `ev_0` and `ev_1`. `ev_1: Fun([1], C) -> C` is a fibration when `C` has pullbacks; the fixed slice projection `C.SliceOver(x) -> C` is a discrete fibration by precomposition for every `C`. State each lift at its construction owner; do not infer it from object fields. |
| `POL-FUN-032` | Let left and right Kan extension constructions own their resulting functors, units, counits, and universally induced natural transformations. These natural transformations are morphisms of the applicable fixed-endpoint functor categories. Build later routes by ordinary composition. |
| `POL-FUN-033` | Make `structure_functors()` select exact construction-named functors or composites. Selection does not create a preferred projection, an unnamed structure map, or another kind of functor. |
| `POL-FUN-034` | Never try to prove, certify, or check fullness, faithfulness, full faithfulness, essential surjectivity, equivalence, or another general functor property. Use external mathematics to choose the property subcategory, construct the functor there, and cite any nontrivial theorem beside that construction. |
| `POL-FUN-035` | A selected functor retains one pure typed construction-input conversion for each object, element, and morphism role that its codomain initializes. An input contains the source node's role identity and typed construction datum. Each resulting canonical value retains one root input. A conversion constructs the canonical target through its category and returns that value's retained input. The object and morphism conversions also implement the corresponding public functor actions. The element conversion supplies compiler input; `F.on_morphism` supplies public element action. For `t: T -> X`, the public image is `q = F(t): F(T) -> F(X)`. The compiler uses the input retained by `q` for a nonclassical source. For a classical source `t: G_C -> X`, it precomposes `q` with the retained comparison `c_F: G_D -> F(G_C)` and uses the input retained by `p: G_D -> F(X)`. The values `q` and `p` have separate identities and cache entries exactly when their stages, defining morphisms, or codomains differ. Identity comparisons satisfy \(c_{\mathrm{id}} = 1_G\). Composite comparisons satisfy \(c_{H \circ F} = H(c_F) \circ c_H\). All routes to one node return the same image and input by identity. A conversion reads no partly initialized value. |

### Why “forgetful functor” is not a construction

The phrase “the forgetful functor from `C` to `D`” does not determine an object of
`Fun(C, D)`. Fixed endpoints can have many functors. A presentation can also have
several projections with different codomains.

For example, a presentation of a lattice as `(M, b)` has a projection to `M` and a
projection to `b`. Neither projection follows from the word “forget.” A presentation of
a module by `rho: A bullet X -> X` has projections and evaluations determined by that
presentation. An equivalent presentation can expose different immediate projections.
The kernel must not inspect tuple positions or fields to choose one.

Use the construction that supplies the map:

- a subcategory supplies its inclusion;
- a product supplies its component projections;
- a coproduct supplies its component injections;
- `Fun([1], C)` supplies its evaluation functors `ev_0` and `ev_1`;
- a slice or coslice supplies projections to its varying object and defining morphism;
- a fibration or opfibration supplies its projection and cartesian or cocartesian lifts;
- a base-change construction supplies its pullback or pushforward functor;
- a Kan extension supplies its extended functor and universal natural transformation;
- ordinary composition combines these maps into longer structural routes.

A category can select one such functor in `structure_functors()`. This selection states
the exact structural route used for inheritance. It does not make that functor a
canonical map determined by the category alone.

Mathlib's `ConcreteCategory.forget` and `HasForget₂.forget₂` are chosen functors carried
as extra structure. They are not derived from their endpoint categories. This repository
models the underlying construction directly and does not add a generic constructor for
that convention. See [the Mathlib concrete-category definition](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/ConcreteCategory/Forget.html).

For the product functor `Products: Diag(C) -> C`, an object `Y` lies in
`C.ImagesOfFunctor(Products)` when some `Products(D)` is isomorphic to `Y`. This full
replete subcategory records no selected diagram or projections.

For each diagram `D`, `C.Products()(D)` is the chosen product: one object of `C`,
placed in `C.Products()`, owning its `product_projection(i)` morphisms and its universal
maps. `C.Products()` is the full subcategory of `C` on those objects, reached by its
retained identity-on-values inclusion, and it retains the diagram and universal data of
each construction. The chosen product lies in the essential image.

For `C = Sets()`, cardinality is the inherited set operation applied to the product object and satisfies \(\#(\prod_i X_i)=\prod_i\#X_i\).
The products category does not define a second set interface or an independent cardinality operation.

## The category of sets

| ID | Policy |
| --- | --- |
| `POL-SET-001` | `Sets()` owns arbitrary sets and arbitrary functions between them. |
| `POL-SET-002` | A set map requires a domain, codomain, and rule. It does not require a finite table. |
| `POL-SET-003` | Permit maps whose rules have no linearity, continuity, or finiteness hypothesis. |
| `POL-SET-004` | Support maps such as `QQ -> NN`, `QQ -> ZZ`, and `RR -> RR^2` as ordinary morphisms in `Sets()`. |
| `POL-SET-005` | Let set-membership predicates return applied propositions. Use `ask()` to obtain `True`, `False`, or `Unknown`. Python containment is the Boolean admission boundary. |
| `POL-SET-006` | Treat `Unknown` as unavailable knowledge, not as `False`. |
| `POL-SET-007` | Construct a predicate-defined subset as an object with an inclusion morphism. |
| `POL-SET-008` | Support infinite predicate subobjects such as the even integers and prime integers inside `ZZ`. |
| `POL-SET-009` | Put cardinality on the set implementation. |
| `POL-SET-010` | Support finite, infinite, and symbolic cardinal values. `X.cardinality()` returns an exact cardinal or the Sage singleton `Unknown`; its type is `Cardinal | UnknownClass`. A cardinal is always an exact value, and cardinals implement no `Unknown` handling. |
| `POL-SET-011` | Use cardinality for sets. Use length only for an ordered finite sequence. |
| `POL-SET-012` | Support function sets and exponentials. |
| `POL-SET-013` | Support products and coproducts indexed by arbitrary small diagrams. |
| `POL-SET-014` | Support general limits and colimits in `Sets()`. |
| `POL-SET-015` | Propagate set operations, including cardinality, to objects produced by functors and universal constructions. |
| `POL-SET-016` | Derive structural properties from construction data, defining predicates, functors, injections, bijections, and universal constructions before considering enumeration. |
| `POL-SET-017` | Use one parent and implementation for the set of functions `X -> Y` and the exponential `Y ** X`. `Mor(Sets())(X, Y)` is the discrete category on the elements of `Y ** X`. |
| `POL-SET-018` | Use one parent and implementation for `P(X)`, `2^X`, and `2 ** X`, where `2 = [1] = {0, 1}`. |
| `POL-SET-019` | Construct a set morphism from a well-typed callable or explicit mapping data. A callable must represent maps such as `QQ -> ZZ` without enumerating `QQ`. |
| `POL-SET-020` | Implement `#(X × Y) = #X #Y`, `#(X ⊔ Y) = #X + #Y`, and `#(Y^X) = (#Y)^(#X)` on the resulting set objects. |
| `POL-SET-021` | Make the cardinality functor call the resulting object's `cardinality()` method. Do not add product, coproduct, or exponential cases to the functor. |
| `POL-SET-022` | Support `X.cardinality() == 3`. Do not require `X.cardinality().value == 3`. |
| `POL-SET-023` | Give every object of `Sets()` the complete `Sets.ObjectType` method surface, including products, coproducts, subsets, exponentials, and the morphism categories `Mor(Sets())(X, Y)`. |
| `POL-SET-024` | Make set products and subsets delegate to the categorical product and subobject constructions instead of defining parallel APIs. |
| `POL-SET-025` | Make `Cardinal()` the set-enriched skeletal category of cardinal representatives. Its morphism categories `Mor(Cardinal())(k, l)` are discrete on the function sets between the selected representatives. Cardinal order is the existence of an injective map, not mere inhabitation of `Mor(Cardinal())(k, l)`. Its categorical coproducts, products, and exponentials give cardinal addition, multiplication, and exponentiation. The selected point functor `{Cardinal()} -> Semirings(Cat())` supplies the category object with its semiring methods. Cardinal objects form an ordered semiring of finite, infinite, and symbolic values, not integer wrappers. `Unknown` is a decision about a proposition, not a cardinal. |
| `POL-SET-026` | Let cardinal arithmetic return cardinal values. Let cardinal equality and order return applied propositions. `ask()` returns `Unknown` when available mathematics does not decide one of those propositions. |
| `POL-SET-027` | Use `len()` only for a finite sequence whose order is part of its meaning. Use `cardinality()` for every mathematical set. |
| `POL-SET-028` | When `rank()` or `ngens()` counts a mathematical set, return its cardinality rather than a sequence length. |
| `POL-SET-029` | Before enumerating a set, determine how the operation behaves for an infinite set and for a very large finite set. Keep unbounded enumeration out of the normal path. |
| `POL-SET-030` | Enumerate to compute cardinality only when a concrete cardinality is required, finiteness is established, and no construction formula or structural relation supplies it. |
| `POL-SET-031` | A constructor that knows a set's cardinality or structural property records it. Functors and related objects derive and transport that information. |
| `POL-SET-032` | Use `NN` for the positive integers. Zero is not an element of `NN`; use `ZZ_{>=0}` for the nonnegative integers. |
| `POL-SET-033` | Apply `POL-API-015` to cardinalities and standard integers. Write `k == 3`, `k <= 3`, or `3 < k`; do not expose named cardinal comparison methods or require integer coercion. |
| `POL-SET-034` | Never require a caller to extract a stored value from a cardinality. A cardinal is the mathematical value, not a wrapper around one; public code does not use `.value`, `.finite_value()`, or an equivalent accessor to compare, calculate with, display, or return it. |
| `POL-SET-035` | Define modulus with domain a finite cardinal `k` and a positive natural cardinal `n`. The value `k % n` is the finite cardinal represented by the natural-number remainder. |
| `POL-SET-036` | Make `Mor(Sets())(X, Y)` the morphism category in `Sets()`: the discrete category whose objects are the total maps from `X` to `Y`. The exponential `Y ** X` is the owned set of those maps, and `Mor(Sets())(X, Y)(rule)` constructs one of them. |

Grounding examples: the even positive integers are infinite, and \(\{1,2,\ldots,10^{10}\}\) is finite but unsuitable for materialization.
The set \(\{n\in\mathbb N\mid n\leq100\}\) is finite from its defining bound.
None requires enumeration to establish finiteness.

If `k` is a cardinal, write `k == 3`, `k <= 3`, or `3 < k`.
Do not write `k.equals(3)`, `k.le(3)`, `k.value == 3`, or `k.finite_value() <= 3`.
When an established finite algorithm requires a primitive loop bound, lower the cardinal once inside that private computation boundary.

## Sage boundary

| ID | Policy |
| --- | --- |
| `POL-SAGE-001` | The owned framework defines the mathematical category graph and public API. |
| `POL-SAGE-002` | Sage supplies computation objects, algorithms, coercion, and runtime machinery. |
| `POL-SAGE-003` | Cross into Sage only through an explicit realization functor or owned computation boundary. |
| `POL-SAGE-004` | Do not make a Sage category a mathematical supercategory of an owned category. |
| `POL-SAGE-005` | Do not modify Sage category classes or install owned methods on them. |
| `POL-SAGE-006` | Do not expose the Python method catalogue of a Sage implementation as the mathematical API. |
| `POL-SAGE-007` | Keep one owned public spelling for each mathematical operation. |
| `POL-SAGE-008` | Keep Sage's category runtime only for dynamic classes, refinement, joins, and construction support. |
| `POL-SAGE-009` | Preserve Sage `Parent`, `Element`, homsets, morphisms, and coercion where they implement the owned model. |
| `POL-SAGE-010` | Use Sage's exact algorithms before writing a parallel local implementation. |
| `POL-SAGE-011` | Use Sage's exact linear-algebra algorithms only behind the tensor realization boundary. Do not expose Sage vectors or matrices as owned objects. |
| `POL-SAGE-012` | Treat agreement with Sage or a Sage doctest as secondary evidence. It is not an independent mathematical oracle for owned behavior. |

## Public API and types

| ID | Policy |
| --- | --- |
| `POL-API-001` | Shape the API from the mathematics, not from current storage fields or Python classes. |
| `POL-API-002` | Give each operation one owner, one named public entry point, and one public export. A standard operator invokes that same owned operation and adds no second implementation. `Fun` is the sole exported alias: it names `Mor(Cat())` because functor construction is the most frequent call. |
| `POL-API-003` | Use standard mathematical and Sage syntax at call sites. |
| `POL-API-004` | Use `as_*` only for an explicit conversion to another mathematical representation. |
| `POL-API-005` | Keep private fields private to their owner or documented subclass contract. |
| `POL-API-006` | Ask another object through its public mathematical interface. |
| `POL-API-007` | Invoke Python special methods through public syntax such as `f(x)`, `iter(x)`, and `len(x)`. |
| `POL-API-008` | Name an accessor for the exact mathematical object or morphism it returns. |
| `POL-API-009` | Use positional standard notation: `Mor(C)(X, Y)` is the morphism category from `X` to codomain `Y`, and `Mor(C)(X, Y)(data)` constructs a morphism `X -> Y`. |
| `POL-API-010` | Let callers construct morphisms only through `Mor(C)(X, Y)(data)` and objects only through `C(data)`. The category-owned constructor is the sole dispatch. |
| `POL-API-011` | Treat every public method-name collision as mathematical ambiguity. Resolve it by naming the exact mathematical operation, not by inheritance precedence, overload selection, or context. |
| `POL-API-012` | Let a structured object expose every applicable operation under its unambiguous name. Its discoverable method surface must preserve distinctions between its structures. |
| `POL-API-013` | Name categorical morphisms as morphisms. Do not replace the standard mathematical object with implementation names such as `Map` or `Rule`. |
| `POL-API-014` | Ban nondescript identifiers that do not state what they contain or denote. Never name a type, method, parameter, field, or local value `data`, `container`, `rule`, or a similarly contentless term. |
| `POL-API-015` | Make every mathematical object and element use standard Python or Sage syntax for comparison, equality, containment, indexing, iteration, and calls. Do not expose a named method that forwards to an operator or special method. Write `x <= y`, `x == y`, and `x in X`; never write `x.le(y)`, `x.equals(y)`, or `X.contains(x)`. On every owned object, element, and morphism, `__eq__` returns the applied equality predicate and `__ne__` its negation; `ask(a == b)` decides it; the predicate's `__bool__` raises, so repository code writes `ask(a == b) is True`. Containment `in` remains the one Boolean boundary. `__hash__` is explicit: objects and morphisms hash by identity, and a classical element hashes by its chosen datum. |
| `POL-API-016` | Prefer a method or constructor on the mathematical owner over a standalone public function. Add a standalone public function only when the operation has no natural category, object, morphism, or functor owner. |
| `POL-API-017` | Never expose a method whose complete implementation only asserts `False`, returns `NotImplemented`, or raises an error. Such a method advertises a capability that the object does not have. |
| `POL-API-018` | Use an abstract method when every concrete object must supply an implementation. Prevent construction of an incomplete concrete object instead of deferring the failure to a method call. |
| `POL-API-019` | When an operation requires a capability, place it on the category that supplies that capability and let the method compiler expose it there. Do not install a failing placeholder on objects outside that category. |
| `POL-API-020` | When a non-predicate mathematical operation exists but available algorithms cannot determine its result, return its typed unknown value: the Sage singleton `Unknown` from `sage.misc.unknown`, with `Decision = bool | UnknownClass`. For an owned predicate, return its applied proposition and let `ask()` produce `Unknown`. Do not replace missing knowledge with a runtime failure. |
| `POL-API-021` | Make every method and constructor total on its declared domain. Require every argument. Never use optional parameters, default values, `None` sentinels, or fallback behavior. Give genuinely different mathematical input forms or computations separate explicit names. An evidence source for one property is not another constructor form. |
| `POL-API-022` | Let each property subcategory own one trusted constructor for its defining property. Do not add checked, hypothesis-backed, or theorem-backed constructor families. The ambient value's predicate owns exact computation, `assume(P(x))` uses the active session, and named mathematical constructions return directly through the same property constructor. Never select evidence with a Boolean, `Decision`, default, proof object, or prose. |
| `POL-API-023` | Never require a caller to supply a value uniquely determined by an established mathematical object or its category placement. Obtain that value from its owner. In particular, an isomorphism supplies its inverse; no leaf helper accepts a second candidate inverse. |
| `POL-TYPE-001` | Give every value the type that names its mathematical role. |
| `POL-TYPE-002` | Distinguish categories, objects, elements, morphisms, functors, rings, sets, domains, and codomains in types. |
| `POL-TYPE-003` | Never use `object` in a type annotation. There are no exceptions. |
| `POL-TYPE-004` | Annotate the candidate parameter of every `__eq__` and `__contains__` method as raw `Any`. These two parameter positions are the only permitted uses of `Any`. |
| `POL-TYPE-005` | Never use `Any` as a return type. |
| `POL-TYPE-006` | Do not silence a type error with a cast, ignored diagnostic, deleted annotation, or wider type. |
| `POL-TYPE-007` | Fix the mathematical model, method owner, import boundary, or missing type declaration exposed by a type error. |
| `POL-TYPE-008` | Use category membership as type information. Do not inspect fields or method names for capabilities. |
| `POL-TYPE-009` | Do not invent wrapper types whose only purpose is to satisfy the type checker. |
| `POL-TYPE-010` | Return `Self`, `None`, or the exact mathematical result type. Use the element type of `NN`, `ZZ`, or `RR` for natural numbers, integers, or real numbers. |
| `POL-TYPE-011` | Use a set, ordered set, multiset, indexed family, or another named mathematical collection in every theory-layer mathematical signature. The compiler-owned `structure_functors()` declaration returns the complete tuple required by `POL-CAT-085`. Never use `Iterable`, `Sequence`, `Collection`, `list`, or `tuple` for a mathematical collection. Use `float` only at an explicit numerical boundary. |
| `POL-TYPE-012` | Primitive signatures can occur inside a private method only when every consumer remains inside that private boundary. |
| `POL-TYPE-013` | Create a type for a genuine mathematical object. Do not wrap invalid constructor inputs in an engineering type to satisfy the checker. |
| `POL-TYPE-014` | Never alias `Any`, directly or as part of a wider alias. Such an alias erases type information while giving the erasure a misleading semantic name. |
| `POL-TYPE-015` | Do not create types with an `Input` suffix to model forms accepted by an implementation. Type each parameter as the mathematical object it denotes. |
| `POL-TYPE-016` | Use types to express the mathematics. Keep parsing, coercion, normalization, and representation conversion behind the typed mathematical boundary. |
| `POL-TYPE-017` | Type every morphism by the element types of its domain and codomain categories. Do not widen either endpoint to a generic mathematical-object type. |
| `POL-TYPE-018` | Give every category its own semantic object, element, and morphism types through `ObjectType`, `ElementType`, and `MorphismType`. Use those types throughout that category's API. |
| `POL-TYPE-019` | Type each method parameter and result by the most specific category that supplies the required structure. Do not widen it to an element or object type from a supercategory. |
| `POL-TYPE-020` | Preserve category-specific role types even when a category adds no new runtime fields or methods. Same-object property refinement updates the Sage dynamic class to include the refined role. It does not erase the refinement or allocate a second semantic value. |
| `POL-TYPE-021` | Admit raw Python container types only inside the implementation kernel, a backend adapter, or a dedicated interoperation module. Convert them immediately into the required mathematical collection before theory code receives them. A theory constructor or helper is not such a boundary. |
| `POL-TYPE-022` | Use `Iterator[T]` only for the Python traversal protocol or a private lazy-enumeration result. It never replaces a named mathematical collection in a theory-layer input or result. |
| `POL-TYPE-023` | Treat type-checker and import output as diagnostic signals. An error can falsify the current implementation, but it cannot establish a new architecture, mathematical owner, or runtime carrier. The mathematical definitions, category ownership, and functor declarations determine correctness. |
| `POL-TYPE-024` | Make the category compiler expose functorial construction and dynamic object, element, and morphism inheritance to static type checkers. A checker's default inability to infer that structure does not justify weakening it. |
| `POL-TYPE-025` | When a checker cannot infer the declared dynamic structure, generate `.pyi` stubs from the authoritative category and functor declarations: one kernel generator projects the same compile-time ownership computation that installs methods, and the commit hook regenerates the stubs whenever a declaration changes. Stub generation is the sole projection mechanism. Do not maintain a second type graph by hand. |
| `POL-TYPE-026` | Treat generated static typing artifacts as projections of repository-owned declarations. Regenerate them through the applicable commit, test, push, and release workflows whenever their source declarations change. |
| `POL-TYPE-027` | Do not define or use `typing.Protocol` or another structural duck type. Type mathematical values through the exact category-owned `ObjectType`, `ElementType`, or `MorphismType`, and express capabilities through category membership and structural functors. |
| `POL-TYPE-028` | Preserve the exact receiver, positional-parameter, keyword-parameter, and result roles of every declaration in its copied compiled method and generated typing artifact. `Callable[..., Any]` and `Callable[..., object]` are forbidden. |
| `POL-TYPE-029` | A broad union of unrelated mathematical roles is type erasure. Do not combine it with `Callable[...]` or variadic parameters as a substitute for each method's exact signature. |

The runtime compiler constructs category relations dynamically, but one repository revision contains a finite declaration graph.
A generator can project that graph into static typing artifacts without changing its mathematical owner.

For example, `gens()` is ambiguous on an object that can be a group, module, and algebra.
Expose `group_generators()`, `module_generators()`, and `algebra_generators()` side by side.
Each name identifies the structure whose generating set it returns.

For example, `SomeMathematicalObjectInput` names a constructor role rather than a mathematical object.
If the parameter denotes an element of a set, its type is `SetElement`.

The special-method signatures are `__eq__(self, candidate: Any)` and `__contains__(self, candidate: Any)`.
Use raw `Any` at those two special-method boundaries.

Likewise, do not define `MathematicalObject = Any` and then type `SetMapRule` as a callable on that alias.
A `SetMorphism` acts from `SetElement` to `SetElement`, with its specific domain and codomain stored on the morphism.
Its evaluation in `Mor(Sets())(X, Y)` can assert `x.parent() in self.base_category()` before verifying that `x` belongs to the declared domain `X`.

For a poset, define `PosetElement = Posets.ElementType` and type `is_sup(x: PosetElement)` accordingly.
Typing `x` as `SetElement` would admit an element without the required poset structure and conceal that error from static checking.

Likewise, use `OrderedSet[MyCatElement]`, not `Iterable[MyCatElement]`, when order and uniqueness are the mathematical input.
The latter type also admits raw lists, tuples, and Python iterators, which discards the required collection semantics.

Use `x <= y`, `x in X`, `X[i]`, and `x == y` instead of public methods such as `x.le(y)`, `X.contains(x)`, `X.index(i)`, or `x.equals(y)` that shadow that standard syntax.

Every object of `Sets()` has `cardinality()`.
It returns an exact cardinal or Sage `Unknown`.
A method available only under an additional mathematical hypothesis belongs to the corresponding property category.

For example, a total set constructor requires a typed cardinality.
The finite, countably infinite, and uncountable property subcategories each own the
constructor that requires and supplies the semantic cardinal data for that property.

Likewise, a natural interval constructor constructs its result directly in the total-order category.
The identity constructor constructs its result directly in the poset morphism category `Mor(Posets())(P, P)`.
A named squaring builder on `NN` constructs its result directly in the same morphism category.
These methods rely on their defining theorems and do not run exhaustive decision procedures.
An arbitrary relation or map starts in its ambient category. Its owned predicate performs
any available exact check. Exact `True` self-refines it through the same property-category
constructor used by the named constructions.

Replace a nondescript name with the exact entity, such as `tensor_coefficients`, `ordered_set`, or `set_morphism`.

A method that enumerates solutions yields them lazily.
The caller can materialize a finite result when its application requires one.

## Implementation style

| ID | Policy |
| --- | --- |
| `POL-CODE-001` | Write each method in the order of the mathematical definition. |
| `POL-CODE-002` | Keep the implementation direct and readable to a mathematician. |
| `POL-CODE-003` | Do not hide defining steps behind non-mathematical helper chains. |
| `POL-CODE-004` | Add an abstraction only when a second real use requires it. |
| `POL-CODE-005` | Use existing project dependencies before adding code or packages. |
| `POL-CODE-006` | Use a maintained library or mature reference implementation before writing local infrastructure. |
| `POL-CODE-007` | Cite the mature source of unavoidable local implementation code. |
| `POL-CODE-008` | Do not add compatibility layers, fallbacks, migrations, or obsolete aliases. |
| `POL-CODE-009` | Keep one current implementation for each operation or construction. |
| `POL-CODE-010` | Fix a repeated defect at its mathematical owner, not at each call site. |
| `POL-CODE-011` | Fail loudly when required mathematical structure or a dependency is absent. |
| `POL-CODE-012` | Do not inspect `__dict__` or recover mathematical structure from storage fields. |
| `POL-CODE-013` | Do not use `setattr` to assemble or modify a mathematical API. Define the method on its owning category or class. |
| `POL-CODE-014` | Keep a matrix distinct from the morphism it represents. |
| `POL-CODE-015` | Keep coordinates distinct from elements of their parent. |
| `POL-CODE-016` | Lower to a computation representation once and reconstruct the mathematical result once. |
| `POL-CODE-017` | Preserve exact arithmetic until an explicit numerical boundary. |
| `POL-CODE-018` | Keep precision parameters at the numerical boundary. |
| `POL-CODE-019` | Remove needless recomputation, enumeration, and verification without obscuring the mathematics. |
| `POL-CODE-020` | Call the owned public method directly. Do not use `getattr(x, name)` to select a mathematical operation. |
| `POL-CODE-021` | Write `assert x in C` for a categorical precondition. Do not write `assert isinstance(x, C.ObjectType)`. |
| `POL-CODE-022` | Use assertions for mathematical preconditions, functionality gates, and type narrowing. |
| `POL-CODE-023` | Make each assertion state a mathematical fact that remains true when the Python implementation class or field layout changes. |
| `POL-CODE-024` | Use an assertion for a violated mathematical precondition. Do not add `try`/`except`, fallback values, or recovery branches. |
| `POL-CODE-025` | When code assigns mathematical ownership wrongly or cannot express the fixed owner, stop runtime debugging and local mechanism design. Reapply the standard definition, identify the owner it already determines, and repair `Cat`, the morphism categories `Mor(n, C)`, method inheritance, and `Sets()` in dependency order. |
| `POL-CODE-026` | During a foundational migration, move each required behavior to its new owner before deleting its old implementation. |
| `POL-CODE-027` | Do not use `hasattr` to guess mathematical capabilities. Ask category membership or call the required category-owned operation. |
| `POL-CODE-028` | Prefer a named primitive that states the mathematical construction over a generic Python composition that merely reproduces it. |
| `POL-CODE-029` | Actively search the standard library, Sage, current dependencies, and maintained packages for primitives that make theory code read more like mathematics. |
| `POL-CODE-030` | Propose a new dependency when it materially improves mathematical vocabulary, auditability, or categorical uniformity. State the mathematical construction that the dependency supplies. |
| `POL-CODE-031` | Use `sum` and `prod` for established finite algebraic aggregations instead of mutable accumulator loops. Use the categorical indexed construction when the family can be infinite. |
| `POL-CODE-032` | Prefer `map`, `reduce`, comprehensions, and named functional combinators when they state the mathematical transformation more directly than an imperative loop. |
| `POL-CODE-033` | Make method bodies functional and expression-oriented. This style concerns transformations inside mathematically owned methods, not a proliferation of standalone functions. |
| `POL-CODE-034` | Replace long structural `if` and `elif` cascades with exhaustive `match` and `case` routing when the cases form a mathematical decomposition. |
| `POL-CODE-035` | Handle trivial or decisive cases with early returns. Then assert the stronger invariants established by their exclusion before implementing the remaining case. |
| `POL-CODE-036` | Prefer immutable transformations, explicit case analysis, and local equations in the style of Haskell and Lean over C-style mutable state and control flow. |
| `POL-CODE-037` | Do not rewrap a value when the new wrapper does not change its required type or semantics. Calls such as `int(0)`, `Integer(0)`, and `ZZ(0)` require a local comment that proves why the conversion is necessary. |
| `POL-CODE-038` | Do not add a function or method whose body only forwards to another function, method, operator, or special method. A category-owned semantic method that lowers inputs, invokes a mature algorithm, or reconstructs an owned result is an implementation rather than a forwarding wrapper. |
| `POL-CODE-039` | Never write `try`/`except` outside the implementation kernel. Let errors propagate from theory, leaf, functor, construction, backend-adapter, and public API code. |
| `POL-CODE-040` | Never use exceptions to select a route, discover a capability, handle optional data, retry, choose an implementation, substitute a value, or continue computation. |
| `POL-CODE-041` | Never catch an exception to return `False`, `Unknown`, `None`, `NotImplemented`, or a default. An unknown mathematical result is explicit data, not a converted runtime failure. |
| `POL-CODE-042` | Compare mechanisms by their semantic role and information flow, not by syntax or location. Moving the same carrier among a decorator, `Annotated` payload, marker type, wrapper, callback, registry, generated class, or helper module leaves the architecture unchanged and does not satisfy a policy that rejects that carrier. |
| `POL-CODE-043` | Before adding a carrier for a proposition, construction obligation, method role, or ownership fact, locate its existing mathematical owner. If its software representation is unclear, stop the edit and derive that representation from the standard definition. Never let implementation momentum or a type, import, or runtime error choose the carrier. |

For adjacent elements, use `itertools.pairwise(xs)` instead of `zip(xs, xs[1:])`.
The named primitive states adjacency, remains lazy, and does not require slicing.
Use `zip` when the mathematics pairs separate indexed families.

Write a finite linear combination as `sum(c_i * e_i for c_i, e_i in terms)` and a finite multiplicative aggregation as `prod(a_i for a_i in factors)`.
The corresponding indexed categorical sum or product owns the potentially infinite case.

Within an owned method, route disjoint construction forms with `match` and `case`.
Return immediately for identities, zero objects, empty diagrams, or already-normal forms when those cases apply.
Assert the mathematical hypotheses that remain before entering the general branch.

For example, do not define `equals(x, y)` to return `x == y` or define `Y.contains(X)` to return `X in Y`.
Use the standard syntax directly.

## Tests and performance

| ID | Policy |
| --- | --- |
| `POL-TEST-001` | Read the repository test rules before editing a test file. |
| `POL-TEST-002` | Make every assertion state a mathematical proposition or an essential type invariant. |
| `POL-TEST-003` | Test the intended end-to-end behavior, not implementation layout or past defects. |
| `POL-TEST-004` | Assert the correct category, parent, domain, codomain, images, composition, and mathematical equality as applicable. |
| `POL-TEST-005` | Use the smallest specimen that distinguishes correct behavior from a plausible failure. |
| `POL-TEST-006` | Test object, element, and morphism inheritance by calling inherited public operations through the real category compiler. Route records, compiled-class identities, and caches do not prove that public surface. |
| `POL-TEST-007` | Test universal constructions through their universal morphisms, not only their apex objects. |
| `POL-TEST-008` | Use a real Sage process for Sage behavior. |
| `POL-TEST-009` | Do not add a test that only asserts the absence of a previous mistake. |
| `POL-TEST-010` | Treat a passing test as evidence only for the proposition it executes. |
| `POL-TEST-011` | Give every mathematical expected value an independent oracle: an inspected source, a theorem-derived formula, or an independently verified canonical fixture. |
| `POL-TEST-012` | Cite the exact theorem, section, table, or page that fixes a literature-based test value. |
| `POL-TEST-013` | Inspect the cited source before writing the fixture. Do not reconstruct a citation or expected value from memory. |
| `POL-TEST-014` | Use Sage parity only as a secondary check. Do not make the implementation under test or Sage's matching output its own oracle. |
| `POL-TEST-015` | Never change an expected mathematical fact to match the implementation output. Repair the implementation or establish a better oracle. |
| `POL-TEST-016` | Use a canonical object or a source-defined fixture. Use a matrix fixture only when the source datum is that matrix or the test constructs its semantic realization. |
| `POL-TEST-017` | Use rank, determinant, signature, parity, dimension, and nonemptiness only as guards when the claim under test is stronger. |
| `POL-TEST-018` | Assert isomorphism, classification data, action, semantic kernel, semantic cokernel, or a universal morphism when that is the mathematical claim. |
| `POL-TEST-019` | Test through the public semantic API. Do not assert coordinate arrays, matrix ranks, private hooks, concrete classes, helper calls, or field layout. |
| `POL-TEST-020` | Do not use `is not None`, `len(x) > 0`, `isinstance`, `hasattr`, `getattr`, or `setattr` as the main evidence for a mathematical claim. |
| `POL-TEST-021` | Use exact arithmetic and exact equality for exact mathematical claims. |
| `POL-TEST-022` | Cross-check an ambiguous expected fact through an independent theorem, implementation, or representation. |
| `POL-TEST-023` | Do not use mocks, simulations, skipped tests, or expected failures as evidence for mathematical behavior. |
| `POL-TEST-024` | Test repository-owned behavior. Do not spend assertions re-proving Sage, Python, or a cited theorem in isolation. |
| `POL-TEST-025` | Keep an assertion only if a plausible mathematically wrong implementation can fail it. |
| `POL-TEST-026` | Let a citation establish the oracle. Assert the resulting mathematical fact rather than the citation text or source layout. |
| `POL-TEST-027` | Make each mathematical test failure state the failed proposition and the expected mathematical behavior. A user must not need implementation context to understand the failure. |
| `POL-PERF-001` | Measure performance with wall time as a function of input size. |
| `POL-PERF-002` | Use call counts only to locate repeated work. Do not use them as efficiency evidence. |
| `POL-PERF-003` | Preserve code that displays the mathematical sequence when a faster form hides it. |
| `POL-PERF-004` | Use small mathematical specimens unless the claim concerns a large named object. |
| `POL-PERF-005` | Keep an enumeration-based approximation explicit and outside foundational paths. Log a clear warning before a potentially large enumeration begins. |

Enumerating isotropic subgroups of a torsion bilinear module can be an explicit first approximation.
It remains a replaceable algorithm, not the representation or default structural method.

## Documentation ownership

| ID | Policy |
| --- | --- |
| `POL-DOC-001` | Use `CONTRIBUTING.md` for general contribution principles and recurring patterns. State the general rule first and use concrete cases only as grounding examples. |
| `POL-DOC-002` | Add a specific observed antipattern to `CONTRIBUTING.md` only when its recurrence or severity makes a dedicated indexed warning useful. Keep its governing general principle explicit. |
| `POL-DOC-003` | Make each specification a forward-facing inventory of the desired mathematical capabilities and public API. |
| `POL-DOC-004` | A specification can describe a private implementation strategy when it constrains feasibility or architecture. Keep backend types, names, and decisions outside the public contract. |
| `POL-DOC-005` | Make each category specification declare its complete `structure_functors()` tuple. Use the exact functor retained by its defining construction, or construct it through `Fun(self, Target)`. Each entry is an ordinary functor. The tuple replaces `super_categories()` as compiler input and determines inherited structure. |
| `POL-DOC-006` | State which capabilities the specified category owns. State inherited capabilities by naming their owning category and the functor path that supplies them. |
| `POL-DOC-007` | Keep one authoritative catalogue for each public method surface. Reference that catalogue from dependent specifications instead of copying it. |
| `POL-DOC-008` | Mention a small number of inherited methods only when they clarify a category-specific example. Do not reproduce the inherited API inventory. |
| `POL-DOC-009` | Declare only mathematically meaningful immediate structural functors. Obtain deeper inherited capabilities by functor composition, not by adding direct functors for convenience. |
| `POL-DOC-010` | Put a mathematical distinction or formal term in an implementation plan only when it changes a required construction, public API, admissible result, or failure condition. Vocabulary alone creates no implementation decision. |
| `POL-DOC-011` | Classify two statements as contradictory only when they impose requirements that cannot both hold in the same scope and context. An override replaces an earlier rule. A specialization narrows it. An unresolved choice records alternatives. A different presentation is not a contradiction unless it imposes incompatible requirements. |
| `POL-DOC-012` | When reconciling project history, let the latest explicit user decision and its stated context control earlier drafts. Then normalize every current durable owner. Do not use the current documents' conflict as evidence for either side. |
| `POL-DOC-013` | Keep an executing plan limited to active decisions, fixed requirements and exclusions, dependency order, and acceptance conditions. Put completed work, archaeology, revision history, and provenance in a separate record. |

For example, a lattice specification declares its selected functor to the appropriate formed-module category.
When its ambient category has a selected carrier functor to `Sets()`, cardinality arrives through the composite route from formed modules through modules and that carrier functor.
It does not list cardinality as a lattice-owned method or add a direct lattice-to-`Sets()` functor.

## Policy maintenance

| ID | Policy |
| --- | --- |
| `POL-INDEX-001` | Give every coding policy exactly one unique identifier. |
| `POL-INDEX-002` | Add an identifier only for a new coding rule, not for an example or restatement. |
| `POL-INDEX-003` | Keep identifiers stable when policy wording improves. |
| `POL-INDEX-004` | Retire an obsolete identifier without assigning it to another policy. |
