#!/usr/bin/env bash
# The phase-order invariants of the core plan card "Gate protocol" (D136, POL-DOC-028),
# read from the vault's card files. Each check names the failure it stops:
#   1. one phase is in-progress across every plan (phases were all left open at once);
#   2. a complete phase carries an accepted revision (statuses were flipped by the executor);
#   3. an open or complete phase has every prerequisite complete (later phases ran early);
#   4. no production leaf is in the tree before the core plan is complete (leaves were
#      built in parallel with the kernel, POL-DOC-021).
# Read-only on the vault; the cards change only through agent-memory.
set -euo pipefail

vault="${AGENT_MEMORY_VAULT:-$HOME/.agent-memory-vault}/projects/github.com__dzackgarza__sage-categories/plans"
core_plan="$vault/features/FEATURE-functor-owned-category-framework/plans/PLAN-pr-8-kernel-cat-architecture-convergence/PLAN-pr-8-kernel-cat-architecture-convergence.md"
test -d "$vault" || { echo "plan-state: vault not found at $vault"; exit 2; }

# Frontmatter of one card as JSON (the text between the first two '---' lines).
frontmatter() {
    awk 'NR==1 && $0=="---" {f=1; next} f && $0=="---" {exit} f' "$1" | uvx --quiet --from yq yq -c .
}

failures=0
fail() { echo "plan-state: $*"; failures=$((failures + 1)); }

declare -A status
declare -A file
while IFS= read -r card; do
    fm="$(frontmatter "$card")"
    id="$(jq -r .id <<<"$fm")"
    status["$id"]="$(jq -r '.status // "unstarted"' <<<"$fm")"
    file["$id"]="$card"
done < <(find "$vault" -name 'PHASE-*.md' | sort)

open=()
for id in "${!status[@]}"; do
    [ "${status[$id]}" = "in-progress" ] && open+=("$id")
done
if [ "${#open[@]}" -ne 1 ]; then
    fail "exactly one phase is in-progress; found ${#open[@]}: ${open[*]:-none}"
fi

for id in "${!status[@]}"; do
    card="${file[$id]}"
    st="${status[$id]}"
    if [ "$st" = "complete" ] && ! grep -Eq '^- Accepted revision: [0-9a-f]{7,40}$' "$card"; then
        fail "$id is complete without an accepted revision on its card"
    fi
    if [ "$st" = "in-progress" ] || [ "$st" = "complete" ]; then
        fm="$(frontmatter "$card")"
        while IFS= read -r dep; do
            [ -z "$dep" ] && continue
            dep="${dep#\[\[}"; dep="${dep%\]\]}"
            if [ "${status[$dep]:-missing}" != "complete" ]; then
                fail "$id is $st but its prerequisite $dep is ${status[$dep]:-missing}"
            fi
        done < <(jq -r '.dependsOn[]? // empty' <<<"$fm")
    fi
done

core_status="$(frontmatter "$core_plan" | jq -r .status)"
if [ "$core_status" != "complete" ]; then
    while IFS= read -r pkg; do
        name="$(basename "$pkg")"
        case "$name" in kernel|cat|__pycache__) ;; *) fail "production leaf '$name' is in src while the core plan is $core_status (D137, POL-DOC-021)";; esac
    done < <(find src/sage_categories -mindepth 1 -maxdepth 1 -type d)
fi

if [ "$failures" -gt 0 ]; then
    echo "plan-state: $failures failure(s)"
    exit 1
fi
echo "plan-state: active phase ${open[0]}; core plan $core_status"
