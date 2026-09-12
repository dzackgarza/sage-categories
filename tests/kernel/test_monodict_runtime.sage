"""Sage MonoDict exposes identity lookup and items(), not dict-only convenience APIs."""

from sage_categories.kernel.sage_runtime import MonoDict


class IdentityKey:
    pass


key = IdentityKey()
table = MonoDict()
table[key] = "retained"

assert key in table
assert table[key] == "retained"
assert tuple(table.items()) == ((key, "retained"),)
assert "get" not in dir(table)
assert "values" not in dir(table)
