# Contribution policy index

This index preserves policy identifiers for review and design discussion.
A linked row delegates its complete contract to that section.
A direct rule records a constraint without a complete specification owner.

[AGENTS.md][sources of truth] defines source authority and execution.
[System architecture](specs/system.md) defines layers and dependencies.
Topic specifications define mathematics and public contracts.
[Decisions](specs/decisions.md) records provenance and supersession.
Phase cards alone record current work and acceptance state.

## Scope and layers

| Policy identifiers | Contract |
| --- | --- |
| `POL-SCOPE-001`, `POL-SCOPE-002`, `POL-SCOPE-004`, `POL-SCOPE-006` | [Implementation and dependencies][implementation and dependencies]. |
| `POL-SCOPE-003` | [Morphism tower][morphism tower] and [Fixed-object constructions][fixed-object constructions]; include endomorphisms, monomorphisms, epimorphisms, isomorphisms, automorphisms, and `Fun([1], C)`. |
| `POL-SCOPE-005` | Implement the full owned `Sets()` category as a foundation for later mathematics. |
| `POL-SCOPE-007`, `POL-SCOPE-009` | [Review and acceptance][review and acceptance]. |
| `POL-SCOPE-008`, `POL-SCOPE-010`, `POL-SCOPE-011`, `POL-SCOPE-012`, `POL-SCOPE-013`, `POL-SCOPE-016` | [Layer ownership][layer ownership]. |
| `POL-SCOPE-014` | Apply a primitive ban to its stated purpose and layer; an implementation-only kernel use is not mathematical classification. |
| `POL-SCOPE-015` | A primitive ban applies to every layer unless an explicit layer rule narrows it. |

## Owned package universe

| Policy identifiers | Contract |
| --- | --- |
| `POL-SHADOW-001` | Shadow supported Sage names with package-owned mathematical objects. |
| `POL-SHADOW-002` | `sage_categories.all` is the primary opt-in import surface, with familiar names for the supported owned universe. |
| `POL-SHADOW-003` | [Computation boundary][computation boundary]. |
| `POL-SHADOW-004` | Construct supported owned counterparts explicitly; never graft arbitrary Sage objects into the owned hierarchy. |
| `POL-SHADOW-005`, `POL-SHADOW-007` | Importing the owned universe guarantees only supported owned workflows. Ordinary Sage interoperability is incidental. |
| `POL-SHADOW-006` | Absorb each required Sage construction through owned categorical APIs; its Sage implementation can remain private. |

## Mathematical model

| Policy identifiers | Contract |
| --- | --- |
| `POL-MATH-001`, `POL-MATH-012`, `POL-MATH-033`, `POL-MATH-038` | [Starting a work unit][starting a work unit]. |
| `POL-MATH-002` | [Cat and its implementation][cat and its implementation]. |
| `POL-MATH-003`, `POL-MATH-004` | [Functor actions][functor actions]. |
| `POL-MATH-005` | Distinguish a mathematical object from its presentation, coordinates, matrix, and private engine value. |
| `POL-MATH-006` | Distinguish an element from its image under a morphism. |
| `POL-MATH-007`, `POL-MATH-008` | Retain chosen structure as owned mathematical data. Recover data determined by its defining morphism. |
| `POL-MATH-009`, `POL-MATH-010` | Define each operation once at the weakest categorical hypotheses that imply it; obtain special cases by restriction. |
| `POL-MATH-011`, `POL-MATH-023`, `POL-MATH-040`, `POL-MATH-049`, `POL-MATH-050`, `POL-MATH-051`, `POL-MATH-052`, `POL-MATH-053` | [Documentation changes][documentation changes]. |
| `POL-MATH-013`, `POL-MATH-014`, `POL-MATH-024`, `POL-MATH-028` | Definition and inspected theorems supply exact typed conclusions at their construction owner. Citations stay in immediate source documentation; runtime does not prove the theorem. |
| `POL-MATH-015` | A form is a callable object of `Mor(C)(A, B)`; a matrix is only a representation. |
| `POL-MATH-016` | [Same-object refinement][same-object refinement]. |
| `POL-MATH-017` | Construct in the strongest established category. Mathematical evidence is never a certificate, proof record, prose field, token, marker, or justification wrapper. |
| `POL-MATH-018`, `POL-MATH-019` | Define public constructions by morphisms and universal properties, including in categories without elements. Element formulas are implementations or consequences. |
| `POL-MATH-020`, `POL-MATH-021` | Retain the base category and structure morphism in each dependent object, parent, type, and morphism. Different structure maps define different objects. |
| `POL-MATH-022` | State the weakest algebraic hypotheses under which each definition and algorithm is valid. |
| `POL-MATH-025` | Return `Unknown` only when defining data, hypotheses, construction theorems, inspected sources, and exact algorithms do not decide the question. Preserve it at Boolean boundaries. |
| `POL-MATH-026`, `POL-MATH-027` | Runtime accepts no proof prose or renamed substitute as mathematical evidence. Use typed mathematical data, exact predicates, explicit hypotheses, or construction rules. |
| `POL-MATH-029` | Only exact `True` establishes a proposition. Hypotheses and construction theorems are separate knowledge sources; absence of rejection establishes nothing. |
| `POL-MATH-030` | Use a defining construction or theorem before exhaustive verification, even on a finite domain. |
| `POL-MATH-031`, `POL-MATH-032`, `POL-MATH-045`, `POL-MATH-055` | A fact has one semantic owner and declaration: its category, exact type, defining morphism, functor, universal presentation, construction, predicate, or session assumption. Runtime metadata, generated entities, or authority tokens cannot repeat or establish that fact. |
| `POL-MATH-034` | [Mathematical questions][mathematical questions] and [Typed queries][typed queries]. Predicate applications and comparisons of typed queries are propositions; forming either question does not evaluate it. |
| `POL-MATH-035` | Ask a proposition before each branch or assertion; reject `Unknown` where a decision is required. [Public propositions][public propositions]. |
| `POL-MATH-036`, `POL-MATH-037`, `POL-MATH-041` | The writer selects categorical laws, properties, universal constructions, coherence, and equivalences from mathematics. Typed construction asserts them; runtime, tests, citations, and computation do not certify them. |
| `POL-MATH-039` | Mathematicians audit all theory declarations, including `Cat`, `Mor`, `Fun`, and properties. Show the standard definition, defining data, and construction asserting each property. Keep runtime wiring outside this audit path; judge the kernel by the mathematical surface it supports. |
| `POL-MATH-042` | Register an exact handler only on its declared semantic domain. Return `None` when undecided; no handler proves a general categorical property. [Proposition handlers][proposition handlers]. |
| `POL-MATH-043` | Treat `Cat` as an abstract universe with unspecified foundation. Use only its explicitly declared structure. |
| `POL-MATH-044` | A mathematical term imports only its explicit repository definition, not surrounding theory or additional laws. |
| `POL-MATH-046`, `POL-MATH-047`, `POL-MATH-048` | [Structure functors and inheritance][structure functors and inheritance]. |
| `POL-MATH-054` | [Layer ownership][layer ownership]. |

## Construction and mathematical identity

| Policy identifiers | Contract |
| --- | --- |
| `POL-ONT-001` | Raw Python values are private carrier data. Owned objects, elements, and morphisms use their category-owned types. [Points and generalized elements][points and generalized elements] fixes their categorical meanings. |
| `POL-ONT-002`, `POL-ONT-008` | [Constructors][constructors] and `POL-API-021`: exact total routes, datum-based `match` dispatch, distinct named presentations, and same-object placement by assumption. |
| `POL-ONT-003` | [Category containment][category containment]. |
| `POL-ONT-004`, `POL-ONT-005` | [Repeated failures][repeated failures]. |
| `POL-ONT-006` | [Proposition handlers][proposition handlers]. |
| `POL-ONT-007` | A callable is constructor input. Construct an owned morphism with explicit endpoints through `Mor(C)(A, B)(rule)`. |
| `POL-ONT-009` | Use [Fixed-object constructions][fixed-object constructions], comma categories, and functor categories for their instances. Leaf-specific names denote these generic constructions, not separate container classes. |
| `POL-ONT-010` | [Starting a work unit][starting a work unit]. |
| `POL-ONT-011` | Properties, predicates, and queries are direct methods on the most general category-owned implementation class that defines them. |

