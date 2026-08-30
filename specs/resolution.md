# Private Sage runtime

This specification owns the private class compiler and runtime support.
It implements D94, D109 through D114, D118, and D123.
It also implements `POL-CAT-012`, `POL-KERNEL-017`, and `POL-KERNEL-028` through `POL-KERNEL-036`.

The public category theory lives in [functor.md](functor.md).
The leaf boundary lives in [leaves.md](leaves.md).
Nothing in this file adds a public mathematical object or a leaf declaration.

## Fixed private dependencies

The project runs in the fixed Sage research environment on Python `>=3.14,<3.15`.
Python packages use uv. GAP packages use PackageManager. Julia and its packages use JuliaPkg.
The private runtime assigns these responsibilities:

| Responsibility | Dependency | Verified scope |
| --- | --- | --- |
| Python implementation classes, controlled C3, dynamic refinement, identity caches, nested-class binding, introspection, indexed families, and `Unknown` | SageMath 10.9.x | Private Python runtime support. The owned category graph remains authoritative. |
| Categories, functors, natural transformations, opposites, category products, and installed universal operations | GAP `>=4.13`; CAP `2026.07-04`; ToolsForHomalg `2026.04-01`; ToolsForCategoricalTowers `2026.08-01`; CartesianCategories `2026.08-02`; MonoidalCategories `2026.08-02`; SubcategoriesForCAP `2026.07-01`; SliceCategories `2026.06-01`; FpCategories `2026.07-03`; FunctorCategories `2026.08-01` | CAP supplies operations installed on CAP categories. ToolsForCategoricalTowers supplies finite decorated-diagram limits and colimits. FunctorCategories requires an object-finite or finitely presented source. FpCategories supplies finite walking shapes and presentations. SliceCategories supplies slices. |
| Pure-GAP categorical-tower compilation | CompilerForCAP `2026.07-01` | It compiles GAP CAP regions only. |
| Finite diagram syntax and retained finite presentations | Julia 1.12.7; Catlab 0.17.6; GATlab 0.2.4; JuliaCall `>=0.9.35,<0.10` | Catlab free diagrams have finite object and morphism sets. Its limit and colimit wrappers retain finite diagrams, apexes, and legs. |
| Proposition algebra, assumptions, and exact symbolic calculation | SymPy `>=1.14,<2` | Boolean expressions, assumptions, and exact symbolic handlers over private handles. |
| Residual exact-handler dispatch | plum-dispatch | Private dispatch without conversions or promotions. |
| Residual wrapper and descriptor behavior | wrapt | Private Python call and descriptor behavior. |
| Private slotted frozen records | attrs `>=26.1,<27` | Private execution records only. |

Each adapter lowers owned inputs and reconstructs the exact owned result.
No dependency defines the public category graph, public operation, category containment, or semantic owner.

The inspected dependencies cover only finite or presented functor-category cases; they do not supply arbitrary non-enumerative `Fun(I, C)`.
They also do not supply a strict pullback category of arbitrary functors or one Python--GAP--Julia bridge.
CAP object-level pullbacks are not pullbacks in owned `Cat`.
Mathlib and Agda Categories provide mature formal references for generic functor and comma categories, but no executable engine for this runtime.
Repository-owned implementation of any uncovered generic construction requires owner approval before its phase starts.

Development uses pytest `>=9.1,<10`, Hypothesis `>=6.165,<7`, Ruff `>=0.16.5,<1`, mypy `>=2`, and `dzackgarza/sagemath-mypy-plugin@main`.
Migration uses LibCST `>=1.9,<2` until its codemods finish.
D114 continues to assign `tree-sitter-sage` to Sage syntax and `makefun` to a later generated-signature need.

The CAP runtime and the Catlab runtime remain separate private engines.
Owned Python values cross them through separate private adapters.
CompilerForCAP compiles only pure GAP CAP regions.

## Inputs

For each category `C`, the compiler receives:

- the local `C.ObjectType`, `C.ElementType`, and `C.MorphismType` declarations;
- the immediate named functors selected by `C.structure_functors()`;
- the applicable target implementation class for each selected functor;
- the exact property categories and construction categories already built in `Cat`.

These inputs describe the repository's owned category graph. The kernel does not inspect
or extend Sage's mathematical category graph. It builds a private Sage runtime mirror only
to obtain Sage's class-building behavior. The implementation classes ultimately share the
ordinary Sage/Python `Parent` ancestry propagated at the `Cat().ObjectType` root; that
runtime ancestry is not a categorical relation in the owned graph.

The compiler treats each functor action as opaque.
It does not interpret its source code, fields, result data, or private helpers.
The object and morphism actions remain the complete public functor declaration.

## Sage class construction

Each owned implementation class is the `parent_class` of a private Sage runtime category.
The kernel gives that category the applicable immediate target categories and the local method provider.

Use these Sage facilities:

- `Category._all_super_categories`;
- `Category._super_categories_for_classes`;
- `Category._make_named_class`;
- `C3_sorted_merge`;
- `dynamic_class`.

