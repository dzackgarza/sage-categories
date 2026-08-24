> **Normative precedence.** The final section, [Normative proposition
> interface](#normative-proposition-interface), supersedes earlier Boolean and
> `Decision` return signatures. The earlier discussion is retained because its
> ownership, refinement, construction, and assumption conclusions remain required.

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

### Strongest property placement and one-object categories

Construct each owned value in the strongest property-based subcategory established by
its construction. A programmer can establish a property by selecting that trusted
subcategory constructor. This is a mathematical assertion in the implementation. It
does not require the general decision procedure to recompute the property.

The category-owned implementation of a named object can also override a defining
predicate to return `True`. This states that every value built by that implementation
has the property. The ordinary predicate rule then invokes the same property-category
constructor and self-refines the value. The override is not a proof object, metadata,
or a second admission path.

Property refinements must propagate through the category graph. If a category `C`
defines a property subcategory `C.P()` and `D` is structurally a subcategory of `C`,
the kernel must derive `D.P()` as the corresponding narrowing of `D`. A leaf must not
define another property class, constructor, predicate, or transport route. Sage's
`with_axiom` mechanism is the design precedent: a property constructor defined once
becomes available on descendant categories.

Thus an expression such as

```python
Fields().Countable().PartiallyOrdered()
```

denotes the strongest combined category stated by those refinements. Its construction
must receive any mathematical data introduced by a structure and must retain every
property already established. The expression must not cause repeated property checks.

A distinguished named object is represented by its parameterized one-object category.
For example, the category `{QQ}` has `QQ` as its sole object. It declares the structural
functors that place `QQ` in countable sets, partially ordered sets, and fields. The field
route then supplies its ring structure. Construction of `QQ` places the sole object in
the strongest combined category declared by these functors.

Likewise, `{FF_p}` is a one-object category parameterized by the prime `p`. Its defining
construction declares finiteness. It never proves finiteness by enumeration, cardinality
computation, or backend inspection. It constructs `FF_p` in the finite property
subcategory, or its category-owned finite predicate returns `True` and triggers the same
refinement.

For an interactive claim not owned by a construction, the user can apply the sanctioned
global assumption operation, such as `assume(finite(X))`. That operation also invokes
the same property-category constructor. Backend and theory code still construct directly
in the category they establish; they do not call `assume()`.

## Normative proposition interface

This section supersedes every earlier predicate signature in this document that returns
`bool`, `Decision`, or `Unknown`. It also supersedes every earlier example in which a
property-category implementation replaces a predicate method with a Boolean constant.
The earlier discussion remains relevant for property ownership, strongest category
placement, same-object refinement, named constructions, and the global mathematical
context.

### Propositional methods return propositions

Every public mathematical method whose result is a proposition returns an unevaluated
proposition. It never returns `True`, `False`, `Decision`, or `Unknown` directly.

This rule applies to:

- object properties such as finiteness, countability, totality, and connectedness;
- arrow properties such as injectivity, surjectivity, monotonicity, and invertibility;
- equality, order, inclusion, and incidence propositions;
- relation laws and construction obligations;
- category-membership propositions;
- every other method whose mathematical codomain is truth values.

For example:

```python
finite_proposition = X.is_finite()
injective_proposition = f.is_injective()
monotone_proposition = f.is_order_preserving()
total_proposition = P.is_total()
```

Each result retains its predicate, semantic arguments, and mathematical owner. In
SymPy terminology, the predicate is the function and the returned proposition is an
`AppliedPredicate`. A Sage symbolic relation such as `x < 2` plays the same role.

`Unknown` is not a proposition. It is one possible result of asking for the truth value
of a proposition:

```python
proposition = X.is_finite()
decision = ask(proposition)
```

The result of `ask(proposition)` is exactly one of:

- `True`, when the active mathematics establishes the proposition;
- `False`, when the active mathematics establishes its negation;
- `Unknown`, when neither conclusion is established.

The kernel translates an engine-specific indeterminate result, such as SymPy `None`,
to the owned `Unknown`. No public propositional method returns that value itself.

### Assumption and decision use one proposition

The same proposition supports assumption and decision:

```python
proposition = X.is_finite()
assume(proposition)
ask(proposition)
proposition.assume()
```

`assume(proposition)` and `proposition.assume()` use the active Sage or SymPy session.
They do not evaluate a Boolean-returning method first. They record the proposition with
its semantic argument intact.

If the proposition defines a property subcategory, a positive assumption invokes that
subcategory's trusted constructor and self-refines the same owned value. An exact
`True` result from `ask()` invokes the same constructor. Direct construction and named
mathematical construction already enter through that constructor.

Thus these routes still converge:

```python
assume(f.is_injective())
ask(f.is_injective())
MonoArrows(Sets)(A, B)(rule)
```

Backend and theory code do not call `assume()` for facts they own. They construct the
result directly in the strongest established category. Interactive users call
`assume()` when they want the active mathematical context to supply the proposition.

### Property categories supply evaluation rules

A property subcategory does not override its propositional method with Boolean `True`.
The method always returns the same kind of proposition:

```python
f.is_injective()
# Applied proposition: injective(f)
```

Category placement contributes an exact evaluation rule:

```python
ask(f.is_injective())
# True when f is already in MonoArrows(Sets)
```

The evaluation order is:

1. Return `True` when category placement establishes the proposition.
2. Return the active positive or negative assumption when one exists.
3. Reuse an exact cached decision when one exists.
4. Run the owned exact handlers and engine algorithms.
5. On exact `True`, invoke the property-category constructor and return `True`.
6. On exact `False`, retain the negative decision and return `False`.
7. Otherwise, return `Unknown` without changing category placement.

This order belongs to `ask()`, its predicate handlers, and the generic refinement
kernel. A leaf method only constructs the proposition.

### Comparisons and membership use different Python protocols

Python permits a rich comparison such as `x < 2` to return a symbolic relation. Sage
therefore passes that unevaluated relation to `assume()`.

Python forces the `in` operator to return a Boolean. Even if `__contains__()` returns a
proposition when called directly, `X in C` converts it to `True` or `False`. Therefore,
`assume(X in C)` can never preserve category membership as a proposition.

The explicit proposition remains available through the category definition:

```python
membership_proposition = C.membership_proposition(X)
assume(membership_proposition)
```

An owned property method can provide the standard user syntax:

```python
assume(X.is_finite())
```

### Category membership is proposition-backed Boolean admission

Every category declares one membership proposition as part of its mathematical
definition. A property category declares the predicate that defines the property. A
category formed from several properties declares the conjunction of the relevant
propositions. The declaration occurs once; `__contains__()` never reimplements the
mathematics.

For example, the kernel can expose the finite-set category as `Sets().Finite()` and
associate it with the proposition returned by `X.is_finite()`. Conceptually:

```python
class FiniteSetsCategory:
    def membership_proposition(self, X: SetObject) -> Proposition:
        return Sets().membership_proposition(X) & X.is_finite()
```

The kernel supplies the Boolean protocol:

```python
def __contains__(self, candidate: Any) -> bool:
    proposition = self.membership_proposition(candidate)
    decision = ask(proposition)
    if decision is Unknown:
        logger.info(
            "Category membership is not established. Returning False."
        )
        return False
    return decision
```

This collapse is permitted only inside a Python containment boundary. It occurs because
Python requires set and category containment to be Boolean. The proposition remains
unknown. The kernel does not cache a negative decision, infer the negated property, or
construct a complementary category from this boundary result.

Consequently:

```python
X.is_finite()           # proposition
ask(X.is_finite())      # True, False, or Unknown
X in Sets().Finite()    # Boolean admission query
```

When the decision is `Unknown`, the last expression is `False` because membership is
not established. It does not assert that `X` is mathematically infinite. Likewise,
`X not in Sets().Finite()` means that current knowledge does not place `X` in that
category; it is not a proof of the negated property.

Compound property categories use the same rule. For example, membership in
`Fields().Countable().PartiallyOrdered()` asks one conjunction built from the defining
propositions. Exact positive knowledge places the object in the strongest combined
category without repeated checks.

### Sage and SymPy own the assumption model

Use the existing Sage and SymPy mechanisms:

- Sage symbolic relations retain propositions and implement `.assume()`;
- Sage generic declarations support standard and user-defined symbolic features;
- SymPy `Predicate` defines a predicate function;
- SymPy `AppliedPredicate` retains the applied proposition;
- SymPy `ask()` evaluates under registered handlers and active assumptions;
- the standard global assumption state records interactive hypotheses.

The repository supplies the semantic bridge from its owned objects and categories to
these standard proposition mechanisms. It does not create another assumption context,
string registry, proof token, predicate metadata system, or Boolean fallback system.
Engine conversion remains private. The public proposition retains the owned
mathematical arguments and never exposes an engine representation choice.

The external contracts are [Python comparison and membership
semantics](https://docs.python.org/3/reference/expressions.html#comparisons), [Sage
symbolic assumptions](https://doc.sagemath.org/html/en/reference/calculus/sage/symbolic/assumptions.html),
and [SymPy predicates, applied predicates, and
assumptions](https://docs.sympy.org/latest/modules/assumptions/assume.html).