## Propositions and assumptions

| Policy identifiers | Contract |
| --- | --- |
| `POL-ASSUME-001` | [Public propositions][public propositions]. |
| `POL-ASSUME-003`, `POL-ASSUME-008`, `POL-ASSUME-016` | [Proposition handlers][proposition handlers]. |
| `POL-ASSUME-002`, `POL-ASSUME-007`, `POL-ASSUME-010`, `POL-ASSUME-011` | [Assumptions][assumptions]. |
| `POL-ASSUME-018` | An ambient hypothesis is a zero-argument SymPy predicate application. Theory modules can declare it in `global_assumptions`; `retract()` removes it. It refines no value. [Assumptions][assumptions]. |
| `POL-ASSUME-004` | [Evaluation][evaluation] maps only SymPy `None` to the existing Sage `Unknown` singleton. |
| `POL-ASSUME-005`, `POL-ASSUME-015` | Mathematical truth questions form propositions; partial value questions form typed queries. Only implementation facts can return a Boolean. [Mathematical questions][mathematical questions]. |
| `POL-ASSUME-006` | [Equality][equality]. |
| `POL-ASSUME-009`, `POL-ASSUME-013` | [Public propositions][public propositions]. |
| `POL-ASSUME-012` | Never compare propositions or decisions by identity with `True` or `False`. Use `ask()` and reject undecided Boolean admission. |
| `POL-ASSUME-014` | At each required Boolean decision, ask and reject Sage `Unknown`; name the undecided proposition. |
| `POL-ASSUME-017` | Validate constructor input before normalization; an invalid input must not become a different valid value. |

## Tensor representations

| Policy identifiers | Contract |
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

## Private computation

| Policy identifiers | Contract |
| --- | --- |
| `POL-ENGINE-001`, `POL-ENGINE-003`, `POL-ENGINE-006`, `POL-ENGINE-008`, `POL-ENGINE-009`, `POL-ENGINE-014`, `POL-ENGINE-016` | [Computation boundary][computation boundary]. |
| `POL-ENGINE-002` | [Computation boundary][computation boundary]; only authorized SymPy proposition expressions cross it as engine values. Nested identity atoms stay private. |
| `POL-ENGINE-004` | Use owned `f.image()` and `Sets().Subobjects(X).from_predicate(predicate)`; engine set constructors stay private. |
| `POL-ENGINE-005` | Retain the defining morphism of an image subobject; construction data establishes its category and inherited operations. |
| `POL-ENGINE-007`, `POL-ENGINE-012` | An engine supplies private representations and algorithms, not a second implementation class, public surface, registry, selectable backend, or replaceability layer. |
| `POL-ENGINE-010` | Translate partial engine results into the owned result type; map SymPy `None` to Sage `Unknown` only in public `ask()`. |
| `POL-ENGINE-011` | A timeout, crash, incomplete calculation, or indeterminate engine result establishes no property, refinement, or Boolean answer. |
| `POL-ENGINE-013` | A private representation, cache, or algorithm call requires no realization functor, category, compiler binding, or natural transformation. |
| `POL-ENGINE-015` | [Fixed private dependencies][fixed private dependencies]. |

## Algebraic generality

| Policy identifiers | Contract |
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
| `POL-GEN-013`, `POL-GEN-014` | General coefficient families define formal power series. Polynomials require finite support and arise by restriction; use `poincare_series()` for the general operation. |
| `POL-GEN-015` | Return a lazy iterator when a method enumerates a result family and materialization is not part of the mathematics. Do not encode an unproved finiteness assumption by returning a list or tuple. |
| `POL-GEN-016` | [Internal algebraic families][internal algebraic families]: magmas require a tensor bifunctor, monoids a monoidal structure, and groups a cartesian monoidal structure. |
| `POL-GEN-017` | [Internal semirings][internal semirings] and [Internal rings][internal rings]. |
| `POL-GEN-018` | [Module objects][module objects] and [Module action laws][module action laws]. |
| `POL-GEN-019` | [Algebra objects][algebra objects] and [Algebra structure functor][algebra structure functor]. |
| `POL-GEN-020` | Define each algebraic family once over its ambient parameter. An instance fixes the parameter; it is neither the definition nor its specialization. Cite each instance and state only downstream mathematical additions. |
| `POL-GEN-021` | [Algebraic laws][algebraic laws]. Structure maps are morphisms out of products; they carry no diagram, cone, injection, or projection. |

## Forms and lattices

| Policy identifiers | Contract |
| --- | --- |
| `POL-FORM-001` | An `R`-lattice is a finitely generated projective `R`-module with the specified form. Present `(M, b)` as a subobject of a product category whose first factor is the applicable module category; its projection supplies the module interface. |
| `POL-FORM-002` | A `W`-valued bilinear form is a morphism `M tensor_R M -> W`, encoded by its Gram tensor. A lattice tensor product inherits the module tensor product and adds the induced tensor of forms; the module owner retains the tensor universal property. |
| `POL-FORM-003` | Use “inner product” only for a positive-definite symmetric bilinear form. |
| `POL-FORM-004` | Do not assume that a lattice is positive definite, embedded in a vector space, free, based, or unimodular. |
| `POL-FORM-005` | Distinguish left and right radicals for a nonsymmetric bilinear form. |
| `POL-FORM-006` | Define orthogonal complements, norms, and reflections only under the symmetry and nondegeneracy hypotheses they require. |
| `POL-FORM-007` | Determine definiteness from the exact behavior of the form on elements, not from floating eigenvalues or numerical spectra. |
| `POL-FORM-008` | Use exact coefficient rings and exact arithmetic for form and lattice predicates. |
| `POL-FORM-009` | Choose the minimal exact coefficient extension required by the mathematical object. Do not approximate algebraic coefficients by floats. |
| `POL-FORM-010` | Use “Gram tensor” for the tensor that encodes a bilinear form. Keep its chosen-basis coefficient data inside that tensor. |

## Category ownership and inheritance

