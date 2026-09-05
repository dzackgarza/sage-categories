# Schemes and their affine presentations

`Schemes()` is the category of schemes and morphisms of locally ringed spaces.
A scheme retains a topological space, a sheaf of commutative rings, and an affine open cover.
A morphism retains its continuous map and the compatible sheaf map; its maps on stalks are local ring homomorphisms.
These data have the standard meaning in [Stacks, locally ringed spaces](https://stacks.math.columbia.edu/tag/01HA).

The forgetful functor to locally ringed spaces is a full inclusion.
Further projections reach ringed spaces and topological spaces through their mathematical owners.
The scheme leaf adds local affineness, affine presentations, and the corresponding constructions.
It obtains generic functor, sheaf, restriction, and gluing operations from their existing owners.

## Affine schemes

Let `CRing` be the owned category of commutative unital rings.
`Spec: CRing.op() -> AffineSchemes()` sends a ring to its prime spectrum with its structure sheaf.
A ring map `A -> B` induces `Spec(B) -> Spec(A)` by inverse image on prime ideals and the induced localization maps.
The affine correspondence retains both actions and the comparison with global sections; see [Stacks, affine morphisms](https://stacks.math.columbia.edu/tag/01I1).

The open `D(f)` carries the localization `A_f` as its section ring.
An implementation retains the principal-open basis, restriction maps, and their composition.
It represents the prime spectrum mathematically even when its points cannot be enumerated.
Rational points alone do not determine that spectrum or its structure sheaf.

A point of the underlying topological space is a prime ideal with a local ring.
A categorical point of a scheme is a morphism from the terminal scheme `Spec(ZZ)`.
An `A`-valued point is a morphism `Spec(A) -> X`.
These three notions have different domains and must have distinct public meanings.

## Gluing

Gluing data consist of schemes `U_i`, open subspaces `U_ij`, and overlap isomorphisms satisfying the cocycle condition.
The construction retains the resulting scheme, its open chart maps, and the unique map induced by compatible maps on the charts.
The topology and sheaf are glued by their owners.
The scheme theorem establishes local affineness of the result.
This is the gluing construction of [Stacks, Section 26.14](https://stacks.math.columbia.edu/tag/01JA).

Finite affine covers with represented overlap covers provide the first evaluation domain.
The definition permits overlap opens covered by several affines.
It does not identify an overlap with a single affine merely because its two charts are affine.

The distinguishing example is the projective line over a finite field.
Two polynomial-ring spectra are glued on their invertible-coordinate opens by `u = t^(-1)`.
The example must recover the two charts, their restriction maps, and the induced chart-swap automorphism.
It uses the scheme's gluing mediator to define that automorphism.

The complete initial consumer boundary belongs to [minimal leaf scaffolding](leaf-scaffolding.md) and the project vault's scheme plan.
