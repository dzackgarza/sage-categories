Yes. This should become the uniform property-refinement architecture.

The crucial correction is this: knowledge can improve lazily, but an object must not mutate into another category.

For an owned predicate \(P\) and its property category \(C_P\):

| Route | Meaning | Result |
|---|---|---|
| Construct in \(C\) | Assert no property | Ordinary object of \(C\) |
| Check \(P(x)\) | Run available exact algorithms | `True`, `False`, or `Unknown` |
| Assume \(P(x)\) | Work under hypothesis \(P(x)\) | Refined object relative to that context |
| Construct in \(C_P\) | Trust the explicitly chosen property constructor | Object of \(C_P\) |
| Named construction theorem | The construction establishes \(P\) | Unconditional object of \(C_P\) |

Thus a set-map constructor assumes neither injectivity nor surjectivity. Its predicate methods can compute those properties lazily.

A monomorphism constructor has different semantics. Choosing `MonoArrows(Sets)(A, B)` explicitly asserts injectivity. It need not enumerate \(A\) or prove the assertion computationally. The target category already states the claimed mathematics.

Likewise, for fixed posets \(P,Q\),

\[
\operatorname{Hom}_{\mathbf{Poset}}(P,Q)
\subseteq
\operatorname{Hom}_{\mathbf{Set}}(U(P),U(Q))
\]

is selected by the order-preserving predicate. Constructing directly in the left-hand Hom can trust monotonicity. Constructing the underlying set map does not.

The two construction surfaces should use one kernel mechanism:

1. Construct the underlying object or arrow.
2. Establish or assume the owned predicate.
3. Create its canonical image in the property category.
4. Cache that image without changing the original value.

Therefore, “lazy refinement” means lazy creation of a canonical refined image. It does not mean changing `f.category()` after `f.is_injective()` runs.

An assumption API is useful, but strings are the wrong representation. This:

```python
assume(f, "is_injective")
```

should instead use an applied mathematical predicate:

```python
injective(f)
order_preserving(f)
total_order(X)
```

A scoped context can then contain these propositions:

```python
context = AssumptionsContext(injective(f))
```

The kernel can use the same proposition for:

- `f.is_injective(context)`;
- containment in the monomorphism category;
- hypothesis-backed refinement;
- inference through composition;
- dispatch to SymPy, Sage, GAP, or another internal engine.

The context must remain explicit and scoped. A process-global `assume()` would let hypotheses escape their mathematical context.

There are also two distinct meanings of “trusted”:

- A user-supplied hypothesis is true relative to an assumption context.
- A named construction theorem gives an unconditional object of the property category.

For example, the identity map is injective by its construction. It needs no assumption. An arbitrary callable placed into `MonoArrows(Sets)` uses a trusted hypothesis unless a checked constructor proves injectivity.

`f.is_injective()` should perform one uniform knowledge query:

1. Category placement can establish `True`.
2. An explicit hypothesis can establish contextual `True`.
3. An explicit negative hypothesis can establish contextual `False`.
4. Exact handlers can compute `True` or `False`.
5. Inference rules can derive a result.
6. Otherwise, return `Unknown`.

If an exact computation contradicts an active hypothesis, the context is inconsistent. The kernel must report that conflict. It must not silently prefer either result.

This removes fields such as:

```python
injective=UNKNOWN
surjective=UNKNOWN
```

Those properties are not construction data. They are owned predicates over the resulting arrow.

The remaining policy gap is important. Existing rules distinguish checked, hypothesis-backed, and theorem-backed admission. They do not yet fully specify:

- that every refinement property has one owned applied predicate;
- that its property category and predicate are the same mathematical condition;
- that direct property-category construction is an explicit trust boundary;
- that lazy computation creates canonical refined images without mutation;
- that assumptions remain scoped during composition and transport;
- that contradictory assumptions fail explicitly;
- that leaves declare only the new predicate and its mathematical inference rules.

That kernel design would cover injectivity, surjectivity, monotonicity, totality, finiteness, commutativity, invertibility, and similar category-defining properties.
