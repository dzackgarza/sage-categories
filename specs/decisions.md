# Architectural decision index

This index preserves decision IDs, source locators, supersession, and recorded uncertainty.
The linked topic specification owns each current technical contract.
[System architecture](system.md) maps those owners; [AGENTS.md](../AGENTS.md) owns the work procedure ([D180](#d180)).
Add decisions with an exact session identifier and message timestamp.

## Contents

- [Sources](#sources)
- [Philosophy](#philosophy)
- [System synthesis and work control](#system-synthesis-and-work-control)
- [Purpose and scope](#purpose-and-scope)
- [Structure functors and inheritance](#structure-functors-and-inheritance)
- [Elements](#elements)
- [Predicates, containment, and assumption](#predicates-containment-and-assumption)
- [Cardinality](#cardinality)
- [Universal constructions](#universal-constructions)
- [Diamonds and identity](#diamonds-and-identity)
- [Leaf discipline](#leaf-discipline)
- [Types and style](#types-and-style)
- [What the documents are for](#what-the-documents-are-for)

## Sources

The original record draws on Claude, Codex, and ChatGPT conversations for this repository.
The legacy source cohort is:

- Claude: `~/.claude/projects/-home-dzack-gitclones-sage-categories/`.
- Codex: `~/.codex/sessions/`, including `~/.codex/sessions/2026`.
- ChatGPT: the recordings read through the `chat-on-steroids` justfile described in [AGENTS.md](../AGENTS.md).

| Legacy session locator |
| --- |
| `rollout-2026-08-24T18-54-56-01a03368` |
| `rollout-2026-08-23T00-58-03-01a02a68` |
| `b55dc6aa` |
| `rollout-2026-08-25T13-22-02-01a0375e` |
| `5df9424f` |
| `rollout-2026-08-24T03-46-01-01a03028` |
| `rollout-2026-08-25T00-27-59-01a03499` |
| `rollout-2026-08-26T12-53-54-01a03c6a` |
| `1c1a3599` |
| `ee78124f` |
| `rollout-2026-08-22T22-55-29-01a029f8` |

Dates use 2026. A date-only entry retains the original incomplete citation; the cohort above does not identify its exact message.
An entry marked inference preserves that status even when a topic specification currently implements it.

## Philosophy

Category theory carries reusable mathematics, and category placement supplies the complete applicable interface.
Place an operation at the most general owner whose hypotheses justify it.
Keep infinite families indexed and preserve the distinction between mathematical objects and their private presentations.
The [system specification](system.md) and [leaf contract](leaves.md#leaf-contract) state these principles operationally.

## System synthesis and work control

### D124

The framework forms one coherent tower of mathematical abstractions. The system specification owns its composition and dependency directions. Owner: [System architecture](system.md).

Source: 08-31, `01a05682` 2026-08-31T12:04:57Z.

### D125

Public propositions use Sage/SymPy's predicate and ask machinery. [D115](#d115) governs the separate application/evaluation boundary; [D179](#d179) fixes the exported predicate base. Owner: [Propositions and typed queries](undecidable-properties.md).

Source: 08-31, `01a05682` 2026-08-31T09:27:03Z; `01a03368` 2026-08-24T20:25:53Z, 21:11:24Z; `b55dc6aa` 2026-08-27T16:38:05Z, 16:39:04Z, 18:32:36Z.

### D126

Inference: the staged bootstrap order was synthesized by an agent. The cited owner statements establish ordinal semiring structure, not that order. The system specification retains the implementation order. Owner: [Foundation bootstrap](system.md#foundation-bootstrap).

Source: 08-31, cited `01a05682` 2026-08-31T12:04:57Z.
Additional source locators: `1c1a3599`; `2026-08-26T23:12:17Z`; `23:23:15Z`.

### D127

Work continues from the current tree and active task. [D180](#d180) owns current execution and context-loading rules. Owner: [Workflow](../AGENTS.md).

Source: 08-31, `01a05682` 2026-08-31T11:21:08Z, 12:04:57Z; `01a03368` 2026-08-24T14:03:20Z.

### D128

Superseded in part by [D154](#d154) and [D161](#d161): the leaf class of X declares C.Point(). The one-object category {X} is not the declaration site. [D169](#d169) fixes the inclusion through which placement proceeds. Owner: [Points and placement](functor.md#point-categories-and-point-functors).

Source: 08-31, corrected 09-02; `01a03368` 2026-08-24T20:58:14Z; `1c1a3599` 2026-08-26T23:21:02Z; `b55dc6aa` 2026-08-27T18:57:29Z; `353b942d` 2026-08-28T14:41:54Z.
Additional source locators: `54674b9b`; `2026-09-02T22:00:14Z`.

### D129

Inference from the general restriction on speculative abstractions: a public mechanism enters with its first mathematical consumer. No message-level owner statement was found in the cited search. Owner: [System architecture](system.md).

Source: 08-31, cited `01a05682` 2026-08-31T12:04:57Z.

### D130

Types communicate exact mathematics. Diagnose repository types, upstream stubs, implementation defects, and checker limitations separately. [D131](#d131) fixes Any exceptions; static projection remains an authorized approach. Owner: [Exact types](leaves.md#exact-types).

Source: 09-01, `01a05a70` 2026-09-01T02:28:51Z; `01a03028` 2026-08-23T20:48:17Z, 23:06:28Z.

## Purpose and scope

### D01

Build the foundation before production leaves. The owned category graph uses Sage only through the private runtime. [D137](#d137) fixes the pre-acceptance tree; [D173](#d173) and [D175](#d175) fix layer ownership. Owner: [System architecture](system.md).

Source: 08-22, clarified 08-30, `2026-08-30-cce86657` 2026-08-29T18:13:42Z.

### D02

The public category API is closed under its operations. Computation engines remain private; public SymPy propositions are the exception fixed by [D125](#d125). Owner: [System architecture](system.md).

Source: 08-23.

### D03

The framework supplies one complete mathematical interface through category theory. A leaf states mathematics; inherited structure supplies the remaining operations. Owner: [System architecture](system.md).

Source: 08-23, clarified 08-29, `01a04c1c-b22b-7f70-8351-6e12ca028470` 2026-08-29T08:08Z, 2026-08-29T08:42Z.

### D04

A leaf declares its new mathematics and immediate functors to known categories. The generic framework supplies the inherited surface. Owner: [Leaf contract](leaves.md#leaf-contract).

Source: 08-23.

## Structure functors and inheritance

### D05

Category-owned classes acquire their bases through compiled structure functors. [D167](#d167) narrows which selected functors carry inheritance. Owner: [Implementation classes](functor.md#cobjecttype-celementtype-and-cmorphismtype).

Source: 08-23, corrected 08-29.
Additional source locators: `01a03028`; `2026-08-23T20:26:43Z`; `01a048f6`; `2026-08-28T21:03:59Z`; `21:06:26Z`.

### D06

Declare mathematical functors in the owned graph. Subcategory relations, structure projections, and implementation inheritance have distinct meanings. Owner: [Selected structure functors](functor.md#structure-functors-and-inherited-classes).

Source: 08-24, clarified 08-30, `2026-08-30-cce86657` 2026-08-29T18:13:42Z.

### D07

A category selects particular functors from those it defines. [D167](#d167) supersedes selection alone as the inheritance condition. Owner: [Selected structure functors](functor.md#structure-functors-and-inherited-classes).

Source: 08-24, corrected 08-29.
Additional source locators: `01a048f6-e3f5-7e42-be2a-1f60f70ac23e`; `2026-08-28T21:20Z`.

### D08

A computing functor has two complete executable actions, each returning a value from the exact target constructor. [D146](#d146), [D154](#d154), and [D162](#d162) fix the inclusion and point construction forms. Owner: [Functor actions](functor.md#functor-actions-are-concrete-constructors).

Source: 08-24, corrected 08-29, `01a04c1c-b22b-7f70-8351-6e12ca028470` 2026-08-29T09:15Z.

### D09

Name the exact projection, inclusion, adjoint, evaluation, or composite, with both endpoints. Owner: [Construction-owned functors](functor.md#construction-named-functors).

Source: 08-25, corrected 08-30.

### D10

Cat constructs point arrows and generic construction maps. cat_kernel constructs axiom-derived subcategories and their inclusions. [D173](#d173) and [D175](#d175) replace the older undifferentiated kernel ownership. Owner: [Layer ownership](system.md#dependency-directions).

Source: 08-25, `01a03368` 2026-08-24, Codex store; owner named under D173 and D175 on 09-03.
Reference locators: `cat/functors.py:690`.

### D11

The functor category owns each explicit declaration. [D55](#d55) supersedes the old morphism-category notation; [D146](#d146) and [D177](#d177) fix monomorphism declarations. Owner: [Monomorphism declarations](functor.md#declaring-one).

Source: 08-25, `01a0375e` 2026-08-25T08:44:37Z; spelling corrected 08-26, `ee78124f` 2026-08-26T09:05:48Z.

### D12

A structure functor is an ordinary functor selected in structure_functors(). [D167](#d167) and [D177](#d177) qualify the semantic declaration that licenses inherited execution. Owner: [Selected structure functors](functor.md#structure-functors-and-inherited-classes).

Source: 08-26, corrected 08-29.

### D13

Run the source's local initializer, then the functor actions that supply inherited state in the construction context. Target constructors initialize that target's state on the same value, once per owner in C3 order. Each owner receives its own datum. Owner: [Construction execution](resolution.md#direct-inherited-execution).

Source: 08-26, corrected 09-02; `36d46178` 2026-08-26T10:33:24Z; `01a0406a` 2026-08-26T23:47:08Z; `01a03368` 2026-08-24T23:50:43Z; `4544eba5` 2026-08-28T11:34:30Z, 12:00:37Z, 12:18:19Z; `2026-08-30-cce86657` 2026-08-29T17:52:11Z, 17:53:44Z, 18:13:42Z; `2026-08-29-52bc359d` 2026-08-29T09:03:22Z, 09:04:47Z; `e38ff397` 2026-09-02T14:14:54Z, endorsing the repair the assistant stated at 14:13:21Z.

### D123

The two ordinary actions are the sole declaration of a computing functor. [D13](#d13) fixes how construction-time execution initializes the same source value from those actions. Owner: [Functor actions](functor.md#functor-actions-are-concrete-constructors).

Source: 08-30, corrected 09-02; `2026-08-29-52bc359d` 2026-08-29T09:03:22Z, 09:04:47Z; `4544eba5` 2026-08-28T12:18:19Z; `b55dc6aa` 2026-08-27T19:02:32Z; `2026-08-30-cce86657` 2026-08-29T17:52:11Z; endorsed report `01a04e73` 2026-08-29T16:56:37Z; `e38ff397` 2026-09-02T14:14:54Z.
Additional source locators: `01a04c1c`; `2026-08-29T09:15:33Z`.

### D14

Every category uses Cat().ObjectType. Objects of C use C.ObjectType and inherit Cat().ElementType. C.ElementType supplies the elements of objects of C; C.MorphismType is Mor(C).ObjectType. Owner: [Morphism tower](functor.md#the-morn-c-tower).

Source: 08-26, corrected 08-29.
Additional source locators: `01a04c1c-b22b-7f70-8351-6e12ca028470`; `2026-08-29T06:11Z`.

### D55

Use Mor(n, C), with Mor(0, C) = C and Mor(C) = Mor(1, C). Mor(C)(A, B) is fixed-endpoint application. C.ObjectType implements objects of C; it is not the category Mor(0, C). Owner: [Morphism tower](functor.md#the-morn-c-tower).

Source: 08-26, `ee78124f` 2026-08-26T09:05:48Z; endorsed report `01a04c1c` 2026-08-29T06:02:35Z.

### D56

Declaration order fixes preference. The original row lacks a message locator; [D37](#d37) and [D165](#d165) independently support this rule. Owner: [C3 and diamonds](resolution.md#diamond-diagnostics-and-future-coherence).

Source: 08-26; no session or timestamp recorded, which `POL-DOC-018` requires.

### D58

An ordinary functor supplies executable target constructions through its two actions. [D123](#d123) fixes these as the entire writer input. Owner: [Functor actions](functor.md#functor-actions-are-concrete-constructors).

Source: 08-27, corrected 08-29.
Additional source locators: `01a04c1c-b22b-7f70-8351-6e12ca028470`; `2026-08-29T09:15Z`.

### D59

Morphism properties belong to Mor(C); functor properties belong to Mor(Cat()) and its fixed-endpoint categories. Owner: [Functor properties](functor.md#property-resolution).

Source: 08-26, corrected 08-30.

### D60

Natural-transformation components are an indexed assignment X -> eta_X, valid for infinite domains. Owner: [Functor actions](functor.md#functor-actions-are-concrete-constructors).

Source: 08-26.

### D61

Common-ancestor tracing needs a named mathematical functor property. [D167](#d167) and [D169](#d169) fix the inheritance and placement conditions. Owner: [Placement conditions](functor.md#monomorphisms-of-cat-and-placement).

Source: 08-27.

## Elements

### D15

Element implementation classes inherit the full applicable surface, including the extra operations of a property or construction category. Owner: [Implementation classes](functor.md#cobjecttype-celementtype-and-cmorphismtype).

Source: 08-23.

### D16

C.ElementType is the shared element surface of objects of C. Points have terminal domain; generalized elements have arbitrary domain. Sets use their discrete categories. Owner: [Points and placement](functor.md#point-categories-and-point-functors).

Source: 08-26, corrected 08-29.
Additional source locators: `01a04c1c-b22b-7f70-8351-6e12ca028470`; `2026-08-29T06:11Z`.

### D17

Transport a point x: * -> X along G: X -> Y by G * x. Element-class inheritance introduces no third functor action. Owner: [Points and placement](functor.md#point-categories-and-point-functors).

Source: 08-26, corrected 08-29; `1aa61835` 2026-08-26T07:01:17Z; `2026-08-29-52bc359d` 2026-08-29T06:03:12Z; endorsed report `01a04c1c` 2026-08-29T06:11:46Z.

### D62

A point is a functor * -> X. A generalized element has arbitrary domain T -> X. Owner: [Points and placement](functor.md#point-categories-and-point-functors).

Source: 08-27, corrected 08-29.

## Predicates, containment, and assumption

### D18

Truth questions construct propositions. Partial value questions construct typed queries with exact result categories. Only ask() evaluates them. Owner: [Propositions and typed queries](undecidable-properties.md).

Source: 08-22, corrected 08-29.
Additional source locators: `01a048f6-e3f5-7e42-be2a-1f60f70ac23e`; `2026-08-28T17:24Z`; `2026-08-28T17:25Z`; `01a04c1c-b22b-7f70-8351-6e12ca028470`; `2026-08-29T06:02Z`.

### D19

Category containment and generated is_P() concern the same proposition. Python containment is its forced two-valued evaluation boundary. Owner: [Containment](undecidable-properties.md#category-containment).

Source: 08-22, corrected 08-29.
Additional source locators: `4544eba5`; `2026-08-28T12:00Z`; `01a048f6-e3f5-7e42-be2a-1f60f70ac23e`; `2026-08-28T19:51Z`.

### D20

Every propositional method constructs a proposition. Only ask() returns its truth decision or Unknown. Owner: [Propositions and typed queries](undecidable-properties.md).

Source: 08-24.

### D21

Construct a result in the strongest category established by its mathematics. [D150](#d150) fixes inherited property constructors; [D154](#d154) supersedes the earlier point-declaration placement. Owner: [Constructors](leaves.md#constructors).

Source: 08-24, `01a03368` 2026-08-24T20:58:14Z; `1c1a3599` 2026-08-26T23:21:02Z; corrected 08-31.
Additional source locators: `4544eba5`; `2026-08-28T12:00Z`.

### D22

A property assumption refines the value through the same property category used by direct construction. [D150](#d150) fixes the already-constructed-value route. Owner: [Assumptions](undecidable-properties.md#assumptions).

Source: 08-24, corrected 08-28.
Additional source locators: `4544eba5`; `2026-08-28T12:00Z`.

### D23

Property refinement strengthens the category of the same value. [D150](#d150) supersedes separate property-constructor wiring; alternative semantic representations remain valid construction data. Owner: [Same-object refinement](property-refinement.md#same-object-refinement).

Source: 08-24, corrected 08-29.
Additional source locators: `01a048f6-e3f5-7e42-be2a-1f60f70ac23e`; `2026-08-28T20:21Z`.

### D24

Theory code and engines construct results in their established categories. The interactive assumption context belongs to the mathematical session. Owner: [Assumptions](undecidable-properties.md#assumptions).

Source: 08-24, `01a03368` 2026-08-24T20:38:59Z, 20:20:39Z; corrected 08-31.

### D25

A named constructor asserts the theorem attached to its controlled mathematical datum. An enumeration can define a total order; an arbitrary relation cannot establish totality by its constructor name. Owner: [Constructors](leaves.md#constructors).

Source: 08-24, 08-25.

### D26

Construction in a category asserts the theorem. Cite nontrivial mathematics at its construction owner; formal proof certification is outside this runtime. Owner: [System architecture](system.md).

Source: 08-25.

### D63

Equality constructs a proposition. Boolean-consuming code evaluates it through ask() and handles Unknown. [D131](#d131) fixes input types. Owner: [Equality](undecidable-properties.md#equality).

Source: 08-26.

## Cardinality

### D27

Derive properties from construction data and mathematical relationships. Enumeration for cardinality is a last route only for a known finite set, and that route warns. Owner: [Sets](sets.md).

Source: 08-22.

### D28

Cardinals support ordinary comparison syntax, including comparisons with integers, through their owned operations. Owner: [Cardinal arithmetic](cardinality.md).

Source: 08-22, 08-23.

### D29

Unknown cardinality is an undecided query, not an absent value. An image inherits its domain's cardinality only through an established injection. [D64](#d64) and [D115](#d115) fix evaluation. Owner: [Typed queries](undecidable-properties.md#typed-queries).

Source: 08-24, amended by D62.

### D30

Cardinal addition and multiplication are the apexes of cardinal coproducts and products. The skeletal arithmetic and retained set presentations have distinct owners under [D66](#d66). Owner: [Cardinal arithmetic](cardinality.md).

Source: 08-25.

### D64

Unknown cardinality belongs to query evaluation. [D18](#d18) and [D115](#d115) supersede calling cardinality a predicate. Known cardinal expressions remain owned cardinals under [D65](#d65). Owner: [Typed queries](undecidable-properties.md#typed-queries).

Source: 08-26, `ee78124f` 2026-08-26T09:05:48Z; corrected 08-29, `01a048f6` 2026-08-28T17:24:29Z, 17:25:36Z.

### D65

Cardinals have semiring arithmetic and an order; the engine supports finite and aleph symbols with sums, products, and exponentials. [D153](#d153) fixes the private Sage ownership of the two-semiring representation. Owner: [Cardinal arithmetic](cardinality.md).

Source: 08-27, `b55dc6aa` 2026-08-27T20:20:25Z, 20:47:14Z, 20:49:31Z; 08-26, `1c1a3599` 2026-08-26T23:08:20Z, 23:12:17Z, 23:23:15Z.
Additional source locators: `cce86657`; `2026-08-29T18:13:42Z`.

### D66

Sets of equal cardinality remain distinct. Equal cardinal values use one skeletal representative, while private cardinal expressions can retain a presentation. Owner: [Cardinal arithmetic](cardinality.md).

Source: 08-27.

## Universal constructions

### D31

Define each construction at its most general owner. Construction categories exist without asserting inhabitation. Tensor products and direct sums first belong to their applicable algebraic owner. Owner: [Universal constructions](functor.md#diagram-shapes-and-universal-constructions).

Source: 08-23.

### D32

A constructed object receives the ambient interface and retains its defining presentation. [D106](#d106) separates presentation from apex; [D167](#d167) fixes the inheritance condition. Owner: [Universal constructions](functor.md#diagram-shapes-and-universal-constructions).

Source: 08-23.

### D33

A poset product lifts the set-product presentation with its componentwise order. Generic construction machinery supplies projections and mediation. Owner: [Order categories](ordered-sets.md).

Source: 08-24.

### D34

Cat owns construction families, projections, slices, coslices, and fixed-object constructions. [D168](#d168) supersedes the earlier product-image membership description. Owner: [Universal constructions](functor.md#diagram-shapes-and-universal-constructions).

Source: 08-25, `01a0375e` 2026-08-25T09:17:33Z; corrected 08-28, `01a048f6` 2026-08-28T18:44:23Z, 18:48:43Z, 19:05:40Z, 19:09:35Z; `353b942d` 2026-08-28T14:14:50Z; `2026-08-29-52bc359d` 2026-08-29T06:03:12Z.

### D101

F.inverse_image(P) is the pullback D ×_C P for F: D -> C. It retains its projections and inclusion into D. Owner: [Property inverse images](property-refinement.md#inverse-images).

Source: 08-29, endorsed report `01a04c1c` 2026-08-29T06:39:12Z; owner's endorsement 08:11:52Z; owner's request `2026-08-29-52bc359d` 2026-08-29T06:28:41Z.

### D102

Op acts on categories, functors, and natural transformations and retains Op * Op ≅ Id. Dual constructions share the limit-side owner. Owner: [Dualization](functor.md#opposites-and-dualization).

Source: 08-29, endorsed report `01a04c1c` 2026-08-29T06:39:12Z; owner's endorsement 08:11:52Z.

### D103

The generic calculus proceeds through functor categories, category constructions, universal structure, and indexed structure. The system specification owns the dependency order. Owner: [System architecture](system.md).

Source: 08-29, endorsed report `01a04c1c` 2026-08-29T07:02:32Z; owner's endorsement 08:11:52Z.

### D104

Composition and evaluation are functors; their morphism actions supply whiskering. Pullbacks own intersections, restrictions, induced functors, fibers, and base change. Owner: [Functor-category calculus](functor.md#functor-category-calculus).

Source: 08-29, endorsed report `01a04c1c` 2026-08-29T07:02:32Z; owner's endorsement 08:11:52Z.

### D105

Comma categories retain projections and a comparison transformation. Strict, full, and essential images retain their distinct object and morphism conditions. Owner: [Image categories](functor.md#strict-full-and-essential-images).

Source: 08-29, endorsed report `01a04c1c` 2026-08-29T07:02:32Z; owner's endorsement 08:11:52Z; `5df9424f` 2026-08-23T20:00:29Z.

### D106

Existence and selected universal data have different owners. Keep diagram, presentation, and apex distinct; the apex fiber classifies presentations of that apex. Adjunctions, equivalences, cones, and representations retain selected data. Owner: [Universal constructions](functor.md#diagram-shapes-and-universal-constructions).

Source: 08-29, endorsed report `01a04c1c` 2026-08-29T07:02:32Z; owner's endorsement 08:11:52Z.

### D107

Shape-indexed functor properties state preservation and creation. Chosen limits give an adjunction to the diagonal; creation supplies lifted universal data. Owner: [Universal constructions](functor.md#diagram-shapes-and-universal-constructions).

Source: 08-29, endorsed report `01a04c1c` 2026-08-29T07:02:32Z; owner's endorsement 08:11:52Z.

### D108

Fibers, Grothendieck constructions, Yoneda, and representations belong to the generic calculus. Monads, comonads, mates, and reflective constructions are later extensions. Owner: [Indexed categories](functor.md#indexed-categories-yoneda-and-representability).

Source: 08-29, `353b942d` 2026-08-28T14:26:05Z; `77631b59` 2026-08-29T02:20:51Z; endorsed report `01a04c1c` 2026-08-29T07:02:32Z, owner's endorsement 08:11:52Z.

### D109

Sage supplies a private runtime mirror for controlled C3, dynamic classes, refinement, and Parent support. Owned declarations determine all mathematics. Owner: [Private runtime](resolution.md).

Source: 08-29, endorsed report `01a04c1c` 2026-08-29T07:34:05Z, owner's request `2026-08-29-52bc359d` 2026-08-29T06:41:21Z; clarified 08-30, `2026-08-30-cce86657` 2026-08-29T18:13:42Z, 18:04:14Z.

### D110

Sage compiles each implementation class. [D13](#d13)'s corrected construction context supplies each owner's state once from the relevant action. Owner: [Construction execution](resolution.md#direct-inherited-execution).

Source: 08-29, endorsed report `01a04c1c` 2026-08-29T07:34:05Z; `2026-08-29-52bc359d` 2026-08-29T09:03:22Z, 09:04:47Z; `4544eba5` 2026-08-28T12:18:19Z; `01a048f6` 2026-08-28T21:19:22Z, 21:40:24Z; corrected 09-02, `e38ff397` 2026-09-02T14:14:54Z endorsing the repair stated at 14:13:21Z.

### D111

Sage refinement and caches own private identity behavior. Exact keys use ordinary Sage caches; proposition-valued equality requires identity-keyed MonoDict or TripleDict. Owner: [Runtime caches](resolution.md#runtime-categories-and-caches).

Source: 08-29, `01a04c1c-b22b-7f70-8351-6e12ca028470` 2026-08-29T07:34Z.

### D112

Sage axiom and construction categories supply private binding and class assembly. [D156](#d156) fixes public identity-functor binding; [D175](#d175) fixes cat_kernel ownership. Owner: [Private property binding](resolution.md#properties-and-constructions).

Source: 08-29, `01a04c1c-b22b-7f70-8351-6e12ca028470` 2026-08-29T07:34Z.

### D113

Generic Mor and Fun belong to Cat. Private engines can use Sage morphism protocols for Sage-parent endpoints without forcing every abstract object into that runtime form. Owner: [Morphism tower](functor.md#the-morn-c-tower).

Source: 08-29, `01a04c1c-b22b-7f70-8351-6e12ca028470` 2026-08-29T07:34Z.

### D114

Python 3.14 ast handles Python declarations and generated stubs; tree-sitter-sage handles Sage syntax. Fixed wrappers use declared functions; generated runtime signatures use makefun when needed. Owner: [Declarations and signatures](resolution.md#declarations-and-signatures).

Source: 08-29, `01a04c1c-b22b-7f70-8351-6e12ca028470` 2026-08-29T07:34Z.

### D115

Constructing a proposition or typed query does not evaluate it. Placement and assumptions affect ask(), not the question's mathematical meaning. Owner: [Propositions and typed queries](undecidable-properties.md).

Source: 08-29, `01a04c1c-b22b-7f70-8351-6e12ca028470` 2026-08-29T08:01Z.

### D116

Ordinary ordinal sum and product use + and *. Hessenberg arithmetic has separate names. The ordinal specification assigns the semiring laws to the Hessenberg operations. Owner: [Ordinal arithmetic](ordinals.md#arithmetic-ownership).

Source: 08-29, endorsed report `01a04c1c` 2026-08-29T06:02:35Z, owner's endorsement `2026-08-29-52bc359d` 2026-08-29T06:03:12Z; `1c1a3599` 2026-08-26T23:23:15Z.

### D117

Aleph and initial-ordinal constructions are functors between the thin order categories. Their actions return the same owned arithmetic values. Owner: [Cardinal arithmetic](cardinality.md).

Source: 08-29, endorsed report `01a04c1c` 2026-08-29T06:02:35Z, owner's endorsement `2026-08-29-52bc359d` 2026-08-29T06:03:12Z.

### D118

A leaf states only its defining data, constructors, functors, and new operations. It reuses retained universal maps and owns one implementation across representations. Owner: [Leaf contract](leaves.md#leaf-contract).

Source: 08-29, corrected 08-29, `01a04c1c-b22b-7f70-8351-6e12ca028470` 2026-08-29T08:47Z, 2026-08-29T08:49Z, 2026-08-29T09:15Z.

### D119

Each value is constructed by its exact category: C, Mor(C)(X, Y), Fun(C, D), or the relevant property or construction category. Owner: [Construction-owned functors](functor.md#construction-named-functors).

Source: 08-29, corrected 08-29, `01a04c1c-b22b-7f70-8351-6e12ca028470` 2026-08-29T09:01Z, 2026-08-29T09:15Z.

### D120

A computing functor uses two known constructor surfaces. Its complete actions can use private helpers; the compiler interprets no function body and asks for no second declaration. Owner: [Functor actions](functor.md#functor-actions-are-concrete-constructors).

Source: 08-29, `01a04c1c-b22b-7f70-8351-6e12ca028470` 2026-08-29T09:15Z.

### D121

Each mathematical fact and public operation has one semantic owner. Runtime and generated artifacts project that declaration. Owner: [System architecture](system.md).

Source: 08-29, `01a04c1c-b22b-7f70-8351-6e12ca028470` 2026-08-29T15:42Z.

### D122

Leaves depend on immediate mathematical targets and private engines. Engines control neither categories nor assumptions. Generated stubs and manifests are output-only. Owner: [Layer ownership](system.md#dependency-directions).

Source: 08-29, `01a04c1c-b22b-7f70-8351-6e12ca028470` 2026-08-29T15:42Z.

### D35

Cat supplies category-level and object-level product, coproduct, biproduct, and exponentiation syntax. The ambient category fixes each operation; [D181](#d181) distinguishes a product-category element from its product-functor image. Owner: [Categorical operators](functor.md#products-coproducts-and-component-functors).

Source: 08-25, `01a0375e` 2026-08-25T07:11:30Z; `1aa61835` 2026-08-26T07:01:17Z; `b55dc6aa` 2026-08-27T15:49:13Z, 16:00:08Z.

### D67

Complete the category framework and owned Sets foundation before later theories. [D137](#d137) fixes the pre-R6 leaf boundary; small examples are witnesses for the foundation. Owner: [System architecture](system.md).

Source: 08-26, corrected 08-28.
Additional source locators: `01a029f8`; `2026-08-22T16:48Z`.

### D68

Support finite diagrams and sequential shapes while retaining arbitrary indexed assignments where required. Finite positional products are a convenience, not the definition. Owner: [Universal constructions](functor.md#diagram-shapes-and-universal-constructions).

Source: 08-26.

### D69

Cat owns the common categorical operators and ambient-category routing. [D140](#d140) fixes the required tracing property; [D181](#d181) fixes the product-call distinction. Owner: [Categorical operators](functor.md#products-coproducts-and-component-functors).

Source: 08-26, `ee78124f` 2026-08-26T09:05:48Z; `b55dc6aa` 2026-08-27T13:54:22Z, 16:00:08Z; `01a048f6` 2026-08-28T21:19:22Z.

### D70

X ** Y denotes the category-owned morphism-object construction from Y to X. The ambient categorical owner supplies this syntax. Owner: [Categorical operators](functor.md#products-coproducts-and-component-functors).

Source: 08-27, `b55dc6aa` 2026-08-27T15:49:13Z, 16:00:08Z; `01a0375e` 2026-08-25T07:11:30Z.

### D71

Cat owns terminal and initial categories, simplices, walking structures, and required horns with their boundaries. Sets owns its empty and canonical finite sets. Owner: [Canonical categories](functor.md#canonical-objects-of-cat).

Source: 08-26.

## Diamonds and identity

### D36

Assume Cat is bicomplete and biclosed. Universe sizes are outside the current model. Owner: [Cat](functor.md#cat-and-its-implementation).

Source: 08-26.

### D37

Sage controlled C3 selects one implementation occurrence. Declaration order fixes precedence; unresolved diamonds receive DEBUG diagnostics. Optional future coherence uses owned 2-morphisms. Owner: [C3 and diamonds](resolution.md#diamond-diagnostics-and-future-coherence).

Source: 08-26, corrected 08-30, `2026-08-30-cce86657` 2026-08-29T18:01:55Z, 18:11:47Z, 18:12:42Z, 18:13:42Z; `01a048f6` 2026-08-28T21:19:22Z, 21:40:24Z.

### D38

Set equality is proposition-valued. Identity, a theorem, or an exact computation can decide it. Each named functor retains its own public image. Owner: [Equality](undecidable-properties.md#equality).

Source: 08-26, corrected 08-28.
Additional source locators: `4544eba5`; `2026-08-28T12:00Z`; `2026-08-28T12:18Z`.

## Leaf discipline

### D80

A category class declares its category and its nested ObjectType, ElementType, and MorphismType together. The compiler constructs those exact classes. Owner: [Implementation classes](functor.md#cobjecttype-celementtype-and-cmorphismtype).

Source: 08-28, corrected 08-29.
Additional source locators: `b55dc6aa`; `2026-08-27T18:57Z`; `01a048f6-e3f5-7e42-be2a-1f60f70ac23e`; `2026-08-28T21:03Z`; `2026-08-28T21:06Z`.

### D81

Kernel modules and Cat import no production leaf. Generic constructions receive their ambient category from their caller. Owner: [Layer ownership](system.md#dependency-directions).

Source: 08-28, `77631b59` 2026-08-28T17:35:47Z.

### D86

Units use the operation's mathematical name: zero() and one() for the additive and multiplicative forms. End_C(X).one() is the unit for composition. Owner: [Categorical operators](functor.md#products-coproducts-and-component-functors).

Source: 08-28, `77631b59` 2026-08-28T19:03:51Z, corrected 2026-08-28T19:06:27Z.
Reference locators: `sage/categories/additive_magmas.py:599,696`; `sage/categories/magmas.py:461,482`.

### D83

Axiom availability, containment propositions, and same-object refinement share one property category. Relations between property categories are their declared monomorphisms. Owner: [Property categories](property-refinement.md#property-category).

Source: 08-28, `4544eba5` 2026-08-28T12:00:37Z; `77631b59` 2026-08-28T22:04:44Z; `b55dc6aa` 2026-08-27T16:08:35Z; endorsed report `01a04e73` 2026-08-29T16:56:37Z.
Additional source locators: `2026-08-28T18:10:28Z`.

### D82

Constant categories use category classes. Category-valued families have their ordinary constructors or functor actions. Cat can declare expected downstream mathematical points without importing their leaves. Owner: [Category-valued families](functor.md#category-classes-and-category-valued-families).

Source: 08-28, `77631b59` 2026-08-28T17:35:47Z, 17:54:04Z, 17:59:49Z; `b55dc6aa` 2026-08-27T18:57:29Z; `01a048f6` 2026-08-28T16:05:24Z.

### D84

End_C(X).one() is the identity morphism. C.Subobjects(X) fixes X's ambient role through C. Owner: [Fixed-object constructions](functor.md#fixed-object-construction-categories).

Source: 08-29, corrected 08-30, `01a048f6` 2026-08-28T18:35:42Z, 18:44:23Z, 18:48:43Z, 19:09:35Z; `77631b59` 2026-08-28T19:06:27Z; endorsed report `01a04e73` 2026-08-29T16:56:37Z.

### D85

Cat().ObjectType defines uniform category operations once. Each leaf inherits them and adds its mathematical realization. Owner: [Fixed-object constructions](functor.md#fixed-object-construction-categories).

Source: 08-29, corrected 08-29, `01a048f6-e3f5-7e42-be2a-1f60f70ac23e` 2026-08-28T18:48Z, 2026-08-28T18:49Z, 2026-08-28T19:05Z, 2026-08-28T19:09Z.

### D87

Cat owns shapes, diagrams, presentations, legs, and universal maps. Each leaf specification states its added structure, predicates, algorithms, and realizations. Owner: [Universal constructions](functor.md#diagram-shapes-and-universal-constructions).

Source: 08-29, `01a048f6-e3f5-7e42-be2a-1f60f70ac23e` 2026-08-28T19:25Z.

### D88

The version-1 interface exposes defining data and mathematical primitives. Users compose short derived operations from those primitives. Owner: [Leaf contract](leaves.md#leaf-contract).

Source: 08-29, `01a048f6` 2026-08-28T19:38:03Z, 19:43:26Z; endorsed report `01a04c1c` 2026-08-29T07:02:32Z.

### D89

An axiom identifier and private proposition generate the one public is_P() application. [D148](#d148) fixes the declaration; [D175](#d175) assigns generation to cat_kernel. Owner: [Property categories](property-refinement.md#property-category).

Source: 08-29, corrected 08-29, `4544eba5` 2026-08-28T12:00:37Z; `01a048f6` 2026-08-28T19:51:04Z, 22:51:01Z, 23:00:18Z, 23:05:25Z, 23:08:36Z; the mechanism at 23:09:46Z endorsed at 23:11:16Z; `01a03368` 2026-08-24T22:05:49Z; owner named under D175 on 09-03.

### D97

An axiom makes its category available. An exact SymPy handler can decide its proposition. Positive results use the same refinement as construction and assumption. Owner: [Property categories](property-refinement.md#property-category).

Source: 08-28, `77631b59` 2026-08-28T22:04:44Z; endorsed `01a03368` 2026-08-24T21:59:43Z, 22:12:42Z.

### D95

C.ObjectType is the exact category-owned class constructed by the compiler. [D167](#d167) narrows which selected targets contribute bases. Owner: [Implementation classes](functor.md#cobjecttype-celementtype-and-cmorphismtype).

Source: 08-29, corrected 08-29, `01a048f6` 2026-08-28T21:03:59Z, 21:06:26Z; `01a04c1c` 2026-08-29T09:15:33Z.

### D96

A structure functor belongs to the new owned graph. Its compiler use establishes neither categorical containment nor equality with its public image; [D167](#d167) fixes inherited execution. Owner: [Selected structure functors](functor.md#structure-functors-and-inherited-classes).

Source: 08-29, corrected 08-30, `01a048f6-e3f5-7e42-be2a-1f60f70ac23e` 2026-08-28T21:20Z; `2026-08-30-cce86657` 2026-08-29T18:13:42Z.

### D90

Element syntax carries algebraic operations. Module actions can also expose their defining action morphism for mathematical use. Owner: [Algebraic operations](magmas-monoids-semirings.md#owned-operations).

Source: 08-29, corrected 08-29, `01a048f6` 2026-08-28T20:21:35Z.

### D91

Same-object property refinement and ingestion of a new representation are distinct. [D150](#d150) fixes the ambient constructors inherited by a property category. Owner: [Same-object refinement](property-refinement.md#same-object-refinement).

Source: 08-29, corrected 08-29, `01a048f6-e3f5-7e42-be2a-1f60f70ac23e` 2026-08-28T20:21Z.

### D92

This earlier row retained explicit prohibitions in specifications. [D180](#d180) controls their current document ownership and the consolidation of repeated rules. Owner: [Document ownership](system.md).

Source: 08-29, `01a048f6-e3f5-7e42-be2a-1f60f70ac23e` 2026-08-28T20:21Z.

### D93

Kernel acceptance precedes production leaves. [D180](#d180) controls the current dependency, review, and defect-return procedure. Owner: [Workflow](../AGENTS.md).

Source: 08-29, `01a048f6-e3f5-7e42-be2a-1f60f70ac23e` 2026-08-28T16:05Z.

### D77

The leaf contract consists of implementation classes, constructors, functor actions, axioms, and defining predicates. [D156](#d156) supersedes the old public axiom-binding field; [D173](#d173) and [D175](#d175) divide generic ownership. Owner: [Leaf contract](leaves.md#leaf-contract).

Source: 08-28, `353b942d` 2026-08-28T14:55:27Z; `77631b59` 2026-08-29T00:55:50Z; `2026-08-29-52bc359d` 2026-08-29T07:54:51Z, 08:28:01Z.

### D39

A leaf supplies minimal construction data and executable functors to immediate mathematical targets. Operations inherited through those targets remain at their owners. Owner: [Leaf contract](leaves.md#leaf-contract).

Source: 08-22.

### D40

Separate mathematical declarations, kernel engineering, and private computation engines by subtree. The import boundary follows this separation. Owner: [Layer ownership](system.md#dependency-directions).

Source: 08-22.

### D41

A category records mathematical structure. Alternative representations and algorithms remain inside its one implementation; subsets use the inherited subobject construction. Owner: [Leaf contract](leaves.md#leaf-contract).

Source: 08-22.

### D42

High-level mathematical category names own discoverable constructors. [D150](#d150) supersedes property-specific constructor wiring: property categories inherit the ambient constructors. Owner: [Constructors](leaves.md#constructors).

Source: 08-22, corrected 08-28.
Additional source locators: `4544eba5`; `2026-08-28T11:34Z`; `2026-08-28T12:00Z`.

### D43

Each mathematical category has one public implementation type. It can use several private computation engines without exposing engine selection. Owner: [Computation engines](leaves.md#computation-engine-boundary).

Source: 08-24.

### D44

Identity and composition arrive from Cat. A leaf adds only its own mathematical specialization of an inherited operation. Owner: [Morphism tower](functor.md#the-morn-c-tower).

Source: 08-24.

### D45

Place each operation at the generic mathematical owner that lets every leaf state only its additional mathematics. Owner: [System architecture](system.md).

Source: 08-24.

### D73

A named functor fixes an explicit mathematical choice. Its endpoint pair alone does not select a projection, image, or representation. Owner: [Construction-owned functors](functor.md#construction-named-functors).

Source: 08-28, `353b942d` 2026-08-28T13:59:29Z, 13:13:10Z; `4544eba5` 2026-08-28T12:00:37Z, 12:18:19Z; `01a0375e` 2026-08-25T08:52:59Z, 08:57:58Z; `b55dc6aa` 2026-08-27T16:00:08Z.

### D76

Preservation gives an isomorphic comparison. A lifted construction can require its chosen apex and defining morphisms to map exactly to the chosen ambient presentation. Owner: [Universal constructions](functor.md#diagram-shapes-and-universal-constructions).

Source: 08-28, corrected 08-28.
Additional source locators: `01a03c6a`; `2026-08-26T07:36Z`; `4544eba5`; `2026-08-28T12:18Z`.

### D75

Chosen-data categories use the applicable diagram, fiber, or Grothendieck construction. Their morphisms must state datum preservation and cartesianness. Generating data is an epimorphism Free_R(S) -> M; presentations and resolutions use the corresponding diagrams. These consumer-specific morphism choices remain open until stated. Owner: [Indexed categories](functor.md#indexed-categories-yoneda-and-representability).

Source: 08-28.
Reference locators: `sage/categories/modules_with_basis.py:179`; `sage/categories/modules_with_basis.py:47`; [Grothendieck+construction](https://ncatlab.org/nlab/show/Grothendieck+construction); [02XJ](https://stacks.math.columbia.edu/tag/02XJ).

### D74

Subobjects(X) retains a representative (A, i) with i: A -> X monic. Represented equality is a proposition; a quotient subobject is an isomorphism class. Restricting added leaf structure belongs to that leaf. Owner: [Fixed-object constructions](functor.md#fixed-object-construction-categories).

Source: 08-26, corrected 08-30, `01a048f6` 2026-08-28T18:44:23Z, 18:48:43Z, 19:09:35Z, 19:25:26Z; `353b942d` 2026-08-28T14:14:50Z; endorsed reports `01a04c1c` 2026-08-29T06:02:35Z, `01a04e73` 2026-08-29T16:56:37Z.

### D72

Structured-object categories take their ambient category as a parameter. Each definition supplies the additional monoidal, action, or closed data it requires. Owner: [Category-valued families](functor.md#category-classes-and-category-valued-families).

Source: 08-27.

## Types and style

### D78

Before 1.0, architecture controls acceptance and checks provide diagnostics. [D132](#d132) narrows the mechanical-check boundary; [D180](#d180) owns the current workflow. Owner: [Workflow](../AGENTS.md).

Source: 08-28, `353b942d` 2026-08-28T15:13:29Z, 15:21:46Z.

### D79

[D132](#d132) narrows the pre-1.0 enforcement restriction for admitted architectural invariants. [D180](#d180) owns the current check and review procedure. Owner: [Workflow](../AGENTS.md).

Source: 08-28, `be8d8a9e` 2026-08-28T15:50:50Z.

### D46

Module elements and morphisms use (p, q)-tensors at the module ElementType level. vector() and matrix() specialize tensor() by shape, base ring, and indexed data; bilinear forms use Gram tensors. Owner: [Module objects](modules.md).

Source: 08-22.

### D47

Morphism evaluation accepts elements constructed by the appropriate owned objects. Owner: [Leaf contract](leaves.md#leaf-contract).

Source: 08-22.

### D48

Use standard mathematical type names. [D131](#d131) fixes the two authorized Any aliases. Owner: [Exact types](leaves.md#exact-types).

Source: 08-22.

### D49

Public signatures use the category's exact object, element, and morphism types, including refinements whose local method body is empty. Owner: [Exact types](leaves.md#exact-types).

Source: 08-22.

### D50

Partial mathematical operations use applied queries and ask(); capability-specific methods belong to the appropriate category or abstract contract. [D18](#d18) and [D115](#d115) supersede the older predicate terminology for cardinality. Owner: [Propositions and typed queries](undecidable-properties.md).

Source: 08-23, `01a03028` 2026-08-23T20:59:19Z; corrected 08-28, `01a048f6` 2026-08-28T17:24:29Z.
Additional source locators: `17:25:36Z`; `01a03368`; `2026-08-24T21:11:24Z`.

### D51

Generated stubs and type-checker plugins can expose dynamic category structure. Type-checker diagnostics do not define architecture; [D130](#d130) fixes their interpretation. Owner: [Static projection](functor.md#static-semantic-projection).

Source: 08-23.

### D52

Use total constructors and separate named forms for distinct complete mathematical data. [D150](#d150) fixes the constructor surface inherited by property categories. Owner: [Constructors](leaves.md#constructors).

Source: 08-24.

### D53

Prefer established mathematical primitives and packages when they express the operation directly. Owner: [Leaf contract](leaves.md#leaf-contract).

Source: 08-23.

## What the documents are for

### D94

Implementation work requires fixed mathematical owners, public contracts, and acceptance. [D180](#d180) controls how plans reference those contracts. Owner: [Workflow](../AGENTS.md).

Source: 08-29, `01a048f6-e3f5-7e42-be2a-1f60f70ac23e` 2026-08-28T17:36Z, 2026-08-28T18:18Z, 2026-08-28T18:20Z, 2026-08-28T18:30Z.

### D100

Restricted Yoneda functors, their properties, evaluation maps, and presentations own generator uses. The earlier claim that generators have no use is superseded by this row's recorded correction. Owner: [Generators and presentations](separating-families-and-categorical-generators.md).

Source: 08-29, `77631b59` 2026-08-29T02:43:39Z.

### D99

Core: Cat -> Groupoids retains the inclusion U(Core(C)) -> C. Core(C) keeps C's objects and isomorphisms; Mor(C).Isomorphisms() lives one level higher. The cardinality functor starts at Core(Sets()). Owner: [Core functor](functor.md#the-core-functor).

Source: 08-29, corrected 08-29, `77631b59` 2026-08-29T00:44:44Z; `01a04ab2-d713-74b3-8a24-eeef392b0869` 2026-08-29T00:48Z.

### D98

Decision provenance records architectural choices; topic specifications state the contracts. [D180](#d180) controls document and plan authority. Owner: [Document ownership](system.md).

Source: 08-29, `01a048f6-e3f5-7e42-be2a-1f60f70ac23e` 2026-08-28T22:17Z, 2026-08-28T22:27Z, 2026-08-28T22:37Z.

### D54

Topic specifications state the desired public interface and immediate structure functors. CONTRIBUTING supplies general principles; [D180](#d180) fixes document ownership. Owner: [Document ownership](system.md).

Source: 08-22, `01a02a68` 2026-08-22T21:09:14Z.

### D131

Equality constructs a proposition. EqualityInput = Any and ContainmentInput = Any are the only permitted Any aliases. These replace the earlier raw-Any spelling. Owner: [Exact types](leaves.md#exact-types).

Source: 09-01, corrected 09-02; `b55dc6aa` 2026-08-27T16:38:05Z, 16:39:04Z, 18:32:36Z; `01a02a68` 2026-08-22T23:42:08Z; `ee78124f` 2026-08-26T09:05:48Z; `e38ff397` 2026-09-02T15:09:26Z, a queued message.

### D133

Kernel engineering, generic Cat mathematics, and cat_kernel generation replace leaf wiring under [D173](#d173)/[D175](#d175). Inference retained: inherited element construction is assigned to the kernel without a located owner statement. The leaf catalogue owns the concrete prohibited shapes. Owner: [Layer ownership](system.md#dependency-directions).

Source: 09-02, `e38ff397` 2026-09-02T14:43:42Z, 14:53:16Z; owner statements `01a03368` 2026-08-24T14:03:20Z, 23:10:13Z, 23:50:43Z; `36d46178` 2026-08-26T10:33:24Z; `1c1a3599` 2026-08-26T23:08:20Z; `4544eba5` 2026-08-28T12:00:37Z; `77631b59` 2026-08-28T19:06:27Z; `b1f26f05` 2026-08-29T04:38:59Z; `8419143e` 2026-09-01T23:35:15Z.

### D134

Durable architectural decisions belong in their owning documents and plans. [D180](#d180) fixes the current ownership and update procedure. Owner: [Document ownership](system.md).

Source: 09-02, `e38ff397` 2026-09-02T14:43:42Z, 15:00:16Z, 15:04:41Z, 15:18:33Z, 15:19:06Z, 15:20:46Z; `2026-08-30-cce86657` 2026-08-29T19:09:08Z, 19:11:16Z; `01a05682` 2026-08-31T09:28:45Z.

### D132

Narrows [D79](#d79): mechanical checks may enforce admitted architectural invariants at exact locations. Conventions and review judgments remain outside those checks. [D180](#d180) owns the current procedure. Owner: [Workflow](../AGENTS.md).

Source: 09-02, `e38ff397` 2026-09-01T23:57:02Z, 2026-09-02T13:46:06Z, 15:26:33Z, 15:30:33Z, 15:37:44Z, 15:40:41Z.
Additional source locators: `2026-09-02T14:53:16Z`.
Reference locators: `kernel/sage_runtime.py`.

### D135

The leaf-shape catalogue has one owner in leaves.md. Other documents link its rules; [D180](#d180) controls the current relation to checks and plans. Owner: [Leaf contract](leaves.md#leaf-contract).

Source: 09-02, `91d641ff` 2026-09-02T15:28Z and 2026-09-02T15:40Z.

### D136

The earlier phase-gate protocol required independent acceptance before dependent work. [D180](#d180) owns the current gate and review procedure. Owner: [Workflow](../AGENTS.md).

Source: 09-02, `54674b9b` 2026-09-02T19:00:44Z, 19:40:34Z; `8419143e` 2026-09-01T23:51:20Z, a queued message; `e38ff397` 2026-09-02T14:56:43Z, 15:40:41Z.

### D137

Pre-acceptance production leaves were removed. Production phases reconstruct them against the accepted framework; [D180](#d180) owns current phase execution. Owner: [Workflow](../AGENTS.md).

Source: 09-02, `54674b9b` 2026-09-02T19:30:16Z, the owner's answer to the question asked at that timestamp.

### D138

The earlier plan protocol added independent review, phase-state checks, and defect-return rules. [D180](#d180) controls the consolidated workflow. Owner: [Workflow](../AGENTS.md).

Source: 09-02, `54674b9b` 2026-09-02T19:40Z.
Additional source locators: `2026-09-02T19:40:57Z`.

### D139

Describe the exact fibration, projection, inclusion, Kan-extension map, source, target, or composite. Endpoints alone select no functor. Owner: [Construction-owned functors](functor.md#construction-named-functors).

Source: 08-25, `01a0375e` 2026-08-25T09:31:57Z, 08:52:59Z, 08:57:58Z.

### D140

A binary categorical operation can route to a common ancestor only through the declared mathematical condition. [D167](#d167) and [D169](#d169) fix inheritance and placement conditions. Owner: [Categorical operators](functor.md#products-coproducts-and-component-functors).

Source: 08-27, `b55dc6aa` 2026-08-27T13:54:22Z, 15:49:13Z, 15:51:20Z, 16:00:08Z.

### D141

Property categories own the constructors for their assumptions. [D150](#d150) specifies that they inherit exactly the ambient constructors. Owner: [Constructors](leaves.md#constructors).

Source: 08-24, `01a03368` 2026-08-24T20:38:59Z.

### D142

The axiom's defining proposition is a private method. cat_kernel generates the public is_P() spelling under [D175](#d175). Owner: [Property categories](property-refinement.md#property-category).

Source: 08-28, `01a048f6` 2026-08-28T23:05:25Z.

### D143

Exact handlers match positively on supported cases. Their SymPy boundary returns None otherwise; public ask() maps that result to Unknown. Owner: [Exact handlers](undecidable-properties.md#proposition-handlers).

Source: 08-25, `01a0375e` 2026-08-25T09:46:21Z, 09:53:12Z.

### D144

Functor equivalence is asserted through construction in its property category. The compiler computes no functor-property decision; selected equivalence data has its separate category. Owner: [Functor properties](functor.md#property-resolution).

Source: 08-28, `353b942d` 2026-08-28T14:41:54Z.

### D145

Gate requirements belong in plans before implementation. [D180](#d180) owns the current planning and review procedure. Owner: [Workflow](../AGENTS.md).

Source: 09-02, `e38ff397` 2026-09-02T15:40:41Z; `54674b9b` 2026-09-02T19:40:34Z.

### D146

Superseded in part by [D154](#d154)/[D161](#d161): C.Point() constructs the point arrow. [D177](#d177) fixes zero-argument monomorphism calls: the named property category is the complete declaration. Owner: [Monomorphism declarations](functor.md#declaring-one).

Source: 09-02, `54674b9b` 2026-09-02T21:26:03Z; superseded in part by D161.
Additional source locators: `23:31:27Z`.
Reference locators: `cat/functors.py:190-201`.

### D147

Relations() owns relation subobjects R -> X * X. Posets() is Relations().PartialOrder(), whose axiom and proposition originate on Relations(). Owner: [Order categories](ordered-sets.md).

Source: 09-02, `54674b9b` 2026-09-02T21:26:03Z.

### D148

A named axiom supplies its defining proposition. cat_kernel constructs its implicit property category and inclusion. Named structure functors transport axioms by pullback. Owner: [Property categories](property-refinement.md#property-category).

Source: 09-02, `54674b9b` 2026-09-02T21:26:03Z.

### D149

Superseded in part by [D181](#d181): a product-category element and its image under the chosen product functor have distinct result categories. The uniform product-object operation remains `C.Products()(X, Y)`. Owner: [Categorical operators](functor.md#products-coproducts-and-component-functors).

Source: 09-02, `54674b9b` 2026-09-02T21:26:03Z.

### D150

Constructors take complete construction data. C.P() inherits exactly C's constructors. An existing value enters a property category by assume(X.is_P()). Owner: [Constructors](leaves.md#constructors).

Source: 09-02, `54674b9b` 2026-09-02T21:43:23Z.

### D151

Preference, not a settled implementation mechanism: exact handlers may ask exact subquestions, with SymPy owning cycle safety. The earlier mutual-recursion prohibition is superseded. Owner: [Exact handlers](undecidable-properties.md#proposition-handlers).

Source: 09-02, `54674b9b` 2026-09-02T21:43:23Z.

### D152

The owner endorsed the POL-ONT block and Core Categorical Philosophy at 0c0aef7, narrowed by [D150](#d150)/[D151](#d151). [D180](#d180) controls their current normalized ownership. Owner: [Document ownership](system.md).

Source: 09-02, `54674b9b` 2026-09-02T21:43:23Z.

### D153

[D01](#d01)'s owned graph controls. [D65](#d65)'s two Sage semirings describe the private cardinal engine; Cardinal() is placed in Semirings(Cat()) by its point declaration. Owner: [Cardinal arithmetic](cardinality.md).

Source: 09-02, `54674b9b` 2026-09-02T21:43:23Z.

### D154

Each leaf class automatically declares a point in Cat. Adding C.Point() places its category object in C and supplies the level-shifted surface. [D169](#d169) separates the point arrow from its generated inclusion. Owner: [Points and placement](functor.md#point-categories-and-point-functors).

Source: 09-02, `54674b9b` 2026-09-02T22:00:14Z.

### D155

The three additional templates cover a pullback-defined category, chosen-data fibration, and universal-construction realization. [D180](#d180) owns their current phase assignment. Owner: [Leaf contract](leaves.md#leaf-contract).

Source: 09-02, `54674b9b` 2026-09-02T22:00:14Z.

### D156

An implementing class selects the named category's identity functor as its first structure functor. [D160](#d160) records the specification's concrete binding spelling. Owner: [Named category implementations](functor.md#implementing-a-named-category).

Source: 09-02, `54674b9b` 2026-09-02T22:33:35Z.

### D157

Use the construction's retained methods, including projection(), ev(i), and product_projection(i). G * F is functor composition. Owner: [Construction-owned functors](functor.md#construction-named-functors).

Source: 09-02, `54674b9b` 2026-09-02T22:33:35Z.

### D158

Construct a functor in CreatesLimits(I) to state its theorem. [D160](#d160) fixes the generated spelling is_limit_creating(I); selected limits retain the required universal data. Owner: [Universal constructions](functor.md#diagram-shapes-and-universal-constructions).

Source: 09-02, `54674b9b` 2026-09-02T22:33:35Z.

### D159

When selected routes inherit the same axiom P, they define one C.P(). The declaration order selects the first route and assumes the stated coherence. Owner: [Property inverse images](property-refinement.md#inverse-images).

Source: 09-02, `54674b9b` 2026-09-02T22:33:35Z.

### D160

Specification choices, not message-level owner decisions: End_Cat(x).one(), is_limit_creating(I), a structure_functors method with identity first, and Cat().implement(cls). [D161](#d161) supersedes the earlier point interpretation. Owner: [Named category implementations](functor.md#implementing-a-named-category).

Source: 09-02, `54674b9b` 2026-09-02T22:33:35Z, the owner's answers whose spellings stay open; superseded in part by D161.

### D161

A structure category supplies its own added structure and functors. A named object is an abstract category whose C.Point() declaration produces the categorical level shift. [D169](#d169) fixes the arrow/inclusion distinction. Owner: [Points and placement](functor.md#point-categories-and-point-functors).

Source: 09-02, `54674b9b` 2026-09-02T23:31:27Z.

### D162

Zero-argument functor declarations are confined to monomorphism categories. Other new computing functors require both actions. [D177](#d177) specifies the exact property-category result. Owner: [Monomorphism declarations](functor.md#declaring-one).

Source: 09-02, `54674b9b` 2026-09-02T23:35:49Z.

### D163

The inherited set of a relation or poset (X, R) is X. The projection to R is a distinct functor. Owner: [Order categories](ordered-sets.md).

Source: 09-02, `54674b9b` 2026-09-02T23:36:52Z.

### D164

Superseded in part by [D165](#d165) and [D167](#d167): declared properties license inheritance, while order fixes precedence among licensed selected functors. Owner: [Selected structure functors](functor.md#structure-functors-and-inherited-classes).

Source: 09-02, `54674b9b` 2026-09-02T23:40:18Z.

### D165

Declaration order fixes precedence. [D167](#d167) supersedes order alone as the condition for inheritance; access-only functors inherit nothing. Owner: [Selected structure functors](functor.md#structure-functors-and-inherited-classes).

Source: 09-02, `54674b9b` 2026-09-02T23:47:38Z.

### D166

For a lattice (L, b), the module projection carries inheritance; the form projection supplies access. [D167](#d167) gives the faithful-isofibration condition. Owner: [Selected structure functors](functor.md#structure-functors-and-inherited-classes).

Source: 09-02, `54674b9b` 2026-09-02T23:49:34Z, 23:50:47Z.

### D167

Selected faithful isofibrations carry inheritance; other selected functors supply access. Order fixes precedence. [D177](#d177) records the trusted faithfulness assertion associated with the selected Isofibrations declaration. Owner: [Selected structure functors](functor.md#structure-functors-and-inherited-classes).

Source: 09-02, `54674b9b` 2026-09-02T23:55:17Z; confirmation at 2026-09-02T23:55:21.682Z on the queued-message surface. Derived from D164, D165, and D166.

### D168

Being a nontrivial product is a parameterized axiom: membership in the essential image of the applicable product functor. Owner: [Universal constructions](functor.md#diagram-shapes-and-universal-constructions).

Source: 09-02, `8419143e` 2026-09-02T14:03:31Z, a queued message; recorded from the R0 gate's reading of the queued surface.

### D169

Placement follows monic isofibrations; inheritance follows selected faithful isofibrations. The point arrow uses its generated full inclusion for both. [D170](#d170) chooses the arrow-condition vocabulary. Owner: [Placement conditions](functor.md#monomorphisms-of-cat-and-placement).

Source: 09-03, `54674b9b` 2026-09-03T00:00:25Z; mathematical answer recorded.

### D170

A subcategory is represented by a monomorphism. State the isofibration condition on the inclusion; full property subcategories carry it. cat_kernel constructs the axiom-derived inclusion under [D175](#d175). Owner: [Placement conditions](functor.md#monomorphisms-of-cat-and-placement).

Source: 09-03, `54674b9b` 2026-09-03T00:06:32Z.
Reference locators: [replete+subcategory](https://ncatlab.org/nlab/show/replete+subcategory).

### D171

The earlier executor assignment used mechanical-unit, construction-unit, kernel-core-unit, r-gate, and r6-gate. [D172](#d172) narrows the unavailable-executor case; [D180](#d180) owns current assignments. Owner: [Workflow](../AGENTS.md).

Source: 09-03, `54674b9b` 2026-09-03T00:20:40Z, 00:22:11Z.

### D172

The recorded unavailable gate executor could be replaced by Opus 5 at high effort, with the actual executor named. [D180](#d180) owns the current executor policy. Owner: [Workflow](../AGENTS.md).

Source: 09-03, `b560a2d2` 2026-09-03T02:31:37Z, the owner's answer when the R1 gate could not run.

### D173

The kernel owns engineering; Cat owns common categorical mathematics, including endpoints, formal composites, identity, and mathematical word reduction. [D175](#d175) assigns their joint work to cat_kernel. Owner: [Layer ownership](system.md#dependency-directions).

Source: 09-03, `58d79934` 2026-09-03T04:20:28Z, the owner's reading of the R1 gate exchange.

### D174

The recorded gate additions were a closed-contract witness, explicit criterion owners, nonvacuous rule coverage, and a closed kernel surface. Their partition was an agent synthesis of the endorsed options. [D180](#d180) owns the current procedure. Owner: [Workflow](../AGENTS.md).

Source: 09-03, `58d79934` 2026-09-03T04:20:28Z.
Additional source locators: `2026-09-03T04:53:34.316Z`; `04:26:09.307Z`.
Reference locators: `scripts/rule_coverage.py`.

### D175

cat_kernel imports from kernel and Cat. Neither imports cat_kernel; leaves reach Cat. cat_kernel builds axiom-derived subcategories and reads inheritance/placement declarations; kernel performs class and placement mechanics. Owner: [Layer ownership](system.md#dependency-directions).

Source: 09-03, `15559161` 2026-09-03T06:47:03.575Z, the owner's answer to the R0 criterion-1 finding on `is_p()`.
Reference locators: `kernel/predicates.py`; `kernel/refinement.py`.

### D176

Withdrawn. Keep this number unassigned. The rejected rule tried to reconcile target orders across independent category declarations; each category compiles its own classes. Owner: [Workflow](../AGENTS.md).

Source: No source locator recorded; withdrawal retained.

### D177

Inference from [D162](#d162) and the cited decisions: a zero-argument monomorphism call declares exactly its named property category, on one retained identity-on-values functor per endpoint pair. Isofibrations alone does not imply Faithful. Selecting an Isofibrations structure functor asserts the required faithfulness without declaring global containment. Fibrations and Opfibrations retain their inclusions into Isofibrations. Owner: [Monomorphism declarations](functor.md#declaring-one).

Source: 09-04, `54674b9b` 2026-09-02T23:35:49Z, the statement D162 records; derived with D83, D146, D167, D169 and the mathematics, and assigned to M2 unit 3 by D146.

### D178

Inference, not an owner statement: POL-API-024 was read to cover instance-attribute names as well as public methods. Unrelated owners cannot write one attribute name. The recorded search found no owner statement that settled this scope. Owner: [Semantic collisions](resolution.md#semantic-collisions).

Source: 09-04, no owner statement on the subject; derived under `POL-DOC-026` from `POL-API-024` and the R1 gate's reading at `a7c5039`.

### D179

Inference from the established truth-value contract: a leaf subclasses the Predicate exported through Cat. Its SymPy application raises on Python truth conversion. SymPy retains application, Boolean operations, handlers, assumptions, and evaluation. The recorded sources settle the stance but do not name the base class. Owner: [Propositions and typed queries](undecidable-properties.md).

Source: 09-04, no owner statement names the base class; the truth-value stance behind it is the owner's, `b55dc6aa` 2026-08-27T16:38:05Z, 16:39:04Z, 16:43:08Z, 18:32:36Z and `01a048f6` 2026-08-28T18:08:43Z; derived under `POL-DOC-026` with `POL-MATH-035`, `POL-API-015` and D131, and assigned to M3 unit 8 by the M3 card.


### D180

Consolidation assigns one source per fact: topic specifications own contracts, this index owns provenance, AGENTS.md owns procedure, and vault cards own work order and acceptance state.
The current workflow replaces repeated full-context reviews, model-specific acceptance conditions, and automatic re-review of unaffected claims.
The reorganized core plan places retained property pullbacks with their first consumer, then extends and integrates them.
Historical reviews remain in Git and existing vault references. Existing accepted revisions retain their historical scope.
The runtime dependency row is corrected to Sage 10.10.beta8, observed through the project `sage --version` command.
Derived typing clarification: EqualityInput applies to both equality operators; ContainmentInput applies to containment.
This resolves the static plan's inequality-input conflict while retaining D131's two aliases and the proposition-valued inequality contract.
Owner: [Workflow](../AGENTS.md), [system architecture](system.md), and the active vault plans.

Source: explicit consolidation and workflow-revision instruction in Codex session `01a06ea2-e610-7fd0-acee-d0efc8315d93`, 2026-09-04T23:04:48.090Z.
The workflow details and work-unit regrouping implement that instruction; they are not quotations of earlier decisions.

### D181

`(C * D)(X, Y)` constructs the element `(X, Y)` of the product category `C * D`.
For `D = C`, the chosen product functor maps that element to the product object in `C`.
This separates the input category from the result category and supersedes the conflated constructor identity in D149.
Owner: [Products and component functors](functor.md#products-coproducts-and-component-functors).

Source: product-category clarification in Codex session `01a06ea2-e610-7fd0-acee-d0efc8315d93`, 2026-09-04T23:16:38.402Z.
The product-functor consequence uses the existing chosen-product definition in `functor.md`.

### D182

Extend the workflow in [AGENTS.md](../AGENTS.md) with history-grounded guidance for preserving semantic claims during repairs.
The guidance covers mathematical scope, dependency reuse, construction state, representative public consumers, proof-preserving test rewrites,
exact typing, independent review, correction continuity, and bounded policy interpretation.
It extends D180's procedure. Topic contracts, phase acceptance, and the D132 admission boundary remain with their existing owners.

Source: workflow-guidance instruction in Codex session `01a06ea2-e610-7fd0-acee-d0efc8315d93`, 2026-09-04T23:41:01.450Z.
Behavioral mechanisms are inferences from inspected changes, not claims about an agent's intent or model capability.
Evidence locators: `4fe67cf`, `5baf28a`, `460a281`, `df0e19c`, `6f32004`, `6660e9c`, `7f8bea5`, `3f8ee1d`,
`94584a2`, `13bdb2a`, `270b9d5`, `af73c40`, `b7c4853`, `e8f54c0`, and `51c74ab`.
The implementation details and causal comparison are recorded with this documentation change in Git.
