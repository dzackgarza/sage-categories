# Vocabulary contract

This file is the deterministic vocabulary contract for agent-facing documentation.
Read it before writing or editing that documentation (`POL-MATH-050`).

Use the required wording in the second column.
Do not decide from familiarity, repository frequency, or nearby source.
A prohibited term can occur only in the first column of this table and in Git history.

When a user correction or accepted review prohibits another term, add one row with its exact replacement.
Do not remove a row after the source becomes clean (`POL-MATH-051`).

## Forbidden vocabulary

| Prohibited term | Required wording |
| --- | --- |
| `DeclaredObjectType`, `DeclaredElementType`, `DeclaredMorphismType` | `ObjectType`, `ElementType`, `MorphismType` |
| `declared functor`, `selected declared functor` | `named functor` |
| `structural functor` | `structure functor` |
| `role`, `role class`, `role-class`, `object role`, `element role`, `morphism role` | the exact class name, such as `C.ObjectType`, or “the class compiled for objects of `C`” |
| `role state`, `role node`, `role map`, `role metadata` | the exact class, constructor datum, structure functor, or class graph that the sentence means |
| `carrier`, `carrier set`, `carrier surface` | the image under a named functor with stated endpoints |
| `carrier_projection`, `underlying_object_projection`, `underlying_set`, a generic `underlying_*()` accessor | construct and apply the named functor with stated endpoints |
| `canonical image`, `canonical ancestor image`, `canonical target image` | `F.on_object(x)` or `F.on_morphism(f)` for the named functor `F` |
| `structural image`, `structural_image` | the image owned by the named functor `F`; a category has no image operation |
| `receiver`, `receiver-valued`, `this_object` | the source instance, or the value to which the method applies |
| `point stage`, `object stage`, `arrow stage`, `classical stage`, `product stage`, `stage comparison`, `stage identity`, `ObjectStageIdentity`, `ArrowStageIdentity`, `stage_comparison` | the exact point, generalized element, or constructor conversion |
| `generalized point` | `generalized element` for `T -> X`; use `point` only for `* -> X` |
| `Ar(C)`, `Hom(C)`, arrow-category or hom-category aliases | `Mor(C)` or `Mor(C)(A, B)` |
| `ChosenSubobjects`, `chosen subobject` | `Subobjects(X)`; a subobject is an object with its monomorphism into `X` |
| `Chosen<Anything>` | `With<Datum>` only when the object retains chosen data; otherwise use the mathematical construction name |
| generic `_construct` | the exact named constructor for the mathematical construction |

## Required distinctions

| Concept | Required statement |
| --- | --- |
| `C.ElementType` | The shared implementation and API for elements of objects of `C`. |
| Point of a category `X` | A functor `* -> X`. This is an actual object of `X`; a set uses its discrete, 0-truncated category. |
| Point of `C in Cat()` | A functor `* -> C`. This is an actual object of `C` and a `Cat().ElementType` value. |
| Generalized element of `X` | A functor `T -> X`. |
| Morphism of `C` | An object of `Mor(C)`. Thus `C.MorphismType = Mor(C).ObjectType`. |
| Functor | An ordinary object of `Fun(C, D)`. A category can name many functors with the same endpoints. |
| Structure functor | An ordinary functor returned by `C.structure_functors()` and used by the kernel to construct inherited class surfaces and constructor conversions. It need not be a subcategory monomorphism. |
| Subcategory relation | A declared subcategory monomorphism. Python class inheritance and selection as a structure functor do not establish it. |
| Classes specified by a category `C` | The category specifies `C.ObjectType`, `C.ElementType`, and `C.MorphismType` directly. The kernel constructs them dynamically from structure functors. |
| Public functor image | The image constructed by the named action `F.on_object(x)` or `F.on_morphism(f)`. |
| Inherited execution | A structure-functor target class is in the source class MRO. Its method runs on the initialized source instance. |
| Constructor conversion | A structure functor converts source construction data to the exact data required by its target constructor. |

