Yes. The main computational use is not equality testing. It is the construction of presentations, resolutions, and faithful computational representations.

A separating family \((G_i)\) gives, when the required coproduct exists,

\[
\varepsilon_X:
\coprod_{i,\;u:G_i\to X} G_i \longrightarrow X.
\]

Each summand maps to \(X\) by its index \(u\). The separating theorem implies that \(\varepsilon_X\) is an epimorphism.

This gives code a precise result:

- Construct the coproduct and evaluation morphism.
- Return the morphism in `Mor(C).Epimorphisms()`.
- Compute its kernel or relations when the leaf supports them.
- Repeat this process to construct a resolution.

Python proves none of this. The implementation uses the theorem by constructing the result in its established category.

## Immediate leaf applications

| Category | Generator | Concrete result |
|---|---|---|
| `Sets()` | \(1\) | \(\coprod_{x\in X}1\cong X\). This adds little computation. |
| `Groups()` | \(\mathbb Z\) | A free group on selected elements maps onto the group. |
| `Modules(R)` | \(R\) | A free module maps onto \(M\). Its kernel gives relations. |
| `Modules(k[G])` | \(k[G]\) | Free and projective presentations support resolutions and representation homology. |
| Commutative rings | \(\mathbb Z[x]\) | A polynomial ring on selected elements maps onto the ring. |
| \(k\)-vector spaces | \(k\) | A basis gives \(k^n\cong V\), so morphisms become matrices. |

