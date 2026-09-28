#!/usr/bin/env bash
# Provision a conda-forge Sage runtime for this checkout on a host without the
# stable Sage installation (for example a cloud session container).
#
# Mirrors the CI setup in the justfile: the Sage interpreter, this checkout with its
# dev and platform dependency groups, the exact GAP package releases in .gap/pkg, and
# the Julia packages from juliapkg.json. Run from the repository root:
#
#     SAGE_PREFIX=/opt/sage scripts/provision_conda_sage.sh
#
# then use SAGE_PREFIX=/opt/sage SAGE_BIN=scripts/sage_conda_launcher.sh.
#
# Known gap: under this Sage, sage_mypy_category_plugin imports sage.structure before
# sage.all and fails with "cannot import name Category". Run a focused mypy check as
#     python -c "import sage.all, sys; from mypy.__main__ import console_entry; \
#         sys.argv[0] = 'mypy'; console_entry()" --config-file ... FILES
#
# This runtime serves diagnosis. Acceptance and QC use the configured stable Sage
# installation (AGENTS.md, Verification).
set -euo pipefail

prefix=${SAGE_PREFIX:?SAGE_PREFIX must name the conda environment to create}
repo_root=$(git rev-parse --show-toplevel)
cd "$repo_root"

if ! command -v micromamba >/dev/null; then
    install -d "$HOME/.local/bin"
    curl -sSL https://micro.mamba.pm/api/micromamba/linux-64/latest \
        | tar -xj -C "$HOME/.local" bin/micromamba
    export PATH="$HOME/.local/bin:$PATH"
fi

# The project pins Python 3.14; `gap` (not only gap-defaults) supplies PackageManager.
if [ ! -x "$prefix/bin/sage" ]; then
    micromamba create -y -p "$prefix" -c conda-forge "sage=10.9" "python=3.14.*" "gap=4.15.1" pytest just
fi
python="$prefix/bin/python"

# conda-forge GAP bundles older homalg/CAP releases in its system package directory.
# .gap-packages.g pins newer releases of the same packages, and engines/gap.py rejects
# a substituted installation, so the bundled copies are moved out of GAP's search path.
shadowed="$prefix/share/gap/pkg-shadowed"
install -d "$shadowed"
for package in cap examplesforhomalg gaussforhomalg generalizedmorphismsforcap \
    gradedringforhomalg homalg homalgtocas io_forhomalg linearalgebraforcap \
    localizeringforhomalg matricesforhomalg modulepresentationsforcap \
    monoidalcategories ringsforhomalg toolsforhomalg toric; do
    if [ -d "$prefix/share/gap/pkg/$package" ]; then
        mv "$prefix/share/gap/pkg/$package" "$shadowed/"
    fi
done

# This checkout, its runtime dependencies, and its dev and platform groups. The
# homotopy workspace member is a maturin extension and needs a Rust toolchain.
"$python" -m pip install --root-user-action=ignore uv
"$python" -m uv pip install --python "$python" --project . \
    --group dev --group platform --editable .

# PackageManager downloads GitHub archive tarballs for commit-pinned packages; hosts
# that only serve git reads cannot fetch them, so the pinned QPA commit is fetched by
# git into the location PackageManager would use. Installed exact versions are kept.
qpa_commit=8ffbde256214f5bcef6e3e86b29ccf0e0acd5afa
qpa_dir=".gap/pkg/QPA2-$qpa_commit"
install -d .gap/pkg
if [ ! -f "$qpa_dir/PackageInfo.g" ]; then
    git init -q "$qpa_dir"
    git -C "$qpa_dir" fetch -q --depth 1 https://github.com/homalg-project/qpa2 "$qpa_commit"
    git -C "$qpa_dir" checkout -q FETCH_HEAD
    rm -rf "$qpa_dir/.git"
fi
"$prefix/bin/gap" -q -r --packagedirs "$repo_root/.gap/pkg" "$repo_root/.gap-packages.g" </dev/null

# The juliapkg CLI needs the optional click dependency; the library call does not.
"$python" -c "import juliapkg; juliapkg.resolve()"

SAGE_BIN="$repo_root/scripts/sage_conda_launcher.sh" SAGE_PREFIX="$prefix" \
    "$repo_root/scripts/sage_conda_launcher.sh" -c \
    "import sage_categories; print('sage_categories', sage_categories.version())"
