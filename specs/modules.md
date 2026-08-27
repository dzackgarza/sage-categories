# Module objects

This specification defines module objects through an action of a monoidal category.
The current implementation milestone remains `Sets()` and its universal constructions.
Module objects are a later vertical acceptance target for that foundation.

The governing policies are `POL-MATH-019`, `POL-MATH-022`, `POL-MATH-023`,
`POL-GEN-001`, `POL-GEN-018`, `POL-GEN-020`, `POL-CAT-027`, `POL-CAT-030`,
`POL-CAT-031`,
and `POL-DOC-003` through `POL-DOC-009`.

## Ambient categorical data

Fix the following data:

- a monoidal category `(M, tensor, I)`;
- a category `C` with a selected left `M`-action
  `bullet: M * C -> C`;
- the associativity and unit coherence isomorphisms for that action;
- a monoid object `A in Monoids(M)` with multiplication `mu` and unit `eta`.

The category `C` with this data is a left `M`-actegory.
The public constructor is

```python
Modules(A, C)
```

The call supplies `C` explicitly.
The category of `A` determines `M`, while the selected actegory data determines
how `A` acts on objects of `C`.
Two actions on the same underlying category give different module categories.

The four items above are the parameters of the definition. No ambient category supplies
them by itself.

The same-category case follows the
[nLab module object](https://ncatlab.org/nlab/show/module%2Bobject) entry, section
"Definition": "Given a monoidal category (C, (x), 1), and given (A, mu, e) a monoid in
(C, (x), 1), then a left module object in (C, (x), 1) over (A, mu, e) is an object N in
C and a morphism rho : A (x) N -> N (called the action)" with the stated unitality and
action-property diagrams.

The form used here is the same entry's section "Definition / Generalisation": "Given a
monoidal category (M, o, 1) and an M-module (also called M-actegory) C (supported by the
monoidal action . : M x C -> C), and given (A, mu, e) a monoid in (M, o, 1), then a left
module object in C over (A, mu, e) is an object N in C and a morphism rho : A . N -> N".
Its unitality diagram uses the unitor of `bullet` and its action property uses the actor
of `bullet`.

## Objects and action laws

An object of `Modules(A, C)` is an object `X in C` with an action morphism

\[
\rho_X:A\mathbin{\bullet}X\longrightarrow X.
\]

Associativity is equality of these two composites:

\[
(A\otimes A)\bullet X
 \xrightarrow{\mu\bullet X}
A\bullet X
 \xrightarrow{\rho_X}
X,
\]

and

\[
(A\otimes A)\bullet X
 \xrightarrow{a_{A,A,X}}
A\bullet(A\bullet X)
 \xrightarrow{A\bullet\rho_X}
A\bullet X
 \xrightarrow{\rho_X}
X.
\]

Unitality is equality of these two morphisms from `I bullet X` to `X`:

\[
I\bullet X
 \xrightarrow{\eta\bullet X}
A\bullet X
 \xrightarrow{\rho_X}
X,
\qquad
I\bullet X\xrightarrow{\lambda_X}X.
\]

These diagrams define the module object without reference to elements.

## Morphisms

A morphism `f:(X, rho_X) -> (Y, rho_Y)` in `Modules(A, C)` is a morphism
`f:X -> Y` in `C` such that

\[
f\circ\rho_X=\rho_Y\circ(A\bullet f).
\]

Composition and identities come from `C`.
The action-preservation equation is stable under both.

## Structural functor

The construction retains the faithful carrier projection

\[
U_A:\operatorname{Modules}(A,C)\longrightarrow C.
\]

It sends `(X, rho_X)` to `X` and sends each module morphism to its morphism in `C`.
The complete immediate structural tuple is

```python
def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
    return (self.carrier_projection(),)
```

`carrier_projection()` is the retained object of
`Fun(Modules(A, C), C).Faithful()` created by the module construction.
It supplies the complete public surface owned by `C`.

## Owned operations

`Modules(A, C)` owns the action morphism and the action-preservation predicate.
Its object surface includes

```python
X.action()
```

`action()` returns `rho_X` in `Mor(C)(A bullet X, X)`.
At compatible point domains, scalar action evaluates this morphism through the
selected actegory action.

All other capabilities come through the selected functor to `C` or through later
property subcategories of `Modules(A, C)`.

## Closed and enriched presentation

Assume the actegory is enriched and tensored over `M`.
Assume it has an internal endomorphism object
`End_C(X) in M` with the required tensor-hom adjunction.
Then the action morphism adjoints to a monoid morphism

\[
A\longrightarrow \operatorname{End}_C(X)
\]

in `M`.
This is the closed or enriched presentation of the same module action.
The action morphism `A bullet X -> X` remains the definition under the weaker
actegory hypotheses.

For ordinary left modules over a ring `R`, take `M = Ab`, regard `R` as a monoid
object under tensor product, and use the standard `Ab`-action on `Ab`.

## Instances

An instance needs all four parameters. Naming one ambient category does not select them.

At `M = Ab` with the tensor product of abelian groups, `C = Ab` with the standard
action, and `A = R` a ring, an object is an ordinary left `R`-module. Sage's
[`Modules`](https://doc.sagemath.org/html/en/reference/categories/sage/categories/modules.html)
names the same objects: "The category of all modules over a base ring R."

There is no module object in `Cat()` until `M`, the left `M`-action on `Cat()`, and
`A in Monoids(M)` are supplied. Taking `M = Cat()` with its finite products, `Cat()`
acting on itself by product, and `A` a strict monoidal category gives objects that are
categories `X` with a functor `A x X -> X` whose unit and action laws are equalities of
functors.

The coherent version of that data is a different construction. The
[nLab module object](https://ncatlab.org/nlab/show/module%2Bobject) entry, section
"Examples", records it: "The notion of coherent action object in the 2-category Cat (of
categories with functors and natural transformations) is a categorified notion of
'action' (namely of monoidal categories), known as module categories (also:
'actegories')." Those laws hold up to coherent isomorphism, not as equalities of
functors, so they are not module objects in the ordinary category `Cat()`.

## Acceptance conditions

- `Modules(A, C)` retains `A`, `C`, and the selected `M`-action.
- An instance names `M`, the action, and `A`; an ambient category alone selects no
  instance.
- `A` is a monoid object of the acting monoidal category `M`.
- A module carrier is an object of the supplied category `C`.
- The action is a morphism `A bullet X -> X` in `C`.
- Module morphisms are morphisms in `C` that preserve the action.
- The faithful carrier projection to `C` is the sole immediate structural functor.
- The enriched map to `End_C(X)` appears when the stated adjunction exists.

The complete governing set also includes `POL-MATH-001` through `POL-MATH-013`,
`POL-MATH-020` through `POL-MATH-023`, `POL-CAT-001` through `POL-CAT-020`,
`POL-CAT-033`, `POL-CAT-043` through `POL-CAT-047`, `POL-CAT-054`,
`POL-CAT-061` through `POL-CAT-087`, `POL-FUN-001` through `POL-FUN-006`,
`POL-FUN-023`, and `POL-DOC-003` through `POL-DOC-009`.
