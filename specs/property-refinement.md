# Property refinement

A property subcategory owns its membership proposition.
The same proposition supports decision, global assumption, direct construction, and same-object refinement.
See [undecidable-properties.md](undecidable-properties.md) for the complete axiom and decision-procedure architecture.

The governing policies are `POL-MATH-016`, `POL-MATH-025`, `POL-MATH-029`, `POL-MATH-034`, `POL-MATH-035`, `POL-CAT-018` through `POL-CAT-020`, `POL-CAT-043`, `POL-CAT-044`, `POL-CAT-060`, `POL-CAT-067` through `POL-CAT-069`, `POL-CAT-082`, `POL-CAT-086` through `POL-CAT-091`, and `POL-FUN-024` through `POL-FUN-027`.

An established positive property should self-refine the owned object.
Direct property construction, an active assumption, and an exact computation all establish the same refinement.
The object's mathematical identity remains unchanged.
Its category and Sage dynamic class become more specific.

### Predicate resolution

For a property \(P\) with property subcategory \(C_P\), use this order:

| Current knowledge | Result | Action |
| --- | --- | --- |
| \(f\) already lies in \(C_P\) | `True` | Category placement entails the membership proposition |
| The active session assumes \(P(f)\) | `True` | Refine \(f\) into \(C_P\) without computation |
| The active session assumes \(\neg P(f)\) | `False` | Skip computation |
| Exact result was cached | Cached result | Reuse it |
| An exact computational route establishes \(P(f)\) | `True` | Refine \(f\) into \(C_P\) |
| An exact computational route establishes \(\neg P(f)\) | `False` | Cache the negative result |
| Available algorithms cannot decide | `Unknown` | Keep the current category |

The defining property category adds real mathematics.
Its role implementations can add operations valid under the property.
They never replace the defining proposition with a Boolean method.
Membership in `Mor(Sets()).Monomorphisms()` makes `ask()` return `True` through category entailment.

### Durable refinement

Suppose an ordinary owned set morphism uses a private SymPy representation.

```python
f = Mor(Sets())(A, B)(rule)
ask(f.is_injective())
```

If the computation returns exact `True`, the kernel uses Sage’s category-refinement machinery.
The same refinement also occurs when the user assumes injectivity or constructs the morphism directly in the property category:

```python
f = Mor(Sets())(A, B)(rule)
assume(f.is_injective())
```

```python
f = Mor(Sets()).Monomorphisms()(A, B)(rule)
```

All three routes establish:

\[
\operatorname{Mor}(\mathbf{Set})(A,B)
\longrightarrow
\operatorname{Monomorphisms}(\operatorname{Mor}(\mathbf{Set}))(A,B).
\]

The same owned morphism now has the more specific category.
Its refined dynamic class places the monomorphism implementation before the general set-morphism implementation.

The next `ask(f.is_injective())` call terminates at category placement.
It does not repeat the SymPy computation.

The refinement must preserve:

- object identity;

- domain and codomain;

- the callable rule;

- the private engine representations;

- existing structural images.

It changes the strongest known category and the resulting public method surface.

If surjectivity is later established, the kernel refines again.
It uses the categorical join of the established property categories.
In `Sets()`, established injectivity and surjectivity can place the map in the isomorphism category.

### Equivalent refinement routes

An active assumption triggers property refinement without running the decision procedure.

```python
f = Mor(Sets())(A, B)(rule)
assume(f.is_injective())
```

This is a shortcut for constructing the same rule in the property category:

```python
f = Mor(Sets()).Monomorphisms()(A, B)(rule)
```

The kernel reuses the existing domain, codomain, rule, private engine representation, and structural images.
It does not recompute injectivity.
It changes the owned morphism's category and dynamic class.

There are three routes to the same placement:

- The user constructs the rule directly in the property category.

- The active mathematical session assumes the property of an existing morphism.

- An exact computation establishes the property.

The routes differ only in how the property becomes established.
They must use the same kernel refinement operation and produce the same canonical owned morphism.

The active Sage or SymPy session remains the mathematical context.
A consumer does not maintain a separate assumption-context object.
After refinement, category placement supplies exact `True` to `ask()`.

### Negative and unknown results

A negative result cannot refine into `Mor(Sets()).Monomorphisms()`. The engine should cache that exact result through standard Sage or SymPy caching facilities.

A complementary category should exist only when it has mathematical value.
It should not exist merely to cache `False`.

