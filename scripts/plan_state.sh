#!/usr/bin/env bash
# Execution ownership is PLAN-native-engine-remediation and its retained issue DAG.
# Historical phase cards are evidence, not active execution prerequisites.
set -euo pipefail

plan_id=PLAN-native-engine-remediation
plan="$(uvx --python 3.14 --from git+https://github.com/dzackgarza/agent-memory agent-memory plan show "$plan_id")"
jq -e --arg id "$plan_id" '
    .id == $id and .type == "plan"
    and (.metadata.status == "in-progress" or .metadata.status == "complete")
    and (.metadata.parents | index("[[FEATURE-functor-owned-category-framework]]") != null)
' <<<"$plan" >/dev/null

# The native validator checks parentage, dependency cycles, inaccessible blockers,
# completion contracts, and selection of work whose own and ancestor blockers are
# satisfied. A source directory or an archived completion label cannot certify a
# prerequisite. Failure to read either owner is a failed gate.
report="$(uvx --from git+https://github.com/dzackgarza/itree itree doctor dzackgarza/sage-categories --json | tee /dev/stderr)"
jq -e '.status == "ok" and .root.ref.number == 36' <<<"$report" >/dev/null

if [ "$(jq -r '.metadata.status' <<<"$plan")" = complete ]; then
    jq -e '.next_issue.kind == "absent" and .metrics.open_work_units == 0' <<<"$report" >/dev/null
    jq -er '.body' <<<"$plan" | grep -Eq '^- Accepted revision: [0-9a-f]{40}$'
fi

printf 'plan-state: %s; native issue dependencies validated; public consumer acceptance remains required\n' "$plan_id"
