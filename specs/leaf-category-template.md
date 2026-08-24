# Leaf category template

Replace each `Leaf`, `Base`, and `defining_data` name with its mathematical name.
Keep only methods introduced by the leaf structure.

```python
class LeafObject(MathematicalObject):
    def __init__(
        self,
        *,
        category: LeafCategory,
        defining_data: LeafDefiningData,
    ) -> None:
        self._defining_data = defining_data
        super().__init__(category=category)

    def leaf_operation(self) -> LeafResult:
        """Return the result of an operation introduced by this structure."""
        ...


class ForgetLeafFunctor(StructuralFunctor):
    def __init__(self, source: LeafCategory, target: BaseCategory) -> None:
        super().__init__(source, target)

    def _object_image(self, source: MathematicalObject) -> BaseObject:
        assert LeafObjects().contains_leaf(source)
        return BaseObjects()(source._defining_data)

    def _morphism_image(self, morphism: Arrow) -> Arrow:
        assert self.domain().contains_arrow(morphism)
        ...

    def _element_image(
        self,
        source: MathematicalObject,
        element: MathematicalElement,
    ) -> BaseElement:
        assert LeafObjects().contains_leaf(source)
        assert element in source
        ...


class LeafCategory(Category):
    ObjectType = LeafObject
    ElementType = LeafElement

    def __call__(self, defining_data: LeafDefiningData) -> LeafObject:
        return self.ObjectType(category=self, defining_data=defining_data)

    def structure_functors(self) -> tuple[Functor, ...]:
        forget = ForgetLeafFunctor(self, BaseObjects())
        return (forget,)

    def contains_leaf(self, candidate: MathematicalObject) -> TypeIs[LeafObject]:
        return candidate in self
```

## Structural functor declarations

Every category declares its complete list of immediate `structure_functors()`.
The list contains functors, not target categories. Each functor supplies its domain,
codomain, object map, and arrow map. The kernel canonicalizes repeated construction of
the same declared functor.

Sage's `super_categories()` relation combines distinct mathematical relations. Sage
treats a category `C` as a supercategory of `D` after an implicit canonical functor
from `D` to `C`. Its documentation states that this functor can be an inclusion or a
forgetful functor. It also warns that the resulting “subcategory” terminology differs
from the standard mathematical definition. See the
[Sage category primer](https://doc.sagemath.org/html/en/reference/categories/sage/categories/primer.html#on-the-category-hierarchy-subcategories-and-super-categories)
and [Sage functor documentation](https://doc.sagemath.org/html/en/reference/categories/sage/categories/functor.html).

Keep these cases distinct:

- A genuine subcategory declares an inclusion functor. The category declaration states
  whether the subcategory is full or replete.
- A category of objects with extra structure declares a forgetful functor. For example,
  `(X, operation)` maps to `X`.
- A category whose objects contain several mathematical components declares the
  applicable projection functors.
- A realization or presentation functor remains an ordinary functor unless the category
  selects it for structural inheritance.

For a property-defined full subcategory, use a full-subcategory inclusion. This follows
the standard inclusion-functor terminology. Mathlib similarly gives an object property's
full subcategory an inclusion functor `ObjectProperty.ι`; see
[Mathlib's full-subcategory API](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/ObjectProperty/FullSubcategory.html).

```python
class Finite(FullRepletePropertySubcategory):
    def structure_functors(self) -> tuple[Functor, ...]:
        iota = FullSubcategoryInclusion(self, Sets())
        return (iota,)
```

`FullSubcategoryInclusion` derives the identity object and arrow maps from the declared
full-subcategory relation. The source category states repleteness. The leaf still lists
the functor explicitly. Only functors in `structure_functors()` contribute inherited
methods.
