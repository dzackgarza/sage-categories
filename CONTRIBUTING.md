# Contributing

This repository implements a categorical foundation for Sage-based mathematics.
Mathematical structure controls the code architecture.

Each coding policy has a permanent identifier of the form `POL-AREA-NNN`. Use these identifiers in code review and design discussion.
Do not reuse a retired identifier.

## Current implementation boundary

| ID | Policy |
| --- | --- |
| `POL-SCOPE-001` | Build the foundation in dependency order: `Cat`, arrow categories, method inheritance, then `Sets()`. |
| `POL-SCOPE-002` | Keep current feature work within the foundation through `Sets()` until that foundation meets its acceptance criteria. |
| `POL-SCOPE-003` | Implement the complete arrow-category family, including hom, endomorphism, monomorphism, epimorphism, isomorphism, automorphism, slice, coslice, subobject, and superobject categories. |
| `POL-SCOPE-004` | Make object, element, and arrow inheritance work before adding theories that depend on it. |
| `POL-SCOPE-005` | Treat the full owned `Sets()` category as foundational work, not as a finite-set helper library. |

## Mathematical model

| ID | Policy |
| --- | --- |
| `POL-MATH-001` | Identify the mathematical objects, elements, arrows, categories, functors, and universal properties before choosing Python representations. |
| `POL-MATH-002` | Model a named category as a category, not as a class with similarly named methods. |
| `POL-MATH-003` | Model a named functor with an object map and an arrow map. |
| `POL-MATH-004` | Model a natural transformation by its components and naturality data. |
| `POL-MATH-005` | Keep a mathematical object distinct from a presentation, coordinate tuple, matrix, or computation-engine value. |
| `POL-MATH-006` | Keep an element distinct from its image under a morphism. |
| `POL-MATH-007` | Store chosen mathematical structure as mathematical data, usually an object or arrow in an owned category. |
| `POL-MATH-008` | Do not duplicate data that a defining arrow already determines. |
| `POL-MATH-009` | Put each operation at the weakest categorical level whose hypotheses imply it. |
| `POL-MATH-010` | Implement the general mathematical notion and obtain special cases by restriction or specialization. |
| `POL-MATH-011` | Use established mathematical terminology. Name each operation by the structure that owns it. |
| `POL-MATH-012` | Treat a missing general construction as a foundational gap. Do not patch only one existing example. |
| `POL-MATH-013` | Keep axiomatic truths distinct from runtime algorithms. |
| `POL-MATH-014` | Cite a standard theorem or reference implementation instead of reproducing its proof as runtime validation. |

## Category ownership and inheritance

| ID | Policy |
| --- | --- |
| `POL-CAT-001` | A category owns its constructors, local operations, and implementation types. |
| `POL-CAT-002` | Use `ObjectType`, `ElementType`, and `ArrowType` for category-owned implementations. |
| `POL-CAT-003` | Apply the same inheritance mechanism to objects, elements, and arrows. |
| `POL-CAT-004` | A category level defines only the structure and operations introduced at that level. |
| `POL-CAT-005` | A leaf category knows only itself and its immediate structural functors. |
| `POL-CAT-006` | Do not copy or forward methods already owned by another category. |
| `POL-CAT-007` | Do not build a second Python class graph to duplicate the category graph. |
| `POL-CAT-008` | Compile category declarations into the public method surface. Do not generate opaque method bodies. |
| `POL-CAT-009` | Give a local declaration precedence over inherited declarations. |
| `POL-CAT-010` | Deduplicate routes that reach the same declaring category and implementation. |
| `POL-CAT-011` | Reject unrelated method-name collisions during method compilation. |
| `POL-CAT-012` | Reject incoherent structural routes that construct different implementations in the same category. |
| `POL-CAT-013` | Maintain one canonical implementation in each category reached from a public object. |
| `POL-CAT-014` | Expose inherited operations directly on the public mathematical object. |
| `POL-CAT-015` | Keep functor images inspectable when their mathematical role matters. |
| `POL-CAT-016` | Derive supercategory information from the selected structural functors. Do not maintain a second inheritance registry. |
| `POL-CAT-017` | Put an axiom at the highest category that can state it. |
| `POL-CAT-018` | Distinguish a property subcategory from a category whose objects contain chosen data. |
| `POL-CAT-019` | Require chosen data during construction. Do not infer its existence from a property name. |
| `POL-CAT-020` | Enforce genuine category obligations when an object is constructed. |

## Functors and universal constructions

| ID | Policy |
| --- | --- |
| `POL-FUN-001` | Every functor explicitly owns its domain, codomain, object map, and arrow map. |
| `POL-FUN-002` | Add an element map only when the mathematical functor has a meaningful action on elements. |
| `POL-FUN-003` | Only selected structural functors contribute inherited public methods. |
| `POL-FUN-004` | Use ordinary functors for mathematical transport that does not define public inheritance. |
| `POL-FUN-005` | Represent forgetting, scalar change, and realization as functors, not object methods. |
| `POL-FUN-006` | Use functor composition to propagate structure. Do not add a separate propagation registry. |
| `POL-FUN-007` | A categorical construction must define its action on objects and arrows. |
| `POL-FUN-008` | Preserve the diagram and universal arrows that define a limit or colimit. |
| `POL-FUN-009` | A product retains its projections and mediating arrow. |
| `POL-FUN-010` | A coproduct retains its injections and mediating arrow. |
| `POL-FUN-011` | Let the apex of a universal construction inherit operations from the category in which it lives. |
| `POL-FUN-012` | Implement arbitrary small diagrams. Do not encode finiteness into the general construction. |
| `POL-FUN-013` | Represent a subobject by an object together with its monomorphism. |
| `POL-FUN-014` | Obtain the containing object of a subobject from the monomorphism's codomain. |

