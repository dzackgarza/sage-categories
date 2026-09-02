# Vocabulary contract

This file is the deterministic vocabulary contract for agent-facing documentation.
Read it before writing or editing that documentation (`POL-MATH-050`).

Use the exact mathematical owner and public spelling in this file.
Do not record retired names in current documentation.

## Required distinctions

| Concept | Required statement |
| --- | --- |
| `C.ElementType` | The shared implementation and API for elements of objects of `C`. |
| Point of a category `X` | A functor `* -> X`. This is an actual object of `X`; a set uses its discrete, 0-truncated category. |
| `Cat().Point(X)` | The one-object category whose distinguished object is `X`. It is not a point `* -> X`. Its selected structure functors are the point functors of `X`, and each places `X` in its codomain (D128). |
| Point of `C in Cat()` | A functor `* -> C`. This is an actual object of `C` and a `Cat().ElementType` value. |
| Generalized element of `X` | A functor `T -> X`. |
| Morphism of `C` | An object of `Mor(C)`. Thus `C.MorphismType = Mor(C).ObjectType`. |
| Functor | An ordinary object of `Fun(C, D)`. A category can name many functors with the same endpoints. |
| Owned category graph | The entirely new graph whose nodes are package-owned objects of `Cat()` and whose selected implementation edges are owned structure functors. It is not Sage's mathematical category graph. Migrating a Sage concept creates a new owned category and the functors required by its mathematics. |
| Structure functor | An ordinary functor returned by `C.structure_functors()` and used by the kernel as an edge of the owned implementation graph. Its ordinary object and morphism actions are already complete and accept source values whose own local state is initialized. It need not be a subcategory monomorphism. |
| Private Sage implementation graph | The runtime-only graph of private Sage categories used to ask Sage for controlled C3 and dynamic implementation classes corresponding to the owned graph. It has no mathematical edges or nodes in the owned `Cat()` graph; the systems share only low-level Python/Sage `Parent` runtime ancestry. |
| Unresolved structural diamond | Two or more owned structure-functor paths reaching one implementation owner with no explicit owned coherence yet supplied between the relevant composites. C3 still chooses one occurrence and compilation proceeds; the condition is reported only at `DEBUG` level. |
| Fixed-object constructions | `C.Subobjects(X)`, `C.Superobjects(X)`, `C.CoveringObjects(X)`, and `C.CoveredObjects(X)`. |
| Named construction map | The exact retained projection, inclusion, evaluation, or adjoint with stated endpoints. |
| Functor actions | `F.on_object(X)` and `F.on_morphism(f)` construct the public images owned by `F` from completed values in the stated source category. Selection for inheritance lets the kernel run the object action during construction to initialize the target implementation on the source value (D13). |
| Subcategory relation | A declared subcategory monomorphism. Python class inheritance and selection as a structure functor do not establish it. |
| Classes specified by a category `C` | The category specifies `C.ObjectType`, `C.ElementType`, and `C.MorphismType` directly. The kernel constructs them dynamically from structure functors. |
| Public functor image | The image constructed by the named action `F.on_object(x)` or `F.on_morphism(f)`. |
| Inherited execution | A structure-functor target class is in the source class MRO. Its method runs on the initialized source instance. |
| Mathematical predicate | A proposition-valued operation owned by its category, property category, or equality operation. |
| Public SymPy predicate | The SymPy `Predicate` subclass that represents one mathematical predicate. SymPy owns its application and evaluation machinery. |
| Applied proposition | A SymPy `AppliedPredicate` or Boolean expression. `ask()` returns `True`, `False`, or Sage `Unknown`. |
| Typed query | A repository-owned operation with an exact non-Boolean result category. Its application remains unevaluated until `ask()` returns an owned result or `Unknown`. |
| Owned value | A public mathematical value constructed by its exact owning category. |
| Engine representation | A private runtime value used to compute with an owned value. It is not public mathematics. |
| Mathematical owner | The category, functor, property, query, or universal construction that defines one fact or operation. |
| Implementation-class owner | The category that declares the local `ObjectType`, `ElementType`, or `MorphismType` method provider. |
| Runtime substrate | The private compiler, dispatch, refinement, assumption, and computation machinery that executes the mathematical tower. |
| Foundational leaf | A production category required by later layers of the mathematical tower. |
| `Posets()` | The category of partially ordered sets and monotone maps. This is the public category spelling. |
| Private Sage implementation category | One node of the private Sage implementation graph that compiles one of `C.ObjectType`, `C.ElementType`, or `C.MorphismType`. It states no relation in the owned `Cat` graph. |

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
| twin-prime conjecture | [MathWorld, “Twin Primes”](https://mathworld.wolfram.com/TwinPrimes.html), the paragraphs on the conjecture and bounded gaps: infinitude of prime pairs separated by exactly two remains open, and bounded-gap theorems do not decide it. |
| `Predicate`, `AppliedPredicate`, `ask()` | [SymPy assumptions documentation](https://docs.sympy.org/latest/modules/assumptions/assume.html): a predicate is Boolean-valued, its application remains unevaluated, and `ask()` returns `True`, `False`, or an undecided result. |
| `dynamic_class(name, bases, cls)` | Sage, `src/sage/structure/dynamic_class.py:128`. With `cls` given, its methods are inserted into the built class and its bases are prepended. |
| `Category.parent_class`, `_make_named_class` | Sage, `src/sage/categories/category.py:1498` and `:1670`. Builds `parent_class` from `ParentMethods`, `element_class` from `ElementMethods`, `morphism_class` from `MorphismMethods`. |
| `Category._all_super_categories`, `_super_categories_for_classes` | Sage, `src/sage/categories/category.py:845`. Uses controlled C3 to compute the category linearization and the minimal supercategories needed as direct class bases. |
| `HierarchyElement` | Sage, `src/sage/misc/c3_controlled.pyx:960`. Computes a controlled linearization from an arbitrary successor relation. |
| `Parent._refine_category_` | Sage, `src/sage/structure/parent.pyx:372`. Joins the current category with the new category and changes the parent to a cached dynamic class containing the joined `parent_class`. |
| `CategoryWithAxiom`, `_base_category_class_and_axiom` | Sage, `src/sage/categories/category_with_axiom.py`. Supplies axiom binding, category construction, and canonical runtime identity. The owned `Cat` declaration supplies the axiom's mathematical meaning. |
| `FunctorialConstructionCategory`, `CartesianProductsCategory` | Sage, `src/sage/categories/covariant_functorial_construction.py` and `src/sage/categories/cartesian_product.py`. Supplies private construction-family binding, base-category access, caching, and method-provider assembly. The owned graph derives its own functors and universal presentations rather than importing Sage's supercategory deductions. |
| `Hom`, `Homset`, `Map`, `Morphism`, `IdentityMorphism` | Sage, `src/sage/categories/homset.py`, `map.pyx`, and `morphism.pyx`. Supplies the concrete endpoint, parent, composition, and identity protocols used when both endpoints are Sage parents. |
| `sage.categories.functor.Functor` | Sage, `src/sage/categories/functor.py`. Supplies the reference object and morphism action protocol. Its endpoints are Sage categories, so generic owned functors do not inherit it. |
| `ModulesWithBasis` | Sage, `src/sage/categories/modules_with_basis.py:179`: "The category of modules with a distinguished basis." A name for the phenomenon on the same axiom machinery as `Finite`. Its morphisms are ordinary module morphisms while its homset reads a matrix in the distinguished bases (`:47`), so the name settles neither the fibration nor the morphisms. |
