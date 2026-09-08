# Separating families and categorical generators

This specification gives the generator constructions built from restricted Yoneda.
[`functor.md`](functor.md#indexed-categories-yoneda-and-representability) owns the generic functor and its property categories.
This file owns its evaluation morphisms, presentations, and domain applications.

## Contents

- [Restricted Yoneda](#restricted-yoneda)
- [Separation and density](#separation-and-density)
- [Evaluation epimorphisms](#evaluation-epimorphisms)
- [Projective and compact generators](#projective-and-compact-generators)
- [Finite presentations](#finite-presentations)
- [Domain applications](#domain-applications)

## Restricted Yoneda

Let \(A\) be a small category, and let \(C\) be locally small.
Let

\[
j:A\longrightarrow C
\]

be a test functor.
It is an object of `Fun(A, C)`.
The generic construction in [`functor.md`](functor.md#indexed-categories-yoneda-and-representability) gives

\[
N_j:C\longrightarrow \operatorname{Fun}(A^{op},\mathbf{Set}),
\qquad
N_j(X)(a)=\operatorname{Hom}_C(j(a),X).
\]

For \(f:X\to Y\), the component at \(a\in A\) is postcomposition:

\[
N_j(f)_a(u)=f\circ u.
\]

Thus, `j.restricted_yoneda()` is an object of
`Fun(C, Fun(A.op(), Sets()))`.
The morphisms of \(A\) record compatibility between the probes \(j(a)\).

## Separation and density

The test functor \(j\) is **separating** when \(N_j\) is faithful.
For parallel morphisms \(f,g:X\to Y\), this means

\[
\bigl(\forall a\in A,\ \forall u:j(a)\to X,\ f\circ u=g\circ u\bigr)
\quad\Longrightarrow\quad
f=g.
\]

The named functor \(N_j\) then belongs to
`Fun(C, Fun(A.op(), Sets())).Faithful()`.

The test functor \(j\) is **dense** when \(N_j\) is fully faithful.
For all \(X,Y\in C\), density gives a bijection

\[
\operatorname{Hom}_C(X,Y)
\cong
\operatorname{Nat}(N_j(X),N_j(Y)).
\]

The right side is the hom-set in `Fun(A.op(), Sets())`.

The named functor \(N_j\) then belongs to
`Fun(C, Fun(A.op(), Sets())).FullyFaithful()`.

Density also gives a canonical reconstruction of each object.
Let \(\int_A N_j(X)\) be the category of elements of \(N_j(X)\).
Its objects are pairs \((a,u)\) with \(u:j(a)\to X\).
The canonical cocone has legs \(u:j(a)\to X\).
Density says that this cocone is colimiting, so

\[
\operatorname*{colim}_{(a,u)\in\int_A N_j(X)} j(a)
\cong X.
\]

Separation determines morphisms from all probe composites.
Density reconstructs objects and morphisms from compatible probe data.

## Evaluation epimorphisms

Assume that \(C\) has the required coproducts.
For each \(X\in C\), define

\[
E_j(X)
=
\coprod_{a\in\operatorname{Ob}(A)}
\coprod_{u\in\operatorname{Hom}_C(j(a),X)} j(a).
\]

The indices define a canonical evaluation morphism

\[
\varepsilon_X:E_j(X)\longrightarrow X.
\]

Its restriction to the summand indexed by \((a,u)\) is \(u\).
The construction is natural in \(X\).

If \(j\) is separating, then \(\varepsilon_X\) is an epimorphism.
Indeed, \(r\varepsilon_X=s\varepsilon_X\) implies \(ru=su\) for every probe map \(u\).
Faithfulness of \(N_j\) then gives \(r=s\).

The separating construction returns \(\varepsilon_X\) in `Mor(C).Epimorphisms()`.

It retains the source \(E_j(X)\), the coproduct injections, and the evaluation legs.
Leaves can use this presentation to compute relations, kernels, and resolutions.

## Projective and compact generators

An object \(G\in C\) is **projective** when it has lifts along epimorphisms.
For every epimorphism \(p:X\twoheadrightarrow Y\) and every \(u:G\to Y\), there is
\(\widetilde u:G\to X\) with \(p\widetilde u=u\).

The probes form a family of projective generators when they separate \(C\) and each \(j(a)\) is projective.
Their evaluation epimorphisms give projective building blocks for presentations and resolutions.

An object \(G\in C\) is **compact for coproducts** when probe maps have finite support.
For every family \((X_i)_{i\in I}\), the canonical map

\[
\operatorname*{colim}_{J\subseteq I,\ J\text{ finite}}
\operatorname{Hom}_C\!\left(G,\coprod_{j\in J}X_j\right)
\longrightarrow
\operatorname{Hom}_C\!\left(G,\coprod_{i\in I}X_i\right)
\]

is a bijection.
A compact separating family reduces each probe map into a coproduct to finite support.

Projectivity and compactness have different roles.
Projectivity supplies lifts through epimorphisms.
Compactness controls maps into coproducts.
Finite presentability instead requires \(\operatorname{Hom}_C(G,-)\) to preserve filtered colimits.

A **projective generator** is both projective and separating.
A **compact projective generator** also has the stated compactness property.

## Finite presentations

Let \(P_0\) and \(P_1\) be finite coproducts of selected probes:

\[
P_0=\coprod_{i=1}^{n}G_i,
\qquad
P_1=\coprod_{r=1}^{m}H_r,
\qquad
G_i=j(a_i),\quad H_r=j(b_r).
\]

A finite presentation of \(X\in C\), relative to \(j\), is a coequalizer presentation

\[
P_1\rightrightarrows P_0\twoheadrightarrow X.
\]

For each \(Y\in C\), the representable functor \(\operatorname{Hom}_C(-,Y)\) sends this coequalizer to an equalizer:

\[
\operatorname{Hom}_C(X,Y)
\cong
\operatorname{Eq}\!\left(
\prod_{i=1}^{n}\operatorname{Hom}_C(G_i,Y)
\rightrightarrows
\prod_{r=1}^{m}\operatorname{Hom}_C(H_r,Y)
\right).
\]

The equalizer is an object of `Sets()`.
Its elements construct morphisms in `Mor(C)` with domain \(X\) and codomain \(Y\).
Each such morphism consists of finitely many probe images that satisfy finitely many relations.

The presentation, not separation alone, gives this finitary constructor.
An owned presented object retains \(P_1\rightrightarrows P_0\twoheadrightarrow X\) and its universal property.

## Domain applications

### Sets

The terminal set \(1\) is a generator of `Sets()`.
For every set \(X\), evaluation gives

\[
\coprod_{x\in X}1\xrightarrow{\sim}X.
\]

Here the evaluation epimorphism is already an isomorphism.

### Groups

The infinite cyclic group \(\mathbb Z\) is a projective generator of `Groups()`.
A chosen tuple \((h_1,\ldots,h_n)\in H^n\) defines a unique morphism

\[
F_n\longrightarrow H.
\]

For a finite presentation

\[
G=\langle x_1,\ldots,x_n\mid r_1,\ldots,r_m\rangle,
\]

the morphism factors through \(G\) exactly when

\[
r_k(h_1,\ldots,h_n)=1
\qquad (1\leq k\leq m).
\]

This is the mathematical contract behind
[Sage group morphisms from generators](https://doc.sagemath.org/html/en/reference/categories/sage/categories/groups.html).

### Modules and representations

The regular module \(R\) is a compact projective generator of `Modules(R)`.
A presentation

\[
R^m\xrightarrow{A}R^n\twoheadrightarrow M
\]

gives

\[
\operatorname{Hom}_R(M,N)
\cong
\ker\!\left(N^n\xrightarrow{A^*}N^m\right).
\]

Thus, module morphisms are finite generator images that satisfy the matrix relations.
The same presentation supports kernels, cokernels, and projective resolutions.
See [Sage free-module morphisms](https://doc.sagemath.org/html/en/reference/modules/sage/modules/fp_graded/free_module.html)
and [Sage finitely presented modules](https://doc.sagemath.org/html/en/reference/modules/sage/modules/fp_graded/module.html).

For a group algebra \(k[G]\), the regular module is a projective generator of `Modules(k[G])`.
Its projective resolutions support computations in group homology and cohomology.

### Commutative algebras

For a finitely presented commutative \(R\)-algebra

\[
B=R[x_1,\ldots,x_n]/(p_1,\ldots,p_m),
\]

an \(R\)-algebra morphism \(B\to S\) is a tuple \((s_1,\ldots,s_n)\in S^n\) with

\[
p_k(s_1,\ldots,s_n)=0
\qquad (1\leq k\leq m).
\]

The presentation converts algebra morphisms into finite polynomial equations.