The point and generalized-element distinction follows the nLab entry [generalized element](https://ncatlab.org/nlab/show/generalized+element), including its “Global elements” section.

## Inspected sources

Every term below was checked against the cited source before it was recorded (`POL-MATH-040`). A term with no source and no plain definition names an implementation artifact: report the missing construction rather than opening a row (`POL-MATH-052`).

| Term | Source |
| --- | --- |
| separator | [nLab, "separator"](https://ncatlab.org/nlab/show/separator): an object `S` such that for every parallel pair `f, g: X -> Y`, if `f . e = g . e` for every `e: S -> X` then `f = g`. Also called a generator, separating object, or generating object. In a locally small category this says `Hom(S, -)` is faithful. |
| replete | [nLab, "replete subcategory"](https://ncatlab.org/nlab/show/replete+subcategory): a subcategory `D` of `C` such that for any object `x` of `D` and any isomorphism `f: x -> y` in `C`, both `y` and `f` lie in `D`. Equivalently the inclusion `D -> C` is an isofibration, which is what makes strict membership respect the principle of equivalence. |
| fibred category | [Stacks Project, Categories, Definition 4.33.5, tag 02XJ](https://stacks.math.columbia.edu/tag/02XJ): "We say `S` is a fibred category over `C` if given any `x` in `Ob(S)` lying over `U` in `Ob(C)` and any morphism `f: V -> U` of `C`, there exists a strongly cartesian morphism `f^*x -> x` lying over `f`." Lemma 4.33.7 gives the pseudofunctor from `C^opp` to the (2,1)-category of categories once pullbacks are chosen. |
| Grothendieck construction | [nLab, "Grothendieck construction"](https://ncatlab.org/nlab/show/Grothendieck+construction): for a pseudofunctor `F: C^op -> Cat`, the category `∫F` has as objects the pairs `(c, a)` with `c` in `Ob(C)` and `a` in `Ob(F(c))`, and as morphisms `(c, a) -> (c', a')` the pairs of `f: c -> c'` in `C` and `phi: a -> F(f)(a')` in `F(c)`. The projection `p: ∫F -> C` takes a pair to its first component, and `∫` is an equivalence of 2-categories between pseudofunctors `C^op -> Cat` and Grothendieck fibrations over `C`. This is the construction behind every category of objects carrying a chosen datum (`POL-CAT-098`). |
| opposite category and dualizing functor | [Mathlib, `CategoryTheory.Opposites`](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Opposites.html): `C^op` has the objects of `C` and reverses its morphisms. [Mathlib, `CategoryTheory.Cat.opFunctor`](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Category/Cat/Op.html): `Op: Cat -> Cat` sends categories and functors to their opposites and has a natural isomorphism `Op compose Op ≅ Id`. |
| inverse-image subcategory | [Mathlib, `ObjectProperty.inverseImage`](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/ObjectProperty/Basic.html): for `F: D -> C` and an object property `P` on `C`, the inverse image contains the objects `X` of `D` for which `P(F(X))` holds. Its associated [full subcategory](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/ObjectProperty/FullSubcategory.html) is the pullback `D ×_C C.P()`. |
| whiskering and horizontal composition | [Mathlib, `CategoryTheory.Whiskering`](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Whiskering.html): composition on either side is functorial on functor categories. Its action on natural transformations is left or right whiskering; their composite gives horizontal composition. |
| comma category | [Mathlib, `CategoryTheory.Comma`](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Comma/Basic.html): for `F: A -> C` and `G: B -> C`, an object is `(a, b, f)` with `f: F(a) -> G(b)`. The category has projections to `A` and `B` and a natural transformation between the induced composites to `C`. |
| fiber of a functor | [Mathlib, `CategoryTheory.Functor.Fiber`](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/FiberedCategory/Fiber.html): for `p: E -> B` and `b in B`, the fiber has objects of `E` over `b` and morphisms over the identity of `b`. |
| strict, full, and essential image | The strict image has the literal object image and those target morphisms equal to morphism images. The full image is the full subcategory spanned by the literal object image. [Mathlib, `CategoryTheory.EssentialImage`](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/EssentialImage) is the full replete subcategory on objects isomorphic to an object image and supplies the essentially-surjective/fully-faithful factorization. |
| adjunction | [Mathlib, `CategoryTheory.Adjunction`](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Adjunction/Basic.html): selected data `F ⊣ G` consists of a unit, a counit, and the two triangle identities. |
| equivalence of categories | [Mathlib, `CategoryTheory.Equivalence`](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Equivalence.html): selected data consists of a functor, an inverse functor, and unit and counit natural isomorphisms with coherence. Equivalences `C ≌ D` form a category whose morphisms are natural transformations between the forward functors. |
| cone and limiting cone | [Mathlib, cone categories](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Limits/ConeCategory.html): cones over a diagram form a category, and a cone is limiting exactly when it is terminal in that category. |
| preserves and creates limits | [Mathlib, adjunctions and limits](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Adjunction/Limits.html) and [Mathlib, creates limits](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Limits/Creates.html): preservation sends limiting cones to limiting cones; creation gives the unique lifted limiting cone whose image is the supplied one. |
| Yoneda embedding | [Mathlib, `CategoryTheory.yoneda`](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Yoneda.html): the fully faithful functor `C -> Fun(C.op(), Sets())` sending `X` to `Mor(C)(-, X)`. |
| representation of a functor | [Mathlib, `Functor.RepresentableBy`](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/RepresentedBy.html): selected data consists of `X in C` and a natural isomorphism `yoneda(X) -> F`. A morphism is a map of representing objects compatible with these isomorphisms. Representability is the existence of such data. |
| `dynamic_class(name, bases, cls)` | Sage, `src/sage/structure/dynamic_class.py:128`. With `cls` given, its methods are inserted into the built class and its bases are prepended. |
| `Category.parent_class`, `_make_named_class` | Sage, `src/sage/categories/category.py:1498` and `:1670`. Builds `parent_class` from `ParentMethods`, `element_class` from `ElementMethods`, `morphism_class` from `MorphismMethods`. |
| `ModulesWithBasis` | Sage, `src/sage/categories/modules_with_basis.py:179`: "The category of modules with a distinguished basis." A name for the phenomenon on the same axiom machinery as `Finite`. Its morphisms are ordinary module morphisms while its homset reads a matrix in the distinguished bases (`:47`), so the name settles neither the fibration nor the morphisms. |