| Policy identifiers | Contract |
| --- | --- |
| `POL-CAT-001`, `POL-CAT-036`, `POL-CAT-039` | [Constructors][constructors]. |
| `POL-CAT-002` | [Cat and its implementation][cat and its implementation] and [Morphism tower][morphism tower]. |
| `POL-CAT-003`, `POL-CAT-005`, `POL-CAT-006`, `POL-CAT-007`, `POL-CAT-014`, `POL-CAT-015`, `POL-CAT-016`, `POL-CAT-047`, `POL-CAT-049`, `POL-CAT-053`, `POL-CAT-054`, `POL-CAT-056`, `POL-CAT-058`, `POL-CAT-059`, `POL-CAT-062`, `POL-CAT-085`, `POL-CAT-096` | [Structure functors and inheritance][structure functors and inheritance]. |
| `POL-CAT-004` | [Leaf contract][leaf contract]. |
| `POL-CAT-008` | [Owned implementation types][owned implementation types]. |
| `POL-CAT-009`, `POL-CAT-010`, `POL-CAT-012`, `POL-CAT-013`, `POL-CAT-061`, `POL-CAT-064` | [Sage class construction][sage class construction]. |
| `POL-CAT-011` | [Semantic collisions][semantic collisions]. |
| `POL-CAT-017` | Declare an axiom at the most general category that can state it. |
| `POL-CAT-018`, `POL-CAT-019` | Property membership selects no witness; chosen data is separate structure. [Property category][property category]. |
| `POL-CAT-020` | Every construction establishes its result-category obligations by definition, exact computation, theorem, or explicit hypothesis; an unrelated property supplies none. |
| `POL-CAT-021`, `POL-CAT-022`, `POL-CAT-089` | [Morphism tower][morphism tower]. |
| `POL-CAT-023` | [Morphism tower][morphism tower] fixes category call and endpoint forms. Identity is `End_C(X).one()`; `Y ** X` is the exponential. |
| `POL-CAT-024` | `Mor(C).ObjectType` owns morphism endpoints, exposed by `domain()` and `codomain()`. |
| `POL-CAT-025` | State a morphism property through its property subcategory of `Mor(C)`. |
| `POL-CAT-026` | [Fixed-object constructions][fixed-object constructions]. |
| `POL-CAT-027`, `POL-CAT-028`, `POL-CAT-029` | Keep a general hom category-valued and distinguish internal Hom from global morphisms. Use an explicit set-valued functor with its required hypotheses before treating a mathematical entity as a set. |
| `POL-CAT-030` | Establish the stated `Sets()` placement or apply an explicit functor to `Sets()` before using set elements, membership, cardinality, enumeration, subsets, or set equality. |
| `POL-CAT-031`, `POL-CAT-035`, `POL-CAT-055`, `POL-CAT-080` | [Starting a work unit][starting a work unit]. |
| `POL-CAT-032` | An operation belongs at the most general category declaring its result, even when its value is partial or no general algorithm exists. |
| `POL-CAT-033` | Subcategories state mathematical properties or structure, never implementation selection. A structure category names its operation once, `operation()`; `+` and `*` belong to the named copies `AdditiveMonoids(V) = Monoids(V) × 1_+` and `MultiplicativeMonoids(V)`, which rename the generator and receive no neutral name (D185). |
| `POL-CAT-034` | Use `POL-API-021`. This identifier remains reserved. |
| `POL-CAT-037`, `POL-CAT-038`, `POL-CAT-067`, `POL-CAT-068`, `POL-CAT-069`, `POL-CAT-074`, `POL-CAT-081`, `POL-CAT-082` | [Same-object refinement][same-object refinement]. |
| `POL-CAT-040`, `POL-CAT-041`, `POL-CAT-042` | Evaluate a morphism only on owned elements of its domain and return owned codomain elements. Validate parents in the base category and exact endpoints. Convert raw representations before evaluation. |
| `POL-CAT-043` | [Category containment][category containment]. |
| `POL-CAT-044` | [Defining predicate][defining predicate]. |
| `POL-CAT-045` | [Inherited constructions][inherited constructions]. |
| `POL-CAT-046`, `POL-CAT-050`, `POL-CAT-051`, `POL-CAT-052`, `POL-CAT-093`, `POL-CAT-105` | [Diagrams and universal constructions][diagrams and universal constructions]. |
| `POL-CAT-079` | Place operations at the most general category that guarantees them. Isomorphisms own inversion; [Diagrams and universal constructions][diagrams and universal constructions] owns presentation operations and unambiguous apex conveniences. |
| `POL-CAT-048` | Expose attached structure by its exact mathematical name. [Structure functors and inheritance][structure functors and inheritance] determines which selected functors also supply inheritance. |
| `POL-CAT-057` | Each explicit category declares its own three implementation types, including empty declarations. Axiom-generated categories repeat no leaf declaration. [Owned implementation types][owned implementation types] and [Same-object refinement][same-object refinement]. |
| `POL-CAT-060` | [Property category][property category]. |
| `POL-CAT-063`, `POL-CAT-075`, `POL-CAT-077` | The owning typed method is the sole declaration of ownership, body, call shape, parameters, and results. Preserve exact signatures in compiled methods and derive projections from them; no decorator, descriptor, registry, or metadata substitutes for that declaration. |
| `POL-CAT-076` | Keep exact mathematical types, Python positional/keyword/variadic call shape, and construction provenance distinct. Named functors and retained presentations state provenance; none of these facts replaces another. |
| `POL-CAT-065`, `POL-CAT-072` | Inherited calls preserve the exact lazy-result or owned-collection type and each item type, without wrapping, relabeling, or inferring collection semantics from Python protocols. |
| `POL-CAT-066`, `POL-CAT-071` | [Functor actions][functor actions]. |
| `POL-CAT-070` | All entry paths select the exact established category before allocation. Raw allocators are private to that category constructor. Cross-module constructor entry points need public mathematical names and exact parameters, including private helpers called by siblings. |
| `POL-CAT-073` | `X in C` states mathematical admissibility. Exact category identity is an implementation fact and does not trigger normalization. |
| `POL-CAT-078` | A category, object, morphism, functor, or universal construction owns a mathematical fact; runtime and generated infrastructure do not. |
| `POL-CAT-083` | [Points and generalized elements][points and generalized elements]. |
| `POL-CAT-084` | [Inverse-image properties][inverse-image properties]. |
| `POL-CAT-086` | Keep `Mor(C)(A, B)` symbolic when inhabitation is undecided. Axioms for `Cat().Inhabited()` and `.Empty()` supply generated proposition methods; `Unknown` does not replace the category. |
| `POL-CAT-087` | [Subcategory declarations][subcategory declarations]. |
| `POL-CAT-088` | On categories, `C * D` and `C + D` are product and coproduct categories, and `D ** C` is `Fun(C, D)`. `Cat().ElementType` supplies product, coproduct, biproduct, and exponential defaults, subject to category-owned algebraic overrides. [Diagrams and universal constructions][diagrams and universal constructions] fixes the product pattern and retained morphisms. |
| `POL-CAT-090` | [Functor properties][functor properties]. |
| `POL-CAT-091` | [Functor property resolution][functor property resolution]. |
| `POL-CAT-092` | [Fixed-object constructions][fixed-object constructions] and [Diagrams and universal constructions][diagrams and universal constructions]. The generic owner defines each construction once; leaves add realizations. Each limit family has a supplied shape; declarations of bicompleteness and cartesian closure assert nothing about an unsupplied category or shape. |
| `POL-CAT-094` | [Component functors][component functors]. |
| `POL-CAT-095`, `POL-CAT-103` | [Comma categories and fibers][comma categories and fibers]. |
| `POL-CAT-097` | Preserve the supplied diagram index family. Order commutative canonical forms only by owned mathematical keys, never printed representations. |
| `POL-CAT-098` | Chosen data defines a total fibration with stated morphisms and cartesian arrows. [Indexed categories and representations][indexed categories and representations]. A generating family is an epimorphism `Free_R(S) -> M`; a finite presentation is a length-two resolution `Free_R(X_1) -> Free_R(X_0) -> M`. General resolutions use the same construction at their stated shapes, not new axioms. |
| `POL-CAT-099` | [Opposites and dualization][opposites and dualization]. |
| `POL-CAT-100` | [Inverse-image subcategories][inverse-image subcategories]. |
| `POL-CAT-101` | [Functor-category calculus][functor-category calculus]. |
| `POL-CAT-102` | [Inverse-image subcategories][inverse-image subcategories], [Restrictions and base change][restrictions and base change], and [Comma categories and fibers][comma categories and fibers]. |
| `POL-CAT-104` | [Adjunctions and equivalences][adjunctions and equivalences], [Diagrams and universal constructions][diagrams and universal constructions], and [Indexed categories and representations][indexed categories and representations] own selected data and their structure-preserving morphisms. |
| `POL-CAT-106` | [Indexed categories and representations][indexed categories and representations]. |

## Leaf implementations

