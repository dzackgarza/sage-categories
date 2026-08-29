# Propositions, typed queries, and `ask()`

This specification owns propositions, typed queries, evaluation, assumptions, and exact handlers.
It implements D48 through D52, D82, D87 through D90, D97, D99, and D103.

See [property-refinement.md](property-refinement.md) for property categories, inverse images, containment, and same-object refinement.

## Propositions

A predicate application is a proposition.
It can be evaluated, assumed, negated, and combined with other propositions.

For a property category `C.P()`, these expressions construct the same owned proposition:

```python
C.P().membership_proposition(X)
X.is_P()
```

Construction does not evaluate the proposition.
The public method returns the proposition, never a Python decision.

Owned equality also returns a proposition:

```python
p = a == b
decision = ask(p)
```

Use `ask(a == b)` at every decision site.
Python truth protocols do not preserve a possible `Unknown` result.

Propositions compose through conjunction, disjunction, negation, and implication.
The operators `&`, `|`, and `~` delegate to the corresponding SymPy Boolean operations.

## Typed queries

A typed query asks for a value in an exact result category.
It is not Boolean.

For example:

```python
q = X.cardinality()
value = ask(q)
```

Here `q` is an applied query with result category `Cardinal()`.
The result of `ask(q)` is an owned cardinal or `Unknown`.
`Unknown` is not an object of `Cardinal()`.

Cardinality, cofinality, rank, suprema, infima, maxima, minima, and extrema use typed queries when their value can be undecidable or undefined.
A comparison with a query result can construct a proposition.

An applied query has no Python truth value.
It does not compose through propositional operators.

## Evaluation

Only `ask()` evaluates a proposition or an applied query.

For a proposition, `ask()` returns:

```text
True | False | Unknown
```

For a query with result category `R`, `ask()` returns:

```text
an object of R | Unknown
```

Evaluation uses this information in order:

1. exact category placement or an active assumption;
2. an exact cached result;
3. the registered exact handlers at the proposition or query owner;
4. `Unknown` when the available mathematics does not decide the application.

An exact positive property result invokes the same-object refinement specified in [property-refinement.md](property-refinement.md).
An exact negative result and `Unknown` add no property placement.

`Decision` is the result of proposition evaluation.
It has no Boolean-algebra operations.
Compose propositions before evaluation.

## Assumptions

`assume(p)` records an owned proposition in the active Sage or SymPy assumption state.
`retract(p)` withdraws a recorded proposition when it created no permanent category placement.

```python
p = X.is_finite()
assume(p)
ask(p)
```

A positive property assumption refines the same owned value into its property category.
Category placement remains established after that refinement.

An ambient mathematical hypothesis is a proposition of arity zero.
It uses the same assumption state and refines no owned value.

Theory code and computation engines do not use assumptions as evidence for results they construct.
Interactive users use assumptions to add hypotheses to the current mathematical context.

## Exact handlers

Each proposition or query owner registers its exact handlers.
The handler receives the complete application and either returns an exact result or declines to decide it.

A handler can:

- use category placement;
- inspect owned mathematical data;
- ask exact subquestions;
- call a mature computation engine;
- apply a cited theorem whose hypotheses are established.

A proposition handler returns `True`, `False`, or `Unknown`.
A query handler returns an object of its exact result category or `Unknown`.

Handlers compose propositions before calling `ask()`.
They do not fold proposition results through `all`, `any`, `and`, `or`, or `not`.

An expensive exact handler can remain unevaluated until `ask()` reaches it.
Its cache key is the owned application and the applicable assumption state.
The handler has no side effect other than an exact cache entry and positive property refinement.

## Category containment

Every category owns a membership proposition for a supplied value.
Property categories use their defining predicate as that proposition.

The Python expression

```python
X in C
```

is a forced protocol boundary.
It calls `ask(C.membership_proposition(X))` and converts only that final decision to `bool`.

Use the proposition directly when the mathematical context must preserve `Unknown`:

```python
p = C.membership_proposition(X)
assume(p)
```

Placement in `C` is a fast positive answer because construction or refinement already established membership.
Placement is not the definition of membership.

## Twin-prime set

Let

\[
X=\{n\in\mathbb N\mid n\text{ and }n+2\text{ are prime}\}.
\]

Membership is decidable for each supplied natural number.
Current mathematics does not decide whether `X` is finite.
It also does not determine its cardinality.

```python
11 in X                  # True
ask(X.is_finite())       # Unknown
ask(X.cardinality())     # Unknown
```

The first line uses the set-membership protocol for one supplied index.
The other lines evaluate distinct global applications.

See MathWorld's [Twin Primes](https://mathworld.wolfram.com/TwinPrimes.html) for the conjecture and the distinction from bounded-gap results.

## Public paths

| Expression | Result before evaluation | Evaluation result |
| --- | --- | --- |
| `C.P().membership_proposition(X)` | proposition | `True`, `False`, or `Unknown` |
| `X.is_P()` | the same proposition | `True`, `False`, or `Unknown` |
| `X.cardinality()` | applied query in `Cardinal()` | owned cardinal or `Unknown` |
| `C.P()(X)` | owned value placed in `C.P()` | no evaluation |
| named construction into `C.P()` | owned value placed in `C.P()` | no evaluation |
| `X in C.P()` | Python protocol result | `bool` |

## Acceptance conditions

The evaluation architecture satisfies this specification when:

- every truth-valued mathematical method returns a proposition;
- every partial value-valued method returns an applied query with an exact result category;
- constructing an application performs no evaluation;
- only `ask()` returns a decision or a query result;
- propositions compose before evaluation;
- owned equality is decided through `ask()`;
- assumptions record owned propositions in the standard active context;
- exact handlers live at the proposition or query owner;
- positive property decisions use same-object refinement;
- negative and unknown property decisions add no placement;
- category containment asks the owned membership proposition at the Python protocol boundary;
- an unavailable result remains `Unknown` and never becomes an object of the result category.
