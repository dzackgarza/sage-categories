The architecture should have one authoritative mathematical declaration:

\[
P:\operatorname{Ob}(C)\to\operatorname{Prop},
\qquad
C.P=\{x\in C\mid P(x)\}.
\]

`is_P()`, `C.P()`, containment, assumptions, computation, and refinement must all derive from this equation.

`is_P()` returns the applied proposition \(P(x)\). It does not evaluate it.

## The six public paths

| Expression | Meaning | Computes? | Refines? |
|---|---|---:|---:|
| `x.is_P()` | Construct \(P(x)\) | No | No |
| `ask(x.is_P())` | Determine \(P(x)\) | Only if needed | On exact `True` |
| `assume(x.is_P())` | Add \(P(x)\) to the global context | No | Immediately |
| `C.P()(x)` | Construct or place `x` directly in \(C.P\) | No | Immediately |
| `x in C.P()` | Ask the defining membership proposition | Possibly | On exact `True` |
| A named construction returning `C.P()` | Apply its construction theorem | No | At construction |

Direct construction and `assume` use the same category-refinement operation. They differ only in provenance:

- `C.P()(x)` is a programmer assertion through the category constructor.
- `assume(P(x))` is an interactive assertion in the global mathematical context.
- A named construction knows \(P(x)\) from its defining theorem.
- `ask(P(x))` tries to derive \(P(x)\) from available knowledge.

No certificate type, authority object, prose theorem, or separate implementation is needed.

## Propositions and decisions

A public predicate method returns a proposition:

```python
proposition = x.is_finite()
```

It never returns `True`, `False`, or `Unknown`.

Only evaluation returns a decision:

```python
decision = ask(proposition)
```

The result is:

```text
True | False | Unknown
```

