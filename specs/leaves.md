# Leaf category implementations

This specification defines the implementation boundary for leaf categories.
It records the discussion that separated structural inheritance from private computation.

The central rule is:

> `C.ObjectType`, `C.ElementType`, and `C.MorphismType` are the executable classes for `C`. The category writes or links them, and the kernel compiles each into the class of that same name.

These classes are not interfaces for another implementation hierarchy.
They are not method catalogues that a compiler matches against backend method names.

## Contents

- [Intended architecture](#intended-architecture)

- [Standard mathematics determines the three classes](#standard-mathematics-determines-the-three-classes)

- [Two different forms of reuse](#two-different-forms-of-reuse)

- [`C.ObjectType`, `C.ElementType`, and `C.MorphismType`](#cobjecttype-celementtype-and-cmorphismtype)

- [The leaf is the implementation firewall](#the-leaf-is-the-implementation-firewall)

- [Category declarations define or link implementations](#category-declarations-define-or-link-implementations)

- [Local methods are ordinary executable methods](#local-methods-are-ordinary-executable-methods)

- [Structure functors determine class inheritance](#structure-functors-determine-class-inheritance)

- [The policy conflict that exposed the gap](#the-policy-conflict-that-exposed-the-gap)

- [Rejected operation decorators](#rejected-operation-decorators)

- [Rejected mirrored backend surfaces](#rejected-mirrored-backend-surfaces)

- [Private computation inside a leaf implementation](#private-computation-inside-a-leaf-implementation)

- [Semantic lowering and reconstruction](#semantic-lowering-and-reconstruction)

- [Realization functors and private representations](#realization-functors-and-private-representations)

- [File placement](#file-placement)

- [Private neighboring engine modules](#private-neighboring-engine-modules)

- [One source of truth](#one-source-of-truth)

- [Leaf, kernel, and backend responsibilities](#leaf-kernel-and-backend-responsibilities)

- [The product algebra example](#the-product-algebra-example)

- [Relation to dynamic class inheritance](#relation-to-dynamic-class-inheritance)

- [Method signatures remain mathematical](#method-signatures-remain-mathematical)

- [Required policy interpretation](#required-policy-interpretation)

- [Acceptance conditions](#acceptance-conditions)

## Intended architecture

A category owns its objects, elements, morphisms, and operations.
Its implementation types are part of that ownership:

- `C.ObjectType` implements objects of `C`;

- `C.ElementType` implements elements of those objects;

- `C.MorphismType` implements morphisms of `C`;

- the category declaration identifies those implementation types;

- structure functors supply inherited operations.

A leaf category introduces only its new mathematics.
However, introducing a new operation includes implementing that operation.
The method body can use Sage or another mature dependency as a private computation engine.

The phrase “a leaf should read like mathematics” constrains semantic ownership and public data.
It does not require the leaf to contain no computation code.

Leaf purity is semantic purity.
It is not implementation abstinence.

Before writing a leaf, answer four questions:

1. What are its objects, elements, and morphisms?

2. What defining datum does the default constructor accept, and which named constructors accept other complete presentations?

3. Which immediate named functors supply inherited structure, and what do their object and morphism actions construct?

4. Which operations, predicates, algorithms, and theorems first belong to this category?

Those answers are the leaf contract.
The explicit structure functors and their executable actions contain the structural transport work.
The kernel compiles their consequences.
The standard templates are in [Leaf category template](leaf-category-template.md).

## Standard mathematics determines the three classes

This repository uses the ordinary mathematical meanings of category, object, element, morphism, functor, construction, and theorem.
The Python implementation does not define new meanings for these terms.

The standard definitions already determine the implementation classes:

- a category determines what its objects and morphisms are;

- `C.ObjectType` and `C.MorphismType` implement those mathematical kinds;

- `C.ElementType` implements the elements of represented objects when the theory has them;

- an operation's mathematical signature determines the exact type of the value it applies to, of each parameter, and of its result;

- a selected structure functor determines the compiled ancestor class, while its ordinary actions construct its public images;

- an element's ambient mathematical object determines its exact element type;

- a named construction owns the theorem used by that construction;

- the result category states the conclusion established by that theorem.

None of these facts requires a second runtime declaration.
An element does not carry a marker that declares it to be an element.
A method does not carry metadata that repeats its mathematical domain.
A functor's action does not depend on a mutable object registry.
A theorem does not become applicable through an authority token.

Use the following meanings throughout this specification:

- **explicit** means present in the semantic API as an exact type, category placement, defining morphism, named functor, named construction, predicate result, or hypothesis;

- **owner** means the category, object, morphism, functor, or universal construction whose mathematical definition states the operation or fact;

- **declaration** means the ordinary typed category, class, method, functor, or constructor definition at that owner;

- **construction authority** means that the named construction establishes its typed result by its defining theorem.

These words request no parallel metadata, decorator, annotation payload, registry, marker type, wrapper, or authority object.

A compiler error, import error, or type error can show that the current Python encoding is wrong.
It cannot select a new mathematical model.
When the code lacks an obvious encoding, derive the encoding from the standard mathematical definition.
If the repository cannot state that definition, the missing category, functor, morphism, construction, or exact type is the foundational defect.

The governing policies are `POL-MATH-001`, `POL-MATH-031` through `POL-MATH-033`, `POL-CAT-075` through `POL-CAT-080`, `POL-LEAF-053` through `POL-LEAF-056`, `POL-LEAF-061`, `POL-LEAF-062`, `POL-KERNEL-021` through `POL-KERNEL-025`, `POL-FUN-023`, `POL-FUN-035`, `POL-API-023`, `POL-API-028`, and `POL-CODE-042` through `POL-CODE-043`.

## Two different forms of reuse

The architecture has two independent reuse mechanisms.

### Structural inheritance

An implementation already owned by a target category reaches the leaf through the structure-functor class graph.
The kernel compiles its methods and constructor into the descendant class class.

Examples include:

- membership inherited from `Sets()`;

- addition inherited from additive groups;

- composition inherited from the owning morphism category;

- cardinality inherited through the route to `Sets()`.

The leaf does not implement, forward, or dispatch these operations.

### Private computation

An operation introduced by the leaf has a local executable method body.
That method can lower owned semantic data to a Sage representation, call a Sage algorithm, and reconstruct the owned result.

Examples for finite posets include:

- lower and upper covers;

- intervals;

- order ideals and filters;

- extrema;

- ranks and level sets;

- linear extensions.

The kernel does not implement or dispatch these methods.
Sage performs selected computations, but Sage does not own the public operation.

Implementation compression applies to inherited boilerplate.
It does not remove the executable bodies of mathematics newly introduced by a leaf.

## `C.ObjectType`, `C.ElementType`, and `C.MorphismType`

`C.ObjectType`, `C.ElementType`, and `C.MorphismType` are the executable classes for `C`.
A category specifies its new mathematics under those exact names.
The kernel constructs each class dynamically from that specification and the structure functors.

They are not:

- abstract declarations awaiting backend completion;

- schemas for generated methods;

- lists of operation names;

- interfaces implemented by a second Sage class;

- stubs whose bodies are replaced by descriptors;

- containers for annotations used by runtime dispatch.

Each public operation has one executable declaration on its mathematical owner.
A local object operation has its body on `C.ObjectType`. The same rule applies to `C.ElementType` and `C.MorphismType`.

Each of these classes can call dependencies.
Calling a dependency does not transfer ownership to that dependency.

## The leaf is the implementation firewall

The repository exists in part to repair a defect in the Sage implementation model.
Mathematically, there is one notion of a free module over a ring and one expected operation surface for that notion.
Sage has three different free-module implementations with different public operations.
Even an inherited operation such as cardinality is not available consistently across them.

For `M = ZZ^3`, the standard coordinate construction retains a finite-product presentation of the underlying set.
The selected structural route to `Sets()` supplies the set-owned cardinality and countability interface.
The product theorem establishes countability from the countability of `ZZ`.
Chosen enumerations of the three factors construct the standard product enumeration.
The property of being countable does not by itself choose that enumeration.
The result must be independent of the Sage free-module class used for private computation.
`M.cardinality()` is the method owned by `Sets().ObjectType` executing directly on `M`.
The selected functor initializes the set state on `M`, so that method needs no forwarding layer.
`M.is_countable()` returns the proposition that the underlying set lies in `Sets().Countable()`.
Established placement lets `ask(M.is_countable())` return `True` without enumeration.

This repository must not reproduce that split behind another abstraction.
A category never offers a menu of competing object implementations.
Its `ObjectType` is the one public class for objects of that category.
The same rule applies to `ElementType` and `MorphismType`.

The sole class is a firewall.
It collects the complete owned public operation surface and hides all possible computation choices.
A caller works with a free module, finite poset, or hyperbolic lattice.
The caller never chooses a Sage parent class, engine adapter, storage variant, or algorithm provider.

The firewall does not restrict private implementation technology.
A method can use:

- a Sage, SymPy, or NumPy value;

- an imported domain package such as VinAL;

- a bespoke class containing new research algorithms;

- compiled Cython code;

- a shell program;

- Julia, GAP, Singular, or Macaulay2;

- different exact algorithms selected from established mathematical hypotheses.

These are internal computations, not alternative implementations of the mathematical object.
They do not add public classes, backend selectors, realization variants, or automatic method routing.
The category-owned method calls the selected private computation explicitly and reconstructs the owned result.

The implementation class supplies public constructors from the semantic data that defines the category.
Those constructors can choose any suitable private representation.
Public code does not construct engine values to select an implementation.

## Construct from the strongest defining data

A leaf constructor accepts the smallest semantic datum that determines its new structure.
It recovers immediate ancestor objects from that datum.
It does not ask the caller to repeat them.

For a poset, an owned relation subobject

\[
R\hookrightarrow X\times X
\]

already determines `X`. The constructor verifies that the two factors are the same set and stores only `R` as local state.
The selected set projection has an object action that returns `X`.
The relation projection is not selected for inheritance.

Present this category as a subobject of the product of the set category and the relation category.
Then `product_projection(0)` is the set functor and `product_projection(1)` is the relation functor.

The same rule applies downstream:

- Let \((\mathcal M,\odot,1)\) be monoidal, let \(\mathcal C\) be an \(\mathcal M\)-actegory, and let \(A\) be a monoid object of \(\mathcal M\). An object of `Modules(A, C)` retains \(X\in\mathcal C\) and its action \(\rho:A\mathbin{\bullet}X\to X\), together with this ambient data.

- When closed or enriched structure represents these actions by an internal endomorphism monoid, the module structure is equivalently a monoid morphism \(A\to\operatorname{End}_{\mathcal C}(X)\).

- An object of `Algebras(R, C)` retains its base-relative presentation as a monoid object in the supplied monoidal category `Modules(R, C)`. The general monoid category owns its multiplication, unit, and laws.

- At a commutative base ring, a bilinear form \(b\) retains its module \(L\), the tensor presentation \(L\otimes_R L\), and its codomain \(R\).

- A lattice constructor can accept `b`, or the explicit pair `(L, b)` when that pair is the intended public presentation.

A downstream leaf returns its immediate structure functors.
Each functor supplies complete executable actions that return actual target objects and morphisms.
Sage's controlled linearization orders those classes and places each shared ancestor once.
With an arbitrary ambient category \(\mathcal C\), the leaf receives the capabilities owned by \(\mathcal C\); a set surface requires an explicit structure functor to `Sets()`.

Each named functor owns its public image of a source value.
It constructs that image through its specified object or morphism action.
Different functors with the same endpoints remain independent.

An inherited method runs on the structured source value.
The kernel makes the declaring category's state available on that same instance (`POL-KERNEL-018`).
The method reads that state through ordinary Python inheritance.

A category that combines two structures on one shared ancestor object is their pullback over that ancestor.
Its constructor asserts with `is` that both projections return the same ancestor object.
The pullback object retains that shared ancestor once with both defining structures.

When added structure does not add element data, the leaf `ElementType` declares no constructor.
The kernel constructs that exact category-owned element type with its ambient object.
Each named projection separately constructs its element image through its morphism action.
The element remains a `C.ElementType`, not an ancestor element type.

The category layer constructs and selects each immediate named functor.
A leaf that is a subobject of a product uses `product_projection(i)`. Otherwise, it reuses the exact functors retained by its defining category construction.

A leaf selects the strongest established property subcategory.
It does not repeat maps already retained by a product, pullback, comma, `Fun([1], C)`, or similar construction.
It never exposes a private engine conversion as a structural map.

If this implementation becomes sufficiently large or dominated by Python, foreign interfaces, conversions, process calls, or caches, move that complexity into private helper modules.
The category implementation class remains the sole public owner.
The helpers remain computation details and never become another method surface.

## A category specifies its three classes

A category specifies `C.ObjectType`, `C.ElementType`, and `C.MorphismType` directly:

```python
class LeafCategory(Category):
    class ObjectType(MathematicalObject):
        def leaf_operation(self) -> LeafResult:
            ...

    class ElementType(MathematicalElement):
        ...

    class MorphismType(MathematicalMorphism):
        ...
```

The kernel constructs these classes dynamically from structure functors.
For each structure functor `F: C -> D`, `C.ObjectType` inherits `D.ObjectType`.
The applicable element and morphism classes follow the same compiler rule.

## Local methods are ordinary executable methods

A local leaf method is an ordinary method with an ordinary executable body.

For example, a finite-poset rank operation can have this conceptual form:

```python
def rank(self) -> NonnegativeInteger:
    engine_rank = self._sage_poset().rank()
    return nonnegative_integer(engine_rank)
```

The method body states the implementation:

1. obtain the private computation representation;

2. run the selected exact algorithm;

3. construct the owned mathematical result.

An element-specific operation uses a separate total method:

```python
def rank_of_element(self, member: FinitePosetElement) -> NonnegativeInteger:
    engine_member = self._sage_element(member)
    engine_rank = self._sage_poset().rank(engine_member)
    return nonnegative_integer(engine_rank)
```

It does not use an optional `member` parameter.
The two mathematical operations have separate names and total signatures.

A short method can still be the correct owner.
A semantic method that invokes a mature algorithm is not a meaningless forwarding wrapper.
It supplies the public mathematical contract and the private computation boundary.

## Functor construction belongs to `Fun(C, D)`

`Cat()` supplies the generic categorical calculus.
The leaf decides which functor presents its structure and implements both actions completely.

The fixed-endpoint functor category owns construction of each functor:

```python
H = Fun(C, D)
F = H(on_object, on_morphism)
```

The leaf writer can inspect `H` for its ordinary and property-specific constructors.
A monic, full, replete functor is constructed in the corresponding property subcategory of `H`.
There is no second constructor namespace in `Cat`, the kernel, or a helper module.

A selected leaf functor has two sources:

1. The categorical construction that defines the leaf retained the exact projection, inclusion, restriction, lift, or evaluation functor.
   The leaf returns that object.

2. The functor is new leaf mathematics.
   The leaf constructs it in `Fun(self, Target)` and supplies its complete object and morphism actions.

`Groups(V)` owns the rule that its group construction determines a monoid construction.
It supplies that rule to the functor in `Fun(Groups(V), Monoids(V))`.
`Modules(A, C)` owns the rule that an action `A bullet X -> X` determines `X` and the matching morphism in `C`.
It supplies that rule to its functor in `Fun(Modules(A, C), C)`.
When a pullback, comma category, or other defining construction already retained the exact projection, the leaf reuses it.

Each object action returns an actual target object through a public target constructor.
Each morphism action returns an actual target morphism through its fixed-endpoint hom category.
The kernel compiles the selected target surface and treats the action functions as opaque.

A helper used only by one functor action is a local function or a private leaf method.
It does not appear in the public method catalogue or generated types.
A defining datum with an independent public mathematical meaning remains public even when a functor uses it.

## Structure functors determine class inheritance

The kernel constructs `C.ObjectType`, `C.ElementType`, and `C.MorphismType` dynamically from the immediate targets of `C.structure_functors()`.
Sage dynamic classes and Sage's controlled linearization resolve the resulting inheritance graph.

`C.ObjectType` inherits `Cat().ElementType` because an object of `C` is a point `* -> C`.
`C.ElementType` is the shared implementation and API for the elements of objects of `C`.
When an object `X` is regarded as a category, its elements are the points `* -> X`.
`C.MorphismType` is `Mor(C).ObjectType`.
A generalized element of a category `X` has the form `T -> X`.

For each structure functor `F: C -> D`, the kernel:

- places the applicable `D.ObjectType`, `D.ElementType`, or `D.MorphismType` in the corresponding class MRO;

- preserves each member specified for the corresponding class of `C`, except `__init__`;

- retains the local initializer for its declaring class;

- installs one generated wrapper in the corresponding class's `__init__` slot;

- makes the target implementation state available on the source instance;

- invokes inherited methods on the original structured value through ordinary Python method resolution;

- lets Sage's controlled linearization place each common ancestor once in the MRO and initialize it once through cooperative `super()`.

The local constructor accepts only the leaf's new semantic data.
It initializes that state and calls `super().__init__()` once.
A declaration can omit `__init__` when it adds no state.
Its generated wrapper advances to the next initializer in Sage's MRO.
The kernel handles private state sharing and once-only initialization.
The leaf does not add ancestor fields or ancestor arguments.
An object construction supplies its point `* -> C` to `Cat().ElementType`.
A morphism follows the object construction of `Mor(C)`.
An element construction supplies the local data required by its category-owned `ElementType`.

The compiler never interprets a local decorator as an instruction to find another method body.
It never pairs a leaf method with an engine method by name.

This is the decisive boundary:

> The kernel composes inherited implementations.
> The leaf implements new mathematics.

## The policy conflict that exposed the gap

The existing philosophy combined several correct goals:

- theory code should remain mathematically auditable;

- generic reflection and dispatch should remain in the kernel;

- engine representations should remain private;

- mature Sage algorithms should replace local reimplementations;

- public results should be owned mathematical values;

- leaves should contain no structural wiring.

Without a sharper boundary, these goals suggested a false choice.

One interpretation put direct Sage calls in the leaf and treated them as forbidden backend wiring.
The other moved the method bodies into a second backend hierarchy and treated the leaf as a declaration surface.

Both interpretations were wrong.

The correct distinction is:

- generic inheritance, construction-input traversal, and compiled class construction are kernel infrastructure;

- each named functor owns its public images;

- a leaf-owned method's selected computation is part of that leaf's implementation;

- lowering to Sage and reconstructing an owned result form a private computation boundary;

- a private computation boundary is not another implementation surface.

“Keep backend dispatch out of leaves” means that a leaf does not select among engines at runtime or maintain a backend registry.
It does not mean that a leaf cannot use Sage as its fixed implementation dependency.

“Keep engine method names private” means that engine names do not become public API. It does not prohibit a private method body from calling a Sage method.

## Rejected operation decorators

One rejected experiment replaced ordinary finite-poset methods with this shape:

```python
@realized_operation
def rank(self) -> NonnegativeInteger:
    assert False
```

The compiler then inspected `RealizedOperation`, recovered a stored declaration, and installed a descriptor that dispatched the operation elsewhere.

This design is invalid.

`realized_operation` has no mathematical meaning.
It is an engineering marker placed on every new leaf operation.
The method body is not an implementation.
The executable operation has moved into compiler dispatch.

This design causes several defects:

- `ObjectType` stops being the implementation class;

- ordinary source navigation no longer finds the executable operation;

- every new leaf method requires non-mathematical annotation;

- the compiler learns category-specific computation dispatch;

- method ownership becomes split between the leaf, descriptor, and backend;

- `assert False` stubs make incomplete methods appear declared;

- public operation signatures can drift from backend implementations.

No replacement decorator, annotation, registration record, or marker type can repair this ownership error.

## Rejected mirrored backend surfaces

A second rejected proposal introduced two matching surfaces:

```text
FinitePosetObject
SageFinitePosetObject
```

The category-owned class would declare operations.
The Sage class would implement the same operations.
A realization binding would connect the two surfaces, and the compiler would match their method names.

This design is also invalid.

There is no second “realization implementation surface.”
`FinitePosetObject` is the implementation.
Sage is a computation dependency used by that class.

A mirrored backend surface would create:

- two operation catalogues;

- two sources of method signatures;

- two places for operation documentation;

- name-based implementation matching;

- pressure for backend registries and abstract interfaces;

- uncertainty about which class owns mathematical reconstruction;

- a parallel hierarchy for objects, elements, and morphisms.

The backend does not implement the owned category.
It supplies engine values, conversions, and algorithms to the owned implementation class.

## Private computation inside a leaf implementation

A leaf implementation can use a private Sage value directly.
This is not a kernel defect.

For example, a finite-poset object can retain or construct a private Sage poset.
Its local methods can call exact Sage algorithms on that value.

The following facts are not defects by themselves:

- the leaf implementation imports a concrete Sage dependency;

- several methods call `self._sage_poset()`;

- a method calls a Sage operation with a similar name;

- the leaf stores a private cached Sage representation;

- a short method delegates the hard computation to Sage.

They become defects when they cause:

- engine values to cross the public boundary;

- repeated incorrect conversion logic;

- runtime selection among speculative backends;

- a second public or semantic operation owner;

- generic dispatch or route machinery inside the leaf;

- results in primitive or engine-shaped collections instead of owned mathematical collections.

Repeated access to one private representation does not alone justify a decorator, descriptor, registry, or second class hierarchy.

## Semantic lowering and reconstruction

Every public leaf method accepts and returns owned mathematical values.

A private computation boundary has this form:

\[
\text{owned input}
\longrightarrow
\text{engine representation}
\longrightarrow
\text{engine result}
\longrightarrow
\text{owned result}.
\]

The leaf method owns the complete sequence.

For a finite-poset method, this can require:

- verifying membership through the owned public operation;

- obtaining the corresponding engine element;

- running a Sage finite-poset algorithm;

- mapping engine elements back to canonical owned elements;

- constructing an owned finite set, ordered set, subobject, or morphism;

- preserving the original ambient poset.

A Sage iterator is not an owned mathematical collection.
A Python `int` is not automatically the required owned nonnegative integer.
A Sage subset is not an owned subobject.

The method reconstructs the semantic result before returning.

The reconstruction remains explicit when different methods return different mathematical kinds.
A generic backend dispatcher cannot infer these mathematical result types from method names.

## Realization functors and private representations

The word “realization” must distinguish two different notions.

### Mathematical realization functor

A realization functor is appropriate when the project models an actual mathematical functor between categories.
It has object and morphism maps and can be used explicitly.

Such a functor does not contribute methods through structural inheritance unless the category selects it in `structure_functors()`.

### Private computation representation

A private Sage parent, element, matrix, poset, or graph used inside one implementation is not automatically a functor.
It is implementation state.

It does not require:

- a category of engine implementations;

- an `ObjectType` parallel to the owned object type;

- a compiler binding;

- a method catalogue;

- natural transformations between backend method surfaces;

- a runtime engine registry.

Do not elevate a private representation into categorical structure only to dispatch ordinary method calls.

## File placement

The default layout keeps the category declaration and its implementation classes together.
This gives the shortest path from mathematical owner to executable method.

When one implementation class becomes a substantial audit unit, split by exact mathematical type:

```text
finite_posets.py
finite_poset_objects.py
finite_poset_elements.py
finite_poset_morphisms.py
```

The category declaration then links the sole implementation classes from those files.

This split does not create another implementation surface.
`FinitePosetObject` remains the only object implementation class.

Do not create one file per type automatically.
A separate file must contain a substantial coherent implementation unit.

Do not name the sole implementation class `SageFinitePosetObject`. Its exact mathematical type is `FinitePosetObject`, even when Sage supplies every nontrivial algorithm.

## Private neighboring engine modules

A category can use a private neighboring engine module when the computation boundary has substantial shared content:

```text
finite_posets.py
_finite_poset_sage.py
```

Prefer the concrete engine name.
A generic name such as `finite_poset_engine.py` suggests interchangeable engines and invites speculative dispatch infrastructure.

The private module can own:

- construction of the Sage representation;

- conversion to and from Sage elements;

- shared engine-native computation primitives;

- private representation caches;

- category-specific adaptation of a mature Sage algorithm.

It cannot own:

- public mathematical signatures;

- `ObjectType`, `ElementType`, or `MorphismType` alternatives;

- category membership or refinement decisions;

- public semantic result construction;

- operation documentation;

- compiler registration;

- a method-name map;

- runtime engine selection;

- a mirror of most public leaf methods.

The public leaf method calls the helper explicitly.
It selects the algorithm and constructs the owned result.

Category-independent Sage conversion primitives can live in the central Sage backend.
Category-specific computation remains beside its mathematical owner when that placement improves local auditability.

There is no mandatory engine module for each category.
Create one only when a real shared computation boundary earns the file.

## One source of truth

File separation is valid only when it preserves one source of truth.

For each public method, one location owns:

- its mathematical name;

- its public signature;

- its hypotheses;

- its result category;

- its executable semantic sequence;

- its documentation.

That location is the category-owned implementation class.

A private helper can own engine-specific conversion or raw computation.
It does not repeat the public contract.

The following shapes indicate a second source of truth:

- matching public and backend method lists;

- matching `ObjectType` and `SageObjectType` classes;

- operation decorators that store another callable;

- compiler tables from public names to engine names;

- duplicate method documentation in backend modules;

- public stubs paired with private executable methods;

- separate result-type declarations for one method.

If changing one mathematical operation requires synchronized edits to two method catalogues, the architecture is wrong.

## Leaf, kernel, and backend responsibilities

| Concern | Owner |
| --- | --- |
| Category-local operation name and signature | `ObjectType`, `ElementType`, or `MorphismType` |
| Category-local executable method body | The same implementation class |
| Local constructor and state | The same local implementation class |
| Complete object and morphism actions | The named functor |
| Controlled class MRO, private state sharing, and once-only initialization | Kernel |
| Inherited executable method | Declaring target category |
| Object and morphism images | The named functor |
| Choice of exact leaf algorithm | Leaf implementation method |
| Private lowering to Sage | Leaf implementation or private helper |
| Sage algorithm execution | Sage, called through the private boundary |
| Reconstruction of the owned result | Leaf implementation method |
| Generic Sage conversion shared by categories | Central Sage backend |
| Runtime backend registry or method matching | No owner; this is outside the design |

The kernel can contain complex Python machinery only for category-independent structural inheritance.
It does not become a universal operation dispatcher.

The backend can contain engine-specific machinery.
It does not become a second mathematical implementation hierarchy.

## The product algebra example

This example takes the ambient to be `Sets()`. Let

\[
\mathcal C=
\operatorname{Groups}(\operatorname{Sets}_\times()).
\operatorname{Additive}().\operatorname{Commutative}()
\]

with its tensor product.
Let \(R\) be a commutative monoid object of \(\mathcal C\), so \(R\) is an ordinary commutative ring.
The category `Modules(R, C)` is monoidal under \(\otimes_R\). Write `V_R` for that selected monoidal category.
`Algebras(R, C)` is its base-relative monoid-object presentation.

The canonical object

\[
R^n=\prod_{i=1}^{n}R
\]

is constructed as a product of ring objects in `Sets()`. It is an object of `Algebras(R, C)` with coordinatewise operations and diagonal structure map

\[
R\longrightarrow R^n,
\qquad
r\longmapsto(r,\ldots,r).
\]

Its structure-functor class graph contains

\[
\operatorname{Algebras}(R,\mathcal C)
\longrightarrow
\operatorname{Monoids}(V_R)
\longrightarrow
\operatorname{Magmas}(V_R)
\longrightarrow
\operatorname{Modules}(R,\mathcal C)
\longrightarrow
\mathcal C
\longrightarrow
\operatorname{Sets}.
\]

This chain reaches the underlying set

\[
U(R^n)=U(R)\times\cdots\times U(R).
\]

`Monoids(V_R)` supplies multiplication and one.
`Modules(R, C)` supplies scalar action.
The additive-group category supplies addition, zero, inverses, and subtraction.
`Sets()` supplies its set operations.

The construction must retain the strongest structure that it establishes:

- product-ring operations;

- \(R\)-algebra operations;

- module operations;

- set operations;

- finite-set operations when \(R\) and the index set are finite.

The algebra's complete surface is the union of the operations owned along this selected chain.

For \(R=\mathbf F_p\), the finite product belongs to finite rings and hence finite sets.
No exhaustive enumeration is required to establish finiteness.

An arbitrary module merely isomorphic to \(R^n\) needs a selected product presentation before this coordinatewise algebra structure transfers to it.
The canonical constructed object \(R^n\) already has that presentation.

This example reinforces the leaf rule.
A construction retains its mathematical placement.
A leaf does not flatten the result to a backend container or manually route it to sets.

## Relation to dynamic class inheritance

The immediate structure-functor targets supply the dynamic bases of the compiled class.
Sage's controlled linearization preserves each branch and places each common class once in the MRO.
See [resolution.md](resolution.md) for the complete decision.

For this set-based \(R^n\), the algebra-to-rings and algebra-to-modules branches introduce different applicable operations.
Both later reach `Sets()`. Sage's MRO contains the common `Sets().ObjectType` once.
The kernel performs no equality check between data attributed to the two branches.

This structural inheritance does not dispatch the algebra's local methods to Sage.
The two mechanisms remain separate:

- the structure-functor class graph determines inherited operations;

- local method bodies determine computations introduced by the category.

A route diamond cannot justify a mirrored backend hierarchy.
A backend representation is not another target class in the structure-functor graph.

## Method signatures remain mathematical

The computation boundary does not weaken public method signatures.

Do not write one method with an optional argument when the presence of that argument selects a different mathematical operation.
Use total named methods such as `rank()` and `rank_of_element(member)`.

Do not accept `Iterable[PosetElement]` when the method requires a mathematical set, ordered set, chain, or subobject.
Use the exact owned collection type.

Do not return `Iterator[PosetElement]` when the result is a mathematical set of covers, a linear extension, or an ordered family of level sets.
Construct the named owned mathematical collection.
Private traversal inside the computation boundary can remain lazy.

Backend APIs do not determine public types.
The public type states the mathematical input and result.
The leaf method performs the required conversion privately.

## Required policy interpretation

Apply the repository policies with these meanings.

### “No engineering wiring in leaves”

This bans:

- route traversal;

- compiled-class construction;

- canonical-image management;

- compiler metadata;

- method-name matching;

- runtime backend registries;

- generic refinement mechanics;

- dynamic type reconstruction.

It permits:

- a fixed Sage dependency;

- a private Sage representation;

- direct exact Sage algorithm calls;

- semantic lowering and reconstruction;

- small private helpers for a real computation boundary.

### “Keep backend details private”

This means that no engine type, name, exception, or collection enters the public contract.
It does not mean that an executable implementation cannot mention its private dependency.

### “Categories own operations”

Ownership includes the executable semantic method.
It is not satisfied by a stub plus a backend implementation elsewhere.

### “Kernel complexity removes leaf repetition”

This applies to structural inheritance repeated across categories.
It does not authorize a generic dispatcher for unrelated leaf algorithms.

### “Use mature algorithms”

The category-owned method calls the mature algorithm.
It does not reimplement it.
The dependency remains a computation engine rather than a mathematical owner.

### “Realizations are functors”

This applies when the realization is an actual modeled mathematical functor.
It does not require every private engine value or algorithm call to enter the functor compiler.

## Acceptance conditions

A leaf implementation satisfies this specification when all these facts hold:

- the category specifies `C.ObjectType`, `C.ElementType`, and `C.MorphismType`, and the kernel constructs their required dynamic inheritance;

- exact object, element, morphism, parameter, result, and constructor types follow from the category, operation, and functor definitions;

- a theorem-backed named construction states its conclusion through the exact result category without an authority value, proof token, or metadata record;

- those types contain the executable bodies of every locally owned public operation;

- local methods are ordinary methods without computation-routing decorators;

- no local method is an `assert False` declaration stub;

- inherited methods arrive only through structure functors;

- every class in Sage's MRO receives the state required by its implementation;

- the compiler does not match local operation names to backend names;

- no `SageXObject` or similar class mirrors the public method surface;

- private engine helpers expose no public mathematical interface;

- a fixed backend dependency can be used directly without a registry;

- every engine input is lowered privately;

- every engine result becomes an owned semantic result before return;

- public signatures use total methods and exact mathematical collection types;

- file splitting preserves one implementation class and one method source of truth;

- an engine-specific neighboring module exists only for substantial shared computation;

- construction results retain every mathematically established category placement;

- Sage's controlled linearization preserves all branch-owned operations and places each common implementation class once in the MRO;

- a mathematician can find the executable operation from its category-owned implementation class without understanding kernel class construction.

The short form is:

> The category-owned type is the implementation.
> The kernel supplies inheritance.
> Sage supplies computation.
> No fourth surface connects them.
