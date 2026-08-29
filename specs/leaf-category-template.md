# Leaf category template

Replace `Leaf`, `Target`, and each datum name with its exact mathematical name.
Keep only mathematics introduced by the leaf.

This template illustrates the local leaf shape specified in [leaves.md](leaves.md).
Functor construction and selection are specified in [functor.md](functor.md).

## Category declaration

```python
class LeafCategory(Category):
    class ObjectType:
        def __init__(self, defining_data: LeafDefiningData) -> None:
            self._defining_data = defining_data

        def leaf_operation(self, argument: LeafArgument) -> LeafResult:
            return compute_leaf_result(self._defining_data, argument)

    class ElementType:
        pass

    class MorphismType:
        pass

    def __call__(self, defining_data: LeafDefiningData) -> ObjectType:
        return self.ObjectType(defining_data)
```

The category declaration adds these local classes and methods.

## Constructors

The default call accepts the smallest complete datum that normally defines one object.
A named constructor accepts another complete mathematical presentation.

```python
C(defining_data)
C.from_presentation(presentation)
C.from_sage(engine_value)
```

Each route returns `C.ObjectType`.
The constructor obtains data already determined by the input from its mathematical owner.

## Structure functor introduced by the leaf

```python
def target_projection(self) -> Cat().MorphismType:
    D = TargetCategory()

    def on_object(X: self.ObjectType) -> D.ObjectType:
        target_data = X.target_data()
        return D(target_data)

    def on_morphism(f: self.MorphismType) -> D.MorphismType:
        source = on_object(f.domain())
        target = on_object(f.codomain())
        target_map = f.target_map()
        return Mor(D)(source, target)(target_map)

    return Fun(self, D)(on_object, on_morphism)

def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
    return (self.target_projection(),)
```

This leaf defines `target_projection()` and selects it for inherited structure.

## Retained functor specimen

```python
def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
    return (
        self.defining_presentation().product_projection(0),
        self.defining_presentation().product_projection(1),
    )
```

These projections belong to `defining_presentation()`.

## Construction specimen

```python
C(data)
Mor(C)(X, Y)(map_data)
Fun(C, D)(on_object, on_morphism)

C.Products()(diagram)
C.Limits(I)(diagram)
C.SliceOver(X)(arrow)
C.Subobjects(X)(monomorphism)

Comma(F, G)
F.inverse_image(P)
F.restrict(P, Q)
p.Fiber(b)
Grothendieck(P)
```

## Property specimen

See [finite-set-minimal-template.py](finite-set-minimal-template.py).
Its category and evaluation behavior comes from [property-refinement.md](property-refinement.md) and [undecidable-properties.md](undecidable-properties.md).

## Private computation specimen

```python
def leaf_operation(self, argument: LeafArgument) -> LeafResult:
    engine_input = self._sage_input(argument)
    engine_result = established_engine_operation(engine_input)
    return LeafResults()(engine_result)
```

The public method returns `LeafResult`.
