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
architecture:
    PYTHONPATH=src uvx --python 3.14 --from import-linter lint-imports --config pyproject.toml
    uvx --from ast-grep-cli ast-grep scan --config .ast-grep/architecture.yml --error src

# Run the full SageMath test suite before pushing.
test-push: architecture
    @just -f ~/ai-review-ci/justfiles/sage.just -d . test-push

# Run CI acceptance QC through the central implementation.
test-ci:
    @just -f ~/ai-review-ci/justfiles/sage.just -d . test-ci

# The research Sage environment, run rather than extracted.
#
# ghcr.io/dzackgarza/sage:develop is published by the fork itself, from the
# same `just research-environment-sync` the desk runs. Every repository that
# writes Sage against that fork consumes this one build; none of them compiles
# Sage, and none of them reaches for upstream's image, which is a different
# Sage on Python 3.12.
#
# The image states its own consumption rule: /sage is neither relocatable nor
# separable. SAGE_ROOT is baked in at configure time, sagelib's extension
# modules link against the Debian libraries the image installs, and the venv
# interpreter is a uv symlink into /root, outside /sage entirely. QC therefore
# runs inside the container and reaches it through host wrappers.
#
# The profile derives `python` and `sage-preparse` as siblings of SAGE_BIN, so
# all three wrappers share one directory. It preparses into host tempdirs and
# byte-compiles from a script on stdin, so the tempdir roots are mounted at
# their own paths and exec keeps stdin open.
#
# The sage profile installs nothing and asserts SAGE_BIN is executable, so this
# runs before that assertion: _qc.yml calls it ahead of setup-profile, and
# $GITHUB_ENV is the channel that reaches the validating step.

# CI: start the research Sage environment and export SAGE_BIN.
ci-provision-sage:
    #!/usr/bin/env bash
    set -euo pipefail
    workspace="$(pwd -P)"
    qc_infra="${HOME}/ai-review-ci"
    qc_cache="${HOME}/.cache/quality-control"
    test -d "${qc_infra}"
    install -d "${qc_cache}"
    mounts=(-v "${workspace}:${workspace}" -v "${qc_infra}:${qc_infra}" -v "${qc_cache}:${qc_cache}" -v /tmp:/tmp)
    if [ -n "${RUNNER_TEMP:-}" ] && [ "${RUNNER_TEMP#/tmp/}" = "${RUNNER_TEMP}" ]; then
        mounts+=(-v "${RUNNER_TEMP}:${RUNNER_TEMP}")
    fi
    docker run --detach --name sage-env "${mounts[@]}" --workdir "${workspace}" \
        ghcr.io/dzackgarza/sage:develop sleep infinity
    sage_dir=/usr/local/sage-env
    sudo install -d "${sage_dir}"
    for tool in sage sage-preparse; do
        printf '%s\n' \
            '#!/usr/bin/env bash' \
            "exec docker exec -i -w \"\$(pwd -P)\" sage-env /sage/.venv/bin/${tool} \"\$@\"" \
            | sudo tee "${sage_dir}/${tool}" >/dev/null
        sudo chmod +x "${sage_dir}/${tool}"
    done
    printf '%s\n' \
        '#!/usr/bin/env bash' \
        'set -euo pipefail' \
        'if [ "$#" -gt 0 ] && [ "$1" = "/usr/local/sage-env/sage-preparse" ]; then' \
        '    shift' \
        '    exec docker exec -i -e "MYPYPATH=${MYPYPATH:-}" -w "$(pwd -P)" sage-env /sage/.venv/bin/python /sage/.venv/bin/sage-preparse "$@"' \
        'fi' \
        'exec docker exec -i -e "MYPYPATH=${MYPYPATH:-}" -w "$(pwd -P)" sage-env /sage/.venv/bin/python "$@"' \
        | sudo tee "${sage_dir}/python" >/dev/null
    sudo chmod +x "${sage_dir}/python"
    sage_bin="${sage_dir}/sage"
    # Install this checkout, its runtime dependencies, and its QC dependency group together.
    docker exec -i -w "${workspace}" sage-env /sage/.venv/bin/uv pip install \
        --python /sage/.venv/bin/python \
        --project "${workspace}" \
        --group dev \
        --group platform \
        --editable "${workspace}"
    # GAP PackageManager resolves the exact native package releases into this checkout.
    docker exec -i -w "${workspace}" sage-env gap -q -r --packagedirs "${workspace}/.gap/pkg" "${workspace}/.gap-packages.g"
    # JuliaPkg reads the package-owned juliapkg.json and resolves Julia, Catlab, and GATlab.
    docker exec -i -w "${workspace}" sage-env /sage/.venv/bin/python -m juliapkg resolve
    # The CI tier measures coverage with the Sage interpreter's own Python, so
    # the tool has to live in that environment rather than on the runner.
    "${sage_dir}/python" -m uv pip install --quiet coverage
    echo "SAGE_BIN=$sage_bin" >> "${GITHUB_ENV:-/dev/stdout}"
    "$sage_bin" -c "import sage_categories; print('sage_categories', sage_categories.version())"
