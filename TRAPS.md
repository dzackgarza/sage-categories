# Execution traps

Concrete failure patterns from the categorical ownership remediation.
Procedure remains in [AGENTS.md](AGENTS.md). The
[implementation handoff](docs/remediation-handoff.md) owns the remaining code work.

## Separate issues can share an unstable implementation boundary

**Observed:** named functor restrictions required changes to refinement,
isofibration inference, retained construction order, and predicate dispatch.
The shared repair spans `7edb77a`, `14ff232`, and `b8f8f6c`. Work on dependent
consumers continued while these core interfaces changed. This required further
integration and execution of the same public paths.

**Trigger:** another active consumer needs a change to the core operation that
an existing worker is modifying. Disjoint file lists do not establish independent
work when both consumers depend on that operation.

**Action:** apply [Delegation](AGENTS.md#delegation) at the semantic dependency.
Give the shared repair one writer and one complete public consumer. Resume its
dependent writers from the resulting committed interface. Keep the original
consumer and expected equations fixed through each repair.

## A prerequisite chain can consume the session without completing a consumer

**Observed:** the source checkpoint `856a3dc` includes useful runtime repairs,
but exact derived-category implementation, additive ownership, and static
projection still prevent their dependent completion claims. The selected Ab
biproduct consumer remained incomplete after these shared repairs.

**Trigger:** the next repair adds another shared owner while the selected public
consumer remains incomplete. A new issue number or agent assignment does not
start a new completion claim.

**Action:** use the existing consumer as the milestone. Apply
[Repeated failures](AGENTS.md#repeated-failures) to the whole operation across
owner changes. At a checkpoint, compare the remaining milestone with the known
usage allowance before opening another workstream. State an unavailable allowance
as unknown. Preserve useful red work and identify the smallest complete repair
boundary when the current allocation no longer supports the milestone.

## Large context reads reproduce their own overhead

**Observed:** the session repeatedly returned combined skill, specification,
issue, and source dumps with truncation warnings. Subsequent reads had to recover
the missing relevant sections. The later cost investigation repeated this pattern
by loading several long guidance files together.

**Trigger:** a response is truncated, a previously loaded contract is requested
again, or a batch's combined output exceeds the intended reading scope.

**Action:** apply [Context and attention](AGENTS.md#context-and-attention).
Retain loaded contracts and exact locators. Budget the combined batch output.
Search for the owning definition, then read that complete definition and its
immediate callers. After truncation, retrieve only the missing relevant section.
For large logs, retain the raw file and return the specific diagnostic needed for
the next decision. Tool-reported output size does not establish the billed quota.

## Progress percentages need a defensible common measure

**Observed:** an estimated 20% completion was reported for a DAG spanning shared
runtime repairs through scheme constructions. The estimate supplied neither a
common unit of work nor a defensible weighting of remaining capabilities. It was
withdrawn. Its apparent precision could support an invalid extrapolation of
future usage.

**Trigger:** a whole-program percentage is requested while units differ greatly
in scope or lack complete public acceptance.

**Action:** state the assessed scope, weighting basis, and uncertainty with any
estimate. Separate delivered runtime behavior, static obligations, and accepted
consumer claims. When a common measure cannot be justified, report that limit
and the concrete completed boundary. Keep actual usage separate from estimates
of mathematical progress. A cost-to-completion projection needs its own evidence.

## Evidence boundary

The code evidence is the committed handoff and its linked public specimens.
The execution evidence is the parent session
`01a07936-6d42-7ac1-a62c-6115b98924eb`, 2026-09-07, read through the transcript
parser. The inspection covered repair commands, coordination calls, oversized
reads, and the completion estimate. It did not establish a billed usage allocation
or inspect every worker's internal execution. These entries identify observed
failure patterns and actions to apply; their future cost effect remains unmeasured.
