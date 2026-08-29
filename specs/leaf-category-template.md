# Leaf category template

Replace each `Leaf`, `Base`, and `defining_data` name with its mathematical name.
Keep only methods introduced by the leaf structure.

This template implements D118 and `POL-LEAF-014`.
It is design pseudocode, not an importable framework API.

## The four leaf questions

A leaf answers four questions:

1. What are its objects, elements, and morphisms?

2. What defining data does its default constructor accept, and which other semantic constructors are useful?

3. Which immediate named functors supply inherited structure, and how does each convert constructor data?

4. Which operations, predicates, algorithms, and theorems first belong to this category?

The explicit structure functors contain most leaf-level transport work.
Each gives its complete object and morphism actions.
Each selected functor also gives the exact object, element, and morphism constructor conversions that it contributes.
The kernel turns those declarations into class inheritance and initialized state.

```python
class LeafCategory(Category):
    class ObjectType:
        def __init__(self, defining_data: LeafDefiningData) -> None:
            self._defining_data = defining_data
            super().__init__()

        def leaf_operation(self) -> LeafResult:
            """Return the result introduced by this structure."""
            ...

    class ElementType:
        """Implement points of leaf objects."""

    class MorphismType:
        """Implement leaf morphisms."""

    def __call__(self, defining_data: LeafDefiningData) -> ObjectType:
        return self.ObjectType(defining_data)

    def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
        """Return the selected immediate functors."""
        ...
```

`Category` is `Cat().ObjectType`. Each entry in `structure_functors()` is an explicitly constructed object of `Fun = Mor(Cat())`. Include only immediate functors whose target catalogue supplies the leaf's inherited public surface.

## Default and named constructors

For a category object `C`, the call `C(defining_data)` is its expected object constructor.
It accepts the smallest complete semantic datum that normally defines one object.
Named constructors accept other meaningful presentations or engine-ingestion inputs:

```python
C(defining_data)
C.from_alternative_presentation(other_data)
C.from_sage(engine_value)
```

All routes construct `C.ObjectType`.
They do not select different public implementations.
A property-category call `C.P()(data)` asserts the defining property and constructs in that same registered category.
An existing owned value passed to `C.P()` uses same-object refinement.

## What `Cat` supplies

The leaf reuses these generic constructions and their retained functors:

```python
Fun(C, D)
Mor(C)(X, Y)
C.op()

C.Products()
C.Coproducts()
C.Limits(I)
C.Colimits(I)
C.SliceOver(X)
C.CosliceUnder(X)
C.MonoOver(X)
C.MonoUnder(X)
C.EpiOver(X)
C.EpiUnder(X)

Comma(F, G)
F.inverse_image(P)
F.restrict(P, Q)
p.Fiber(b)
F.base_change(p)
Grothendieck(P)
```

The construction that creates a product, pullback, comma category, slice, fiber, or Grothendieck construction retains its projections and comparison data.
The leaf selects those functors from the retained presentation.
It writes a new `Fun(self, Target)` object only when it introduces a new mathematical action.

The kernel supplies class compilation, constructor threading, inherited method execution, property inverse images, generated `is_P()` methods, the positive-decision refinement connection, same-object refinement, and public type projection.
Sage and SymPy supply the session assumption context.
An ordinary leaf contains none of that machinery.

For each target class contributed by a selected structure functor, the leaf states which
target constructor consumes the converted source construction data. The target category can
have many constructors. The kernel uses the selected functor's construction rule to
initialize the target class on the source instance.
Point actions use ordinary composition for functors between the categories that carry the points.
Compiled `ElementType` inheritance uses the selected structure functor's exact element-constructor conversion.

A leaf specification links each inherited construction to its generic specification.
Its construction section states only the added leaf structure, predicates, exact algorithms, and private engine realizations.
The generic specification owns the shape, index, diagram, cone or cocone, defining morphisms, universal morphism, and presentation operations.

A subcategory monomorphism uses the constructor on its fixed-endpoint functor category.
A product, pullback, comma, `Fun([1], C)`, or other category construction creates and retains its named projection functors.
A leaf reuses those exact objects.

Present structured categories as subobjects of sequence products when their objects have named components.
The generic `Cat().MonoOver(P)` construction then supplies `product_projection(i)`. The leaf selects the applicable indices without restating maps.

For another functor, the leaf supplies its complete object and morphism actions through `Fun(self, Target)`. It selects the strongest established property subcategory before construction.
The endpoints never select a functor by themselves.

For a structured object with several defining components, select only components used as its inherited public structure.
Other component functors remain ordinary functors.
This selection has the same purpose as Sage's `super_categories()` declaration.

## Standard construction-defined patterns

### Pullback-defined categories

A category that combines compatible structures uses the projections retained by its defining pullback.
For example, `Rings(C)` selects the semiring and additive-group projections.
Its leaf adds only their compatibility condition.

