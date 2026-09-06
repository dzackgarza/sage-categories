# Bimodule objects

Fix a monoidal category `V` and monoid objects `R` and `S` in `V`.
`Bimodules(R, S, V)` has objects `X` with a left action `R tensor X -> X` and a right action `X tensor S -> X`.
Both actions satisfy their unit and associativity diagrams.
They commute: the two maps `(R tensor X) tensor S -> X` agree after the associator identifies the action domains.

A morphism is one morphism of `V` preserving both actions.
The two action projections reach the same object and morphism of `V`.
Cat's inserters, equifiers, and pullbacks retain this compatibility and its projections.
The bimodule category owns the two action equations and their interpretation.

## Right actions through the reverse

`Reversed(V)` is the reverse monoidal category `V^rev`, with `x tensor^rev y = y tensor x`, the same unit, `a^rev_{x,y,z} = a_{z,y,x}^{-1}`, and the two unitors exchanged.
Reversing needs no braiding on `V`.

A right `S`-action `X tensor S -> X` is a left action of `S` in `V^rev`, because `S bullet X` there is `X tensor S`.
`S tensor^rev S` is `S tensor S`, so the multiplication and unit of `S` present a monoid object of `V^rev` without further data; that monoid object is the opposite monoid.
Right `S`-modules are therefore `Modules(S_opposite, SelfAction(Reversed(V)))`, and the module construction in [modules.md](modules.md) covers both sides.

`Bimodules(R, S, V)` takes `R` and `S` as monoid objects of `V` and reads `S` in `V^rev` itself, so a caller writes no opposite by hand.
It is the pullback of the left and right module categories over their forgetful functors to `V`, cut by the equifier of

\[
\lambda\circ(R\bullet\rho)
\qquad\text{and}\qquad
\rho\circ(\lambda\bullet S)\circ a^{-1}_{R,X,S}
\]

on `R tensor (X tensor S)`. The pullback supplies one carrier and both actions; the equifier imposes the commuting law.
`Bimodules(R, S, V)(left_action, right_action)` is the object constructor, `to_left()` and `to_right()` are the retained legs, `forgetful()` is the carrier functor, and `homomorphism(source, target, f)` constructs the morphism over a map of `V` that preserves both actions.

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

For `V = Ab` the abelian leaf supplies the coequalizer.
`coequalizer_projection(f, g)` is the universal map `B -> B / im(f - g)` of a parallel pair of homomorphisms, and `coequalizer_mediator(q, k)` factors a homomorphism that kills the same subgroup.
In Smith generators the quotient adjoins the rows of the difference matrix to the relations of the target, so it stays presented.
`relative_tensor(right_action, left_action)` is the balanced map `X tensor Y -> X tensor_S Y`, whose codomain is the relative tensor product.
`balanced_tensor(q, x, y)` is the point `x tensor_S y`, and `relative_tensor_mediator(q, C, h)` is the map out of the relative tensor through which a biadditive `S`-balanced rule factors.
`induced_left_action(q, lambda_X)` and `induced_right_action(q, rho_Y)` are the outer actions: acting on the outer factor commutes with the identification the middle monoid makes, so each action descends to the quotient.
`coequalizer_lift(q, t)` chooses a preimage through the retained cover; a rule written through it defines a homomorphism exactly when it kills the subgroup the quotient adjoins, which the constructed morphism checks.

The tensor product acts on pairs of compatible bimodule morphisms.
For `R=S=T`, the regular bimodule is the unit, with comparison isomorphisms induced by its actions.
Thus the supplied relative tensor product gives the monoidal category required for monoid objects over a noncommutative base.

The initial executable boundary is specified by [minimal leaf scaffolding](leaf-scaffolding.md).
It includes a noncommutative middle ring and an actual factorization of a balanced map.
