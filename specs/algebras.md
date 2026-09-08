# Algebra objects

This specification defines algebras over a supplied base object and ambient category.
The initial executable boundary is [minimal leaf scaffolding](leaf-scaffolding.md).

The governing policies are `POL-MATH-019`, `POL-MATH-022`, `POL-MATH-023`, `POL-GEN-001`, `POL-GEN-019`, `POL-GEN-020`, `POL-CAT-027`, `POL-CAT-030`, `POL-CAT-031`, and `POL-DOC-003` through `POL-DOC-009`.

## Ambient categorical data

Fix a base monoid object `R` and an ambient category `C` for which `Modules(R, C)` has a selected monoidal structure

\[
(\operatorname{Modules}(R,C),\mathbin{\otimes_R},I_R).
\]

The tensor product, unit object, associator, and unitors are part of the supplied module-category data.
Write `V_R` for `Modules(R, C)` with this selected monoidal structure.
The public constructor is

```python
Algebras(R, C)
```

Mathematically, its objects are monoid objects in `V_R`. This applies the monoid-object construction to `Modules(R, C)`. The definition of a monoid object is stated once, in [Monoids](magmas-monoids-semirings.md#monoids); this specification adds only the base relative placement.

The [nLab monoid in a monoidal category](https://ncatlab.org/nlab/show/monoid%2Bin%2Ba%2Bmonoidal%2Bcategory) entry, section "Examples", names the resulting objects: "A monoid in a monoidal category of modules RMod (over any ground ring R and equipped with the tensor product of modules) is an associative unital algebra over R."

For any selected monoidal category `V`, `Monoids(V)` is the public general monoid-object construction.
`Algebras(R, C)` is the base-relative presentation category obtained by applying that construction to `V_R`. Its retained presentation functor to `Monoids(V_R)` is an equivalence.
The general monoid category owns the multiplication, unit, and monoid laws.

For a commutative `R` in a symmetric monoidal setting, the usual relative tensor product supplies the monoidal structure on left `R`-module objects.
The constructor applies only when this monoidal structure is supplied.
A noncommutative base instead requires the monoid-object construction in a supplied monoidal category of `R`-bimodule objects under relative tensor product.
That ambient and its balancing maps are specified in [Bimodule objects](bimodules.md).
The public-name distinction from endofunctor algebras is fixed by the [scaffolding boundary](leaf-scaffolding.md#public-names-and-implementation-boundary).

## Objects

An object of `Algebras(R, C)` is a module object `B in Modules(R, C)` with morphisms

\[
m_B:B\otimes_R B\longrightarrow B,
\qquad
u_B:I_R\longrightarrow B
\]

in `Modules(R, C)`. The associativity and unit diagrams use the associator and unitors of the selected monoidal module category.

In the ordinary commutative-ring case, `I_R` is the regular module `R`. Then `u_B:R -> B` is the usual scalar structure morphism.

## Morphisms

An algebra morphism `f:B -> D` is a morphism in `Modules(R, C)` that preserves `m` and `u`:

\[
f\circ m_B=m_D\circ(f\otimes_R f),
\qquad
f\circ u_B=u_D.
\]

Thus every algebra morphism is already a module morphism in the supplied module category.

## Structure functor

The construction retains its base-relative presentation functor

\[
P_R:\operatorname{Algebras}(R,C)\longrightarrow\operatorname{Monoids}(V_R).
\]

The complete immediate structure-functor tuple is

```python
def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
    return (self.monoid_presentation(),)
```

`monoid_presentation()` is the retained object of `Fun(Algebras(R, C), Monoids(V_R)).Equivalences()` created by the algebra construction.
The module object is the image under the named composite `U_R := U_{Modules} after U_{Magmas} after U_{Monoids} after monoid_presentation()`, whose factors are:

\[
\operatorname{Algebras}(R,C)
\longrightarrow \operatorname{Monoids}(V_R)
\longrightarrow \operatorname{Magmas}(V_R)
\longrightarrow \operatorname{Modules}(R,C)
\longrightarrow C.
\]

## Owned operations

`Algebras(R, C)` owns the base-relative placement and its scalar-change functors.
`Monoids(V_R)` owns `operation()`, `unit_morphism()`, associativity, and the unit laws.
The named copy `MultiplicativeMonoids(V_R)` supplies `multiplication()`, `*`, and `one()` ([Named operations](magmas-monoids-semirings.md#named-operations)). The defining morphisms remain constructor data.

The module action and every operation owned by `C` arrive along `U_R`. No algebra constructor repeats those operations, and no accessor stands in for the composite (`POL-FUN-037`).

The same Python realization in `Algebras(R, C)` and `Algebras(S, C)` represents different algebra objects when the scalar structure morphisms differ.
Scalar change is a functor between these categories.

## Instances

An instance needs the supplied monoidal structure `V_R`, not an ambient category alone.

At `R` a commutative ring and `C = Ab` with the relative tensor product, an object is an ordinary associative unital `R`-algebra.
Sage's [`Algebras`](https://doc.sagemath.org/html/en/reference/categories/sage/categories/algebras.html) names the same objects: "The category of associative and unital algebras over a given base ring.
An associative and unital algebra over a ring R is a module over R which is itself a ring."

At `R = ZZ` the module category is `Ab` itself, and the same nLab "Examples" section gives the instance: "A monoid object in the monoidal category Ab of abelian groups with the tensor product of abelian groups, is a ring."

There is no algebra object in `Cat()`. The construction needs `Modules(R, Cat())`, which first needs a monoidal `M`, a left `M`-action on `Cat()`, and `R in Monoids(M)` ([Instances](modules.md#instances)), and then a monoidal structure on that module category.
Naming `Cat()` supplies none of these.

## Relation to module objects

The algebra construction starts only after the selected module category has a monoidal structure.
An actegory action by itself supplies `Modules(R, C)` through `R bullet X -> X`. The additional relative tensor product and its coherence data supply the monoid-object construction used by `Algebras(R, C)`.

The module action contract is stated once, in [Module objects](modules.md#objects-and-action-laws).

## Finite presentation and the underlying module

Finite generation and finite presentation must name the category in which they
hold. Neither property for an `R`-algebra establishes finite generation of its
underlying `R`-module.

For a nonzero commutative ring `R`, the free associative unital algebra `R<x,y>`
has two algebra generators and no additional relations. Its underlying module is
free on all finite words in `x,y`, including the empty word. There are infinitely
many such basis words, so this module has infinite rank. Each algebra element is a
finite linear combination of words; no global bound on word length follows.
Sage's [free algebra documentation, `monoid()`, `one_basis()`, and `product_on_basis()`](https://doc.sagemath.org/html/en/reference/algebras/sage/algebras/free_algebra.html)
specifies this native basis and multiplication.

The named functor through `Monoids(V_R)` and `Magmas(V_R)` into `Modules(R, C)`
must retain that entire module. It must not replace it by the span of the two
algebra generators, a fixed degree truncation, or a finite-dimensional quotient.
Multiplication and induced morphisms operate on supplied words of arbitrary finite
length through the native engine; leaf code implements no duplicate word algebra.

An acceptance consumer follows this functor and the inherited module action on
words of degree greater than one, checks exact multiplication, and compares with
the algebra morphism induced by chosen generator images. For instance, substitution
`x |-> x+y`, `y |-> y` sends `x*y` to `x*y+y*y`. Such evaluation must retain the
full target algebra and its module, without choosing a degree cutoff. The
[module contract](modules.md#size-and-coordinate-presentations) owns the general
distinction between finite support and finite rank.

## Acceptance conditions

- `Algebras(R, C)` retains the selected monoidal structure on `Modules(R, C)`.

- An instance names `V_R`; an ambient category alone selects no instance.

- The underlying object of an algebra is a module object in that supplied category.

- The free finitely presented algebra consumer retains its infinite rank underlying
  module and exact multiplication and induced maps on finite expressions of
  unrestricted degree.

- Multiplication and unit are morphisms in the module category.

- Algebra morphisms preserve both structure morphisms.

- The equivalence to `Monoids(V_R)` is the sole immediate structure functor.

- The route to `C` passes through `Monoids(V_R)`, `Magmas(V_R)`, and `Modules(R, C)`.

- A noncommutative-base construction supplies a monoidal category of `R`-bimodule objects.

The complete governing set also includes `POL-MATH-001` through `POL-MATH-013`, `POL-MATH-020` through `POL-MATH-023`, `POL-CAT-001` through `POL-CAT-020`, `POL-CAT-033`, `POL-CAT-043` through `POL-CAT-047`, `POL-CAT-054`, `POL-CAT-061` through `POL-CAT-087`, `POL-FUN-001` through `POL-FUN-006`, `POL-FUN-023`, `POL-GEN-001` through `POL-GEN-010`, and `POL-DOC-003` through `POL-DOC-009`.
