# Bimodule objects

Fix a monoidal category `V` and monoid objects `R` and `S` in `V`.
`Bimodules(R, S, V)` has objects `X` with a left action `R tensor X -> X` and a right action `X tensor S -> X`.
Both actions satisfy their unit and associativity diagrams.
They commute: the two maps `(R tensor X) tensor S -> X` agree after the associator identifies the action domains.

A morphism is one morphism of `V` preserving both actions.
The two action projections reach the same object and morphism of `V`.
Cat's inserters, equifiers, and pullbacks retain this compatibility and its projections.
The bimodule category owns the two action equations and their interpretation.

For ordinary rings, take `V` to be abelian groups under tensor product over the integers.
An `(R,S)`-bimodule then has a unital left `R`-action and a unital right `S`-action on one abelian group.
Changing either action changes the bimodule even if the group stays fixed.
A right `S`-action can also be expressed as a left action of the opposite ring.
The opposite ring and the map implementing that correspondence retain their mathematical ownership in ring theory.

## Relative tensor product

For an `(R,S)`-bimodule `X` and an `(S,T)`-bimodule `Y`, the tensor product over `S` is an `(R,T)`-bimodule.
Its defining presentation is the coequalizer

\[
X\otimes S\otimes Y\rightrightarrows X\otimes Y
  \longrightarrow X\otimes_S Y,
\]

where the parallel maps use the right action on `X` and the left action on `Y`.
The associator fixes the bracketing in this diagram.
The ambient category must supply these coequalizers, and tensoring must preserve the ones used to induce the outer actions.
The retained balanced map and mediator are part of the result.
For ordinary modules this is the usual balanced tensor product; see [Stacks, bimodules and tensor product](https://stacks.math.columbia.edu/tag/0FQM).

The tensor product acts on pairs of compatible bimodule morphisms.
For `R=S=T`, the regular bimodule is the unit, with comparison isomorphisms induced by its actions.
Thus the supplied relative tensor product gives the monoidal category required for monoid objects over a noncommutative base.

The initial executable boundary is specified by [minimal leaf scaffolding](leaf-scaffolding.md).
It includes a noncommutative middle ring and an actual factorization of a balanced map.