Sage owns graph traversal, controlled C3 linearization, dynamic class identity, and method resolution.
The repository does not implement a second version of those operations.

A shared target class occurs once in the method resolution order.
Each local initializer runs once.
Local declarations take precedence over inherited declarations.

## Direct inherited execution

For a selected functor `F: C -> D`, the applicable `D` implementation class occurs in the compiled class of `C`.
Methods declared by `D` run directly on the source value.
Python special methods follow the same rule.

The two ordinary actions of `F` remain the sole public description of how target values are
constructed (D123), and they apply only to completed source values. The kernel must not
invoke either action on a partially initialized source as an implicit constructor-state
transport. Public functor application remains separate from private inherited-state
installation.

Private initializer threading follows the compiled implementation DAG. Each reached
implementation class initializes once. If several structural paths reach one implementation
owner, controlled C3 contributes one shared occurrence and the other paths do not cause
second initialization or competing public image construction. Route preference, wherever
needed, remains the declaration-order rule of D56 rather than a second C3-specific rule.
Any private execution record or cached class data remains implementation-only and cannot
become a second leaf-authored description of a functor action.

## Diamond diagnostics and future coherence

Every diamond in the owned structure-functor graph is accepted. Until the owned theory
explicitly supplies coherence between the relevant composites, the kernel emits a
`DEBUG`-level diagnostic identifying the unresolved diamond. If the diagnostic names a
preferred path, it uses D56's declaration order. Debugging is opt-in: the same condition
is never a warning or compilation failure.

M1 requires only this diagnostic and the once-only C3 behavior. A later kernel extension
can consume ordinary owned 2-morphism data between the composite functors and suppress the
diagnostic for that diamond. That future mechanism must reuse the natural-transformation
machinery of `Fun`; it must not add a coherence certificate, proof record, route registry,
or second functor declaration. No public hook spelling or exact 2-cell property is fixed in
M1.

## Runtime categories and caches

Cache `_RuntimeImplementationCategory(C, kind)` by the identity of the owned category and exact implementation kind.
Normalize categorical level identities before lookup.
In particular, use `Mor(C).ObjectType = C.MorphismType`.

Use Sage cache facilities according to key equality:

- use `CachedRepresentation`, `UniqueRepresentation`, and `cached_method` for ordinary exact keys;
- use `MonoDict` and `TripleDict` when a key contains an owned value with proposition-valued equality;
- use `dynamic_class(..., cache=True)` for a class built directly by the kernel.

These caches preserve runtime identity only.
They do not own mathematical equality or categorical structure.

## Properties and constructions

Use Sage `CategoryWithAxiom` and `_base_category_class_and_axiom` for private property-class binding.
Use Sage `uncamelcase(identifier, "_")` when an axiom identifier needs snake case.
The owned property category, containment proposition, inverse images, and subcategory monomorphism remain in `Cat`.

Reuse Sage functorial-construction category factories for private family binding and method-provider assembly.
For example, Sage `CartesianProductsCategory` can supply private implementation classes.
The owned limiting cone still retains the diagram, legs, apex, and universal map.

Use Sage `Hom`, `Homset`, `Map`, `Morphism`, and `IdentityMorphism` when their endpoints are Sage parents.
Keep generic `Mor` and `Fun` in the owned `Cat` layer.
Do not force an abstract category object to become a Sage `Parent`.

## Declarations and signatures

Read ordinary Python declarations and generated stubs with Python 3.14 `ast`.
Migration codemods use LibCST when they must preserve source formatting.
Use ordinary declared functions for fixed wrappers.
Use Sage introspection and wrapt for residual callable, descriptor, and signature behavior.

The kernel can inspect exact method signatures and mathematical annotations.
It does not require a leaf to describe call mechanics or compiler state.

## Semantic collisions

Sage resolves method order.
It does not decide whether two unrelated mathematical owners can use one public spelling.

Keep one semantic collision check.
Reject a compiled class when unrelated declaring categories define different mathematical operations with the same public name.
Do not use selection order to resolve that conflict.

## Acceptance conditions

The private runtime satisfies this specification when:

- Sage constructs each owned implementation class from local methods and immediate selected targets;
- the same mechanism handles objects, elements, and morphisms;
- both branches of a class diamond contribute their local methods;
- a shared target class occurs once and initializes once;
- unresolved owned structural diamonds compile and appear only in opt-in `DEBUG` logs;
- local declarations take precedence;
- inherited methods run directly on the source value;
- public functor application returns its separate owned image;
- public functor actions are never invoked on partially initialized source values for state installation;
- the private Sage implementation graph remains distinct from Sage's mathematical category graph;
- temporary runtime data has no public mathematical effect;
- unrelated mathematical declarations with one spelling fail as a semantic collision;
- theory modules import no private runtime type;
- every fixed dependency owns only its assigned private responsibility;
- each adapter reconstructs the exact owned mathematical result.
