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

    def structure_functors(self) -> tuple[Functor, ...]:
        """Return the selected immediate structural functors."""
        ...

    def contains_leaf(self, candidate: MathematicalObject) -> TypeIs[LeafObject]:
        return candidate in self
```

`structure_functors()` selects inheritance routes. It is not a catalogue of all functors
from the leaf. Include only immediate functors whose target catalogue should become part
of the leaf's public surface. The leaf must also meet each functor's construction
obligations for objects, elements, and arrows. Keep all other mathematical functors
outside this tuple.

For each inherited operation, the selected functor must construct every receiver and
argument image that the operation needs. It must also support any required result
reconstruction. The compiler does not invent missing maps. See
[the construction obligation](functor.md#the-construction-obligation).

The functor connects the category-owned implementation roles. Its object map constructs
the canonical target `ObjectType`. Its arrow and element maps do the same for their roles.
A bespoke functor can use any public constructor route owned by its codomain. The functor
fixes that route; the runtime does not search for one.

Standard inclusions and projections already implement this contract in the kernel. The
leaf only selects them. It does not add forwarding initializers, conversion methods, or
delegating copies of inherited operations.

For a structured object with several defining components, select only the component used
as its inherited public structure. The existence of another projection does not make that
projection a structure functor. This selection has the same purpose as Sage's
`super_categories()` declaration.

See [functor.md](functor.md) for inclusion, forgetting, projection, and induced-functor
declarations.

See [finite-set-minimal-template.py](finite-set-minimal-template.py) for a property
subcategory. See [poset-minimal-template.py](poset-minimal-template.py) for objects with
additional structure and a kernel-owned carrier projection.
