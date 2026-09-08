# Mathematical execution DAG

This is the repository entry point to the approved
[native-engine remediation plan][plan], especially its sections 19 and 20.
The plan owns full mathematical obligations, engine allocations, acceptance,
and retained issue dependencies. This file names their work nodes and immediate
dependency edges; it does not assert that an implementation is absent or that
an earlier checkpoint must be repeated. Start from delivered source and valid
consumer evidence. Preserve work already in flight.

Read [AGENTS.md](AGENTS.md), the named [contribution policies](CONTRIBUTING.md),
and [COMPLAINTS.md](COMPLAINTS.md) before selecting affected work. The
[continuation locator](docs/remediation-handoff.md) supplies plan retrieval when
the local vault link is unavailable.

## Nodes and prerequisites

`A` in `B`'s Needs column means `A -> B`: B consumes the stated output of A.
`none` means no prerequisite node in this table; existing mathematical inputs
and the plan's retained issue contracts still apply. Acceptance belongs to the
linked contract, not the short node name. Multiple prerequisites are conjunctive.

| ID | Work and full obligation in the governing plan | Needs |
| --- | --- | --- |
| `runtime` | Section 19.1: runtime bindings, owned reconstruction, exact installation, earlier objects and selected maps | none |
| `sets` | Section 19.2: restore general Sets products, including rule-defined integers, represented reals and mixed inputs, while retaining finite native operations | none |
| `functors` | Section 19.2: native categories, both functor actions, transformations, compositions, whiskerings and nonenumerated sources | none |
| `paths` | Section 19.2: complete typed presented paths and native finite universal-construction operation families | none |
| `universal` | Section 19.2: retained diagrams, chosen apex/legs/mediators, nonstandard indexing, opposites and predicate subobjects (#30/#24/#41; intrinsic #32) | `sets`, `functors`, `paths` |
| `indexed` | Section 19.2: full infinite/nonenumerable indexed constructions and sequential colimits with maps and their specified equality | `sets`, `functors` |
| `diagrams` | Section 19.3: symbolic, supplied monoidal and cell interpretation, including nonstrict comparisons and noninvertible ordinary arrows | `functors` |
| `refinement` | Section 19.4: same-object refinement (#31), with existing inherited operations | none |
| `inverses` | Section 19.4: retained inverses (#33) | none |
| `isofibrations` | Section 19.4: composite isofibrations and generic state transport (#35) | none |
| `named` | Section 19.4: named projections and composites (#39), consuming the required structure and transport | `refinement`, `inverses`, `isofibrations` |
| `additive` | Section 19.4: native additive owner (#40 and additive #32), exact Ab Homs, both selected presentations and forgetful maps | `named`, `paths` |
| `tensor` | Section 19.4: ordinary tensor (#42), induced maps, universal factors and comparisons | `additive` |
| `relative` | Section 19.4: relative tensor (#43), distinct outer rings, noncommutative middle ring, both actions and balanced factors | `tensor`, `inverses` |
| `actions` | Section 19.4: supplied actions and module transport (#44), retaining distinct acting and acted-on categories and generic structured objects | `relative`, `named`, `diagrams` |
| `kan` | Sections 14 and 19.4: Kan, weighted, profunctor and relation consumers with actual diagrams and universal maps | `universal`, `functors` |
| `orders` | Section 19.4: #41, #9/#10 order branch; selected squares, supplied inverse transport, indexed comparisons and undecided predicates | `universal`, `inverses` |
| `groups` | Section 19.5: group presentations (#21), relation arrows and universal factors | `named`, `paths` |
| `modules` | Section 19.5: module presentations and constructors (#22), scalar conventions, cokernel and supplied actions | `tensor` |
| `module-sums` | Section 19.5: arbitrary indexed module sums, finite support per element, injections and universal maps | `indexed`, `actions` |
| `algebras` | Section 19.5: #46 then #23; full algebra presentations and infinite underlying-module consumer R<x,y>, retaining genuine forgetful maps | `relative`, `module-sums` |
| `rings` | Section 19.5: rings/localization (#47), owned maps and native algebra integration | `named`, `additive` |
| `spaces-sheaves` | Section 19.5 and #48: spaces, topology/maps, sheaf values and restrictions on their proper domains | `rings` |
| `affine` | Sections 17 and 19.5: affine branch (#49), contravariant Spec, native pullbacks and induced maps | `spaces-sheaves` |
| `gluing` | Sections 17 and 19.5: gluing (#50), projective-line charts, structure sheaf and chart-swap action | `affine` |
| `topological-colimit` | Section 19.5: full CP^infty diagram, CW topology, inclusions and induced continuous maps | `indexed`, `spaces-sheaves` |
| `adeles` | Section 19.5: full restricted product, topology, ring operations, component maps and diagonal QQ map | `indexed`, `rings`, `spaces-sheaves` |
| `gate` | Section 19.6: ordinary execution gate (#51) against the governing plan and retained issue/PR claims | none |
| `python-runtime` | Section 19.6: declared Sage/Python runtime available to actual execution processes | none |
| `static` | Sections 18 and 19.6: exact static projection (#45), developed alongside the same runtime consumers | none |
| `acceptance` | Section 20 in full, including displaced-code removal under 20.1 and native integration extensions under 20.2 | `runtime`, `sets`, `functors`, `paths`, `universal`, `indexed`, `diagrams`, `refinement`, `inverses`, `isofibrations`, `named`, `additive`, `tensor`, `relative`, `actions`, `kan`, `orders`, `groups`, `modules`, `module-sums`, `algebras`, `rings`, `spaces-sheaves`, `affine`, `gluing`, `topological-colimit`, `adeles`, `gate`, `python-runtime`, `static` |

## Use the graph at the consumer boundary

The plan's named next boundary is the general Sets product; reuse its accepted
repair if already delivered. Continue independent authorized mathematics while
runtime or gate repairs proceed. A runtime binding defect blocks acceptance of
the affected consumer, not all source work. Static projection accompanies each
affected operation; the `static` node is not permission to defer its first types.

Edges apply to the required output, not blanket closure of a work family. In
particular, additive #32 does not require the independent opposite-diagram #24
consumer; group presentations need #32's intrinsic coequalizer, not additive
completion. The topology and adelic extensions do not block projective-line
gluing. Ordinary finite module/tensor consumers do not await all infinite-rank
extensions. Read the retained issue prerequisites before selecting a subtask.

When a node's independently deliverable output needs its own scheduling, name
that output at the existing task and redirect the affected edges without losing
any obligation. Preserve the plan's full hypotheses and section-20 consumers.
Do not infer readiness from a phase label or a package installation. Record new
observed issues in COMPLAINTS and link the affected node; logging is not repair.

Before committing graph changes, check unique IDs, resolved prerequisite IDs,
absence of cycles, and a path from each required node to `acceptance`. Keep
completion evidence in the existing plan/issue records and implementation commits,
not a second checkbox ledger in this routing table.

[plan]: .agents/plans/features/FEATURE-functor-owned-category-framework/plans/PLAN-native-engine-remediation/PLAN-native-engine-remediation.md