| Policy identifiers | Contract |
| --- | --- |
| `POL-LEAF-001`, `POL-LEAF-003`, `POL-LEAF-005`, `POL-LEAF-007`, `POL-LEAF-008`, `POL-LEAF-016`, `POL-LEAF-032`, `POL-LEAF-037`, `POL-LEAF-038`, `POL-LEAF-049`, `POL-LEAF-058`, `POL-LEAF-061` | [Leaf structure functors][leaf structure functors]. |
| `POL-LEAF-002`, `POL-LEAF-004` | [Constructors][constructors]. |
| `POL-LEAF-006`, `POL-LEAF-025`, `POL-LEAF-026`, `POL-LEAF-036`, `POL-LEAF-039`, `POL-LEAF-052` | [Repeated failures][repeated failures]. |
| `POL-LEAF-009`, `POL-LEAF-044`, `POL-LEAF-048` | [Computation boundary][computation boundary]. |
| `POL-LEAF-010` | [Verification][verification]. |
| `POL-LEAF-011`, `POL-LEAF-017` | [Inherited constructions][inherited constructions] and [Diagrams and universal constructions][diagrams and universal constructions]: supply the mathematical lifting data at the structure functor; the generic construction supplies projections and mediators. Declare `.CreatesLimits(I)` where its reflection condition also holds. |
| `POL-LEAF-012`, `POL-LEAF-021`, `POL-LEAF-056`, `POL-LEAF-060` | [Inherited constructions][inherited constructions]. |
| `POL-LEAF-013`, `POL-LEAF-015` | A leaf author uses its mathematics and nearby category contracts. Adding a leaf requires neither kernel changes nor knowledge of distant subtrees. |
| `POL-LEAF-014` | Maintain the [leaf design templates][]: ordinary leaves, property implementations, pullback-defined categories, chosen-datum fibrations, and universal-construction realizations. They show minimal constructors, complete actions, immediate retained functors, new methods, and exact handlers. Templates are design pseudocode, never executed, imported, type-checked, or graded by spelling; their shape must compile without duplicate ownership or layer violations. |
| `POL-LEAF-018`, `POL-LEAF-027`, `POL-LEAF-028` | [Inherited operations][inherited identity, composition, construction, and retention]. |
| `POL-LEAF-019` | Elements use their owning category's `ElementType`; no separate free-standing element category replaces it. |
| `POL-LEAF-020` | Each explicit refinement or construction declares its own three implementation types. [Same-object refinement][same-object refinement] supplies the dynamic class without copying state. |
| `POL-LEAF-022` | Require exactly the named structure. Totality adds total comparison to a partial order; enumeration, ranking, and unranking require separate structure. |
| `POL-LEAF-023`, `POL-LEAF-035` | [Same-object refinement][same-object refinement]. |
| `POL-LEAF-034` | [Kernel machinery in a leaf][kernel machinery in a leaf] fixes retention. Leaves own no ambient wrapper, refinement cache, or local refinement mechanism. |
| `POL-LEAF-024` | [Leaf contract][leaf contract]. |
| `POL-LEAF-029`, `POL-LEAF-030`, `POL-LEAF-031` | Override inherited behavior only for a new leaf mathematical or realization step. First form its inherited semantic result; preserve the operation's name, laws, endpoints, and owner. Delete a wrapper that adds no such step. |
| `POL-LEAF-033`, `POL-LEAF-059` | [Leaf property categories][leaf property categories]. |
| `POL-LEAF-040` | Preserve the established input object and its strongest category; no ancestor normalization, exact-category branch, or repeated membership after transport. |
| `POL-LEAF-041`, `POL-LEAF-042`, `POL-LEAF-043` | One executable category-owned implementation class owns each exact mathematical type and its ordinary public method bodies. No competing realization class, routing marker, decorator, or backend method map replaces it. [Computation boundary][computation boundary]. |
| `POL-LEAF-045` | A category-owned method that invokes a dependency and reconstructs the semantic result is an implementation. Repeated private access alone does not justify dispatch or a parallel hierarchy. |
| `POL-LEAF-046`, `POL-LEAF-050` | [Private helpers and files][private helpers and files]. Substantial shared engine integration can use a private neighbor; it supplies no category classes, public catalogue, registry, compiler binding, or mirror implementation. |
| `POL-LEAF-047` | Each local initializer takes one exact datum for its new state. Functor actions use public target constructors; [Direct inherited execution][direct inherited execution] threads each owner once, including the parent at `Cat().ElementType`. |
| `POL-LEAF-051`, `POL-LEAF-053`, `POL-LEAF-054`, `POL-LEAF-055` | An ordinary exact typed method on its owning class is complete. No kernel import, decorator, annotation payload, signature mirror, or compiler state belongs in a leaf declaration. [Exact leaf types][exact leaf types]. |
| `POL-LEAF-057` | Construct named objects in their definitionally known property categories; do not enumerate or query an engine to rediscover defining facts. [Leaf property categories][leaf property categories] owns generated property applications. |
| `POL-LEAF-062` | Keep a helper local or private when only leaf-internal code or a functor action consumes it. Genuinely public mathematical data retains its public name. [Functor actions][functor actions]. |
| `POL-LEAF-063` | [Manual inherited initialization][manual inherited initialization]. |
| `POL-LEAF-064` | [Hand-built subcategories][hand-built subcategories]. |
| `POL-LEAF-065` | [Inherited identity, composition, construction, and retention][inherited identity, composition, construction, and retention]. |
| `POL-LEAF-066` | [Kernel machinery in a leaf][kernel machinery in a leaf]. |
| `POL-LEAF-067` | [Sage runtime in a theory declaration][sage runtime in a theory declaration]. |
| `POL-LEAF-068` | [Hand-written property applications][hand-written property applications]. |
| `POL-LEAF-069` | [Datum-free constructors and point categories][datum-free constructors and point categories]. |
| `POL-LEAF-070` | [Actions written for a functor that computes nothing][actions written for a functor that computes nothing]. |
| `POL-LEAF-071` | [Rewritten retained projections][rewritten retained projections]. |
| `POL-LEAF-072` | [Placeholder datum][placeholder datum]. |
| `POL-LEAF-073` | [Union or optional parameter][union or optional parameter]. |
| `POL-LEAF-074` | [Properties on datum records][properties on datum records]. |
| `POL-LEAF-075` | [Generic parameters on a leaf declaration][generic parameters on a leaf declaration]. |
| `POL-LEAF-076` | [Import-order wiring][import-order wiring]. |
| `POL-LEAF-077` | [Declaration lookup by name string][declaration lookup by name string]. |
| `POL-LEAF-078` | [Accessors replacing functors][accessors replacing functors]. |
| `POL-LEAF-079` | [Two spellings of one fact][two spellings of one fact]. |
| `POL-LEAF-080` | [Implementing a named category][implementing a named category]. |
| `POL-LEAF-081` | [Inverse-image properties][inverse-image properties]. |

## Private kernel

