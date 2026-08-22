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

# The research Sage environment, pulled rather than rebuilt.
#
# ghcr.io/dzackgarza/sage:develop is published by the fork itself, from the
# same `just research-environment-sync` the desk runs. Every repository that
# writes Sage against that fork consumes this one build; none of them compiles
# Sage, and none of them reaches for upstream's image, which is a different
# Sage on Python 3.12.
#
# SAGE_ROOT is baked in at configure time, so the tree is restored to /sage --
# the path it was configured at -- rather than relocated.
#
# The sage profile installs nothing and asserts SAGE_BIN is executable, so this
# runs before that assertion: _qc.yml calls it ahead of setup-profile, and
# $GITHUB_ENV is the channel that reaches the validating step.

# CI: pull the research Sage environment and export SAGE_BIN.
ci-provision-sage:
    #!/usr/bin/env bash
    set -euo pipefail
    docker create --name sage-env ghcr.io/dzackgarza/sage:develop
    sudo install -d -o "$(id -un)" -g "$(id -gn)" /sage
    docker cp sage-env:/sage/. /sage/
    docker rm sage-env
    sage_bin=/sage/.venv/bin/sage
    # The checkout under test, not whatever version the image happened to carry.
    "$sage_bin" -pip install --quiet --no-deps -e .
    echo "SAGE_BIN=$sage_bin" >> "${GITHUB_ENV:-/dev/stdout}"
    "$sage_bin" -c "import sage_categories; print('sage_categories', sage_categories.version())"