Do not treat `Unknown` as a durable mathematical fact.
A later assumption, realization, or algorithm can make the predicate decidable.

Every exact computational route belongs behind the owning predicate.
`ask()` selects applicable routes from their declared semantic domains.
Its call has no route-selection parameters.
The public API consists of the predicate and `ask()`.

The invariant is:

> Established positive knowledge monotonically refines the owned object’s category.
> Category placement then entails the property category's membership proposition.

The private SymPy, Sage, GAP, or other engine value never self-refines.
The category-owned public morphism does.

Property refinement is not transport into a second implementation.
It is not a family of admission constructors.
It strengthens the category of the same owned value.

### One constructor per property category

For a property \(P\) defining \(C_P\), the property category owns the trusted constructor:

```python
f = Mor(Sets()).Monomorphisms()(A, B)(rule)
```

That constructor accepts the semantic data needed for a monomorphism.
Choosing the category asserts injectivity.
The evidence source does not change the constructor.

The four public routes are:

| Route | Operation |
| --- | --- |
| Direct property construction | Call the \(C_P\) constructor |
| Interactive assumption | `assume(C_P.membership_proposition(f))` invokes the same \(C_P\) refinement |
| Exact computation | A `True` result invokes the same \(C_P\) refinement |
| Named mathematical construction | Return directly through the \(C_P\) constructor |

A named mathematical construction can still have its own API because it accepts different mathematical data.
It does not exist merely to select “the theorem route.”

### Backend code does not call `assume()`

The Sage or SymPy session owns the global assumption context.
A notebook user can write:

```python
assume(Mor(Sets()).Monomorphisms().membership_proposition(f))
```

The standard spelling `assume(f.is_injective())` applies the same owned predicate.
Both forms record the standard assumption and refine \(f\) through `Mor(Sets()).Monomorphisms()`.

Internal code does something different:

- An exact computational route that returns `True` refines into `Mor(Sets()).Monomorphisms()`.

- An identity constructor constructs into `Mor(Sets()).Monomorphisms()`.

- A theorem-backed construction constructs into `Mor(Sets()).Monomorphisms()`.

- A product lift constructs its projections in the required property category.

Backend code does not create contexts or call `assume()` to justify its own output.
It already knows the category in which it must construct the result.

### Property refinement is not structural transport

A structural functor can create another owned implementation:

\[
F:C\longrightarrow D,\qquad x\longmapsto F(x).
\]

That operation can require canonical images and preimages.

Property refinement is a subcategory monomorphism:

\[
C_P\hookrightarrow C.
\]

The refined value remains the same owned value.
Refinement changes:

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

There is no target wrapper.
There is no separate ambient implementation.
There is no property-refinement image cache.

After refinement, the property category contributes only the operations valid under its defining mathematics.
The ambient `is_X()` predicate still returns the category-owned proposition.

### Strongest property placement and one-object categories

Construct each owned value in the strongest property-based subcategory established by its construction.
A programmer can establish a property by selecting that trusted subcategory constructor.
This is a mathematical assertion in the implementation.
It does not require the general decision procedure to recompute the property.

A named-object construction places its result directly in every property category established by the construction.
It does not override a predicate method or run the general decision procedure.

Property refinements must propagate through the category graph.
If a category `C` defines a property subcategory `C.P()` and `D` is structurally a subcategory of `C`, the kernel must derive `D.P()` as the corresponding narrowing of `D`. A leaf must not define another property class, constructor, predicate, or transport route.
Sage's `with_axiom` mechanism is the design precedent: a property constructor defined once becomes available on descendant categories.

Thus an expression such as

```python
Fields().Countable().PartiallyOrdered()
```

denotes the strongest combined category stated by those refinements.
Its construction must receive any mathematical data introduced by a structure and must retain every property already established.
The expression must not cause repeated property checks.

A distinguished named object is represented by its parameterized one-object category.
For example, the category `{QQ}` has `QQ` as its sole object.
It declares the structural functors that place `QQ` in countable sets, partially ordered sets, and fields.
The field route then supplies its ring structure.
Construction of `QQ` places the sole object in the strongest combined category declared by these functors.

Likewise, `{FF_p}` is a one-object category parameterized by the prime `p`. Its defining construction declares finiteness.
It never derives finiteness by enumeration, cardinality computation, or backend inspection.
It constructs `FF_p` directly in the finite property subcategory.

