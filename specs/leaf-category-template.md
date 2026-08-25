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

`Category` is `Cat().ObjectType`. Each entry in `structure_functors()` is an explicitly
constructed object of `Fun = Ar(Cat())`. Include only immediate functors whose target
catalogue supplies the leaf's inherited public surface.

For each inherited operation, the selected functor must construct every required object
and arrow image. The compiler does not invent missing maps.

The functor connects the category-owned implementation roles. Its object and arrow maps
construct the corresponding target roles. A concrete functor category can add an element
action when its mathematics supplies one.

An inclusion uses the constructor on its fixed-endpoint functor category. A product,
pullback, comma, arrow, or other category construction creates and retains its named
projection functors. A leaf reuses those exact objects.

Present structured categories as subobjects of sequence products when their objects have
named components. The generic `Cat().Products().Subobjects()` construction then supplies
`product_projection(i)`. The leaf selects the applicable indices without restating maps.

For another functor, the leaf supplies its complete object and arrow actions through
`Fun(self, Target)`. It selects the strongest established property subcategory before
construction. The endpoints never select a functor by themselves.

For a structured object with several defining components, select only components used as
its inherited public structure. Other component functors remain ordinary functors. This
selection has the same purpose as Sage's `super_categories()` declaration.

See [functor.md](functor.md) for inclusion, projection, evaluation, and induced-functor
declarations.

See [finite-set-minimal-template.py](finite-set-minimal-template.py) for a property
subcategory. See [poset-minimal-template.py](poset-minimal-template.py) for objects with
additional structure and an explicit set projection.
