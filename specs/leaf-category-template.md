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

    def __init__(self) -> None:
        self._forgetful_functor: ForgetLeafFunctor | None = None
        super().__init__()

    def __call__(self, defining_data: LeafDefiningData) -> LeafObject:
        return self.ObjectType(category=self, defining_data=defining_data)

    def forgetful_functor(self) -> ForgetLeafFunctor:
        if self._forgetful_functor is None:
            self._forgetful_functor = ForgetLeafFunctor(self, BaseObjects())
        return self._forgetful_functor

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        return (self.forgetful_functor(),)

    def contains_leaf(self, candidate: MathematicalObject) -> TypeIs[LeafObject]:
        return candidate in self
```
