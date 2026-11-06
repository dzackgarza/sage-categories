# ai-review-ci SageMath QC delegation justfile.
# The central implementation lives in ~/ai-review-ci/justfiles/sage.just.
# Public recipes delegate to that central justfile while preserving this repo as the caller root.

# ai-review-ci contract variables consumed by doctor and workflow installers.
ai_review_ci_schema_version := "1"
ai_review_ci_profile := "sage"
ai_review_ci_ref := "main"
ai_review_ci_release_channel := "main"
ai_review_ci_workflow_template_version := "1"
ai_review_ci_local_delegation := "global-justfile"
ai_review_ci_default_branch := "main"
# List available recipes.
default:
    @just --list

# Run commit-tier SageMath QC through the central implementation.
test-commit:
    @just -f ~/ai-review-ci/justfiles/sage.just -d . test-commit

# Architecture invariants from specs/system.md and specs/resolution.md (D132): a hard stop before push.
#
# The coverage check runs first (D174): a rule whose file glob matches nothing is green
# because it read nothing, which is not a measurement. A rule names only packages in the
# tree, so each P-phase adds its package back to the rules it owns, exactly as the
# pyproject comment states for the import contracts.
# Cheap local boundary check: import graph plus structural leaf rules, no Sage runtime.
architecture-boundary:
    #!/usr/bin/env bash
    set +e
    PYTHONPATH=src uvx --python 3.14 --from 'import-linter==2.15' lint-imports --config pyproject.toml
    import_status=$?
    uvx --from 'ast-grep-cli==0.45.0' ast-grep scan --config .ast-grep/architecture.yml --error src tests/kernel
    ast_status=$?
    if [ "$import_status" -ne 0 ] || [ "$ast_status" -ne 0 ]; then exit 1; fi

architecture:
    uv run --no-project --python 3.14 --with pyyaml python scripts/rule_coverage.py
    uv run --no-project --python 3.14 --with pyyaml python scripts/architecture_regressions.py
    just architecture-boundary

# Validate the governing plan and its native issue dependencies.
plan-state:
    bash scripts/plan_state.sh

# Regenerate the compiler-derived static projection and make every emitted stub
# satisfy the same global Ruff contract used by repository QC.
generate-stubs:
    #!/usr/bin/env bash
    set -euo pipefail
    sage_bin="${SAGE_BIN:?SAGE_BIN must name the Sage executable}"
    ruff_config="${HOME}/ai-review-ci/tool-configs/ruff-global.toml"
    projector_python="$(uv run --no-sync --group dev python -c 'import sys; print(sys.executable)')"
    PATH="$(dirname "$projector_python"):$PATH" "$sage_bin" -c "from pathlib import Path; from sage_categories.kernel.stub_generator import _generate_stubs; _generate_stubs('sage_categories', Path('src/sage_categories'), Path('$ruff_config'))"
    mapfile -t stubs < <(find src/sage_categories -type f -name '*.pyi' -print | sort)
    test "${#stubs[@]}" -gt 0
    uvx --from ruff ruff check "${stubs[@]}"
    uvx --from ruff ruff format --check --config "$ruff_config" "${stubs[@]}"
    uvx --from ruff ruff check --config "$ruff_config" "${stubs[@]}"

# Run the full SageMath test suite before pushing.
test-push: plan-state architecture
    @just -f ~/ai-review-ci/justfiles/sage.just -d . test-push

# Run CI acceptance QC through the central implementation.
test-ci:
    @just -f ~/ai-review-ci/justfiles/sage.just -d . test-ci

# The research Sage environment.
#
# ghcr.io/dzackgarza/sage:develop is published by the fork itself, from the
# same `just research-environment-sync` the desk runs. Every repository that
# writes Sage against that fork consumes this one build; none of them compiles
# Sage, and none of them reaches for upstream's image, which is a different
# Sage on Python 3.12.
#
# ai-review-ci's _qc.yml runs sage test-ci inside that image, where SAGE_BIN is
# /sage/.venv/bin/sage, and runs this recipe there before setup-profile.

# CI: install this checkout and its native dependencies into the image's Sage.
ci-provision-sage:
    #!/usr/bin/env bash
    set -euo pipefail
    workspace="$(pwd -P)"
    # Install this checkout, its runtime dependencies, and its QC dependency group together.
    uv pip install \
        --python /sage/.venv/bin/python \
        --project "${workspace}" \
        --group dev \
        --editable "${workspace}"
    # GAP PackageManager resolves the exact native package releases into this checkout.
    gap -q -r --packagedirs "${workspace}/.gap/pkg" "${workspace}/.gap-packages.g"
    # JuliaPkg reads the package-owned juliapkg.json and resolves Julia, Catlab, and GATlab.
    /sage/.venv/bin/python -m juliapkg resolve
    "$SAGE_BIN" -c "import sage_categories; print('sage_categories', sage_categories.version())"
