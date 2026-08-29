# Leaf category template

Replace `Leaf`, `Target`, and each datum name with its exact mathematical name.
Keep only mathematics introduced by the leaf.

This template implements D118 through D123, `POL-LEAF-014`, `POL-LEAF-061`, `POL-LEAF-062`, and `POL-API-028`.
It illustrates the contracts in [leaves.md](leaves.md) and [functor.md](functor.md).
It does not define another contract.

## Leaf questions

A leaf answers four questions:

1. What are its objects, elements, and morphisms?
2. What complete datum constructs one object or morphism?
3. Which immediate named functors supply inherited structure?
4. Which operations, predicates, algorithms, and theorems first belong here?

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

`Category` is `Cat().ObjectType`.
The three nested classes state the complete local implementation surface.
An empty class adds no local operation for that mathematical kind.

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

A new leaf functor contains complete executable object and morphism actions.
Each action constructs its public target value directly.

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

The two actions are the sole declaration of this functor.
Selection in `structure_functors()` makes the applicable target implementation classes available on source values.

A helper used only by one action stays local to that action or private to the leaf.
A datum with independent public mathematical meaning keeps its public name.

## Functors retained by constructions

Return an existing retained functor when the defining construction already owns it.
Examples include:

- a product projection;
- a pullback projection;
- a comma-category projection;
- an evaluation functor from `Fun([1], C)`;
- a subcategory monomorphism;
- the projection from a Grothendieck construction.

```python
def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
    return (
        self.defining_presentation().product_projection(0),
        self.defining_presentation().product_projection(1),
    )
```

The leaf does not reconstruct a retained functor.
Ordinary functors that supply no inherited implementation remain unselected.

## Construction owners

Use the category that owns each result:

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

The defining construction retains all projections, evaluations, and universal morphisms.
One apex can have several presentations.
An operation that depends on one presentation stays on that presentation object.

## Property categories

A leaf declares a property axiom once.
The registered identifier determines the generated `is_P()` method.
A predicate-backed property category supplies its defining private `_predicate()` method.

See [property-refinement.md](property-refinement.md) for the category construction and refinement.
See [undecidable-properties.md](undecidable-properties.md) for propositions, typed queries, and handlers.
See [finite-set-minimal-template.py](finite-set-minimal-template.py) for the one complete property example.

## Private computation

A category-owned method can use a mature engine behind a private boundary.
It constructs an owned mathematical result before it returns.

```python
def leaf_operation(self, argument: LeafArgument) -> LeafResult:
    engine_input = self._sage_input(argument)
    engine_result = established_engine_operation(engine_input)
    return LeafResults()(engine_result)
```

The public method names the mathematics.
The caller does not select the engine.

## Checklist

- The leaf states only its new mathematical data and operations.
- `ObjectType`, `ElementType`, and `MorphismType` have their exact names.
- The default constructor accepts one complete defining datum.
- Each new functor has complete object and morphism actions.
- Each functor action constructs an owned target value.
- `structure_functors()` returns only immediate named functors that supply inheritance.
- Retained construction functors are reused directly.
- Universal data remains on its presentation object.
- Property declarations link to their canonical specification.
- Every public signature uses exact mathematical types.
- Private engine work returns an owned result.
- The leaf imports no kernel internal.
