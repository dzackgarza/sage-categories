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

# Run the full SageMath test suite before pushing.
test-push:
    @just -f ~/ai-review-ci/justfiles/sage.just -d . test-push

# Run CI acceptance QC through the central implementation.
test-ci:
    @just -f ~/ai-review-ci/justfiles/sage.just -d . test-ci

# CI: install this package and its Sage into a venv, and export SAGE_BIN.
#
# The sage profile installs nothing and asserts SAGE_BIN is executable, so
# this has to run before that assertion -- _qc.yml calls it ahead of
# setup-profile for exactly that reason, and $GITHUB_ENV is the channel that
# reaches the validating step. The repo's .envrc cannot serve: _qc.yml sources
# it a step later, and its SAGE_BIN is a path on the developer's machine.
#
# Sage arrives the way every other dependency does -- from the fork declared
# in pyproject.toml, which pins the interpreter this package is written
# against.

# CI: install Sage and this package into a venv, and export SAGE_BIN.
ci-provision-sage:
    #!/usr/bin/env bash
    set -euo pipefail
    sage_venv="${RUNNER_TEMP:-/tmp}/sage-venv"
    uv venv --python 3.14 "$sage_venv"
    uv pip install --python "$sage_venv/bin/python" .
    echo "SAGE_BIN=$sage_venv/bin/sage" >> "${GITHUB_ENV:-/dev/stdout}"
    "$sage_venv/bin/sage" -c "import sage_categories; print('sage_categories', sage_categories.version())"
