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

    def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
        """Return the selected immediate structural functors."""
        ...
```

`Category` is `Cat().ObjectType`. Each entry in `structure_functors()` is an explicitly constructed object of `Fun = Mor(Cat())`. Include only immediate functors whose target catalogue supplies the leaf's inherited public surface.

For each inherited operation, the selected functor must construct every required object and morphism image.
The compiler does not invent missing maps.

The functor connects the category-owned implementation roles.
Its object and morphism maps construct the corresponding target roles.
A concrete functor category can add an element action when its mathematics supplies one.

A subcategory monomorphism uses the constructor on its fixed-endpoint functor category.
A product, pullback, comma, `Fun([1], C)`, or other category construction creates and retains its named projection functors.
A leaf reuses those exact objects.

Present structured categories as subobjects of sequence products when their objects have named components.
The generic `Cat().Products().ChosenSubobjects()` construction then supplies `product_projection(i)`. The leaf selects the applicable indices without restating maps.

For another functor, the leaf supplies its complete object and morphism actions through `Fun(self, Target)`. It selects the strongest established property subcategory before construction.
The endpoints never select a functor by themselves.

For a structured object with several defining components, select only components used as its inherited public structure.
Other component functors remain ordinary functors.
This selection has the same purpose as Sage's `super_categories()` declaration.

## Property subcategories and predicate handlers

A property subcategory owns its membership predicate.
The ambient object method only constructs that proposition:

```python
def is_P(self) -> Proposition:
    return C().P().membership_proposition(self)
```

Use the same proposition for decisions and interactive assumptions:

```python
proposition = x.is_P()
decision = ask(proposition)
assume(proposition)
proposition.assume()
```

The leaf does not implement `ask()`, `assume()`, or `Proposition.assume()`. The predicate kernel owns those operations.
Direct construction in `C().P()` asserts the property.
An exact `True` decision or a positive assumption refines the same owned object through that property-category constructor.

Bind computational procedures at the property-category integration site.
Put their engine work in a private backend module:

```python
C().P().register_exact_handler(C.ObjectType, decide_P_for_C_objects)
```

The backend entry point positively matches only the semantic cases that it supports:

```python
def decide_P_for_C_objects(x: C.ObjectType) -> Decision:
    match x:
        case SupportedConstruction(defining_data=data):
            return decide_supported_construction(data)
        case AnotherSupportedConstruction(defining_data=data):
            return decide_another_supported_construction(data)
        case _:
            return Unknown
```

Add support by adding a new `case`. Do not start from unsupported cases.
Do not replace this form with an `if` cascade.
The wildcard case is the only fallback and returns `Unknown`.

The handler returns `True`, `False`, or `Unknown`. It does not call `assume()`, refine an object, construct a property category, or mutate the mathematical context.
The generic `ask()` path owns those effects after it receives the decision.

For example, one exact set-map handler can support symbolic real endomorphisms:

```python
def decide_surjective_set_map(f: Sets().MorphismType) -> Decision:
    match (f.domain(), f.codomain()):
        case (number_sets.RR, number_sets.RR):
            return sympy_sets.decide_exact_image_equals_reals(f)
        case _:
            return Unknown


Mor(Sets()).Epimorphisms().register_exact_handler(
    Sets().MorphismType,
    decide_surjective_set_map,
)
```

The private SymPy procedure constructs the exact owned image and compares it with `RR`. It returns `Unknown` when SymPy does not determine the image.
This handler belongs to `Mor(Sets()).Epimorphisms()` because it decides surjectivity.
An injectivity handler belongs to `Mor(Sets()).Monomorphisms()` and uses an exact injectivity procedure.

See [functor.md](functor.md) for subcategory-monomorphism, projection, evaluation, and induced-functor declarations.

See [finite-set-minimal-template.py](finite-set-minimal-template.py) for a property subcategory.
See [poset-minimal-template.py](poset-minimal-template.py) for objects with additional structure and an explicit set projection.