| Policy identifiers | Contract |
| --- | --- |
| `POL-KERNEL-001`, `POL-KERNEL-010`, `POL-KERNEL-017`, `POL-KERNEL-028` | [Sage class construction][sage class construction]. |
| `POL-KERNEL-002`, `POL-KERNEL-012`, `POL-KERNEL-013`, `POL-KERNEL-014` | [Same-object refinement][same-object refinement] and [Runtime properties and constructions][runtime properties and constructions] define one typed operation preserving identity, data, and realizations across objects, elements, and morphisms. |
| `POL-KERNEL-003` | [Functor actions][functor actions]. |
| `POL-KERNEL-004` | [Inherited constructions][inherited constructions]. |
| `POL-KERNEL-005`, `POL-KERNEL-006` | Add kernel complexity only when a mathematical declaration removes the same infrastructure from applicable leaves. Keep category-specific branches outside it. |
| `POL-KERNEL-007`, `POL-KERNEL-008`, `POL-KERNEL-009` | Private runtime mechanics can inspect implementation classes through Python reflection and collection protocols. Inspection realizes typed declarations; it never establishes membership, properties, method ownership, or functor structure. |
| `POL-KERNEL-011` | Kernel permissions do not permit erased types, casts, ignored diagnostics, fallbacks, or fabricated mathematical evidence. `POL-TYPE-004` fixes the two input aliases. |
| `POL-KERNEL-015`, `POL-KERNEL-016` | A kernel catch adds precise context, translates an exception with its cause, or performs required cleanup, then terminates by raising. It never retries, substitutes, suppresses, or continues. |
| `POL-KERNEL-018`, `POL-KERNEL-029` | [Direct inherited execution][direct inherited execution]. |
| `POL-KERNEL-019` | A constructor requiring an object of `C` accepts every `X in C`; resolve its owned implementation privately in the kernel. |
| `POL-KERNEL-020` | Give Sage the local executable method provider. Never replace a locally owned method with engine dispatch or interpret metadata as its computation route. |
| `POL-KERNEL-021`, `POL-KERNEL-022`, `POL-KERNEL-023`, `POL-KERNEL-024` | [Declarations and signatures][declarations and signatures] derives exact receiver, parameter, result, and call-shape information from ordinary declarations. Reject an inexact required type; add no leaf signature DSL, marker, mirror, or type relabeling. |
| `POL-KERNEL-025` | Compile every placement-forced operation, including inverse and universal maps, from its owner. Missing descendant operations require repair there or in compilation, never leaf wiring. |
| `POL-KERNEL-026` | Compile inverse-image properties from their retained pullback and functors, including classes, constructors, containment, refinement, and predicates. [Runtime properties and constructions][runtime properties and constructions]. |
| `POL-KERNEL-027` | [Functor construction][functor construction] and [Restrictions and base change][restrictions and base change] own functors and their induced actions. The kernel never selects a functor by interpreting leaf data. |
| `POL-KERNEL-030`, `POL-KERNEL-032` | [Runtime categories and caches][runtime categories and caches]. |
| `POL-KERNEL-031` | [Diamond diagnostics][diamond diagnostics]. |
| `POL-KERNEL-033`, `POL-KERNEL-034`, `POL-KERNEL-035` | [Runtime properties and constructions][runtime properties and constructions]. |
| `POL-KERNEL-036` | [Declarations and signatures][declarations and signatures]. |
| `POL-KERNEL-037` | [Repeated failures][repeated failures]. |
| `POL-KERNEL-038` | [Closed kernel surface][closed kernel surface]. |

## Mathematical layout

| Policy identifiers | Contract |
| --- | --- |
| `POL-LAYOUT-001` | [Leaf contract][leaf contract]. |
| `POL-LAYOUT-002` | Lattice cardinality is inherited through named functors to modules and sets; it has no lattice-local owner. |
| `POL-LAYOUT-003`, `POL-LAYOUT-004`, `POL-LAYOUT-006`, `POL-LAYOUT-007`, `POL-LAYOUT-016`, `POL-LAYOUT-017`, `POL-LAYOUT-018` | Separate mathematical owners and private engineering in the filesystem. Split substantial units by their exact category, property, or construction, not size or technique. Each mathematics audit must be local; runtime review establishes no new mathematics. |
| `POL-LAYOUT-005` | Mirror source ownership in tests; keep kernel tests in their own subtree. |
| `POL-LAYOUT-008`, `POL-LAYOUT-010`, `POL-LAYOUT-011`, `POL-LAYOUT-014`, `POL-LAYOUT-015` | [Computation boundary][computation boundary]. |
| `POL-LAYOUT-009` | Use private backend subtrees for category-independent adapters; a substantial category-specific helper can neighbor its owner. |
| `POL-LAYOUT-012` | [Implementation and dependencies][implementation and dependencies]. |
| `POL-LAYOUT-013`, `POL-LAYOUT-021` | [Layer dependencies][layer dependencies]. |
| `POL-LAYOUT-019`, `POL-LAYOUT-020` | [Private helpers and files][private helpers and files]. |

## Functors and universal constructions

| Policy identifiers | Contract |
| --- | --- |
| `POL-FUN-001`, `POL-FUN-002`, `POL-FUN-007`, `POL-FUN-017`, `POL-FUN-035` | [Functor actions][functor actions]. |
| `POL-FUN-003`, `POL-FUN-004`, `POL-FUN-006`, `POL-FUN-033` | [Structure functors and inheritance][structure functors and inheritance]. |
| `POL-FUN-005` | Model projections, scalar change, and mathematical realizations as explicit functors. Private engine values and calls need no such functor. |
| `POL-FUN-008`, `POL-FUN-009`, `POL-FUN-010`, `POL-FUN-011`, `POL-FUN-012`, `POL-FUN-016`, `POL-FUN-019`, `POL-FUN-020`, `POL-FUN-021`, `POL-FUN-022`, `POL-FUN-039` | [Diagrams and universal constructions][diagrams and universal constructions]. |
| `POL-FUN-013`, `POL-FUN-014` | [Fixed-object constructions][fixed-object constructions]. |
| `POL-FUN-015`, `POL-FUN-018` | [Functor images][functor images]. |
| `POL-FUN-023` | Preserve functor identities and composition, including `F(f.inverse()) == F(f).inverse()`. Descendants inherit this action. |
| `POL-FUN-024`, `POL-FUN-025` | [Functor properties][functor properties]. |
| `POL-FUN-026`, `POL-FUN-034` | [Functor property resolution][functor property resolution]. |
| `POL-FUN-027` | [Functor construction][functor construction]. |
| `POL-FUN-028` | [Construction-named functors][construction-named functors] and [Leaf structure functors][leaf structure functors] fix the faithful poset-to-underlying-set isofibration and its componentwise-order lifting data. |
| `POL-FUN-029`, `POL-FUN-030`, `POL-FUN-037` | [Construction-named functors][construction-named functors]. |
| `POL-FUN-031` | [Comma categories and fibers][comma categories and fibers]. |
| `POL-FUN-032` | [Induced functors][induced functors]. |
| `POL-FUN-036` | [Placement and inheritance conditions][placement and inheritance conditions]. |
| `POL-FUN-038`, `POL-FUN-040` | [Adjunctions and equivalences][adjunctions and equivalences]. |
| `POL-FUN-041` | [Comma categories and fibers][comma categories and fibers] and [Restrictions and base change][restrictions and base change] retain the fiber and pulled-back cartesian lifts. |
| `POL-FUN-042` | [Indexed categories and representations][indexed categories and representations]. |

## Sets and cardinals

| Policy identifiers | Contract |
| --- | --- |
| `POL-SET-001`, `POL-SET-009`, `POL-SET-015`, `POL-SET-023`, `POL-SET-024` | [Sets-owned operations][sets-owned operations]. |
| `POL-SET-002`, `POL-SET-003`, `POL-SET-004`, `POL-SET-012`, `POL-SET-017`, `POL-SET-019`, `POL-SET-036` | [Set maps and exponentials][set maps and exponentials]. |
| `POL-SET-005`, `POL-SET-006` | [Category containment][category containment]. |
| `POL-SET-007` | [Set subobjects and power objects][set subobjects and power objects]. |
| `POL-SET-008` | Support infinite predicate subobjects, including the even and prime integers. [Set subobjects and power objects][set subobjects and power objects]. |
| `POL-SET-010`, `POL-SET-020`, `POL-SET-021`, `POL-SET-022`, `POL-SET-031` | [Set cardinality query][set cardinality query]. |
| `POL-SET-011`, `POL-SET-027` | Use cardinality for mathematical sets and length only for finite sequences whose order matters. |
| `POL-SET-013`, `POL-SET-014` | [Diagrams and universal constructions][diagrams and universal constructions] and [Set limits and colimits][set limits and colimits] admit arbitrary small diagrams. |
| `POL-SET-016` | Derive structural facts from defining data, predicates, functors, injections, bijections, and universal constructions before enumeration. |
| `POL-SET-018` | Use one parent and implementation for `P(X)`, `2^X`, and `2 ** X`, where `2` is the two-element set. [Set subobjects and power objects][set subobjects and power objects]. |
| `POL-SET-025` | [Cardinal model][cardinal model]. |
| `POL-SET-026` | Cardinal arithmetic returns exact cardinals. Equality and order form propositions, whose decision can be `Unknown`. [Cardinal model][cardinal model]. |
| `POL-SET-028` | When rank or number of generators counts a mathematical set, return its cardinality, not sequence length. |
| `POL-SET-029`, `POL-SET-030` | Before enumeration, determine the infinite and large-finite cases. Compute cardinality by enumeration only when a concrete value is required, finiteness established, and structural formulas unavailable. |
| `POL-SET-032` | `NN` denotes positive integers; use `ZZ_{>=0}` for nonnegative integers. |
| `POL-SET-033`, `POL-SET-034` | Compare and calculate with a cardinal directly using standard syntax, including comparisons with integers. No coercion, stored-value accessor, or named comparison alias is required. |
| `POL-SET-035` | [Finite cardinal remainder][finite cardinal remainder]. |
| `POL-SET-037` | [Ordinal arithmetic][ordinal arithmetic] and [Hessenberg arithmetic][hessenberg arithmetic]. `**` remains the categorical exponential. |
| `POL-SET-038` | [Cardinal and ordinal orders][cardinal and ordinal orders]. |

