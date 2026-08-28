# Magmas, monoids, and semirings

This specification defines algebraic objects in a supplied ambient category.
The current implementation milestone remains `Sets()` and its universal constructions.
These algebraic categories are vertical acceptance targets for that foundation.

The governing policies are `POL-MATH-019`, `POL-MATH-022`, `POL-MATH-023`, `POL-GEN-001`, `POL-GEN-016`, `POL-GEN-017`, `POL-GEN-020`, `POL-GEN-021`, `POL-CAT-027`, `POL-CAT-030`, `POL-CAT-031`, and `POL-DOC-003` through `POL-DOC-009`.

## Contents

- [Ambient categorical data](#ambient-categorical-data)

- [Magmas](#magmas)

- [Additive and multiplicative forms](#additive-and-multiplicative-forms)

- [Monoids](#monoids)

- [Groups](#groups)

- [Semirings](#semirings)

- [Selected functors](#selected-functors)

- [Owned operations](#owned-operations)

- [Laws in the supplied ambient](#laws-in-the-supplied-ambient)

- [Definition sources](#definition-sources)

- [Acceptance conditions](#acceptance-conditions)

## Ambient categorical data

The ambient is a parameter of every definition below.
`Magmas(V)`, `Monoids(V)`, `Groups(V)`, and `Semirings(C)` are the general notions.
Fixing the parameter gives an instance.
`Monoids(Sets())` gives ordinary monoids.
`Monoids(Cat())` gives strict monoidal categories.
Neither instance is the definition, and neither is a specialization of the other.

Let `V` be a category `C` with a selected tensor bifunctor

\[
\mathbin{\otimes}:C\times C\longrightarrow C.
\]

`Magmas(V)` requires this bifunctor.
`Monoids(V)` requires a selected monoidal extension

\[
(C,\mathbin{\otimes},I,a,\lambda,\rho).
\]

The structured argument `V` retains `C` and all selected ambient structure.
Two tensor or monoidal structures on one underlying category give different values of `V` and therefore different magma and monoid categories.

The internal semiring construction uses finite products.
Write `C_x` for the specified cartesian monoidal category `(C, product, 1)`. Then `Semirings(C)` uses `Monoids(C_x)` for both of its monoid structures.
It does not select another monoidal structure carried by the same underlying category.
`Semirings(Sets())` gives ordinary semirings.

The definitions use morphisms and commutative diagrams in `C`. They remain meaningful when `C` has no element-based description.

## Magmas

An object of `Magmas(V)` is an object `X in C` with a chosen multiplication morphism

\[
\mu_X:X\otimes X\longrightarrow X.
\]

A morphism from `(X, mu_X)` to `(Y, mu_Y)` is a morphism `f:X -> Y` in `C` such that

\[
f\circ\mu_X=\mu_Y\circ(f\otimes f).
\]

`Magmas(V)` is the category of these objects and morphisms.
Its defining presentation retains `X`, `mu_X`, and their endpoint equation.
`Magmas(V)` presents its objects as pairs, so the selected functor to `C` is the
first product projection, whose index names it and whose codomain is fixed by the
product:

```python
def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
    return (self.product_projection(0),)
```

The projection to the multiplication morphism remains an ordinary retained functor.
It does not contribute the morphism category's public method surface.

`mu_X` is a morphism out of a tensor product.
It presents no diagram and carries no cone, injection, or projection.
An object with a magma structure needs no product or coproduct construction of its own.
Every multiplication morphism below has this form.

At `V = Sets()` with the cartesian product, an object is a set with a binary operation: an ordinary magma.
At `V = Cat()` with the cartesian product, an object is a category `X` with a functor

\[
\mu_X:X\times X\longrightarrow X,
\]

and no law.

The constructor receives or defines `mu_X`.
The specification does not prescribe its private storage.
The public surface has no generic `operation()` or `combine()` alias.
The fixed-endpoint magma-morphism category owns the operation-preservation containment predicate.
The kernel derives its standard property application.

## Additive and multiplicative forms

The two notation subcategories are

```python
Magmas(V).Additive()
Magmas(V).Multiplicative()
```

They retain the same underlying object, multiplication morphism, and morphisms.
The additive subcategory exposes `+` on points.
The multiplicative subcategory exposes `*` on points.
Their complete immediate structural tuples are

```python
# Magmas(V).Additive()
def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
    return (Fun(self, Magmas(V)).Monomorphisms().Isofibrations().Full()(),)
```

```python
# Magmas(V).Multiplicative()
def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
    return (Fun(self, Magmas(V)).Monomorphisms().Isofibrations().Full()(),)
```

For cartesian `V`, two generalized elements `x,y:T -> X` combine through

\[
T\xrightarrow{\Delta_T}T\times T
 \xrightarrow{x\times y}X\times X
 \xrightarrow{\mu_X}X.
\]

This diagram is the generalized-element meaning of the syntax.
When `T` is terminal, `x` and `y` are points and the result is an actual element.
For `C = Sets()`, this gives the usual binary operation on elements.

When `V` is braided monoidal, `Magmas(V).Commutative()` is defined by equality of `mu_X` and its composite with the braiding on `X tensor X`. It propagates to both notation subcategories through property inverse image.

## Monoids

An object of `Monoids(V)` is an object `X in C` with morphisms

\[
\mu_X:X\otimes X\longrightarrow X,
\qquad
\eta_X:I\longrightarrow X.
\]

The associativity diagram uses the associator `a` of `V`. The unit diagrams use `lambda` and `rho`. A monoid morphism preserves both `mu` and `eta`.

This is the standard monoid-object construction in a monoidal category.

At `V = Sets()` with the cartesian product, an object is an ordinary monoid.
At `V = Cat()` with the cartesian product, the associator and the unitors are identities, so the associativity and unit diagrams become equalities of functors.
An object is then a strict monoidal category: a category `X` with a chosen object `I in X` and a functor `mu_X: X * X -> X` for which

\[
(A\otimes B)\otimes C=A\otimes(B\otimes C),
\qquad
I\otimes A=A=A\otimes I,
\]

and the matching three equations on morphisms of `X`.

Its immediate selected functor forgets associativity and the unit:

```python
def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
    return (Fun(self, Magmas(V)).Monomorphisms().Isofibrations()(),)
```

The constructor receives or defines `mu_X` and `eta_X`.
The notation-neutral category exposes the unit morphism:

```python
M.unit_morphism()
```

`unit_morphism()` returns `eta_X:I -> X`.
It is a point only when `I` is terminal.

The notation subcategories are

```python
Monoids(V).Additive()
Monoids(V).Multiplicative()
```

They are inverse images of the matching `Magmas(V)` subcategories.
Their complete immediate structural tuples preserve both category branches:

```python
# Monoids(V).Additive()
def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
    return (
        Fun(self, Monoids(V)).Monomorphisms().Isofibrations().Full()(),
        Fun(self, Magmas(V).Additive()).Monomorphisms().Isofibrations()(),
    )
```

```python
# Monoids(V).Multiplicative()
def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
    return (
        Fun(self, Monoids(V)).Monomorphisms().Isofibrations().Full()(),
        Fun(self, Magmas(V).Multiplicative()).Monomorphisms().Isofibrations()(),
    )
```

When `V` is cartesian, the additive form names the unit point `zero()` and the multiplicative form names it `one()`.

`Monoids(V).Additive().Commutative()` denotes commutative additive monoid objects.
The matching multiplicative expression denotes commutative multiplicative monoid objects.

## Groups

When `V` is cartesian monoidal, `Groups(V)` is the full property subcategory of `Monoids(V)` on objects with an inversion morphism

\[
\iota_X:X\longrightarrow X
\]

that satisfies the left and right inverse diagrams.
A monoid morphism between group objects preserves inversion.
The additive form `Groups(V).Additive()` exposes unary `-` and subtraction.
The commutative additive group category is `Groups(V).Additive().Commutative()`.

Its complete immediate structural tuple is

```python
def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
    return (Fun(self, Monoids(V)).Monomorphisms().Isofibrations().Full()(),)
```

The selected functor supplies the multiplication morphism and unit data required by the monoid constructor.
`Groups(V)` adds only the inversion morphism and its laws.

At `V = Sets()`, an object is an ordinary group.
At `V = Cat()`, an object is a strict 2-group: a category `X` whose multiplication, unit, and inversion are functors and whose group laws are equalities of functors.
The cartesian hypothesis is not cosmetic.
The unit and inverse diagrams use the diagonal `Delta_X`, which a general monoidal ambient does not supply.

## Semirings

Let `C` have finite products.
A strict internal semiring object in `C` consists of one object `X in C` with:

- a commutative additive monoid structure on `X`;

- a multiplicative monoid structure on `X`;

- left and right distributivity diagrams;

- left and right zero-absorption diagrams.

Both monoid structures use the cartesian product of `C`. Addition and multiplication are morphisms `X * X -> X`, in the sense stated under [Magmas](#magmas).
A semiring morphism is a morphism in `C` that preserves both structures.

At `C = Sets()`, an object is an ordinary semiring.
At `C = Cat()`, an object is a category `X` with two functors

\[
\alpha,\mu:X\times X\longrightarrow X,
\]

two functors `1 -> X` that select the zero object and the one object, and every law an equality of functors.
`Cardinal()` and `Ordinals()` are the objects of `Semirings(Cat())` that this package constructs; see [Cardinalities and ordinals](cardinality.md) and [Ordinals](ordinals.md).

The strict internal category is the subcategory of `Monoids(C_x).Additive().Commutative() * Monoids(C_x).Multiplicative()` whose two underlying objects agree and whose distributivity and absorption diagrams commute.
Its defining presentation retains both component projections.

The complete immediate structural tuple is

```python
def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
    return (
        self.product_projection(0),
        self.product_projection(1),
    )
```

Both paths supply the same constructor datum for the underlying object of `C`. The structural diamond supplies both additive and multiplicative element interfaces.

`Semirings(C)` owns the compatibility laws and the combined additive and multiplicative surface.
Its object interface exposes both unit points.
Its point interface exposes `+` and `*` through the two retained monoid structures.

```python
X.zero()
X.one()
x + y
x * y
```

Here `X in Semirings(C)`. The points `x` and `y` have a common domain on which the addition and multiplication morphisms can act.
At `C = Cat()`, `X` is a category, `zero()` and `one()` return objects of `X`, and the two operators apply its addition and multiplication functors.

For `C = Sets()`, the diagrams give the familiar formulas

\[
x(y+z)=xy+xz,
\qquad
(x+y)z=xz+yz,
\qquad
0x=0=x0.
\]

These formulas are consequences of the internal diagrams.

## Selected functors

Each selected functor acts on objects and morphisms.
Its point action comes from its morphism action and terminal-object comparison.

The additive and multiplicative refinements use subcategory monomorphisms.
The semiring component functors come from the generic subobject-of-product construction.
Longer routes to `C` arise through the projections of `C_x`.

## Owned operations

| Category | New public mathematics |
| --- | --- |
| `Magmas(V)` | Operation-preservation predicate on morphisms. |
| `Magmas(V).Additive()` | `+` on points. |
| `Magmas(V).Multiplicative()` | `*` on points. |
| `Monoids(V)` | Associativity, unit laws, and unit-preserving morphisms. |
| `Monoids(V).Additive()` | `zero()` when the monoidal unit is terminal. |
| `Monoids(V).Multiplicative()` | `one()` when the monoidal unit is terminal. |
| `Groups(V)` | Inversion and the inverse laws. |
| `Groups(V).Additive()` | Unary `-` and subtraction. |
| `Semirings(C)` | Distributivity, absorption, and both selected monoid structures. |

Inherited capabilities come from the listed selected functors.
Each defining predicate returns its owned proposition.

## Laws in the supplied ambient

Every law above is an equation between morphisms of the supplied ambient category.
No instance weakens a law to an isomorphism, and no instance replaces a law by a coherence datum.

At `C = Sets()` the morphisms are maps, so each law is an equality of maps.
At `C = Cat()` the morphisms are functors, so each law is an equality of functors.
This is why `Monoids(Cat())` gives strict monoidal categories and not monoidal categories.

`Cardinal()` and `Ordinals()` satisfy the equalities at `C = Cat()` because both are skeletal.
Addition and multiplication each select one representative, so `(a + b) + c` and `a + (b + c)` name one object.

`Rings(C)` uses the same rule; see [Ring objects](rings.md).

## Definition sources

The magma-object definition follows the [nLab magma](https://ncatlab.org/nlab/show/magma) entry, section "Definitions": "for M a monoidal category, a magma structure on X is a morphism m: X (x) X -> X". `Magmas(V)` requires only the selected bifunctor of `V`, which is what that morphism needs.

The monoid-object definition and its associativity and unit diagrams follow the [nLab monoid in a monoidal category](https://ncatlab.org/nlab/show/monoid%2Bin%2Ba%2Bmonoidal%2Bcategory) entry, section "Definition": "a monoid in C is an object M equipped with a multiplication mu : M (x) M -> M and a unit eta : I -> M satisfying the associative law", together with the left and right unit laws stated there.
The same entry's "Idea" section fixes the `Sets()` instance: "Classical monoids are of course just monoids in Set with the cartesian product."

The `Cat()` instance follows the [nLab monoidal category](https://ncatlab.org/nlab/show/monoidal%2Bcategory) entry, section "Strict monoidal categories": "A strict monoidal category is equivalently a monoid in the cartesian monoidal 1-category Cat of categories and functors".
The same section lists the six equations that this makes explicit.

The commutativity condition follows the [nLab commutative monoid in a symmetric monoidal category](https://ncatlab.org/nlab/show/commutative%2Bmonoid%2Bin%2Ba%2Bsymmetric%2Bmonoidal%2Bcategory) entry, section "Definition": a monoid `(A, mu, e)` is commutative when `mu` composed with the braiding `tau_{A,A}` equals `mu`.

The group-object definition follows the [nLab group object](https://ncatlab.org/nlab/show/group%2Bobject) entry, section "Definition / In a cartesian monoidal category": an object `G` with `m: G x G -> G`, `e: * -> G`, and inversion `G -> G` whose associativity, unitality, and inverse diagrams commute.
Its "Examples" section fixes both instances: "A group object in Sets is a group" and "A group object in Cat is a strict 2-group".
Its remark that the diagrams use the diagonal states why `Groups(V)` requires cartesian `V`.

The strict internal semiring pattern uses the finite-product form of the [nLab ring object](https://ncatlab.org/nlab/show/ring%2Bobject) entry, section "Definition / Traditional definition": "a ring object consists of an object R in a cartesian monoidal category C together with morphisms a : R x R -> R (addition), m : R x R -> R (multiplication), 0 : 1 -> R (zero), e : 1 -> R (multiplicative identity), - : R -> R (additive inversion), subject to commutative diagrams in C that express the usual ring axioms".
A semiring object drops the additive inversion and keeps the four conditions that the same entry lists in section "Definition / Via the microcosm principle": a commutative additive monoid, a multiplicative monoid, the distributivity diagrams, and the diagrams "corresponding to the rig axioms 0a = 0 and a0 = 0".

That microcosm definition uses a bimonoidal ambient, where the two operations come from the ambient's own two monoidal structures.
It is a different construction, and the same entry states its `Cat` case separately: "A rig in (Cats, ∐,×, ∅_(cat), pt) is a strict monoidal category".
`Semirings(C)` instead takes both monoid structures over the finite products of `C`, as the traditional definition does, so both operations come from the underlying object.

The notation subcategories use the Sage reference sections for [magmas](https://doc.sagemath.org/html/en/reference/categories/sage/categories/magmas.html) ("A magma is a set with a binary operation"), [additive monoids](https://doc.sagemath.org/html/en/reference/categories/sage/categories/additive_monoids.html), [monoids](https://doc.sagemath.org/html/en/reference/categories/sage/categories/monoids.html), [groups](https://doc.sagemath.org/html/en/reference/categories/sage/categories/groups.html) ("The category of (multiplicative) groups, i.e. monoids with inverses"), and [semirings](https://doc.sagemath.org/html/en/reference/categories/sage/categories/semirings.html) ("it is a combination of a commutative additive monoid (S, +) and a multiplicative monoid (S, *), where * distributes over +").

## Acceptance conditions

- `Magmas(V)` retains the selected tensor bifunctor of `V`.

- `Monoids(V)` retains the selected monoidal structure of `V`.

- `Groups(V)` uses the selected cartesian monoidal structure of `V`.

- Their objects and morphisms live in the underlying category `C`.

- Every algebraic law is a diagram in `C`.

- `Semirings(C)` uses `C_x`, the specified cartesian monoidal structure on `C`.

- Both semiring component routes reach one canonical object of `C`.

- Every immediate structural edge is an owned functor.

- Deeper inherited operations arrive through functor composition.

- Each multiplication morphism has domain a tensor or cartesian product.

- Every law is an equation between morphisms of the supplied ambient.

- `Monoids(Sets())` gives ordinary monoids; `Monoids(Cat())` gives strict monoidal categories.

- `Groups(Sets())` gives ordinary groups; `Groups(Cat())` gives strict 2-groups.

- `Semirings(Sets())` gives ordinary semirings; `Semirings(Cat())` states its laws as equalities of functors.

The complete governing set also includes `POL-MATH-001` through `POL-MATH-013`, `POL-MATH-034`, `POL-MATH-035`, `POL-CAT-001` through `POL-CAT-020`, `POL-CAT-033`, `POL-CAT-043` through `POL-CAT-047`, `POL-CAT-054`, `POL-CAT-061` through `POL-CAT-087`, `POL-FUN-001` through `POL-FUN-006`, `POL-FUN-023`, and `POL-DOC-003` through `POL-DOC-009`.
