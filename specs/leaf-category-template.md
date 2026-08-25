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


class LeafCategory(Category):
    ObjectType = LeafObject
    ElementType = LeafElement

    def __call__(self, defining_data: LeafDefiningData) -> LeafObject:
        return self.ObjectType(category=self, defining_data=defining_data)

    def structure_functors(self) -> tuple[Cat().ArrowType, ...]:
        """Return the selected immediate structural functors."""
        ...

    def contains_leaf(self, candidate: MathematicalObject) -> TypeIs[LeafObject]:
        return candidate in self
```

`Category` is `Cat().ObjectType`. Each entry in `structure_functors()` is an already
established object of `Ar(Cat())`. Include only immediate functors whose target
catalogue supplies the leaf's inherited public surface.

For each inherited operation, the selected functor must construct every required object
and arrow image. The compiler does not invent missing maps.

The functor connects the category-owned implementation roles. Its object and arrow maps
construct the corresponding target roles. A concrete functor category can add an element
action when its mathematics supplies one.

The kernel implements standard functor constructions. The leaf calls its category-owned
`inclusion()`, `forget()`, carrier, or projection construction and selects the result.

For a structured object with several defining components, select only the component used
as its inherited public structure. The existence of another projection does not make that
projection a structure functor. This selection has the same purpose as Sage's
`super_categories()` declaration.

See [functor.md](functor.md) for inclusion, forgetting, projection, and induced-functor
declarations.

See [finite-set-minimal-template.py](finite-set-minimal-template.py) for a property
subcategory. See [poset-minimal-template.py](poset-minimal-template.py) for objects with
additional structure and a kernel-owned carrier projection.
