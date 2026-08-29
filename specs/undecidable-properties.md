The architecture should have one authoritative mathematical declaration:

\[
P:\operatorname{Ob}(C)\to\operatorname{Prop},
\qquad
C.P=\{x\in C\mid P(x)\}.
\]

The axiom `P` declares the functorial construction `C |-> C.P()`.
Each result retains its monomorphism `C.P() -> C`.
`C.P().membership_proposition(x)`, containment, assumptions, computation, and refinement must all derive from this equation.

The kernel derives the standard ambient application, such as `x.is_P()`, from the axiom declaration and the category-owned containment proposition.
It does not evaluate it.

## Public paths

| Expression | Meaning | Computes? | Refines? |
| --- | --- | ---: | ---: |
| `C.P().membership_proposition(x)` | Construct \(P(x)\) | No | No |
| `x.is_P()` | Apply the category-owned predicate to `x` | No | No |
| `ask(C.P().membership_proposition(x))` | Determine \(P(x)\) | Only if needed | On exact `True` |
| `assume(C.P().membership_proposition(x))` | Add \(P(x)\) to the global context | No | Immediately |
| `retract(p)` | Withdraw \(p\) from the global context | No | No |
| `C.P()(x)` | Construct or place `x` directly in \(C.P\) | No | Immediately |
| `x in C.P()` | Ask the defining membership proposition | Possibly | On exact `True` |
| A named construction returning `C.P()` | Apply its construction theorem | No | At construction |

Direct construction and `assume` use the same category-refinement operation.
They differ only in provenance:

- `C.P()(x)` is a programmer assertion through the category constructor.

- `assume(P(x))` is an interactive assertion in the global mathematical context.

- A named construction returns `C.P()` because the code writer knows \(P(x)\) from external mathematics.

- `ask(P(x))` tries to derive \(P(x)\) from available knowledge.

No certificate type, authority object, prose theorem, or separate implementation is needed.

The category constructor trusts the programmer assertion.
It does not prove, certify, or validate the proposition.
When the assertion uses a nontrivial theorem, cite the inspected source on the construction line or in its immediate documentation.
The citation exists for human mathematical audit and never enters runtime state.

### Global hypotheses

A hypothesis of the ambient set theory names no owned value and refines no category.
It is an owned predicate of arity zero, applied and recorded in the same active assumption state as any other proposition.
`assume()` records it and `retract()` withdraws it.
`retract()` applies only to a proposition that recorded no placement: category placement is permanent, so a property assumption does not retract.

