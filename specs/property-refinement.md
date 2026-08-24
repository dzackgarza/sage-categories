The two cited clauses expose one larger false model.

Property refinement is not transport into a second implementation. It is not a family of admission constructors. It strengthens the category of the same owned value.

### One constructor per property category

For a property \(P\) defining \(C_P\), the property category owns the trusted constructor:

```python
f = MonoArrows(Sets)(A, B)(rule)
```

That constructor accepts the semantic data needed for a monomorphism. Choosing the category asserts injectivity.

These APIs should not exist:

```python
monos.checked(...)
monos.from_hypothesis(...)
monos.from_theorem(...)
monos.construct(..., check=True)
```

The evidence source does not create another constructor family.

The four public routes are:

| Route | Operation |
|---|---|
| Direct property construction | Call the \(C_P\) constructor |
| Interactive assumption | `assume(P(f))` invokes the same \(C_P\) refinement |
| Exact computation | A `True` result invokes the same \(C_P\) refinement |
| Named mathematical construction | Return directly through the \(C_P\) constructor |

A named mathematical construction can still have its own API because it accepts different mathematical data. It does not exist merely to select “the theorem route.”

### Backend code does not call `assume()`

The Sage or SymPy session owns the global assumption context. A notebook user can write:

```python
assume(injective(f))
```

That public operation records the standard assumption and refines \(f\) through `MonoArrows(Sets)(A, B)`.

Internal code does something different:

- A computation that proves injectivity constructs into `MonoArrows(Sets)`.
- An identity constructor constructs into `MonoArrows(Sets)`.
- A theorem-backed construction constructs into `MonoArrows(Sets)`.
- A product lift constructs its projections in the required property category.

Backend code does not create contexts or call `assume()` to justify its own output. It already knows the category in which it must construct the result.

### Property refinement is not structural transport

`POL-KERNEL-013` currently conflates two different operations.

A structural functor can create another owned implementation:

\[
F:C\longrightarrow D,\qquad x\longmapsto F(x).
\]

That operation can require canonical images and preimages.

Property refinement is an inclusion:

\[
C_P\hookrightarrow C.
\]

The refined value remains the same owned value. Refinement changes:

- its strongest category;
- its Sage dynamic class;
- its MRO;
- its inherited public operations.

Refinement preserves:

- Python identity;
- mathematical identity;
- construction data;
- domain and codomain;
- private engine representations;
- existing structural images.

There is no target wrapper. There is no separate ambient implementation. There is no property-refinement image cache.

After refinement, the property category contributes its defining mathematics:

```python
class Monomorphism(...):
    def is_injective(self) -> bool:
        return True
```

### Required policy changes

The stale surface is larger than two lines.

These assumption policies require correction:

- `POL-ASSUME-004`: remove explicit `AssumptionsContext`.
- `POL-ASSUME-007`: make `assume(P(f))` invoke property refinement.
- `POL-ASSUME-009`: remove public hypothesis-context types.
- `POL-ASSUME-011`: replace explicit contexts with the active Sage or SymPy session.
- The prose following these policies must use the global standard assumption state.

These category and leaf policies also require correction:

- `POL-CAT-069`: remove the separate named hypothesis constructor.
- `POL-LEAF-033`: remove checked, hypothesis-backed, and theorem-backed constructor families.
- `POL-LEAF-035`: state that every established positive predicate invokes the same self-refinement.
- `POL-API-022`: replace route-specific admission methods with property-category constructors.

These kernel policies require correction:

- `POL-KERNEL-002`: separate property self-refinement from structural images.
- `POL-KERNEL-013`: preserve the same object instead of constructing a target implementation.
- `POL-KERNEL-014`: let category-owned role classes contribute to the refined dynamic MRO. Do not create wrappers.

The durable rule should be:

> A property subcategory owns the constructor that trusts its defining property. Direct construction, global assumption, exact computation, and construction-owned mathematics all converge on that constructor and refine the same owned value.
