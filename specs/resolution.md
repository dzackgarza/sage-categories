# Private Sage runtime

This specification owns the private class compiler and runtime support.
It implements D94, D109 through D114, D118, and D123.
It also implements `POL-CAT-012`, `POL-KERNEL-017`, and `POL-KERNEL-028` through `POL-KERNEL-036`.

The public category theory lives in [functor.md](functor.md).
The leaf boundary lives in [leaves.md](leaves.md).
Nothing in this file adds a public mathematical object or a leaf declaration.

## Inputs

For each category `C`, the compiler receives:

- the local `C.ObjectType`, `C.ElementType`, and `C.MorphismType` declarations;
- the immediate named functors selected by `C.structure_functors()`;
- the applicable target implementation class for each selected functor;
- the exact property categories and construction categories already built in `Cat`.

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

This private mechanism does not apply `F`.
The public call `F.on_object(X)` constructs the separate image in `D`.
The public call `F.on_morphism(f)` constructs the separate image in the exact target hom category.

The runtime can keep temporary initialization records or cached class data.
Such data has no public mathematical meaning.
It does not select a functor, define a functor image, establish category placement, or require a leaf-authored counterpart.

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
Use `inflection` for the public method spelling derived from the registered axiom identifier.
The owned property category, containment proposition, inverse images, and subcategory monomorphism remain in `Cat`.

Reuse Sage functorial-construction category factories for private family binding and method-provider assembly.
For example, Sage `CartesianProductsCategory` can supply private implementation classes.
The owned limiting cone still retains the diagram, legs, apex, and universal map.

Use Sage `Hom`, `Homset`, `Map`, `Morphism`, and `IdentityMorphism` when their endpoints are Sage parents.
Keep generic `Mor` and `Fun` in the owned `Cat` layer.
Do not force an abstract category object to become a Sage `Parent`.

## Declarations and signatures

Read ordinary Python declarations and generated stubs with Python 3.14 `ast`.
Use `tree-sitter-sage` only for Sage syntax.
Use ordinary declared functions for fixed wrappers.
Use `makefun` only when a generated wrapper needs a runtime signature.

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
- local declarations take precedence;
- inherited methods run directly on the source value;
- public functor application returns its separate owned image;
- temporary runtime data has no public mathematical effect;
- unrelated mathematical declarations with one spelling fail as a semantic collision;
- theory modules import no private runtime type.
