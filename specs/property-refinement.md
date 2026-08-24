Yes. My earlier “do not change the category” statement was wrong.

An established positive property should self-refine the owned object. Direct property construction, an active assumption, and an exact computation all establish the same refinement. The object's mathematical identity remains unchanged. Its category and Sage dynamic class become more specific.

### Predicate resolution

For a property \(P\) with property subcategory \(C_P\), use this order:

| Current knowledge | Result | Action |
|---|---|---|
| \(f\) already lies in \(C_P\) | `True` | The \(C_P\) implementation wins through the MRO |
| The active session assumes \(P(f)\) | `True` | Refine \(f\) into \(C_P\) without computation |
| The active session assumes \(\neg P(f)\) | `False` | Skip computation |
| Exact result was cached | Cached result | Reuse it |
| An exact algorithm proves \(P(f)\) | `True` | Refine \(f\) into \(C_P\) |
| An exact algorithm disproves \(P(f)\) | `False` | Cache the negative result |
| Available algorithms cannot decide | `Unknown` | Keep the current category |

The defining property category adds real mathematics. Therefore, this override is valid:

```python
class Monomorphism(...):
    def is_injective(self) -> bool:
        return True
```

It is not duplicate engineering code. Membership in `MonoArrows(Sets)` mathematically implies injectivity.

### Durable refinement

Suppose an ordinary owned set morphism uses a private SymPy representation.

```python
f = Hom(Sets)(A, B)(rule)
f.is_injective()
```

If the computation returns exact `True`, the kernel uses Sage’s category-refinement machinery. The same refinement also occurs when the user assumes injectivity or constructs the morphism directly in the property category:

```python
f = Hom(Sets)(A, B)(rule)
assume(injective(f))
```

```python
f = MonoArrows(Sets)(A, B)(rule)
```

All three routes establish:

\[
\operatorname{Hom}_{\mathbf{Set}}(A,B)
\longrightarrow
\operatorname{MonoArrows}(\mathbf{Set})(A,B).
\]

The same owned morphism now has the more specific category. Its refined dynamic class places the monomorphism implementation before the general set-morphism implementation.

The next call reaches the constant `True` method through the MRO. It does not repeat the SymPy computation.

The refinement must preserve:

- object identity;
- domain and codomain;
- the callable rule;
- the private engine representations;
- existing structural images.

It changes the strongest known category and the resulting public method surface.

If surjectivity is later proved, the kernel refines again. It uses the categorical join of the established property categories. In `Sets()`, established injectivity and surjectivity can place the map in the isomorphism category.

### Equivalent refinement routes

An active assumption triggers property refinement without running the decision procedure.

```python
f = Hom(Sets)(A, B)(rule)
assume(injective(f))
```

This is a shortcut for constructing the same rule in the property category:

```python
f = MonoArrows(Sets)(A, B)(rule)
```

The kernel reuses the existing domain, codomain, rule, private engine representation, and structural images. It does not recompute injectivity. It changes the owned morphism's category and dynamic class.

There are three routes to the same placement:

- The user constructs the rule directly in the property category.
- The active mathematical session assumes the property of an existing morphism.
- An exact computation establishes the property.

The routes differ only in how the property becomes established. They must use the same kernel refinement operation and produce the same canonical owned morphism.

The active Sage or SymPy session remains the mathematical context. A consumer does not maintain a separate assumption-context object. After refinement, the property-category implementation supplies `True` through the MRO.

### Negative and unknown results

A negative result cannot refine into `MonoArrows(Sets)`. The engine should cache that exact result through standard Sage or SymPy caching facilities.

A complementary category should exist only when it has mathematical value. It should not exist merely to cache `False`.

Do not treat `Unknown` as a durable mathematical fact. A later assumption, realization, or algorithm can make the predicate decidable.

For expensive alternative procedures, use separate named total methods. Do not add `check=`, `algorithm=`, or fallback arguments. The ordinary predicate can use the canonical procedure. A caller can request a specific expensive procedure explicitly.

The corrected invariant is:

> Established positive knowledge monotonically refines the owned object’s category. Category placement then supplies the predicate through inheritance.

The private SymPy, Sage, GAP, or other engine value never self-refines. The category-owned public morphism does.

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