## Sage boundary

| Policy identifiers | Contract |
| --- | --- |
| `POL-SAGE-001` | [Layer ownership][layer ownership]. |
| `POL-SAGE-002`, `POL-SAGE-008`, `POL-SAGE-009` | [Fixed private dependencies][fixed private dependencies]. |
| `POL-SAGE-003`, `POL-SAGE-004`, `POL-SAGE-005`, `POL-SAGE-006` | Use Sage only through a modeled realization functor or private computation boundary. Sage categories never become mathematical supercategories of owned categories; do not modify them or export their method catalogue. |
| `POL-SAGE-007` | Each mathematical operation has one owned public spelling. |
| `POL-SAGE-010` | [Implementation and dependencies][implementation and dependencies]. |
| `POL-SAGE-011` | Use Sage exact linear algebra behind the private tensor realization boundary. |
| `POL-SAGE-012` | [Verification][verification]. |
| `POL-SAGE-013` | [Runtime categories and caches][runtime categories and caches]. |
| `POL-SAGE-014` | Define each comparison operator from its own mathematical definition. Reflected-operator recursion is unsafe across same-object refined subclasses. |
| `POL-SAGE-015` | A module binds the names its source declares. No cross-module namespace assignment or provisional binding later overwritten. |
| `POL-SAGE-016` | [Layer dependencies][layer dependencies]. Add a new Sage engine module deliberately to the `pyproject.toml` import contract. |

## Public API

| Policy identifiers | Contract |
| --- | --- |
| `POL-API-001` | Derive API shape from mathematics, not storage fields or current Python classes. |
| `POL-API-002` | Through version 1, each operation has one owner and public spelling. Standard operators invoke that implementation. Convenience aliases start after version 1. |
| `POL-API-003`, `POL-API-007` | Use standard public mathematical and Sage syntax, including Python operators and protocols. |
| `POL-API-004` | Use `as_*` only for conversion to another mathematical representation. |
| `POL-API-005`, `POL-API-006` | Private fields stay with their owner or documented subclass contract; use another object's public mathematical interface. |
| `POL-API-008`, `POL-API-013` | Name each accessor and morphism for the exact mathematical entity it denotes. |
| `POL-API-009`, `POL-API-010` | [Cat and its implementation][cat and its implementation]. |
| `POL-API-011`, `POL-API-012`, `POL-API-024` | [Semantic collisions][semantic collisions]. |
| `POL-API-014` | Names must state their mathematical content; avoid `data`, `container`, `rule`, `value`, `values`, and equivalent nonspecific identifiers. |
| `POL-API-015` | Use standard comparison, equality, containment, indexing, iteration, and call syntax without forwarding aliases. [Owned equality and hashing][owned equality and hashing] and [Category containment][category containment] fix proposition and Boolean boundaries. |
| `POL-API-016` | A standalone public function is permitted only when the operation has no natural mathematical owner. |
| `POL-API-017`, `POL-API-018`, `POL-API-019` | Expose an operation only on the category that supplies it. Abstract methods prevent incomplete concrete construction; a method that only fails advertises no capability. |
| `POL-API-020` | Every partial value operation forms a [typed query][typed queries] with one exact result category; a truth question forms a proposition. `Unknown` is never inside an owned result. |
| `POL-API-021` | Methods and constructors are total on their declared domains. Require all arguments; no optional parameters, defaults, `None` sentinels, or fallback behavior. Give distinct presentations and computations explicit names, not distinct evidence-source routes. |
| `POL-API-022` | [Same-object refinement][same-object refinement]. |
| `POL-API-023` | Obtain a uniquely determined value from its owner. In particular, an isomorphism supplies its inverse. |
| `POL-API-025` | [Owned implementation types][owned implementation types]. |
| `POL-API-026` | Use `Self` only when returning the same value; otherwise annotate the exact owned result type. |
| `POL-API-027` | Through version 1, add no operation expressible in one or two lines of public composition. Expose defining data at its owner; axiom-generated `is_P()` is the existing property contract. |
| `POL-API-028` | Construct through the exact category, hom category, functor category, or property/construction subcategory. Named constructors stay on that owner; no parallel factory namespace. [Cat and its implementation][cat and its implementation]. |

## Exact types

| Policy identifiers | Contract |
| --- | --- |
| `POL-TYPE-001` | Give every value the type that names its exact mathematical type. |
| `POL-TYPE-002` | Distinguish categories, objects, elements, morphisms, functors, rings, sets, domains, and codomains in types. |
| `POL-TYPE-003` | Never use `object` in a type annotation. There are no exceptions. |
| `POL-TYPE-004` | Use `EqualityInput` for the candidate of `__eq__` and `__ne__`, and `ContainmentInput` for `__contains__`. These are the two aliases of `Any`, each declared once; the equality and containment input boundaries are its only permitted uses (D131, D180). |
| `POL-TYPE-005` | Never use `Any` as a return type. |
| `POL-TYPE-006` | Do not silence a type error with a cast, ignored diagnostic, deleted annotation, or wider type. |
| `POL-TYPE-007` | Fix the mathematical model, method owner, import boundary, or missing type declaration exposed by a type error. |
| `POL-TYPE-008` | Use category membership as type information. Do not inspect fields or method names for capabilities. |
| `POL-TYPE-009` | Do not invent wrapper types whose only purpose is to satisfy the type checker. |
| `POL-TYPE-010` | Return `Self`, `None`, or the exact mathematical result type. Use the element type of `NN`, `ZZ`, or `RR` for natural numbers, integers, or real numbers. |
| `POL-TYPE-011` | Use a set, ordered set, multiset, indexed family, or another named mathematical collection in every theory-layer mathematical signature. The compiler-owned `structure_functors()` declaration returns the complete tuple required by `POL-CAT-085`. Never use `Iterable`, `Sequence`, `Collection`, `list`, or `tuple` for a mathematical collection. Use `float` only at an explicit numerical boundary. |
| `POL-TYPE-012` | Primitive signatures can occur inside a private method only when every consumer remains inside that private boundary. |
| `POL-TYPE-013` | Create a type for a genuine mathematical object. Do not wrap invalid constructor inputs in an engineering type to satisfy the checker. |
| `POL-TYPE-014` | Use the input aliases specified by `POL-TYPE-004`; neither `object` nor a structural wrapper replaces them. |
| `POL-TYPE-015` | Never create a type such as `MembershipInput` that models the candidate accepted by equality or containment; the two aliases name the position, not a model of the input (D131). |
| `POL-TYPE-016` | Use types to express the mathematics. Keep parsing, coercion, normalization, and representation conversion behind the typed mathematical boundary. |
| `POL-TYPE-017` | Type every morphism by the element types of its domain and codomain categories. Do not widen either endpoint to a generic mathematical-object type. |
| `POL-TYPE-018` | Give every category its own semantic object, element, and morphism types through `ObjectType`, `ElementType`, and `MorphismType`. Use those types throughout that category's API. |
| `POL-TYPE-019` | Type each method parameter and result by the most specific category that supplies the required structure. Do not widen it to an element or object type from a supercategory. |
| `POL-TYPE-020` | Preserve category-specific implementation classes even when a category adds no new runtime fields or methods. Same-object property refinement updates the Sage dynamic class to include the refined class. It does not erase the refinement or allocate a second semantic value. |
| `POL-TYPE-021` | Admit raw Python container types only inside the implementation kernel, a backend adapter, or a dedicated interoperation module. Convert them immediately into the required mathematical collection before theory code receives them. A theory constructor or helper is not such a boundary. |
| `POL-TYPE-022` | Use `Iterator[T]` only for the Python traversal protocol or a private lazy-enumeration result. It never replaces a named mathematical collection in a theory-layer input or result. |
| `POL-TYPE-023` | Treat type-checker and import output as diagnostic signals. An error can falsify the current implementation, but it cannot establish a new architecture or mathematical owner. The mathematical definitions, category ownership, and functor declarations determine correctness. |
| `POL-TYPE-024`, `POL-TYPE-028` | [Static semantic projection][static semantic projection]. |
| `POL-TYPE-025`, `POL-TYPE-026` | [Static semantic projection][static semantic projection] is the sole output-only typing projection. One kernel generator derives stubs from the same ownership computation as compilation; applicable commit, test, push, and release workflows regenerate changed declarations. |
| `POL-TYPE-027` | Use exact category-owned nominal types and membership, never `typing.Protocol` or another structural duck type. [Static semantic projection][static semantic projection]. |
| `POL-TYPE-029` | A broad union of unrelated exact types erases semantics; never use it with callables or variadics instead of an exact signature. |

