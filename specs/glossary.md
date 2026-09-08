# Vocabulary and references

Use the mathematical terms below. Each linked topic owns its full definition and public interface.
[System architecture](system.md) owns layer boundaries; [decisions.md](decisions.md) retains provenance.

## Required distinctions

| Term | Meaning | Owner |
| --- | --- | --- |
| The kernel | Private class compilation, initialization, retention, refinement, and placement mechanics. | [Private runtime](resolution.md#the-closed-kernel-surface) |
| Cat | The mathematical owner of operations shared by all categories. | [System ownership](system.md); [Cat](functor.md#cat-and-its-implementation) |
| cat_kernel | The joint layer that builds axiom-derived categories and reads placement and inheritance declarations. | [Layer dependencies](system.md#dependency-directions) |
| C.ElementType | The shared implementation and API for elements of objects of C. | [Implementation classes](functor.md#cobjecttype-celementtype-and-cmorphismtype) |
| Point of X | A functor * -> X, presenting an object of X; sets use discrete categories. | [Points](functor.md#point-categories-and-point-functors); [nLab, generalized element, Global elements](https://ncatlab.org/nlab/show/generalized+element) |
| C.Point() | The point arrow selected in a leaf class to place its category object in C. | [Point declaration and level shift](functor.md#point-categories-and-point-functors) |
| Generalized element of X | A functor T -> X with a supplied domain T. | [Points](functor.md#point-categories-and-point-functors) |
| Morphism of C | An object of Mor(C); C.MorphismType = Mor(C).ObjectType. | [Morphism tower](functor.md#the-morn-c-tower) |
| Functor | An object of Fun(C, D), with exact endpoints and ordinary actions. | [Functors](functor.md#functors-as-morphisms-of-cat) |
| Owned category graph | The graph of repository-owned categories and their named mathematical functors. | [System architecture](system.md) |
| Structure functor | An ordinary functor selected in structure_functors(); its declared properties determine whether it supplies inheritance or access. | [Selected functors](functor.md#structure-functors-and-inherited-classes) |
| Private Sage implementation graph | The runtime mirror used for controlled C3 and dynamic classes. | [Sage compilation](resolution.md#sage-class-construction) |
| Private Sage implementation category | A runtime node that compiles one category-owned implementation class. | [Sage compilation](resolution.md#sage-class-construction) |
| Unresolved structural diamond | Selected inheritance paths reach one implementation owner without supplied coherence between their composites. | [Diamond diagnostics](resolution.md#diamond-diagnostics-and-future-coherence) |
| Fixed-object constructions | C.Subobjects(X), C.Superobjects(X), C.CoveringObjects(X), and C.CoveredObjects(X). | [Fixed-object constructions](functor.md#fixed-object-construction-categories) |
| Named construction map | A retained projection, inclusion, evaluation, adjoint, or universal map with exact endpoints. | [Construction-owned functors](functor.md#construction-named-functors) |
| Functor actions | F.on_object(X) and F.on_morphism(f) construct the named functor's images. | [Executable actions](functor.md#functor-actions-are-concrete-constructors) |
| Subcategory relation | A represented monomorphism of categories; placement additionally requires its isofibration declaration. | [Placement conditions](functor.md#monomorphisms-of-cat-and-placement) |
| Classes specified by C | The local ObjectType, ElementType, and MorphismType declarations that the compiler builds. | [Implementation classes](functor.md#cobjecttype-celementtype-and-cmorphismtype) |
| Public functor image | The image returned by the named ordinary functor action. | [Functor actions](functor.md#functor-actions-are-concrete-constructors) |
| Inherited execution | A target owner's method runs directly on the initialized source instance through its compiled class. | [Construction execution](resolution.md#direct-inherited-execution) |
| Mathematical predicate | A proposition-valued operation with one mathematical owner. | [Questions](undecidable-properties.md#mathematical-questions) |
| Public SymPy predicate | The category-owned Predicate subclass exposed through Cat's exported base. | [Public propositions](undecidable-properties.md#public-propositions) |
| Applied proposition | A SymPy AppliedPredicate or Boolean expression evaluated through ask(). | [Public propositions](undecidable-properties.md#public-propositions) |
| Typed query | A partial mathematical operation with an exact non-Boolean result category. | [Typed queries](undecidable-properties.md#typed-queries) |
| Owned value | A public mathematical value constructed by its exact category. | [Ownership](system.md) |
| Engine representation | A private runtime representation used for computation. | [Computation engines](leaves.md#computation-engine-boundary) |
| Mathematical owner | The category, functor, property, query, or construction that defines a fact or operation. | [Ownership](system.md) |
| Implementation-class owner | The category declaring a local ObjectType, ElementType, or MorphismType method provider. | [Implementation classes](leaves.md#owned-implementation-classes) |
| Runtime substrate | Private compilation, dispatch, refinement, assumptions, and computation support. | [Runtime](resolution.md) |
| Foundational leaf | A production category consumed by later mathematical layers. | [System tower](system.md) |
| Posets() | The category of partially ordered sets and monotone maps. | [Order categories](ordered-sets.md) |

## Inspected sources

These exact reference locators were recorded with the definitions before consolidation.
The topic link gives the current repository contract.

| Reference term | Topic owner | Exact source |
| --- | --- | --- |
| separator | [Generators](separating-families-and-categorical-generators.md#separation-and-density) | [nLab, "separator"](https://ncatlab.org/nlab/show/separator) |
| replete | [Placement](functor.md#monomorphisms-of-cat-and-placement) | [nLab, "replete subcategory"](https://ncatlab.org/nlab/show/replete+subcategory) |
| fibred category | [Indexed categories](functor.md#indexed-categories-yoneda-and-representability) | [Stacks Project, Categories, Definition 4.33.5, tag 02XJ](https://stacks.math.columbia.edu/tag/02XJ); Lemma 4.33.7 for the pseudofunctor after choosing pullbacks |
| Grothendieck construction | [Indexed categories](functor.md#indexed-categories-yoneda-and-representability) | [nLab, "Grothendieck construction"](https://ncatlab.org/nlab/show/Grothendieck+construction) |
| opposite category and dualizing functor | [Dualization](functor.md#opposites-and-dualization) | [Mathlib, `CategoryTheory.Opposites`](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Opposites.html); [Mathlib, `CategoryTheory.Cat.opFunctor`](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Category/Cat/Op.html) |
| inverse-image subcategory | [Inverse images](property-refinement.md#inverse-images) | [Mathlib, `ObjectProperty.inverseImage`](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/ObjectProperty/Basic.html); [full subcategory](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/ObjectProperty/FullSubcategory.html) |
| whiskering and horizontal composition | [Functor calculus](functor.md#functor-category-calculus) | [Mathlib, `CategoryTheory.Whiskering`](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Whiskering.html) |
| comma category | [Comma categories](functor.md#comma-categories-slices-coslices-and-fibers) | [Mathlib, `CategoryTheory.Comma`](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Comma/Basic.html) |
| fiber of a functor | [Fibers](functor.md#comma-categories-slices-coslices-and-fibers) | [Mathlib, `CategoryTheory.Functor.Fiber`](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/FiberedCategory/Fiber.html) |
| strict, full, and essential image | [Images](functor.md#strict-full-and-essential-images) | [Mathlib, `CategoryTheory.EssentialImage`](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/EssentialImage) |
| adjunction | [Adjunctions](functor.md#adjunctions-and-equivalences) | [Mathlib, `CategoryTheory.Adjunction`](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Adjunction/Basic.html) |
| equivalence of categories | [Equivalences](functor.md#adjunctions-and-equivalences) | [Mathlib, `CategoryTheory.Equivalence`](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Equivalence.html) |
| cone and limiting cone | [Universal presentations](functor.md#diagram-shapes-and-universal-constructions) | [Mathlib, cone categories](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Limits/ConeCategory.html) |
| preserves and creates limits | [Universal constructions](functor.md#diagram-shapes-and-universal-constructions) | [Mathlib, adjunctions and limits](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Adjunction/Limits.html); [Mathlib, creates limits](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Limits/Creates.html) |
| Yoneda embedding | [Yoneda](functor.md#indexed-categories-yoneda-and-representability) | [Mathlib, `CategoryTheory.yoneda`](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Yoneda.html) |
| representation of a functor | [Representations](functor.md#indexed-categories-yoneda-and-representability) | [Mathlib, `Functor.RepresentableBy`](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/RepresentedBy.html) |
| twin-prime conjecture | [Twin-prime set](undecidable-properties.md#twin-prime-set) | [MathWorld, “Twin Primes”](https://mathworld.wolfram.com/TwinPrimes.html) |
| `Predicate`, `AppliedPredicate`, `ask()` | [Propositions](undecidable-properties.md#public-propositions) | [SymPy assumptions documentation](https://docs.sympy.org/latest/modules/assumptions/assume.html) |
| `dynamic_class(name, bases, cls)` | [Sage compilation](resolution.md#sage-class-construction) | `src/sage/structure/dynamic_class.py:128` |
| `Category.parent_class`, `_make_named_class` | [Sage compilation](resolution.md#sage-class-construction) | `src/sage/categories/category.py:1498`; `src/sage/categories/category.py:1670` |
| `Category._all_super_categories`, `_super_categories_for_classes` | [Sage compilation](resolution.md#sage-class-construction) | `src/sage/categories/category.py:845` |
| `HierarchyElement` | [Sage compilation](resolution.md#sage-class-construction) | `src/sage/misc/c3_controlled.pyx:960` |
| `Parent._refine_category_` | [Runtime refinement](resolution.md#runtime-categories-and-caches) | `src/sage/structure/parent.pyx:372` |
| `CategoryWithAxiom`, `_base_category_class_and_axiom` | [Private property binding](resolution.md#properties-and-constructions) | `src/sage/categories/category_with_axiom.py` |
| `FunctorialConstructionCategory`, `CartesianProductsCategory` | [Construction binding](resolution.md#properties-and-constructions) | `src/sage/categories/covariant_functorial_construction.py`; `src/sage/categories/cartesian_product.py` |
| `Hom`, `Homset`, `Map`, `Morphism`, `IdentityMorphism` | [Private morphism protocols](resolution.md#properties-and-constructions) | `src/sage/categories/homset.py`; `src/sage/categories/map.pyx`; `src/sage/categories/morphism.pyx` |
| `sage.categories.functor.Functor` | [Functor actions](functor.md#functor-actions-are-concrete-constructors) | `src/sage/categories/functor.py` |
| `ModulesWithBasis` | [Chosen-data morphisms](functor.md#indexed-categories-yoneda-and-representability) | `src/sage/categories/modules_with_basis.py:179`; `src/sage/categories/modules_with_basis.py:47` (ordinary module morphisms; bases supply matrix coordinates) |
