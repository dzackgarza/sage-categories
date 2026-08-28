# Dynamic class resolution and structure functors

This specification defines how structure functors contribute Python inheritance.
It also separates that compiler use from the mathematical meaning of a functor.

## Structure functors replace `super_categories()`

For a category `C`, `C.structure_functors()` returns ordinary functors with domain `C`.
The kernel uses their target classes as dynamic bases for `C.ObjectType`, `C.ElementType`,
and `C.MorphismType`.

This is the replacement for Sage's use of `super_categories()` as input to its dynamic
category classes. It fixes the Sage problem that a supercategory edge combines two facts:
a mathematical relation between categories and a request for inherited implementation.
This repository states the implementation relation with a structure functor.

A structure functor can be:

- a forgetful functor;

- a projection from a category of structured objects;

- a fibration;

- a subcategory monomorphism;

- another ordinary functor whose target classes supply inherited implementation.

Returning `F: C -> D` from `C.structure_functors()` does not assert that `C` is a
subcategory of `D`. It does not assert that `C` is "`D` with more structure."
A subcategory relation exists only through its declared monomorphism.

## Exact compiled classes

A category specifies these exact nested classes:

- `C.ObjectType`;

- `C.ElementType`;

- `C.MorphismType`.

The kernel constructs each named class dynamically. For an immediate structure functor
`F: C -> D`, the corresponding class of `D` is a dynamic base of the class of `C` when
`F` supplies that mathematical kind.

The result is still `C.ObjectType`, `C.ElementType`, or `C.MorphismType`. It is not an
unnamed implementation class and not a second class passed into the category.

## C3 owns diamonds

The compiled classes follow Sage's dynamic-class model and Python C3 linearization.
For a graph

\[
D\longrightarrow B\longrightarrow A,
\qquad
D\longrightarrow C\longrightarrow A,
\]

the classes contributed by `B` and `C` both remain in the MRO. The shared class from `A`
occurs once. Cooperative initialization runs that class once.

The kernel does not:

- enumerate complete functor paths to `A`;

- construct one candidate datum for each path;

- compare constructor conversions or constructor data from different paths;

- decide equality to establish inheritance coherence;

- select one path as the owner of the shared class.

There is no second diamond-resolution system beside Sage dynamic classes and Python C3.

## Constructor conversions

Each structure functor retains the pure conversion that supplies the data required by its
target constructor. The kernel uses the immediate structure functors and the C3 MRO to
initialize the compiled source instance.

Each local constructor initializes only the state introduced by its category. It calls
`super().__init__()` cooperatively. A leaf does not accept ancestor constructor fields,
traverse functor paths, compare path data, or manage inherited state itself.

The target method then runs by ordinary attribute lookup on the original source instance.
It reads the target state carried by that instance. Python special methods follow the same
rule.

## Public functor images remain separate

Dynamic inheritance and functor application are different operations.

For a named functor `F: C -> D`, `F.on_object(x)` constructs the object of `D` defined by
`F`. The functor owns and caches that public image. Two named functors with the same
endpoints can construct different images.

An inherited method does not call `F.on_object(x)`. It runs on `x` through the compiled
MRO. Thus Python inheritance does not identify `x` with `F(x)` and does not establish
categorical containment.

The kernel never merges public functor images by identity, set equality, or constructor
data equality.

## Method ownership and collisions

A method introduced by one branch remains available in the compiled class. A method owned
by a shared ancestor appears once because that ancestor class appears once in the C3 MRO.

Local declarations win over inherited declarations. One declaring category reached through
several branches remains one method owner. If unrelated declaring categories use one public
name for different mathematical operations, the declarations conflict. Route order does not
resolve that conflict.

## Universal constructions are not class diamonds

Two diagrams can construct isomorphic apexes with different projections, injections, cones,
or cocones. Those presentations remain distinct mathematical construction data. Python C3
does not identify them, and the compiler does not compare them.

A selected construction retains its own diagram and universal morphisms. Another presentation
remains an ordinary construction or is related by an explicit morphism or isomorphism.

## Acceptance examples

The kernel acceptance suite must establish these facts for objects, elements, and morphisms:

1. `C.ObjectType`, `C.ElementType`, and `C.MorphismType` are the dynamic classes constructed
   from the immediate structure-functor targets.

2. A forgetful structure functor supplies inherited methods without asserting a subcategory
   relation.

3. A declared subcategory monomorphism can also serve as a structure functor, with its
   categorical meaning retained independently of compiler selection.

4. Both branches of a dynamic-class diamond contribute their local methods.

5. A shared target class occurs once in the C3 MRO and initializes once.

6. Construction performs no equality call and no comparison of path-specific constructor
   data.

7. A public call to a named functor returns its separate image, while an inherited method
   runs on the original source instance.

8. Unrelated declarations with one public name fail as a semantic collision.

The same rules apply to `ObjectType`, `ElementType`, and `MorphismType`.