## Implementation style

| Policy identifiers | Contract |
| --- | --- |
| `POL-CODE-001`, `POL-CODE-002`, `POL-CODE-003` | Order method bodies by the mathematical definition. Keep defining steps direct and readable without non-mathematical helper chains. |
| `POL-CODE-004`, `POL-CODE-005`, `POL-CODE-006`, `POL-CODE-007`, `POL-CODE-029`, `POL-CODE-030` | [Implementation and dependencies][implementation and dependencies]. |
| `POL-CODE-008`, `POL-CODE-009` | Keep one current implementation; no compatibility layers, fallbacks, migrations, or obsolete aliases. |
| `POL-CODE-010`, `POL-CODE-025`, `POL-CODE-026`, `POL-CODE-042`, `POL-CODE-043` | [Repeated failures][repeated failures]. |
| `POL-CODE-011` | Fail loudly when required mathematical structure or a dependency is absent. |
| `POL-CODE-012`, `POL-CODE-013`, `POL-CODE-020`, `POL-CODE-027` | Read and call declared mathematical interfaces directly. Never infer capabilities from storage or reflection, or assemble a mathematical API with `setattr`. |
| `POL-CODE-014`, `POL-CODE-015`, `POL-CODE-016` | Keep coordinates, matrices, elements, and morphisms distinct. Lower once at the private computation boundary and reconstruct once. |
| `POL-CODE-017`, `POL-CODE-018` | Use exact arithmetic until an explicit numerical boundary; keep precision parameters there. |
| `POL-CODE-019` | Remove unnecessary computation, enumeration, and verification while preserving the visible mathematics. |
| `POL-CODE-021`, `POL-CODE-022`, `POL-CODE-023`, `POL-CODE-024` | Assert mathematical preconditions, required capabilities, and type narrowing through owned propositions or membership. Assertions remain true across representation changes; no recovery branch replaces a violated precondition. |
| `POL-CODE-028` | Prefer a named mathematical primitive over generic composition that conceals it. Use `itertools.pairwise` for adjacency and `zip` to pair separate indexed families. |
| `POL-CODE-031` | Use `sum` and `prod` for established finite aggregations; use indexed categorical constructions for potentially infinite families. |
| `POL-CODE-032`, `POL-CODE-033`, `POL-CODE-036` | Use direct functional expressions, immutable transformations, named combinators, and local equations inside owned methods when they express the mathematics clearly. |
| `POL-CODE-034` | Use exhaustive `match`/`case` for a mathematical decomposition instead of a structural conditional cascade. |
| `POL-CODE-035` | Return early for decisive cases, then assert the stronger remaining hypotheses. |
| `POL-CODE-037` | A conversion that changes neither type nor semantics requires a local comment establishing why the conversion is necessary. |
| `POL-CODE-038` | A forwarding-only method is inadmissible. Semantic lowering, an algorithm call, or owned-result reconstruction is an implementation step. |
| `POL-CODE-039`, `POL-CODE-040`, `POL-CODE-041` | Exceptions propagate outside the kernel. Never use them for routing, capability discovery, optional inputs, retries, continuation, or substitute results. Kernel catches obey `POL-KERNEL-015` and `POL-KERNEL-016`. |

## Verification

| Policy identifiers | Contract |
| --- | --- |
| `POL-TEST-001`, `POL-TEST-002`, `POL-TEST-003`, `POL-TEST-004`, `POL-TEST-005`, `POL-TEST-006`, `POL-TEST-007`, `POL-TEST-008`, `POL-TEST-009`, `POL-TEST-010`, `POL-TEST-011`, `POL-TEST-012`, `POL-TEST-013`, `POL-TEST-014`, `POL-TEST-015`, `POL-TEST-016`, `POL-TEST-017`, `POL-TEST-018`, `POL-TEST-019`, `POL-TEST-020`, `POL-TEST-021`, `POL-TEST-022`, `POL-TEST-023`, `POL-TEST-024`, `POL-TEST-025`, `POL-TEST-026`, `POL-TEST-027`, `POL-TEST-028`, `POL-TEST-029`, `POL-TEST-030`, `POL-TEST-031` | [Verification][verification]. |

## Performance

| Policy identifiers | Contract |
| --- | --- |
| `POL-PERF-001`, `POL-PERF-002`, `POL-PERF-003`, `POL-PERF-004`, `POL-PERF-005` | [Verification][verification]. |

## Documentation

| Policy identifiers | Contract |
| --- | --- |
| `POL-DOC-001`, `POL-DOC-002`, `POL-DOC-003`, `POL-DOC-004`, `POL-DOC-005`, `POL-DOC-006`, `POL-DOC-007`, `POL-DOC-008`, `POL-DOC-009`, `POL-DOC-010`, `POL-DOC-011`, `POL-DOC-014`, `POL-DOC-015`, `POL-DOC-016`, `POL-DOC-017`, `POL-DOC-018`, `POL-DOC-019`, `POL-DOC-023` | [Documentation changes][documentation changes]. |
| `POL-DOC-012` | [Sources of truth][sources of truth]. |
| `POL-DOC-025`, `POL-DOC-026`, `POL-DOC-027` | [Documentation changes][documentation changes]. |
| `POL-DOC-013`, `POL-DOC-024` | [Session continuity][session continuity]. |
| `POL-DOC-020` | [Starting a work unit][starting a work unit]. |
| `POL-DOC-021` | [Implementation and dependencies][implementation and dependencies]. |
| `POL-DOC-022` | [Repeated failures][repeated failures]. |
| `POL-DOC-028` | [Review and acceptance][review and acceptance]. |
| `POL-DOC-029` | [Verification][verification]. |

## Policy identifiers

| Policy identifiers | Contract |
| --- | --- |
| `POL-INDEX-001`, `POL-INDEX-002`, `POL-INDEX-003`, `POL-INDEX-004` | Each policy keeps one stable unique identifier. Add one only for a new rule, not an example or restatement. Never reassign a retired identifier. |

