# Leaf category implementations

This specification owns the boundary between category theory, the kernel, and private computation engines.
It implements D03, D08, D13, D118 through D123, and `POL-LEAF-053` through `POL-LEAF-062`.

See [functor.md](functor.md) for `Cat`, `Mor`, `Fun`, functor actions, and structure-functor selection.
See [property-refinement.md](property-refinement.md) for property categories and same-object refinement.
See [resolution.md](resolution.md) for the private Sage compiler.

## Contents

- [Leaf contract](#leaf-contract)
- [Owned implementation classes](#owned-implementation-classes)
- [Constructors](#constructors)
- [Structure functors](#structure-functors)
- [Inherited constructions](#inherited-constructions)
- [Property categories](#property-categories)
- [Computation-engine boundary](#computation-engine-boundary)
- [Exact types](#exact-types)
- [Private helpers and files](#private-helpers-and-files)
- [Acceptance conditions](#acceptance-conditions)

## Leaf contract

A leaf states only its new mathematics.
It answers four questions:

1. What are its objects, elements, and morphisms?
2. What data constructs one object or morphism?
3. Which immediate named functors supply inherited structure?
4. Which operations, predicates, algorithms, and theorems first belong here?

The category owns these answers.
Generic categorical constructions retain their own functors and universal data.
The kernel compiles inherited implementation.
Private engines supply algorithms.

## Owned implementation classes

For each category `C`:

- `C.ObjectType` implements objects of `C`.
- `C.ElementType` implements elements of objects of `C`.
- `C.MorphismType` implements morphisms of `C`.

These classes contain the executable methods first owned by `C`.
Each public operation has one method definition and one exact signature.
The category declaration writes or links all three classes.

```python
class LeafCategory(Category):
    class ObjectType:
        def leaf_operation(self, argument: LeafArgument) -> LeafResult:
            ...

    class ElementType:
        pass

    class MorphismType:
        pass
```

An empty class body states that the leaf adds no local mathematics for that kind.
Inherited methods still reach the compiled class through selected structure functors.

## Constructors

The default call `C(data)` constructs an object of `C` from its usual complete mathematical data.
A named constructor accepts another complete mathematical presentation.
Every constructor returns `C.ObjectType`.

```python
C(defining_data)
C.from_presentation(presentation)
C.from_sage(engine_value)
```

The constructor asks for the smallest datum that determines the new structure.
It obtains data already determined by that datum from its mathematical owner.

For a poset, the primary datum is a relation subobject

\[
R\hookrightarrow X\times X.
\]

The codomain and retained product projections determine `X`.
The caller does not repeat `X`.

The [poset template](poset-minimal-template.py) shows this constructor and its functor to `Sets()`.

## Structure functors

Each entry in `C.structure_functors()` is an ordinary object of `Fun(C, D)`.
Selection contributes the applicable target implementation classes.
It does not change the functor's type or mathematical action.
These declarations build the repository's new owned category graph. They do not import,
reuse, or modify Sage's mathematical category graph; a migrated Sage category is a new
owned leaf or construction in this graph.

A leaf gets a selected functor in one of two ways:

1. It returns the exact functor retained by its defining categorical construction.
2. It constructs new leaf mathematics through `Fun(C, D)`.

A new leaf functor supplies complete executable actions:

```python
def target_functor(self) -> Cat().MorphismType:
    D = TargetCategory()

    def on_object(X: self.ObjectType) -> D.ObjectType:
        return D(X.target_data())

    def on_morphism(f: self.MorphismType) -> D.MorphismType:
        source = on_object(f.domain())
        target = on_object(f.codomain())
        return Mor(D)(source, target)(f.target_action())

    return Fun(self, D)(on_object, on_morphism)
```

`on_object(X)` constructs and returns the public image in `D`.
`on_morphism(f)` constructs and returns the public image in the exact target hom category.
These two actions are the sole leaf declaration of the functor.
Their inputs are completed source values. The kernel does not ask a leaf to make either
action support partially initialized constructor state.

A leaf can create a structural diamond simply by selecting functors whose transitive
targets meet. This never requires route-resolution boilerplate. The kernel chooses the
single shared implementation occurrence through controlled C3 and debug-logs the diamond
while its coherence remains implicit. Future optional coherence is expressed, if needed,
by ordinary owned 2-morphism data between the composite functors rather than by a
leaf-specific compiler record.

A helper used only by one action stays local to that action or private to the leaf.
A datum with independent public mathematical meaning keeps its public mathematical name.

## Inherited constructions

The generic category theory owns its complete construction data.
A leaf reuses that data and states only its added structure or theorem.

Examples include:

- a pullback-defined category selects the retained pullback projections;
- a category of structured pairs selects the relevant product projections;
- a subcategory selects its retained monomorphism;
- a lifted limit reuses the selected cone and universal morphism;
- a restricted functor comes from `F.restrict(P, Q)`;
- an inherited property category comes from `F.inverse_image(C.P())`.

For a universal construction, `Cat` owns the shape, diagram, cone or cocone, legs, apex, and universal map.
The leaf states the additional leaf structure and the theorem that the construction preserves or creates it.

One apex can have many presentations.
Operations that depend on one presentation remain on that presentation object.

## Property categories

A leaf declares a property axiom once.
The registered axiom identifier determines the public `is_P()` spelling.
The generated method returns the containment proposition for `C.P()`.

A predicate-backed implementation supplies the private abstract `_predicate()` method required by `PredicateSubcategory`.
It can also register exact handlers at the property owner.

The complete example exists in [finite-set-minimal-template.py](finite-set-minimal-template.py).
The general contract exists in [property-refinement.md](property-refinement.md).

## Computation-engine boundary

A category-owned method can use Sage, SymPy, GAP, Singular, Macaulay2, Julia, Cython, shell programs, or imported research software.
The method remains the public mathematical owner.

A private computation has this form:

\[
\text{owned input}
\longrightarrow
\text{engine input}
\longrightarrow
\text{engine result}
\longrightarrow
\text{owned result}.
\]

The leaf method owns the complete sequence.
It selects the exact algorithm from established mathematical data.
It returns an owned category, object, element, morphism, functor, proposition, or query result.

```python
def rank(self) -> NonnegativeInteger:
    engine_rank = self._sage_poset().rank()
    return NonnegativeIntegers()(engine_rank)
```

The public API names the mathematical operation.
Private helpers can use engine names and engine types.
The caller does not select an engine.

## Exact types

Every public signature uses the exact mathematical input and result types.

- Use `C.ObjectType`, `C.ElementType`, and `C.MorphismType` for category-owned values.
- Use an owned set, ordered set, indexed family, or other named collection.
- Use separate total methods for distinct mathematical operations.
- Return a proposition for a truth question.
- Return an applied query with an exact result category for a partial value question.

For example, `rank()` and `rank_of_element(x)` are distinct operations.
They do not share one optional parameter.

## Private helpers and files

Keep the category declaration and its implementation classes together by default.
Split a substantial implementation by exact mathematical type:

```text
finite_posets.py
finite_poset_objects.py
finite_poset_elements.py
finite_poset_morphisms.py
```

A substantial private Sage boundary can use a neighboring module:

```text
finite_posets.py
_finite_poset_sage.py
```

The private module can own engine conversion, engine-native computations, and private caches.
The category-owned classes retain public signatures, semantic result construction, and operation documentation.

## Acceptance conditions

A leaf satisfies this specification when:

- its source states only the category's new mathematics after inherited structure is removed;
- it declares `ObjectType`, `ElementType`, and `MorphismType` under their exact names;
- each locally owned public operation has one executable method body;
- each new functor has complete object and morphism actions;
- `structure_functors()` returns only the immediate named functors that supply inheritance;
- the leaf reuses functors and universal data retained by its defining constructions;
- every public signature uses exact mathematical types;
- private computation returns an owned mathematical result;
- property methods and typed queries follow their canonical specifications;
- the leaf imports no kernel internal;
- the caller selects no computation engine;
- one mathematical fact has one semantic owner.

The kernel consequence is direct inherited execution on the structured source value.
The private mechanism is specified only in [resolution.md](resolution.md).