For an interactive claim not owned by a construction, the user can apply the sanctioned global assumption operation, such as `assume(Sets().Finite().membership_proposition(X))`. The owned predicate method permits `assume(X.is_finite())`. Both forms invoke the same property-category constructor.
Backend and theory code still construct directly in the category they establish; they do not call `assume()`.

## Proposition interface

### Predicates return propositions

Most mathematical truth-valued operations are owned predicates.
Applying one returns an unevaluated proposition.
It does not return `True`, `False`, `Decision`, or `Unknown`.

A specification can instead declare a direct decision when an exact total algorithm is part of that operation's public meaning.
This is an explicit exception.
It does not change the default predicate contract.

This rule applies to:

- object properties such as finiteness, countability, totality, and connectedness;

- morphism properties such as injectivity, surjectivity, monotonicity, and invertibility;

- functor properties such as fullness, faithfulness, full faithfulness, and essential surjectivity;

- equality, order, inclusion, and incidence propositions;

- relation laws and construction obligations;

- category-membership propositions;

- every other operation specified as an owned predicate.

For example:

```python
finite_proposition = X.is_finite()
injective_proposition = f.is_injective()
monotone_proposition = f.is_order_preserving()
total_proposition = P.is_total()
```

Each result retains its predicate, semantic arguments, and mathematical owner.
In SymPy terminology, the predicate is the function and the returned proposition is an `AppliedPredicate`. A Sage symbolic relation such as `x < 2` plays the same role.

`Unknown` is not a proposition.
It is one possible result of asking for the truth value of a proposition:

```python
proposition = X.is_finite()
decision = ask(proposition)
```

The result of `ask(proposition)` is exactly one of:

- `True`, when the active mathematics establishes the proposition;

- `False`, when the active mathematics establishes its negation;

- `Unknown`, when neither conclusion is established.

The kernel translates an engine-specific indeterminate result, such as SymPy `None`, to Sage's `sage.misc.unknown.Unknown` singleton.
No public propositional method returns that value itself.

### Functor predicates

Every functor is an object of `Fun = Mor(Cat())`. Functor properties therefore use the same property-subcategory mechanism as object and morphism properties:

```python
FullFunctors = Mor(Cat()).Full()
FaithfulFunctors = Mor(Cat()).Faithful()
FullyFaithfulFunctors = Mor(Cat()).FullyFaithful()
```

The owning methods return applied predicates:

```python
F.is_full()
F.is_faithful()
F.is_fully_faithful()
```

Direct construction in one of these categories establishes the property.
An interactive assumption refines the same owned functor:

```python
F = Fun(C, D)(on_object, on_morphism)
assume(F.is_full())
```

The kernel also applies established implications.
Placement in `Mor(Cat()).FullyFaithful()` entails both fullness and faithfulness.

These functor predicates have no computational routes.
In the absence of category placement, an active assumption, or an applicable implication, `ask(F.is_full())` returns `Unknown`.

### Fixed-endpoint predicates

For every category `C` and objects `A, B in C`, `Mor(C)(A, B)` is a category.
Its existence does not depend on a decision about its objects.

The fixed-endpoint category owns these predicates:

```python
H = Mor(C)(A, B)

H.is_inhabited()
H.is_empty()
```

They state mutually negated propositions.
Their evaluations can both remain unresolved:

```python
ask(H.is_inhabited())  # True, False, or Unknown
ask(H.is_empty())      # True, False, or Unknown
```

A constructed object of `H` establishes inhabitation.
Exact emptiness establishes that no such object exists.
`Unknown` preserves the same symbolic fixed-endpoint category.

An implementation must not replace an unresolved fixed-endpoint category with an empty category.
This rule applies to thin categories and to general categories.

### Assertions ask predicates

An assertion states that its condition is known to be true.
Therefore, an assertion on an applied predicate must ask it:

```python
assert ask(proposition) is True
```

Do not rely on the proposition's Python truth value.
A direct exact decision can appear in an assertion without another `ask()` call.

### Assumption and decision use one proposition

The same proposition supports assumption and decision:

```python
proposition = X.is_finite()
assume(proposition)
ask(proposition)
proposition.assume()
```

`assume(proposition)` and `proposition.assume()` use the active Sage or SymPy session.
They do not evaluate a Boolean-returning method first.
They record the proposition with its semantic argument intact.