[properties on datum records]: specs/leaves.md#pol-leaf-074--a-property-on-a-datum-record
[rewritten retained projections]: specs/leaves.md#pol-leaf-071--a-retained-projection-rewritten
[actions written for a functor that computes nothing]: specs/leaves.md#pol-leaf-070--actions-written-for-a-functor-that-computes-nothing
[adjunctions and equivalences]: specs/functor.md#adjunctions-and-equivalences
[algebra objects]: specs/algebras.md#ambient-categorical-data
[algebra structure functor]: specs/algebras.md#structure-functor
[algebraic laws]: specs/magmas-monoids-semirings.md#laws-in-the-supplied-ambient
[accessors replacing functors]: specs/leaves.md#pol-leaf-078--an-accessor-standing-in-for-a-functor
[assumptions]: specs/undecidable-properties.md#assumptions
[manual inherited initialization]: specs/leaves.md#pol-leaf-063--base-initializer-or-inherited-state-installed-by-hand
[cardinal and ordinal orders]: specs/cardinality.md#cardinal-and-ordinal-order-categories
[cardinal model]: specs/cardinality.md#cardinal-model
[cat and its implementation]: specs/functor.md#cat-and-its-implementation
[category containment]: specs/undecidable-properties.md#category-containment
[closed kernel surface]: specs/resolution.md#the-closed-kernel-surface
[comma categories and fibers]: specs/functor.md#comma-categories-slices-coslices-and-fibers
[component functors]: specs/functor.md#products-coproducts-and-component-functors
[computation boundary]: specs/leaves.md#computation-engine-boundary
[construction-named functors]: specs/functor.md#construction-named-functors
[constructors]: specs/leaves.md#constructors
[datum-free constructors and point categories]: specs/leaves.md#pol-leaf-069--datum-free-constructor-or-a-one-object-category-built-by-hand
[declaration lookup by name string]: specs/leaves.md#pol-leaf-077--declaration-lookup-by-name-string
[declarations and signatures]: specs/resolution.md#declarations-and-signatures
[defining predicate]: specs/property-refinement.md#defining-predicate
[diagrams and universal constructions]: specs/functor.md#diagram-shapes-and-universal-constructions
[diamond diagnostics]: specs/resolution.md#diamond-diagnostics-and-future-coherence
[direct inherited execution]: specs/resolution.md#direct-inherited-execution
[documentation changes]: AGENTS.md#documentation-changes
[equality]: specs/undecidable-properties.md#equality
[evaluation]: specs/undecidable-properties.md#evaluation
[exact leaf types]: specs/leaves.md#exact-types
[finite cardinal remainder]: specs/cardinality.md#remainder-for-finite-cardinals
[fixed private dependencies]: specs/resolution.md#fixed-private-dependencies
[fixed-object constructions]: specs/functor.md#fixed-object-construction-categories
[functor actions]: specs/functor.md#functors-as-morphisms-of-cat
[functor construction]: specs/functor.md#functor-construction-and-presentation-data
[functor images]: specs/functor.md#strict-full-and-essential-images
[functor properties]: specs/functor.md#functor-property-subcategories
[functor property resolution]: specs/functor.md#property-resolution
[functor-category calculus]: specs/functor.md#functor-category-calculus
[generic parameters on a leaf declaration]: specs/leaves.md#pol-leaf-075--generic-parameters-on-a-leaf-declaration
[hand-written property applications]: specs/leaves.md#pol-leaf-068--hand-written-property-application-or-accessor
[hessenberg arithmetic]: specs/ordinals.md#hessenberg-natural-arithmetic
[inherited identity, composition, construction, and retention]: specs/leaves.md#pol-leaf-065--identity-composition-morphism-or-element-construction-or-element-retention-for-inherited-structure
[implementation and dependencies]: AGENTS.md#implementation-and-dependencies
[implementing a named category]: specs/functor.md#implementing-a-named-category
[import-order wiring]: specs/leaves.md#pol-leaf-076--import-order-wiring
[indexed categories and representations]: specs/functor.md#indexed-categories-yoneda-and-representability
[induced functors]: specs/functor.md#induced-functors
[inherited constructions]: specs/leaves.md#inherited-constructions
[inherited operations]: specs/leaves.md#pol-leaf-065--identity-composition-morphism-or-element-construction-or-element-retention-for-inherited-structure
[internal algebraic families]: specs/magmas-monoids-semirings.md#ambient-categorical-data
[internal rings]: specs/rings.md#ambient-categorical-data
[internal semirings]: specs/magmas-monoids-semirings.md#semirings
[inverse-image properties]: specs/property-refinement.md#inverse-images
[inverse-image subcategories]: specs/functor.md#inverse-image-subcategories
[kernel machinery in a leaf]: specs/leaves.md#pol-leaf-066--kernel-machinery-in-a-leaf-branching-refinement-after-construction-own-value-store-kernel-state-in-a-constructor
[layer dependencies]: specs/system.md#dependency-directions
[layer ownership]: specs/system.md#system-shape
[leaf contract]: specs/leaves.md#leaf-contract
[leaf property categories]: specs/leaves.md#property-categories
[leaf structure functors]: specs/leaves.md#structure-functors
[mathematical questions]: specs/undecidable-properties.md#mathematical-questions
[module action laws]: specs/modules.md#objects-and-action-laws
[module objects]: specs/modules.md#ambient-categorical-data
[morphism tower]: specs/functor.md#the-morn-c-tower
[opposites and dualization]: specs/functor.md#opposites-and-dualization
[ordinal arithmetic]: specs/ordinals.md#ordinary-ordinal-arithmetic
[owned equality and hashing]: specs/sets.md#equality
[owned implementation types]: specs/functor.md#cobjecttype-celementtype-and-cmorphismtype
[placeholder datum]: specs/leaves.md#pol-leaf-072--placeholder-datum
[placement and inheritance conditions]: specs/functor.md#monomorphisms-of-cat-and-placement
[points and generalized elements]: specs/functor.md#point-categories-and-point-functors
[private helpers and files]: specs/leaves.md#private-helpers-and-files
[property category]: specs/property-refinement.md#property-category
[hand-built subcategories]: specs/leaves.md#pol-leaf-064--property-or-construction-subcategory-built-by-hand
[proposition handlers]: specs/undecidable-properties.md#proposition-handlers
[public propositions]: specs/undecidable-properties.md#public-propositions
[repeated failures]: AGENTS.md#repeated-failures
[restrictions and base change]: specs/functor.md#restrictions-and-change-of-base
[review and acceptance]: AGENTS.md#review-and-acceptance
[runtime categories and caches]: specs/resolution.md#runtime-categories-and-caches
[runtime properties and constructions]: specs/resolution.md#properties-and-constructions
[sage class construction]: specs/resolution.md#sage-class-construction
[sage runtime in a theory declaration]: specs/leaves.md#pol-leaf-067--sage-machinery-as-the-categorys-runtime
[same-object refinement]: specs/property-refinement.md#same-object-refinement
[semantic collisions]: specs/resolution.md#semantic-collisions
[session continuity]: AGENTS.md#session-continuity
[set cardinality query]: specs/sets.md#cardinality-query
[set limits and colimits]: specs/sets.md#general-limits-and-colimits
[set maps and exponentials]: specs/sets.md#set-maps-morphism-categories-and-function-sets
[set subobjects and power objects]: specs/sets.md#subobjects-images-and-power-objects
[sets-owned operations]: specs/sets.md#sets-owned-operations
[sources of truth]: AGENTS.md#sources-of-truth
[starting a work unit]: AGENTS.md#starting-a-work-unit
[static semantic projection]: specs/functor.md#static-semantic-projection
[structure functors and inheritance]: specs/functor.md#structure-functors-and-inherited-classes
[subcategory declarations]: specs/functor.md#declaring-one
[two spellings of one fact]: specs/leaves.md#pol-leaf-079--two-spellings-of-one-fact
[typed queries]: specs/undecidable-properties.md#typed-queries
[union or optional parameter]: specs/leaves.md#pol-leaf-073--union-or-optional-parameter
[verification]: AGENTS.md#verification
[leaf design templates]: specs/leaf-category-template.md
