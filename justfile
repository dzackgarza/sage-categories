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

# Put Sage on the CI runner and report where it landed.
#
# The sage profile installs nothing and asserts SAGE_BIN is executable, so
# this recipe has to provide Sage before that assertion runs -- _qc.yml calls
# it ahead of setup-profile for exactly that reason. The repo's .envrc cannot
# serve here: _qc.yml sources it a step later, and its SAGE_BIN is a path on
# the developer's machine. $GITHUB_ENV is the channel that reaches the
# validating step.
#
# `sagemath/sagemath` is the distribution build, driver script included; the
# apt and conda routes do not carry that script. The tag is `develop`, which
# follows Sage's development branch, so the gate runs the Sage this package is
# written against rather than the last release.

# CI: install Sage on the runner and export SAGE_BIN.
ci-provision-sage:
    #!/usr/bin/env bash
    set -euo pipefail
    docker create --name sage-dist sagemath/sagemath:develop
    sudo install -d -o "$(id -un)" -g "$(id -gn)" /home/sage
    docker cp sage-dist:/home/sage/sage /home/sage/sage
    docker rm sage-dist
    sage_bin=/home/sage/sage/sage
    "$sage_bin" -pip install --quiet pytest coverage
    "$sage_bin" -pip install --quiet -e .
    echo "SAGE_BIN=$sage_bin" >> "${GITHUB_ENV:-/dev/stdout}"
    "$sage_bin" -c "import sage_categories; print('sage_categories', sage_categories.version())"