If the proposition defines a property subcategory, a positive assumption invokes that subcategory's trusted constructor and self-refines the same owned value.
An exact `True` result from `ask()` invokes the same constructor.
Direct construction and named mathematical construction already enter through that constructor.

Thus these routes still converge:

```python
assume(f.is_injective())
ask(f.is_injective())
Mor(Sets()).Monomorphisms()(A, B)(rule)
```

Backend and theory code do not call `assume()` for facts they own.
They construct the result directly in the strongest established category.
Interactive users call `assume()` when they want the active mathematical context to supply the proposition.

### Property categories supply evaluation rules

A property subcategory does not override its propositional method with Boolean `True`. The method always returns the same kind of proposition:

```python
f.is_injective()
# Applied proposition: injective(f)
```

Category placement contributes an exact evaluation rule:

```python
ask(f.is_injective())
# True when f is already in Mor(Sets()).Monomorphisms()
```

The evaluation order is:

1. Return `True` when category placement establishes the proposition.

2. Return the active positive or negative assumption when one exists.

3. Reuse an exact cached decision when one exists.

4. Run the owned exact handlers and engine algorithms.

5. On exact `True`, invoke the property-category constructor and return `True`.

6. On exact `False`, retain the negative decision and return `False`.

7. Otherwise, return `Unknown` without changing category placement.

This order belongs to `ask()`, its predicate handlers, and the generic refinement kernel.
A leaf method only constructs the proposition.

### Comparisons and membership use different Python protocols

Python permits a rich comparison such as `x < 2` to return a symbolic relation.
Sage therefore passes that unevaluated relation to `assume()`.

Python forces the `in` operator to return a Boolean.
Even if `__contains__()` returns a proposition when called directly, `X in C` converts it to `True` or `False`. Therefore, `assume(X in C)` can never preserve category membership as a proposition.

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

Every category declares one membership proposition as part of its mathematical definition.
A property category declares the predicate that defines the property.
A category formed from several properties declares the conjunction of the relevant propositions.
The declaration occurs once; `__contains__()` never reimplements the mathematics.

For example, the finite-set category owns its membership proposition.
Its `X.is_finite()` method applies that predicate.
Conceptually:

```python
class FiniteSetsCategory:
    def membership_proposition(self, X: SetObject) -> Proposition:
        return self.applied_predicate(
            X,
            definition=(
                Sets().membership_proposition(X)
                & X.cardinality().is_finite()
            ),
        )
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
    return decision is True
```

This collapse is permitted only inside a Python containment boundary.
It occurs because Python requires set and category containment to be Boolean.
The proposition remains unknown.
The kernel does not cache a negative decision, infer the negated property, or construct a complementary category from this boundary result.

Consequently:

```python
X.is_finite()           # proposition
ask(X.is_finite())      # True, False, or Unknown
X in Sets().Finite()    # Boolean admission query
```

When the decision is `Unknown`, the last expression is `False` because membership is not established.
It does not assert that `X` is mathematically infinite.
Likewise, `X not in Sets().Finite()` means that current knowledge does not place `X` in that category; it does not establish the negated property.

Compound property categories use the same rule.
For example, membership in `Fields().Countable().PartiallyOrdered()` asks one conjunction built from the defining propositions.
Exact positive knowledge places the object in the strongest combined category without repeated checks.

### Sage and SymPy own the assumption model

Use the existing Sage and SymPy mechanisms:

- Sage symbolic relations retain propositions and implement `.assume()`;

- Sage generic declarations support standard and user-defined symbolic features;

- SymPy `Predicate` defines a predicate function;

- SymPy `AppliedPredicate` retains the applied proposition;

- SymPy `ask()` evaluates under registered handlers and active assumptions;

- the standard global assumption state records interactive hypotheses.

The repository supplies the semantic bridge from its owned objects and categories to these standard proposition mechanisms.
It does not create another assumption context, string registry, proof token, predicate metadata system, or Boolean fallback system.
Engine conversion remains private.
The public proposition retains the owned mathematical arguments and never exposes an engine representation choice.

The external contracts are [Python comparison and membership semantics](https://docs.python.org/3/reference/expressions.html#comparisons), [Sage symbolic assumptions](https://doc.sagemath.org/html/en/reference/calculus/sage/symbolic/assumptions.html), and [SymPy predicates, applied predicates, and assumptions](https://docs.sympy.org/latest/modules/assumptions/assume.html).
