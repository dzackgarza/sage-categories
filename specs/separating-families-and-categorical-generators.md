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
