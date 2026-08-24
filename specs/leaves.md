# Leaf category implementations

This specification defines the implementation boundary for leaf categories. It records
the discussion that separated structural inheritance from private computation.

The central rule is:

> `C.ObjectType`, `C.ElementType`, and `C.ArrowType` are the executable implementation
> classes for `C`. The category declaration defines or links those exact classes.

These classes are not interfaces for another implementation hierarchy. They are not
method catalogues that a compiler matches against backend method names.

## Contents

- [Intended architecture](#intended-architecture)
- [Two different forms of reuse](#two-different-forms-of-reuse)
- [The implementation classes](#the-implementation-classes)
- [The leaf is the implementation firewall](#the-leaf-is-the-implementation-firewall)
- [Category declarations define or link implementations](#category-declarations-define-or-link-implementations)
- [Local methods are ordinary executable methods](#local-methods-are-ordinary-executable-methods)
- [Inherited methods remain kernel-owned transport](#inherited-methods-remain-kernel-owned-transport)
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
- [Relation to structural diamonds](#relation-to-structural-diamonds)
- [Method signatures remain mathematical](#method-signatures-remain-mathematical)
- [Required policy interpretation](#required-policy-interpretation)
- [Acceptance conditions](#acceptance-conditions)

## Intended architecture

A category owns its objects, elements, arrows, and operations. Its implementation types
are part of that ownership:

- `C.ObjectType` implements objects of `C`;
- `C.ElementType` implements elements of those objects;
- `C.ArrowType` implements arrows of `C`;
- the category declaration identifies those implementation types;
- selected structural functors supply inherited operations.

A leaf category introduces only its new mathematics. However, introducing a new
operation includes implementing that operation. The method body can use Sage or another
mature dependency as a private computation engine.

The phrase “a leaf should read like mathematics” constrains semantic ownership and
public data. It does not require the leaf to contain no computation code.

Leaf purity is semantic purity. It is not implementation abstinence.

## Two different forms of reuse

The architecture has two independent reuse mechanisms.

### Structural inheritance

An operation already owned by a structural ancestor reaches the leaf through the
selected structural functors. The kernel transports the receiver, arguments, and
result.

Examples include:

- membership inherited from `Sets()`;
- addition inherited from additive groups;
- composition inherited from the owning arrow category;
- cardinality inherited through the route to `Sets()`.

The leaf does not implement, forward, or dispatch these operations.

### Private computation

An operation introduced by the leaf has a local executable method body. That method can
lower owned semantic data to a Sage representation, call a Sage algorithm, and
reconstruct the owned result.

Examples for finite posets include:

- lower and upper covers;
- intervals;
- order ideals and filters;
- extrema;
- ranks and level sets;
- linear extensions.

The kernel does not implement or dispatch these methods. Sage performs selected
computations, but Sage does not own the public operation.

Implementation compression applies to inherited boilerplate. It does not remove the
executable bodies of mathematics newly introduced by a leaf.

## The implementation classes

`ObjectType`, `ElementType`, and `ArrowType` have one precise meaning. They are the
classes whose instances implement the corresponding mathematical roles.

They are not:

- abstract declarations awaiting backend completion;
- schemas for generated methods;
- lists of operation names;
- interfaces implemented by a second Sage class;
- stubs whose bodies are replaced by descriptors;
- containers for annotations used by runtime dispatch.

Each public operation has one executable declaration on its mathematical owner. A local
operation on objects has its body on `C.ObjectType`. The same rule applies to elements
and arrows.

The implementation class can call dependencies. Calling a dependency does not transfer
ownership to that dependency.

## The leaf is the implementation firewall

The repository exists in part to repair a defect in the Sage implementation model.
Mathematically, there is one notion of a free module over a ring and one expected
operation surface for that notion. Sage has three different free-module
implementations with different public operations. Even an inherited operation such as
cardinality is not available consistently across them.

This repository must not reproduce that split behind another abstraction. A category
never offers a menu of competing object implementations. Its `ObjectType` is the one
public class for objects of that category. The same rule applies to `ElementType` and
`ArrowType`.

The sole class is a firewall. It collects the complete owned public operation surface
and hides all possible computation choices. A caller works with a free module, finite
poset, or hyperbolic lattice. The caller never chooses a Sage parent class, engine
adapter, storage variant, or algorithm provider.

The firewall does not restrict private implementation technology. A method can use:

- a Sage, SymPy, or NumPy value;
- an imported domain package such as VinAL;
- a bespoke class containing new research algorithms;
- compiled Cython code;
- a shell program;
- Julia, GAP, Singular, or Macaulay2;
- different exact algorithms selected from established mathematical hypotheses.

These are internal computations, not alternative implementations of the mathematical
object. They do not add public classes, backend selectors, realization variants, or
automatic method routing. The category-owned method calls the selected private
computation explicitly and reconstructs the owned result.

The implementation class supplies constructor routes from the general semantic data
that defines the category. Those constructors can choose any suitable private
representation. Public code does not construct engine values to select an
implementation.

The category layer also defines the immediate structural functors. Each object map
uses a public constructor route of the target category to construct the required
mathematical image. For example, a functor from a leaf to its immediate supercategory
must understand that supercategory's constructors. It must not expose a private engine
conversion as the structural map.

If this implementation becomes sufficiently large or dominated by Python, foreign
interfaces, conversions, process calls, or caches, move that complexity into private
helper modules. The category implementation class remains the sole public owner. The
helpers remain computation details and never become another method surface.

## Category declarations define or link implementations

A category declaration can define its implementation class locally:

```python
class LeafCategory(Category):
    class ObjectType(MathematicalObject):
        def leaf_operation(self) -> LeafResult:
            ...
```

It can instead link one imported class:

```python
class LeafCategory(Category):
    ObjectType = LeafObject
    ElementType = LeafElement
    ArrowType = LeafMorphism
```

Both forms have one implementation class for each mathematical role.

When the category links an imported class, the category module contains no duplicate
method declarations, abstract stubs, or backend method map. The linked class is the
canonical implementation.

The link from the category to its implementation type is part of the categorical
declaration. It is not a runtime implementation-routing mechanism.

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

It does not use an optional `member` parameter. The two mathematical operations have
separate names and total signatures.

A short method can still be the correct owner. A semantic method that invokes a mature
algorithm is not a meaningless forwarding wrapper. It supplies the public mathematical
contract and the private computation boundary.

## Inherited methods remain kernel-owned transport

The compiler acts only on inherited operations.

For a method declared by a structural ancestor, the compiler:

- selects the complete structural route to the declaring category;
- transports the receiver and mathematical arguments;
- invokes the ancestor's executable method;
- transports the mathematical result back;
- preserves exact ambient objects, domains, and codomains.

For a method declared locally by the leaf, the compiler does none of these operations.
It keeps the ordinary local method body.

The compiler never interprets a local decorator as an instruction to find another
method body. It never pairs a leaf method with an engine method by name.

This is the decisive boundary:

> The kernel transports inherited mathematics. The leaf implements new mathematics.

## The policy conflict that exposed the gap

The existing philosophy combined several correct goals:

- theory code should remain mathematically auditable;
- generic reflection and dispatch should remain in the kernel;
- engine representations should remain private;
- mature Sage algorithms should replace local reimplementations;
- public results should be owned mathematical values;
- leaves should contain no structural wiring.

Without a sharper boundary, these goals suggested a false choice.

One interpretation put direct Sage calls in the leaf and treated them as forbidden
backend wiring. The other moved the method bodies into a second backend hierarchy and
treated the leaf as a declaration surface.

Both interpretations were wrong.

The correct distinction is:

- generic inheritance, route traversal, transport, and method installation are kernel
  infrastructure;
- a leaf-owned method's selected computation is part of that leaf's implementation;
- lowering to Sage and reconstructing an owned result form a private computation
  boundary;
- a private computation boundary is not another implementation surface.

“Keep backend dispatch out of leaves” means that a leaf does not select among engines at
runtime or maintain a backend registry. It does not mean that a leaf cannot use Sage as
its fixed implementation dependency.

“Keep engine method names private” means that engine names do not become public API. It
does not prohibit a private method body from calling a Sage method.

## Rejected operation decorators

One rejected experiment replaced ordinary finite-poset methods with this shape:

```python
@realized_operation
def rank(self) -> NonnegativeInteger:
    assert False
```

The compiler then inspected `RealizedOperation`, recovered a stored declaration, and
installed a descriptor that dispatched the operation elsewhere.

This design is invalid.

`realized_operation` has no mathematical meaning. It is an engineering marker placed on
every new leaf operation. The method body is not an implementation. The executable
operation has moved into compiler dispatch.

This design causes several defects:

- `ObjectType` stops being the implementation class;
- ordinary source navigation no longer finds the executable operation;
- every new leaf method requires non-mathematical annotation;
- the compiler learns category-specific computation dispatch;
- method ownership becomes split between the leaf, descriptor, and backend;
- `assert False` stubs make incomplete methods appear declared;
- public operation signatures can drift from backend implementations.

No replacement decorator, annotation, registration record, or marker type can repair
this ownership error.

## Rejected mirrored backend surfaces

A second rejected proposal introduced two matching surfaces:

```text
FinitePosetObject
SageFinitePosetObject
```

The category-owned class would declare operations. The Sage class would implement the
same operations. A realization binding would connect the two surfaces, and the compiler
would match their method names.

This design is also invalid.

There is no second “realization implementation surface.” `FinitePosetObject` is the
implementation. Sage is a computation dependency used by that class.

A mirrored backend surface would create:

- two operation catalogues;
- two sources of method signatures;
- two places for operation documentation;
- name-based implementation matching;
- pressure for backend registries and abstract interfaces;
- uncertainty about which class owns mathematical reconstruction;
- a parallel hierarchy for objects, elements, and arrows.

The backend does not implement the owned category. It supplies engine values,
conversions, and algorithms to the owned implementation class.

## Private computation inside a leaf implementation

A leaf implementation can use a private Sage value directly. This is not a kernel
defect.

For example, a finite-poset object can retain or construct a private Sage poset. Its
local methods can call exact Sage algorithms on that value.

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
- results in primitive or engine-shaped collections instead of owned mathematical
  collections.

Repeated access to one private representation does not alone justify a decorator,
descriptor, registry, or second class hierarchy.

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
- constructing an owned finite set, ordered set, subobject, or arrow;
- preserving the original ambient poset.

A Sage iterator is not an owned mathematical collection. A Python `int` is not
automatically the required owned nonnegative integer. A Sage subset is not an owned
subobject.

The method reconstructs the semantic result before returning.

The reconstruction remains explicit when different methods return different
mathematical kinds. A generic backend dispatcher cannot infer these roles from method
names.

## Realization functors and private representations

The word “realization” must distinguish two different notions.

### Mathematical realization functor

A realization functor is appropriate when the project models an actual mathematical
functor between categories. It has object and arrow maps and can be used explicitly.

Such a functor does not contribute methods through structural inheritance unless the
category deliberately selects it as a structural functor.

### Private computation representation

A private Sage parent, element, matrix, poset, or graph used inside one implementation
is not automatically a functor. It is implementation state.

It does not require:

- a category of engine implementations;
- an `ObjectType` parallel to the owned object type;
- a compiler binding;
- a method catalogue;
- natural transformations between backend method surfaces;
- a runtime engine registry.

Do not elevate a private representation into categorical structure only to dispatch
ordinary method calls.

## File placement

The default layout keeps the category declaration and its implementation classes
together. This gives the shortest path from mathematical owner to executable method.

When one implementation class becomes a substantial audit unit, split by mathematical
role:

```text
finite_posets.py
finite_poset_objects.py
finite_poset_elements.py
finite_poset_morphisms.py
```

The category declaration then links the sole implementation classes from those files.

This split does not create another implementation surface. `FinitePosetObject` remains
the only object implementation class.

Do not create one file per type automatically. A separate file must contain a
substantial coherent implementation unit.

Do not name the sole implementation class `SageFinitePosetObject`. Its mathematical
role is `FinitePosetObject`, even when Sage supplies every nontrivial algorithm.

## Private neighboring engine modules

A category can use a private neighboring engine module when the computation boundary
has substantial shared content:

```text
finite_posets.py
_finite_poset_sage.py
```

Prefer the concrete engine name. A generic name such as `finite_poset_engine.py`
suggests interchangeable engines and invites speculative dispatch infrastructure.

The private module can own:

- construction of the Sage representation;
- conversion to and from Sage elements;
- shared engine-native computation primitives;
- private representation caches;
- category-specific adaptation of a mature Sage algorithm.

It cannot own:

- public mathematical signatures;
- `ObjectType`, `ElementType`, or `ArrowType` alternatives;
- category membership or refinement decisions;
- public semantic result construction;
- operation documentation;
- compiler registration;
- a method-name map;
- runtime engine selection;
- a mirror of most public leaf methods.

The public leaf method calls the helper explicitly. It selects the algorithm and
constructs the owned result.

Category-independent Sage conversion primitives can live in the central Sage backend.
Category-specific computation remains beside its mathematical owner when that placement
improves local auditability.

There is no mandatory engine module for each category. Create one only when a real
shared computation boundary earns the file.

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

A private helper can own engine-specific conversion or raw computation. It does not
repeat the public contract.

The following shapes indicate a second source of truth:

- matching public and backend method lists;
- matching `ObjectType` and `SageObjectType` classes;
- operation decorators that store another callable;
- compiler tables from public names to engine names;
- duplicate method documentation in backend modules;
- public stubs paired with private executable methods;
- separate result-role declarations for one method.

If changing one mathematical operation requires synchronized edits to two method
catalogues, the architecture is wrong.

## Leaf, kernel, and backend responsibilities

| Concern | Owner |
| --- | --- |
| Category-local operation name and signature | `ObjectType`, `ElementType`, or `ArrowType` |
| Category-local executable method body | The same implementation class |
| Inherited method catalogue | Declaring structural ancestor |
| Structural route discovery | Kernel |
| Receiver and argument transport | Kernel |
| Result and collection reverse transport | Kernel |
| Canonical images and preimages | Kernel |
| Dynamic descriptor installation for inherited methods | Kernel |
| Choice of exact leaf algorithm | Leaf implementation method |
| Private lowering to Sage | Leaf implementation or private helper |
| Sage algorithm execution | Sage, called through the private boundary |
| Reconstruction of the owned result | Leaf implementation method |
| Generic Sage conversion shared by categories | Central Sage backend |
| Runtime backend registry or method matching | No owner; this is outside the design |

The kernel can contain complex Python machinery only for category-independent
structural inheritance. It does not become a universal operation dispatcher.

The backend can contain engine-specific machinery. It does not become a second
mathematical implementation hierarchy.

## The product algebra example

The discussion also corrected the treatment of \(R^n\).

The canonical object

\[
R^n=\prod_{i=1}^{n}R
\]

is constructed as a product of rings. Under the repository's commutative-base
convention, it is an \(R\)-algebra with coordinatewise operations and diagonal structure
map

\[
R\longrightarrow R^n,
\qquad
r\longmapsto(r,\ldots,r).
\]

It therefore has structural routes through both rings and modules:

\[
\operatorname{Algebras}(R)
\longrightarrow
\operatorname{Rings}
\longrightarrow
\operatorname{Sets},
\]

and

\[
\operatorname{Algebras}(R)
\longrightarrow
\operatorname{Modules}(R)
\longrightarrow
\operatorname{Sets}.
\]

Both routes reach the same underlying set:

\[
U(R^n)=U(R)\times\cdots\times U(R).
\]

The construction must retain the strongest structure that it establishes:

- product-ring operations;
- \(R\)-algebra operations;
- module operations;
- set operations;
- finite-set operations when \(R\) and the index set are finite.

The algebra does not add a direct structural functor to sets for convenience. Its set
surface arrives through the mathematically meaningful intermediate categories.

For \(R=\mathbf F_p\), the finite product belongs to finite rings and hence finite sets.
No exhaustive enumeration is required to establish finiteness.

An arbitrary module merely isomorphic to \(R^n\) needs a selected product presentation
before this coordinatewise algebra structure transfers to it. The canonical constructed
object \(R^n\) already has that presentation.

This example reinforces the leaf rule. A construction retains its mathematical
placement. A leaf does not flatten the result to a backend container or manually route
it to sets.

## Relation to structural diamonds

Structural diamonds preserve every branch. They resolve only duplicate access to a
common owner. See [resolution.md](resolution.md) for the complete decision.

For \(R^n\), the algebra-to-rings and algebra-to-modules routes introduce different
applicable operations. Both later reach `Sets()`. The kernel preserves both catalogues
and chooses one canonical underlying set image.

This structural transport does not dispatch the algebra's local methods to Sage. The
two mechanisms remain separate:

- category paths determine inherited operations;
- local method bodies determine computations introduced by the category.

A route diamond cannot justify a mirrored backend hierarchy. A backend representation
is not another structural ancestor.

## Method signatures remain mathematical

The computation boundary does not weaken public method signatures.

Do not write one method with an optional argument when the presence of that argument
selects a different mathematical operation. Use total named methods such as `rank()` and
`rank_of_element(member)`.

Do not accept `Iterable[PosetElement]` when the method requires a mathematical set,
ordered set, chain, or subobject. Use the exact owned collection type.

Do not return `Iterator[PosetElement]` when the result is a mathematical set of covers,
a linear extension, or an ordered family of level sets. Construct the named owned
mathematical collection. Private traversal inside the computation boundary can remain
lazy.

Backend APIs do not determine public types. The public type states the mathematical
input and result. The leaf method performs the required conversion privately.

## Required policy interpretation

Apply the repository policies with these meanings.

### “No engineering wiring in leaves”

This bans:

- route traversal;
- descriptor installation;
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

This means that no engine type, name, exception, or collection enters the public
contract. It does not mean that an executable implementation cannot mention its private
dependency.

### “Categories own operations”

Ownership includes the executable semantic method. It is not satisfied by a stub plus
a backend implementation elsewhere.

### “Kernel complexity removes leaf repetition”

This applies to structural inheritance repeated across categories. It does not authorize
a generic dispatcher for unrelated leaf algorithms.

### “Use mature algorithms”

The category-owned method calls the mature algorithm. It does not reimplement it. The
dependency remains a computation engine rather than a mathematical owner.

### “Realizations are functors”

This applies when the realization is an actual modeled mathematical functor. It does
not require every private engine value or algorithm call to enter the functor compiler.

## Acceptance conditions

A leaf implementation satisfies this specification when all these facts hold:

- the category declaration defines or links one `ObjectType`, one `ElementType`, and one
  `ArrowType`;
- those types contain the executable bodies of every locally owned public operation;
- local methods are ordinary methods without computation-routing decorators;
- no local method is an `assert False` declaration stub;
- inherited methods arrive only through selected structural functors;
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
- structural diamonds preserve all branch-owned operations and one canonical common
  image;
- a mathematician can find the executable operation from its category-owned
  implementation class without understanding compiler dispatch.

The short form is:

> The category-owned type is the implementation. The kernel supplies inheritance. Sage
> supplies computation. No fourth surface connects them.
