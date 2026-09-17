#!/usr/bin/env bash
# Remediation execution ownership is PLAN-native-engine-remediation. The GitHub issue
# tree also contains broader topic-contract work, so completion of this remediation
# plan does not imply that every reachable framework issue is closed.
# Historical phase cards are evidence, not active execution prerequisites.
set -euo pipefail

# Model selection is explicit, never inferred from the number of archived phases.
case "${1:-issue-dag}" in
    phase-managed)
        shift
        exec uv run --no-project --python 3.14 --with pyyaml python scripts/plan_state.py --model phase-managed "$@"
        ;;
    issue-dag)
        if [ "$#" -gt 0 ]; then shift; fi
        [ "$#" -eq 0 ] || { echo 'plan-state: unexpected issue-DAG arguments' >&2; exit 2; }
        ;;
    *) echo 'usage: plan_state.sh [issue-dag | phase-managed [phase options]]' >&2; exit 2 ;;
esac

plan_id=PLAN-native-engine-remediation
plan="$(uvx --python 3.14 --from git+https://github.com/dzackgarza/agent-memory agent-memory plan show "$plan_id")"
jq -e --arg id "$plan_id" '
    .id == $id and .type == "plan"
    and (.metadata.status == "in-progress" or .metadata.status == "complete")
    and (.metadata.parents | index("[[FEATURE-functor-owned-category-framework]]") != null)
' <<<"$plan" >/dev/null

# The native validator checks the live issue graph's parentage and dependency health.
# It remains useful after remediation closure because those issues continue to own
# broader topic contracts. Failure to read either owner is a failed gate.
report="$(uvx --from git+https://github.com/dzackgarza/itree itree doctor dzackgarza/sage-categories --json)"
printf '%s\n' "$report" >&2
jq -e '
    .status == "ok" and .metrics.errors == 0
    and .repo == "dzackgarza/sage-categories"
    and .root.kind == "present" and .root.ref.number == 36
    and .root.ref.repo_ref == {owner: "dzackgarza", repo: "sage-categories"}
' <<<"$report" >/dev/null

# The governing plan delegates the revision-scoped completion frontier to TODO.
uv run --no-project --python 3.14 python scripts/plan_state.py --model issue-dag

open_work_units="$(jq -r '.metrics.open_work_units' <<<"$report")"
printf 'plan-state: %s; remediation state valid; live issue DAG valid (%s broader open work units)\n' "$plan_id" "$open_work_units"
