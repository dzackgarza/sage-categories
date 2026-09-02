# Leaf category implementations

This specification owns the boundary between category theory, the kernel, and private computation engines.
It implements D03, D08, D13, D118 through D123, D133, D135, and `POL-LEAF-053` through `POL-LEAF-079`.
Its [Red flags](#red-flags) section is the one catalogue of banned leaf shapes; every other document refers to it by policy row.

See [functor.md](functor.md) for `Cat`, `Mor`, `Fun`, functor actions, and structure-functor selection.
See [property-refinement.md](property-refinement.md) for property categories and same-object refinement.
See [resolution.md](resolution.md) for the private Sage compiler.

## Contents

- [Leaf contract](#leaf-contract)
- [Owned implementation classes](#owned-implementation-classes)
- [Constructors](#constructors)
- [Structure functors](#structure-functors)
- [Inherited constructions](#inherited-constructions)
- [Property categories](#property-categories)
- [Computation-engine boundary](#computation-engine-boundary)
- [Exact types](#exact-types)
- [Private helpers and files](#private-helpers-and-files)
- [Acceptance conditions](#acceptance-conditions)

## Leaf contract

A leaf states only its new mathematics.
It answers four questions:

1. What are its objects, elements, and morphisms?
2. What data constructs one object or morphism?
3. Which immediate named functors supply inherited structure?
4. Which operations, predicates, algorithms, and theorems first belong here?

The category owns these answers.
Generic categorical constructions retain their own functors and universal data.
The kernel compiles inherited implementation.
Private engines supply algorithms.

## Owned implementation classes

For each category `C`:

- `C.ObjectType` implements objects of `C`.
- `C.ElementType` implements elements of objects of `C`.
- `C.MorphismType` implements morphisms of `C`.

These classes contain the executable methods first owned by `C`.
Each public operation has one method definition and one exact signature.
The category declaration writes or links all three classes.

```python
class LeafCategory(Category):
    class ObjectType:
        def leaf_operation(self, argument: LeafArgument) -> LeafResult:
            ...

    class ElementType:
        pass

    class MorphismType:
        pass
```

An empty class body states that the leaf adds no local mathematics for that kind.
Inherited methods still reach the compiled class through selected structure functors.

## Constructors

The default call `C(data)` constructs an object of `C` from its usual complete mathematical data.
A named constructor accepts another complete mathematical presentation.
Every constructor returns `C.ObjectType`.

```python
C(defining_data)
C.from_presentation(presentation)
C.from_sage(engine_value)
```

The constructor asks for the smallest datum that determines the new structure.
It obtains data already determined by that datum from its mathematical owner.

For a poset, the primary datum is a relation subobject

\[
R\hookrightarrow X\times X.
\]

The codomain and retained product projections determine `X`.
The caller does not repeat `X`.

The [poset template](poset-minimal-template.py) shows this constructor and its functor to `Sets()`.

## Structure functors

Each entry in `C.structure_functors()` is an ordinary object of `Fun(C, D)`.
Selection contributes the applicable target implementation classes.
It does not change the functor's type or mathematical action.
These declarations build the repository's new owned category graph. They do not import,
reuse, or modify Sage's mathematical category graph; a migrated Sage category is a new
owned leaf or construction in this graph.

A leaf gets a selected functor in one of two ways:

1. It returns the exact functor retained by its defining categorical construction.
2. It constructs new leaf mathematics through `Fun(C, D)`.

A new leaf functor supplies complete executable actions:

```python
def target_functor(self) -> Cat().MorphismType:
    D = TargetCategory()

    def on_object(X: self.ObjectType) -> D.ObjectType:
        return D(X.target_data())

    def on_morphism(f: self.MorphismType) -> D.MorphismType:
        source = on_object(f.domain())
        target = on_object(f.codomain())
        return Mor(D)(source, target)(f.target_action())

    return Fun(self, D)(on_object, on_morphism)
```

`on_object(X)` constructs and returns the public image in `D`.
`on_morphism(f)` constructs and returns the public image in the exact target hom category.
These two actions are the sole leaf declaration of the functor.
Their inputs are source values whose own local state is initialized, and an action uses only
the source category's own methods. The kernel runs the object action during construction to
initialize the inherited target implementation; a leaf writes no base-class initializer call.

A leaf can create a structural diamond simply by selecting functors whose transitive
targets meet. This never requires route-resolution boilerplate. The kernel chooses the
single shared implementation occurrence through controlled C3 and debug-logs the diamond
while its coherence remains implicit. Future optional coherence is expressed, if needed,
by ordinary owned 2-morphism data between the composite functors rather than by a
leaf-specific compiler record.

A helper used only by one action stays local to that action or private to the leaf.
A datum with independent public mathematical meaning keeps its public mathematical name.

## Inherited constructions

The generic category theory owns its complete construction data.
A leaf reuses that data and states only its added structure or theorem.

Examples include:

- a pullback-defined category selects the retained pullback projections;
- a category of structured pairs selects the relevant product projections;
- a subcategory selects its retained monomorphism;
- a lifted limit reuses the selected cone and universal morphism;
- a restricted functor comes from `F.restrict(P, Q)`;
- an inherited property category comes from `F.inverse_image(C.P())`.

For a universal construction, `Cat` owns the shape, diagram, cone or cocone, legs, apex, and universal map.
The leaf states the additional leaf structure and the theorem that the construction preserves or creates it.

One apex can have many presentations.
Operations that depend on one presentation remain on that presentation object.

## Property categories

A leaf declares a property axiom once.
The registered axiom identifier determines the public `is_P()` spelling.
The leaf owns the predicate's mathematical meaning.
Its public representation is a SymPy `Predicate` subclass.
The generated method returns its applied SymPy proposition for `C.P()`.

The property owner registers its exact handlers through SymPy.
The kernel performs same-object refinement after an exact positive result.
Any Python declaration helper remains private and creates no second predicate model.

The complete example exists in [finite-set-minimal-template.py](finite-set-minimal-template.py).
The general contract exists in [property-refinement.md](property-refinement.md).

## Computation-engine boundary

A category-owned method can use Sage, SymPy, GAP, Singular, Macaulay2, Julia, Cython, shell programs, or imported research software.
The method remains the public mathematical owner.

A private computation has this form:

\[
\text{owned input}
\longrightarrow
\text{engine input}
\longrightarrow
\text{engine result}
\longrightarrow
\text{owned result}.
\]

The leaf method owns the complete sequence.
It selects the exact algorithm from established mathematical data.
It returns an owned category, object, element, morphism, functor, typed-query result, or authorized SymPy proposition.

```python
def rank(self) -> NonnegativeInteger:
    engine_rank = self._sage_poset().rank()
    return NonnegativeIntegers()(engine_rank)
```

The public API names the mathematical operation.
Private helpers can use engine names and engine types.
The caller does not select an engine.

## Exact types

Every public signature uses the exact mathematical input and result types.

- Use `C.ObjectType`, `C.ElementType`, and `C.MorphismType` for category-owned values.
- Use an owned set, ordered set, indexed family, or other named collection.
- Use separate total methods for distinct mathematical operations.
- Return a SymPy proposition for a truth question.
- Return an applied query with an exact result category for a partial value question.

For example, `rank()` and `rank_of_element(x)` are distinct operations.
They do not share one optional parameter.

## Private helpers and files

Keep the category declaration and its implementation classes together by default.
Split a substantial implementation by exact mathematical type:

```text
finite_posets.py
finite_poset_objects.py
finite_poset_elements.py
finite_poset_morphisms.py
```

A substantial private Sage boundary can use a neighboring module:

```text
finite_posets.py
_finite_poset_sage.py
```

The private module can own engine conversion, engine-native computations, and private caches.
The category-owned classes retain public signatures, semantic result construction, and operation documentation.

## Red flags

A leaf that contains any of these shapes exposes a kernel defect (D133, D135, `POL-LEAF-063` to `POL-LEAF-079`, `POL-KERNEL-037`).
Repair the kernel; do not polish the leaf.

This section is the catalogue.
Each entry names the shape, the code that carries it, the owner that supplies it instead, and the gate that finds it.
A gate is a rule in `.ast-grep/architecture/` or a contract in `[tool.importlinter]`; `just architecture` runs both over `src` and the witness categories in `tests/kernel` at the push tier and fails on a file and line (D132).
"Review" marks a shape that D132 admits no mechanical check for; the gate agent finds it by reading.
The decision record stays in `decisions.md`; the compact rule stays in `CONTRIBUTING.md`; a plan card cites the row.

### `POL-LEAF-063` — base initializer, or inherited state installed by hand

- In code: `super().__init__(...)` or `Base.__init__(self, ...)` in a category class or in `ObjectType`, `ElementType`, `MorphismType`; an `__init__` on a category class that builds subcategories, registers handlers, or constructs objects.
- Owner: the kernel runs every reached initializer once with its owner's datum (D13). A category class has no initializer beyond storing its parameters.
- Gate: `no-manual-initializer-threading`, `no-manual-initializer-threading-category`, `no-constructor-name-strings`.

### `POL-LEAF-064` — property or construction subcategory built by hand

- In code: `PropertySubcategory(self, "Name", ())`, `FullSubcategory(self)`; `self._p.Q = lambda: ...`; a hand-written accessor `Finite()`, `Countable()`, `WithBottom()`; a subcategory constructed by hand and then registered as an inverse image.
- Owner: `Finite = Axiom()` in the class body; `_base_category_class_and_axiom` on the implementing class; `F.inverse_image(C.P())` for an inherited property (D83, D89).
- Gate: `no-hand-built-property-subcategory`, `no-patched-accessor`, `no-constructor-name-strings`.

### `POL-LEAF-065` — identity, composition, morphism or element construction, or element retention for inherited structure

- In code: `construct_identity`, `composite`, `inverse_morphism`, `element_from_defining_morphism`; a `construct_morphism` whose body forwards through a structure functor; `P.element(x)` building `* -> P` by hand; an equality handler that decides inherited equality through a functor.
- Owner: `Cat` defines each once; the kernel constructs elements from functor images (D44, D84, D85, D121). `Sets()` is the base and is exempt (D132).
- Gate: `no-inherited-operation-rewritten`; review for forwarding `construct_morphism` bodies and equality handlers.

### `POL-LEAF-066` — kernel machinery in a leaf: branching, refinement after construction, own value store, kernel state in a constructor

- In code: `role_of(x) is Role.X`, `is_placed(x, C)`, `is_subcategory`; `refine(x, C)`; `x = C(...)` then `D()(x)` or `C.P()(x)` as a statement; `self._store[key] = ...`, `_NAME_CATEGORIES: MonoDict = MonoDict()`, `x: dict[...] = {}`, `@cached_method`, `@cached_function`; `ObjectType(self, data)`, `ObjectType(category=self, ...)`, `MorphismType(self.morphism_category(1), ...)`.
- Owner: a leaf imports no kernel module (D122); a value is constructed into its strongest category by a named constructor, so `C.P()(x)` is refinement and `C.P().from_data(...)` is construction; retention by identity is the kernel's (D111); the kernel supplies the placement (D21).
- Gate: import contract "A leaf imports no kernel internal"; `no-refinement-after-construction`; `no-hand-rolled-retention`; `no-leaf-value-store`; `no-compiler-state-in-constructor`; `no-compiler-state-in-constructor-positional`. Review for a refinement call whose category is bound to a local name.

### `POL-LEAF-067` — Sage machinery as the category's runtime

- In code: a subclass of `Parent`, `Element`, `ElementWrapper`, or `UniqueRepresentation` in a theory module; `from sage...` in a theory module; engine arithmetic or normalization on the category or object class.
- Owner: an engine module named in the import contract, `_<leaf>_sage.py` (D40, `POL-LEAF-046`, `POL-LEAF-050`, `POL-SAGE-016`).
- Gate: import contract "Only the kernel's Sage runtime module and the named engine modules import Sage".

### `POL-LEAF-068` — hand-written property application or accessor

- In code: `def is_finite(self) -> AppliedPredicate`, `def has_bottom(self)`, `def is_total(self)`.
- Owner: the kernel generates `is_p()` on `C.ObjectType` from the axiom identifier, and descendants inherit it (D89).
- Gate: `no-hand-written-property-application`.

### `POL-LEAF-069` — datum-free constructor, or a one-object category built by hand

- In code: `def __call__(self) -> ObjectType: return self._x` with the object built in `__init__` and refined into `self`.
- Owner: `Cat().Point(X)` with a selected point functor places `X` and supplies the codomain's surfaces (D128). The leaf states the membership rule, the cardinal, and one functor.
- Gate: `no-datum-free-constructor`.

### `POL-LEAF-070` — a selected functor declared without its two actions

- In code: `Fun(self, D).Monomorphisms().Full()()`.
- Owner: `Fun(C, D)(on_object, on_morphism)`; the two actions are the whole declaration (D08, D123).
- Gate: `no-functor-without-actions`.

### `POL-LEAF-071` — a retained projection rewritten

- In code: `def product_projection(self, index)` with an index branch and `raise IndexError`; a pullback-defined category whose projections are hand-written functors.
- Owner: the defining construction retains its projections and universal data; the leaf selects them (D09, D10, `POL-LEAF-049`, "Retained functor specimen" in [leaf-category-template.md](leaf-category-template.md)).
- Gate: `no-retained-projection-rewritten`.

### `POL-LEAF-072` — placeholder datum

- In code: `self(carrier, None, None, None)`; `ElementType(m, None)`; a "presentation" that stores generators and relations and reads neither; a carrier `sets(lambda x: True)`.
- Owner: a witness uses an existing mathematical object (D129); no method only fails (D50).
- Gate: `no-placeholder-datum`; review for unread construction data and total-membership carriers.

### `POL-LEAF-073` — union or optional parameter

- In code: `value: OrdinalObject | int`, `rule: Rule | SetMap`, `assumptions: Proposition | None = None`, `cardinality: CardinalObject | UnknownClass`, `*inverse_rule`.
- Owner: one total method per operation and one named constructor per presentation (D52); a partial value is an applied query (D50).
- Gate: `no-union-parameter`.

### `POL-LEAF-074` — a property on a datum record

- In code: `@property def unit(self): return self.zero` on a `@dataclass` datum, present so that a target owner's initializer can read the source datum.
- Owner: the kernel initializes each target from the datum the functor action feeds to the target constructor (D13); a datum record holds exactly the new state (`POL-LEAF-047`, D121).
- Gate: `no-property-on-datum`.

### `POL-LEAF-075` — generic parameters on a leaf declaration

- In code: `class PosetsCategory(Category[[Rule], []])`, `PropertySubcategory[[Rule], []]`.
- Owner: the kernel derives call shape and compiler data from the ordinary method signature (`POL-LEAF-054`, `POL-LEAF-055`); the template writes `class LeafCategory(Category)`.
- Gate: `no-generic-parameter-on-leaf-category`.

### `POL-LEAF-076` — import-order wiring

- In code: `global NAME` rebinding inside a function; a module-level `__getattr__`; `_other_module.Name = value`; handler registration deferred to the module bottom with a comment on import order.
- Owner: each module binds the names it declares (`POL-SAGE-015`); layer dependencies are static (D122).
- Gate: `no-import-order-wiring`; review for cross-module binding.

### `POL-LEAF-077` — declaration lookup by name string

- In code: `Cat().declarations()["Sets"]`; `_implements = "Sets"`; `predicate(f"ThinOrder({self!r})")`; string tags such as `"finite"` and `"initial"` as an object's kind.
- Owner: the class declaration is the registration (`Axiom`, `_base_category_class_and_axiom`); an object's kind is its category placement (D89).
- Gate: `no-declaration-lookup-by-name`; review for string tags.

### `POL-LEAF-078` — an accessor standing in for a functor

- In code: `carrier()`, `carrier_morphism()`, `underlying_set()`; a public method that returns what a selected functor's `on_object` returns.
- Owner: apply the named functor (D73); a functor action may read private state (D39, D120).
- Gate: review.

### `POL-LEAF-079` — two spellings of one fact

- In code: `covers()` returning a proposition on `Posets().ObjectType` and a `bool` on `FinitePosets().ObjectType`; `action()` beside `action_morphism()`; `binary_product()` and `__mul__` beside `Products()`; a docstring that names `+`, `zero()`, or `*` on a class that defines none of them.
- Owner: one mathematical fact has one semantic owner and one method (D88, D121).
- Gate: review.

## Acceptance conditions

A leaf satisfies this specification when:

- its source states only the category's new mathematics after inherited structure is removed;
- it declares `ObjectType`, `ElementType`, and `MorphismType` under their exact names;
- each locally owned public operation has one executable method body;
- each new functor has complete object and morphism actions;
- `structure_functors()` returns only the immediate named functors that supply inheritance;
- the leaf reuses functors and universal data retained by its defining constructions;
- every public signature uses exact mathematical types;
- each category-specific computation adapter reconstructs an owned mathematical result;
- proposition methods return the authorized SymPy expressions and `ask()` results;
- property methods and typed queries follow their canonical specifications;
- the leaf imports no kernel internal;
- the caller selects no computation engine;
- one mathematical fact has one semantic owner.

The kernel consequence is direct inherited execution on the structured source value.
The private mechanism is specified only in [resolution.md](resolution.md).
