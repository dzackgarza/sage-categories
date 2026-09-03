# Propositions, typed queries, and `ask()`

This specification owns the public question and evaluation contract.
It implements D18 through D25, D63, D83, D89, D97, D115, and D125.

It consumes property categories from [property-refinement.md](property-refinement.md).
It provides propositions, typed queries, assumptions, equality, and evaluation.

## Mathematical questions

A predicate is a proposition-valued mathematical operation.
Its category, property category, or equality operation owns its meaning.

A typed query is a partial value-valued mathematical operation.
Its owner declares one exact result category.

Forming either question performs no evaluation.
Only `ask()` evaluates it.

## Public propositions

A proposition is a SymPy Boolean expression.
A predicate that no existing method supplies has a SymPy `Predicate` subclass its owner defines; applying it returns a SymPy `AppliedPredicate`.
Compound propositions use SymPy `And`, `Or`, `Not`, and `Implies`.

For a property category `C.P()`, the deciding proposition is a private method of the declaring category (D142), and `cat_kernel` generates its one public spelling:

```python
X.is_P()
```

The property category owns the predicate meaning.
SymPy owns the public predicate class, application class, and Boolean algebra.

An owned value enters a SymPy expression through a private identity atom.
The atom preserves the value's identity and gives the handler access to that value.
The atom has no independent public API.

## Equality

Each exact category owns equality for its objects, elements, and morphisms.
That owner defines a SymPy predicate and its exact handlers.

```python
p = a == b
decision = ask(p)
```

`a == b` returns the applied category-owned predicate.
It does not return a Python Boolean or a SymPy `Eq`.
`a != b` returns `Not(a == b)`.

Equality decisions do not cause property refinement.
A Python protocol that requires a Boolean must call `ask()` and reject `Unknown`.

## Typed queries

A typed query owns its argument contract and exact result category.
Application returns an owned unevaluated query application.

```python
q = X.cardinality()
value = ask(q)
```

Here the result category is `Cardinal()`.
Evaluation returns an owned cardinal or Sage `Unknown`.
`Unknown` is not an object of `Cardinal()`.

Cardinality, cofinality, rank, suprema, infima, maxima, minima, and extrema use typed queries when their result can be undecided or undefined.
A comparison of a typed query with an object of its result category, such as `X.cardinality() < aleph0`, is a proposition that `ask()` evaluates (D18).

## Evaluation

Public `ask()` has two branches.

For a SymPy proposition, it calls `sympy.ask()`.
It returns the resulting `True` or `False`.
It maps SymPy `None` to Sage `Unknown`.

For a typed query, it calls the exact evaluator owned by that query.
It returns an object of the declared result category or Sage `Unknown`.

An exact positive property result invokes the same-object refinement in [property-refinement.md](property-refinement.md).
An exact negative result and `Unknown` add no category placement.

The repository has no second proposition evaluator, proposition cache, connective hierarchy, or proposition handler graph.

## Proposition handlers

Each mathematical predicate registers exact handlers through SymPy.
A handler receives the arguments of the applied predicate, here the private identity atom of the owned value, and the active SymPy assumptions; SymPy 1.14.0 `Predicate.eval` calls `self.handler(*args, assumptions=assumptions)` (`sympy/assumptions/assume.py`, inspected 2026-09-03).
It returns `True`, `False`, or `None`.

A handler matches positively, with `match` and `case`, on the cases it can decide and returns `None` for every other case.
The leaf writer extends coverage by adding cases.
A case can use an exact computational construction that decides the predicate for that case.
A case can ask an exact subquestion through `ask()`; SymPy owns the safety of the resulting evaluation cycle (D151).

Handler domains are exact and unambiguous.
The predicate owner supplies their mathematical meaning.
SymPy supplies their dispatch and evaluation.

Typed-query evaluators remain at the query owner.
Their private dispatch mechanism has no mathematical authority.

## Assumptions

SymPy `global_assumptions` owns the active proposition context.
Public `assume(p)` adds the SymPy proposition `p` to that context.
Public `retract(p)` removes it from that context.

A positive property assumption also refines the same owned value.
This assumption, `assume(X.is_P())`, is the placement route for a value already constructed; a constructor takes construction data (D150).
Removing the assumption does not reverse established category placement.

An ambient hypothesis is a zero-argument SymPy predicate application.
It uses the same assumption context and refines no value.

Theory code and computation engines do not add assumptions for results they construct.
They construct those results in the exact category their mathematics establishes.

## Category containment

Every category owns a membership proposition for a supplied value.
For a property category `C.P()` that proposition is `X.is_P()`.

The Python expression `X in C` is a forced two-valued protocol boundary.
It calls `ask()` on that proposition (`POL-ONT-003`).
It converts only a decided result to `bool`.

Placement in `C` is an exact positive result.
Placement is not the definition of membership.

Property containment is a declared subcategory monomorphism.
It is not an implication registry between predicates.
Proposition implication uses SymPy `Implies`.

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

See MathWorld's [Twin Primes](https://mathworld.wolfram.com/TwinPrimes.html).

## Public paths

| Expression | Unevaluated value | Result from `ask()` |
| --- | --- | --- |
| `X.is_P()` | SymPy proposition | `True`, `False`, or `Unknown` |
| `a == b` | Category-owned SymPy proposition | `True`, `False`, or `Unknown` |
| `X.cardinality()` | Typed query with result category `Cardinal()` | Owned cardinal or `Unknown` |
| `X in C.P()` | Python `bool` | Not applicable |

## Acceptance conditions

The architecture satisfies this specification when:

- each truth-valued method returns a SymPy proposition;
- each predicate meaning has one mathematical owner;
- SymPy owns proposition application, composition, assumptions, dispatch, and evaluation;
- private identity atoms expose no independent public value;
- `ask()` maps only undecided SymPy results to Sage `Unknown`;
- each partial value-valued method has one exact result category;
- a comparison of a typed query with an object of its result category is a proposition;
- every equality operation uses its exact category-owned predicate;
- positive property results refine the same value;
- property containment uses declared monomorphisms;
- category containment asks the same membership proposition;
- no unavailable result becomes an object of its result category.