## The category of sets

| ID | Policy |
| --- | --- |
| `POL-SET-001` | `Sets()` owns arbitrary sets and arbitrary functions between them. |
| `POL-SET-002` | A set map requires a domain, codomain, and rule. It does not require a finite table. |
| `POL-SET-003` | Permit maps whose rules have no linearity, continuity, or finiteness hypothesis. |
| `POL-SET-004` | Support maps such as `QQ -> NN`, `QQ -> ZZ`, and `RR -> RR^2` as ordinary arrows in `Sets()`. |
| `POL-SET-005` | Let membership predicates return `bool \| Unknown`. |
| `POL-SET-006` | Treat `Unknown` as unavailable knowledge, not as `False`. |
| `POL-SET-007` | Construct a predicate-defined subset as an object with an inclusion arrow. |
| `POL-SET-008` | Support infinite predicate subobjects such as the even integers and prime integers inside `ZZ`. |
| `POL-SET-009` | Put cardinality on the set implementation. |
| `POL-SET-010` | Support finite, infinite, symbolic, and unknown cardinality results. |
| `POL-SET-011` | Use cardinality for sets. Use length only for an ordered finite sequence. |
| `POL-SET-012` | Support function sets and exponentials. |
| `POL-SET-013` | Support products and coproducts indexed by arbitrary small diagrams. |
| `POL-SET-014` | Support general limits and colimits in `Sets()`. |
| `POL-SET-015` | Propagate set operations, including cardinality, to objects produced by functors and universal constructions. |
| `POL-SET-016` | Do not enumerate an infinite set to answer a structural predicate. |

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

## Public API and types

| ID | Policy |
| --- | --- |
| `POL-API-001` | Shape the API from the mathematics, not from current storage fields or Python classes. |
| `POL-API-002` | Give each operation one owner, one public name, and one public export. |
| `POL-API-003` | Use standard mathematical and Sage syntax at call sites. |
| `POL-API-004` | Use `as_*` only for an explicit conversion to another mathematical representation. |
| `POL-API-005` | Keep private fields private to their owner or documented subclass contract. |
| `POL-API-006` | Ask another object through its public mathematical interface. |
| `POL-API-007` | Invoke Python protocols through public syntax such as `f(x)`, `iter(x)`, and `len(x)`. |
| `POL-API-008` | Name an accessor for the exact mathematical object or arrow it returns. |
| `POL-TYPE-001` | Give every value the type that names its mathematical role. |
| `POL-TYPE-002` | Distinguish categories, objects, elements, arrows, functors, rings, sets, domains, and codomains in types. |
| `POL-TYPE-003` | Never use `object` as a type. |
| `POL-TYPE-004` | Use `Any` only for a parameter that must accept an arbitrary membership candidate. |
| `POL-TYPE-005` | Never use `Any` as a return type. |
| `POL-TYPE-006` | Do not silence a type error with a cast, ignored diagnostic, deleted annotation, or wider type. |
| `POL-TYPE-007` | Fix the mathematical model, method owner, import boundary, or missing type declaration exposed by a type error. |
| `POL-TYPE-008` | Use category membership as type information. Do not inspect fields or method names for capabilities. |
| `POL-TYPE-009` | Do not invent wrapper types whose only purpose is to satisfy the type checker. |

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
| `POL-CODE-013` | Do not use `setattr` to assemble mathematical APIs after class construction. |
| `POL-CODE-014` | Keep a matrix distinct from the morphism it represents. |
| `POL-CODE-015` | Keep coordinates distinct from elements of their parent. |
| `POL-CODE-016` | Lower to a computation representation once and reconstruct the mathematical result once. |
| `POL-CODE-017` | Preserve exact arithmetic until an explicit numerical boundary. |
| `POL-CODE-018` | Keep precision parameters at the numerical boundary. |
| `POL-CODE-019` | Remove needless recomputation, enumeration, and verification without obscuring the mathematics. |

## Tests and performance

| ID | Policy |
| --- | --- |
| `POL-TEST-001` | Read the repository test rules before editing a test file. |
| `POL-TEST-002` | Make every assertion state a mathematical proposition or an essential type invariant. |
| `POL-TEST-003` | Test the intended end-to-end behavior, not implementation layout or past defects. |
| `POL-TEST-004` | Assert the correct category, parent, domain, codomain, images, composition, and mathematical equality as applicable. |
| `POL-TEST-005` | Use the smallest specimen that distinguishes correct behavior from a plausible failure. |
| `POL-TEST-006` | Test object, element, and arrow inheritance through the real category compiler. |
| `POL-TEST-007` | Test universal constructions through their universal arrows, not only their apex objects. |
| `POL-TEST-008` | Use a real Sage process for Sage behavior. |
| `POL-TEST-009` | Do not add a test that only asserts the absence of a previous mistake. |
| `POL-TEST-010` | Treat a passing test as evidence only for the proposition it executes. |
| `POL-PERF-001` | Measure performance with wall time as a function of input size. |
| `POL-PERF-002` | Use call counts only to locate repeated work. Do not use them as efficiency evidence. |
| `POL-PERF-003` | Preserve code that displays the mathematical sequence when a faster form hides it. |
| `POL-PERF-004` | Use small mathematical specimens unless the claim concerns a large named object. |

## Policy maintenance

| ID | Policy |
| --- | --- |
| `POL-INDEX-001` | Give every coding policy exactly one unique identifier. |
| `POL-INDEX-002` | Add an identifier only for a new coding rule, not for an example or restatement. |
| `POL-INDEX-003` | Keep identifiers stable when policy wording improves. |
| `POL-INDEX-004` | Retire an obsolete identifier without assigning it to another policy. |