This matches SymPy’s split between a `Predicate`, an applied predicate, and `ask()`. SymPy also provides type-specific predicate handlers and global assumptions. [SymPy assumptions documentation](https://docs.sympy.org/latest/modules/assumptions/ask.html)

The repository must provide one kernel bridge between that logic and categorical refinement. SymPy does not know the category graph.

## How `ask()` works

For an atomic proposition \(P(x)\), `ask()` uses this order.

1. Inspect category placement.

   If `x` already belongs to \(C.P\), then \(P(x)\) is true.

2. Inspect the global assumption context.

   `assume(P(x))` establishes the proposition without computation.

3. Apply categorical implications.

   Examples include:

   \[
   \mathrm{Finite}\Longrightarrow\mathrm{Countable},
   \]

   and

   \[
   \mathrm{Isomorphism}\Longrightarrow
   \mathrm{Monomorphism}\land\mathrm{Epimorphism}.
   \]

4. Evaluate structural images.

   If \(D.P\) is induced through \(F:D\to C\), evaluate \(P(F(x))\).

5. Consult a cached exact decision.

   Computed facts and user assumptions remain distinct sources of knowledge.

6. Run applicable exact decision procedures.

   These are the last computational stage.

7. Return `Unknown` if no procedure establishes either truth value.

When `ask(P(x))` returns `True`, the kernel refines `x` into \(C.P\). Later queries then stop at category placement.

When it returns `False`, the kernel records the decision. It refines into a complement only when that complement is an actual declared category.

If two trusted sources disagree, the kernel must report an inconsistent mathematical context. It must not choose one source silently.

Backend failures are not mathematical decisions. They propagate as failures. An algorithm may return `Unknown` only when it completed correctly but did not decide the proposition.

## How containment works

Python forces `x in category` to produce a Boolean. It cannot preserve an unevaluated proposition. [Python membership semantics](https://docs.python.org/3/reference/expressions.html#membership-test-operations)

The kernel therefore generates this behavior:

```python
def __contains__(self, candidate: MembershipCandidate) -> bool:
    proposition = self.membership_proposition(candidate)
    decision = ask(proposition)

    if decision is Unknown:
        logger.log("Category membership was not established.")
        return False

    return decision is True
```

The important distinction is:

- `False` from `in` means admission was not established.
- It does not establish the negated mathematical proposition.
- The kernel must not cache `Unknown` as mathematical falsity.

Leaves never implement `__contains__`.

## Property propagation

Suppose \(P\) is defined at category \(C\). Let \(F:D\to C\) be the selected structural functor.

The kernel defines:

\[
D.P=\{x\in D\mid P(F(x))\}.
\]

Therefore:

```python
D.P()
```

is the inverse-image property category \(F^{-1}(C.P)\).

The kernel derives:

- the category constructor;
- the membership proposition;
- the structural functor \(D.P\to C.P\);
- the refined object, element, and arrow types;
- assumption-driven refinement;
- category implications;
- descendant propagation.

A leaf does not copy `is_P()`. It also does not forward it by hand.

This follows the main idea of Sage’s `CategoryWithAxiom`: define an axiom at the largest category where it makes sense. Subcategories then inherit refinements such as `Groups().Finite()`. [Sage category-with-axiom documentation](https://doc.sagemath.org/html/en/reference/categories/sage/categories/category_with_axiom.html)

The repository should retain that mathematics. It should not copy Sage’s string-based axiom registry or method-name discovery.

A derived property needs a selected structural functor. If two routes give different meanings, the category must select one route explicitly.

## `Finite` and `Countable`

These properties first make sense on `Sets()`:

\[
\operatorname{Finite}(X),\qquad
\operatorname{Countable}(X).
\]

Their declarations produce:

```python
Sets().Finite()
Sets().Countable()
```

The implication

\[
\operatorname{Finite}(X)\Longrightarrow\operatorname{Countable}(X)
\]

becomes a category inclusion:

```text
Sets().Finite() ⊆ Sets().Countable()
```

Thus `ask(X.is_countable())` returns `True` immediately when `X` already belongs to `Sets().Finite()`.

For a category \(C\) with a selected underlying-set functor

\[
U:C\to\mathbf{Set},
\]

the kernel defines:

\[
C.\operatorname{Finite}
=
\{x\in C\mid \operatorname{Finite}(U(x))\}.
\]

The same rule defines `C.Countable()`.

A named finite construction goes directly into `C.Finite()`. It does not enumerate itself to prove finiteness.

A generic set may use an exact decision procedure when `ask(X.is_finite())` reaches the computational stage. That procedure can use Sage, SymPy, GAP, Julia, or another engine.

## `Injective`, `Monos`, and `Isos`

These properties live on arrows.

For \(D=\operatorname{Ar}(C)\), the generic categorical propositions are:

\[
\operatorname{Monic}(f),
\qquad
\operatorname{Epic}(f),
\qquad
\operatorname{Isomorphism}(f).
\]

They define:

```python
D.Monos()
D.Epis()
D.Isos()
```

For set maps, there is also the concrete proposition:

\[
\operatorname{Injective}(f).
\]

In `Sets()`, a theorem identifies monomorphisms with injective functions:

\[
\operatorname{Monic}(f)
\iff
\operatorname{Injective}(f).
\]

That equivalence belongs to `Sets()`. It does not define monomorphisms in an arbitrary category.

Likewise, the generic definition of an isomorphism is:

\[
\exists g,\quad
g\circ f=\operatorname{id}
\quad\land\quad
f\circ g=\operatorname{id}.
\]

In `Sets()` one can use:

\[
\operatorname{Isomorphism}(f)
\iff
\operatorname{Injective}(f)\land\operatorname{Surjective}(f).
\]

That converse is category-specific. A monic and epic arrow need not be an isomorphism in every category.

Examples:

```python
f = Hom(Sets())(X, Y, rule)
ask(f.is_injective())       # May compute or return Unknown.

g = Ar(Sets()).Monos()(X, Y, rule)
ask(g.is_injective())       # True from category placement.

assume(f.is_injective())    # Refines f through the same Monos constructor.
```

An identity map constructs directly into `D.Isos()`. It never runs injectivity or surjectivity algorithms.

If an assumed isomorphism lacks a computed inverse, `inverse()` can return the owned symbolic inverse arrow. Category placement establishes its equations. A backend may later realize that arrow computationally.

## Finite posets

A poset is not merely a property of a bare set. Its relation is part of its data.

Start with a category of sets equipped with a binary relation. Then define:

\[
\operatorname{is\_poset}(X,\leq)
\]

as the conjunction of reflexivity, antisymmetry, and transitivity.

The poset category is the property subcategory cut out by that proposition.

Let

\[
U:\mathbf{Poset}\to\mathbf{Set}
\]

be the forgetful functor. Then:

\[
\mathbf{FinitePoset}
=
\mathbf{Poset}.\operatorname{Finite}
=
\{P\in\mathbf{Poset}\mid \operatorname{Finite}(U(P))\}.
\]

Its membership proposition is the conjunction:

\[
\operatorname{is\_poset}(P)
\land
\operatorname{is\_finite}(U(P)).
\]

If `P` already belongs to `PartiallyOrderedSets()`, the first term follows from category placement.

If `P` was directly constructed in `FinitePosets()`, both terms follow from placement.

If `P` is only a relation-bearing object, `ask(P.is_poset())` may run an exact finite-law checker. A positive result refines it into `PartiallyOrderedSets()`.

No finite-poset leaf implements:

- a second finiteness predicate;
- combined refinement code;
- manual routes to `Sets()`;
- a special `__contains__`;
- an assumption method.

## Template for a new property

A new property leaf supplies one mathematical predicate and one defining equation.

Conceptually:

```python
class CObject:
    def is_P(self) -> Proposition:
        return P(self)


class PObjects(PropertySubcategoryOfC):
    defining_proposition = CObject.is_P

    class ObjectType:
        # Only operations introduced by P.
        ...
```

The exact syntax can differ. The semantic requirements cannot.

The direct reference to `CObject.is_P` is important. The compiler must not infer the link from the string `"P"` or the method name `"is_P"`.

From that single link, the kernel generates:

- `C.P()`;
- its constructor;
- its membership proposition;
- `__contains__`;
- `assume` integration;
- positive self-refinement;
- descendant categories such as `D.P()`;
- structural propagation;
- implication closure.

The leaf does not define `assume()` on `ObjectType`. The proposition already supports:

```python
x.is_P().assume()
```

That operation uses the global mathematical context and the predicate-to-category link.

## Where computation handlers belong

`is_P()` does not contain the algorithm.

The predicate owner may provide exact decision procedures. Backend-specific procedures may live behind private engine boundaries.

Conceptually:

```python
P.register_exact_handler(CObject, decide_P_for_C_objects)
```

This is not a decorator on a public mathematical method. It is private integration with the standard predicate-dispatch system.

The handler:

- accepts the semantic object;
- may lower it into Sage, SymPy, GAP, Julia, or another engine;
- returns an exact decision;
- does not construct categories;
- does not mutate assumptions;
- does not implement `__contains__`;
- reconstructs any semantic data before returning it.

No handler is required. Without one, `ask(P(x))` can still succeed from placement, assumptions, implications, or structural images.

## The main boundary

The ownership split is:

- The category layer defines \(P\) and \(C.P\).
- The proposition engine owns logical inference and global assumptions.
- The repository kernel connects positive propositions to category refinement.
- Structural functors propagate properties between categories.
- Computation engines supply exact decision procedures.
- Named constructions place results directly in established categories.
- Leaves state only their new predicate and their new mathematics.

That split makes `C.Finite()`, `C.Countable()`, `D.Monos()`, and `D.Isos()` instances of one mechanism. It avoids four separate engineering designs.
