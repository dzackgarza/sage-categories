Yes. My earlier “do not change the category” statement was wrong.

An exact positive result should self-refine the owned object. Its mathematical identity remains unchanged. Its category and Sage dynamic class become more specific.

### Predicate resolution

For a property \(P\) with property subcategory \(C_P\), use this order:

| Current knowledge | Result | Action |
|---|---|---|
| \(f\) already lies in \(C_P\) | `True` | The \(C_P\) implementation wins through the MRO |
| Exact result was cached | Cached result | Reuse it |
| The active session assumes \(P(f)\) | `True` | Skip computation |
| The active session assumes \(\neg P(f)\) | `False` | Skip computation |
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

If the computation returns exact `True`, the kernel uses Sage’s category-refinement machinery:

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

### Assumptions versus computations

A temporary session assumption should short-circuit the query. It should not cause an irreversible refinement by itself.

```python
assume(injective(f))
f.is_injective()  # True without computation
```

Sage permits assumptions to be forgotten or temporarily scoped. Permanent self-refinement would survive `forget()`. It would then retain category placement whose only support had disappeared.

There are two ways to make the placement durable:

- An exact computation proves the property.
- The user explicitly constructs or promotes the map into the property category.

Thus:

```python
MonoArrows(Sets)(A, B)(rule)
```

trusts injectivity permanently because the user selected that category. This is different from a temporary active assumption about an existing ordinary map.

### Negative and unknown results

A negative result cannot refine into `MonoArrows(Sets)`. The engine should cache that exact result through standard Sage or SymPy caching facilities.

A complementary category should exist only when it has mathematical value. It should not exist merely to cache `False`.

Do not treat `Unknown` as a durable mathematical fact. A later assumption, realization, or algorithm can make the predicate decidable.

For expensive alternative procedures, use separate named total methods. Do not add `check=`, `algorithm=`, or fallback arguments. The ordinary predicate can use the canonical procedure. A caller can request a specific expensive procedure explicitly.

The corrected invariant is:

> Exact positive knowledge monotonically refines the owned object’s category. Category placement then supplies the predicate through inheritance.

The private SymPy, Sage, GAP, or other engine value never self-refines. The category-owned public morphism does.
