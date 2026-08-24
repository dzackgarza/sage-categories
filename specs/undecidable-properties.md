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

The missing rule is this:

> Sage’s `with_axiom` machinery can build category intersections and dynamic classes. It cannot define what an axiom means.

The owned kernel must give every property axiom a defining proposition.

## What remains from `with_axiom`

The repository should retain these parts of Sage’s model:

- `Sets().Finite()` constructs a property subcategory.
- Descendants can inherit the property as `C.Finite()`.
- Category joins combine established properties.
- Dynamic classes expose methods added by the refined category.
- `FiniteSets()` and `Sets().Finite()` denote one canonical category.

Sage supports separate and nested implementations of a category with an axiom. It also canonicalizes forms such as `FiniteSets()` and `Sets().Finite()`. [Sage `CategoryWithAxiom` documentation](https://doc.sagemath.org/html/en/reference/categories/sage/categories/category_with_axiom.html)

The repository must not retain the bare-string semantics:

```python
_with_axiom("Finite")
```

The string can remain a private Sage runtime key. It cannot define the mathematics.

## What an owned property axiom means

The owned declaration must bind three things:

\[
\operatorname{Finite}:
\operatorname{Ob}(\mathbf{Set})\to\operatorname{Prop},
\]

\[
X\longmapsto X.\operatorname{is\_finite}(),
\]

and

\[
\mathbf{FiniteSet}
=
\{X\in\mathbf{Set}\mid X.\operatorname{is\_finite}()\}.
\]

Conceptually, the declaration has this shape:

```python
class SetsCategory(Category):
    class ObjectType:
        def is_finite(self) -> Proposition:
            return finite(self)

    class Finite(
        PropertySubcategory,
        defining_proposition=ObjectType.is_finite,
    ):
        class ObjectType:
            # Only mathematics available for known finite sets.
            ...
```

This is a conceptual interface. The important part is the direct method reference:

```python
defining_proposition=ObjectType.is_finite
```

The kernel must not infer this link from either string:

```text
"Finite"
"is_finite"
```

It must not use method-name matching.

The property class states the mathematical equation:

\[
\mathbf{Sets.Finite}
=
\{X\in\mathbf{Sets}\mid X.\operatorname{is\_finite}()\}.
\]

That equation is not engineering metadata. It is the definition of the full subcategory.

## `FiniteSets()` is not a second category

The following identity must hold:

```python
FiniteSets() is Sets().Finite()
```

A separate module can contain the Python definition of the category class. That choice only controls source layout.

It must not create:

- a second finite-set category;
- a second implementation hierarchy;
- a second object constructor;
- a second defining predicate.

`Sets().Finite()` must resolve to the owned `FiniteSets` category implementation.

## No predicate override

`FiniteSets.ObjectType` must not implement this:

```python
def is_finite(self) -> bool:
    return True
```

The kernel must not inject such an override either.

`is_finite()` always has one owner and one return contract:

```python
def is_finite(self) -> Proposition:
    return finite(self)
```

A finite set inherits that same method. Calling it still produces the proposition:

\[
\operatorname{finite}(X).
\]

Category placement supplies an entailment rule:

\[
X\in\mathbf{Sets.Finite}
\Longrightarrow
\operatorname{ask}(X.\operatorname{is\_finite}())=\mathrm{True}.
\]

Thus, the MRO does not establish truth by replacing the method. The proposition engine establishes truth from category placement.

This preserves one public method owner. It also preserves one return type.

## Calling `is_finite()` does not compute

This call only constructs a proposition:

```python
proposition = X.is_finite()
```

It does not:

- query SymPy;
- enumerate `X`;
- change the category;
- return `Unknown`;
- refine `X`.

Computation begins only here:

```python
decision = ask(X.is_finite())
```

Therefore, the state transition is:

```python
X.category()                 # Sets()
X.is_finite()                # Applied proposition; no change
ask(X.is_finite())           # Runs resolution if needed
X.category()                 # Sets().Finite(), if the answer was True
```

The exact category API can expose the strongest category differently. The mathematical transition remains the same.

The containment spelling also invokes `ask()`:

```python
X in Sets().Finite()
```

It asks the defining membership proposition. Therefore, containment can trigger the same lazy computation.

## Direct construction and assumptions

These routes do not compute:

```python
Sets().Finite()(X)
assume(X.is_finite())
```

Both routes invoke the same trusted property refinement.

`Sets().Finite()(X)` means:

> Treat this owned set as a finite set.

`assume(X.is_finite())` means:

> Add this proposition to the global context, then perform the corresponding refinement.

Neither route calls the finiteness decision procedure.

If a later exact computation contradicts that placement, the mathematical context is inconsistent. The kernel must report that conflict.

## What happens during set construction

A constructor must place its result in the strongest category already established by that construction.

It should not launch unrelated property searches.

There are three cases.

### Case 1: The construction theorem establishes finiteness

An explicit finite-set constructor knows that its result is finite:

```python
X = Sets().Finite()(members, cardinality)
```

It constructs directly in `Sets().Finite()`.

It does not call `ask()`.

### Case 2: The backend’s normal result establishes finiteness

Suppose the predicate-set constructor asks SymPy to construct:

\[
X=\{x\in\mathbf{NN}\mid x\leq 10\}.
\]

SymPy might return an exact finite representation, such as a finite range or finite set.

The backend contract then establishes finiteness. The construction boundary reconstructs the owned set directly in `Sets().Finite()`.

If the backend also supplies cardinality \(10\), the owned construction retains that cardinal value.

This is not eager property discovery. The ordinary construction already produced decisive semantic data.

### Case 3: The construction leaves finiteness unresolved

SymPy might retain the set as a `ConditionSet` or another symbolic predicate set.

Then the owned object remains in `Sets()`:

```python
X.category() is Sets()
```

No constructor should launch every available finiteness algorithm merely to strengthen category placement.

A later call to `ask(X.is_finite())` performs that work.

## Where finiteness algorithms belong

The `FiniteSets` leaf does not own algorithms that classify arbitrary sets.

That category owns mathematics valid after finiteness is established.

The classification problem accepts objects of `Sets()`. Therefore, its decision procedures belong to the `finite` predicate defined at `Sets()`.

There can be exact handlers for different semantic constructions:

```text
finite(explicit finite set)
finite(predicate subset)
finite(cartesian product)
finite(coproduct)
finite(SymPy-backed set)
finite(Sage-backed set)
```

The public architecture is conceptually:

```python
finite.register_exact_handler(
    PredicateSubset,
    decide_predicate_subset_finiteness,
)
```

This registration is private predicate-engine integration. It is not a decorator on `is_finite()`.

A handler:

- accepts an owned semantic set;
- lowers it at a private engine boundary;
- uses exact backend facilities;
- returns `True`, `False`, or `Unknown`;
- does not refine the object itself.

The generic `ask()` operation performs refinement after it receives exact `True`.

This separation matters:

```text
decision procedure → Decision
ask()               → logical resolution and refinement
FiniteSets()        → trusted property category
is_finite()         → proposition construction
```

## Where individual handlers live

Use the narrowest mathematical or engine owner.

- A general cardinality implication belongs at `Sets()`.
- A product theorem belongs to the set-product construction.
- A SymPy `ConditionSet` procedure belongs in the private SymPy set boundary.
- A Sage finite-set procedure belongs in the private Sage boundary.
- A named construction places its result directly in the known category.

The `FiniteSets` leaf must not become a central dispatcher with a large case split.

It should not import every engine. It should not inspect private representation types.

A neighboring private engine module can contain the SymPy interaction. The public `Sets.ObjectType` remains the implementation firewall.

## The predicate-subset example

Let

\[
X=\{x\in\mathbf{NN}\mid x\leq 10\}.
\]

A complete lazy route is:

```python
X = Sets().subset_from_predicate(NN, x <= 10)
```

Assume the constructor retains an unresolved symbolic predicate.

Then:

```python
X.category() is Sets()
```

This call constructs only the proposition:

```python
p = X.is_finite()
```

This call starts resolution:

```python
decision = ask(p)
```

`ask()` checks, in order:

1. Existing category placement.
2. Global assumptions.
3. Known categorical implications.
4. Cached exact decisions.
5. Applicable exact handlers.

The predicate-subset handler can then:

1. Lower `X` to its private SymPy representation.
2. Ask SymPy whether the set is finite.
3. Simplify the symbolic set when that operation is exact.
4. Return `True`, `False`, or `Unknown`.

If it returns `True`, `ask()` invokes:

```python
Sets().Finite()(X)
```

Afterward:

```python
X in Sets().Finite()
ask(X.is_finite()) is True
```

The second `ask()` does not repeat the SymPy computation. Category placement settles it.

If the handler returns `Unknown`, `X` remains in `Sets()`.

## Enumeration is not a general handler

This procedure is not suitable for automatic `ask()` dispatch:

```python
for member in X:
    ...
return True
```

It semi-decides finiteness. It terminates for some finite enumerations. It can run forever for infinite sets.

Every automatic decision handler must terminate on its declared input domain. It must return an exact decision or `Unknown`.

A potentially unbounded search requires a separate explicitly named operation. It must not run implicitly through `ask()` or `__contains__`.

If an enumeration carries a certified terminal bound, then the bound already establishes finiteness. No open-ended search is needed.

## How descendant categories receive `Finite()`

Let

\[
U:C\to\mathbf{Sets}
\]

be the selected structural functor.

The kernel defines:

\[
C.\operatorname{Finite}
=
\{X\in C\mid U(X)\in\mathbf{Sets.Finite}\}.
\]

For an owned subcategory of `Sets()`, Sage’s axiom-join machinery can help construct this category and its dynamic role classes.

For a general structural functor, the correct object is an inverse-image property category. It is not only a Python class join.

The kernel must derive:

- `C.Finite()`;
- its inclusion into `C`;
- its structural functor into `Sets().Finite()`;
- its membership proposition;
- its role-class inheritance;
- its trusted constructor;
- its refinement behavior.

The descendant leaf supplies none of this.

If several structural functors give different meanings to “finite,” the category must select the intended functor. The kernel must not infer a route from method names.

## Property axioms and structure additions differ

Not every upstream Sage axiom fits this proposition-defined model.

`Finite` is a property of an existing set. It defines a full subcategory.

`Associative` is a property of an existing magma operation. It can also define a property subcategory.

A construction that adds mathematical data requires more than a proposition. Its arrows can also change.

For example, “has a unit” and “has a chosen unit preserved by arrows” are different categorical statements.

The kernel should therefore distinguish:

- proposition-defined property subcategories;
- categories that add structure or change the arrow notion.

Only the first class receives automatic `ask()`, `assume()`, and property refinement.

## The exact architectural rule

A property axiom declaration supplies:

1. Its largest meaningful base category.
2. Its ordinary proposition-valued public method.
3. Its property-subcategory implementation.
4. A direct link from the category to that method.
5. Its categorical implication rules.
6. Exact decision handlers, when available.

The kernel supplies:

1. `C.P()`.
2. Descendant `D.P()` constructions.
3. `__contains__`.
4. Global-assumption integration.
5. `ask()` dispatch.
6. Positive self-refinement.
7. Dynamic role-class refinement.
8. Canonical category joins.

The property leaf supplies only operations valid because \(P\) is known.

## Current documentation conflict

The current policy still contains the older model.

[CONTRIBUTING.md](/home/dzack/gitclones/sage-categories/CONTRIBUTING.md:265) says the property category overrides its predicate with `True`.

[CONTRIBUTING.md](/home/dzack/gitclones/sage-categories/CONTRIBUTING.md:338) says `X.is_finite()` decides finiteness and refines `X`.

Both statements conflict with the proposition-valued interface.

The correct rules are:

- `X.is_finite()` constructs a proposition.
- `ask(X.is_finite())` decides it.
- Exact `True` refines `X`.
- Category placement makes later `ask()` calls return `True`.
- No leaf or injected MRO method replaces `is_finite()` with a Boolean.
