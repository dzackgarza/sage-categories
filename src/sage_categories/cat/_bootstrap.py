"""Bootstrap ``Cat`` before importing modules that consume its declarations."""

from importlib import import_module as _import_module

from sage_categories.cat import category as _category

_category.bootstrap()

# ``opposites`` constructs the retained Op² ≅ Id transformation at import time.
# Load it before ``kan -> constructions -> diagrams`` can reach it recursively through
# ``dual_functor_categories``; this preserves the pre-lint bootstrap order explicitly.
_import_module("sage_categories.cat.opposites")