This matches existing Sage interfaces. Sage constructs group and module morphisms from images of generators. Finitely presented modules use generators and relations. [Sage group generators](https://doc.sagemath.org/html/en/reference/categories/sage/categories/groups.html), [Sage free-module morphisms](https://doc.sagemath.org/html/en/reference/modules/sage/modules/fp_graded/free_module.html), [Sage finitely presented modules](https://doc.sagemath.org/html/en/reference/modules/sage/modules/fp_graded/module.html).

There are two distinct notions here:

- A categorical generator, such as \(R\) in `Modules(R)`.
- Selected generators of one object, such as \(m_1,\ldots,m_n\in M\).

Each \(m_j\) corresponds to a morphism \(R\to M\). If they generate \(M\), they give the tractable epimorphism

\[
R^n\twoheadrightarrow M.
\]

Thus, categorical generators organize leaf-level `gens()`, presentations, and morphism constructors.

## Why a family is useful

Some important categories have a natural family of test objects, but no preferred single test object.

For an inclusion \(j:A\to C\) of test objects, form the restricted Yoneda functor

\[
N_j:C\longrightarrow [A^{op},\mathbf{Set}],
\qquad
N_j(X)(a)=\operatorname{Hom}_C(j(a),X).
\]

Then:

- A separating family makes \(N_j\) faithful.
- A dense family makes \(N_j\) fully faithful.
- Projective generators support lifting and resolutions.
- Compact generators can reduce coproduct computations to finite data.

These properties must remain separate. Separation alone implies none of the stronger results.

This also explains why an actual test category is better than a tuple. Morphisms between test objects encode compatibility and naturality.

## Presheaves and sheaves

For presheaves, the representables \(y(c)\) form the decisive test family.

Yoneda gives

\[
\operatorname{Hom}(y(c),F)\cong F(c).
\]

Consequently:

- A natural transformation is determined by its action on representables.
- Every presheaf has a canonical colimit presentation by representables.
- Presheaves of modules receive canonical epimorphisms from coproducts of free representables.
- Kernels then produce relations and resolutions.

Mathlib already implements this exact pattern. It constructs a canonical epimorphism from a coproduct of free Yoneda objects. It also presents every module-valued presheaf as a cokernel. [Mathlib presheaf generators](https://leanprover-community.github.io/mathlib4_docs/Mathlib/Algebra/Category/ModuleCat/Presheaf/Generator.html)

For sheaves, sheafified representables give analogous presentations. The Stacks Project constructs sheaves as coequalizers of coproducts of such objects. [Stacks Project, representable sheaves](https://stacks.math.columbia.edu/tag/00WO)

These are direct computational foundations for:

- constructing maps from local section data;
- free presentations of sheaves of modules;
- resolutions used for derived functors;
- extension of functors from representable objects.

## Schemes and stacks

A scheme already has its functor of points,

\[
h_X(T)=\operatorname{Hom}(T,X).
\]

[The Stacks Project defines this functor explicitly](https://stacks.math.columbia.edu/tag/01J5).

Affine test schemes, together with the sheaf and descent theorems, enable:

- pointwise computation of fiber products;
- construction of morphisms from affine-local ring maps;
- gluing compatible local morphisms;
- recognition that a computed presheaf is represented by a scheme.

For example,

\[
h_{X\times_ZY}(T)
\cong
h_X(T)\times_{h_Z(T)}h_Y(T).
\]

Code can compute the right side pointwise. A cited representability theorem then places the result back in `Schemes()`.

Stacks use the groupoid-valued version of this structure. Test schemes and atlases support pointwise 2-fiber products, descent data, and representability checks. That requires 2-Yoneda and descent structure beyond ordinary separation.

## Suitable foundation

The useful kernel object is not `separating_family() -> tuple`.

It is:

1. An indexed test functor \(j:A\to C\).
2. Its restricted Yoneda functor \(N_j\).
3. Placement of \(N_j\) in `.Faithful()` when separation is established.
4. Placement in `.FullyFaithful()` when density is established.
5. The canonical evaluation morphism, placed in `.Epimorphisms()`.
6. Separate projective, compact, and dense refinements when available.

For the current `Sets()` leaf, this gives little new functionality. For groups, modules, rings, representations, presheaves, and sheaves, it gives concrete constructors and computational presentations. That is sufficient reason to retain the mathematics in the foundation, but not the present tuple-based metadata form.

Yes, with one important distinction:

A separating family gives a reduction to probe data. It does not make that data finite by itself.

For test objects \(G_i\), define

\[
N(X)=\bigl(\operatorname{Hom}(G_i,X)\bigr)_i.
\]

Separation says that \(N\) is faithful. Thus, a morphism \(f:X\to Y\) is determined by all composites

\[
G_i\xrightarrow{u}X\xrightarrow{f}Y.
\]

However, the sets of \(i\) and \(u\) can remain infinite. Finitary computation needs more structure.

## The hierarchy of reductions

| Additional structure | What it supplies |
|---|---|
| Separating family | Detects equality of morphisms |
| Strong generator | Detects isomorphisms |
| Dense test category | Reconstructs objects and morphisms from probe data |
| Projective generator | Supplies lifts and free presentations |
| Compact generator | Controls maps from a generator into coproducts |
| Finitely presentable generator | Controls maps into filtered colimits |
| Finite presentation of \(X\) | Reduces maps from \(X\) to finite generators and relations |
| Progenerator | Replaces the category by modules over an endomorphism ring |

Therefore, the real computational pattern is:

\[
\text{arbitrary global datum}
\longrightarrow
\text{data on standard probes}
+
\text{compatibility relations}.
\]

It becomes genuinely finite when the probes, presentations, or compatibility relations are finite.

## Module morphisms

For an \(R\)-module presentation

\[
R^m\xrightarrow{A}R^n\twoheadrightarrow M,
\]

a morphism \(M\to N\) is equivalent to:

1. the images of the \(n\) standard generators;
2. the condition that those images kill the relations from \(A\).

For finite free modules, this is matrix data. For finitely presented modules, it is matrix data subject to matrix equations.

This is stronger than merely knowing that \(R\) generates `Modules(R)`. Projectivity and finite presentation produce the algorithm.

For \(k[G]\)-modules, \(k[G]\) is a projective generator. This supports:

- matrices over \(k[G]\);
- finite presentations of representations;
- kernels and cokernels;
- projective resolutions;
- chain complexes computing group homology or cohomology.

A progenerator gives an even stronger result. The functor

\[
\operatorname{Hom}(P,-)
\]

can implement a Morita equivalence with modules over \(\operatorname{End}(P)^{op}\). This converts categorical computations into module computations.

## Functors determined by generators

A functor is not generally determined by its value on one generator.

It must also specify:

- its action on endomorphisms of that generator;
- its action on morphisms between test objects;
- how it preserves the constructions used to build other objects.

Density gives the correct statement.

Let \(j:A\to C\) be a dense test category. Each \(X\in C\) has a canonical presentation by objects \(j(a)\). For a suitable colimit-preserving functor \(F:C\to D\),

\[
F(X)
\cong
\operatorname*{colim}_{j(a)\to X}F(j(a)).
\]

Thus, \(F\) is determined by:

- its restriction \(Fj:A\to D\);
- its action on morphisms in \(A\);
- the specified colimit preservation.

Natural transformations between such functors are also determined by their components on \(A\).

This can be a major reduction. It replaces a rule for every object of \(C\) with data on a small test category.

Again, “small” does not mean finite. An actual finite computation needs finite presentations or a finite relevant subdiagram.

## Presheaves

Representables give the cleanest example.

For \(F:C^{op}\to\mathbf{Set}\),

\[
\operatorname{Hom}(y(c),F)\cong F(c).
\]

The representables form a dense family. Therefore:

- the values \(F(c)\) and restriction maps specify the presheaf;
- maps between presheaves are specified componentwise;
- naturality supplies the compatibility equations;
- every presheaf is a colimit of representables.

For a finite category \(C\) and finite values \(F(c)\), this becomes finite data.

For module-valued presheaves, free representables produce presentations. A finite site and finitely presented values can reduce morphisms to finite matrices and naturality equations.

This is more than an organization of equality checks. It supplies constructors for objects, morphisms, and functors from test-object data.

## Sheaves, schemes, and stacks

A site basis acts like a test category. The sheaf condition adds descent relations.

Under finite-cover or quasi-compact hypotheses, a global construction can reduce to:

- finitely many local objects;
- their pairwise overlap data;
- cocycle equations on triple overlaps.

For schemes, an affine cover can reduce a morphism to ring maps on affine pieces. Compatibility on overlaps then constructs the global morphism.

The functor of points applies the same pattern externally. Instead of manipulating a scheme directly, code manipulates

\[
T\longmapsto\operatorname{Hom}(T,X)
\]

on selected test schemes. Density and descent determine when those test values reconstruct \(X\).

For stacks, the values are groupoids. The data then include objects, isomorphisms, and cocycle conditions. Atlases and descent can still reduce global constructions to explicit local diagrams.

These reductions need more than separation. They need density, descent, representability, and suitable finiteness hypotheses.

## The functional-analysis analogy

The analogy is sound, but \(L^2(\mathbb R)\) needs care.

The exponentials \(e^{i\xi x}\) are not elements of \(L^2(\mathbb R)\). They are generalized Fourier modes. Also, a general bounded operator on \(L^2(\mathbb R)\) need not have an ordinary integral kernel.

Special operator classes do have tractable descriptions:

- translation-invariant operators have Fourier multipliers;
- Hilbert–Schmidt operators have \(L^2\) kernels;
- finite-rank operators have finite matrix descriptions;
- compact operators can be approximated by finite-rank operators;
- diagonal, sparse, or banded operators have restricted matrix data.

An orthonormal basis gives coordinates, but its operator matrix remains infinite. The analytic property makes the representation tractable.

The categorical situation is the same:

- generators provide coordinates;
- separation provides detection;
- density provides reconstruction;
- projectivity provides presentations;
- compactness controls infinite sums;
- finite presentation produces finite data.

So “determined by generators” is the common organizing principle. The added categorical properties determine whether that principle yields an actual finite algorithm.

I used the wrong completion standard. You asked about broad finitary constructors. I answered whether they represent every possible morphism.

A CAS does not need to represent every object or morphism. It needs exact constructors for useful computational classes.

The central categorical formula is this. Suppose \(X\) has a finite presentation

\[
\coprod_{j=1}^{m}G_j
\rightrightarrows
\coprod_{i=1}^{n}G_i
\twoheadrightarrow X.
\]

Then

\[
\operatorname{Hom}(X,Y)
\cong
\operatorname{Eq}\left(
\prod_{i=1}^{n}\operatorname{Hom}(G_i,Y)
\rightrightarrows
\prod_{j=1}^{m}\operatorname{Hom}(G_j,Y)
\right).
\]

Thus, a morphism from \(X\) consists of:

- finitely many images of generators;
- finitely many compatibility equations.

That is the general infinitary-to-finitary reduction.

## Standard examples

For a free group \(F_n\),

\[
\operatorname{Hom}(F_n,H)\cong H^n.
\]

Every tuple in \(H^n\) defines one group homomorphism.

For a finitely presented group

\[
G=\langle x_1,\ldots,x_n\mid r_1,\ldots,r_m\rangle,
\]

a homomorphism \(G\to H\) is an \(n\)-tuple satisfying

\[
r_j(h_1,\ldots,h_n)=1
\]

for each relation.

For an \(R\)-module,

\[
\operatorname{Hom}_R(R^n,N)\cong N^n.
\]

If

\[
R^m\xrightarrow{A}R^n\twoheadrightarrow M,
\]

then

\[
\operatorname{Hom}_R(M,N)
\cong
\ker\left(N^n\xrightarrow{A^\ast}N^m\right).
\]

For finite free targets, this becomes a matrix equation.

For a finitely presented commutative \(R\)-algebra

\[
A=R[x_1,\ldots,x_n]/(p_1,\ldots,p_m),
\]

an \(R\)-algebra map \(A\to B\) is a tuple \((b_1,\ldots,b_n)\) satisfying

\[
p_j(b_1,\ldots,b_n)=0.
\]

These constructors can represent every morphism from the supported presented domain. They need not represent arbitrary objects in the ambient category.

## What the categorical generator contributes

A categorical generator identifies the standard building blocks \(G_i\). A presentation identifies the finite construction of one object from those blocks.

The generator alone supplies detection. The presentation supplies the finitary constructor.

Useful combinations include:

- free generators, which allow arbitrary generator images;
- projective generators, which support lifting and resolutions;
- finitely presentable generators, which interact with filtered constructions;
- finite presentations, which reduce morphisms to finite equations;
- effective equality algorithms, which decide those equations in supported leaves.

The computational object should therefore retain its presentation. A bare assertion that the ambient category has a generator is insufficient.

## Functor-level reductions

The same principle can reduce functor construction.

Let \(A\) be a dense test category in \(C\). A colimit-preserving functor \(F:C\to D\) is determined by:

- the objects \(F(a)\) for \(a\in A\);
- its action on morphisms of \(A\);
- its prescribed preservation of the presentations building objects of \(C\).

For a presheaf \(P\),

\[
P\cong
\operatorname*{colim}_{y(a)\to P}y(a).
\]

Therefore,

\[
F(P)\cong
\operatorname*{colim}_{y(a)\to P}F(y(a)).
\]

A rule on all presheaves is replaced by a rule on representables and one extension formula.

Natural transformations between such functors are likewise determined by their components on the test category.

This is not merely organizational. It constructs an infinite class of functor values from smaller data.

## Stronger examples

Eilenberg–Watts gives a particularly sharp reduction. Under its standard hypotheses, an additive, right-exact, coproduct-preserving module functor is determined by one bimodule:

\[
F(M)\cong M\otimes_R F(R).
\]

Instead of supplying an arbitrary rule on every module and morphism, the writer supplies \(F(R)\) and its bimodule structure.

Morita theory goes further. A progenerator \(P\) can identify an entire category with modules over

\[
\operatorname{End}(P)^{op}.
\]

Objects and morphisms then receive module presentations and matrix computations.

For affine schemes,

\[
\operatorname{Hom}(\operatorname{Spec}B,\operatorname{Spec}A)
\cong
\operatorname{Hom}(A,B).
\]

When \(A\) is finitely presented, scheme morphisms become finite tuples satisfying polynomial equations.

Sheaf and stack constructors use the related descent pattern. Local objects and morphisms are supplied on a tractable cover. Compatibility equations construct the global result.

## The exact conclusion

“Values determined on generators” is the common mathematical principle.

Its computational forms are stronger and more specific:

- free extension from generator images;
- quotienting by finite relations;
- reconstruction from a dense test category;
- extension of functors from representables;
- Morita reduction to module computations;
- descent from local presentation data.

A separating family becomes computationally important when it participates in one of these constructions. Separation by itself only says that the probes distinguish morphisms. It does not yet provide the finitary presentation.
