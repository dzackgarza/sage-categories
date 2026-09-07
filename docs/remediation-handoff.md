# Categorical ownership remediation: continuation

## Cutoff

Source checkpoint: `856a3dcf855535f286efb7de216cb5ee182c3dd5` on
`codex/functorial-core-kernel`, 2026-09-07. The delivery remains in
[draft PR #8](https://github.com/dzackgarza/sage-categories/pull/8).

This is a foundation implementation checkpoint. Full issue and phase acceptance
remains open. The checkpoint contains runtime repairs, public red consumers for
the remaining additive prerequisites, and unfinished static projection work.
An independent acceptance review of this revision remains required.

[Roadmap #36](https://github.com/dzackgarza/sage-categories/issues/36) owns the
execution DAG. [#37](https://github.com/dzackgarza/sage-categories/issues/37) owns
the immediate remediation; [#38](https://github.com/dzackgarza/sage-categories/issues/38)
owns the downstream presentations and geometry. Their acceptance contracts remain
unchanged. This document supplies the implementation continuation at the cutoff.

The next complete units are:

1. Repair static class identity and lexical dependencies at the generator. Use
   [the static handoff](remediation-static-handoff.md) and the unchanged public consumer.
2. Implement an exact derived category through its identity functor. Preserve its
   existing construction, projections, values, and inherited state. Use
   [the derived-category handoff](remediation-derived-handoff.md).
3. Give the exact category Ab its additive operations and retained forgetful
   functor. Complete the mixed free/torsion biproduct consumer.
4. Install the first abelian coequalizer in its intrinsic universal family.
5. Continue tensor, order, presentation, and geometry work along the issue DAG.

The first two units concern shared core owners. Finish them before editing an
algebra or order leaf. Each has one source writer; they share compiler-derived
interfaces. The order above is an execution choice, rather than a new mathematical
dependency between the two repairs.

## Mathematical boundary

A leaf definition should expose its categories, maps, hypotheses, and equations.
Evaluation of a functor action is an ordinary mathematical operation. When the
definition is a composite of known functors, retain that composite and its factors.

A product point, its image under a tensor map, and a multiplication image are
different mathematical objects. Write the required maps explicitly. The same rule
applies to associators, unit comparisons, and universal mediators.

A named magma, monoid, group, or defining action is legitimate mathematical data.
Private engine coordinates and runtime class state have different owners. A local
helper that copies such state does not supply the missing categorical map.

Keep a universal presentation, its apex, and a selected total construction distinct.
The intrinsic family C.Colimits(J) quantifies over cocones in C. A chosen cocone for
one diagram does not supply a chosen colimit functor on every diagram.

The layer boundary remains [specs/system.md](../specs/system.md). Mathematical
operations belong to their categories; the private kernel realizes declarations;
private computation engines own coordinates and algorithms. The linked issue
contracts and topic specifications retain the full required mathematics.

## Runtime evidence retained at the checkpoint

The table identifies the precise scope of existing evidence. It is not an issue
closure table. Source and public specimens are durable; temporary command logs are
secondary local records.

| Owner | Delivered runtime boundary | Public specimen and remaining delta |
| --- | --- | --- |
| #31 | Sage-generated implementation classes retain written methods and initialized state through refinement. | `tests/algebra/test_module_scaffold.sage` retains the two distinct F₂×F₂ actions. Its exact Ab hom-owner assertion remains red under #40. |
| #33 | Fixed hom owners, full-subcategory refinements, intersections, and retained inverse equations use the same semantic category. | `tests/algebra/test_named_group_inverse.sage`: cyclic groups of different orders and both orders of property refinement. Downstream tensor comparisons and exact static consumers remain required. |
| #35 | Composite functors retain their factors and inherit the isofibration property under its stated hypotheses. | `tests/kernel/test_composite_inheritance.sage`: nonidentity actions n↦n+1 and m↦2m give the inherited value 8 at 3. |
| #39 | Named restrictions are composites of product projections, neutral restrictions, and retained universal sections. Inherited axiom accessors retain their source axiom. | `tests/algebra/test_named_functor_calculus.sage` and `test_ring_scaffold.sage`. The abelian leaf still needs its single actual forgetful composite and static images. |
| #30 | Chosen enumeration is e:I→X, with its inverse and a separate inclusion I→NN. Product enumeration uses the retained factor enumerations. | `tests/kernel/test_chosen_enumeration_consumers.sage` and `test_named_set_declaration.sage`. The final finite-subset specimen uses {1,2}⊂NN and the distinct index set {7,9}. |
| #41 | Predicate subobjects retain the ambient set and inclusion. Their predicate can return True, False, or a legitimate undecided result. Finiteness can follow independently from a retained finite enumeration. | `tests/kernel/test_predicate_set_subobjects.sage` and the finite-subset enumeration specimen. Order consumers remain under #9. |
| Generic #32 | Intrinsic universal families preserve C, their diagrams, oriented legs, and mediators. Distinct presentations can share an apex. | `tests/kernel/test_intrinsic_universal_presentations.sage`: c is the coproduct in the full subcategory on a,b,c,e; a competing cocone reaches e. The actual abelian coequalizer remains open. |
| #24 | The indexed coproduct and its opposite limiting presentation retain the original indexing category and dual mediator. | The final test in `test_intrinsic_universal_presentations.sage` uses nonidentity maps from {2,3} and {4,5} into {20,30,41,51}. Fixed-revision acceptance remains required. |
| #44 | Transport uses the scalar identity in the acting category of the supplied action M×C→C. | `tests/algebra/test_module_transport_owners.sage`: M=Sets, C=Sets×1, a changed action, exact endpoints, and transport back. The static owner parameters remain under #45. |

The complete intrinsic/dual specimen and chosen-enumeration specimen were executed
against the final source delta included in the checkpoint. Other rows retain their
focused public evidence from the integrated work; they have not received a new
independent acceptance review at this revision.

## Immediate additive unit: #40

### Exact input and owner

Use the retained category

```python
Ab = AdditiveGroups(Cartesian(Sets())).Commutative()
```

Its identity-bound implementation prerequisite is described separately. The
mathematical result is an operation on this category, including existing objects,
points, homomorphisms, and functor images.

`tests/algebra/test_additive_biproduct_owner.sage` is the committed public red proof.
It fails at `Ab.biproduct(Z, Z/4)`: the category declares no biproduct. Its later
assertions remain part of the required result.

The specimen retains both the product and coproduct presentations of Z⊕Z/4. It
checks projections, inclusions, diagonal identities, cross zero morphisms, pairing,
and copairing. The pair is n↦(2n,n mod 4); the copair is (a,b)↦a+b mod 4.
Their composite must be n↦3n mod 4. Both mediators have exact base Ab.

The same specimen applies the actual functor Ab→Sets to objects and arrows. A plain
set product remains an independent nonadditive consumer.

### Required ownership repair

The current `Sets.ObjectForm` requires additive operations, including direct sum
and zero. Split the actual responsibilities before changing names. Sets owns its
general products and maps. Ab owns biproducts, zero morphisms, and linear extension.
The private abelian engine evaluates its Smith coordinates, matrices, and quotient
representatives.

Inspect `src/sage_categories/sets/finite.py`,
`src/sage_categories/algebra/abelian.py`, their topic contracts, and immediate
callers. Reuse the existing generic limit and colimit presentations. A possible
private engine destination is `algebra/_abelian_sage.py`; its exact interface must
follow the required additive operations and existing engine dependency.

`_linear_homomorphism` currently constructs an AdditiveGroups hom instead of a hom
with exact base Ab. Preserve the existing failing assertion in
`test_module_scaffold.sage` while correcting this owner. `_points` and `_point_map`
should apply one retained forgetful composite; their repeated action evaluation
does not retain that represented factorization.

### Complete consumer boundary

Finish the mixed biproduct, its actual forgetful images, the exact Ab hom owner,
existing additive calculations, and static endpoints in the same additive unit.
Then exercise the module consumer that originally exposed the wrong hom base.
The generic derived-category repair must precede these leaf edits.

## Coequalizers, tensors, and supplied actions

| Unit and prerequisites | Required construction | Decisive next consumer |
| --- | --- | --- |
| #32: generic intrinsic families plus #40 | For f,g:A→B in Ab, retain B/im(f−g), its quotient cocone, and its mediator in Ab.Colimits(J). | Distinct relation maps, a nonzero quotient, and an independently supplied equalizing homomorphism h. Obtain its factor from the presentation and check the factorization equation. |
| #42: #32 and #33 | The abelian tensor functor on objects and arrows, including free summands, its unit, and comparisons. Its universal input has the declared biadditivity hypothesis. | Z⊗Z≅Z, Z⊗Z/4≅Z/4, a torsion tensor, and nonidentity morphism images. Apply both directions of unit comparisons and check the universal equations. |
| #43: #42 | The actual bifunctor Bimod(R,S;V)×Bimod(S,T;V)→Bimod(R,T;V), defined by its balancing coequalizer. | Retain the noncommutative middle ring. Check both outer actions, a nonidentity pair of maps, composition, balancing, and an independent mediator. |
| #44: runtime repair present; static continuation in #45 | For φ:X→Y, use ρY=φ∘ρX∘(1A•φ⁻¹) in the supplied action. | Preserve the existing distinct-category example and its reverse transport. Add exact static distinctions between M and C. |

For relative tensors, derive h from

```text
h ∘ q_(X,Y) = q_(X′,Y′) ∘ (f ⊗ g).
```

Descend the outer actions using the specified preservation of the balancing
coequalizer by tensoring. General V retains these hypotheses. The ordinary
finitely presented instance supplies its evaluator. Unit and associativity maps
come from this universal data and retain owned inverses and coherence equations.

### Existing tensor work to integrate

Commit `e59ab4f52032e48695e4bba352f079b5696ced72` is already in this branch. It adds
`AbelianBimoduleTensor`, free Smith summands, retained relative quotients, and unit
and associativity comparisons. Its mathematical consumer is
`tests/algebra/test_bimodule_tensor_monoidal_scaffold.sage`, with additional tensor
claims in `test_abelian_tensor_scaffold.sage`.

That commit records deferred Sage execution. This cutoff does not establish its
acceptance. Read its complete source and assertions after repairing Ab. Reuse its
required behavior through the owned coequalizer and tensor maps. Current
representative callbacks in the associator need inspection at that boundary.

## Relations, orders, and downstream program

The issue DAG remains authoritative. The table gives the next complete result to
seek after its prerequisites; each linked issue retains its detailed contract.

| Unit | Prerequisites | Result and public evidence to retain |
| --- | --- | --- |
| [#9](https://github.com/dzackgarza/sage-categories/issues/9), with #10 admission reconciliation | #41, #30, #33, generic #32 | Transport R↪X×X along an isomorphism by inverse image under φ⁻¹×φ⁻¹. Retain the chosen square. Exercise an infinite carrier, two presentations sharing an apex, and an indexed order with its universal comparison. Preserve exact False and undecided admission outcomes. |
| [#21](https://github.com/dzackgarza/sage-categories/issues/21) | #39 and the needed universal calculus | Free group objects and relation arrows give an actual presentation. A relation-respecting assignment factors uniquely; an incompatible assignment does not define that factor. |
| [#22](https://github.com/dzackgarza/sage-categories/issues/22) | #42 | Finite free modules and a relation map give the specified cokernel. Retain the noncommutative scalar example, the correct scalar side, and the universal map. |
| [#46](https://github.com/dzackgarza/sage-categories/issues/46), then [#23](https://github.com/dzackgarza/sage-categories/issues/23) | #43, then #46 | Algebras are monoids in the supplied relative monoidal category. Their presentations use its free construction and coequalizer. Keep central commutative-base algebras distinct from general noncentral ring maps. |
| [#47](https://github.com/dzackgarza/sage-categories/issues/47) | #39 and #40 | Commutative-ring presentations and localization, with their universal maps and exact ring owners. |
| [#48](https://github.com/dzackgarza/sage-categories/issues/48) | #9 | Spaces, sheaves, and the geometric structures needed by the specified locally ringed spaces. |
| [#49](https://github.com/dzackgarza/sage-categories/issues/49) | #47 and #48 | Contravariant Spec acts on ring maps, including maps on sections. Preserve the affine comparison and variance. |
| [#50](https://github.com/dzackgarza/sage-categories/issues/50) | #49 | Glue affine charts as locally ringed spaces. Retain the projective line, its structure sheaf, and the chart-swap automorphism. |

Group, module, and algebra presentations consume their own free constructions.
Their sibling order imposes no additional mathematical dependence. The broader
cardinality obligations remain with #4 and the production plan. Finite enumeration
evidence does not establish those broader algorithms.

## Resume and acceptance

Start with the current Git revision and working tree. Read this handoff, the next
unit's issue, its topic owner, and its complete public specimen. Retrieve plan
state through the project vault:

```bash
uvx --python 3.14 --from git+https://github.com/dzackgarza/agent-memory agent-memory plan show PLAN-categorical-ownership-remediation-dag
uvx --python 3.14 --from git+https://github.com/dzackgarza/agent-memory agent-memory plan show PLAN-pr-8-kernel-cat-architecture-convergence
uvx --python 3.14 --from git+https://github.com/dzackgarza/agent-memory agent-memory plan show PLAN-mypy-static-projection-remediation
```

Use `phase show` and `card dag` for the active phase and direct prerequisites.
Preserve historical accepted revisions where their claims remain valid. The new
cutoff has no phase acceptance record.

The working Sage runtime is the research environment, with Python 3.14. Use the
repo `justfile` and actual `sage -c` entry point. A focused Sage specimen runs as:

```bash
sage -c 'from sage.repl.preparse import preparse; path="tests/kernel/test_exact_derived_category_implementation.sage"; exec(compile(preparse(open(path).read()), path, "exec"))'
```

Replace only the literal test path for another owned specimen. Preserve its input,
equations, and expected owners. Commit and push hooks own aggregate checks. Exact
static-consumer commands are in the static handoff.

At each completed unit, commit the implementation and its complete public consumer.
Use the repository's fixed-revision independent review protocol and owned
architecture checks before phase acceptance. Review the claim and source at that
revision, including inherited behavior and the static projection. A generic
repair includes its first real consumer; a later integration phase composes
capabilities that already work.

## Remote recovery

The ordinary push of source checkpoint `856a3dc` is blocked by
[#51](https://github.com/dzackgarza/sage-categories/issues/51). The push stops at
`plan-state`: it requires one active vault phase, while current execution uses
the issue DAG and the earlier core phases are archived. The later architecture
and source push checks were not reached.

The remote branch still points to
`a0350a123e9e574166751ea070c37ccfbbbd1b05`. The source checkpoint and the committed
handoff therefore require this local checkout for recovery. The local push log
is `/tmp/sage-categories-cutoff-push.log`.

Resolve #51 against the actual execution owner, then use the ordinary push:

```bash
git push origin codex/functorial-core-kernel
```

Inspect the next real gate result. The source also has the explicit red consumers
under #40 and #45 described above. Their sanctioned red commits authorize those
individual checkpoints; they do not certify the source or grant a general push
exception. Preserve the full acceptance claims while completing the repairs.

GitHub cutoff snapshots linked from #36, #40, and #45 preserve the continuation
text independently of this blocked source push. The repository files own the
editable handoff; the issue contracts own required behavior.