A theory module may record such a hypothesis at load, which makes it the package's default state.
`POL-ASSUME-018` governs that case; `POL-ASSUME-011` continues to forbid `assume()` as the justification of a computed result.
The generalized continuum hypothesis is the one such hypothesis this package declares; see [Cardinalities and ordinals](cardinality.md#the-continuum-hypothesis).

## Propositions and decisions

A property category constructs its membership proposition:

```python
proposition = Sets().Finite().membership_proposition(x)
```

The kernel-derived application `x.is_finite()` returns that same proposition.

It never returns `True`, `False`, or `Unknown`.

Only evaluation returns a decision:

```python
decision = ask(proposition)
```

The result is:

```text
True | False | Unknown
```

This matches SymPy’s split between a `Predicate`, an applied predicate, and `ask()`. SymPy also provides type-specific predicate handlers and global assumptions.
[SymPy assumptions documentation](https://docs.sympy.org/latest/modules/assumptions/ask.html)

The repository must provide one kernel bridge between that logic and categorical refinement.
SymPy does not know the category graph.

There is one logic.
Propositions compose under `conjunction`, `disjunction`, `negation`, and `implication`, and under the `&`, `|`, and `~` operators, all of which delegate to `sympy.logic.boolalg`'s `And`, `Or`, `Not`, and `Implies`. An exact handler builds one proposition from its sub-questions and returns `ask` of it; it never folds decisions.
A decided part composes with a proposition, so a handler that compares two private data at the computation boundary needs no separate combinator.
`Decision` is what `ask` returns and nothing more: it has no operations of its own.

## How `ask()` works

For an atomic proposition \(P(x)\), `ask()` uses this order.

1. Inspect category placement.

   If `x` already belongs to \(C.P\), then \(P(x)\) is true.

2. Inspect the global assumption context.

   `assume(P(x))` establishes the proposition without computation.

3. Read the declared subcategory containments.

   Examples include:

   ```text
   Sets().Finite() ⊆ Sets().Countable()
   Mor(C).Isomorphisms() ⊆ Mor(C).Monomorphisms()
   Mor(C).Isomorphisms() ⊆ Mor(C).Epimorphisms()
   ```

   The isomorphisms are a full subcategory of each of the other two simultaneously; that
   is the statement, and there is no conjunction of predicates underneath it (D83).

4. Evaluate images owned by structure functors.

   If \(D.P\) is induced through \(F:D\to C\), evaluate \(P(F(x))\).

5. Consult a cached exact decision.

   Computed facts and user assumptions remain distinct sources of knowledge.

6. Run applicable exact decision procedures.

   These are the last computational stage.

7. Return `Unknown` if no procedure establishes either truth value.

When `ask(P(x))` returns `True`, the kernel refines `x` into \(C.P\). Later queries then stop at category placement.

When it returns `False`, the kernel records the decision.
It refines into a complement only when that complement is an actual declared category.

If two trusted sources disagree, the kernel must report an inconsistent mathematical context.
It must not choose one source silently.

Backend failures are not mathematical decisions.
They propagate as failures.
An algorithm may return `Unknown` only when it completed correctly but did not decide the proposition.

## How containment works

Python forces `x in category` to produce a Boolean.
It cannot preserve an unevaluated proposition.
[Python membership semantics](https://docs.python.org/3/reference/expressions.html#membership-test-operations)

The kernel therefore generates this behavior:

```python
def __contains__(self, candidate: Any) -> bool:
    decision = ask(self.membership_proposition(candidate))
    assert decision is not Unknown, "membership is not established by the available data and algorithms"
    return decision is True
```

`Unknown` is not `False`, and a bool cannot carry it, so the undecided case fails loudly rather than being reported as non-membership.
The three-valued question is `ask(C.membership_proposition(x))`, which every caller that must handle the undecided case asks instead.

Placement is a positive shortcut inside that one question, not a second notion of membership: construction or same-object refinement into the property category already established the defining predicate, so step 1 answers `True` without recomputing (`POL-CAT-068`). A value without that placement still has the defining predicate evaluated, and that predicate can be undecided. Endpoint equality in `Mor(C)(A, B)` and the membership rule of a rule-defined set are the same case. Those are what the assertion catches.

The kernel must not cache `Unknown` as mathematical falsity.

Leaves never implement `__contains__` on a category.

## Inverse-image property categories

Suppose \(P\) is defined at category \(C\). Let \(F:D\to C\) be the structure functor.

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

- the structure functor \(D.P\to C.P\);

- the refined object, element, and morphism types;

- assumption-driven refinement;

- declared subcategory containments;

- inverse images along selected structure functors.

A leaf does not copy `is_P()`. It also does not forward it by hand.

This follows the main idea of Sage’s `CategoryWithAxiom`: define an axiom at the largest category where it makes sense.
Subcategories then inherit refinements such as `Groups().Finite()`. [Sage category-with-axiom documentation](https://doc.sagemath.org/html/en/reference/categories/sage/categories/category_with_axiom.html)

The repository should retain that mathematics.
It should not copy Sage’s string-based axiom registry or method-name discovery.

A derived property needs a structure functor.
If two routes give different meanings, the category must select one route explicitly.

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

One is a full subcategory of the other, and the monomorphism presenting it is the whole
statement (D83):

```text
Sets().Finite() ⊆ Sets().Countable()
```

"Finite implies countable" is set-theoretic logic and has no category-theoretic
formulation. `Sets()` states the containment through `Axiom`'s `full_subcategory_of`,
and nothing derives it from a relation between the two predicates.

Thus `ask(X.is_countable())` returns `True` immediately when `X` already belongs to `Sets().Finite()`.

For a category \(C\) with a selected set-valued functor

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

A named finite construction goes directly into `C.Finite()`. It does not enumerate itself to derive finiteness.

A generic set may use an exact decision procedure when `ask(X.is_finite())` reaches the computational stage.
That procedure can use Sage, SymPy, GAP, Julia, or another engine.

## Injectivity, monomorphisms, and isomorphisms

These properties live on morphisms.

For \(D=\operatorname{Mor}(C)\), the generic categorical propositions are:

\[
\operatorname{Monic}(f),
\qquad
\operatorname{Epic}(f),
\qquad
\operatorname{Isomorphism}(f).
\]

They define:

```python
D.Monomorphisms()
D.Epimorphisms()
D.Isomorphisms()
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

That converse is category-specific.
A monic and epic morphism need not be an isomorphism in every category.

Examples:

```python
f = Mor(Sets())(X, Y)(rule)
ask(f.is_injective())       # May compute or return Unknown.

g = Mor(Sets()).Monomorphisms()(X, Y)(rule)
ask(g.is_injective())       # True from category placement.

assume(f.is_injective())    # Refines f through the kernel's same-object mechanism.
```

An identity map constructs directly into `D.Isomorphisms()`. It never runs injectivity or surjectivity algorithms.

If an assumed isomorphism lacks a computed inverse, `inverse()` returns the owned symbolic inverse morphism.
Category placement establishes its equations.
A backend may later realize that morphism computationally.

## Functor properties

The kernel constructs `Fun = Mor(Cat())` from the same `Mor` construction used for every category.
Its objects are functors.
Therefore, functor properties are ordinary property subcategories:

```python
FullFunctors = Mor(Cat()).Full()
FaithfulFunctors = Mor(Cat()).Faithful()
FullyFaithfulFunctors = Mor(Cat()).FullyFaithful()
EssentiallySurjectiveFunctors = Mor(Cat()).EssentiallySurjective()
Equivalences = Mor(Cat()).Equivalences()
```

Fixed endpoints use the same dispatch as every property subcategory of `Mor(K)`: `Fun(C, D).Full()` is `Mor(Cat())(C, D).Full()`.

Their membership propositions are applied through the functor:

```python
F.is_full()
F.is_faithful()
F.is_fully_faithful()
```

The standard positive routes remain uniform:

```python
F = Mor(Cat()).Full()(F)  # Trusted property-category construction.
assume(G.is_full())      # Interactive assumption and same-object refinement.
```

The monomorphism of a full subcategory is constructed as `Fun(Source, Target).Monomorphisms().Isofibrations().Full()()`.  `Fun.Monomorphisms()` is declared a full subcategory of `Fun.Faithful()`, so a monomorphism is placed in both (D83).

These property categories register no computational handlers.
`ask(F.is_full())` returns `Unknown` unless category placement, an active assumption, a cached exact decision, or a declared subcategory containment decides it.

## Finite posets

A poset is not merely a property of a bare set.
Its relation is part of its data.

Start with a category of sets equipped with a binary relation.
Then define:

\[
\operatorname{is\_poset}(X,\leq)
\]

as the conjunction of reflexivity, antisymmetry, and transitivity.

The poset category is the property subcategory cut out by that proposition.

Let

\[
\pi_X:\mathbf{Poset}\to\mathbf{Set}
\]

be `PartiallyOrderedSets().product_projection(0)` from the product-subobject presentation.
Then:

\[
\mathbf{FinitePoset}
=
\mathbf{Poset}.\operatorname{Finite}
=
\{P\in\mathbf{Poset}\mid \operatorname{Finite}(\pi_X(P))\}.
\]

Its membership proposition is the conjunction:

\[
\operatorname{is\_poset}(P)
\land
\operatorname{is\_finite}(U(P)).
\]

If `P` already belongs to `PartiallyOrderedSets()`, the first term follows from category placement.

If `P` was directly constructed in `FinitePosets()`, both terms follow from placement.

If `P` is only a relation-bearing object, `ask(P.is_poset())` may run an exact finite-law checker.
A positive result refines it into `PartiallyOrderedSets()`.

No finite-poset leaf implements:

- a second finiteness predicate;

- combined refinement code;

- manual routes to `Sets()`;

- a special `__contains__`;

- an assumption method.

## Template for a predicate-backed axiom implementation

An axiom makes `C.P()` available without requiring a decision procedure.
A concrete category can register itself as that same `C.P()` through Sage's axiom mechanism.
When it supports computed refinement, it inherits `PredicateSubcategory` and implements
the private abstract `_predicate()` contract.

Conceptually:

```python
class PObjects(PredicateSubcategory):
    _base_category_class_and_axiom = (CClass, "P")

    def _predicate(self, x: C.ObjectType) -> Proposition:
        return property_formula(x)

    class ObjectType:
        # Only operations introduced by P.
        ...
```

The exact syntax can differ.
The semantic requirements cannot.

The registered class is `C.P()` itself. It is not a second category.
`PredicateSubcategory` defines the containment proposition from ambient membership and
the implemented predicate. The predicate has private identity in the proposition engine.
The `_base_category_class_and_axiom = (CClass, "P")` registration identifies the axiom.
The kernel converts that registered CamelCase axiom identifier to snake case and prefixes
`is_`: `"Finite"` becomes `is_finite()`, `"FullyFaithful"` becomes
`is_fully_faithful()`, and `"OfCardinalityExactlyFour"` becomes
`is_of_cardinality_exactly_four()`. This conversion supplies only the public spelling.
The private `_predicate()` method supplies the mathematical meaning.

From the axiom declaration and optional registered implementation, the kernel supplies:

- `C.P()`;

- its category-owned construction dispatcher;

- its membership proposition;

- `__contains__`;

- `assume` integration;

- positive self-refinement;

- descendant categories such as `D.P()`;

- inverse-image categories along selected structure functors;

- the declared subcategory containments.

The leaf does not define `assume()` on `ObjectType`. The membership proposition already supports:

```python
C.P().membership_proposition(x).assume()
```

That operation uses the global mathematical context and the proposition's category owner.

The ambient category that declares the axiom owns the generated predicate application.
Its value is `C.P().membership_proposition(self)`.

## Where computation handlers belong

`membership_proposition()` and its generated public application contain no algorithm.

The property category owns the decision surface.
Backend-specific procedures may live behind private engine boundaries.

Conceptually:

```python
PObjects().register_exact_handler(C.ObjectType, decide_P_for_C_objects)
```

This is not a decorator on a public mathematical method.
It is private integration with the standard predicate-dispatch system.

The handler:

- accepts the semantic object;

- may lower it into Sage, SymPy, GAP, Julia, or another engine;

- returns an exact decision;

- does not construct categories;

- does not mutate assumptions;

- does not implement `__contains__`;

- reconstructs any semantic data before returning it.

Each handler positively matches the semantic cases it can decide.
The final wildcard case returns `Unknown`. Add a new supported procedure by adding a new `case`. Do not encode applicability as an `if` cascade over unsupported cases.

No handler is required.
Without one, `ask(PObjects().membership_proposition(x))` can still succeed from placement, assumptions, declared containments, or images owned by structure functors.

## The main boundary

The ownership split is:

- The property category defines \(P\), \(C.P\), and their membership proposition.

- The proposition engine owns logical inference and global assumptions.

- The repository kernel connects positive propositions to category refinement.

- Each inherited property category is the inverse image along its selected structure functor.

- Computation engines supply exact decision procedures.

- Named constructions place results directly in established categories.

- Leaves state only their new predicate and their new mathematics.

That split makes `C.Finite()`, `C.Countable()`, `D.Monomorphisms()`, and `D.Isomorphisms()` instances of one mechanism.
It avoids four separate engineering designs.

The missing rule is this:

> Sage’s `with_axiom` machinery can build category intersections and dynamic classes.
> It cannot define what an axiom means.

The owned kernel must give every property axiom a defining proposition.

## What remains from `with_axiom`

The repository should retain these parts of Sage’s model:

- `Sets().Finite()` constructs a property subcategory.

- Descendants can inherit the property as `C.Finite()`.

- Category joins combine established properties.

- Dynamic classes expose methods added by the refined category.

- `FiniteSets()` and `Sets().Finite()` denote one canonical category.

Sage supports separate and nested implementations of a category with an axiom.
It also canonicalizes forms such as `FiniteSets()` and `Sets().Finite()`. [Sage `CategoryWithAxiom` documentation](https://doc.sagemath.org/html/en/reference/categories/sage/categories/category_with_axiom.html)

Take the separate form as the model, not the nested one. `Sets().Infinite()` is an axiom
applied to `Sets()`; it is not a class nested inside `Sets`. The axiom is declared once,
the implementing class is defined independently anywhere, and one declared field wires
that class to its ambient category and axiom, as Sage's `_base_category_class_and_axiom`
does. A property subcategory is therefore an ordinary category class and declares its own
`ObjectType`, `ElementType`, and `MorphismType` like any other (`POL-LEAF-059`).

The repository must not retain the bare-string semantics:

```python
_with_axiom("Finite")
```

The string can remain a private Sage runtime key.
It cannot define the mathematics.

## What an owned property axiom means

The axiom and its optional predicate-backed implementation are separate declarations:

\[
\operatorname{Finite}:
\operatorname{Ob}(\mathbf{Set})\to\operatorname{Prop},
\]

\[
\mathbf{FiniteSet}
=
\{X\in\mathbf{Set}\mid
\mathbf{FiniteSet}.\operatorname{membership\_proposition}(X)\}.
\]

Conceptually, the declarations have this shape:

```python
class SetsCategory(Category):
    Finite = Axiom()


class FiniteSets(PredicateSubcategory):
    _base_category_class_and_axiom = (SetsCategory, "Finite")

    def _predicate(self, X: Sets().ObjectType) -> Proposition:
        return X.cardinality() < aleph0

    class ObjectType:
        # Only mathematics available for known finite sets.
        ...
```

The axiom gives the kernel `C |-> C.Finite()` and its monomorphisms.
Sage registration makes `FiniteSets()` the implementation of `Sets().Finite()`.
The private `_predicate()` method gives `PredicateSubcategory` the defining proposition.

The kernel must not infer the definition from either string:

```text
"Finite"
"is_finite"
```

It must not use method-name matching.

The property class states the mathematical equation directly:

\[
\mathbf{Sets.Finite}
=
\{X\in\mathbf{Sets}\mid
\mathbf{Sets.Finite}.\operatorname{membership\_proposition}(X)\}.
\]

That equation is not engineering metadata.
It is the definition of the full subcategory.

## `FiniteSets()` is not a second category

The following identity must hold:

```python
FiniteSets() is Sets().Finite()
```

A separate module can contain the Python definition of the category class.
That choice only controls source layout.

It must not create:

- a second finite-set category;

- a second implementation hierarchy;

- a parallel same-object refinement mechanism;

- a second defining predicate.

`Sets().Finite()` must resolve to the owned `FiniteSets` category implementation.

## Predicate application

The kernel derives the ambient predicate application from the registered axiom identifier.
For finite sets its value is `Sets().Finite().membership_proposition(self)` and its return type is `Proposition`.

`FiniteSets().ObjectType` must not replace it with a Boolean override:

```python
def is_finite(self) -> bool:
    return True
```

The kernel must not inject that override.
No standalone public `finite(X)` function duplicates the generated application.

A finite set inherits that same method.
Calling it still produces the category-owned membership proposition.

Category placement supplies an entailment rule:

\[
X\in\mathbf{Sets.Finite}
\Longrightarrow
\operatorname{ask}(X.\operatorname{is\_finite}())=\mathrm{True}.
\]

Thus, the MRO does not establish truth by replacing the method.
The proposition engine establishes truth from category placement.

This preserves one public method owner.
It also preserves one return type.

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

The exact category API can expose the strongest category differently.
The mathematical transition remains the same.

The containment spelling also invokes `ask()`:

```python
X in Sets().Finite()
```

It asks the defining membership proposition.
Therefore, containment can trigger the same lazy computation.

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

If a later exact computation contradicts that placement, the mathematical context is inconsistent.
The kernel must report that conflict.

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

The backend contract then establishes finiteness.
The construction boundary reconstructs the owned set directly in `Sets().Finite()`.

If the backend also supplies cardinality \(10\), the owned construction retains that cardinal value.

This is not eager property discovery.
The ordinary construction already produced decisive semantic data.

### Case 3: The construction leaves finiteness unresolved

SymPy might retain the set as a `ConditionSet` or another symbolic predicate set.

Then the owned object remains in `Sets()`:

```python
X.category() is Sets()
```

No constructor should launch every available finiteness algorithm merely to strengthen category placement.

A later call to `ask(X.is_finite())` performs that work.

## Where finiteness algorithms belong

`FiniteSets` owns the finiteness membership proposition and its decision surface.
Its public object implementation contains only mathematics valid after finiteness is established.

The decision implementations can live in private set-engine modules.
They accept owned objects of `Sets()` and return exact decisions to the category-owned predicate resolver.

There can be exact handlers for different semantic constructions:

```text
FiniteSets.membership(explicit finite set)
FiniteSets.membership(predicate subset)
FiniteSets.membership(cartesian product)
FiniteSets.membership(coproduct)
FiniteSets.membership(SymPy-backed set)
FiniteSets.membership(Sage-backed set)
```

The public architecture is conceptually:

```python
Sets().Finite().register_exact_handler(
    PredicateSubset,
    decide_predicate_subset_finiteness,
)
```

This registration is private predicate-engine integration.
It is not a decorator on `is_finite()` or another public mathematical application.

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

It should not import every engine.
It should not inspect private representation types.

A neighboring private engine module can contain the SymPy interaction.
The public `Sets().ObjectType` remains the implementation firewall.

## How descendant categories receive `Finite()`

Let

\[
U:C\to\mathbf{Sets}
\]

be the structure functor.

The kernel defines:

\[
C.\operatorname{Finite}
=
\{X\in C\mid U(X)\in\mathbf{Sets.Finite}\}.
\]

For an owned subcategory of `Sets()`, Sage's axiom-join machinery can help construct this category and its dynamic implementation classes.

For a general structure functor, the correct object is an inverse-image property category.
It is not only a Python class join.

The kernel must derive:

- `C.Finite()`;

- its monomorphism into `C`;

- its structure functor into `Sets().Finite()`;

- its membership proposition;

- its compiled-class inheritance;

- its category-owned construction dispatcher;

- its refinement behavior.

The descendant leaf supplies none of this.

If several structure functors give different meanings to “finite,” the category must select the intended functor.
The kernel must not infer a route from method names.

## Property axioms and structure additions differ

Not every upstream Sage axiom fits this proposition-defined model.

`Finite` is a property of an existing set.
It defines a full subcategory.

`Associative` is a property of an existing magma operation.
It can also define a property subcategory.

A construction that adds mathematical data requires more than a proposition.
Its morphisms can also change.

For example, “has a unit” and “has a chosen unit preserved by morphisms” are different categorical statements.

The kernel should therefore distinguish:

- proposition-defined property subcategories;

- categories that add structure or change the morphism notion.

Only the first class receives automatic `ask()`, `assume()`, and property refinement.

## The exact architectural rule

A property axiom declaration and its optional concrete implementation supply:

1. The axiom `P` on its ambient category `C`.

2. The functorial construction `C |-> C.P()` and each monomorphism `C.P() -> C`.

3. The concrete category registered as `C.P()`, when one exists.

4. The private `_predicate()` method required when that category inherits `PredicateSubcategory`.

5. The property subcategories it is a full subcategory of.

6. Exact decision handlers, when available.

The kernel derives the standard `is_P()` application from that declaration.
It returns the membership proposition.

The kernel supplies:

1. `C.P()`.

2. Descendant `D.P()` constructions.

3. `__contains__`.

4. Global-assumption integration.

5. `ask()` dispatch.

6. Positive self-refinement.

7. Dynamic class refinement.

8. Canonical category joins.

The property category's implementation classes supply only operations valid because \(P\) is known.
Its category declaration can bind decision procedures for the ambient membership proposition.

## Addendum: property-owned predicates and decision procedures

No standalone public `finite(X)` function exists.

The property category owns the predicate.
The kernel derives `X.is_finite()` as its public application on set objects.

### One source of truth

The canonical proposition is:

```python
Sets().Finite().membership_proposition(X)
```

This produces the proposition:

\[
X\in\mathbf{Sets.Finite}.
\]

The kernel derives the owned predicate application from that category declaration.

The assumption engine still needs a predicate object internally.
That object belongs privately to the `Sets().Finite()` category singleton.

Thus:

- `Sets().Finite()` owns the mathematical property.

- `membership_proposition(X)` is the category-owned definition.

- The kernel derives `X.is_finite()` as its public application on set objects.

- The private SymPy or Sage predicate does not enter the global namespace.

### A research property declares its ambient predicate

Consider:

```python
FourSets = Sets().OfCardinalityExactlyFour()
```

The category declaration supplies:

\[
\operatorname{Ob}(\mathbf{FourSets})
=
\{X\in\mathbf{Sets}\mid \#X=4\}.
\]

Conceptually:

```python
class OfCardinalityExactlyFour(PredicateSubcategory):
    _base_category_class_and_axiom = (SetsClass, "OfCardinalityExactlyFour")

    def _predicate(self, X: Sets().ObjectType) -> Proposition:
        return X.cardinality() == 4
```

The axiom supplies the generated application name. The registered implementation supplies
its meaning. The kernel derives the application from `FourSets.membership_proposition(X)`.

The user can then write:

```python
p = X.is_cardinality_exactly_four()

ask(p)
assume(p)
FourSets(X)
X in FourSets
```

The axiom supplies the application name. Its declaring category is the ambient owner.
The kernel compiles that application and rejects a name collision.

### The corrected property template

A property leaf requires:

1. The ambient category.

2. The concrete category registered as the implementation of `C.P()`, when one exists.

3. Its `PredicateSubcategory` base and private `_predicate()` method, when computed refinement is supported.

4. The property subcategories it is a full subcategory of.

5. Its decision procedures, when available.

A predicate-backed implementation supplies the private `_predicate()` method and its category-specific operations.

Conceptually:

```python
class OfCardinalityExactlyFour(PredicateSubcategory):
    _base_category_class_and_axiom = (SetsClass, "OfCardinalityExactlyFour")

    def _predicate(self, X: Sets().ObjectType) -> Proposition:
        return X.cardinality() == 4
```

`applied_predicate` here means the category-owned proposition mechanism.
It is not a required public spelling.

The applied proposition retains:

- the candidate `X`;

- the property category;

- its defining formula;

- the private assumption-engine predicate.

Therefore, an exact positive result knows which category must receive `X`.

### Defining formulas and decision procedures differ

The defining proposition answers:

> What does membership in this category mean?

A decision procedure answers:

> Can the current representation establish that proposition?

For four-element sets, the definition is:

\[
\#X=4.
\]

No special decision procedure may be needed.
`ask()` can evaluate the cardinal equality through existing cardinality logic.

The property leaf should not duplicate cardinality computation.

For surjectivity, the definition is:

\[
\operatorname{surjective}(f)
\iff
\operatorname{image}(f)=\operatorname{codomain}(f).
\]

That definition does not prescribe one algorithm.

### Surjectivity as the better example

Let:

\[
f:\mathbf{RR}\to\mathbf{RR}.
\]

The canonical proposition is:

```python
Mor(Sets()).Epimorphisms().membership_proposition(f)
```

The generated property application is:

```python
f.is_surjective()
```

It returns the same proposition.

Neither expression computes an image.

Computation begins with:

```python
ask(f.is_surjective())
```

The resolver first uses non-computational knowledge:

1. Existing placement in `Mor(Sets()).Epimorphisms()`.

2. A global assumption.

3. A known inverse.

4. A construction theorem.

5. A cached exact decision.

Only then does it invoke registered decision procedures.

### Where the decision procedures live

The property category owns the decision surface because it owns the proposition.

The implementations can live in private engine modules.

For surjectivity, possible procedures include:

- decide from a known inverse;

- decide from an exact finite table;

- decide from an exact image construction;

- decide through symbolic equation solving;

- decide through quantifier elimination;

- decide through a backend-specific range algorithm.

The category declaration binds the typed computational routes for its membership predicate.
Private engines perform the work.

The exact engine dispatch remains private.
The category binds typed handlers to its predicate.
`ask()` is their only public decision surface.

A SymPy integration can use SymPy’s predicate multipledispatch internally.
[SymPy `ask()` documentation](https://docs.sympy.org/latest/modules/assumptions/ask.html)

### Several automatic procedures

Several procedures can apply to the same property.

They must declare exact applicability.
Use a positive `match` with one case for each supported semantic construction.
The final wildcard case returns `Unknown`:

```python
def decide_property(x: SemanticObject) -> Decision:
    match x:
        case FirstSupportedConstruction(defining_data=data):
            return decide_first_construction(data)
        case SecondSupportedConstruction(defining_data=data):
            return decide_second_construction(data)
        case _:
            return Unknown
```

Extend this function by adding a case.
Do not use negative tests, an `if` cascade, or exceptions to select algorithms.

For example:

```text
Explicit finite map
    → exact finite-image procedure

Map with a known inverse
    → inverse procedure

Symbolic real map
    → symbolic image procedure

Unsupported representation
    → Unknown
```

The property resolver selects a procedure from the semantic construction and its available representations.

It does not inspect arbitrary Python fields in the leaf.

Every automatic procedure must terminate on its declared domain.
It returns:

```text
True | False | Unknown
```

If several exact procedures return conflicting decisions, the kernel reports an implementation defect.

### Expensive computational routes

`ask()` selects from registered routes by their exact semantic domains.
Its public call has no route-selection parameters.
A costly route remains a private handler.
It passes its result through the same kernel resolution operation:

```text
ask(predicate)
        ↓
applicable computational route
        ↓
record exact result
        ↓
refine on True
        ↓
cache False or retain Unknown
```

Therefore, an exact positive result from any computational route refines `f` into `Mor(Sets()).Epimorphisms()`.

The handlers may delegate to private Sage, SymPy, GAP, Julia, or external-program implementations.

### Example: an exact image computation

Suppose a private SymPy engine can construct the exact image:

\[
f(\mathbf{RR})\subseteq\mathbf{RR}.
\]

The decision procedure computes an owned image set \(I\). It then asks:

\[
I=\mathbf{RR}.
\]

For \(f(x)=x^2\), an exact engine can obtain:

\[
I=[0,\infty).
\]

It then returns `False`.

For \(f(x)=x^3\), an exact engine can obtain:

\[
I=\mathbf{RR}.
\]

It then returns `True`.

For a symbolic rule whose image cannot be determined, it returns `Unknown`.

The backend result does not escape as a SymPy set.
The private boundary reconstructs the owned set or proposition first.

The property category wires this procedure through a positive semantic case:

```python
def decide_surjective_set_map(f: Sets().MorphismType) -> Decision:
    match (f.domain(), f.codomain()):
        case (number_sets.RR, number_sets.RR):
            return sympy_sets.decide_exact_image_equals_reals(f)
        case _:
            return Unknown


Mor(Sets()).Epimorphisms().register_exact_handler(
    Sets().MorphismType,
    decide_surjective_set_map,
)
```

The SymPy procedure returns `True` only when the exact owned image equals `RR`. It returns `False` when the exact image differs from `RR`. It returns `Unknown` when no supported symbolic-image case determines the result.
Add another supported domain, codomain, or map construction as another `case`.

### Refinement timing

Calling the predicate does not refine:

```python
p = f.is_surjective()
```

Calling `ask()` can refine:

```python
decision = ask(p)
```

If `decision` is `True`, then:

```python
f in Mor(Sets()).Epimorphisms()
```

becomes true through category placement.

A registered exact-image route can also refine through the same public call:

```python
ask(f.is_surjective())
```

A global assumption refines without computation:

```python
assume(f.is_surjective())
```

Direct construction also refines without computation:

```python
f = Mor(Sets()).Epimorphisms()(A, B)(rule)
```

All positive routes establish the same category placement through the kernel's refinement mechanism.

### The clean ownership rule

The final model is:

- The property category owns its membership proposition.

- Its private predicate object belongs to that category.

- The public property application is the method generated from the axiom declaration.

- The category that declares the axiom receives the generated application on its compiled class.

- `ask()` invokes the canonical automatic decision route.

- All computational routes remain behind the owned predicate.

- Every exact positive decision invokes the same category refinement.

`Sets().OfCardinalityExactlyFour()` owns the containment proposition.
Its generated application returns that proposition.
Surjectivity can still use several private computational routes.