```python
def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
    return (
        self.product_projection(0),  # semiring projection
        self.product_projection(1),  # additive-group projection
    )
```

### Categories with selected data

For `P: C.op() -> Cat()`, `Grothendieck(P)` owns the category of pairs `(X, datum)` and its projection `p` to `C`.
A specialization adds only the API of the selected datum:

```python
class BasedObjects(Grothendieck(Bases)):
    class ObjectType:
        def basis(self) -> Basis:
            return self.chosen_datum()

    class ElementType:
        pass

    class MorphismType:
        pass

    def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
        return (p,)
```

Existence of some datum is a property.
An object together with one selected datum is an object of the total category.
Presentations, bases, generating sets, and realizations use this distinction.

### Universal-construction realizations

A leaf can realize a limit by adding only its local structure to the inherited cone.
When a named structure functor creates the limits, the leaf places that functor in `.CreatesLimits(I)`.
The generic construction then supplies the lifted cone and universal maps.

```python
U = Fun(self, C).CreatesLimits(I)(on_object, on_morphism)

def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
    return (U,)
```

The leaf does not rebuild the construction category, diagram, legs, mediator, caching, or descendant interface.

## Named exemplars

| Category | Leaf-local mathematical delta |
| --- | --- |
| [`Sets()`](sets.md) | set membership, total-map evaluation, and set realizations of generic constructions |
| [`Sets().Finite()`](finite-set-minimal-template.py) | axiom registration, the defining finiteness proposition, and finite-set-only operations |
| [`PartiallyOrderedSets()`](poset-minimal-template.py) | an owned relation subobject, the order laws, and monotone-map mathematics |
| [`Magmas(V)`, `Monoids(V)`, and `Groups(V)`](magmas-monoids-semirings.md) | structure morphisms and their laws; notation subcategories add the conventional point operators |
| [`Semirings(C)`](magmas-monoids-semirings.md) and [`Rings(C)`](rings.md) | compatibility of structures reached through retained product or pullback projections |
| [`Modules(A, C)`](modules.md) | the action morphism, module laws, and the retained projection to `C` |

These specifications are the full mathematical owners.
The snippets here show only the common leaf shape.

## Property subcategories and predicate handlers

A category declares an axiom `P` to make the functorial construction `C |-> C.P()`
available. The kernel constructs the monomorphism `C.P() -> C` and generates `is_P()`
on `C.ObjectType`.

A concrete category can register itself as the implementation of `C.P()` through Sage's
axiom mechanism. If it supports computed refinement, inherit `PredicateSubcategory` and
implement its private abstract `_predicate()` method:

```python
class PObjects(PredicateSubcategory):
    _base_category_class_and_axiom = (CClass, "P")

    def _predicate(self, x: C.ObjectType) -> Proposition:
        return property_formula(x)
```

The registration string supplies `P` in the generated `is_P()` spelling. The kernel
converts CamelCase to snake case and prefixes `is_`. The concrete category does not name
that public method separately.

The generic base defines the containment proposition from membership in `C` and this
predicate. The registered class is `C.P()` itself. It is not a second category.
Descendants receive `is_P()` through compiled inheritance. The leaf declares no ambient
method.

Use the same proposition for decisions and interactive assumptions:

```python
proposition = x.is_P()
decision = ask(proposition)
assume(proposition)
proposition.assume()
```

The leaf does not implement `ask()`, `assume()`, or `Proposition.assume()`. The kernel implements them.
Direct construction in `C.P()` asserts the property.
An exact `True` decision or a positive assumption refines the same owned object through the kernel mechanism.

Bind computational procedures at the property-category integration site.
Put their engine work in a private backend module:

```python
C.P().register_exact_handler(C.ObjectType, decide_P_for_C_objects)
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

## Value-valued query cases

A partial invariant keeps one public query operation at its mathematical owner.
A theorem for a specific construction registers an exact evaluation case there.
It does not add another public method to the constructed leaf.

For the set exponential `Y ** X`, the set realization owns the theorem

\[
\lvert Y^X\rvert=\lvert Y\rvert^{\lvert X\rvert}.
\]

Its exact case asks the two operand cardinality queries.
It returns the resulting owned cardinal when both values are available.
Otherwise, it returns `Unknown`.
Thus `(RR ** RR).cardinality()` remains the ordinary applied cardinality query.
`ask()` uses the exponential theorem without any method on `RR` or on a special function-set leaf.

A construction-specific external theorem follows the same rule.
Place the cited case at the narrowest mathematical construction owner.
Keep engine work in its private boundary and reconstruct the owned query result there.

See [functor.md](functor.md) for subcategory-monomorphism, projection, evaluation, and induced-functor declarations.

See [finite-set-minimal-template.py](finite-set-minimal-template.py) for a property subcategory.
See [poset-minimal-template.py](poset-minimal-template.py) for objects with additional structure and an explicit set projection.
