"""The root package bootstraps Cat without relying on dict-only APIs or loading leaves."""

import sys

import sage_categories


assert sage_categories.Cat() is not None
assert "sage_categories.algebra" not in sys.modules
