#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 2 ]; then
    echo "usage: $0 RELATIVE_TEST_FILE.sage TEST_FUNCTION" >&2
    exit 2
fi

source_file=$1
test_name=$2
repo_root=$(git rev-parse --show-toplevel)
sage_bin=${SAGE_BIN:?SAGE_BIN must name the declared Sage executable}

case "$source_file" in
    /*)
        echo "test file must be repository-relative: $source_file" >&2
        exit 2
        ;;
    *.sage) ;;
    *)
        echo "test file must end in .sage: $source_file" >&2
        exit 2
        ;;
esac

case "$test_name" in
    test_[A-Za-z0-9_]*) ;;
    *)
        echo "test function must be named test_*: $test_name" >&2
        exit 2
        ;;
esac

test -f "$repo_root/$source_file"

work=$(mktemp -d "${TMPDIR:-/tmp}/sage-categories-targeted.XXXXXX")
cleanup() {
    if [ -e "$work" ]; then
        gio trash "$work"
    fi
}
trap cleanup EXIT

mkdir -p "$work/$(dirname "$source_file")"

# A .sage file can still carry direct top-level calls so it remains executable as
# a standalone consumer.  The targeted runner asks pytest to execute one named test,
# so suppress only those top-level test invocations in the temporary copy; definitions
# and every assertion in the selected function remain byte-for-byte unchanged.
sed -E '/^test_[A-Za-z_][A-Za-z0-9_]*\(\)$/d' \
    "$repo_root/$source_file" > "$work/$source_file"

(
    cd "$work"
    "$sage_bin" --preparse "$source_file" >/dev/null
)

generated="$work/${source_file}.py"
importable="${generated%.sage.py}.py"
mv "$generated" "$importable"

relative_importable="${source_file%.sage}.py"
(
    cd "$work"
    PYTHONPATH="$repo_root/src${PYTHONPATH:+:$PYTHONPATH}" \
        "$sage_bin" -python -m pytest -vv -s "$relative_importable::$test_name" &
    pytest_pid=$!
    while kill -0 "$pytest_pid" 2>/dev/null; do
        sleep 15
        if kill -0 "$pytest_pid" 2>/dev/null; then
            ps -o pid=,stat=,etime=,pcpu=,rss= -p "$pytest_pid" >&2
        fi
    done
    if wait "$pytest_pid"; then
        exit 0
    else
        status=$?
        exit "$status"
    fi
)
